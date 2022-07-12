# -*- coding: utf-8 -*-
"""

@author Ajoo
forked from Adam Gągol's script based on Elena Cuoco's

"""

import numpy as np
import pandas as pd
from scipy.signal import butter, lfilter
from sklearn.linear_model import LogisticRegression
from sklearn.lda import LDA
from sklearn.qda import QDA
from sklearn.preprocessing import StandardScaler
 
#############function to read data###########
FNAME = "../input/{0}/subj{1}_series{2}_{3}.csv"
def load_data(subj, series=range(1,9), prefix = 'train'):
    data = [pd.read_csv(FNAME.format(prefix,subject,s,'data'), index_col=0) for s in series]
    idx = [d.index for d in data]
    data = [d.values.astype(float) for d in data]
    if prefix == 'train':
        events = [pd.read_csv(FNAME.format(prefix,subject,s,'events'), index_col=0).values for s in series]
        return data, events
    else:
        return data, idx

def compute_features(X, scale=None):
    X = [x[:,0:4] for x in X]
    
    b,a = butter(3, 1/250.0, btype='lowpass')
    F = np.concatenate([lfilter(b,a,x) for x in X])

    F = np.concatenate((np.concatenate(X), F, F**2),axis=1)
    if scale is None:    
        scale = StandardScaler()
        F = scale.fit_transform(F)
        return F, scale
    else:
        F = scale.transform(F)
        return F


#%%########### Initialize ####################################################
cols = ['HandStart','FirstDigitTouch',
        'BothStartLoadPhase','LiftOff',
        'Replace','BothReleased']

subjects = range(1,13)
idx_tot = []
scores_tot = []

###loop on subjects and 8 series for train data + 2 series for test data
for subject in subjects:

    X_train, y = load_data(subject)
    X_test, idx = load_data(subject,[9,10],'test')

################ Train classifiers ###########################################
    #lda = LDA()
    lr = LogisticRegression()
    
    X_train, scaler = compute_features(X_train)
    X_test = compute_features(X_test, scaler)   #pass the learned mean and std to normalized test data
    
    y = np.concatenate(y,axis=0)
    scores = np.empty((X_test.shape[0],6))
    
    downsample = 50
    for i in range(6):
        print('Train subject %d, class %s' % (subject, cols[i]))
        lr.fit(X_train[::downsample,:], y[::downsample,i])
        #lda.fit(X_train[::downsample,:], y[::downsample,i])
       
        scores[:,i] = 1*lr.predict_proba(X_test)[:,1]# + 0.5*lda.predict_proba(X_test)[:,1]

    scores_tot.append(scores)
    idx_tot.append(np.concatenate(idx))
    
#%%########### submission file ################################################
submission_file = 'Submission.csv'
# create pandas object for submission
submission = pd.DataFrame(index=np.concatenate(idx_tot),
                          columns=cols,
                          data=np.concatenate(scores_tot))

# write file
submission.to_csv(submission_file,index_label='id',float_format='%.3f')