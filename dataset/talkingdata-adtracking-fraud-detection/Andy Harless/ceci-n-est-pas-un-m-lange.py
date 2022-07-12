
LOGIT_WEIGHT = 0.3

import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
from scipy.special import expit, logit

almost_zero = 1e-10
almost_one = 1 - almost_zero

models = {
  'part1':  "../input/krishna-s-r-lgbm-with-time-deltas-partition-1/lgb_Usrnewness.csv",
  'part2':  "../input/krishna-s-r-lgbm-with-time-deltas-partition-2/lgb_Usrnewness.csv",
  'part3':  "../input/krishna-s-r-lgbm-with-time-deltas-partition-3/lgb_Usrnewness.csv",
  'part4':  "../input/krishna-s-r-lgbm-with-time-deltas-partition-4/lgb_Usrnewness.csv"
  }
 
weights = {
  'part1':  .53,
  'part2':  .27,
  'part3':  .14,
  'part4':  .06
  }
  
print (sum(weights.values()))


subs = {m:pd.read_csv(models[m]) for m in models}
first_model = list(models.keys())[0]
n = subs[first_model].shape[0]

ranks = {s:subs[s]['is_attributed'].rank()/n for s in subs}
logits = {s:subs[s]['is_attributed'].clip(almost_zero,almost_one).apply(logit) for s in subs}

logit_avg = 0
rank_avg = 0
for m in models:
    s = logits[m].std()
    print(m, s)
    logit_avg = logit_avg + weights[m]*logits[m] / s
    rank_avg = rank_avg + weights[m]*ranks[m]

logit_rank_avg = logit_avg.rank()/n
final_avg = LOGIT_WEIGHT*logit_rank_avg + (1-LOGIT_WEIGHT)*rank_avg

final_sub = pd.DataFrame()
final_sub['click_id'] = subs[first_model]['click_id']
final_sub['is_attributed'] = final_avg

print( final_sub.head() )

final_sub.to_csv("sub_krishnas_r_lgb_bag4.csv", index=False, float_format='%.8f')