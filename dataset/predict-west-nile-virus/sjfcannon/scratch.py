import pandas
#import os
import numpy as np
import matplotlib.pyplot as plt
from sklearn.neighbors import KernelDensity

#os.system("ls ..")
#os.system("ls ../input")
#os.system("ls ../src")
#os.system("ls .")
#os.system("ls ../working")

#print(os.getcwd( ))

#help("modules")

print("--------------------------------------------------------------------------------")
train = pandas.read_csv("../input/train.csv")
species = pandas.np.unique(train['Species'])
print("Species of Misquito:")
print(species)
spray = pandas.read_csv("../input/spray.csv", parse_dates=['Date'])
weather = pandas.read_csv("../input/weather.csv")

#loc = pandas.merge(train, spray, on=['Latitude', 'Longitude'])
#print(loc.head( ))

#print(dir(train))
#print("Training set has {0[0]} rows and {0[1]} columns".format(train.shape))

#print(train.head( ))

print("--------------------------------------------------------------------------------")

traps = pandas.read_csv('../input/train.csv', parse_dates=['Date'])[['Date', 'Trap','Longitude', 'Latitude', 'Species', 'WnvPresent']]
mapdata = np.loadtxt("../input/mapdata_copyright_openstreetmap_contributors.txt")

alpha_cm = plt.cm.Reds
alpha_cm._init()
alpha_cm._lut[:-3,-1] = abs(np.logspace(0, 1, alpha_cm.N) / 10 - 1)[::-1]
alpha_mcm = plt.cm.Greens
alpha_mcm._init()
alpha_mcm._lut[:-3,-1] = abs(np.logspace(0, 1, alpha_cm.N) / 10 - 1)[::-1]
aspect = mapdata.shape[0] * 1.0 / mapdata.shape[1]
lon_lat_box = (-88, -87.5, 41.6, 42.1)

subplot = 0
numSpcs = len(species)
plt.figure(figsize=(18,6*numSpcs))
for spcsIndx in range(numSpcs):
    for year in [2007, 2009, 2011, 2013]:
        subplot += 1
        sightings = traps[(traps['Species'] == species[spcsIndx])
                          & (traps['WnvPresent'] > 0)
                          & (traps['Date'].apply(lambda x: x.year) == year)]
        sightings = sightings.groupby(['Date', 'Trap', 'Longitude', 'Latitude', 'Species']).max()['WnvPresent'].reset_index()
        mSightings = traps[(traps['Species'] == species[spcsIndx])
                          & (traps['Date'].apply(lambda x: x.year) == year)]
        mSightings = mSightings.groupby(['Date', 'Trap', 'Longitude', 'Latitude', 'Species']).max()['WnvPresent'].reset_index()
        if(len(mSightings) <= 0):
            print("SKIPPING [" + str(subplot) + "]:" + str(year) + " (" + species[spcsIndx] + ")\t\tNo sightings")
            continue

        mX = mSightings[['Longitude', 'Latitude']].values
        mkd = KernelDensity(bandwidth=0.02)
        mkd.fit(mX)
        mxv,myv = np.meshgrid(np.linspace(-88, -87.5, 100), np.linspace(41.6, 42.1, 100))
        mGridpoints = np.array([mxv.ravel(),myv.ravel()]).T
        mzv = np.exp(mkd.score_samples(mGridpoints).reshape(100,100))

        plt.subplot(numSpcs, 4, subplot)
        plt.gca().set_title(str(year) + " (" + species[spcsIndx] + ")")
        plt.imshow(mapdata, 
                   cmap=plt.get_cmap('gray'), 
                   extent=lon_lat_box, 
                   aspect=aspect)
        plt.imshow(mzv, 
                   origin='lower', 
                   cmap=alpha_mcm, 
                   extent=lon_lat_box, 
                   aspect=aspect)
        if(len(sightings) > 0):
            X = sightings[['Longitude', 'Latitude']].values
            kd = KernelDensity(bandwidth=0.02)
            kd.fit(X)
            xv,yv = np.meshgrid(np.linspace(-88, -87.5, 100), np.linspace(41.6, 42.1, 100))
            gridpoints = np.array([xv.ravel(),yv.ravel()]).T
            zv = np.exp(kd.score_samples(gridpoints).reshape(100,100))
            plt.imshow(zv, 
                       origin='lower', 
                       cmap=alpha_cm, 
                       extent=lon_lat_box, 
                       aspect=aspect)
        print("         [" + str(subplot) + "]:" + str(year) + " (" + species[spcsIndx] + ")")
        plt.tight_layout()
        locations = traps[['Longitude', 'Latitude']].drop_duplicates().values
        plt.scatter(locations[:,0], locations[:,1], marker='x')

plt.savefig('heatmap.png')

