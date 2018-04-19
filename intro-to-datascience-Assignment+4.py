
# coding: utf-8

# ---
# 
# _You are currently looking at **version 1.1** of this notebook. To download notebooks and datafiles, as well as get help on Jupyter notebooks in the Coursera platform, visit the [Jupyter Notebook FAQ](https://www.coursera.org/learn/python-data-analysis/resources/0dhYG) course resource._
# 
# ---

# In[38]:

import pandas as pd
import numpy as np
import re
from scipy.stats import ttest_ind


# # Assignment 4 - Hypothesis Testing
# This assignment requires more individual learning than previous assignments - you are encouraged to check out the [pandas documentation](http://pandas.pydata.org/pandas-docs/stable/) to find functions or methods you might not have used yet, or ask questions on [Stack Overflow](http://stackoverflow.com/) and tag them as pandas and python related. And of course, the discussion forums are open for interaction with your peers and the course staff.
# 
# Definitions:
# * A _quarter_ is a specific three month period, Q1 is January through March, Q2 is April through June, Q3 is July through September, Q4 is October through December.
# * A _recession_ is defined as starting with two consecutive quarters of GDP decline, and ending with two consecutive quarters of GDP growth.
# * A _recession bottom_ is the quarter within a recession which had the lowest GDP.
# * A _university town_ is a city which has a high percentage of university students compared to the total population of the city.
# 
# **Hypothesis**: University towns have their mean housing prices less effected by recessions. Run a t-test to compare the ratio of the mean price of houses in university towns the quarter before the recession starts compared to the recession bottom. (`price_ratio=quarter_before_recession/recession_bottom`)
# 
# The following data files are available for this assignment:
# * From the [Zillow research data site](http://www.zillow.com/research/data/) there is housing data for the United States. In particular the datafile for [all homes at a city level](http://files.zillowstatic.com/research/public/City/City_Zhvi_AllHomes.csv), ```City_Zhvi_AllHomes.csv```, has median home sale prices at a fine grained level.
# * From the Wikipedia page on college towns is a list of [university towns in the United States](https://en.wikipedia.org/wiki/List_of_college_towns#College_towns_in_the_United_States) which has been copy and pasted into the file ```university_towns.txt```.
# * From Bureau of Economic Analysis, US Department of Commerce, the [GDP over time](http://www.bea.gov/national/index.htm#gdp) of the United States in current dollars (use the chained value in 2009 dollars), in quarterly intervals, in the file ```gdplev.xls```. For this assignment, only look at GDP data from the first quarter of 2000 onward.
# 
# Each function in this assignment below is worth 10%, with the exception of ```run_ttest()```, which is worth 50%.

# In[39]:

# Use this dictionary to map state names to two letter acronyms
states = {'OH': 'Ohio', 'KY': 'Kentucky', 'AS': 'American Samoa', 'NV': 'Nevada', 'WY': 'Wyoming', 'NA': 'National', 'AL': 'Alabama', 'MD': 'Maryland', 'AK': 'Alaska', 'UT': 'Utah', 'OR': 'Oregon', 'MT': 'Montana', 'IL': 'Illinois', 'TN': 'Tennessee', 'DC': 'District of Columbia', 'VT': 'Vermont', 'ID': 'Idaho', 'AR': 'Arkansas', 'ME': 'Maine', 'WA': 'Washington', 'HI': 'Hawaii', 'WI': 'Wisconsin', 'MI': 'Michigan', 'IN': 'Indiana', 'NJ': 'New Jersey', 'AZ': 'Arizona', 'GU': 'Guam', 'MS': 'Mississippi', 'PR': 'Puerto Rico', 'NC': 'North Carolina', 'TX': 'Texas', 'SD': 'South Dakota', 'MP': 'Northern Mariana Islands', 'IA': 'Iowa', 'MO': 'Missouri', 'CT': 'Connecticut', 'WV': 'West Virginia', 'SC': 'South Carolina', 'LA': 'Louisiana', 'KS': 'Kansas', 'NY': 'New York', 'NE': 'Nebraska', 'OK': 'Oklahoma', 'FL': 'Florida', 'CA': 'California', 'CO': 'Colorado', 'PA': 'Pennsylvania', 'DE': 'Delaware', 'NM': 'New Mexico', 'RI': 'Rhode Island', 'MN': 'Minnesota', 'VI': 'Virgin Islands', 'NH': 'New Hampshire', 'MA': 'Massachusetts', 'GA': 'Georgia', 'ND': 'North Dakota', 'VA': 'Virginia'}


# In[40]:

def get_list_of_university_towns():
    '''Returns a DataFrame of towns and the states they are in from the 
    university_towns.txt list. The format of the DataFrame should be:
    DataFrame( [ ["Michigan", "Ann Arbor"], ["Michigan", "Yipsilanti"] ], 
    columns=["State", "RegionName"]  )
    
    The following cleaning needs to be done:

    1. For "State", removing characters from "[" to the end.
    2. For "RegionName", when applicable, removing every character from " (" to the end.
    3. Depending on how you read the data, you may need to remove newline character '\n'. '''
    
    read1 = open('university_towns.txt', "r")
    read = read1.readlines()

    '''remove empty lines'''
    new_text = []
    for text in read:
        if not re.match(r'^\s*$', text):
            new_text.append(text)
        
    read = new_text.copy()
    '''remove white space'''
    for index, text in enumerate(read):
        read[index] = text.strip()
    '''create dataframe'''
    df_towns = pd.DataFrame(columns=('State', 'RegionName'))
    counter = 0
    state = ""
    region = ""
    '''first state, then region from ( to the end'''
    for text in read:
        if '[edit]' in text:
            state = text.replace('[edit]', "")
        else:
            region = re.sub(r' \(.*', "", text)
            df_towns.loc[counter] = [state, region]
            counter+=1
        
    return df_towns

get_list_of_university_towns()


# In[41]:

def get_recession_start():
    '''Returns the year and quarter of the recession start time as a 
    string value in a format such as 2005q3'''
    
    df_gdp = pd.read_excel('gdplev.xls', skiprows=220, parse_cols='E,G', header=None)
    df_gdp.columns = ['quarter', 'GDP']

    for i in range(4, len(df_gdp)):
        if (df_gdp.loc[i-4, 'GDP'] > df_gdp.loc[i-3, 'GDP'])                 and (df_gdp.loc[i-3, 'GDP'] > df_gdp.loc[i-2, 'GDP'])                 and (df_gdp.loc[i-2, 'GDP'] < df_gdp.loc[i-1, 'GDP'])                 and (df_gdp.loc[i-1, 'GDP'] < df_gdp.loc[i, 'GDP']):
            recession_base = i-4
            
    answer = df_gdp.loc[recession_base, 'quarter']
    j = recession_base
    while True:
        if (df_gdp.loc[j-1, 'GDP'] > df_gdp.loc[j, 'GDP']):
            j-=1
        else:
            answer = df_gdp.loc[j+1, 'quarter']
            break
    return answer

get_recession_start()


# In[42]:

def get_recession_end():
    '''Returns the year and quarter of the recession end time as a 
    string value in a format such as 2005q3'''
    df_gdp = pd.read_excel('gdplev.xls', skiprows=220, parse_cols='E,G', header=None)
    df_gdp.columns = ['quarter', 'GDP']
    for i in range(4, len(df_gdp)):
        if (df_gdp.loc[i-4, 'GDP'] > df_gdp.loc[i-3, 'GDP'])                 and (df_gdp.loc[i-3, 'GDP'] > df_gdp.loc[i-2, 'GDP'])                 and (df_gdp.loc[i-2, 'GDP'] < df_gdp.loc[i-1, 'GDP'])                 and (df_gdp.loc[i-1, 'GDP'] < df_gdp.loc[i, 'GDP']):
            answer = df_gdp.loc[i, 'quarter']
    
    return answer
    
       
get_recession_end()


# In[43]:

def get_recession_bottom():
    '''Returns the year and quarter of the recession bottom time as a 
    string value in a format such as 2005q3'''
    df_gdp = pd.read_excel('gdplev.xls', skiprows=220, parse_cols='E,G', header=None)
    df_gdp.columns = ['quarter', 'GDP']
    for i in range(4, len(df_gdp)):
        if (df_gdp.loc[i-4, 'GDP'] > df_gdp.loc[i-3, 'GDP'])                 and (df_gdp.loc[i-3, 'GDP'] > df_gdp.loc[i-2, 'GDP'])                 and (df_gdp.loc[i-2, 'GDP'] < df_gdp.loc[i-1, 'GDP'])                 and (df_gdp.loc[i-1, 'GDP'] < df_gdp.loc[i, 'GDP']):
            answer = df_gdp.loc[i-2, 'quarter']
    return answer

get_recession_bottom()


# In[44]:

def convert_housing_data_to_quarters():
   df = pd.read_csv('City_Zhvi_AllHomes.csv', header=0)
   
   # Create columns to keep
   cols_to_keep = ['RegionID', 'RegionName', 'State']
   for i in range(2000, 2017):
       for j in range(1, 13):
           if j <= 9:
               if i == 2016 and j == 9:
                   pass
               else:
                   month_str = '0' + str(j)
           else:
               if i == 2016:
                   pass
               else:
                   month_str = str(j)
           cols_to_keep.append(str(i) + '-' + month_str)
   df = df[cols_to_keep]
   
   # Convert two letter state abbreviations to state names
   df['State'] = df['State'].replace(states)

   def convert_to_qtr(ym):
       year, month = ym.split('-')
       if month == '01' or month == '02' or month == '03':
           result = year + 'q1'
       elif month == '04' or month == '05' or month == '06':
           result = year + 'q2'
       elif month == '07' or month == '08' or month == '09':
           result = year + 'q3'
       else:
           result = year + 'q4'
       return result

   # Stack the columns of GDP values and add a quarter column
   df_compiled = df.copy().set_index(['State', 'RegionName', 'RegionID']).stack(dropna=False)
   df_compiled = df_compiled.reset_index().rename(columns={'level_3': 'year_month', 0: 'gdp'})
   df_compiled.drop_duplicates(inplace=True)
   df_compiled['quarter'] = df_compiled['year_month'].apply(convert_to_qtr)
   df_compiled = df_compiled.drop('year_month', axis=1)
   result = df_compiled.pivot_table(values='gdp', index=['State', 'RegionName', 'RegionID'], columns='quarter', aggfunc=np.mean)
   result = result.reset_index()
   result = result.drop('RegionID', axis=1)
   
   result = result.set_index(['State', 'RegionName'])
   return result

convert_housing_data_to_quarters()


# In[45]:

def run_ttest():
    '''First creates new data showing the decline or growth of housing prices
    between the recession start and the recession bottom. Then runs a ttest
    comparing the university town values to the non-university towns values, 
    return whether the alternative hypothesis (that the two groups are the same)
    is true or not as well as the p-value of the confidence. 
    
    Return the tuple (different, p, better) where different=True if the t-test is
    True at a p<0.01 (we reject the null hypothesis), or different=False if 
    otherwise (we cannot reject the null hypothesis). The variable p should
    be equal to the exact p value returned from scipy.stats.ttest_ind(). The
    value for better should be either "university town" or "non-university town"
    depending on which has a lower mean price ratio (which is equivilent to a
    reduced market loss).'''
    
    univ = get_list_of_university_towns()
    bottom = get_recession_bottom()
    start = get_recession_start()
    data = convert_housing_data_to_quarters()
    newstart = data.columns[data.columns.get_loc(start) - 1]
    
    data['ratio'] = data[start] - data[bottom]
    data = data[[bottom, newstart, 'ratio']]
    data = data.reset_index()
    
    
    df = pd.merge(data,univ,how='inner',on=['State','RegionName'])
    df['uni'] = True
    data2 = pd.merge(data, df, how='outer', on=['State','RegionName',bottom, newstart, 'ratio'])
    data2['uni'] = data2['uni'].fillna(False)
    
    # t-test to determine if there is a difference between university and non-university towns
    univ_town_price_ratio = data2[data2['uni'] == True]
    non_univ_town_price_ratio = data2[data2['uni'] == False]
    st, p = ttest_ind(univ_town_price_ratio['ratio'].dropna(), non_univ_town_price_ratio['ratio'].dropna())

    # get different and better values
    different = False
    if p < 0.01:
        different = True

    # determine which type of town is better
    better = "university town" if univ_town_price_ratio['ratio'].mean() < non_univ_town_price_ratio['ratio'].mean() else "non-university town"
    

    return (different, p, better)

run_ttest()

