import math
import pandas as pd
import numpy as np
import datetime as dt
from matplotlib import pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.svm import SVR
from sklearn.model_selection import RandomizedSearchCV
from sklearn.metrics import mean_squared_error, mean_absolute_error, mean_squared_log_error
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LogisticRegression,LinearRegression,BayesianRidge, Lasso
from statistics import mean
from math import sqrt
import torch
import torch.nn as nn
import torch.nn.functional as F
import datetime
import warnings

from copy import deepcopy
import os
# Input data files are available in the "../input/" directory.
# For example, running this (by clicking run or pressing Shift+Enter) will list all files under the input directory

for dirname, _, filenames in os.walk('/kaggle/input'):
    for filename in filenames:
        print(os.path.join(dirname, filename))

# Any results you write to the current directory are saved as output.
df_train = pd.read_csv('/kaggle/input/covid19-global-forecasting-week-4/train.csv')
df_train['Province_State'] = df_train['Province_State'].fillna('')
df_train['Date_datetime'] = df_train['Date'].apply(lambda x: (datetime.datetime.strptime(x, '%Y-%m-%d')))
df_train['Country_Province'] = df_train['Country_Region'] + '_' + df_train['Province_State']
df_train['Country_Province'] = df_train['Country_Province'].apply(lambda x:(x[:-1] if x.endswith('_') else x))
df_train = df_train.drop(columns=['Date','Province_State','Country_Region'])
df_train = df_train[df_train["Date_datetime"]<datetime.datetime.strptime('2020-04-12', '%Y-%m-%d')]
print(df_train)

df_test = pd.read_csv('/kaggle/input/covid19-global-forecasting-week-4/test.csv')
df_test['Province_State'] = df_test['Province_State'].fillna('')
df_test['Date_datetime'] = df_test['Date'].apply(lambda x: (datetime.datetime.strptime(x, '%Y-%m-%d')))
df_test['Country_Province'] = df_test['Country_Region'] + '_' + df_test['Province_State']
df_test['Country_Province'] = df_test['Country_Province'].apply(lambda x:(x[:-1] if x.endswith('_') else x))
df_test = df_test.drop(columns=['Date','Province_State','Country_Region'])
df_test.head()

df_lockdown = pd.read_csv('/kaggle/input/covid19/lockdown.csv')
df_lockdown['Province'] = df_lockdown['Province'].fillna('')
df_lockdown['Date'] = df_lockdown['Date'].fillna('08/05/2020')
df_lockdown['Date_datetime'] = df_lockdown['Date'].apply(lambda x: (datetime.datetime.strptime(x, '%d/%m/%Y')))
df_lockdown['Country_Province'] = df_lockdown['Country/Region'] + '_' + df_lockdown['Province']
df_lockdown['Country_Province'] = df_lockdown['Country_Province'].apply(lambda x:(x[:-1] if x.endswith('_') else x))
df_lockdown = df_lockdown.drop(columns=['Date','Province','Country/Region','Type','Reference'])
print(df_lockdown)

lockdown_dates = {}

for _,i in df_lockdown.iterrows():
  lockdown_dates[i['Country_Province']] = i['Date_datetime']

print(lockdown_dates)

warnings.simplefilter(action='ignore')

test_dates = df_test['Date_datetime'].unique()

for country in df_train['Country_Province'].unique():

    print(country)
    
    country_train = df_train[(df_train['Country_Province']==country) &
                            (df_train['ConfirmedCases']>0)]
    country_test = df_test[df_test['Country_Province']==country]
    
    country_min_date = country_train['Date_datetime'].min()

    country_train['Days since start'] = country_train['Date_datetime']-country_min_date
    country_train['Days since lockdown'] = country_train['Date_datetime'] - lockdown_dates[country]
    country_train['Days since lockdown'] = country_train['Days since lockdown'].apply(
        lambda x:x if(x>datetime.timedelta(minutes=0)) else datetime.timedelta(days=0))
    
    country_test['Days since start'] = country_test['Date_datetime']-country_min_date
    country_test['Days since lockdown'] = country_test['Date_datetime'] - lockdown_dates[country]
    country_test['Days since lockdown'] = country_test['Days since lockdown'].apply(
        lambda x:x if(x>datetime.timedelta(minutes=0)) else datetime.timedelta(days=0))
    
#     print("Train pre")
#     print(country_train)
    
#     print("Test pre")
#     print(country_test)
    
    ## normalizing data ##
    
    math_cols = ['Days since start','Days since lockdown','ConfirmedCases','Fatalities']
    props = {}
    for col in math_cols:
        minmax = []
        minmax.append(country_train[col].min())
        minmax.append(country_train[col].max() - minmax[0])
        props[col] = minmax
        
        country_train[col] = ((country_train[col] - minmax[0])*1.0)/(minmax[1]*1.0)
        country_train[col] = country_train[col].fillna(0)
        
    country_test['Days since start'] = ((country_test['Days since start'] 
                                         - props['Days since start'][0])*1.0)/(props['Days since start'][1]*1.0)

    country_test['Days since lockdown'] = ((country_test['Days since lockdown'] 
                                         - props['Days since lockdown'][0])*1.0)/(props['Days since lockdown'][1]*1.0)
    country_test = country_test.fillna(0.0)
    
    country_train = country_train.replace([np.inf,-np.inf],0.0)
    country_test = country_test.replace([np.inf,-np.inf],0.0)
    
#     print("Train post")
#     print(country_train)
    
#     print("Test post")
#     print(country_test)
    
    ## predicting confirmed cases ## .astype('timedelta64[D]')

    train_X = ((country_train[['Days since start','Days since lockdown']]).to_numpy()).reshape((-1,2))
    train_y_conf = country_train.ConfirmedCases.to_numpy()
    
    test_X = ((country_test[['Days since start','Days since lockdown']]).to_numpy()).reshape((-1,2))

    clf_conf = LinearRegression()
    clf_conf.fit(train_X,np.log(train_y_conf+1))

    poly_pred_init_conf = np.exp(clf_conf.predict(test_X))-1

    poly_pred_conf = np.array([x if x>0 else 0 for x in poly_pred_init_conf])
    poly_pred_conf = np.nan_to_num(poly_pred_conf)

    ## predicting fatalities ## astype('timedelta64[D]').

    train_X = ((country_train[['Days since start','Days since lockdown']]).to_numpy()).reshape((-1,2))
    train_y_fat = country_train.Fatalities.to_numpy()
    
    test_X = ((country_test[['Days since start','Days since lockdown']]).to_numpy()).reshape((-1,2))
    
    clf_fat = LinearRegression()
    clf_fat.fit(train_X,np.log(train_y_fat+1))

    poly_pred_init_fat = np.exp(clf_fat.predict(test_X))-1

    poly_pred_fat = np.array([x if x>0 else 0 for x in poly_pred_init_fat])
    poly_pred_fat = np.nan_to_num(poly_pred_fat)
    
    mask = df_test['Country_Province'] == country
    df_test.loc[mask,'ConfirmedCases'] = poly_pred_conf
    df_test.loc[mask,'ConfirmedCases'] = (df_test[mask]['ConfirmedCases']*
                                          props['ConfirmedCases'][1]) + props['ConfirmedCases'][0]
    
    df_test.loc[mask,'Fatalities'] = poly_pred_fat
    df_test.loc[mask,'Fatalities'] = (df_test[mask]['Fatalities']*
                                          props['Fatalities'][1]) + props['Fatalities'][0]
    
sub = df_test.drop(columns=['Date_datetime','Country_Province'])
sub.to_csv('submission.csv',index=False)