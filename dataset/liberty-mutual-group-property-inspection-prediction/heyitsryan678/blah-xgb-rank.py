'''


Based on Abhishek Catapillar benchmark
https://www.kaggle.com/abhishek/caterpillar-tube-pricing/beating-the-benchmark-v1-0

@Soutik

Have fun;)
'''

import pandas as pd
import numpy as np 
from sklearn import preprocessing
import xgboost as xgb
from sklearn.feature_extraction import DictVectorizer
from scipy.stats import rankdata

def xgboost_pred(train,labels,test):
	params = {}
	params["objective"] = "reg:linear"
	params["eta"] = 0.005
	params["min_child_weight"] = 6
	params["subsample"] = 0.7
	params["colsample_bytree"] = 0.7
	params["scale_pos_weight"] = 1
	params["silent"] = 1
	params["max_depth"] = 9
    
    
	plst = list(params.items())

	#Using 5000 rows for early stopping. 
	offset = 4000

	num_rounds = 10000
	xgtest = xgb.DMatrix(test)

	#create a train and validation dmatrices 
	xgtrain = xgb.DMatrix(train[offset:,:], label=labels[offset:])
	xgval = xgb.DMatrix(train[:offset,:], label=labels[:offset])

	#train using early stopping and predict
	watchlist = [(xgtrain, 'train'),(xgval, 'val')]
	model = xgb.train(plst, xgtrain, num_rounds, watchlist, early_stopping_rounds=120)
	preds1 = model.predict(xgval,ntree_limit=model.best_iteration)


	#reverse train and labels and use different 5k for early stopping. 
	# this adds very little to the score but it is an option if you are concerned about using all the data. 
	train = train[::-1,:]
	labels = np.log(labels[::-1])

	xgtrain = xgb.DMatrix(train[offset:,:], label=labels[offset:])
	xgval = xgb.DMatrix(train[:offset,:], label=labels[:offset])

	watchlist = [(xgtrain, 'train'),(xgval, 'val')]
	model = xgb.train(plst, xgtrain, num_rounds, watchlist, early_stopping_rounds=120)
	preds2 = model.predict(xgval,ntree_limit=model.best_iteration)


	#combine predictions
	#since the metric only cares about relative rank we don't need to average
	preds = preds1*1.4 + preds2*8.6
	return preds

#load train and test 
train  = pd.read_csv('../input/train.csv', index_col=0)
test  = pd.read_csv('../input/test.csv', index_col=0)


labels = train.Hazard
train.drop('Hazard', axis=1, inplace=True)

train_s = train
test_s = test


train_s.drop('T2_V10', axis=1, inplace=True)
train_s.drop('T2_V7', axis=1, inplace=True)
train_s.drop('T1_V13', axis=1, inplace=True)
train_s.drop('T1_V10', axis=1, inplace=True)

test_s.drop('T2_V10', axis=1, inplace=True)
test_s.drop('T2_V7', axis=1, inplace=True)
test_s.drop('T1_V13', axis=1, inplace=True)
test_s.drop('T1_V10', axis=1, inplace=True)

columns = train.columns
test_ind = test.index


train_s1 = np.array(train_s)
test_s1 = np.array(test_s)

# label encode the categorical variables
for i in range(train_s1.shape[1]):
    lbl = preprocessing.LabelEncoder()
    lbl.fit(list(train_s1[:,i]) + list(test_s1[:,i]))
    train_s1[:,i] = lbl.transform(train_s1[:,i])
    test_s1[:,i] = lbl.transform(test_s1[:,i])

train_s1 = train_s1.astype(float)
test_s1 = test_s1.astype(float)


preds1 = xgboost_pred(train_s1,labels,test_s1)

#model_2 building

train = train_s.T.to_dict().values()
test = test_s.T.to_dict().values()

vec = DictVectorizer()
train = vec.fit_transform(train)
test = vec.transform(test)

preds2 = xgboost_pred(train,labels,test)


preds = 0.47 * (preds1**0.4) + 0.53 * (preds2**0.4)

def Gini(y_true, y_pred):
    # check and get number of samples
    assert y_true.shape == y_pred.shape
    n_samples = y_true.shape[0]
    
    # sort rows on prediction column 
    # (from largest to smallest)
    arr = np.array([y_true, y_pred]).transpose()
    true_order = arr[arr[:,0].argsort()][::-1,0]
    pred_order = arr[arr[:,1].argsort()][::-1,0]
    
    # get Lorenz curves
    L_true = np.cumsum(true_order) / np.sum(true_order)
    L_pred = np.cumsum(pred_order) / np.sum(pred_order)
    L_ones = np.linspace(0, 1, n_samples)
    
    # get Gini coefficients (area between curves)
    G_true = np.sum(L_ones - L_true)
    G_pred = np.sum(L_ones - L_pred)
    
    # normalize to true Gini coefficient
    return G_pred/G_true

act = labels[:4000]
gs = Gini(act,preds)
print(gs)

#generate solution
#preds = pd.DataFrame({"Id": test_ind, "Hazard": preds})
#preds = preds.set_index('Id')
#preds.to_csv('xgboost_benchmark_kk_ranked.csv')