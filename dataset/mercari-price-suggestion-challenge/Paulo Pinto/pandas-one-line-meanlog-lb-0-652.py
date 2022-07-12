import pandas as pd;pd.read_csv('../input/test.tsv',sep='\t',usecols=[0,3]).set_index(['category_name'] ).join(pd.read_csv('../input/train.tsv',sep='\t',usecols=[3,5],converters={'price': lambda p: pd.np.log1p(float(p))}).groupby(['category_name'])['price'].mean().to_frame('price' ).apply(pd.np.expm1),how='left').fillna(17.).to_csv('meanlog.csv',float_format='%.2f',index=None)