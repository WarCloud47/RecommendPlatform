from flask import flash, redirect, render_template, request, url_for, jsonify, current_app, send_from_directory, send_file
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename
from datetime import datetime
import os
from app import db 
from app.models import Movie, Sentiment
from app.recommender import bp
from app.recommender.forms import ChooseGenre, ChooseUser, PollReview, TextSeniment, DataRecommend, BackSentiment
import pandas as pd
import numpy as np
from ast import literal_eval
from app.recommender.rated import get_wr_top
from app.recommender.rated_popul_genres import build_chart
from app.recommender.CF_model import get_user_recommend, get_user_love, get_user_not_love, get_new_user_recommend
from app.recommender.vader_sent import sentiment_analyzer_scores
from app.recommender.my_sent import get_rating
from app.recommender.build_recommend import get_ratings_model
from app.recommender.utils_sent import rescale, round_of_rating
from datetime import datetime
from guess_language import guess_language
import sys

@bp.route('/rated', methods=['GET', 'POST'])
#@login_required
def rated():
    table = pd.read_csv("app/static/data/movies.csv")
    table = get_wr_top(table)
    table = table.head(25)
    return render_template("recommender/rated.html", title = 'Топ фильмы', table = table.to_html(classes=["table table-striped","table-hover","thead-dark"], index = False))

@bp.route('/chart')
#@login_required
def chart():
    form = ChooseGenre()
    return render_template("recommender/chart.html", title ='Топ в жанре', form = form)

@bp.route('/get_genre', methods=['POST'])
def get_len():
    genre = request.form['genre']
    movies = pd.read_csv("app/static/data/movies_genres.csv")
    table = build_chart(movies, genre)
    table = table.head(25)
    return jsonify(table.to_html(classes=["table table-striped","table-hover","thead-dark"], index = False))

@bp.route('/collab_filter',)
#@login_required
def collab_filter():
    #form = ChooseUser()
    form = PollReview()
    return render_template("recommender/collab_filter.html", title='Коллаборативная фильтрация', form=form)

@bp.route('/user_predict', methods=['POST'])
def user_predict():
    counter = request.form.get('counter', type = int)
    movies = pd.read_csv("app/static/data/movies.csv")
    movies['genres'] = movies['genres'].fillna('[]').apply(literal_eval).apply(lambda x: [i['name'] for i in x] if isinstance(x, list) else [])
    movies['year'] = (pd.to_datetime(movies['release_date'], errors='coerce').apply(lambda x: str(x).split('-')[0] if x != np.nan else np.nan))
    movies.drop(movies.columns.difference(['movieId','title', 'genres', 'year']), 1, inplace=True)

    if counter == 1:
        ratings = pd.read_csv("app/static/data/ratings.csv")
    else: 
        ratings = pd.read_csv("app/static/data/ratings_test.csv")

    file_name = os.path.abspath('app/static/dump_file')
    
    title = request.form['title']
    year = request.form['year']
    review = request.form['review']
    find = movies[(movies['title'] == title) & (movies['year'] == year)].index.item()
    analyzer = request.form['analyzer']
    if analyzer == 'true': 
        review = sentiment_analyzer_scores(review)
    else:
        if guess_language(review) == 'en':
            review = get_rating(review, 'en')
        else: 
            review = get_rating(review, 'ru')

    if counter == 1:
        USER = ratings['userId'].max() + 1
        ratings = ratings.append(pd.Series([USER, find, review, datetime.utcnow()], index=ratings.columns), ignore_index=True)
        ratings.to_csv("app/static/data/ratings_test.csv", index = False)
        counter = counter + 1
        return jsonify(counter = counter, rating = review)

    elif counter < 5:
        USER = ratings['userId'].max()
        ratings = ratings.append(pd.Series([USER, find, review, datetime.utcnow()], index=ratings.columns), ignore_index=True)
        ratings.to_csv("app/static/data/ratings_test.csv", index = False)
        counter = counter + 1
        return jsonify(counter = counter, rating = review)

    else:
        USER = ratings['userId'].max()
        ratings = ratings.append(pd.Series([USER, find, review, datetime.utcnow()], index=ratings.columns), ignore_index=True)
        ratings.to_csv("app/static/data/ratings_test.csv", index = False)
        counter = counter + 1
        movies = pd.read_csv("app/static/data/movies.csv")
        table = get_new_user_recommend(ratings, movies, USER)
        del table['movieId']
        table.columns = ['Название фильма', 'Жанры', 'Год выпуска', 'Прогноз рейтинга']
        table = table.head(15)
        return jsonify(table = table.to_html(classes=["table table-striped","table-hover","thead-dark"], index = False), counter = counter, rating = review)

@bp.route('/sentiment', methods=['GET', 'POST'])
#@login_required
def sentiment():
    #form = ChooseUser()
    form = TextSeniment()
    form2 = BackSentiment()

    if form2.validate_on_submit():
        rating = form2.rating_sent.data
        rating = round(rescale(rating, 0, 5, -1, 1))
        sentiment = Sentiment(reviewText = form2.review_test.data, sentiment = rating)
        db.session.add(sentiment)
        db.session.commit()
        flash('Отзыв отправлен!')
        #return redirect(url_for('recommender.sentiment'))
    return render_template("recommender/sentiment.html", title='Sentiment анализ', form=form, form2 = form2)

@bp.route('/get_sentiment', methods=['POST'])
def get_sentiment():
    review = request.form['review']
    analyzer = request.form['analyzer']
    if analyzer == 'true': 
        review_rating = sentiment_analyzer_scores(review)
    else:
        if guess_language(review) == 'en':
            review_rating = get_rating(review, 'en')
        else: 
            review_rating = get_rating(review, 'ru')
    return jsonify(rating = review_rating, review = review)

@bp.route('/build_recommend')
#@login_required
def build_recommend():
    #print('Hello world!', file=sys.stderr)
    form = DataRecommend()
    filename_one = 'myratings_new.csv'
    filename_two = 'item_mean.csv'
    filename_three = 'dump_file_test'
    #form = DataRecommend()
    return render_template("recommender/build_recommend.html", title='Прогон datasetа', form = form, filename_one = filename_one, filename_two = filename_two, filename_three = filename_three )

@bp.route('/get_file', methods=['POST'])
def get_file():
    ratings = request.files['file']
    filename = secure_filename(ratings.filename)
    ratings.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
    return jsonify(result="Файл успешно загружен")

@bp.route('/get_recommend', methods=['POST'])
def get_recommend():
    scale_bottom = float(request.form['scale_bottom'])
    scale_top = float(request.form['scale_top'])
    round_rating = request.form['round_rating']
    analyzer = request.form['analyzer']
    if round_rating == 'true': 
        round_rating = True
    else:
        round_rating = False

    if analyzer == 'true': 
        analyzer = True
    else:
        analyzer = False
    
    ratings = pd.read_csv('app/static/load/myratings.txt', sep='\t')
    file_name = os.path.abspath('app/static/load/dump_file_test')

    get_ratings_model(ratings, file_name, scale_bottom, scale_top, round_rating, fast_sent=analyzer)
    #if analyzer == 'true': 
    #    review = sentiment_analyzer_scores(review)
    #get_ratings_model
    return jsonify(result='Построение рейтингов и рекомендательной модели завершено')

@bp.route('/static/load/<path:filename>', methods=['GET', 'POST'])
def download(filename):
    print('Hello world!', file=sys.stderr)
    uploads = os.path.join(current_app.root_path, current_app.config['UPLOAD_FOLDER'])
    print(str(current_app.root_path +  current_app.config['UPLOAD_FOLDER_NEW'] ) + str(filename))
    try:
        return send_from_directory(directory=current_app.root_path +  current_app.config['UPLOAD_FOLDER_NEW'], filename=filename, as_attachment=True)
    except Exception as e:
	    return str(e) + str(current_app.config['UPLOAD_FOLDER_NEW'] ) + str(filename) 

@bp.route('/return-files/')
def return_files_tut():
	try:
		return send_file(current_app.config['UPLOAD_FOLDER_NEW'] + '\\myratings_new.csv')
	except Exception as e:
		return str(e)



