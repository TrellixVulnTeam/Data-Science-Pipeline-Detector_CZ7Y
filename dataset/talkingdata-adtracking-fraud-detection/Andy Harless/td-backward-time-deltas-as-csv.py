import numpy as np 
import pandas as pd 
import os

print(os.listdir("../input"))

df = pd.read_pickle('../input/bidirectional-talkingdata-time-deltas/bidirectional_time_deltas.pkl.gz')
df.head()

df[['time_delta']].to_csv('td_time_deltas.csv', index=False)