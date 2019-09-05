from flask import Blueprint

bp = Blueprint('recommender', __name__)

from app.recommender import routes