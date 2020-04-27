#notifications.py
'''Notification sender logic'''
from .models import Notification
from sqlalchemy.exc import IntegrityError
from app import db

welcome='''
Bem-vindo ao projeto Ikebana Sanguetsu. Este website é uma plataforma de
aprendizagem e compartilhamento de arranjos e ideias, bem como videoaulas e
tutoriais.
'''
turned_member='''
Você se tornou membro do website. Agora poderá criar novos arranjos e projetos
para compartilhar com a comunidade.
'''

new_project='''
Novo projeto adicionado: ##
'''

new_request='''
Foi requisitado o arranjo: ##
Por: @@

Mensagem do solicitador:
&&

Faça-o se puder
'''

def notify_user(user_id, content, *args):
    '''Wrapper function to create Notification object and attempt to store in
    DB

    Args:
        user_id (int): User id (primary key)
        content (str): Message text, pick from above
        *args: value string to be replaced on content message
        response: placeholder for return message

    Raises:
        IntegrityError: Couldn't add notification object to database
    
    Return:
        void
    '''
    if 'request' in content:
        response = new_request
        response = response.replace('##', args[0])
        response = response.replace('@@', args[1])
        response = response.replace('&&', args[2])
    elif 'project' in content:
        response = new_project
        response = response.replace('##', args[0])
    elif 'turned_member' in content:
        response = turned_member
    elif 'welcome' in content:
        response = welcome
    notif = Notification(user_id=user_id, content=response)
    try:
        db.session.add(notif)
    except IntegrityError:
        abort(500)
    else:
        db.session.commit()
