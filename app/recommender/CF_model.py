
#%%
import os
import pandas as pd
from ast import literal_eval
import numpy as np
from surprise import Reader
from surprise import Dataset
from surprise.model_selection import cross_validate
from surprise import SVD
from surprise.model_selection import GridSearchCV
from surprise import dump

def new_trainset(ratings, filename, scale_bottom = 0.0, scale_top = 5.0):
    reader = Reader(rating_scale=(scale_bottom, scale_top))
    data = Dataset.load_from_df(ratings, reader)
    svd = SVD() 
    trainset = data.build_full_trainset()
    svd.fit(trainset)
    file_name = os.path.abspath(filename)
    dump.dump(file_name, algo=svd)

def get_new_user_recommend(ratings, movies, USER):
    movies['genres'] = movies['genres'].fillna('[]').apply(literal_eval).apply(lambda x: [i['name'] for i in x] if isinstance(x, list) else [])
    movies['year'] = (pd.to_datetime(movies['release_date'], errors='coerce').apply(lambda x: str(x).split('-')[0] if x != np.nan else np.nan))
    movies.drop(movies.columns.difference(['movieId','title', 'genres', 'year']), 1, inplace=True)
    movies.set_index('movieId', inplace = True)
    reader = Reader(rating_scale=(0.5, 5))
    data = Dataset.load_from_df(ratings[['userId', 'movieId', 'rating']], reader)
    svd = SVD() #(n_factors=160, n_epochs=100, lr_all=0.005, reg_all=0.1) 0.86?
    #cross_validate(svd, data, measures=['RMSE', 'MAE'], cv = 5)
    user_ratings = ratings[(ratings['userId'] == USER)]
    user_ratings= user_ratings.set_index('movieId')
    user_ratings = user_ratings.join(movies)
    user_ratings.drop(user_ratings.columns.difference(['movieId','title', 'genres', 'year']), 1, inplace=True)
    movies_cut = movies[~movies.isin(user_ratings)].dropna()
    trainset = data.build_full_trainset()
    svd.fit(trainset)
    file_name = os.path.abspath('app/static/dump_file')
    dump.dump(file_name, algo=svd)
    user_predict = movies_cut.copy()
    user_predict = user_predict.reset_index()
    user_predict['Estimate_Score'] = user_predict['movieId'].apply(lambda x: svd.predict(USER, x).est)
    user_predict = user_predict.sort_values('Estimate_Score', ascending=False)
    return user_predict

#%%
def get_user_recommend(ratings, movies, USER, filename):
    movies['genres'] = movies['genres'].fillna('[]').apply(literal_eval).apply(lambda x: [i['name'] for i in x] if isinstance(x, list) else [])
    movies['year'] = (pd.to_datetime(movies['release_date'], errors='coerce').apply(lambda x: str(x).split('-')[0] if x != np.nan else np.nan))
    movies.drop(movies.columns.difference(['movieId','title', 'genres', 'year']), 1, inplace=True)
    movies.set_index('movieId', inplace = True)
    user_ratings = ratings[(ratings['userId'] == USER)]
    user_ratings= user_ratings.set_index('movieId')
    user_ratings = user_ratings.join(movies)
    user_ratings.drop(user_ratings.columns.difference(['movieId','title', 'genres', 'year']), 1, inplace=True)
    movies_cut = movies[~movies.isin(user_ratings)].dropna()
    _, svd = dump.load(filename)
    user_predict = movies_cut.copy()
    user_predict = user_predict.reset_index()
    user_predict['Estimate_Score'] = user_predict['movieId'].apply(lambda x: svd.predict(USER, x).est)
    user_predict = user_predict.sort_values('Estimate_Score', ascending=False)
    return user_predict

#%%
def get_user_love(ratings, movies, USER):
    user_love = ratings[(ratings['userId'] == USER) & (ratings['rating'] > 3.5)]
    user_love = user_love.set_index('movieId')
    user_love = user_love.join(movies)['title']
    return user_love

#%%
def get_user_not_love(ratings, movies, USER):
    user_love = ratings[(ratings['userId'] == USER) & (ratings['rating'] < 4.0)]
    user_love = user_love.set_index('movieId')
    user_love = user_love.join(movies)['title']
    return user_love