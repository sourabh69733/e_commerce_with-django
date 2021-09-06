import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
from tensorflow import keras
import numpy as np
# from __future__ import print_function
from PIL import Image
# import tensorflow_hub as hub
import os 


# model url --cassava_disease model with 6 classes 
# classifier_model = "https://tfhub.dev/google/cropnet/classifier/cassava_disease_V1/2"
IMAGE_SHAPE = (224, 224)

# classifier = tf.keras.Sequential([
    # hub.KerasLayer(classifier_model, input_shape=IMAGE_SHAPE+(3,))
# ])
# keras.models.save_model(classifier,"cassava_model")

classifier = keras.models.load_model("cassava_model")

# classifier.compile("adam",loss="sparse_categorical_crossentropy",metrics=['accuracy'])


image_directory = "media/"

name_map = dict(
    cmd='Mosaic Disease',
    cbb='Bacterial Blight',
    cgm='Green Mite',
    cbsd='Brown Streak Disease',
    healthy='Healthy',
    unknown='Unknown'
)

labels = list(name_map.keys())

def predict_img(img_path):
    image = Image.open(img_path).resize(IMAGE_SHAPE)
    image = np.array(image)/255.0
    pred_img = classifier.predict(image[np.newaxis, ...])
    predicted_class = np.argmax(pred_img[0], axis=-1)
    predicted_class = labels[predicted_class]
    return predicted_class, name_map[predicted_class]

def get_image_files():
    files = os.listdir(image_directory)
    if files:
        file = files[0]
        file = os.path.join(image_directory, file)
        s,c = predict_img(file)
        return  s,c
    return "No file provided", "No file provided"
