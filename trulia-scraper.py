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