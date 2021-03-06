# -*- coding: utf-8 -*-
"""BTL.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1qmIRaV7Bge7ANh0r_Il5vlT1Gqt9BPvp
"""

from google.colab import drive
drive.mount('/content/drive')

import os
from PIL import Image as PImage
import cv2 as cv
from os import listdir
import glob
from keras.preprocessing.image import ImageDataGenerator, array_to_img, img_to_array, load_img
import csv
from sklearn.model_selection import train_test_split
import os
import random
import pandas as pd
import numpy as np
from tensorflow.keras.utils import to_categorical
from tensorflow.keras import applications
from tensorflow.keras.layers import Input, Add, Dense, Activation, ZeroPadding2D, BatchNormalization, Flatten, Conv2D, AveragePooling2D, MaxPooling2D,GlobalAveragePooling2D, GlobalMaxPooling2D, Dropout
from tensorflow.keras.models import Model, load_model
from tensorflow.keras.preprocessing import image
from tensorflow.keras.utils import  plot_model
from tensorflow.keras.utils import get_file
from tensorflow.keras.utils import model_to_dot
from tensorflow.keras.applications.imagenet_utils import preprocess_input
from tensorflow.keras.losses import categorical_crossentropy
from tensorflow.keras.initializers import glorot_uniform
from tensorflow.keras.optimizers import SGD, Adam
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.preprocessing.image import img_to_array
from matplotlib import pyplot as plt


ld = pd.read_csv('/content/drive/MyDrive/Data_Augmentation/Data.csv', names = ['ID','Name','Class'])
ld['Class'].value_counts()
ds = ld['Class'].unique() 
dataset_path ='/content/drive/MyDrive/Data_Augmentation/Logo'


def labelDecoder(labels):
    result=[]
    for label in labels:
        if label == 'Sun': i = 0
        if label == 'Lion': i = 1
        if label == 'Human': i = 2
        if label == 'Compass': i = 3
        # if i == 0 or i == 1 or i ==2 or i == 3:
        result.append(i)
    return np.array(result)
def load(image_paths, verbose=-1):
# Initialize the list of images and labels
    data = []
    labels = []
# Loop over input paths to read the data
# Load images
# Assuming path in following format:
# /path/to/dataset/{class}/{image-name}.jpg
    for (i, path) in enumerate(image_paths):
        image = cv.imread(path)
        label = path.split(os.path.sep)[-2]
# Resize image
        image = cv.resize(image, (224, 224))
# Push into data list
        data.append(image)
# Encode labels as intergers
        labels.append(label)
# Show update
        if verbose > 0 and i > 0 and (i + 1) % verbose == 0:
           print("[INFO] processed {}/{}".format(i + 1, len(image_paths)))# Return a tuple of data and labels
    return (np.array(data), np.array(labels))
imagePaths = []
# ds = np.delete(ds,0)
#print(label)
for diag in ds:
    paths = [os.path.join(dataset_path, diag, s) for s in os.listdir(path = os.path.join(dataset_path,diag)) if '.jpg' in s] 
    imagePaths.extend(paths)
random.seed(42)
random.shuffle(imagePaths)

# initialize the shape of image,
# and the number of class
img_height,img_width = 224,224
num_classes = 4  
# initialize the number of epochs to train for,
# and batch size
BatchSize = 64
Epochs = 25
# initialize the data and labels
print("[INFO] loading images...")
(data, labels) = load(imagePaths, verbose=500)
labels = labelDecoder(labels)
# print(labels, data)

# initialize the shape of image,
# and the number of class
img_height,img_width = 224,224
num_classes = 4  
# initialize the number of epochs to train for,
# and batch size
BatchSize = 64
Epochs = 25
# initialize the data and labels
print("[INFO] loading images...")
(data, labels) = load(imagePaths, verbose=500)
labels = labelDecoder(labels)

# Show memory consumption
print("[INFO] features matrix: {:.1f}MB".format(data.nbytes / (1024 * 1024.0)))
# Partition the data.
# training: 75%, testing: 25%
#data = np.array(data,dtype='int')
(trainX, testX, trainY, testY) = train_test_split(data, labels, test_size= 0.25, random_state=42)
trainY = to_categorical(trainY, num_classes)
testY = to_categorical(testY, num_classes)
trainX=trainX.astype('float32')
testX=testX.astype('float32')
print ("number of training examples = " + str(trainX.shape[0]))
print ("number of test examples = " + str(testX.shape[0]))
print ("X_train shape: " + str(trainX.shape))
print ("Y_train shape: " + str(trainY.shape))
print ("X_test shape: " + str(testX.shape))
print ("Y_test shape: " + str(testY.shape))

"""vgg16"""
from keras.models import Sequential
from keras.layers import Conv2D, MaxPooling2D, Dropout, Flatten, Dense, Activation, BatchNormalization
from keras.models import Sequential
from sklearn.metrics import f1_score
IMAGE_WIDTH, IMAGE_HEIGHT, IMAGE_CHANNELS = 224, 224, 3
IMAGE_SHAPE = (IMAGE_WIDTH, IMAGE_HEIGHT, IMAGE_CHANNELS) 

Vgg16_model = applications.vgg16.VGG16(input_shape=IMAGE_SHAPE,include_top = False, weights= 'imagenet')
x = Vgg16_model.output
x = GlobalAveragePooling2D()(x)
x = Dense(4069,activation ='relu')(x)
x = Dense(4069,activation = 'relu')(x)
predictions = Dense(4, activation='softmax')(x)
model = Model(inputs = Vgg16_model.input, outputs = predictions)
adam = Adam(learning_rate=0.000001)
model.compile(optimizer= adam, loss='categorical_crossentropy', metrics=['accuracy'])
model.summary()

H=model.fit(trainX, trainY, batch_size=BatchSize, epochs=Epochs, verbose=1, validation_data=(testX, testY),steps_per_epoch=len(trainX)//BatchSize)

plt.figure(figsize = (15,5))
plt.subplot(1,2,1)
plt.title('Accuracy,Loss')
plt.plot(H.history['accuracy'], label = 'training acc')
plt.plot(H.history['val_accuracy'], label = 'validation acc')
plt.legend()
plt.subplot(1,2,2)
plt.plot(H.history['loss'], label = 'training loss')
plt.plot(H.history['val_loss'], label = 'validation loss')
plt.legend()
plt.title('Loss')
plt.savefig('plot.png', bbox_inches="tight")
# print loss and test accuracy
preds = model.evaluate(testX, testY)
print ("Loss = " + str(preds[0]))
print ("Test Accuracy = " + str(preds[1]))


from tensorflow.keras.models import Model
feature_layer = model.layers[-4].output
extractor = Model(inputs = Vgg16_model.input, outputs = feature_layer)
extractor.summary()

#h??m tr??ch xu???t vector ?????c ch??ng
def feature_vt(img_path):
   img = image.load_img(img_path, target_size=(224,224))
   x = image.img_to_array(img)
   x = np.expand_dims(x, axis = 0)
   feature = extractor.predict(x)
      # print(feature.shape)
   value = np.asarray(feature).reshape((feature.shape[1], feature.shape[0])) #reshape l???i feature th??nh 1 ma tr???n c?? 512 h??ng v?? 1 c???t feature.shape[1] 
      # = 512 v?? feature.shpe[0] = 1 --> t???o ra m???ng (512, 1) 
      # print(value)
   value = value.flatten()
   return value

#tr??ch xu???t vector ?????c tr??ng cho t???p data
import csv
# path_to_csv = '/content/drive/MyDrive/dataML_up/feature_train.csv'   #file cho h??nh ???nh ko text
path_to_csv = '/content/drive/MyDrive/DataAI/feature_train.csv'

with open(path_to_csv, 'w') as csvfile:
    writer = csv.writer(csvfile)
    header = 'Labels'
    data = [header]
    for i in range(512):
      feature_n = 'feature' +str(i)
      data.append(feature_n)
    writer.writerow(data)
    for i in range(len(imagePaths)):
      data = [labels[i]]
      # print(imagePaths[i])
      img = image.load_img(imagePaths[i], target_size=(224,224))
      x = image.img_to_array(img)
      # x = x.reshape((1, x.shape[0], x.shape[1], x.shape[2]))
      x = np.expand_dims(x, axis = 0)
      feature = extractor.predict(x)
      value = np.asarray(feature).reshape((feature.shape[1], feature.shape[0])) #reshape l???i feature th??nh 1 ma tr???n c?? 512 h??ng v?? 1 c???t feature.shape[1] 
      # = 512 v?? feature.shpe[0] = 1 --> t???o ra m???ng (512, 1) 
      # print(value)
      value = value.flatten()
      # print(value)
      data.extend(value)
      # print(data)
      writer.writerow(data)
      
import numpy as np
np.random.seed(1234)
from math import sqrt
 
# calculate euclidean distance
def euclidean_distance(a, b):
	return sqrt(sum((e1-e2)**2 for e1, e2 in zip(a,b)))


#code cho 1 t???p test
j = 0
path_csv = []          # m???ng ch??a link cho file csv
Arr_total = []         # m???ng ch???a t???t c??? input n??i ch??a c??c ?????c tr??ng
input = []             # m???ng ch???a ?????a ch??? ?????u v??o
 #L???y c??c gi?? tr??? vector ?????c tr??ng c???a t???p d??? li???u
# df_test = pd.read_csv('/content/drive/MyDrive/dataML_up/feature_train.csv')
df_test = pd.read_csv('/content/drive/MyDrive/DataAI/feature_train.csv')
Arr = np.asarray(df_test.iloc[:,1:513])
Label_arr = np.asanyarray(df_test.iloc[:,0])
for s in os.listdir(path = os.path.join(dataset_path_test,'sun_test')):  # l???y ???nh test 
    if '.jpg' in s:
     paths = os.path.join(dataset_path_test, 'sun_test', s)
    # img_test = '/content/drive/MyDrive/dataML_t/hm2.jpg'    #input
    path_to_csv = '/content/drive/MyDrive/test_MLtext/distance_compass' + str(j) +  '.csv'    #File l??u kho???ng c??ch t??nh ???????c
    path_csv.append(path_to_csv)
    #L???y gi?? tr??? vector ?????c tr??ng input
    value_feature = feature_vt(paths)    
    input.append(paths)
    Arr_dis = []   #m???ng ch???a dist   # ch???a d??? li???u cho 1 input
    with open(path_to_csv, 'w') as csvfile:
        writer = csv.writer(csvfile)
        for i in range(len(imagePaths)):
          tempt = [i]
          tempt.append(Label_arr[i])
          dist = euclidean_distance(value_feature, Arr[i])
          tempt.append(dist)
          writer.writerow(tempt)
          Arr_dis.append(tempt)            
    Arr_total.append(Arr_dis)    #m???ng ch??a d??? li???u cho c??c input
    j = j + 1


# code for displaying multiple images in one figure

#import libraries
import cv2
# from matplotlib import pyplot as plt
import matplotlib.image as mpimg

#h??m in ???nh
def showimg(input, path_img, Arr_dis):
    # create figure
    fig = plt.figure(figsize=(25, 10))

    # setting values to rows and column variables
    rows = 3
    columns = 9

    # reading images
    # ImageInput = cv2.imread(input)
    ImageInput = mpimg.imread(input)

    Image = []
    for i in range(26):
      img = mpimg.imread(path_img[i])
      Image.append(img)

    # Adds a subplot at the input position
    fig.add_subplot(rows, columns, 1)

    # showing image
    plt.imshow(ImageInput)
    # plt.axis('off')
    plt.title('0')
    string = str(input)
    plt.xlabel('Input')

    for i in range(26):
      fig.add_subplot(rows, columns, i + 2)

      # showing image
      plt.imshow(Image[i])
      # plt.axis('off')
      plt.title(Arr_dis[i])
      string = str(path_img[i])
      plt.xlabel(string.split('/')[6])


#@title Default title text
#L??m cho 1 chu???i test
from IPython.display import Image
import matplotlib.image as mpimg

for i in range(len(Arr_total)):
  Arr_dis = np.array(Arr_total[i])
  sorted_array = Arr_dis[Arr_dis[:,2].argsort()]
  path_img = []
  arr_dis = []


  for j in range(26):
    arr_dis.append(sorted_array[j][2])
  for j in range(26):
    path_img.append(imagePaths[int(sorted_array[j][0])])
  showimg(input[i], path_img, arr_dis)