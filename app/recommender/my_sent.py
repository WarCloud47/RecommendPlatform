#%%
import keras as K
import os
from keras.datasets import imdb
from keras.preprocessing import sequence
from keras.models import load_model
from app.recommender.utils_sent import rescale, round_of_rating
import pickle

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2' 

def get_rating(review , lang = 'en', maxlen = 50, scale_bottom = 0, scale_top = 5):
    if (lang == 'en'):
        K.backend.clear_session()
        d = K.datasets.imdb.get_word_index()
        #review = clean_text(review)
        words = review.split()
        review = []
        for word in words:
          if word not in d: 
            review.append(2)
          else:
            review.append(d[word]+3) 

        review = sequence.pad_sequences([review], maxlen=80)
        model = load_model('app/static/imdb_model.h5')
        prediction = model.predict(review)
        return round_of_rating(rescale(prediction[0][0], 0, 1, scale_bottom, scale_top))
    else:
        K.backend.clear_session()
        with open('app/static/tokenizer_twitter.pickle', 'rb') as handle:
            tokenizer = pickle.load(handle)
        review = tokenizer.texts_to_sequences(review)
        review = sequence.pad_sequences(review, maxlen=30)
        model = load_model('app/static/twitter_model.h5')
        prediction = model.predict(review)
        return round_of_rating(rescale(prediction[0][0], 0, 1, scale_bottom, scale_top))
        




