from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from flask import url_for
from flask_login import UserMixin
from app import login
from hashlib import md5

class PaginatedAPIMixin(object):
    @staticmethod
    def to_collection_dict(query, page, per_page, endpoint, **kwargs):
        resources = query.paginate(page, per_page, False)
        data = {
            'items': [item.to_dict() for item in resources.items],
            '_meta': {
                'page': page,
                'per_page': per_page,
                'total_pages': resources.pages,
                'total_items': resources.total
            },
            '_links': {
                'self': url_for(endpoint, page=page, per_page=per_page,
                                **kwargs),
                'next': url_for(endpoint, page=page + 1, per_page=per_page,
                                **kwargs) if resources.has_next else None,
                'prev': url_for(endpoint, page=page - 1, per_page=per_page,
                                **kwargs) if resources.has_prev else None
            }
        }
        return data


class User(PaginatedAPIMixin, UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    posts = db.relationship('Post', backref='author', lazy='dynamic') #u.posts будет запускать запрос базы данных, который возвращает все записи, написанные этим пользователем
    ratings = db.relationship('Rating', backref='author', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username) 

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

    def to_dict(self, include_email=False):
        data = {
            'id': self.id,
            'username': self.username,
            'last_seen': self.last_seen.isoformat() + 'Z',
            'about_me': self.about_me,
            'post_count': self.posts.count(),
            '_links': {
                'self': url_for('api.get_user', id=self.id),
                'avatar': self.avatar(128)
            }
        }
        if include_email:
            data['email'] = self.email
        return data

    def from_dict(self, data, new_user=False):
        for field in ['username', 'email', 'about_me']:
            if field in data:
                setattr(self, field, data[field])
        if new_user and 'password' in data:
            self.set_password(data['password'])

    
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow) #передача самой функции а не вызовы()
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.body)

class Movie(db.Model):
    movieId = db.Column(db.Integer, primary_key=True)
    imdbId = db.Column(db.Integer)
    tmdbId = db.Column(db.Integer)
    title = db.Column(db.Text)
    tagline = db.Column(db.Text)
    genres = db.Column(db.Text)
    overview = db.Column(db.Text)
    poster_path = db.Column(db.Text)
    runtime = db.Column(db.Float)
    release_date = db.Column(db.Date)
    budget = db.Column(db.Integer)
    revenue = db.Column(db.Float)
    popularity = db.Column(db.Float)
    vote_average = db.Column(db.Float)
    vote_count = db.Column(db.Float)
    ratings = db.relationship('Rating', backref='movie', lazy='dynamic')

    def __repr__(self):
        return '<Movie {}>'.format(self.title)

class Rating(db.Model):
    ratingId = db.Column(db.Integer, primary_key=True)
    #userId = db.Column(db.Integer)
    #movieId = db.Column(db.Integer)
    rating = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow) #передача самой функции а не вызовы()
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.movieId'))
    #movieId = db.Column(db.Integer, db.ForeignKey('link.movieId'))

    def __repr__(self):
        return '<Rating {}>'.format(self.rating)

class Sentiment(db.Model):
    reviewId = db.Column(db.Integer, primary_key=True)
    reviewText = db.Column(db.String(5000))
    sentiment = db.Column(db.Integer)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))
