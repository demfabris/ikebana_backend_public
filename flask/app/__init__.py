#__init__.py
'''
Flask app instance setup. Extends `config.py` Config object.
Initialize app blueprints and dependencie modules
'''

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_mail import Mail
from oauthlib.oauth2 import WebApplicationClient
from boto3 import resource

import os

from app.config import Development
from app.config import Production

db = SQLAlchemy()
jwt = JWTManager()
mail = Mail()
client = WebApplicationClient(os.environ.get('GOOGLE_CLIENT_ID'))
s3 = resource('s3')


def instance(mode=Production):
    app = Flask(__name__)
    CORS(app)
    app.config.from_object(mode)

    db.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)

    from app.resources.user_auths import user_auths
    from app.resources.content_manager import contents
    from app.resources.oauth import oauth
    app.register_blueprint(oauth)
    app.register_blueprint(user_auths)
    app.register_blueprint(contents)

    return app
