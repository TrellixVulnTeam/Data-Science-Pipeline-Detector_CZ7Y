# -*- coding: utf-8 -*-
"""
Created on Wed Feb 22 20:34:46 2017

@author: user
"""

# This Python 3 environment comes with many helpful analytics libraries installed
# It is defined by the kaggle/python docker image: https://github.com/kaggle/docker-python
# For example, here's several helpful packages to load in 


import numpy as np
import pandas as pd
from scipy import sparse
from sklearn import model_selection, preprocessing, ensemble
from sklearn.metrics import log_loss
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.grid_search import GridSearchCV
from sklearn import preprocessing
# For example, running this (by clicking run or pressing Shift+Enter) will list the files in the input directory
df = pd.read_json(open("../input/train.json", "r"))

ulimit = np.percentile(df.price.values, 99)
df['price'].ix[df['price']>ulimit] = ulimit
# price is right skewed so using log to create a gaussian pattern
df['price']=np.log1p(df['price'])
df["num_photos"] = df["photos"].apply(len)
df["num_features"] = df["features"].apply(len)
df["num_description_words"] = df["description"].apply(lambda x: len(x.split(" ")))
df["created"] = pd.to_datetime(df["created"])
df["created_year"] = df["created"].dt.year
df["created_month"] = df["created"].dt.month
df["created_day"] = df["created"].dt.day

categorical = ["display_address", "manager_id", "building_id", "street_address"]

for f in categorical:
        if df[f].dtype=='object':
            #print(f)
            lbl = preprocessing.LabelEncoder()
            lbl.fit(list(df[f].values))
            df[f] = lbl.transform(list(df[f].values))




num_feats =["bathrooms", "bedrooms", "latitude", "longitude", "price",
       "num_photos", "num_features", "num_description_words",
       "created_year", "created_month", "created_day",
       "listing_id","display_address", "manager_id", "building_id", "street_address"]

X = df[num_feats]
y = df["interest_level"]
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.33)
clf = RandomForestClassifier(n_estimators=1000)
clf.fit(X_train, y_train)
y_val_pred = clf.predict_proba(X_val)
log_loss(y_val, y_val_pred)
df = pd.read_json(open("../input/test.json", "r"))
print(df.shape)
df['price']=np.log1p(df['price'])
df["num_photos"] = df["photos"].apply(len)
df["num_features"] = df["features"].apply(len)
df["num_description_words"] = df["description"].apply(lambda x: len(x.split(" ")))
df["created"] = pd.to_datetime(df["created"])
df["created_year"] = df["created"].dt.year
df["created_month"] = df["created"].dt.month
df["created_day"] = df["created"].dt.day
categorical = ["display_address", "manager_id", "building_id", "street_address"]

for f in categorical:
        if df[f].dtype=='object':
            #print(f)
            lbl = preprocessing.LabelEncoder()
            lbl.fit(list(df[f].values))
            df[f] = lbl.transform(list(df[f].values))
X = df[num_feats]

y = clf.predict_proba(X)


out_df = pd.DataFrame(y)
out_df.columns = ["high", "medium", "low"]
out_df["listing_id"] = df.listing_id.values
out_df.to_csv("rf_starter2.csv", index=False)


# Any results you write to the current directory are saved as output.