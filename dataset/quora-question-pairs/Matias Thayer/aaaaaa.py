# This Python 3 environment comes with many helpful analytics libraries installed
# It is defined by the kaggle/python docker image: https://github.com/kaggle/docker-python
# For example, here's several helpful packages to load in 

from functools import partial
import numpy as np
import pandas as pd
from collections import Counter
import xgboost as xgb
import numpy as np
import pandas as pd
from sklearn.cross_validation import train_test_split


def load_data():
    df_train = pd.read_csv('../input/train.csv')#.sample(1000)
    df_test = pd.read_csv('../input/test.csv')#.sample(1000)
    return df_train, df_test

def get_weight(count, eps=10000, min_count=2):
    ''' If a word appears only once, we ignore it completely (likely a typo)
     Epsilon defines a smoothing constant, which makes the effect of extremely rare words smaller'''
    if count < min_count:
        return 0.
    else:
        return 1. / float(count + eps)

def count_words(row, stop_words={}):
    #stops = get_stop_words('english')
    #stops = [normalize('NFKD', stop).encode('ascii','ignore') for stop in stops]
    q1words = {}
    q2words = {}
    for word in str(row['question1']).lower().split():
        if word not in stop_words:
            q1words[word] = 1
    for word in str(row['question2']).lower().split():
        if word not in stop_words:
            q2words[word] = 1
    return q1words, q2words

def word_match_share(row, stop_words={}):
    q1words, q2words = count_words(row, stop_words={})
    if len(q1words) == 0 or len(q2words) == 0:
        return 0
    shared_words_in_q1 = [w for w in q1words.keys() if w in q2words]
    shared_words_in_q2 = [w for w in q2words.keys() if w in q1words]
    R = (len(shared_words_in_q1) + len(shared_words_in_q2))/float(len(q1words) + len(q2words))
    return R

def tfidf_word_match_share(row, stop_words={}):
    q1words, q2words = count_words(row, stop_words)
    if len(q1words) == 0 or len(q2words) == 0:
        # The computer-generated chaff includes a few questions that are nothing but stopwords
        return 0
    shared_weights = [weights.get(w, 0) for w in q1words.keys() if w in q2words] + [weights.get(w, 0) for w in q2words.keys() if w in q1words]
    total_weights = [weights.get(w, 0) for w in q1words] + [weights.get(w, 0) for w in q2words]

    R = np.sum(shared_weights) / float(np.sum(total_weights))
    return R

def add_word_count(df, word):
    count1 = df['question1'].apply(lambda x: (word in str(x).lower())*1)
    count2 = df['question2'].apply(lambda x: (word in str(x).lower())*1)
    return count1, count2 

def add_features(df):
    stop_words = {'here', 'o', 'own', 'being', 'did', 'up', 'under', 'below', 're', 'itself', 'why', 'for', 'the', 'more', 'do', 'just', 'these', 'himself', 'with', 'off', 't', 'further', 'only', 'doesn', 'hasn', 'each', 'doing', 'theirs', 'm', 'same', 'their', 'because', 'nor', 'myself', 'how', 's', 'am', 'into', 'after', 'any', 'ours', 'our', 'most', 'no', 'too', 'does', 'as', 'all', 'herself', 'are', 'they', 'then', 'very', 'she', 'ourselves', 'few', 'where', 'needn', 'some', 'had', 'haven', 'if', 'her', 'it', 'against', 'yourselves', 'what', 'now', 'again', 'before', 'should', 'mustn', 'hadn', 'will', 'weren', 'be', 'y', 'is', 'mightn', 'than', 'them', 'at', 'i', 'in', 'there', 'its', 'about', 'through', 'such', 'out', 'on', 'ma', 'have', 've', 'was', 'and', 'were', 'so', 'ain', 'until', 'hers', 'yours', 'he', 'aren', 'you', 'can', 'not', 'has', 'shouldn', 'which', 'when', 'his', 'themselves', 'don', 'above', 'down', 'other', 'd', 'didn', 'to', 'we', 'those', 'who', 'll', 'shan', 'once', 'your', 'couldn', 'yourself', 'wouldn', 'while', 'been', 'that', 'between', 'a', 'him', 'both', 'isn', 'but', 'or', 'whom', 'having', 'this', 'from', 'during', 'me', 'by', 'an', 'my', 'won', 'over', 'of', 'wasn'}
    x_df = pd.DataFrame()
    f = partial(word_match_share, stop_words=stop_words)
    x_df['word_match_stops'] = df.apply(f, axis=1, raw=True)
    x_df['tfidf_word_match'] = df.apply(tfidf_word_match_share, axis=1, raw=True)
    f = partial(tfidf_word_match_share, stop_words=stop_words)
    x_df['tfidf_word_match_stops'] = df.apply(f, axis=1, raw=True)
    x_df['len_q1'] = df['question1'].apply(lambda x: len(str(x)))
    x_df['len_q2'] = df['question2'].apply(lambda x: len(str(x)))
    x_df['caps_count_q1'] = df['question1'].apply(lambda x:sum(1 for i in str(x) if i.isupper()))
    x_df['caps_count_q2'] = df['question2'].apply(lambda x:sum(1 for i in str(x) if i.isupper()))
    #df['question1'] = [x.lower() for x in df['question1']]
    #df['question2'] = [x.lower() for x in df['question2']]
    x_df['how.c1'], x_df['how.c2'] = add_word_count(df,'how')
    x_df['what.c1'], x_df['what.c2'] = add_word_count(df,'what')
    x_df['who.c1'], x_df['what.c2'] = add_word_count(df,'what')
    x_df['which.c1'], x_df['which.c2'] = add_word_count(df,'which')
    x_df['where.c1'], x_df['where.c2'] = add_word_count(df,'where')
    x_df['when.c1'], x_df['when.c2'] = add_word_count(df,'when')
    x_df['why.c1'], x_df['why.c2'] = add_word_count(df,'why')
    x_df['starwars.c1'], x_df['starwars.c2'] = add_word_count(df,'star wars')
    x_df['mbf.c1'], x_df['mbf.c2'] = add_word_count(df,'mind-blowing facts')
    x_df['wcil.c1'], x_df['wcil.c2'] = add_word_count(df,'what can i learn')
    x_df['mif.c1'], x_df['mif.c2'] = add_word_count(df,'most interesting facts')
    return x_df

def rebalancing_data(x_train, y_train):
    pos_train = x_train[y_train == 1]
    neg_train = x_train[y_train == 0]

    # Now we oversample the negative class
    # There is likely a much more elegant way to do this...
    p = 0.165
    scale = ((len(pos_train) / (len(pos_train) + len(neg_train))) / p) - 1
    while scale > 1:
        neg_train = pd.concat([neg_train, neg_train])
        scale -=1
    neg_train = pd.concat([neg_train, neg_train[:int(scale * len(neg_train))]])
    print(len(pos_train) / (len(pos_train) + len(neg_train)))

    x_train = pd.concat([pos_train, neg_train])
    y_train = (np.zeros(len(pos_train)) + 1).tolist() + np.zeros(len(neg_train)).tolist()
    del pos_train, neg_train
    return x_train, y_train

def get_xgb_params():
    params = {
            'num_rounds':420,
            "objective": "binary:logistic",
            "booster": "gbtree",
            "eval_metric": 'logloss',
            'seed':1,
            'silent': 1,
            "max_depth": 4,
            'eta': 0.3,
           # "subsample": 0.6,
           # "alpha": 0,
           # "lambda": 1,
           # "colsample_bytree": 0.7,
           # 'min_child_weight': 15,
            }
    return params

if __name__ == '__main__':
    df_train, df_test = load_data()
    train_qs = pd.Series(df_train['question1'].tolist() + df_train['question2'].tolist()).astype(str)
    test_qs = pd.Series(df_test['question1'].tolist() + df_test['question2'].tolist()).astype(str)
    words = (" ".join(train_qs)).lower().split()
    counts = Counter(words)
    weights = {word: get_weight(count) for word, count in counts.items()}
    print('Most common words and weights: \n')
    print(sorted(weights.items(), key=lambda x: x[1] if x[1] > 0 else 9999)[:10])
    print('Least common words and weights: ')
    print(sorted(weights.items(), key=lambda x: x[1], reverse=True)[:10])  
    x_train = add_features(df_train)
    x_test = add_features(df_test)

    #x_train.to_csv('train_feats.gzip', compression='gzip', index=False)
    #x_test.to_csv('test_feats.gzip', compression='gzip', index=False)

    y_train = df_train['is_duplicate'].values
    #x_train, y_train = rebalancing_data(x_train, np.array(y_train))
    print(x_train.columns)
    
    x_train, x_valid, y_train, y_valid = train_test_split(x_train, y_train, test_size=0.15, random_state=4242)
    y_train = np.array(y_train)
    y_valid = np.array(y_valid)
    params = get_xgb_params()
    d_train = xgb.DMatrix(x_train, label=y_train, missing=np.nan)
    d_valid = xgb.DMatrix(x_valid, label=y_valid, missing=np.nan)

    watchlist = [(d_train, 'train'), (d_valid, 'valid')]

    bst = xgb.train(params, d_train, 700, watchlist, early_stopping_rounds=50, verbose_eval=10)

    d_test = xgb.DMatrix(x_test)
    p_test = bst.predict(d_test)

    sub = pd.DataFrame()
    sub['test_id'] = df_test['test_id']
    sub['is_duplicate'] = p_test
    sub.to_csv('not_so_simple_now.csv', index=False)