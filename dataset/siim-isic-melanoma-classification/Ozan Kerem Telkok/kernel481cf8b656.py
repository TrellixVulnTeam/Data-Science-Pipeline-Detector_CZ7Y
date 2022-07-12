import tensorflow as tf
from tensorflow import keras
import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
from PIL import Image
from PIL import ImageFile
import random
import os
def accessImage(path,resize):
    image = Image.open(path)
    image = image.resize((512, 512))
    image = np.array(image)
    return image
base_path = '/kaggle/input/siim-isic-melanoma-classification'
train_img_path = '/kaggle/input/siim-isic-melanoma-classification/jpeg/train/'
test_img_path = '/kaggle/input/siim-isic-melanoma-classification/jpeg/test/'
img_stats_path = '/kaggle/input/melanoma2020imgtabular'

model = keras.models.Sequential()
model.add(keras.layers.Conv2D(16, (8, 8), strides=(8,8) ,activation='relu', input_shape=(512, 512, 3)))
model.add(keras.layers.MaxPooling2D((2, 2)))
model.add(keras.layers.Conv2D(32, (8, 8),strides=(2,2) ,activation='relu'))
model.add(keras.layers.Conv2D(32, (8, 8), activation='relu'))
model.add(keras.layers.Flatten(input_shape=(6, 6,32)))
model.add(keras.layers.Dense(2,activation = 'softmax'))
model.compile(optimizer='adam',
                  loss='binary_crossentropy',
                  metrics=['accuracy'])
model.summary()
trainF = pd.read_csv(os.path.join(base_path, 'train.csv'))
breakFlag = 0

for y in range(1):
    trImages = []
    lastIndex = (y+1)*100
    if lastIndex > len(trainF['image_name']):
        lastIndex = len(trainF['image_name'])-1
        breakFlag = 1
    train = trainF[y*100:lastIndex]
    trainIm = train['image_name']
    train_images = trainIm.values.tolist()
    train_img = [os.path.join( i + ".jpg") for i in train_images]
    for imname in train_img:
            img = accessImage(train_img_path+imname,[512,512])
            trImages.append(img)
    trImages = np.asarray(trImages)
    trImages = trImages/255.
    trTargets = np.asarray(train['target'])
    class_weight = {0: 2.,1: 10.,}
    history = model.train_on_batch(trImages, trTargets,class_weight = class_weight)
    if breakFlag == 1:
        break
del train
del trainF
del trainIm
del train_images
del trImages
del train_img
del trTargets
breakFlag = 0
testF = pd.read_csv(os.path.join(base_path, 'test.csv'))
output = []
for y in range(1):
    lastIndex = (y+1)*100
    if lastIndex > len(testF['image_name']):
        lastIndex = len(testF['image_name'])
        breakFlag = 1
    test = testF[y*100:lastIndex]
    testIm = test['image_name']
    test_images = testIm.values.tolist()
    test_img = [os.path.join( i + ".jpg") for i in test_images]
    teImages = []
    for imname in test_img:
        teImages.append(accessImage(test_img_path+imname,[512,512]))
    teImages = np.asarray(teImages)
    teImages = teImages / 255.
    pred_y = model.predict_on_batch(teImages)
    for (imname,elements) in zip(test_images,pred_y):
        output.append([imname,elements[1]])
    if breakFlag == 1:
        break
        
del testF
del test
del testIm
del test_img
del teImages
#for element in output:
#    print(element)
f = open("submission.csv", "w+")
f.write('image_name,target'+os.linesep)
for element in output:
    f.write(element[0]+','+str(element[1]) + os.linesep)
f.close()
    