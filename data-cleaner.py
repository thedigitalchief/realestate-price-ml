import pandas as pd
import sqlite3
import regex as re
#from sklearn.model_selection import train_test_split
from mlxtend.preprocessing import minmax_scaling



#takes 1-2 min to process per lisiting
#query the raw trulia house data from SQLite database
conn = sqlite3.connect('/Users/dylannguyen/Documents/Coding/trulia_house_data.db')
houses_dataframe = pd.read_sql_query("SELECT * FROM trulia_house_raw_data", conn)


#summarizing missing values
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

#pool boolean
houses_dataframe['has_pool']=houses_dataframe['home_description'].apply(lambda x: 1 if 'pool' in x.lower() else 0)

#upstair boolean
houses_dataframe['has_upstairs']=houses_dataframe['home_description'].apply(lambda x: 1 if ('upstair' in x.lower() or 'upstairs' in x.lower()) else 0)



#eliminate rows containing missing values of price, num_baths, lot area, year built
houses_dataframe['has_IV']=houses_dataframe['home_description'].apply(lambda x: 1 if 'isla vista' in x.lower() else 0)
houses_dataframe.dropna(subset=['price','num_baths','lot_area','year_built'],inplace=True)

#eliminate rows containing outlier prices (above 10 million)
houses_dataframe=houses_dataframe[houses_dataframe['price']<10]

#eliminate rows with outlying land area (below 20 acres)
houses_dataframe = houses_dataframe[houses_dataframe['lot_area'] < 20]


#notifies if sqft is missing for future reference
houses_dataframe['building_sqft'+'_was_missing']=houses_dataframe['building_sqft'].isnull()


#congregating missing values & calculating sum
missing_values_count = houses_dataframe.isnull().sum()

print('___CLEANED DATA SUMMARY____')
print(missing_values_count)
print("number of samples: "+str(len(houses_dataframe)))


#storing the now cleaned data in a new table: my SQLite database
houses_dataframe.to_sql(name='trulia_house_SB_data_cleaned', con=conn, schema='trulia_sb_house_data.db', if_exists='replace')
