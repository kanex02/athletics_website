import os
import sqlalchemy as db
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'super-secret-key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'info.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    RESULTS_PER_PAGE = 35
    ZO_SPORT_DATABASE_URL = ''
    SESSION_COOKIE_SECURE = True
    TEMPLATES_AUTO_RELOAD = True