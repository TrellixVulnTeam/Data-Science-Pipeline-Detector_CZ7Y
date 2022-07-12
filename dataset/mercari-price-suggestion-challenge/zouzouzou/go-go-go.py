import pandas as pd
import numpy as np
import scipy
from datetime import datetime
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.preprocessing import LabelBinarizer
from sklearn.linear_model import Ridge

# read data from train.tsv & test.tsv
print("read train data from csv")
df_train = pd.read_table("../input/train.tsv", engine='c')
print("read test data from csv")
df_test = pd.read_table("../input/test.tsv", engine='c')

# concat train & test together
print("concat train data & test data")
df_all = pd.concat([df_train, df_test])

# count of train data
nrow_train = df_train.shape[0]

# y_train
y_train = np.log1p(df_train['price'])

# name
# use CountVectorizer
print("name ...")
df_all['name'] = df_all['name'].fillna('none').astype('category')
count_name = CountVectorizer(ngram_range=(1, 2))
X_name = count_name.fit_transform(df_all['name'])

# transform category_name
# use CountVectorizer
print("category_name ...")
df_all['category_name'] = df_all['category_name'].fillna('Other').astype('category')
count_category_name = CountVectorizer()
X_category_name = count_category_name.fit_transform(df_all['category_name'])

# brand_name
# use LabelBinarizer
print("brand_name ...")
df_all['brand_name'].fillna('unknown', inplace=True)
pop_brands = df_all['brand_name'].value_counts().index[:2500]
df_all.loc[~df_all['brand_name'].isin(pop_brands), 'brand_name'] = 'Other'
df_all['brand_name'] = df_all['brand_name'].astype('category')
vect_brand = LabelBinarizer(sparse_output=True)
X_brand_name = vect_brand.fit_transform(df_all['brand_name'])

# shipping & item_condition_id
print("shipping & item_condition_id...")
X_shipping_and_item_condition_id = scipy.sparse.csr_matrix(pd.get_dummies(df_all[['item_condition_id', 'shipping']], sparse=True))

# item description
# use TfidfVectorizer
print("item_description ...")
df_all['item_description'].fillna('None', inplace=True)
count_description = TfidfVectorizer(stop_words='english', ngram_range=(1, 3), max_features = 50000)
X_item_description = count_description.fit_transform(df_all['item_description'])

# all
print("hstack all columns")
X_all = scipy.sparse.hstack([X_name, X_brand_name, X_shipping_and_item_condition_id, X_category_name, X_item_description]).tocsr()

# train
print("model training...")
X_train = X_all[:nrow_train]
model = Ridge(solver='sag', fit_intercept=True)
model.fit(X_train, y_train)

# test
print("model predicting...")
X_test = X_all[nrow_train:]
preds = model.predict(X_test)

print("save preds to csv file")
df_test['price'] = np.expm1(preds)
df_test[['test_id', 'price']].to_csv('preds.csv', index=False)
print("complete!!!!")