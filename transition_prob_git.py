"""
Supermarket analysis: calculate transition probabilites
"""

import pandas as pd
import glob
import os
from sqlalchemy import create_engine
import numpy as np
from datetime import datetime,timedelta
from sqlalchemy.types import Integer, DateTime,String



# Read csv files
path = r'...' #<--- add the path where the customer data files are
all_files = glob.glob(os.path.join(path, "*.csv"))


df = pd.DataFrame()

for num,filename in enumerate(all_files):
    if num == 0:
        df1 = pd.read_csv(filename, index_col=None,sep=';')
        df = df.append(df1)
    else:
        df1 = pd.read_csv(filename, index_col=None,sep=';')
        df1['customer_no'] = df1['customer_no']+num*20000
        df = df.append(df1)

# Change from string to datetime
df['timestamp'] =  pd.to_datetime(df['timestamp'], format='%Y-%m-%d %H:%M:%S')

df = df.sort_values('timestamp')
df.set_index('timestamp', inplace=True)


# Add time in between sections for each customer
customer_list = df['customer_no'].unique().tolist()
df_complete = pd.DataFrame()

for c in customer_list:
    temp = df.loc[df['customer_no'] == c]
    x = pd.DataFrame()
    #Add entrance at the beginning
    time_entrance = temp.index[0] - timedelta(minutes = 1)

    row = pd.Series({'customer_no':c,'location':'entrance'},name=time_entrance)
    temp = temp.append(row)
    temp = temp.sort_index()

    #Check if chekout is the last entry, if not, add it
    if temp.iloc[-1][1] == 'checkout':
        pass
    else:
        time_checkout = temp.index[-1] + timedelta(minutes = 1)
        row = pd.Series({'customer_no':c,'location':'checkout'},name=time_checkout)
        temp = temp.append(row)


    time_range = pd.date_range(start=temp.index[0].strftime('%Y-%m-%d %H:%M'), end=temp.index[-1].strftime('%Y-%m-%d %H:%M'), freq='min')
    temp = temp.reindex(time_range)
    temp = temp.ffill(axis = 0)
    df_complete = df_complete.append(temp)

df_complete['shift_loc'] = df_complete['location'].shift(-1)
df_complete['shift_c'] = df_complete['customer_no'].shift(-1)
df_complete['move'] = df_complete['location'] + '-' + df_complete['shift_loc']
df_complete.drop(['move'],axis=1)
df_complete['move'] = df_complete.apply(lambda x : x['location'] + '-' + x['shift_loc'] if x['customer_no'] == x['shift_c'] or x['location'] == 'entrance' else "", axis=1)
df_complete = df_complete.reset_index()
df_complete.rename(columns={'index':'timestamp'}, inplace=True)
# Delete rows with no move
indexNames = df_complete[ df_complete['move'] == "" ].index

# Delete these row indexes from dataFrame
df_complete.drop(indexNames , inplace=True)
# Delete column shift_c
df_complete=df_complete.drop(['shift_c'],axis=1)

# Connect to postgres
USERNAME = '....'  # <-- add credentials
PASSWORD = '...' # <-- add credentials
HOST = 'localhost'
PORT = '5432'
DBNAME = '...' # <-- add name of the DB

conn_string = f'postgres://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}'
db = create_engine(conn_string)

# Send to postgres
df_complete.to_sql('moves',db,dtype={"timestamp": DateTime(),"customer_no": Integer(), "location": String(), "shift_loc": String(), "move": String()})


query = "select distinct(move), count(move), location,shift_loc  from moves group by move, location, shift_loc order by location, shift_loc asc;"
result = db.execute(query)

df_transition=pd.DataFrame(result,columns=result.keys())

# Transition probabilites
col = ['checkout','dairy','drinks','entrance','fruit','spieces']
ind = ['checkout','dairy','drinks','entrance','fruit','spieces']

df_prob = pd.DataFrame(0, columns=col, index=ind)

#Calculate transition probabilites
a = df_transition.groupby(['location','shift_loc'],as_index = False).sum().pivot('location','shift_loc').fillna(0)

#Total sum per row:
total_per_row = a.sum(axis=1)

prob_dairy = a.iloc[0,:].div(total_per_row[0])
prob_drinks = a.iloc[1,:].div(total_per_row[1])
prob_entrance = a.iloc[2,:].div(total_per_row[2])
prob_fruit =a.iloc[3,:].div(total_per_row[3])
prob_spices = a.iloc[4,:].div(total_per_row[4])

## Find a better way!!!!!
df_prob.iloc[1,0] = prob_dairy[0]
df_prob.iloc[1,1] = prob_dairy[1]
df_prob.iloc[1,2] = prob_dairy[2]
df_prob.iloc[1,3] = 0
df_prob.iloc[1,4] = prob_dairy[3]
df_prob.iloc[1,5] = prob_dairy[4]

df_prob.iloc[2,0] = prob_drinks[0]
df_prob.iloc[2,1] = prob_drinks[1]
df_prob.iloc[2,2] = prob_drinks[2]
df_prob.iloc[2,3] = 0
df_prob.iloc[2,4] = prob_drinks[3]
df_prob.iloc[2,5] = prob_drinks[4]

df_prob.iloc[3,0] = prob_entrance[0]
df_prob.iloc[3,1] = prob_entrance[1]
df_prob.iloc[3,2] = prob_entrance[2]
df_prob.iloc[3,3] = 0
df_prob.iloc[3,4] = prob_entrance[3]
df_prob.iloc[3,5] = prob_entrance[4]

df_prob.iloc[4,0] = prob_fruit[0]
df_prob.iloc[4,1] = prob_fruit[1]
df_prob.iloc[4,2] = prob_fruit[2]
df_prob.iloc[4,3] = 0
df_prob.iloc[4,4] = prob_fruit[3]
df_prob.iloc[4,5] = prob_fruit[4]

df_prob.iloc[5,0] = prob_spices[0]
df_prob.iloc[5,1] = prob_spices[1]
df_prob.iloc[5,2] = prob_spices[2]
df_prob.iloc[5,3] = 0
df_prob.iloc[5,4] = prob_spices[3]
df_prob.iloc[5,5] = prob_spices[4]

df_prob.iloc[0,0] = 1
