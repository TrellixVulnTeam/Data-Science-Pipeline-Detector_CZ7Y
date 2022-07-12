# Note: Kaggle only runs Python 3, not Python 2

# We'll use the pandas library to read CSV files into dataframes
import pandas as pd
import numpy as np
from math import fabs
import statsmodels.api as sm
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import RandomForestRegressor
from sklearn import ensemble
from sklearn import linear_model
from sklearn.linear_model import Ridge
from sklearn.linear_model import ElasticNet
from sklearn.cross_validation import train_test_split
from sklearn.cross_validation import cross_val_predict
from sklearn.ensemble import AdaBoostRegressor
from sklearn.cross_validation import cross_val_score
from sklearn import metrics
from sklearn.metrics import accuracy_score
from sklearn.metrics import roc_auc_score
from math import fabs
from sklearn.ensemble import RandomForestClassifier
from sklearn import linear_model
from sklearn.linear_model import Ridge
from sklearn.linear_model import ElasticNet
import matplotlib.pyplot as plt
#%matplotlib inline
import seaborn as sns
sns.set(color_codes=True)
train = pd.read_csv("../input/train.csv")
test  = pd.read_csv("../input/test.csv")

import numpy as np


#train['Hazard']= train['Hazard']*10


def gini(solution, submission):                                                 
    df = sorted(zip(solution, submission), key=lambda x : (x[1], x[0]),  reverse=True)
    random = [float(i+1)/float(len(df)) for i in range(len(df))]                
    totalPos = np.sum([x[0] for x in df])                                       
    cumPosFound = np.cumsum([x[0] for x in df])                                     
    Lorentz = [float(x)/totalPos for x in cumPosFound]                          
    Gini = [l - r for l, r in zip(Lorentz, random)]                             
    return np.sum(Gini)                                                         


def normalized_gini(solution, submission):                                      
    normalized_gini = gini(solution, submission)/gini(solution, solution)       
    return normalized_gini                                                      

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
    
Variable=[]
Variabletype=[]
for i in train.columns:
    if (type(train[i].head()[1]) == np.int64) == True:
        Variable.append(i)
        variabletype= 'Numerical'
        Variabletype.append(variabletype)
        
    else:
        variabletype = 'Categorical'
        Variable.append(i)
        Variabletype.append(variabletype)
    
Variablestructure= pd.DataFrame({'Variable':Variable,'Variabletype':Variabletype})        

Variablestructure_cat=Variablestructure[Variablestructure['Variabletype']=='Categorical']

for i in Variablestructure_cat['Variable']:
    train[i]=train[i].astype('category')
    

T1_V4=train['T1_V4'].unique()
repl_T1_V4= np.arange(1,len(T1_V4)+1)
table_T1_V4 = pd.DataFrame({'T1_V4':T1_V4,'repl_T1_V4':repl_T1_V4})

T1_V5=train['T1_V5'].unique()
repl_T1_V5= np.arange(1,len(T1_V5)+1)
table_T1_V5 = pd.DataFrame({'T1_V5':T1_V5,'repl_T1_V5':repl_T1_V5})

T1_V6=train['T1_V6'].unique()
repl_T1_V6= np.arange(1,len(T1_V6)+1)
table_T1_V6 = pd.DataFrame({'T1_V6':T1_V6,'repl_T1_V6':repl_T1_V6})

T1_V7=train['T1_V7'].unique()
repl_T1_V7= np.arange(1,len(T1_V7)+1)
table_T1_V7 = pd.DataFrame({'T1_V7':T1_V7,'repl_T1_V7':repl_T1_V7})

T1_V8=train['T1_V8'].unique()
repl_T1_V8= np.arange(1,len(T1_V8)+1)
table_T1_V8 = pd.DataFrame({'T1_V8':T1_V8,'repl_T1_V8':repl_T1_V8})

T1_V9=train['T1_V9'].unique()
repl_T1_V9= np.arange(1,len(T1_V9)+1)
table_T1_V9 = pd.DataFrame({'T1_V9':T1_V9,'repl_T1_V9':repl_T1_V9})

T1_V11=train['T1_V11'].unique()
repl_T1_V11= np.arange(1,len(T1_V11)+1)
table_T1_V11 = pd.DataFrame({'T1_V11':T1_V11,'repl_T1_V11':repl_T1_V11})

T1_V12=train['T1_V12'].unique()
repl_T1_V12= np.arange(1,len(T1_V12)+1)
table_T1_V12 = pd.DataFrame({'T1_V12':T1_V12,'repl_T1_V12':repl_T1_V12})

T1_V15=train['T1_V15'].unique()
repl_T1_V15= np.arange(1,len(T1_V15)+1)
table_T1_V15 = pd.DataFrame({'T1_V15':T1_V15,'repl_T1_V15':repl_T1_V15})

T1_V16=train['T1_V16'].unique()
repl_T1_V16= np.arange(1,len(T1_V16)+1)
table_T1_V16 = pd.DataFrame({'T1_V16':T1_V16,'repl_T1_V16':repl_T1_V16})

T1_V17=train['T1_V17'].unique()
repl_T1_V17= np.arange(1,len(T1_V17)+1)
table_T1_V17 = pd.DataFrame({'T1_V17':T1_V17,'repl_T1_V17':repl_T1_V17})

T2_V3=train['T2_V3'].unique()
repl_T2_V3= np.arange(1,len(T2_V3)+1)
table_T2_V3 = pd.DataFrame({'T2_V3':T2_V3,'repl_T2_V3':repl_T2_V3})

T2_V5=train['T2_V5'].unique()
repl_T2_V5= np.arange(1,len(T2_V5)+1)
table_T2_V5 = pd.DataFrame({'T2_V5':T2_V5,'repl_T2_V5':repl_T2_V5})

T2_V11=train['T2_V11'].unique()
repl_T2_V11= np.arange(1,len(T2_V11)+1)
table_T2_V11 = pd.DataFrame({'T2_V11':T2_V11,'repl_T2_V11':repl_T2_V11})

T2_V12=train['T2_V12'].unique()
repl_T2_V12= np.arange(1,len(T2_V12)+1)
table_T2_V12 = pd.DataFrame({'T2_V12':T2_V12,'repl_T2_V12':repl_T2_V12})

T2_V13=train['T2_V13'].unique()
repl_T2_V13= np.arange(1,len(T2_V13)+1)
table_T2_V13=pd.DataFrame({'T2_V13':T2_V13,'repl_T2_V13':repl_T2_V13})



train_data=pd.merge(pd.merge(pd.merge(pd.merge(pd.merge(pd.merge(pd.merge(pd.merge(pd.merge(pd.merge(pd.merge(pd.merge(pd.merge(pd.merge(pd.merge(pd.merge(train,table_T2_V13),table_T2_V12),table_T2_V11),table_T2_V5),table_T2_V3),
table_T1_V17),table_T1_V16),table_T1_V15),table_T1_V12),table_T1_V11),table_T1_V9),table_T1_V8),table_T1_V7),table_T1_V6),table_T1_V5),table_T1_V4)




train_data=pd.DataFrame(data={'Id':train_data['Id'], 'Hazard':train_data['Hazard'], 'T1_V1':train_data['T1_V1'], 'T1_V2':train_data['T1_V2'],
 'T1_V3':train_data['T1_V3'], 'T1_V4':train_data['repl_T1_V4'], 'T1_V5':train_data['repl_T1_V5'], 'T1_V6':train_data['repl_T1_V6'],
       'T1_V7':train_data['repl_T1_V7'], 'T1_V8':train_data['repl_T1_V8'], 'T1_V9':train_data['repl_T1_V9'], 'T1_V10':train_data['T1_V10'],
 'T1_V11':train_data['repl_T1_V11'], 'T1_V12':train_data['repl_T1_V12'], 'T1_V13':train_data['T1_V13'],
       'T1_V14':train_data['T1_V14'], 'T1_V15':train_data['repl_T1_V15'], 'T1_V16':train_data['repl_T1_V16'], 'T1_V17':train_data['repl_T1_V17'],
 'T2_V1':train_data['T2_V1'], 'T2_V2':train_data['T2_V2'], 'T2_V3':train_data['repl_T2_V3'],
       'T2_V4':train_data['T2_V4'], 'T2_V5':train_data['repl_T2_V5'], 'T2_V6':train_data['T2_V6'], 'T2_V7':train_data['T2_V7'],
 'T2_V8':train_data['T2_V8'], 'T2_V9':train_data['T2_V9'], 'T2_V10':train_data['T2_V10'],
       'T2_V11':train_data['repl_T2_V11'], 'T2_V12':train_data['repl_T2_V12'], 'T2_V13':train_data['repl_T2_V13'], 'T2_V14':train_data['T2_V14'], 
'T2_V15':train_data['T2_V15']})


for i in Variablestructure_cat['Variable']:
    train_data[i]=train_data[i].astype('category')


train_data_pre= train_data[['T1_V1', 'T1_V10', 'T1_V11', 'T1_V12', 'T1_V13', 'T1_V14', 'T1_V15', 'T1_V16', 'T1_V17', 
                         'T1_V2', 'T1_V3', 'T1_V4', 'T1_V5', 'T1_V6', 'T1_V7', 'T1_V8', 'T1_V9', 'T2_V1', 'T2_V10',
                         'T2_V11', 'T2_V12', 'T2_V13', 'T2_V14', 'T2_V15', 'T2_V2', 'T2_V3', 
                         'T2_V4', 'T2_V5', 'T2_V6', 'T2_V7', 'T2_V8', 'T2_V9']]

target_data=train_data[['Hazard']]

X_train_pre, X_test_pre,target_train_pre, target_test_pre =train_test_split(train_data_pre,target_data,test_size=.30,random_state=72)
X_train_pre.shape, X_test_pre.shape,target_train_pre.shape, target_test_pre.shape

from sklearn.cluster import KMeans
k_means = KMeans(n_clusters=8, n_init=10)
k_means.fit(X_train_pre)
Cluster=k_means.predict(train_data_pre)
Cluster=Cluster.tolist()

train_data['cluster']=pd.DataFrame({'cluster':Cluster})
train_data['cluster']=train_data['cluster'].astype('category')


train_data1= train_data[['T1_V1', 'T1_V10', 'T1_V11', 'T1_V12', 'T1_V13', 'T1_V14', 'T1_V15', 'T1_V16', 'T1_V17', 
                         'T1_V2', 'T1_V3', 'T1_V4', 'T1_V5', 'T1_V6', 'T1_V7', 'T1_V8', 'T1_V9', 'T2_V1', 'T2_V10',
                         'T2_V11', 'T2_V12', 'T2_V13', 'T2_V14', 'T2_V15', 'T2_V2', 'T2_V3', 
                         'T2_V4', 'T2_V5', 'T2_V6', 'T2_V7', 'T2_V8', 'T2_V9',
                         'cluster']]

target_data=train_data[['Hazard']]

#from sklearn.preprocessing import PolynomialFeatures
#poly = PolynomialFeatures(interaction_only=True)
#newdata=poly.fit_transform(train_data1)

#print(newdata.shape)
#print(newdata)
print("Stage1 clear")

X_train, X_test,target_train, target_test =train_test_split(train_data1,target_data,test_size=.30,random_state=72)
X_train.shape, X_test.shape,target_train.shape, target_test.shape


test_target_check=target_test['Hazard'].tolist()



target_test_sub=[]
for i  in range(0,len(test_target_check)):
    z=test_target_check[i]
    target_test_sub.append(z)
 
train_target_check=target_train['Hazard'].tolist()
target_train_sub=[]
for i  in range(0,len(train_target_check)):
    z=train_target_check[i]
    target_train_sub.append(z)
    
# Models 


Model=ensemble.GradientBoostingRegressor(n_estimators=50, max_depth=4,
                                learning_rate=0.1, loss='huber',
                                random_state=1)
Model.fit(X_train,target_train)
pred_val=Model.predict(X_train)
prediction_val=pred_val


Model2=linear_model.LinearRegression()
Model2.fit(X_train,target_train)
pred2_val=Model2.predict(X_train)
#prediction2_val=pred2_val

prediction2_val=[]
for i in pred2_val.tolist():
    z= i[0]
    prediction2_val.append(z)
    
Model3=RandomForestRegressor(n_estimators=50, max_depth=4)
Model3.fit(X_train,target_train)
pred3_val=Model3.predict(X_train)
prediction3_val=pred3_val

Model4=ensemble.BaggingRegressor(Model)
Model4.fit(X_train,target_train)
pred4_val=Model4.predict(X_train)
prediction4_val=pred4_val

Model5=ensemble.BaggingRegressor(Model3)
Model5.fit(X_train,target_train)
pred5_val=Model5.predict(X_train)
prediction5_val=pred5_val

#print(prediction5_val)

pred=Model.predict(X_test)
prediction=pred

pred2=Model2.predict(X_test)
#prediction2=pred2

prediction2=[]
for i in pred2.tolist():
    z= i[0]
    prediction2.append(z)

pred3=Model3.predict(X_test)
prediction3=pred3

pred4=Model4.predict(X_test)
prediction4=pred4

pred5=Model5.predict(X_test)
prediction5=pred5



print("Model clear")


Eval_val=pd.DataFrame()
Eval_val['Gra_Pred']=pd.DataFrame({'Gra_Pred':prediction_val})
Eval_val['Reg_Pred']=pd.DataFrame({'Reg_Pred':prediction2_val})
Eval_val['ET_Pred']=pd.DataFrame({'ET_Pred':prediction3_val})
Eval_val['Bag_Pred']=pd.DataFrame({'Bag_Pred':prediction4_val})
Eval_val['Bag_GB_Pred']=pd.DataFrame({'Bag_GB_Pred':prediction4_val})
Eval_val['Hazard']=pd.DataFrame({'Hazard':target_train_sub})
Eval_val['total']= abs((Eval_val['Gra_Pred']+Eval_val['Reg_Pred']+Eval_val['ET_Pred'])/3)
Eval_val['Gra_resi']=abs(Eval_val['Gra_Pred']-Eval_val['Hazard'])
Eval_val['Reg_resi']=abs(Eval_val['Reg_Pred']-Eval_val['Hazard'])
Eval_val['ET_resi']=abs(Eval_val['ET_Pred']-Eval_val['Hazard'])
Eval_val['Bag_resi']=abs(Eval_val['Bag_Pred']-Eval_val['Hazard'])
Eval_val['Bag_GB_resi']=abs(Eval_val['Bag_GB_Pred']-Eval_val['Hazard'])
Eval_val['total_resi']= abs((Eval_val['total']-Eval_val['Hazard']))
Eval_val['Gra_Pred']=Eval_val['Gra_Pred'].round(0)
Eval_val['Reg_Pred']=Eval_val['Reg_Pred'].round(0)
Eval_val['total']=Eval_val['total'].round(0)
Eval_val['Bag_Pred']=Eval_val['Bag_Pred'].round(0)
Eval_val['Bag_GB_Pred']=Eval_val['Bag_Pred'].round(0)
print(Eval_val.head(10))

print(sum(Eval_val['total_resi']))

from scipy.stats import probplot
probplot(Eval_val['Gra_resi'],plot=plt)


from scipy.stats import probplot
probplot(Eval_val['Reg_resi'],plot=plt)



from scipy.stats import probplot
probplot(Eval_val['total_resi'],plot=plt)

from scipy.stats import probplot
probplot(Eval_val['ET_resi'],plot=plt)  



"GRadient",normalized_gini(Eval_val['Hazard'],Eval_val['Gra_Pred']),"Reg",normalized_gini(Eval_val['Hazard'],Eval_val['Reg_Pred']),"ET",normalized_gini(Eval_val['Hazard'],Eval_val['ET_Pred']),"Total",normalized_gini(Eval_val['Hazard'],Eval_val['total'])

"GRadient",Gini(Eval_val['Hazard'],Eval_val['Gra_Pred']),"ET",Gini(Eval_val['Hazard'],Eval_val['ET_Pred']),"Reg",Gini(Eval_val['Hazard'],Eval_val['Reg_Pred']),"Total",Gini(Eval_val['Hazard'],Eval_val['total'])

Eval_test=pd.DataFrame()
Eval_test['GB_pred']=pd.DataFrame({'GB_pred':prediction})
Eval_test['LR_pred']=pd.DataFrame({'LR_pred':prediction2})
Eval_test['ET_pred']=pd.DataFrame({'ET_pred':prediction3})
Eval_test['Bag_pred']=pd.DataFrame({'Bag_pred':prediction4})
Eval_test['Bag_pred']=pd.DataFrame({'Bag_pred':prediction4})
Eval_test['Bag_pred']=pd.DataFrame({'Bag_pred':prediction4})
Eval_test['total_pred']=abs((Eval_test['GB_pred']+ Eval_test['LR_pred']+Eval_test['ET_pred'])/3)
Eval_test['Hazard']=pd.DataFrame({'Hazard':target_test_sub})
Eval_test['Bag_GB_pred']=pd.DataFrame({'Bag_GB_pred':prediction5})
Eval_test['GB_resi']=abs(Eval_test['GB_pred']-Eval_test['Hazard'])
Eval_test['LR_resi']=abs(Eval_test['LR_pred']-Eval_test['Hazard'])
Eval_test['ET_resi']=abs(Eval_test['ET_pred']-Eval_test['Hazard'])
Eval_test['Bag_resi']=abs(Eval_test['Bag_pred']-Eval_test['Hazard'])
Eval_test['Bag_GB_resi']=abs(Eval_test['Bag_GB_pred']-Eval_test['Hazard'])
Eval_test['total_resi']=abs(Eval_test['total_pred']-Eval_test['Hazard'])

print(Eval_test.head(10))

from scipy.stats import probplot
probplot(Eval_test['ET_resi'],plot=plt)

from scipy.stats import probplot
probplot(Eval_test['GB_resi'],plot=plt)

from scipy.stats import probplot
probplot(Eval_test['LR_resi'],plot=plt)

from scipy.stats import probplot
probplot(Eval_test['total_resi'],plot=plt)

print("GRadient",normalized_gini(Eval_test['Hazard'],Eval_test['GB_pred']))
print("LR",normalized_gini(Eval_test['Hazard'],Eval_test['LR_pred']))
print("RR",normalized_gini(Eval_test['Hazard'],Eval_test['ET_pred']))
print("Bag",normalized_gini(Eval_test['Hazard'],Eval_test['Bag_pred']))
print("total",normalized_gini(Eval_test['Hazard'],Eval_test['total_pred']))
print("Bag_GB",normalized_gini(Eval_test['Hazard'],Eval_test['Bag_GB_pred']))

print("GRadient",Gini(Eval_test['Hazard'],Eval_test['GB_pred']))
print("LR",Gini(Eval_test['Hazard'],Eval_test['LR_pred']))
print("RR",Gini(Eval_test['Hazard'],Eval_test['ET_pred']))
print("Bag",Gini(Eval_test['Hazard'],Eval_test['Bag_pred']))
print("total",Gini(Eval_test['Hazard'],Eval_test['total_pred']))
print("Bag_GB",Gini(Eval_test['Hazard'],Eval_test['Bag_GB_pred']))