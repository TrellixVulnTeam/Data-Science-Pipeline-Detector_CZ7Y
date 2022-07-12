import time
start_time = time.time()

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, BaggingRegressor
from sklearn import decomposition, pipeline, metrics, grid_search
from sklearn.metrics import mean_squared_error, make_scorer
from nltk.metrics import edit_distance
from nltk.corpus import stopwords
from nltk.stem.porter import *
stemmer = PorterStemmer()
import re, math
#import enchant
import random
from collections import Counter

random.seed(1966)
cachedStopWords = stopwords.words("english")
WORD = re.compile(r'\w+')

df_train = pd.read_csv('../input/train.csv', encoding="ISO-8859-1")
df_test = pd.read_csv('../input/test.csv', encoding="ISO-8859-1")
df_pro_desc = pd.read_csv('../input/product_descriptions.csv')
df_attr = pd.read_csv('../input/attributes.csv')
df_brand = df_attr[df_attr.name == "MFG Brand Name"][["product_uid", "value"]].rename(columns={"value": "brand"})

num_train = df_train.shape[0]

def get_cosine(vec1, vec2):
     intersection = set(vec1.keys()) & set(vec2.keys())
     numerator = sum([vec1[x] * vec2[x] for x in intersection])
     sum1 = sum([vec1[x]**2 for x in vec1.keys()])
     sum2 = sum([vec2[x]**2 for x in vec2.keys()])
     denominator = math.sqrt(sum1) * math.sqrt(sum2)
     if not denominator:
        return 0.0
     else:
        return float(numerator) / denominator

def text_to_vector(text):
     words = WORD.findall(text)
     return Counter(words)

def calculate_similarity(str1,str2):
    vector1 = text_to_vector(str1)
    vector2 = text_to_vector(str2)
    return get_cosine(vector1, vector2)
    
def str_stem(s): 
    if isinstance(s, str):
        s = s.replace("''","in.") # character
        s = s.replace("'","in.") # character
        s = s.replace("inches","in.") # whole word
        s = s.replace("inch","in.") # whole word
        s = s.replace(" in ","in. ") # no period
        s = s.replace(" in.","in.") # prefix space
        
        s = s.replace("''","ft.") # character
        s = s.replace(" feet ","ft. ") # whole word
        s = s.replace("feet","ft.") # whole word
        s = s.replace("foot","ft.") # whole word
        s = s.replace(" ft ","ft. ") # no period
        s = s.replace("ft"," ft. ") # no period
        s = s.replace(" ft.","ft.") # prefix space
        
        s = s.replace(" pounds ","lb. ") # character
        s = s.replace(" pound ","lb. ") # whole word
        s = s.replace("pound","lb.") # whole word
        s = s.replace(" lb ","lb. ") # no period
        s = s.replace(" lb.","lb.") # prefix space
        s = s.replace(" lbs ","lbs. ") # no period
        
        s = s.replace(" sq ft "," sq. ft. ") # whole word
        s = s.replace(" sq ft"," sq. ft. ") # whole word
        s = s.replace("sq ft","sq. ft.") # whole word
        s = s.replace("sqft"," sq. ft. ") # whole word
        s = s.replace(" sqft ","sq. ft. ") # no period
        s = s.replace("sq. ft","sq. ft.") # whole word
        s = s.replace("sq ft.","sq. ft.") # whole word
        s = s.replace("sq feet","sq. ft.") # whole word
        
        s = s.replace(" gallons "," gal. ") # character
        s = s.replace(" gallon "," gal. ") # whole word
        s = s.replace("gallons"," gal.") # character
        s = s.replace("gallon"," gal.") # whole word
        s = s.replace(" gal "," gal. ") # character
        s = s.replace(" gal"," gal.") # whole word
        
        s = s.replace(" amps "," Amp ") # character
        s = s.replace(" amps","Amp ") # whole word	
        
        #regex for 4x2 split and UoM
        #volts, watts, amps, mm, sq ft, cm, gallons
        
        return " ".join([stemmer.stem(re.sub('[^A-Za-z0-9-./]', ' ', word)) for word in s.lower().split()])
    else:
        return "null"

def str_common_word(str1, str2):
    str1, str2 = str1.lower(), str2.lower()
    words, cnt, words2 = str1.split(), 0, str2.split()
    for word in words:
        if len(words2)<10 and len(words)<4:
            for word2 in words2:
                if edit_distance(word, word2, transpositions=False) <= 1:
                    cnt+=1
        else:
            if str2.find(word)>=0:
                cnt+=1
    return cnt

def str_whole_word(str1, str2, i_):
    str1, str2 = str1.lower().strip(), str2.lower().strip()
    cnt = 0
    while i_ < len(str2):
        i_ = str2.find(str1, i_)
        if i_ == -1:
            return cnt
        else:
            cnt += 1
            i_ += len(str1)
    return cnt

def fmean_squared_error(ground_truth, predictions):
    fmean_squared_error_ = mean_squared_error(ground_truth, predictions)**0.1
    return fmean_squared_error_

df_all = pd.concat((df_train, df_test), axis=0, ignore_index=True)
df_all = pd.merge(df_all, df_pro_desc, how='left', on='product_uid')
df_all = pd.merge(df_all, df_brand, how='left', on='product_uid')

print("Stemming...")
df_all['search_term'] = df_all['search_term'].map(lambda x:str_stem(x))
df_all['product_title'] = df_all['product_title'].map(lambda x:str_stem(x))
df_all['product_description'] = df_all['product_description'].map(lambda x:str_stem(x))

print("Creating features...")
df_all['brand'] = df_all['brand'].map(lambda x:str_stem(x))
df_all['len_of_query'] = df_all['search_term'].map(lambda x:len(x.split())).astype(np.int64)
df_all['len_of_title'] = df_all['product_title'].map(lambda x:len(x.split())).astype(np.int64)
df_all['len_of_description'] = df_all['product_description'].map(lambda x:len(x.split())).astype(np.int64)
df_all['len_of_brand'] = df_all['brand'].map(lambda x:len(x.split())).astype(np.int64)
df_all['product_info'] = df_all['search_term']+"\t"+df_all['product_title'] +"\t"+df_all['product_description']+"\t"+df_all['brand']
df_all['query_in_title'] = df_all['product_info'].map(lambda x:str_whole_word(x.split('\t')[0],x.split('\t')[1],0))
df_all['query_in_description'] = df_all['product_info'].map(lambda x:str_whole_word(x.split('\t')[0],x.split('\t')[2],0))
df_all['word_in_title'] = df_all['product_info'].map(lambda x:str_common_word(x.split('\t')[0],x.split('\t')[1]))
df_all['word_in_description'] = df_all['product_info'].map(lambda x:str_common_word(x.split('\t')[0],x.split('\t')[2]))
df_all['ratio_title'] = df_all['word_in_title']/df_all['len_of_query']
df_all['ratio_description'] = df_all['word_in_description']/df_all['len_of_query']
df_all['attr'] = df_all['search_term']+"\t"+df_all['brand']
df_all['word_in_brand'] = df_all['attr'].map(lambda x:str_common_word(x.split('\t')[0],x.split('\t')[1]))
df_all['ratio_brand'] = df_all['word_in_brand']/df_all['len_of_brand']

print("Creating similarity features...")
df_all['similarity_in_title']=df_all['product_info'].map(lambda x:calculate_similarity(x.split('\t')[0],x.split('\t')[1]))
df_all['similarity_in_description']=df_all['product_info'].map(lambda x:calculate_similarity(x.split('\t')[0],x.split('\t')[2]))
df_all['similarity_in_brand']=df_all['product_info'].map(lambda x:calculate_similarity(x.split('\t')[0],x.split('\t')[3]))

df_all = df_all.drop(['search_term','product_title','product_description','product_info','attr','brand'],axis=1)
df_all.head()
#print (df_all[:10])
#print("--- Features Set: %s minutes ---" % ((time.time() - start_time)/60))

df_train = df_all.iloc[:num_train]
df_test = df_all.iloc[num_train:]
id_test = df_test['id']
y_train = df_train['relevance'].values
X_train = df_train.drop(['id','relevance'],axis=1).values
X_test = df_test.drop(['id','relevance'],axis=1).values

RMSE  = make_scorer(fmean_squared_error, greater_is_better=False)
rfr = GradientBoostingRegressor(loss = 'huber', learning_rate = 0.1, verbose = 1, random_state = 21)
clf = pipeline.Pipeline([('rfr', rfr)])
param_grid = {'rfr__n_estimators' : [300],# 300 top
              'rfr__max_depth': [8], #list(range(7,8,1))
            }
model = grid_search.GridSearchCV(estimator = clf, param_grid = param_grid, n_jobs = -1, cv = 10, verbose = 150, scoring=RMSE)
model.fit(X_train, y_train)

print("Best parameters found by grid search:")
print(model.best_params_)
print("Best CV score:")
print(model.best_score_)

y_pred = model.predict(X_test)
print(len(y_pred))
pd.DataFrame({"id": id_test, "relevance": y_pred}).to_csv('submit_brandfeat.csv',index=False)
print("--- Training & Testing: %s minutes ---" % ((time.time() - start_time)/60))