# jwt.py
'''JWT generation logic'''

from flask import abort
from flask_jwt_extended import (create_access_token,
                                create_refresh_token)
from .models import User
import datetime
from .hashing import verify_password


def user_gen_jwt(username, password='', refresh=False):
    '''
    Main JWT dispatching function. Checks incoming username data and checks if 
    user exists in Database.

    Args:
        username (str): Username string `email` that will be queried into DB
        [password (str)]: Password string unhashed to output JWT with increased
        security
        refresh (bool): Whether return as refresh token or not

    Raises:
        TypeError,
        Abort 401: Failed username query

    Returns:
        access_token (str): JWT session key with 3600min life-span
        [refresh_token (str)]: JWT refresh session key, returned only if
        refresh==True
    '''
    aux = User.query.filter_by(username=username).first()
    if aux and verify_password(aux.password, password):
        if refresh:
            refresh_token = create_refresh_token(identity=username)
            return refresh_token
        access_token = create_access_token(identity=username)
        return access_token
    elif aux and password == '':
        access_token = create_access_token(identity=username)
        return access_token
    else:
        abort(401)
