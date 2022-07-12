# This script creates and evaluates an adaboost model in Python for the 'San Francisco Crime Classification' competition.
# This iteration is only to get the model up and running, so there is minimal feature engineering and parameter tuning.

# Import modules.
import pandas as pd
from sklearn import preprocessing, cross_validation
from sklearn.ensemble import AdaBoostClassifier
from sklearn.tree import DecisionTreeClassifier

# Import training and test data.
train = pd.read_csv('../input/train.csv')
test = pd.read_csv('../input/test.csv')

# PRE-PROCESSING AND FEATURE ENGINEERING.

# Rename columns of training and testing data set.
train.columns = ['date', 'category_predict', 'description_ignore', 'day_of_week', 'pd_district', 'resolution', 'address', 'x', 'y']
test.columns = ['id', 'date', 'day_of_week', 'pd_district', 'address', 'x', 'y']

# Get hour of each crime.
train['hour'] = train['date'].str[11:13]
test['hour'] = test['date'].str[11:13]

# Convert categorical variables ('day_of_week' and 'pd_district') to numerical labels to add to 'train' and 'test'.
# The scikit-learn implementation of random forest apparently can't handle character strings...
day_of_week_encoded = preprocessing.LabelEncoder()
day_of_week_encoded.fit(train['day_of_week'])
train['day_of_week_encoded'] = day_of_week_encoded.transform(train['day_of_week'])

pd_district_encoded = preprocessing.LabelEncoder()
pd_district_encoded.fit(train['pd_district'])
train['pd_district_encoded'] = pd_district_encoded.transform(train['pd_district'])

day_of_week_encoded = preprocessing.LabelEncoder()
day_of_week_encoded.fit(test['day_of_week'])
test['day_of_week_encoded'] = day_of_week_encoded.transform(test['day_of_week'])

pd_district_encoded = preprocessing.LabelEncoder()
pd_district_encoded.fit(test['pd_district'])
test['pd_district_encoded'] = pd_district_encoded.transform(test['pd_district'])

# Create data subset to train model on (training on full data set throws a memory error).
# 'subset' contains at least 1 example of every crime category.
subset = train.iloc[:30000]
subset = subset.append(train.iloc[[30023, 33953, 37297, 41096, 41979, 44478, 48706, 48836, 49305, 53714, 93716, 102636, 102644, 102677, 102918, 103516, 103711, 107733, 148475, 148475, 
                   192190, 205045, 252093, 279791, 316490, 317526, 332820, 337880]])

# CREATE MODEL AND PREDICTIONS.

# Create classifier.
adaboost = AdaBoostClassifier(DecisionTreeClassifier(max_depth = 5),
                              n_estimators = 100,
                              learning_rate = 1.5, 
                              random_state = 1)

# Fit classifier on 'subset' (fitting on 'train' throws a memory error).
adaboost.fit(subset[['day_of_week_encoded', 'pd_district_encoded', 'x', 'y', 'hour']],
       subset['category_predict'])

# Generate predictions for training ('subset') and test data.
# For training data, I want accuracy.
# For test data, the submission format is specified by Kaggle.com.
# I comment out the creation of the test predictions because it throws a memory error.
subset['pred'] = adaboost.predict(subset[['day_of_week_encoded', 'pd_district_encoded', 'x', 'y', 'hour']])
# test_pred = adaboost.predict_proba(test[['day_of_week_encoded', 'pd_district_encoded', 'x', 'y', 'hour']])

# CHECK TRAINING SET ACCURACY.

# Compute training set accuracy.
print('Training Set Accuracy :', sum(subset['category_predict'] == subset['pred']) / len(subset['date']))

# CROSS VALIDATION.

# Get cross validation scores.
cv_scores = cross_validation.cross_val_score(adaboost,
                                             subset[['day_of_week_encoded', 'pd_district_encoded', 'x', 'y', 'hour']],
                                             subset['category_predict'],
                                             cv = 2)

# Take the mean accuracy across all cross validation segments.
print('Cross Validation Accuracy: ', cv_scores.mean())
                                            
# EXPORT TEST SET PREDICTIONS.
# This section exports test predictions to a csv in the format specified by Kaggle.com.
# This section is commented out because the test predictions can't be generated (memory error).

# Turn 'test_pred' into data frame.
# test_pred = pd.DataFrame(test_pred)

# Add column names to 'test_pred'.
# test_pred.columns = nb.classes_

# Name index column.
# test_pred.index.name = 'Id'

# Write csv.
# This is commented out because I don't actually want to create a csv right now.
# test_pred.to_csv('test_pred_benchmark_nb.csv')
