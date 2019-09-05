import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db') #расположение БД
    SQLALCHEMY_TRACK_MODIFICATIONS = False #отключить функцию Flask-SQLAlchemy, которая мне не нужна, 
    #которая должна сигнализировать приложению каждый раз, когда в базе данных должно быть внесено изменение.

    POSTS_PER_PAGE = 5

    MAIL_SERVER = 'smtp.mail.ru'
    MAIL_PORT = 465
    MAIL_USE_TLS = 1
    MAIL_USERNAME = 'mihan1247'
    MAIL_PASSWORD = 'mail1247m'
    ADMINS = ['mihan1247@mail.ru']

    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')

    UPLOAD_FOLDER = './app/static/load'
    UPLOAD_FOLDER_NEW = '\\static\\load\\'
    #ALLOWED_EXTENSIONS = set(['txt', 'csv', 'xls', 'db'])