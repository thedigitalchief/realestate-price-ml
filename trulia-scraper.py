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


# scrapping each house listing's weblink
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