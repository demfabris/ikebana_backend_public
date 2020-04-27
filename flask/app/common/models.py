# models.py

from sqlalchemy.ext.mutable import MutableDict
from app import db
from datetime import datetime


class User(db.Model):
    '''User database model'''

    def __repr__(self):
        return (
            'E-mail: {}, Partner: {}'
        ).format(self.email, self.partner)

    __table_name__ = 'User'
    id = db.Column(db.Integer, primary_key=True)
    oauth_id = db.Column(db.String, nullable=True, unique=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(25), unique=True, nullable=False)
    tel = db.Column(db.String(25), nullable=True)
    city = db.Column(db.String, nullable=True)
    personal_address = db.Column(db.String, nullable=True)
    work_address = db.Column(db.String, nullable=True)
    location = db.Column(db.String, nullable=True)
    fullname = db.Column(db.String(70), nullable=True)
    partner = db.Column(db.Boolean, default=False)
    partner_on = db.Column(db.DateTime, nullable=True)
    created_on = db.Column(db.DateTime, default=datetime.now())
    password = db.Column(db.String(30), nullable=False)
    confirmed = db.Column(db.Boolean, nullable=False, default=False)
    confirmed_on = db.Column(db.DateTime, nullable=True)
    bio = db.Column(db.Text, nullable=True, default='')
    picture = db.Column(db.String(60), nullable=True,
                        default='https://ikebana-app-users.s3-sa-east-1.' +
                        'amazonaws.com/default/default_user.png')

    @property
    def json_dump(self):
        '''Dumps itself (object) as json serializable'''
        total_orders = 0
        '''Catching amount of orders'''
        aux = [pj.orders for pj in self.projects]
        total_orders = sum(aux)
        '''Checking if is oAuth user'''
        def _(): return True if self.oauth_id else False
        return dict(id=self.id, username=self.username, email=self.email,
                    tel=self.tel, fullname=self.fullname, isPartner=self.partner,
                    partnerWhen=self.partner_on,
                    createdOn=self.created_on,
                    isConfirmed=self.confirmed, bio=self.bio,
                    picture=self.picture, city=self.city,
                    projects_amount=len(self.projects),
                    total_orders=total_orders,
                    location=self.location, work_address=self.work_address,
                    personal_address=self.personal_address,
                    notifications=[notif.json_dump for notif in
                                   self.notifications], is_oauth=_())

    @property
    def status(self):
        '''Return confirmation status'''
        if self.confirmed is False:
            return (
                'Created on : {}, confirmed e-mail : {}'
            ).format(self.created_on, self.confirmed)
        else:
            return (
                'Created on : {}, e-mail not confirmed'
            ).format(self.created_on)

    @property
    def confirm_email(self):
        '''Confirm user email registration'''
        self.confirmed = True
        self.confirmed_on = datetime.now()

    @property
    def turn_partner(self):
        '''Promote this user to partner status'''
        self.partner = True



class Project(db.Model):
    '''Project arrangement model'''

    def __repr__(self):
        return f'Project: {self.name}, autor: {self.autor.email}'

    __table_name__ = 'Project'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True, nullable=False)
    autor_id = db.Column(db.Integer, db.ForeignKey('user.id'),
                         nullable=False)
    autor = db.relationship('User', backref=db.backref('projects', lazy=True))
    type = db.Column(db.String, nullable=False, default='arrangement')
    created_on = db.Column(db.DateTime, default=datetime.now())
    picture = db.Column(MutableDict.as_mutable(db.JSON), nullable=True) 
    video = db.Column(db.String, nullable=True)
    liked_by = db.Column(MutableDict.as_mutable(db.JSON), nullable=True,
                         default=dict())
    description = db.Column(db.Text, nullable=False, default='')
    orders = db.Column(db.Integer, nullable=False, default=0)
    allow = db.Column(db.Boolean, nullable=False, default=False)

    @property
    def json_dump(self):
        '''Dumps itself (object) as json serializable'''
        return dict(project_id=self.id, name=self.name, orders=self.orders, 
                    type=self.type,
                    autor=self.autor.username, likes=len(self.liked_by),
                    description=self.description, pictures=self.picture,
                    created_on=self.created_on, video=self.video,
                    avaiable_on=self.autor.city, autor_pic=self.autor.picture,
                    autor_fullname=self.autor.fullname, liked_by=self.liked_by,
                    allow=self.allow)


class Notification(db.Model):
    '''User notification message table'''

    def __repr__(self):
        return f'Notification for user {self.user.email}, when: {self.sended_on}'

    __table_name__ = 'Notification'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('notifications',
                                                      lazy=True))
    sender = db.Column(db.String, nullable=False, default='Mensagem do Sistema')
    sended_on = db.Column(db.DateTime, default=datetime.now())
    content = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)

    @property
    def text(self):
        return f'Content: {self.content}'

    @property
    def json_dump(self):
        '''Dumps itself as json serializable'''
        return dict(user_id=self.user_id, user=self.user.email, id=self.id,
                    sended_on=self.sended_on, content=self.content,
                    is_read=self.is_read)
