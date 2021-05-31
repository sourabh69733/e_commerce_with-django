import numpy as np
import tensorflow as tf
import tensorflow.keras as keras
import tensorflow_hub as hub
from PIL import Image

classifier = hub.KerasLayer(
    'https://tfhub.dev/google/cropnet/classifier/cassava_disease_V1/2')

model = keras.models.Sequential([
    keras.layers.Dense(128, "selu")

])

model.load_weights(classifier.weights)
