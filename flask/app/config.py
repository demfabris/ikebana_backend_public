# config.py
'''Config file, contains main config object and parent instances'''
import os


class Config(object):
    '''Config base object'''
    SECRET_KEY = os.environ.get('APP_SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///storage/users.db'
    SQLALCHEMY_BINDS = {
        'content': 'sqlite:///storage/content.db'
    }
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = 'secret'
    JWT_TOKEN_LOCATION = ('query_string', 'headers')
    JWT_ACCESS_TOKEN_EXPIRES = 3600
    JWT_QUERY_STRING_NAME = 'code'
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('EMAIL_USER')
    MAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')


class Development(Config):
    '''Dev config. Debug on'''
    PORT = 5000
    DEBUG = True
    TESTING = False
    ENV = 'development'

class Production(Config):
    '''Production config. Debuf off'''
    PORT = 5000
    DEBUG = False
    TESTING = False
    ENV = 'production'
