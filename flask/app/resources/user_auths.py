# user_auths.py
'''User logic and endpoints'''

from flask import jsonify, Blueprint, request, abort
from flask_jwt_extended import (jwt_required, get_jwt_identity, 
                                jwt_refresh_token_required)
from app import db
from app.common.notifications import notify_user
from app.common.hashing import hash_password, verify_password
from app.common.uploads import upload_to_s3
from app.common.models import User, Notification, Project
from app.common.jwt import user_gen_jwt
from app.common.email import (
    send_confirmation_link, send_partner_notification_email,
    send_recover_email)

from sqlalchemy.exc import IntegrityError
from datetime import datetime
import json


user_auths = Blueprint('user_auths', __name__)

@user_auths.route('/login', methods=['POST'])
def login():
    '''
    Main user login endpoint

    Note:
        Redirects to `/oauth_login` on attempting google login

    Methods:
        POST

    Raises:
        400: User registered with oAuth tries to log in using password
        403: User email not confirmed
        401: Incorrect credentials

    Returns:
        JWT session key and refresh key
    '''
    payload = request.json
    user_q = User.query.filter_by(username=payload['email']).first()
    if user_q:
        if user_q.oauth_id:
            abort(400)
        if user_q.confirmed is False:
            abort(403)
        jwt = user_gen_jwt(payload['email'], payload['password'])
        refresh_jwt = user_gen_jwt(payload['email'], payload['password'],
                                   refresh=True)
        return jsonify({'key': '{}'.format(jwt),
                        'refresh_key': '{}'.format(refresh_jwt)})
    else:
        abort(401)


@user_auths.route('/user_register', methods=['POST'])
def register():
    '''
    Main endpoint for register new user. No relation with oauth
    
    Methods:
        POST

    Raises:
        IntegrityError

    Returns: 
        Trigger email notification with confirmation link
    '''
    payload = request.json
    aux = User(username=payload['email'],
               email=payload['email'],
               fullname=payload['fullname'],
               password=hash_password(payload['password']))
    '''Try adding to database'''
    try:
        db.session.add(aux)
        db.session.commit()
    except IntegrityError:
        abort(401)
    else:
        response = {
            'registration': 'success',
            'user': '{}'.format(payload['email'])
        }
    finally:
        '''Generate JWT and send confirmation link'''
        access_code = user_gen_jwt(payload['email'], payload['password'])
        send_confirmation_link(aux.email, access_code)
        return jsonify(response)


@user_auths.route('/recover_pass', methods=['POST'])
def recover_pass():
    '''
    Send recovery link to user email

    Methods:
        POST

    Raises:
        IntegrityError
        500: Internal Error
        403: oAuth user trying to recover password, username not found
    '''
    try:
        '''Check if e-mail exists in database'''
        payload = request.json
        user_q = User.query.filter_by(email=payload['email']).first()
    except IntegrityError:
        abort(500)
    else:
        '''Abort if e-mail does not exists in database'''
        if user_q is None:
            abort(403)
        elif user_q.oauth_id:
            abort(403)
        else:
            '''Send recover message if email exists in database'''
            access_code = user_gen_jwt(user_q.email)
            send_recover_email(user_q.email, access_code)
            return jsonify({'response': 'email sent'})


@user_auths.route('/reset_pass', methods=['POST'])
@jwt_required
def reset_pass():
    '''
    Reset password endpoint, expects JWT key

    Methods:
        POST

    Raises:
        IntegrityError
        500: Internal Error
        401: Couldn't find username in database
    '''
    try:
        '''Fetch user object from database
        returns error if jwt identity doesnt match an user'''
        user_q = User.query.filter_by(username=get_jwt_identity()).first()
        if user_q is None:
            '''User does not exist'''
            abort(401)
    except IntegrityError:
        abort(500)
    else:
        payload = request.json
        user_q.password = hash_password(payload['password'])
        db.session.commit()
        return jsonify({'response': 'success'})


@user_auths.route('/verify', methods=['GET'])
@jwt_required
def verify():
    '''
    Registration confirmation endpoint, expects JWT key as query argument

    Methods:
        GET

    Raises:
        IntegrityError
        500: Internal Error
        401: Couldn't find username in database or user already confirmed email
    '''
    try:
        '''Fetch user object from database
        returns error if jwt identity doesnt match an user'''
        user_q = User.query.filter_by(username=get_jwt_identity()).first()
        if user_q is None:
            abort(401)
    except IntegrityError:
        abort(500)
    else:
        '''Throw error if user is already confirmed'''
        if user_q.confirmed is True:
            abort(401)
        else:
            '''Confirms and commit changes'''
            user_q.confirm_email
            db.session.commit()
    finally:
        notify_user(user_q.id, 'welcome')
        return jsonify({'confirmation': 'success',
                        'user': '{}'.format(user_q.username)})


@user_auths.route('/become_partner', methods=['POST'])
@jwt_required
def turn_partner():
    '''
    Endpoint for turning partner

    Methods:
        POST

    Raises:
        IntegrityError
        500: Internal Error
        401: Couldn't find username in database
    '''
    user_q = User.query.filter_by(username=get_jwt_identity()).first()
    if user_q is None:
        abort(401)
    payload = request.json
    try:
        user_q.city = payload['city']
        user_q.tel = payload['tel']
        user_q.personal_address = payload['personal_address']
        user_q.location = payload['location']
        user_q.work_address = payload['work_address']
    except IntegrityError:
        abort(500)
    else:
        if user_q.partner:
            db.session.commit()
            return jsonify({'response': 'data updated'})
        user_q.partner = True
        user_q.partner_on = datetime.now()
        db.session.commit()
        send_partner_notification_email(user_q.email)
        notify_user(user_q.id, 'turned_member')
    return jsonify({'success': 'notification sent'})


@user_auths.route('/user', methods=['GET', 'POST', 'DELETE'])
@jwt_required
def retrieve_user():
    '''
    Main endpoint for user information

    Methods:
        
        GET: Retrieve full user data by `json_dump` method

        POST: Updates public user info if request is form-data. Updates user
        password if request is pure json.

        DELETE: Delete all user notifications

    Raises:
        IntegrityError: Database error
        401: Couldn't find username in database

    Returns:
        Json response on success
    '''
    user_q = User.query.filter_by(username=get_jwt_identity()).first()
    if user_q is None:
        abort(401)
    if request.method == 'GET':
        return jsonify(user_q.json_dump)
    elif request.method == 'POST':
        if 'form-data' in request.content_type:
            payload = request.form
            try:
                user_q.fullname = payload['fullname']
                user_q.bio = payload['bio']
                if request.files:
                    file = request.files['file']
            except IntegrityError:
                abort(500)
            else:
                if request.files:
                    '''upload files if form-data payload'''
                    upload_to_s3('ikebana-app-users', file, user_id=user_q.id)
                    user_q.picture = ('https://ikebana-app-users.s3-sa-east-1.a'+
                                      'mazonaws.com/profile_pictures/'+str(user_q.id)+'_profile_pic.'+
                                      file.mimetype.split('image/')[1])
            finally:
                db.session.commit()
            return jsonify({'response': 'data updated'})
        elif 'application/json' in request.content_type:
            '''if not form-data then password change is requested'''
            payload = request.json
            if user_q.oauth_id:
                abort(500)
            if verify_password(user_q.password, payload['old_pass']):
                try:
                    user_q.password = hash_password(payload['new_pass'])
                except IntegrityError:
                    abort(500)
                finally:
                    db.session.commit()
                    return jsonify({'password': 'updated'})
            else:
                abort(401)
    elif request.method == 'DELETE':
        '''clear notifications'''
        notifications = Notification.query.filter_by(user_id=user_q.id).all()
        try:
            for notif in notifications:
                db.session.delete(notif)
        except IntegrityError:
            abort(500)
        else:
            db.session.commit()
        finally:
            return jsonify({'notifications': 'deleted'})



@user_auths.route('/refresh', methods=['POST'])
@jwt_refresh_token_required
def refresh():
    '''
    Refresh JWT session key endpoint

    Methods:
        POST

    Raises:
        401: Couldn't find username in database

    Returns:
        New JWT session key
    '''
    user_q = User.query.filter_by(username=get_jwt_identity()).first()
    if user_q is None:
        abort(401)
    jwt = user_gen_jwt(user_q.email)
    return jsonify({'key': '{}'.format(jwt)})


@user_auths.route('/update_notif', methods=['POST'])
@jwt_required
def update_msg():
    '''
    Updated notification `is_read` status

    Methods:
        POST

    Raises:
        IntegrityError
        500: Internal Error
        401: Couldn't find username in database

    Returns
        Response success
    '''
    payload = request.json
    notif_q = Notification.query.filter_by(id=payload['notif_id']).first()
    if notif_q is None:
        return jsonify({'error': 'internal'})
    try:
        notif_q.is_read = True
    except IntegrityError:
        abort(500)
    else:
        db.session.commit()
    finally:
        return jsonify({'response': 'success'})


@user_auths.route('/autor_public/<int:id>', methods=['GET'])
def autor_public(id):
    '''
    Endpoint for retrieving autor public info

    Args:
        id (int): User id for querying

    Methods:
        GET
    '''
    proj_q = Project.query.filter_by(id=id).first()
    user_q = User.query.filter_by(email=proj_q.autor.email).first()
    return user_q.json_dump
