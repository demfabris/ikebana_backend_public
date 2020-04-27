# content_manager.py

'''Manage Ikebana database logic operations'''
import json
from flask import jsonify, Blueprint, request, abort
from app import db
from sqlalchemy.exc import IntegrityError
from app.common.notifications import notify_user
from app.common.models import Project, User
from app.common.uploads import upload_to_s3
from flask_jwt_extended import jwt_required, get_jwt_identity

contents = Blueprint('contents', __name__)

@contents.route('/projects', methods=['POST', 'GET', 'PUT', 'DELETE'])
@jwt_required
def register():
    '''
    Main endpoint for project interaction
    
    Methods:
        POST: Register projects, expects multiform-data payload
        GET: List all user projects
        PUT: Change project info, expects multiform-data payload
        DELETE: Delete project entry

    Raises:
        IntegrityError: Couldn't modify database
        200: Success
        500: Internal Error
        401: Couldn't find username in database
    '''
    user_q = User.query.filter_by(username=get_jwt_identity()).first()
    if request.method == 'POST':
        if user_q.partner:
            payload = request.form
            files = request.files
            '''Handling allow solicitations'''
            if payload['project_allow'] == 'true':
                allow=True
            else:
                allow=False
            try:
                proj_q = Project(name=payload['project_title'], autor_id=user_q.id,
                                 type=payload['project_type'], video=payload['project_video'],
                                 description=payload['project_desc'],
                                 allow=allow)
                db.session.add(proj_q)
                db.session.commit()
            except IntegrityError:
                abort(500)
            else:
                proj_q.picture = dict()
                if len(proj_q.picture) == 0:
                    proj_q.picture.update({'file1':
                                           'https://ikebana-app-content.s3-sa-east-1'+
                                           '.amazonaws.com/static/mainlogo.png'})
                for file, name in zip(files.values(), files.keys()):
                    proj_q.picture.update({name: 'https://ikebana-app-content.s3-sa-east-1.a'+
                                           'mazonaws.com/projects/'+str(proj_q.id)+'_'+name+'_arrang_pic.'+
                                           file.mimetype.split('image/')[1]})
                    upload_to_s3('ikebana-app-content', file,
                                 project_id=proj_q.id, file_name=name)
            finally:
                db.session.commit()
                notify_user(user_q.id, 'project', proj_q.name)
        return jsonify({'response': 'success'})
    elif request.method == 'GET':
        proj_q = Project.query.filter_by(autor_id=user_q.id)
        response = [project.json_dump for project in proj_q]
        return jsonify(response)
    elif request.method == 'PUT':
        if user_q.partner:
            payload = request.form
            files = request.files
            try:
                '''Update project info'''
                proj_q = Project.query.filter_by(id=payload['project_id']).first()
                proj_q.name = payload['project_title']
                proj_q.type = payload['project_type']
                proj_q.video = payload['project_video']
                proj_q.description = payload['project_desc']
                '''Allow solicitations handler'''
                if payload['project_allow'] == 'true':
                    proj_q.allow = True
                else:
                    proj_q.allow = False
            except IntegrityError:
                abort(500)
            else:
                '''Overwrite stored pictures'''
                for file, name in zip(files.values(), files.keys()):
                    proj_q.picture.update({name: 'https://ikebana-app-content.s3-sa-east-1.a'+
                                           'mazonaws.com/projects/'+str(proj_q.id)+'_'+name+'_arrang_pic.'+
                                           file.mimetype.split('image/')[1]})
                    upload_to_s3('ikebana-app-content', file,
                                 project_id=proj_q.id, file_name=name)
                '''Remove pictures entries marked for deletion'''
                for entry in payload:
                    if 'file' in entry and entry in proj_q.picture:
                        if payload[entry] == 'del':
                            proj_q.picture.pop(entry)
                if len(proj_q.picture) == 0:
                    proj_q.picture.update({'file1':
                                           'https://ikebana-app-content.s3-sa-east-1'+
                                           '.amazonaws.com/static/mainlogo.png'})
            finally:
                db.session.commit()
    elif request.method == 'DELETE':
        if user_q.partner:
            payload = request.json
            proj_q = Project.query.filter_by(id=payload['project_id']).first()
            try:
                db.session.delete(proj_q)
                db.session.commit()
            except IntegrityError:
                abort(500)
            finally:
                return jsonify({'delete': 'success'})
    return jsonify({'response': 'success'})

        



@contents.route('/list', methods=['GET'])
def list_arrangements():
    '''
    List all ikebana arrangements

    Methods:
        GET

    Returns:
        All avaiable projects as json
    '''
    projects = [proj.json_dump for proj in Project.query.all()]
    return jsonify(projects)

@contents.route('/like_project', methods=['POST'])
@jwt_required
def like_project():
    '''
    Increment project like count

    Methods:
        POST

    Raises:
        500: IntegrityError
        401: Couldn't find username in database
    '''
    payload = request.json
    proj_q = Project.query.filter_by(id=payload['project_id']).first()
    '''Select project'''
    if proj_q is None:
        abort(500)
    '''Checks if it is a logged user'''
    user_q = User.query.filter_by(username=get_jwt_identity()).first()
    if user_q:
        try:
            proj_q.liked_by.update({user_q.id: user_q.email})
            db.session.commit()
        except IntegrityError:
            abort(500)
        else:
            return jsonify({'response': 'success as logged'})

@contents.route('/get_project/<id>', methods=['GET'])
def get_projcet(id):
    '''
    Endpoint for retrieving single project info

    Args:
        id (int): Project id

    Methods:
        GET

    Raises:
        401: Couldn't find username in database
    '''
    proj_q = Project.query.filter_by(id=id).first()
    return proj_q.json_dump


@contents.route('/solicitation', methods=['POST'])
@jwt_required
def new_solicitation():
    '''
    Create new arrangement solicitation

    Methods:
        POST
    
    Raises:
        IntegrityError
        401: Couldn't find username in database
        500: Internal Error

    '''
    user_q = User.query.filter_by(username=get_jwt_identity()).first()
    arrangements = request.json[0]
    msg = request.json[1]
    for arr in arrangements.values():
        proj_q = Project.query.filter_by(id=arr['project_id']).first()
        try:
            proj_q.orders += 1
            db.session.commit()
        except IntegrityError:
            abort(500)
        else:
            notify_user(proj_q.autor.id, 'new_request', proj_q.name, user_q.fullname,
                        msg['autor_msg'])
    return jsonify({'response': 'success'})


@contents.route('/search', methods=['POST'])
def search():
    '''
    Search queries endpoint

    Methods:
        POST

    Returns:
        Search results as json
    '''
    query = '%{}%'.format(request.json['string'])
    proj_results = Project.query.filter(Project.name.like(query)).all()
    proj_results = [proj.json_dump for proj in proj_results]
    return jsonify(proj_results)
