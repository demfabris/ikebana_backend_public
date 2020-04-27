# oauth.py
'''Oauth endpoints'''
from flask import Blueprint, jsonify, request, abort

from app import client, db
from app.common.models import User
from app.common.hashing import hash_password
from app.common.jwt import user_gen_jwt
from sqlalchemy.exc import IntegrityError

import json
import os
import requests

oauth = Blueprint('oauth', __name__)


@oauth.route('/oauth_login', methods=['GET'])
def login_endpoint():
    '''
    oAuth2 login endpoint

    Methods:
        GET

    Returns:
        First request redirect to google approval
    '''

    '''Fetch oauth configuration json'''
    config_payload = requests.get(
        os.environ.get('GOOGLE_DISCOVERY_URL')
    ).json()
    auth_endpoint = config_payload['authorization_endpoint']
    '''Generate authorization request'''
    request_uri = client.prepare_request_uri(
        auth_endpoint,
        redirect_uri='https://fabricio7p.com.br/oauth',
        scope=['openid', 'email', 'profile'],
    )
    return jsonify({'request_uri': '{}'.format(request_uri)})


@oauth.route('/callback')
def oauth_callback():
    '''
    oAuth2 Callback endpoint, expects google accepted query string
    '''
    '''Parse given authorization code'''
    code = request.args.get('code')
    config_payload = requests.get(
        os.environ.get('GOOGLE_DISCOVERY_URL')
    ).json()
    token_endpoint = config_payload['token_endpoint']
    '''Prepare the token request'''
    '''Spits out token_url, headers and body'''
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url='https://fabricio7p.com.br/oauth',
        code=code
    )
    '''Send the actual request that gets access to user info'''
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(os.environ.get('GOOGLE_CLIENT_ID'),
              os.environ.get('GOOGLE_CLIENT_SECRET')),
    )
    '''Parse received token'''
    '''Retrieve user information from google response'''
    client.parse_request_body_response(json.dumps(token_response.json()))
    userinfo_endpoint = config_payload['userinfo_endpoint']
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)
    if userinfo_response.json().get('email_verified'):
        unique_id = userinfo_response.json()['sub']
        users_email = userinfo_response.json()['email']
        picture = userinfo_response.json()['picture']
        users_name = userinfo_response.json()['given_name']
    else:
        return jsonify(
            {'response': 'User email not avaiable or not verified by Google'}
        )
    '''Finally adding google user to own app database'''
    user_q = User(oauth_id=unique_id, username=users_email, email=users_email,
                  picture=picture, fullname=users_name,
                  password=hash_password(os.environ.get('APP_SECRET_KEY')))
    if not User.query.filter_by(oauth_id=unique_id).first():
        try:
            db.session.add(user_q)
            db.session.commit()
        except IntegrityError:
            abort(500)
    access_code = user_gen_jwt(users_email, os.environ.get('APP_SECRET_KEY'))
    refresh_jwt = user_gen_jwt(users_email, refresh=True)
    '''Returns jwt to client'''
    return jsonify({'key': '{}'.format(access_code),
                    'refresh_key': '{}'.format(refresh_jwt)})
