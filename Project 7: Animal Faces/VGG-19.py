"""
PROJECT 7: Vehicle Classification
TASK: Multi-class classification
PROJECT GOALS AND OBJECTIVES
PROJECT GOAL
> Studying architecture: VGG
PROJECT OBJECTIVES
1. Exploratory Data Analysis
2. Training VGG-16
3. Training VGG-19
"""
# %%
# IMPORT LIBRARIES

import numpy as np
import pandas as pd
import cv2
import os
import pathlib
import itertools

from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Dropout, Flatten, Dense, Layer, BatchNormalization
from tensorflow.keras.models import Sequential
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
from keras.preprocessing.image import ImageDataGenerator, load_img

import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go

# %%
# PATH & LABEL PROCESS
# Main path
train_path = "/Users/rttrif/Data_Science_Projects/Tensorflow_Certification/Project_7_Animal_Faces/data/afhq/train/"

val_path = "/Users/rttrif/Data_Science_Projects/Tensorflow_Certification/Project_7_Animal_Faces/data/afhq/val/"

classes = {"cat": "0", "dog": "1", "wild": "2"}

all_filenames_train = []
all_categories_train = []
for classElement in classes:
    filenames = os.listdir(train_path + classElement)
    all_filenames_train += [classElement + "/" + file for file in filenames]
    all_categories_train += [classes[classElement]] * len(filenames)

train_df = pd.DataFrame({'filename': all_filenames_train,
                         'class': all_categories_train})
# Checking results
print(train_df.tail())
print(train_df.info())

all_filenames_test = []
all_categories_test = []
for classElement in classes:
    filenames = os.listdir(val_path + classElement)
    all_filenames_test += [classElement + "/" + file for file in filenames]
    all_categories_test += [classes[classElement]] * len(filenames)

test_df = pd.DataFrame({'filename': all_filenames_test,
                        'class': all_categories_test})
# Checking results
print(test_df.tail())
print(test_df.info())
# %%
# DATA PREPARATION

# Splitting train and test
train_data, valid_data = train_test_split(train_df, test_size=0.20)
train_data = train_data.reset_index(drop=True)
valid_data = valid_data.reset_index(drop=True)

# Checking results
print("Train shape: ", train_data.shape)
print("Validation shape: ", valid_data.shape)
print("Test shape: ", test_df.shape)

print(f'Train class value counts: \n{train_data["class"].value_counts()}')
print(f'Validation class value counts: \n{valid_data["class"].value_counts()}')
print(f'Test class value counts: \n{test_df["class"].value_counts()}')
# %%
# Image generator
train_generator = ImageDataGenerator(rescale=1. / 255,
                                     shear_range=0.3,
                                     zoom_range=0.2,
                                     rotation_range=30,
                                     width_shift_range=0.1,
                                     height_shift_range=0.1,
                                     horizontal_flip=True,
                                     vertical_flip=True,
                                     fill_mode='reflect')

validation_generator = ImageDataGenerator(rescale=1. / 255)

test_generator = ImageDataGenerator(rescale=1. / 255)

# %%
# Applying generator and transformation to tensor
print("Preparing the training data:")
train_images = train_generator.flow_from_dataframe(train_data,
                                                   directory=train_path,
                                                   x_col='filename',
                                                   y_col='class',
                                                   target_size=(256, 256),
                                                   class_mode='categorical',
                                                   batch_size=32)

print("Preparing the validation data:")
valid_images = validation_generator.flow_from_dataframe(valid_data,
                                                        directory=train_path,
                                                        x_col='filename',
                                                        y_col='class',
                                                        target_size=(256, 256),
                                                        class_mode='categorical',
                                                        batch_size=32)
print("Preparing the test data:")
test_images = test_generator.flow_from_dataframe(dataframe=test_df,
                                                 directory=val_path,
                                                 x_col='filename',
                                                 y_col='class',
                                                 target_size=(256, 256),
                                                 class_mode='categorical',
                                                 batch_size=32)
# Checking
print("Checking the training data:")
for data_batch, label_batch in train_images:
    print("DATA SHAPE: ", data_batch.shape)
    print("LABEL SHAPE: ", label_batch.shape)
    break

print("Checking the validation data:")
for data_batch, label_batch in valid_images:
    print("DATA SHAPE: ", data_batch.shape)
    print("LABEL SHAPE: ", label_batch.shape)
    break

print("Checking the test data:")
for data_batch, label_batch in test_images:
    print("DATA SHAPE: ", data_batch.shape)
    print("LABEL SHAPE: ", label_batch.shape)
    break


# %%
# Evaluation and visualization of model parameters

def learning_curves(history):
    pd.DataFrame(history.history).plot(figsize=(20, 8))
    plt.grid(True)
    plt.title('Learning curves')
    plt.gca().set_ylim(0, 1)
    plt.show()


def evaluation_model(history):
    fig, (axL, axR) = plt.subplots(ncols=2, figsize=(20, 8))
    axL.plot(history.history['loss'], label="Training loss")
    axL.plot(history.history['val_loss'], label="Validation loss")
    axL.set_title('Training and Validation loss')
    axL.set_xlabel('Epochs')
    axL.set_ylabel('Loss')
    axL.legend(loc='upper right')

    axR.plot(history.history['accuracy'], label="Training accuracy")
    axR.plot(history.history['val_accuracy'], label="Validation accuracy")
    axR.set_title('Training and Validation accuracy')
    axR.set_xlabel('Epoch')
    axR.set_ylabel('Accuracy')
    axR.legend(loc='upper right')

    plt.show()


def model_confusion_matrix(y_true, y_pred, classes=None, figsize=(10, 10), text_size=15):
    # Create the confustion matrix
    cm = confusion_matrix(y_true, y_pred)
    cm_norm = cm.astype("float") / cm.sum(axis=1)[:, np.newaxis]
    n_classes = cm.shape[0]

    # Plot the figure and make it pretty
    fig, ax = plt.subplots(figsize=figsize)
    cax = ax.matshow(cm, cmap=plt.cm.Blues)  # colors will represent how 'correct' a class is, darker == better
    fig.colorbar(cax)

    # Are there a list of classes?
    if classes:
        labels = classes
    else:
        labels = np.arange(cm.shape[0])

    # Label the axes
    ax.set(title="Confusion Matrix",
           xlabel="Predicted label",
           ylabel="True label",
           xticks=np.arange(n_classes),  # create enough axis slots for each class
           yticks=np.arange(n_classes),
           xticklabels=labels,  # axes will labeled with class names (if they exist) or ints
           yticklabels=labels)

    # Make x-axis labels appear on bottom
    ax.xaxis.set_label_position("bottom")
    ax.xaxis.tick_bottom()

    # Set the threshold for different colors
    threshold = (cm.max() + cm.min()) / 2.

    # Plot the text on each cell
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        plt.text(j, i, f"{cm[i, j]} ({cm_norm[i, j] * 100:.1f}%)",
                 horizontalalignment="center",
                 color="white" if cm[i, j] > threshold else "black",
                 size=text_size)
    plt.show()


# %%
# MODEL: VGG-19

def VGG_19(epochs, patience):
    model = Sequential([
        # CONVOLUTION LAYERS (64, 3×3)
        # Layer C1
        Conv2D(filters=64, kernel_size=(3, 3), padding="same", activation="relu", input_shape=(256, 256, 3)),
        # Layer C2
        Conv2D(filters=64, kernel_size=(3, 3), padding="same", activation="relu"),

        # MAX POOLING LAYER(2×2)
        # Layer S1
        MaxPooling2D((2, 2)),

        # CONVOLUTION LAYERS (128, 3×3)
        # Layer C3
        Conv2D(filters=128, kernel_size=(3, 3), padding="same", activation="relu"),
        # Layer C4
        Conv2D(filters=128, kernel_size=(3, 3), padding="same", activation="relu"),

        # MAX POOLING LAYER(2×2)
        # Layer S2
        MaxPooling2D((2, 2)),

        # CONVOLUTION LAYERS (256, 3×3)
        # Layer C5
        Conv2D(filters=256, kernel_size=(3, 3), padding="same", activation="relu"),
        # Layer C6
        Conv2D(filters=256, kernel_size=(3, 3), padding="same", activation="relu"),
        # Layer C7
        Conv2D(filters=256, kernel_size=(3, 3), padding="same", activation="relu"),
        # Layer C8
        Conv2D(filters=256, kernel_size=(3, 3), padding="same", activation="relu"),

        # MAX POOLING LAYER(2×2)
        # Layer S3
        MaxPooling2D((2, 2)),

        # CONVOLUTION LAYERS (512, 3×3)
        # Layer C9
        Conv2D(filters=512, kernel_size=(3, 3), padding="same", activation="relu"),
        # Layer C10
        Conv2D(filters=512, kernel_size=(3, 3), padding="same", activation="relu"),
        # Layer C11
        Conv2D(filters=512, kernel_size=(3, 3), padding="same", activation="relu"),
        # Layer C12
        Conv2D(filters=512, kernel_size=(3, 3), padding="same", activation="relu"),

        # MAX POOLING LAYER(2×2)
        # Layer S4
        MaxPooling2D((2, 2)),

        # CONVOLUTION LAYERS (512, 3×3)
        # Layer C13
        Conv2D(filters=512, kernel_size=(3, 3), padding="same", activation="relu"),
        # Layer C14
        Conv2D(filters=512, kernel_size=(3, 3), padding="same", activation="relu"),
        # Layer C15
        Conv2D(filters=512, kernel_size=(3, 3), padding="same", activation="relu"),
        # Layer C16
        Conv2D(filters=512, kernel_size=(3, 3), padding="same", activation="relu"),

        # MAX POOLING LAYER(2×2)
        # Layer S5:
        MaxPooling2D((2, 2)),

        # FLATTEN
        Flatten(),

        # FULLY - CONNECTED LAYER(4096)
        # Layer F17
        Dense(4096, activation='relu'),
        # Layer F18:
        Dense(4096, activation='relu'),

        # FULLY - CONNECTED LAYER(1000)
        # Layer F19
        Dense(3, activation="softmax")
    ])

    model.compile(optimizer='Adam',
                  loss='categorical_crossentropy',
                  metrics=["accuracy"])

    model.summary()
    tf.keras.utils.plot_model(model, to_file='VGG-16.png')

    early_stopping_cb = tf.keras.callbacks.EarlyStopping(patience=patience,
                                                         restore_best_weights=True)
    history = model.fit(train_images,
                        validation_data=valid_images,
                        epochs=epochs,
                        callbacks=[early_stopping_cb])

    return history, model


history, model = VGG_19(epochs=5, patience=5)

# Learning curves
learning_curves(history)

# Evaluation model
evaluation_model(history)

# Evaluate the model on the test set
evaluate = model.evaluate(test_images, verbose=2)

# Predicting the test set results
predict = model.fit(test_images)

test_df['prediction'] = np.argmax(predict, axis=-1)
label_map = dict((v, k) for k, v in train_generator.class_indices.items())
test_df['prediction'] = test_df['prediction'].replace(label_map)
test_df['prediction'] = test_df['prediction'].replace({'1': 1, '0': 0})

# Distribution of predicted classes
plt.title('Distribution of predicted classes')
test_df['prediction'].value_counts().plot.pie(figsize=(5, 5))
plt.show()

# Confusion matrix
model_confusion_matrix(test_df['prediction'], predict)
