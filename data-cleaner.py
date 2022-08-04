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

#rescale price to millions
houses_dataframe['price']=houses_dataframe['price'].apply(lambda x: x/(1e6))

#rescale sqft to thousands of sqft
houses_dataframe['building_sqft']=houses_dataframe['building_sqft'].apply(lambda x: x/(1000))

#Extract garage boolean from description
houses_dataframe['has_garage']=houses_dataframe['home_description'].apply(lambda x: 1 if 'garage' in x.lower() else 0)


