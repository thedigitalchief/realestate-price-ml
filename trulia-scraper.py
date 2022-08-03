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
