from datetime import datetime
from werkzeug.security import generate_password_hash, \
     check_password_hash
from sqlalchemy.dialects import mysql

from apps import db
from apps.payments.models import Plan


GENDER_CHOICES = (
    ('M', 'Male'),
    ('F', 'Female'),
)

class User(db.Model):
    __tablename__ = 'auth_user'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    username = db.Column(db.String(120), unique=True)
    email = db.Column(db.String(120), unique=True)
    phone = db.Column(db.String(20))
    company = db.Column(db.String(255))
    country = db.Column(db.String(120))
    website = db.Column(db.String(120))
    industry = db.Column(db.String(120))
    company_size = db.Column(db.String(120))
    password = db.Column(db.String(255), nullable=False, server_default='')
    time_zone = db.Column(db.DateTime(timezone=False), )
    dst = db.Column(db.Boolean)
    logo_image_name = db.Column(db.Unicode(64))
    logo_image_path = db.Column(db.Unicode(128))
    permission_type = db.Column(mysql.ENUM('a', 'v', 'c'))
    parent = db.Column(db.Integer(), db.ForeignKey('auth_user.id'))
    is_admin = db.Column(db.Boolean)
    is_active = db.Column(db.Boolean, server_default='1')
    date_created  = db.Column(db.DateTime,  default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime,  default=db.func.current_timestamp(),
                              onupdate=db.func.current_timestamp())

    # Relationships
    roles = db.relationship('Role', secondary='user_roles',
                            backref=db.backref('auth_user', lazy='dynamic'))
    contact_group = db.relationship('ContactGroup', secondary='contact_groups',
                                    backref=db.backref('user', lazy='dynamic'))
    plan = db.relationship(Plan, backref=db.backref('user'))

    def __init__(self, first_name, last_name, email, password, phone=None, country=None, company=None,
                 website=None, industry=None, company_size=None, parent=None, is_admin=None,
                 logo_image_name=None):
        self.first_name = first_name
        self.last_name = last_name
        self.username = email
        self.email = email
        self.phone = phone
        self.company = company
        self.company_size = company_size
        self.industry = industry
        self.website = website
        self.country = country
        self.parent = parent
        self.logo_image_name = logo_image_name

        if password:
            self.set_password(password)
        if is_admin:
            self.is_admin = is_admin
        else:
            self.is_admin = False

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.pw_hash, password)
        
    def __repr__(self):
        return '<User %r>' % self.username

    @classmethod
    def email_is_available(self,email):
        if User.query.filter(User.email==email, User.is_active==True).first():
            return False
        return True

    def __json__(self):
        return ['id', 'first_name', 'last_name', 'username', 'email', 'phone', 'company',
                'country', 'website', 'industry', 'company_size', 'time_zone', 'is_admin',
                'is_active', 'date_created', 'date_modified']

    # def simplifed(self):
    #     return {
    #         "username":self.username,
    #         "asdf":self.www
    #     }

class Role(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)


# Define UserRoles model
class UserRoles(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('auth_user.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey('role.id', ondelete='CASCADE'))


class ContactGroup(db.Model):
    __tablename__ = 'contact_group'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(255))
    owner = db.Column(db.Integer(), db.ForeignKey('auth_user.id', ondelete='CASCADE'))


contact_groups = db.Table('contact_groups',
    db.Column('auth_user_id', db.Integer, db.ForeignKey('auth_user.id')),
    db.Column('contact_group_id', db.Integer, db.ForeignKey('contact_group.id'))
)


class PasswordReset(db.Model):
    __tablename__ = 'password_reset_token'
    id = db.Column(db.Integer(), primary_key=True)
    token = db.Column(db.String(255))
    user = db.Column(db.Integer(), db.ForeignKey('auth_user.id'))
    expire = db.Column(db.Boolean, server_default='0')


class Message(db.Model):
    __tablename__ = 'message'

    id = db.Column(db.Integer(), primary_key=True)
    subject = db.Column(db.String(255))
    text = db.Column(db.Text())
    user = db.Column(db.Integer(), db.ForeignKey('auth_user.id'))
    read = db.Column(db.Boolean, server_default='0')
    date_created = db.Column(db.DateTime,  default=db.func.current_timestamp())

    def __json__(self):
        return ['id', 'subject', 'text', 'user', 'read', 'date_created']
