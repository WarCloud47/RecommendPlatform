import os
import pandas as pd
from app.recommender.CF_model import new_trainset
from app.recommender.vader_sent import sentiment_analyzer_scores
from app.recommender.my_sent import get_rating
from app.recommender.utils_sent import clean_text
from guess_language import guess_language
from app.recommender.utils_sent import rescale, round_of_rating


def get_ratings_model(ratings, file_name, scale_bottom = 0, scale_top = 5, round_rating = True, fast_sent = False):
    ratings['rating'] = ratings['Review'].apply(review_to_ratings, args = (scale_bottom, scale_top, fast_sent))
    del ratings['Review']
    ratings.to_csv('app/static/load/myratings_new.csv', index=False)

    item_mean = ratings[['idItem','rating']].copy()
    item_mean = item_mean.groupby(['idItem'], as_index=False).mean()
    if round_rating:
        item_mean['rating'] = item_mean['rating'].apply(round_of_rating)

    item_mean.to_csv('app/static/load/item_mean.csv', index=False)

    new_trainset(ratings, file_name, scale_bottom, scale_top)

def review_to_ratings(review, scale_bottom = 0, scale_top = 5, fast_sent = False):
    if fast_sent:
        return sentiment_analyzer_scores(str(review), scale_bottom = scale_bottom, scale_top = scale_top)
    else:
        return get_rating(str(review), guess_language(review), scale_bottom = scale_bottom, scale_top = scale_top)

