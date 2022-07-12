import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import warnings
warnings.filterwarnings('ignore')

from sklearn.base import BaseEstimator, TransformerMixin, RegressorMixin, clone
from sklearn.decomposition import PCA, KernelPCA
from sklearn.model_selection import learning_curve
from sklearn.model_selection import ShuffleSplit
import lightgbm as lgb
from lightgbm import *

import gc, sys
gc.enable()

train_data = pd.read_csv("../input/pubg-finish-placement-prediction/train_V2.csv",encoding="utf-8")
test_data = pd.read_csv("../input/pubg-finish-placement-prediction/test_V2.csv",encoding="utf-8")

train_data = pd.get_dummies(train_data, columns=['matchType'])
test_data = pd.get_dummies(test_data, columns=['matchType'])

def reduce_mem_usage(df):
    """ iterate through all the columns of a dataframe and modify the data type
        to reduce memory usage.        
    """
    start_mem = df.memory_usage().sum() 
    print('Memory usage of dataframe is {:.2f} MB'.format(start_mem))
    
    for col in df.columns:
        col_type = df[col].dtype
        
        if col_type != object:
            c_min = df[col].min()
            c_max = df[col].max()
            if str(col_type)[:3] == 'int':
                if c_min > np.iinfo(np.int8).min and c_max < np.iinfo(np.int8).max:
                    df[col] = df[col].astype(np.int8)
                elif c_min > np.iinfo(np.int16).min and c_max < np.iinfo(np.int16).max:
                    df[col] = df[col].astype(np.int16)
                elif c_min > np.iinfo(np.int32).min and c_max < np.iinfo(np.int32).max:
                    df[col] = df[col].astype(np.int32)
                elif c_min > np.iinfo(np.int64).min and c_max < np.iinfo(np.int64).max:
                    df[col] = df[col].astype(np.int64)  
            else:
                if c_min > np.finfo(np.float16).min and c_max < np.finfo(np.float16).max:
                    df[col] = df[col].astype(np.float16)
                elif c_min > np.finfo(np.float32).min and c_max < np.finfo(np.float32).max:
                    df[col] = df[col].astype(np.float32)
                else:
                    df[col] = df[col].astype(np.float64)
        else:
            df[col] = df[col].astype('category')

    end_mem = df.memory_usage().sum() 
    print('Memory usage after optimization is: {:.2f} MB'.format(end_mem))
    print('Decreased by {:.1f}%'.format(100 * (start_mem - end_mem) / start_mem))
    
    return df

def add_feature(data):
    data['headshotrate'] = data['kills']/data['headshotKills']
    data['killStreakrate'] = data['killStreaks']/data['kills']
    data['healthitems'] = data['heals'] + data['boosts']
    data['totalDistance'] = data['rideDistance'] + data["walkDistance"] + data["swimDistance"]
    data['killPlace_over_maxPlace'] = data['killPlace'] / data['maxPlace']
    data['headshotKills_over_kills'] = data['headshotKills'] / data['kills']
    data['distance_over_weapons'] = data['totalDistance'] / data['weaponsAcquired']
    data['walkDistance_over_heals'] = data['walkDistance'] / data['heals']
    data['walkDistance_over_kills'] = data['walkDistance'] / data['kills']
    data['killsPerWalkDistance'] = data['kills'] / data['walkDistance']
    data["skill"] = data["headshotKills"] + data["roadKills"]
    data[data == np.Inf] = np.NaN
    data[data == np.NINF] = np.NaN
    data.fillna(0,inplace=True)
    return data

def outlier_detection(data):
    data["killswithoutmove"] = (data["kills"]>0) & (data["totalDistance"] ==0)
    data.drop(data[data['killswithoutmove'] == True].index, inplace=True)
    data.drop(data[(data["kills"]>=29) & (train_data["totalDistance"]<1000)].index,inplace =True)
    data.drop(data[data["headshotrate"] ==1].index,inplace=True)
    data.drop(data[data['longestKill'] >= 1000].index, inplace=True)
    data.drop(data[data['longestKill'] >= 1000].index, inplace=True)
    data.drop(data[data['rideDistance'] >= 20000].index, inplace=True)
    data.drop(data[data['swimDistance'] >= 1000].index, inplace=True)
    data.drop(data[data['weaponsAcquired'] >= 20].index, inplace=True)
    data.drop(data[data['heals'] >= 20].index, inplace=True)
    data.drop(["killswithoutmove"], axis =1,inplace=True)
    return data

train_data = add_feature(train_data)
test_data = add_feature(test_data)

#train_data = outlier_detection(train_data)

select_train_data = train_data.drop(["Id","groupId","matchId","winPlacePerc"],axis=1)
select_test_data = test_data.drop(["Id","groupId","matchId"],axis=1)

pca = PCA(n_components=51)

def pca_train_data(train_data):
    train_data_scaled=pca.fit_transform(train_data)
    return train_data_scaled

def pca_test_data(test_data):
    test_data_scaled=pca.transform(test_data)
    return test_data_scaled

train_data_processed = pca_train_data(select_train_data)
test_data_processed = pca_test_data(select_test_data)

X_train = pd.DataFrame(train_data_processed,columns=select_train_data.columns)
y_train = train_data["winPlacePerc"]
X_test = pd.DataFrame(test_data_processed,columns=select_test_data.columns)

X_train = reduce_mem_usage(X_train)
X_test = reduce_mem_usage(X_test)

Id = test_data["Id"]
del train_data
del test_data
del train_data_processed
del test_data_processed
del select_train_data
del select_test_data

'''
to_keep_1 = ['assists', 'damageDealt', 'numGroups', 'matchType_solo','headshotKills', 'DBNOs', 'matchDuration',
       'matchType_normal-solo-fpp', 'matchType_normal-solo', 'heals','boosts', 'matchType_normal-duo-fpp', 'winPoints', 
       'rankPoints','killPlace', 'longestKill', 'rideDistance', 'killPoints','revives', 'matchType_duo', 'maxPlace',
       'matchType_normal-squad-fpp', 'swimDistance', 'matchType_duo-fpp','weaponsAcquired', 'matchType_solo-fpp', 'healthitems']

X_train_keep_1 = X_train[to_keep_1]
X_test_keep_1 = X_test[to_keep_1]
'''

train_index = round(int(X_train.shape[0]*0.8))
dev_X = X_train[:train_index] 
val_X = X_train[train_index:]
dev_y = y_train[:train_index] 
val_y = y_train[train_index:] 
gc.collect();

def run_lgb(train_X, train_y, val_X, val_y, x_test):
    params = {"objective" : "regression", "metric" : "mae", 'n_estimators':20000, 'early_stopping_rounds':200,
              "num_leaves" : 31, "learning_rate" : 0.05, "bagging_fraction" : 0.7,
               "bagging_seed" : 0, "num_threads" : 4,"colsample_bytree" : 0.7
             }
    
    lgtrain = lgb.Dataset(train_X, label=train_y)
    lgval = lgb.Dataset(val_X, label=val_y)
    model = lgb.train(params, lgtrain, valid_sets=[lgtrain, lgval], early_stopping_rounds=200, verbose_eval=1000)
    
    pred_test_y = model.predict(x_test, num_iteration=model.best_iteration)
    return pred_test_y,model

pred_test,model = run_lgb(dev_X, dev_y, val_X, val_y, X_test)

df_sub = pd.read_csv("../input/pubg-finish-placement-prediction/sample_submission_V2.csv")
df_test = pd.read_csv("../input/pubg-finish-placement-prediction/test_V2.csv")
df_sub['winPlacePerc'] = pred_test
# Restore some columns
df_sub = df_sub.merge(df_test[["Id", "matchId", "groupId", "maxPlace", "numGroups"]], on="Id", how="left")

# Sort, rank, and assign adjusted ratio
df_sub_group = df_sub.groupby(["matchId", "groupId"]).first().reset_index()
df_sub_group["rank"] = df_sub_group.groupby(["matchId"])["winPlacePerc"].rank()
df_sub_group = df_sub_group.merge(
    df_sub_group.groupby("matchId")["rank"].max().to_frame("max_rank").reset_index(), 
    on="matchId", how="left")
df_sub_group["adjusted_perc"] = (df_sub_group["rank"] - 1) / (df_sub_group["numGroups"] - 1)

df_sub = df_sub.merge(df_sub_group[["adjusted_perc", "matchId", "groupId"]], on=["matchId", "groupId"], how="left")
df_sub["winPlacePerc"] = df_sub["adjusted_perc"]

# Deal with edge cases
df_sub.loc[df_sub.maxPlace == 0, "winPlacePerc"] = 0
df_sub.loc[df_sub.maxPlace == 1, "winPlacePerc"] = 1

# Align with maxPlace
# Credit: https://www.kaggle.com/anycode/simple-nn-baseline-4
subset = df_sub.loc[df_sub.maxPlace > 1]
gap = 1.0 / (subset.maxPlace.values - 1)
new_perc = np.around(subset.winPlacePerc.values / gap) * gap
df_sub.loc[df_sub.maxPlace > 1, "winPlacePerc"] = new_perc

# Edge case
df_sub.loc[(df_sub.maxPlace > 1) & (df_sub.numGroups == 1), "winPlacePerc"] = 0
assert df_sub["winPlacePerc"].isnull().sum() == 0

df_sub[["Id", "winPlacePerc"]].to_csv("submission.csv", index=False)