import sqlite3
import zipfile
import pandas as pd
import numpy as np
from pandas.io import sql
from sklearn.linear_model import LogisticRegression
from datetime import datetime

conn = sqlite3.connect('../input/database.sqlite')
print("Connected to DB")

query1 = """
select tss.HistCTR, tss.Position, si.IsUserLoggedOn, si.CategoryID, tss.IsClick from trainSearchStream tss left join SearchInfo si on tss.SearchID = si.SearchID where ObjectType=3 limit 100000
"""
print("first query")

# Get test data
query_test = """
select tss.TestID, tss.HistCTR, tss.Position, si.IsUserLoggedOn, si.CategoryID from testSearchStream tss left join SearchInfo si on tss.SearchID = si.SearchID where ObjectType=3 limit 100000
"""
print("second query")


df = pd.read_sql(query1, conn)
print("Created dataframe")
#print(df)
xList_d = df[['Position', 'HistCTR', 'IsUserLoggedOn', 'CategoryID']]
print("x list d")
labels_d = df.IsClick
print("y label")

df_test = pd.read_sql(query_test, conn)
print("second query executed")
X_test = df_test[['Position', 'HistCTR', 'IsUserLoggedOn', 'CategoryID']]
print("test dataframe")

# Learn
model = LogisticRegression()
print("created LR")
model.fit(xList_d, labels_d)
print("model fit")
pred = model.predict_proba(X_test)
print("predicted")

# Output to csv
filename = 'submission.csv'
print("output")
pd.DataFrame({'ID': df_test.TestId, 'IsClick': pred[:, 1]}).to_csv(filename, index=False)
print("finished")
