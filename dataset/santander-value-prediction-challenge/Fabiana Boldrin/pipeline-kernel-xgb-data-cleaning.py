#!/usr/bin/env python3

import numpy as np
import pandas as pd
import xgboost as xgb
from scipy.stats import skew, kurtosis

from sklearn.base import BaseEstimator, TransformerMixin, RegressorMixin
from sklearn.base import clone, is_classifier
from sklearn.model_selection._split import check_cv

from sklearn.feature_selection import VarianceThreshold
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline, FeatureUnion


class UniqueTransformer(BaseEstimator, TransformerMixin):
    
    def __init__(self, axis=1, accept_sparse=False):
        if axis == 0:
            raise NotImplementedError('axis is 0! Not implemented!')
        if accept_sparse:
            raise NotImplementedError('accept_sparse is True! Not implemented!')
        self.axis = axis
        self.accept_sparse = accept_sparse
        
    def fit(self, X, y=None):
        _, self.unique_indices_ = np.unique(X, axis=self.axis, return_index=True)
        return self
    
    def transform(self, X, y=None):
        return X[:, self.unique_indices_]


class StatsTransformer(BaseEstimator, TransformerMixin):
    
    def __init__(self, stat_funs=None):
        self.stat_funs = stat_funs
    
    def _get_stats(self, row):
        stats = []
        for fun in self.stat_funs:
            stats.append(fun(row))
        return stats
    
    def fit(self, X, y=None):
        return self
    
    def transform(self, X, y=None):
        return np.apply_along_axis(self._get_stats, arr=X, axis=1)


class ClassifierTransformer(BaseEstimator, TransformerMixin):
    
    def __init__(self, estimator=None, n_classes=2, cv=3):
        self.estimator = estimator
        self.n_classes = n_classes
        self.cv = cv
    
    def _get_labels(self, y):
        y_labels = np.zeros(len(y))
        y_us = np.sort(np.unique(y))
        step = int(len(y_us) / self.n_classes)
        
        for i_class in range(self.n_classes):
            if i_class + 1 == self.n_classes:
                y_labels[y >= y_us[i_class * step]] = i_class
            else:
                y_labels[
                    np.logical_and(
                        y >= y_us[i_class * step],
                        y < y_us[(i_class + 1) * step]
                    )
                ] = i_class
        return y_labels
        
    def fit(self, X, y):
        y_labels = self._get_labels(y)
        cv = check_cv(self.cv, y_labels, classifier=is_classifier(self.estimator))
        self.estimators_ = []
        
        for train, _ in cv.split(X, y_labels):
            self.estimators_.append(
                clone(self.estimator).fit(X[train], y_labels[train])
            )
        return self
    
    def transform(self, X, y=None):
        cv = check_cv(self.cv, y, classifier=is_classifier(self.estimator))
        
        X_prob = np.zeros((X.shape[0], self.n_classes))
        X_pred = np.zeros(X.shape[0])
        
        for estimator, (_, test) in zip(self.estimators_, cv.split(X)):
            X_prob[test] = estimator.predict_proba(X[test])
            X_pred[test] = estimator.predict(X[test])
        return np.hstack([X_prob, np.array([X_pred]).T])

class XGBRegressorCV(BaseEstimator, RegressorMixin):
    
    def __init__(self, xgb_params=None, fit_params=None, cv=3):
        self.xgb_params = xgb_params
        self.fit_params = fit_params
        self.cv = cv
    
    @property
    def feature_importances_(self):
        feature_importances = []
        for estimator in self.estimators_:
            feature_importances.append(
                estimator.feature_importances_
            )
        return np.mean(feature_importances, axis=0)
    
    @property
    def evals_result_(self):
        evals_result = []
        for estimator in self.estimators_:
            evals_result.append(
                estimator.evals_result_
            )
        return np.array(evals_result)
    
    @property
    def best_scores_(self):
        best_scores = []
        for estimator in self.estimators_:
            best_scores.append(
                estimator.best_score
            )
        return np.array(best_scores)
    
    @property
    def cv_scores_(self):
        return self.best_scores_ 
    
    @property
    def cv_score_(self):
        return np.mean(self.best_scores_)
    
    @property
    def best_iterations_(self):
        best_iterations = []
        for estimator in self.estimators_:
            best_iterations.append(
                estimator.best_iteration
            )
        return np.array(best_iterations)
    
    @property
    def best_iteration_(self):
        return np.round(np.mean(self.best_iterations_))
    
    def fit(self, X, y, **fit_params):
        cv = check_cv(self.cv, y, classifier=False)
        self.estimators_ = []
        
        for train, valid in cv.split(X, y):
            self.estimators_.append(
                xgb.XGBRegressor(**self.xgb_params).fit(
                    X[train], y[train],
                    eval_set=[(X[valid], y[valid])],
                    **self.fit_params
                )
            )

        return self
    
    def predict(self, X):
        y_pred = []
        for estimator in self.estimators_:
            y_pred.append(estimator.predict(X))
        return np.mean(y_pred, axis=0)


def get_stat_funs():
    
    def get_percentiles():
        percentiles = []
        for q in np.arange(0.1, 1.0, 0.1):
            percentiles.append(lambda x: np.percentile(x, q=q))
        return percentiles

    stat_funs = []
    stats = [len, np.min, np.max, np.mean, np.std, skew, kurtosis] + get_percentiles()
    
    for stat in stats:
        stat_funs.append(
            lambda x: -1 if x[x != 0.0].size == 0 else stat(x[x != 0.0])
        )
        stat_funs.append(
            lambda x: -1 if np.unique(x[x != 0.0]).size == 0 else stat(np.unique(x[x != 0.0]))
        )
        stat_funs.append(
            lambda x: -1 if np.diff(x[x != 0.0]).size == 0 else stat(np.diff(x[x != 0.0]))
        )
        stat_funs.append(
            lambda x: -1 if np.diff(np.unique(x[x != 0.0])).size == 0 else stat(np.diff(np.unique(x[x != 0.0])))
        )
    
    return stat_funs
    
def add_SumZeros(train, test, features):
    flist = [x for x in train.columns if not x in ['ID','target']]
    if 'SumZeros' in features:
        train.insert(1, 'SumZeros', (train[flist] == 0).astype(int).sum(axis=1))
        test.insert(1, 'SumZeros', (test[flist] == 0).astype(int).sum(axis=1))
    flist = [x for x in train.columns if not x in ['ID','target']]

    return train, test

def add_SumValues(train, test, features):
    flist = [x for x in train.columns if not x in ['ID','target']]
    if 'SumValues' in features:
        train.insert(1, 'SumValues', (train[flist] != 0).astype(int).sum(axis=1))
        test.insert(1, 'SumValues', (test[flist] != 0).astype(int).sum(axis=1))
    flist = [x for x in train.columns if not x in ['ID','target']]

    return train, test


def add_OtherAgg(train, test, features):
    flist = [x for x in train.columns if not x in ['ID', 'target', 'SumZeros', 'SumValues']]
    if 'OtherAgg' in features:
        train['Mean'] = train[flist].mean(axis=1)
        train['Median'] = train[flist].median(axis=1)
        train['Mode'] = train[flist].mode(axis=1)
        train['Max'] = train[flist].max(axis=1)
        train['Var'] = train[flist].var(axis=1)
        train['Std'] = train[flist].std(axis=1)

        test['Mean'] = test[flist].mean(axis=1)
        test['Median'] = test[flist].median(axis=1)
        test['Mode'] = test[flist].mode(axis=1)
        test['Max'] = test[flist].max(axis=1)
        test['Var'] = test[flist].var(axis=1)
        test['Std'] = test[flist].std(axis=1)
    flist = [x for x in train.columns if not x in ['ID', 'target', 'SumZeros', 'SumValues']]

    return train, test

def get_rfc():
    return RandomForestClassifier(
        n_estimators=50,
        max_features=0.5,
        max_depth=None,
        max_leaf_nodes=270,
        min_impurity_decrease=0.0001,
        random_state=123,
        n_jobs=-1
    )

def get_data():
    train = pd.read_csv('../input/train.csv')
    test = pd.read_csv('../input/test.csv')
    y_train_log = np.log1p(train['target'])
    id_test = test['ID']
    del test['ID']
    del train['ID']
    del train['target']
    
    colsToRemove = []
    for col in train.columns:
        if train[col].std() == 0:
            colsToRemove.append(col)
            
    train.drop(colsToRemove, axis=1, inplace=True)
    test.drop(colsToRemove, axis=1, inplace=True)
    
    train, test = add_SumZeros(train, test, ['SumZeros'])
    train, test = add_SumValues(train, test, ['SumValues'])
    train, test = add_OtherAgg(train, test, ['OtherAgg'])
    
    return train.values, y_train_log.values, test.values, id_test.values

def main():
    
    xgb_params = {
        'n_estimators': 1000,
        'objective': 'reg:linear',
        'booster': 'gbtree',
        'learning_rate': 0.02,
        'max_depth': 22,
        'min_child_weight': 57,
        'gamma' : 1.45,
        'alpha': 0.0,
        'lambda': 0.0,
        'subsample': 0.67,
        'colsample_bytree': 0.054,
        'colsample_bylevel': 0.50,
        'n_jobs': -1,
        'random_state': 456
    }
    
    fit_params = {
        'early_stopping_rounds': 15,
        'eval_metric': 'rmse',
        'verbose': False
    }
    
    pipe = Pipeline(
        [
            ('vt', VarianceThreshold(threshold=0.0)),
            ('ut', UniqueTransformer()),
            ('fu', FeatureUnion(
                    [
                        ('pca', PCA(n_components=100)),
                        ('ct-2', ClassifierTransformer(get_rfc(), n_classes=2, cv=5)),
                        ('ct-3', ClassifierTransformer(get_rfc(), n_classes=3, cv=5)),
                        ('ct-4', ClassifierTransformer(get_rfc(), n_classes=4, cv=5)),
                        ('ct-5', ClassifierTransformer(get_rfc(), n_classes=5, cv=5)),
                        ('st', StatsTransformer(stat_funs=get_stat_funs()))
                    ]
                )
            ),
            ('xgb-cv', XGBRegressorCV(
                    xgb_params=xgb_params,
                    fit_params=fit_params,
                    cv=10
                )
            )
        ]
    )
    
    X_train, y_train_log, X_test, id_test = get_data()
    
    pipe.fit(X_train, y_train_log)
    print(pipe.named_steps['xgb-cv'].cv_scores_)
    print(pipe.named_steps['xgb-cv'].cv_score_)
    
    y_pred_log = pipe.predict(X_test)
    y_pred = np.expm1(y_pred_log)

    submission = pd.DataFrame()
    submission['ID'] = id_test
    submission['target'] = y_pred
    submission.to_csv('pipeline_kernel_xgb_fe_cv{}.csv'.format(
        np.round(pipe.named_steps['xgb-cv'].cv_score_), 5), index=None
    )
    
if __name__ == '__main__':
    main()
