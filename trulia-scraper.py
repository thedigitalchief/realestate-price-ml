from bs4 import BeautifulSoup
import time
import numpy as np
import pandas as pd
import regex as re
import requests


# HTTP header for scraping requests:
req_headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'en-US,en;q=0.8',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Chrome/61.0.3163.100 Safari/537.36'
}

user_agent_list=['Chrome/61.0.3163.100 Safari/537.36','AppleWebKit/537.36 (KHTML, like Gecko)','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36']



# scraping each house listing's weblink
def get_house_links(base_link, num_pages):
    
    global req_headers
    link_list=[]
    
    #starting a request session
    with requests.Session() as s:
        
        #loop through all pages
        for i in range(1,num_pages+1):
            
            #add desired page number to the base http link
            link=base_link+str(i)+"_p/"
            
            #making the http request
            with requests.Session() as s:
                data=s.get(link,headers=req_headers)
            
            #using bs4 to change the output from the request to a soup object, easily analysed
            soup=BeautifulSoup(data.content,'html.parser')
            
            #find all of the property card tags in HTML doc
            house_link=soup.find_all("a",class_=re.compile('PropertyCard'))

            #extract the link string from  property card and add to remainder of the HTTP request
            for n in [item['href'] for item in house_link]:
                link_list=link_list+["https://www.trulia.com/"+n]
                
                
            #random vary time and the header in between every 4 requests so its more human
            if i%4==0:
                r=np.random.randint(0,3)
                user_agent=user_agent_list[r]
                req_headers = {
                    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                    'accept-encoding': 'gzip, deflate, br',
                    'accept-language': 'en-US,en;q=0.8',
                    'upgrade-insecure-requests': '1',
                    'user-agent': user_agent
                    }
                
                time.sleep(np.random.randint(60,180))
            
            #randomly vary the time in between each request
            time.sleep(np.random.randint(20,30))
            
    return link_list



def extract_link_data(link_list): 
    #Function to take in list of links for trulia house listings and return dataframe of data for all links
    #type link_list: str - list of links for each realestate listing retrieved by the search
    #rtype: obj (pandas df) - Data from trulia links

    global req_headers
    
    price_list=[]
    address_list=[]
    zip_list=[]
    beds_list=[]
    baths_list=[]
    building_sqft_list=[]
    year_built_list=[]
    lot_area_list=[]
    
     #starts a requests session
    with requests.Session() as s:
        
        for i in range(len(link_list)):
            link=link_list[i]
            
            #get HTML doc from house listing
            data=s.get(link,headers=req_headers)
            soup=BeautifulSoup(data.content,'html.parser')
            
            #Uncomment to save HTML data to directory to save progress in case program stops 
            #do to a "captcha" bot on the site
            '''
            with open("C:/Users/dakot/Desktop/DataScience/Project Scrap work/trulia_project/raw_page_html/"+str(i)+".html", "w") as f:
                f.write(str(data.content))
            '''
            
            #use our extraction functions below to scrape information from links and add to lists from above
            price_list.append(get_price(soup))
            address_list.append(get_address(soup))
            zip_list.append(get_zip(soup))
            beds_list.append(get_beds(soup))
            baths_list.append(get_baths(soup))
            year_built_list.append(get_year_built(soup))
            
            
            #2 different spots on the site where building and lot area are listed, so trying to scrape both
            building_area=get_building_area(soup)
            if pd.isnull(building_area):
                building_area=get_living_area(soup)
            
            lot_area=get_lot_area(soup)        
            if pd.isnull(lot_area):
                lot_area=get_lot_area_alt(soup)
                
            building_sqft_list.append(building_area)
    
            lot_area_list.append(lot_area)
            
            
            #Randomly vary the time and header every 4 requests to seem less bot-like
            if i%4==0:
                r=np.random.randint(0,3)
                user_agent=user_agent_list[r]
                req_headers = {
                    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                    'accept-encoding': 'gzip, deflate, br',
                    'accept-language': 'en-US,en;q=0.8',
                    'upgrade-insecure-requests': '1',
                    'user-agent': user_agent
                    }
                
                time.sleep(np.random.randint(60,180))
            
            #randomly vary the time in between requests to seem less robot-like
            time.sleep(np.random.randint(20,30))
            
            print(i)
            
            
    #creating a dataframe with all of scraped data
    dataframe=pd.DataFrame({'price':price_list,'address':address_list,'zip':zip_list,'num_bedrooms':beds_list,'num_baths':baths_list,'building_sqft':building_sqft_list,'year_built':year_built_list,'lot_area':lot_area_list})
    return dataframe


def get_price(soup):
    """
    :type soup: obj - beautiful soup object for a house listing on trulia
    :rtype: int - House price
    """
    
    try:
        price=float([item.text for item in soup.find_all() if "data-testid" in item.attrs and item["data-testid"]=='home-details-price-detail'][0].replace('$','').replace(',',''))    
        return price
    except:
        return np.nan
    
    
def get_address(soup):
    """
    :type soup: obj - beautiful soup object for a house listing on trulia
    :rtype: str - Address for a house listing
    """

    try:
        address = str([item.text for item in soup.find_all(
        ) if "data-testid" in item.attrs and item["data-testid"] == 'home-details-summary-address'][0])
        return address
    except:
        return 'None'


def get_zip(soup):
    """
    :type soup: obj - beautiful soup object for a house listing on trulia
    :rtype: str - zipcode for a house
    """

    try:
        zip = str([item.text for item in soup.find_all(
        ) if "data-testid" in item.attrs and item["data-testid"] == 'home-details-summary-city-state'][0])
        return (re.sub('\D', '', zip))
    except:
        return 'None'


def get_beds(soup):
    """
    :type soup: obj - beautiful soup object for a house listing on trulia
    :rtype: int - number of bedrooms
    """

    try:
        num_beds = float(([item.text for item in soup.find_all(
        ) if "data-testid" in item.attrs and item["data-testid"] == 'home-summary-size-bedrooms'][0]).lower().replace('beds', ''))
        return num_beds
    except:
        return np.nan


def get_baths(soup):
    """
    :type soup: obj - beautiful soup object for a house listing on trulia
    :rtype: int - number of bathrooms
    """

    try:
        num_baths = float(([item.text for item in soup.find_all(
        ) if "data-testid" in item.attrs and item["data-testid"] == 'home-summary-size-bathrooms'][0]).lower().replace('baths', ''))
        return num_baths
    except:
        return np.nan


def get_year_built(soup):
    """
    :type soup: obj - beautiful soup object for a house listing on trulia
    :rtype: int - year the house was built
    """

    try:
        table_text = [item.text for item in soup.find_all(
        ) if "data-testid" in item.attrs and item["data-testid"] == 'structured-amenities-table-category']
        for item in table_text:
            item = item.lower()

            if 'year built' in item:
                i = item.index('year built')
                year_built = item[i:i+100]
                possible_years = list(range(1900, 2022))
                possible_years = [str(year) for year in possible_years]
                try:
                    year_built = int(
                        [year for year in possible_years if year in year_built][0])
                except:
                    year_built = np.nan
        return year_built
    except:
        return np.nan


def get_lot_area(soup):
    """
    :type soup: obj - beautiful soup object for a house listing on trulia
    :rtype: int - lot area for a listing (acres)
    """

    try:
        table_text = [item.text for item in soup.find_all(
        ) if "data-testid" in item.attrs and item["data-testid"] == 'structured-amenities-table-category']
        for item in table_text:
            item = item.lower()

            if 'lot area' in item:
                if 'feet' in item:
                    lot_sqft = item.replace('feet', '').replace('square', '').replace(
                        'area', '').replace('lot', '').replace('information', '').replace(':', '')
                    lot_area = float(lot_sqft)/43560
                if 'acres' in item:
                    lot_area = item.replace('acres', '').replace('area', '').replace(
                        'lot', '').replace('information', '').replace(':', '')
                    lot_area = float(lot_area)

        return lot_area
    except:
        return np.nan


def get_lot_area_alt(soup):
    """ Searches a different location in the HTML for the lot area (compared to the function above)
    :type soup: obj - beautiful soup object for a house listing on trulia
    :rtype: int - lot area for a listing (acres)
    """

    try:
        lot_size = ([item.text for item in soup.find_all() if "data-testid" in item.attrs and item["data-testid"] ==
                    'home-summary-size-lotsize'][0].replace('(', '').replace(')', '').replace('on', '').replace('acre', '').replace('s', ''))
        return float(lot_size)
    #*43560
    except:
        return np.nan


def get_building_area(soup):
    """ 
    :type soup: obj - beautiful soup object for a house listing on trulia
    :rtype: int - building area (sq feet)
    """

    try:
        table_text = [item.text for item in soup.find_all(
        ) if "data-testid" in item.attrs and item["data-testid"] == 'structured-amenities-table-category']
        for item in table_text:
            item = item.lower()
            if 'building area' in item:
                house_sqft = item.replace('building', '').replace('area', '').replace(
                    ':', '').replace('square', '').replace('feet', '')
                house_sqft = float(house_sqft)
        return house_sqft
    except:
        return np.nan


def get_living_area(soup):
    """ Searches a different location in the HTML for the building area/living area (compared to the function above)
    :type soup: obj - beautiful soup object for a house listing on trulia
    :rtype: int - building area (sq feet)
    """

    try:
        table_text = [item.text for item in soup.find_all(
        ) if "data-testid" in item.attrs and item["data-testid"] == 'structured-amenities-table-category']

        for item in table_text:
            item = item.lower()
            if 'living area' in item:
                i = item.index('living area')
                living_area = item[i:i+100]
                living_area = re.sub('\D', '', living_area)
        return float(living_area)
    except:
        return np.nan


#main trulia web scraper function
def web_scraper(base_link, num_pages):
    """ Main callable function 
    :type base_link: str - Link for a trulia.com search
    :type num_pages: int - The number of pages retirieved by the search (pages of listings that the user wants to scrape)
    :rtype: obj (pandas dataframe) - dataframe of house listing data from a trulia search
    """

    link_list = get_house_links(base_link, num_pages)
    dataframe = extract_link_data(link_list)
    return dataframe
