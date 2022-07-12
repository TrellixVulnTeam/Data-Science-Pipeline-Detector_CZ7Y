#
#State of the art...in REPLACE



#latitude values are primarily between 40.6 and 40.9
#longitude values range between -73.8 and -74.02


#================================================
import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
from scipy import sparse

from sklearn.ensemble import RandomForestClassifier
from sklearn import model_selection, preprocessing, ensemble
from sklearn.metrics import log_loss
import xgboost as xgb
from sklearn import  preprocessing, ensemble
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer

#from subprocess import check_output 
#print(check_output(["ls", "../input"]).decode("utf8"))
from sklearn import model_selection, preprocessing, ensemble

pd.set_option('display.max_columns', None)

df_train = pd.read_json(open("../input/train.json", "r"))
target_num_map = {'high':0, 'medium':1, 'low':2}
yy = np.array(df_train['interest_level'].apply(lambda x: target_num_map[x]))
yxa = df_train['interest_level']

df_test = pd.read_json(open("../input/test.json", "r"))

llista=np.array(df_test["listing_id"])
print(df_train.shape)
print(df_test.shape)

#Outliars...
df_train.loc[df_train['price'] == 111111, 'price'] = 1025

#COLUMNS....
#'bathrooms', 'bedrooms', 'building_id', 'created', 'description',
#       'display_address', 'features', 'interest_level', 'latitude',
#       'listing_id', 'longitude', 'manager_id', 'photos', 'price',
#       'street_address']

#========================================
##Block experiment...
#df100= (df_train[["block","interest_level"]])
#interest_dummies = pd.get_dummies(df_train.interest_level)
#df100 = pd.concat([df100,interest_dummies[['low','medium','high']]], axis = 1).drop('interest_level', axis = 1)
#print(df100.head())

#gby = pd.concat([df100.groupby('block').mean(),df100.groupby('block').count()], axis = 1).iloc[:,:-2]
#gby.columns = ['low','medium','high','count']
#print(gby.sort_values(by = 'count', ascending = False).head())
##End of experiment
#======================================
#CC
df_train["listing_id"] = df_train["listing_id"] - 68119576.0


df_train["price"]=np.log(df_train["price"])
df_train["zero_building_id"] = df_train["building_id"].apply(lambda x: 1 if x=='0' else 0)
df_train["num_photos"] = df_train["photos"].apply(len)
df_train["num_features"] = df_train["features"].apply(len)
df_train["num_description_words"] = df_train["description"].apply(lambda x: len(x.split(" ")))
df_train["created"] = pd.to_datetime(df_train["created"])
df_train["created_year"] = df_train["created"].dt.year
df_train["created_month"] = df_train["created"].dt.month
df_train["created_day"] = df_train["created"].dt.day
df_train["created_hour"] = df_train["created"].dt.hour
#CC
df_train["total_days"] =   (df_train["created_month"] -4.0)*30 + df_train["created_day"] +  df_train["created_hour"] /25.0
df_train["diff_rank"]= df_train["total_days"]/df_train["listing_id"]



df_test["listing_id"] =  df_test["listing_id"] - 68119576.0

df_test["price"]=np.log(df_test["price"])
df_test["zero_building_id"] = df_test["building_id"].apply(lambda x: 1 if x=='0' else 0)
df_test["num_photos"] = df_test["photos"].apply(len)
df_test["num_features"] = df_test["features"].apply(len)
df_test["num_description_words"] = df_test["description"].apply(lambda x: len(x.split(" ")))
df_test["created"] = pd.to_datetime(df_test["created"])
df_test["created_year"] = df_test["created"].dt.year
df_test["created_month"] = df_test["created"].dt.month
df_test["created_day"] = df_test["created"].dt.day
df_test["created_hour"] = df_test["created"].dt.hour
#CC
df_test["total_days"] =(df_test["created_month"] -4.0)*30 + df_test["created_day"] +  df_test["created_hour"] /25.0        
df_test["diff_rank"]= df_test["total_days"]/df_test["listing_id"]
 

#Price per ...
df_train["price_bed"] = df_train["price"]/df_train["bedrooms"]
df_train["price_bath"] = df_train["price"]/df_train["bathrooms"]
df_train["price_bath_bed"] = df_train["price"]/(df_train["bathrooms"] + df_train["bedrooms"])
#***
df_train["bedPerbath"] = (df_train["bedrooms"]/df_train["bathrooms"])
df_train["bedDiffbath"] = (df_train["bedrooms"]-df_train["bathrooms"])
df_train["bedPlusbath"] = (df_train["bedrooms"]+df_train["bathrooms"])
df_train["bedPerc"] = (df_train["bedrooms"]/(df_train["bathrooms"]+df_train["bedrooms"]))
#***
df_train.fillna(-1,inplace=True)

df_test["price_bed"] = df_test["price"]/df_test["bedrooms"]
df_test["price_bath"] = df_test["price"]/df_test["bathrooms"]
df_test["price_bath_bed"] = df_test["price"]/(df_test["bathrooms"] + df_test["bedrooms"])
#***
df_test["bedPerbath"] = (df_test["bedrooms"]/df_test["bathrooms"])
df_test["bedDiffbath"] = (df_test["bedrooms"]-df_test["bathrooms"])
df_test["bedPlusbath"] = (df_test["bedrooms"]+df_test["bathrooms"])
df_test["bedPerc"]     = (df_test["bedrooms"]/(df_test["bathrooms"]+df_test["bedrooms"]))
#***
df_test.fillna(-1,inplace=True)

#numfeats
#CC
num_feats = ["bathrooms", "bedrooms", "latitude", "longitude", "price",
             "num_photos", "num_features", "num_description_words",
             "created_year", "created_month", "created_day","created_hour",
             "price_bed","price_bath","price_bath_bed","zero_building_id",
             "bedPerbath","bedDiffbath","bedPlusbath","bedPerc","listing_id"
             ,"diff_rank","total_days"
             ]

#----------------------------------------------------------
#address1
df_train['address1'] = df_train['display_address']
df_test['address1'] = df_test['display_address']

df_train['address1'] = df_train['address1'].apply(lambda x: str(x).lower())
df_test['address1'] =  df_test['address1'].apply(lambda x: str(x).lower())

address_map = {
    'w': 'west',
    'st.': 'street',
    'ave': 'avenue',
    'st': 'street',
    'e': 'east',
    'n': 'north',
    's': 'south',
    'blvd': 'blvd',
    'square': 'square',
    'park': 'park',
    'place': 'place',
    'road': 'road',
    'rd': 'road',
    'center': 'center',
    'terrace': 'teracce'

    }
    
def address_map_func(s):
    s = s.split(' ')
    out = []
    for x in s:
        if x in address_map:
            out.append(address_map[x])
        else:
            out.append(x)
    return ' '.join(out)

def dict_init(aa): 
    gdict={}
    for rr in range(len(aa)):
        rr1=aa[rr].split(' ')
        for jj in range(len(rr1)):
                ww=rr1[jj]
                z1=gdict.get(ww,-999)
                if z1==-999:
                    gdict[ww]=1
                else:
                    gdict[ww]+=1   
    return gdict
#train['address1'] = train['address1'].apply(lambda x: x.translate(remove_punct_map))
#test['address1'] = test['address1'].apply(lambda x: x.translate(remove_punct_map))

df_train['address1'] = df_train['address1'].apply(lambda x: address_map_func(x))
df_test['address1']  =  df_test['address1'].apply(lambda x: address_map_func(x))

new_cols = ['street', 'avenue', 'east', 'west', 'north', 'south']

for col in new_cols:
    df_train[col] = df_train['address1'].apply(lambda x: 1 if col in x else 0)
    df_test[col] =  df_test['address1'].apply(lambda x: 1 if col in x else 0)
    num_feats.append(col)
#---------------------------------------------------------

#LabelEncoding
categorical = ["display_address", "manager_id", "building_id", "street_address"]
for f in categorical:
        if df_train[f].dtype=='object':
            #print(f)
            lbl = preprocessing.LabelEncoder()
            lbl.fit(list(df_train[f].values) + list(df_test[f].values))
            df_train[f] = lbl.transform(list(df_train[f].values))
            df_test[f] = lbl.transform(list(df_test[f].values))
            num_feats.append(f)

#=============================================================================
# compute fractions and count for each manager
temp = pd.concat([df_train.manager_id,pd.get_dummies(yxa)], axis = 1).groupby('manager_id').mean()
temp.columns = ['high_frac','low_frac', 'medium_frac']
temp['count'] = df_train.groupby('manager_id').count().iloc[:,1]
temp['one_manager'] = np.where(temp['count']==1, 1, 0)

# compute skill
temp['manager_skill'] = temp['high_frac']*2 + temp['medium_frac']

# get ixes for unranked managers...
unranked_managers_ixes = temp['count']<20
# ... and ranked ones
ranked_managers_ixes = ~unranked_managers_ixes

# compute mean values from ranked managers and assign them to unranked ones
mean_values = temp.loc[ranked_managers_ixes, ['high_frac','low_frac', 'medium_frac','manager_skill']].mean()
print(mean_values)
temp.loc[unranked_managers_ixes,['high_frac','low_frac', 'medium_frac','manager_skill']] = mean_values.values
temp.loc[unranked_managers_ixes,['one_manager']] =0

print(temp.tail(10))

# inner join to assign manager features to the managers in the training dataframe
df_train = df_train.merge(temp.reset_index(),how='left', left_on='manager_id', right_on='manager_id')


# add the features computed on the training dataset to the validation dataset
df_test = df_test.merge(temp.reset_index(),how='left', left_on='manager_id', right_on='manager_id')
new_manager_ixes = df_test['high_frac'].isnull()
df_test.loc[new_manager_ixes,['high_frac','low_frac', 'medium_frac','manager_skill']] = mean_values.values
#=============================================================================
#Split - vectorizer
# [Cats Allowed, No Fee]--> [Cats_Allowed No_Fee]

df_train['features'] = df_train["features"].apply(lambda x: " ".join(["_".join(i.split(" ")).lower() for i in x]))
df_test['features']   = df_test["features"].apply(lambda x: " ".join(["_".join(i.split(" ")).lower() for i in x]))
#============================================
#Description featuring...
lista=["manhattan","central park","subway","train","bikeway","columbus circle"]
sfe_train = np.array(df_train['description'])
sfe_test =  np.array(df_test['description'])
for ww in lista:
        sar_train=np.zeros(df_train.shape[0])
        sar_test=np.zeros(df_test.shape[0])
        for rr in range(df_train.shape[0]):
                if ww in sfe_train[rr].lower():
                    sar_train[rr]=1
                else:
                    sar_train[rr]=0
        df_train[ww]=sar_train
        for rr in range(df_test.shape[0]):
                if ww in sfe_test[rr].lower():
                    sar_test[rr]=1
                else:
                    sar_test[rr]=0
        df_test[ww]=sar_test
#==============================================================================        
#   Replace-Join features  Section...
def rep_join(aa,s_from,s_to): 
    aa_new=aa.copy()
    for rr in range(len(aa)):
        rr1=aa[rr].split(' ')
        axa=''
        for jj in range(len(rr1)):
#            if rr1[jj]==s_from and len(rr1[jj])!= len(s_from):
#                print ('NO BINGO...')
                
            if rr1[jj]==s_from and len(rr1[jj])== len(s_from):
                #if s_from=='washer':
                 #print ('Bingo...',rr1[jj])
                rr1[jj]=s_to                 
            axa+=rr1[jj] 
            axa+=' '
       
       
        aa_new[rr]=axa
    return aa_new
    
 #==================================================================   
#TRAIN ******************
##Direct replace
df_train['features']=df_train['features'].str.replace("garden/patio","garden")
df_train['features']=df_train['features'].str.replace("patio","garden")
df_train['features']=df_train['features'].str.replace("residents_garden","garden")
df_train['features']=df_train['features'].str.replace("common_garden","garden")

df_train['features']=df_train['features'].str.replace("wifi_access","wifi")

df_train['features']=df_train['features'].str.replace("24/7","24")
df_train['features']=df_train['features'].str.replace("24-hour","24")
df_train['features']=df_train['features'].str.replace("24hr","24")
df_train['features']=df_train['features'].str.replace("concierge","doorman")
df_train['features']=df_train['features'].str.replace("ft_doorman","doorman")
df_train['features']=df_train['features'].str.replace("24_doorman","doorman")
df_train['features']=df_train['features'].str.replace("24_hr_doorman","doorman")
df_train['features']=df_train['features'].str.replace("doorman_service","doorman")
df_train['features']=df_train['features'].str.replace("full-time_doorman","doorman")

df_train['features']=df_train['features'].str.replace("gym/fitness","fitness")
df_train['features']=df_train['features'].str.replace("fitness_room","fitness")

df_train['features']=df_train['features'].str.replace("washer","laundry")
df_train['features']=df_train['features'].str.replace("laundry_in_bldg","laundry")
df_train['features']=df_train['features'].str.replace("laundry_in_building","laundry")
df_train['features']=df_train['features'].str.replace("laundry_in_building/dryer","laundry")
df_train['features']=df_train['features'].str.replace("laundry_in_building_&_dryer","laundry")
df_train['features']=df_train['features'].str.replace("laundry_room","laundry")
df_train['features']=df_train['features'].str.replace("laundry_&_housekeeping","laundry")
df_train['features']=df_train['features'].str.replace("laundry_in_unit","laundry")
df_train['features']=df_train['features'].str.replace("laundry_in-unit","laundry")
df_train['features']=df_train['features'].str.replace("laundry_on_every_floor","laundry")
df_train['features']=df_train['features'].str.replace("laundry_on_floor","laundry")
df_train['features']=df_train['features'].str.replace("in-unit_laundry/dryer","laundry")
df_train['features']=df_train['features'].str.replace("on-site_laundry","laundry")
df_train['features']=df_train['features'].str.replace("laundry/dryer","laundry")

df_train['features']=df_train['features'].str.replace("high-speed_internet","high_speed_internet")
df_train['features']=df_train['features'].str.replace("high_speed_internet_available","high_speed_internet")

df_train['features']=df_train['features'].str.replace("parking_available","parking")
df_train['features']=df_train['features'].str.replace("parking_space","parking")
df_train['features']=df_train['features'].str.replace("on-site_garage","parking")
df_train['features']=df_train['features'].str.replace("on-site_parking","parking")
df_train['features']=df_train['features'].str.replace("on-site_parking_lot","parking")
df_train['features']=df_train['features'].str.replace("full_service_garage","parking")
df_train['features']=df_train['features'].str.replace("common_parking/garage","parking")
df_train['features']=df_train['features'].str.replace("garage","parking")
df_train['features']=df_train['features'].str.replace("assigned-parking-space","private_parking")

df_train['features']=df_train['features'].str.replace("storage_available","storage")
df_train['features']=df_train['features'].str.replace("storage_facilities_available","storage")
df_train['features']=df_train['features'].str.replace("storage_space","storage")
df_train['features']=df_train['features'].str.replace("storage_room","storage")
df_train['features']=df_train['features'].str.replace("common_storage","storage")

df_train['features']=df_train['features'].str.replace("central_a/c","central_air")
df_train['features']=df_train['features'].str.replace("central_ac","central_air")
df_train['features']=df_train['features'].str.replace("air_conditioning","central_air")

df_train['features']=df_train['features'].str.replace("close_to_subway","subway")

df_train['features']=df_train['features'].str.replace("roofdeck","roof_deck")
df_train['features']=df_train['features'].str.replace("roof-deck","roof_deck")
df_train['features']=df_train['features'].str.replace("rooftop_terrace","roof_deck")
df_train['features']=df_train['features'].str.replace("rooftop_deck","roof_deck")
df_train['features']=df_train['features'].str.replace("roof_access","roof_deck")
df_train['features']=df_train['features'].str.replace("common_roof_deck","roof_deck")

df_train['features']=df_train['features'].str.replace("swimming_pool","pool")
df_train['features']=df_train['features'].str.replace("indoor_pool","pool")

df_train['features']=df_train['features'].str.replace("deco_fireplace","fireplaces")
df_train['features']=df_train['features'].str.replace("decorative_fireplace","fireplaces")

#Word replace (_MMM_)

mel_count=df_train['features'].str.contains("washer").sum()
print ('BEFORE Replace-Join  Section...*************',mel_count)

aa=np.array(df_train['features'])
df_train['features']=rep_join(aa,"gym_in_building","fitness")

aa=np.array(df_train['features'])
df_train['features']=rep_join(aa,"gym","fitness")

aa=np.array(df_train['features'])
df_train['features']=rep_join(aa,"health_club","fitness")

aa=np.array(df_train['features'])
df_train['features']=rep_join(aa,"fitness_center","fitness")

aa=np.array(df_train['features'])
df_train['features']=rep_join(aa,"pets_ok","pets_allowed")

aa=np.array(df_train['features'])
df_train['features']=rep_join(aa,"lounge_room","residents_lounge")

aa=np.array(df_train['features'])
df_train['features']=rep_join(aa,"wheelchair_ramp","wheelchair_access")

   
aa=np.array(df_train['features'])

#New voc setup
f_dict=dict_init(aa)
dlista= (sorted(f_dict.items(), key=lambda x:x[1]))
new_voc=[]
for rr in range(-1,-190,-1):
    if dlista[rr][0]!='XXXXXX' and  dlista[rr][0]!='':
        new_voc.append(dlista[rr][0])
print ('********',new_voc)

#===============================================================
#===============================================================
#TEST
print ('TEST')
#Direct replace
df_test['features']=df_test['features'].str.replace("garden/patio","garden")
df_test['features']=df_test['features'].str.replace("patio","garden")
df_test['features']=df_test['features'].str.replace("residents_garden","garden")
df_test['features']=df_test['features'].str.replace("common_garden","garden")

df_test['features']=df_test['features'].str.replace("wifi_access","wifi")

df_test['features']=df_test['features'].str.replace("24/7","24")
df_test['features']=df_test['features'].str.replace("24-hour","24")
df_test['features']=df_test['features'].str.replace("24hr","24")
df_test['features']=df_test['features'].str.replace("concierge","doorman")
df_test['features']=df_test['features'].str.replace("ft_doorman","doorman")
df_test['features']=df_test['features'].str.replace("24_doorman","doorman")
df_test['features']=df_test['features'].str.replace("24_hr_doorman","doorman")
df_test['features']=df_test['features'].str.replace("doorman_service","doorman")
df_test['features']=df_test['features'].str.replace("full-time_doorman","doorman")

df_test['features']=df_test['features'].str.replace("gym/fitness","fitness")
df_test['features']=df_test['features'].str.replace("fitness_room","fitness")

df_test['features']=df_test['features'].str.replace("washer","laundry")
df_test['features']=df_test['features'].str.replace("laundry_in_bldg","laundry")
df_test['features']=df_test['features'].str.replace("laundry_in_building","laundry")
df_test['features']=df_test['features'].str.replace("laundry_in_building/dryer","laundry")
df_test['features']=df_test['features'].str.replace("laundry_in_building_&_dryer","laundry")
df_test['features']=df_test['features'].str.replace("laundry_room","laundry")
df_test['features']=df_test['features'].str.replace("laundry_&_housekeeping","laundry")
df_test['features']=df_test['features'].str.replace("laundry_in_unit","laundry")
df_test['features']=df_test['features'].str.replace("laundry_in-unit","laundry")
df_test['features']=df_test['features'].str.replace("laundry_on_every_floor","laundry")
df_test['features']=df_test['features'].str.replace("laundry_on_floor","laundry")
df_test['features']=df_test['features'].str.replace("in-unit_laundry/dryer","laundry")
df_test['features']=df_test['features'].str.replace("on-site_laundry","laundry")
df_test['features']=df_test['features'].str.replace("laundry/dryer","laundry")

df_test['features']=df_test['features'].str.replace("high-speed_internet","high_speed_internet")
df_test['features']=df_test['features'].str.replace("high_speed_internet_available","high_speed_internet")

df_test['features']=df_test['features'].str.replace("parking_available","parking")
df_test['features']=df_test['features'].str.replace("parking_space","parking")
df_test['features']=df_test['features'].str.replace("on-site_garage","parking")
df_test['features']=df_test['features'].str.replace("on-site_parking","parking")
df_test['features']=df_test['features'].str.replace("on-site_parking_lot","parking")
df_test['features']=df_test['features'].str.replace("full_service_garage","parking")
df_test['features']=df_test['features'].str.replace("common_parking/garage","parking")
df_test['features']=df_test['features'].str.replace("garage","parking")
df_test['features']=df_test['features'].str.replace("assigned-parking-space","private_parking")

df_test['features']=df_test['features'].str.replace("storage_available","storage")
df_test['features']=df_test['features'].str.replace("storage_facilities_available","storage")
df_test['features']=df_test['features'].str.replace("storage_space","storage")
df_test['features']=df_test['features'].str.replace("storage_room","storage")
df_test['features']=df_test['features'].str.replace("common_storage","storage")

df_test['features']=df_test['features'].str.replace("central_a/c","central_air")
df_test['features']=df_test['features'].str.replace("central_ac","central_air")
df_test['features']=df_test['features'].str.replace("air_conditioning","central_air")

df_test['features']=df_test['features'].str.replace("close_to_subway","subway")

df_test['features']=df_test['features'].str.replace("roofdeck","roof_deck")
df_test['features']=df_test['features'].str.replace("roof-deck","roof_deck")
df_test['features']=df_test['features'].str.replace("rooftop_terrace","roof_deck")
df_test['features']=df_test['features'].str.replace("rooftop_deck","roof_deck")
df_test['features']=df_test['features'].str.replace("roof_access","roof_deck")
df_test['features']=df_test['features'].str.replace("common_roof_deck","roof_deck")

df_test['features']=df_test['features'].str.replace("swimming_pool","pool")
df_test['features']=df_test['features'].str.replace("indoor_pool","pool")

df_test['features']=df_test['features'].str.replace("deco_fireplace","fireplaces")
df_test['features']=df_test['features'].str.replace("decorative_fireplace","fireplaces")

#Word replace (_MMM_)
aa=np.array(df_test['features'])
#mel_count=df_test['features'].str.contains("**").sum()
#print ('AFTER Replace-Join  Section...*************',mel_count)

aa=np.array(df_test['features'])
df_test['features']=rep_join(aa,"gym_in_building","fitness")

aa=np.array(df_test['features'])
df_test['features']=rep_join(aa,"gym","fitness")

aa=np.array(df_test['features'])
df_test['features']=rep_join(aa,"health_club","fitness")

aa=np.array(df_test['features'])
df_test['features']=rep_join(aa,"fitness_center","fitness")

aa=np.array(df_test['features'])
df_test['features']=rep_join(aa,"pets_ok","pets_allowed")

aa=np.array(df_test['features'])
df_test['features']=rep_join(aa,"lounge_room","residents_lounge")

aa=np.array(df_test['features'])
df_test['features']=rep_join(aa,"wheelchair_ramp","wheelchair_access")
#===============================================================
tfidf = CountVectorizer(stop_words='english', max_features=200,vocabulary=new_voc) 
#tfidf = CountVectorizer(stop_words='english', max_features=200) 
tr_sparse = tfidf.fit_transform(df_train["features"])
vocabulary_list=[]
for key in tfidf.vocabulary_.items():
    kk=key[0].split(', ')
    vocabulary_list.append(kk[0])

te_sparse = tfidf.transform(df_test["features"])
#=============================================================================
#train_test section
ntrain=df_train.shape[0]
train_test = pd.concat((df_train, df_test), axis=0).reset_index(drop=True)

train_test['bathrooms_cat'] = train_test['bathrooms'].apply(lambda x: str(x))
train_test['bathrooms_cat'], labels = pd.factorize(train_test['bathrooms_cat'].values, sort=True)
df_train['bathrooms_cat']=np.array(train_test['bathrooms_cat'])[:ntrain]
df_test['bathrooms_cat']=np.array(train_test['bathrooms_cat'])[ntrain:]

train_test['bedrooms_cat'] = train_test['bedrooms'].apply(lambda x: str(x))
train_test['bedrooms_cat'], labels = pd.factorize(train_test['bedrooms_cat'].values, sort=True)
df_train['bedrooms_cat']=np.array(train_test['bedrooms_cat'])[:ntrain]
df_test['bedrooms_cat']=np.array(train_test['bedrooms_cat'])[ntrain:]

buildings_count = train_test['building_id'].value_counts()
train_test['top_5_building'] = train_test['building_id'].apply(lambda x: 1 if x in buildings_count.index.values[
    buildings_count.values >= np.percentile(buildings_count.values, 95)] else 0)
train_test['top_10_building'] = train_test['building_id'].apply(lambda x: 1 if x in buildings_count.index.values[
    buildings_count.values >= np.percentile(buildings_count.values, 90)] else 0)
train_test['top_25_building'] = train_test['building_id'].apply(lambda x: 1 if x in buildings_count.index.values[
    buildings_count.values >= np.percentile(buildings_count.values, 75)] else 0)
    
df_train['top_5_building']=np.array(train_test['top_5_building'])[:ntrain]
df_test['top_5_building']=np.array(train_test['top_5_building'])[ntrain:]     
df_train['top_10_building']=np.array(train_test['top_10_building'])[:ntrain]
df_test['top_10_building']=np.array(train_test['top_10_building'])[ntrain:]
df_train['top_25_building']=np.array(train_test['top_25_building'])[:ntrain]
df_test['top_25_building']=np.array(train_test['top_25_building'])[ntrain:]
 

train_test=[]

num_feats.append('manager_skill')
num_feats.remove('bathrooms')
num_feats.append('bathrooms_cat')
num_feats.remove('bedrooms')
num_feats.append('bedrooms_cat')
num_feats.append('one_manager')

num_feats.append('top_5_building')
num_feats.append('top_10_building')
num_feats.append('top_25_building')

for ww in lista:
    num_feats.append(ww)
print (list(df_train.columns) )    
#===================================================================================
df_train = sparse.hstack([df_train[num_feats], tr_sparse]).tocsr()
df_test =  sparse.hstack([df_test[num_feats], te_sparse]).tocsr()
print(df_train.shape, df_test.shape)
print ('FINAL COLUMNS...',num_feats)

#==========================================================================
param = {}
param['objective'] = 'multi:softprob'
param['eta'] = 0.03  #0.016
param['max_depth'] = 6#6
param['silent'] = 1
param['num_class'] = 3
param['eval_metric'] = "mlogloss"
param['min_child_weight'] = 1
param['subsample'] = 0.80#0.80
param['colsample_bytree'] = 0.5 #0.5
#param['colsample_bylevel'] = 0.7 #
#param['num_parallel_tree'] = 3 #

param['seed'] = 1
#param['lambda'] = 5
param['gamma'] = 1#1

num_rounds = 3000 

plst = list(param.items())

#==========================================================================
#CV...
cv=0
if cv :
        cv_scores = []
        noa=0
        kf = model_selection.KFold(n_splits=5, shuffle=True, random_state=2016)
        for dev_index, val_index in kf.split(range(df_train.shape[0])):
               
                noa+=1
                print ('Training ..',noa)
                dev_X, val_X = df_train[dev_index,:], df_train[val_index,:]
                dev_y, val_y = yy[dev_index], yy[val_index]
                

                xgtrain = xgb.DMatrix(dev_X, label=dev_y)
                xgtest = xgb.DMatrix(val_X, label=val_y)
                watchlist = [ (xgtrain,'train'), (xgtest, 'test') ]
                
                model = xgb.train(plst, xgtrain, num_rounds, watchlist, early_stopping_rounds=50)
                pred_test_xgb  = model.predict(xgtest)
               
                #Ansamble
                y_val_pred7=(pred_test_xgb  )
                score=log_loss(val_y, y_val_pred7)
                print (noa,' *** XGB1  ',score)
                cv_scores.append(round(log_loss(val_y, y_val_pred7),4))
                print(cv_scores)
                break
                
        print ('AVERAGE...',np.mean(cv_scores))      
#================================================
#================================================
#ACTUAL TRAINING
print ('Actual training...')


num_rounds=1350
xgtrain = xgb.DMatrix(df_train, label=yy)
xgtest = xgb.DMatrix(df_test)
model = xgb.train(plst, xgtrain, num_rounds)
print ('XGB train OK')
pred_test_xgb  = model.predict(xgtest)

y=(pred_test_xgb )
#================================================
#Output setup
sub = pd.DataFrame()
sub["listing_id"] = llista
ff0=np.zeros(len(y))
ff1=np.zeros(len(y))
ff2=np.zeros(len(y))

for rr in range(len(y)):
    ff0[rr] = y[rr][0]
    ff1[rr] = y[rr][1]
    ff2[rr] = y[rr][2]

sub['high']=ff0
sub['medium']=ff1  
sub['low']=ff2  

sub.to_csv("submission_rf.csv", index=False)


