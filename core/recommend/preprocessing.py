import tensorflow as tf
import tensorflow.keras as keras
import pandas  as pd
import numpy as np

model  = keras.load_model('recommend.h5')
vocabulary_lookup = pd.read_csv("vocabulary_lookup.csv")

# inferences
movie_embeddings = model.get_layer("item_embedding").get_weights()[0]
print("Movie Embedding:\t", movie_embeddings.shape)
# movie_embedding[1]
def get_movie_title_by_id(movieId):
    return list(movies[movies['movieId']==movieId].title)[0]

def get_movie_id_by_id(movie_title):
    return list(movies[movies['title']==movie_title].movieId)[0]


def create_preditions(query_movies):
    movie_embeddings = model.get_layer("item_embedding").get_weights()[0]
    query_embeddings = []
    for movie_title in query_movies:
        # get_movie_title_by_id
        movieId = get_movie_id_by_id(movie_title)
        token_id = vocabulary_lookup[movieId]
        movie_embedding = movie_embeddings[token_id]
        query_embeddings.append(movie_embedding)
    query_embeddings = np.array(query_embeddings)
    # return query_embeddings
    similarities = tf.linalg.matmul(
        tf.math.l2_normalize(query_embeddings),
        tf.math.l2_normalize(movie_embeddings),
        transpose_b=True,
    )
    
    _, indices = tf.math.top_k(similarities, k=5)
    indices = indices.numpy().tolist()
    for idx, title in enumerate(query_movies):
        print(title)
        print("".rjust(len(title), "-"))
        similar_tokens = indices[idx]
        for token in similar_tokens:
            similar_movieId = vocabulary[token]
            similar_title = get_movie_title_by_id(similar_movieId)
            print(f"- {similar_title}")
            yield similar_title
    