import pandas as pd
import numpy as np

from sklearn.metrics import roc_auc_score
from sklearn.linear_model import LogisticRegression
from sklearn import metrics

from sklearn.model_selection import train_test_split
# Input data files are available in the "../input/" directory.
# For example, running this (by clicking run or pressing Shift+Enter) will list the files in the input directory

import os
print(os.listdir("../input"))

# Any results you write to the current directory are saved as output.


train_df = pd.read_csv('../input/train.csv')
test_df = pd.read_csv('../input/test.csv')

X = train_df.drop(['ID_code','target'], axis=1) # Features
y = train_df.target.values # Target variable

X_test_pred = test_df.drop(['ID_code'], axis=1)

target_count = train_df.target.value_counts()
print('Class 0:', target_count[0])
print('Class 1:', target_count[1])
target_count.plot(kind='bar', title='Count (target)');

# Clases
count_class_0, count_class_1 = train_df.target.value_counts()

# Divide las clases
df_class_0 = train_df[train_df['target'] == 0]
df_class_1 = train_df[train_df['target'] == 1]

#Under sampling
df_class_0_under = df_class_0.sample(count_class_1)
df_test_under = pd.concat([df_class_0_under, df_class_1], axis=0)
print('Random under-sampling:')
print(df_test_under.target.value_counts())

#Over sampling
df_class_1_over = df_class_1.sample(count_class_0, replace=True)
df_test_over = pd.concat([df_class_0, df_class_1_over], axis=0)
print('Random over-sampling:')
print(df_test_over.target.value_counts())

X = df_test_under.drop(['ID_code','target'], axis=1) # Features
y = df_test_under.target.values # Target variable

#Sigue....

#Dividimos X e y en datos de entrenamiento y prueba
X_train,X_test,y_train,y_test=train_test_split(X,y,test_size=0.2,random_state=0)

#entrenamos el modelo
logist_reg = LogisticRegression()
logist_reg.fit(X_train,y_train)
#prediccion
y_pred=logist_reg.predict(X_test)

##Evaluacion del modelo
from sklearn import metrics
cnf_matrix = metrics.confusion_matrix(y_test, y_pred)
cnf_matrix

print("Accuracy:",metrics.accuracy_score(y_test, y_pred))
print("Precision:",metrics.precision_score(y_test, y_pred))
print("Recall:",metrics.recall_score(y_test, y_pred))


import matplotlib.pyplot as plt
import seaborn as sns

#ROC
y_pred_proba = logist_reg.predict_proba(X_test)[::,1]
fpr, tpr, _ = metrics.roc_curve(y_test,  y_pred_proba)
auc = metrics.roc_auc_score(y_test, y_pred_proba)
plt.plot(fpr,tpr,label="data 1, auc="+str(auc))
plt.legend(loc=4)
plt.show()

y_pred_test = logist_reg.predict(X_test_pred)
#creacion del archivo
submission = pd.DataFrame({'ID_code':test_df.ID_code,'target':y_pred_test})
submission.to_csv('submission.csv', index=False)