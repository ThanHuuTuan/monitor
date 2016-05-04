import datetime
import uuid

from flask.ext.wtf import Form
from werkzeug.security import generate_password_hash, check_password_hash

# Import Form elements such as TextField and BooleanField (optional)
from wtforms import StringField, TextField, PasswordField, BooleanField

# Import Form validators
from wtforms.validators import *
from wtforms import ValidationError

from flask_jwt import current_identity

from apps import db, app, mail
from models import User, Message, ContactGroup, PasswordReset
from apps.payments.models import Plan


# Define the login form (WTForms)
class LoginForm(Form):
    email    = TextField('Email Address', [Email(),
                Required(message='Forgot your email address?')])
    password = PasswordField('Password', [
                Required(message='Must provide a password. ;-)')])


def unique_email_validator(form, field):
    """ Username must be unique"""
    if not User.email_is_available(field.data):
        raise ValidationError('This Email is already in use. Please try another one.')


def update_email_validator(form, field):
    """ Username must be unique"""
    obj = User.query.filter(User.username==current_identity.username).first()
    if not User.email_is_available(field.data) and not field.data == obj.email:
        raise ValidationError('This Email is already in use. Please try another one.')


def update_sub_account_email_validator(form, field):
    """ Username must be unique"""
    if not User.email_is_available(field.data) and not field.data == form.instance.email:
        raise ValidationError('This Email is already in use. Please try another one.')


def password_validator(form, field):
    if not check_password_hash(current_identity.password, field.data):
        raise ValidationError('Password Incorrect.')


def permission_type_validator(form, field):
    if not field.data in ['a', 'v', 'c']:
        raise ValidationError('Wrong permission type')


def reset_password_email_validator(form, field):
    if User.email_is_available(field.data):
        raise ValidationError('Email is not registered')


def contact_validator(form, field):
    user = User.query.filter(User.id == field.data).first()
    if not user:
        raise ValidationError('Invalid user ID.')
    elif not user.id==current_identity.id and not user.parent==current_identity.id:
        raise ValidationError('Invalid user ID.')


def group_ownership_validator(form, field):
    group = ContactGroup.query.filter(ContactGroup.id == field.data,
                                            ContactGroup.owner == current_identity.id).first()
    if not group:
        raise ValidationError('Invalid group ID.')


def token_validator(form, field):
    user = User.query.filter(User.email==form.email.data).first()
    instance = PasswordReset.query.filter(PasswordReset.user==user.id,
                                          PasswordReset.token==field.data,
                                          PasswordReset.expire==False).first()
    if not instance:
        raise ValidationError('Invalid token.')


def group_validator(form, field):
    groups = ContactGroup.query.filter(ContactGroup.owner == current_identity.id).all()
    group_names = []
    for group in groups:
        group_names.append(group.name)
    if field.data in group_names:
        raise ValidationError('There is already a group with the same name. Specify a different name.')


class RegisterForm(Form):

    first_name = StringField('First Name', validators=[
        DataRequired('First Name is required')])
    last_name = StringField('Last Name', validators=[
        DataRequired('Last Name is required')])
    country = StringField('Country', validators=[
        DataRequired('Country is required')])
    email = StringField('Email', validators=[
        DataRequired('Email is required'),
        Email('Invalid Email'),
        unique_email_validator])
    company = StringField('Company', validators=[
        DataRequired('Company is required')])  
    phone = StringField('Phone', validators=[
        DataRequired('Phone Number is required')])    
    password = PasswordField('Password', validators=[
        DataRequired('Password is required')])

    def save(self,instance=None):
        data = self.data
        user = User(**data)
        db.session.add(user)
        db.session.flush()
        time_now = datetime.date.today()
        expire = time_now + datetime.timedelta(15)
        plan_data = {"plan_level": "free", "plan_period": "15 days",
                     "plan_bought": time_now, "plan_expires": expire, "plan_price": 0,
                     "plan_trial": True,"user_id": user.id}
        plan = Plan(**plan_data)
        db.session.add(plan)
        db.session.commit()
        return User.query.filter_by(id=user.id).first()


class ProfileUpdateForm(Form):

    first_name = StringField('First Name', validators=[
        DataRequired('First Name is required')])
    last_name = StringField('Last Name', validators=[
        DataRequired('Last Name is required')])
    country = StringField('Country', validators=[
        DataRequired('Country is required')])
    email = StringField('Email', validators=[
        DataRequired('Email is required'),
        Email('Invalid Email'), update_email_validator])
    company = StringField('Company', validators=[
        DataRequired('Company is required')])
    phone = StringField('Phone', validators=[
        DataRequired('Phone Number is required')])
    company_size = StringField('Company size')
    industry = StringField('Industry')
    website = StringField('Website')

    def save(self, instance=None):
        data = self.data
        db.session.query(User).filter_by(username=instance.username).update(data)
        db.session.commit()
        return User.query.filter_by(id=instance.id).first()


class CreateSubAccountForm(Form):

    first_name = StringField('First Name', validators=[
        DataRequired('First Name is required')])
    last_name = StringField('Last Name', validators=[
        DataRequired('Last Name is required')])
    email = StringField('Email', validators=[
        DataRequired('Email is required'),
        Email('Invalid Email'), unique_email_validator])
    password = PasswordField('Password', validators=[
        DataRequired('Password is required')])
    retype_password = PasswordField('Retype Password', validators=[
        EqualTo('password', message='Password and Retype Password did not match')])

    def save(self, instance=None):
        data = self.data
        data['parent'] = current_identity.id
        del data['retype_password']
        user = User(**data)
        db.session.add(user)
        db.session.flush()
        db.session.commit()
        return User.query.filter_by(id=user.id).first()


class UpdateSubAccountForm(Form):

    first_name = StringField('First Name', validators=[
        DataRequired('First Name is required')])
    last_name = StringField('Last Name', validators=[
        DataRequired('Last Name is required')])
    email = StringField('Email', validators=[
        DataRequired('Email is required'),
        Email('Invalid Email'), update_sub_account_email_validator])
    password = PasswordField('Password', )
    retype_password = PasswordField('Retype Password', validators=[
        EqualTo('password', message='Password and Retype Password did not match')])

    def __init__(self, *args, **kwargs):
        self.instance = kwargs['instance']
        super(UpdateSubAccountForm, self).__init__(*args, **kwargs)

    def save(self, sub_account_id):
        data = self.data
        data['username'] = data['email']
        del data['retype_password']
        db.session.query(User).filter_by(id=sub_account_id).update(data)
        db.session.commit()
        return User.query.filter_by(id=sub_account_id).first()


def allowed_file(form, fields):
    filename = form.data['logo'].filename
    if '.' in filename and \
           not filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']:
        raise ValidationError('Unsupported file type.')


# Define the Logo image form (WTForms)
class LogoUpdateForm(Form):
    logo = StringField('Logo', validators=[
        DataRequired('Logo image is required'), allowed_file])

    def save(self, instance=None, url=None):
        data = self.data['logo']
        name = data.filename
        db.session.query(User).filter_by(username=instance.username).\
            update({"logo_image_name": name, "logo_image_path": url})
        db.session.commit()


class PasswordChangeForm(Form):
    current_password = StringField('Current Password', validators=[
        DataRequired('Current Password is required'), password_validator])
    password = StringField('Current Password', validators=[
        DataRequired('Password is required')])
    retype_password = PasswordField('Retype Password', validators=[
        EqualTo('password', message='Password and Retype Password did not match')])

    def save(self, instance=None):
        data = self.data
        password_hash = generate_password_hash(data['password'])
        db.session.query(User).filter_by(username=instance.username).\
            update({"password": password_hash})
        db.session.commit()


class ForgotPasswordForm(Form):

    email = StringField('Email', validators=[
        DataRequired('Email is required'),
        Email('Invalid Email'), reset_password_email_validator])

    def send_mail(self, instance=None):
        token = uuid.uuid4().hex
        data = {"token": token, "user": instance.id}
        db.session.add(PasswordReset(**data))
        db.session.commit()
        from flask_mail import Message
        msg = Message("Reset Password", recipients=[instance.email, ])
        msg.body = "Click the following link to reset your password"
        msg.html = "<p>Click <a href='http://127.0.0.1:5000/api/v1/users/password-reset/?email="+instance.email+"&&token="+token+"'>here</a> " \
                   "to reset your password</p>"
        mail.send(msg)


class PasswordResetForm(Form):
    token = StringField('Token', validators=[
        DataRequired('Token is required'), token_validator])
    email = StringField('Email', validators=[
                        DataRequired('Email is required'),
                        Email('Invalid Email')])
    password = StringField('Current Password', validators=[
        DataRequired('Password is required')])
    retype_password = PasswordField('Retype Password', validators=[
        EqualTo('password', message='Password and Retype Password did not match')])

    def save(self, instance=None):
        data = self.data
        password_hash = generate_password_hash(data['password'])
        db.session.query(User).filter_by(email=data["email"]).\
            update({"password": password_hash})
        db.session.query(PasswordReset).filter_by(token=data["token"]).\
            update({"expire": True})
        db.session.commit()


class MessageForm(Form):
    subject = StringField('Subject', validators=[
        DataRequired('Subject is required')])
    text = StringField('Description', validators=[
        DataRequired('Message description is required')])
    user = StringField('User ID', validators=[
        DataRequired('User is required')])

    def save(self):
        data = self.data
        db.session.add(Message(**data))
        db.session.commit()


class UpdateSubAccountPermissionForm(Form):
    permission_type = StringField('Permission Type', validators=[
        DataRequired('Permission type is required'), permission_type_validator])

    def save(self, sub_account_id):
        data = self.data
        db.session.query(User).filter(User.id == sub_account_id).update(data)
        db.session.commit()
        return User.query.filter_by(id=sub_account_id).first()


class CreateContactGroupForm(Form):
    name = StringField('Group Name', validators=[
        DataRequired('Group name is required'), group_validator])

    def save(self):
        data = self.data
        data['owner'] = current_identity.id
        group = ContactGroup(**data)
        db.session.add(group)
        db.session.flush()
        db.session.commit()
        return ContactGroup.query.filter_by(id=group.id).first()


class ContactGroupingForm(Form):
    group = StringField('Group ID', validators=[
        DataRequired('Group is required'), group_ownership_validator])
    contact = StringField('Contact ID', validators=[
        DataRequired('Contact is required'), contact_validator])

    def save(self):
        data = self.data
        user = User.query.filter(User.id == data['contact']).first()
        group = ContactGroup.query.filter(ContactGroup.id == data['group']).first()
        user.contact_group.append(group)
        db.session.commit()
        return ContactGroup.query.filter_by(id=group.id).first()

    def delete(self):
        data = self.data
        user = User.query.filter(User.id == data['contact']).first()
        group = ContactGroup.query.filter(ContactGroup.id == data['group']).first()
        user.contact_group.remove(group)
        db.session.commit()


class ContactGroupRenameForm(Form):

    name = StringField('Group Name', validators=[
        DataRequired('Group name is required'), group_validator])

    def save(self, instance):
        data = self.data
        data['owner'] = current_identity.id
        db.session.query(ContactGroup).filter_by(id=instance.id).update(data)
        db.session.commit()
        return ContactGroup.query.filter_by(id=instance.id).first()
