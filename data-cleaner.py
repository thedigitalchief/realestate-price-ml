import pandas as pd
import sqlite3
import regex as re
from mlxtend.preprocessing import minmax_scaling
#from sklearn.model_selection import train_test_split


#takes ~1-2 min per listing
#query the raw trulia house data from SQLite database
conn = sqlite3.connect(
    '/Users/dylannguyen/Documents/Coding/trulia_house_data.db')

houses_dataframe = pd.read_sql_query("SELECT * FROM trulia_house_raw_data", conn)


#congregating missing values
missing_values_count = houses_dataframe.isnull().sum()
print('___RAW DATA SUMMARY____')
print(missing_values_count)
print("number of samples: "+str(len(houses_dataframe)))


#converting "year built" value into "house age"
houses_dataframe['house_age'] = houses_dataframe['year_built'].apply(
    lambda x: 2022-x)


#Rescaling numerical data values
#rescale home price to millions
houses_dataframe['price']=houses_dataframe['price'].apply(lambda x: x/(1e6))

#rescale squarefeet to thousands of sqft
houses_dataframe['building_sqft']=houses_dataframe['building_sqft'].apply(lambda x: x/(1000))


#Extracting boolean values from descriptions:
#garage boolean
houses_dataframe['has_garage']=houses_dataframe['home_description'].apply(lambda x: 1 if 'garage' in x.lower() else 0)

#ocean views boolean 
houses_dataframe['has_ocean_views'] = houses_dataframe['home_description'].apply(
    lambda x: 1 if 'ocean view' in x.lower() else 0)

#mountian views boolean 
houses_dataframe['has_mountain_views'] = houses_dataframe['home_description'].apply(
    lambda x: 1 if 'mountain view' in x.lower() else 0)

# Extract pool boolean from description
houses_dataframe['has_pool']=houses_dataframe['home_description'].apply(lambda x: 1 if 'pool' in x.lower() else 0)

# Extract upstair boolean from description
houses_dataframe['has_upstairs']=houses_dataframe['home_description'].apply(lambda x: 1 if ('upstair' in x.lower() or 'upstairs' in x.lower()) else 0)


#eliminate rows containing missing values of price, num_baths, lot area, year built
houses_dataframe['has_IV']=houses_dataframe['home_description'].apply(lambda x: 1 if 'isla vista' in x.lower() else 0)
houses_dataframe.dropna(subset=['price','num_baths','lot_area','year_built'],inplace=True)


#eliminate rows containing outlier prices (above 10 million)
houses_dataframe=houses_dataframe[houses_dataframe['price']<10]


#notifies if sqft is missing for future reference
houses_dataframe['building_sqft'+'_was_missing']=houses_dataframe['building_sqft'].isnull()


#congregating missing values & calculating sum
missing_values_count = houses_dataframe.isnull().sum()

print('___CLEANED DATA SUMMARY____')
print(missing_values_count)
print("number of samples: "+str(len(houses_dataframe)))
