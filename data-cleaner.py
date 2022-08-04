import pandas as pd
import sqlite3
import regex as re
from mlxtend.preprocessing import minmax_scaling
#from sklearn.model_selection import train_test_split



#query the raw trulia house data from SQLite database
conn = sqlite3.connect(
    '/Users/dylannguyen/Documents/Coding/trulia_house_data.db')

houses_dataframe = pd.read_sql_query("SELECT * FROM trulia_house_raw_data", conn)


missing_values_count = houses_dataframe.isnull().sum()

print('___RAW DATA SUMMARY____')

print(missing_values_count)

print("number of samples: "+str(len(houses_dataframe)))
