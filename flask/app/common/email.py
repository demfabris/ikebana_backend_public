# email.py
'''Confirmation and alert e-mail senders'''

from flask_mail import Message

from app import mail


def send_confirmation_link(user_email, access_code):
    '''
    Confirmation link redirect.

    Args:
        user_email (str): Target user email
        access_code (str): Redirect jwt key to send as query string
    
    Returns:
        void
    '''
    msg = Message('Hello', sender="email@email.com",
                  recipients=[user_email])
    msg.html = """
<h1>Confirmação de cadastro</h1>
<a href=https://fabricio7p.com.br//verify?code={}>Clique no link</a>
""".format(access_code)
    mail.send(msg)


def send_partner_notification_email(user_email):
    '''
    Notify that user request partnership

    Args:
        user_email (str): Target user email

    Returns:
        void
    '''
    msg = Message('Hello', sender="email@email.com",
                  recipients=[user_email])
    msg.html = """
<h1>Você solicitou se tornar um membro do site Ikebana Sanguetsu</h1>
<h2>Aproveite as novas funcionalidades.</h2>
"""
    mail.send(msg)


def send_recover_email(user_email, access_code):
    '''
    Reset password redirect notification

    Args:
        user_email (str): Target user email
        access_code (str): Redirect jwt key to send as query string
    
    Returns:
        void
    '''
    msg = Message('Hello', sender="email@email.com",
                  recipients=[user_email])
    msg.html = """
<h1>Recuperação de senha</h1>
<a href="https://fabricio7p.com.br/reset_pass?code={}">Clique aqui</a>
    """.format(access_code)
    mail.send(msg)
