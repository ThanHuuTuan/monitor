import datetime

from flask.ext.wtf import Form
from flask_jwt import current_identity

# Import Form elements such as TextField and BooleanField (optional)
from wtforms import StringField, BooleanField

# Import Form validators
from wtforms.validators import *
from wtforms import ValidationError

from apps import db, app
from models import CreditCard, Plan
from apps.payments.stripe import add_card, update_card


class CreditCardForm(Form):

    card_holders_name = StringField('Card Holders Name', validators=[
        DataRequired('Card holders name is required')])
    card_number = StringField('Card Number', validators=[
        DataRequired('Card number is required')])
    cvv = StringField('CVV', validators=[
        DataRequired('CVV is required')])
    expiration_month = StringField('Expiration Month', validators=[
        DataRequired('Expiration Month is required')])
    expiration_year = StringField('Expiration Year', validators=[
        DataRequired('Expiration year is required')])
    billing_company = StringField('Billing Company', validators=[
        DataRequired('Billing company is required')])
    billing_address = StringField('Billing Address', validators=[
        DataRequired('Billing address is required')])
    city = StringField('City', validators=[
        DataRequired('City is required')])
    state = StringField('State', validators=[
        DataRequired('State is required')])
    country = StringField('Country', validators=[
        DataRequired('Country is required')])
    zip_code = StringField('Pin', validators=[
        DataRequired('Pin is required')])

    def save(self, instance=None):
        data = self.data
        data['user_id'] = instance.id
        credit_card = CreditCard.query.filter(CreditCard.user_id==instance.id,
                                              CreditCard.is_active==True).first()
        if credit_card:
            data['stripe_customer_id'] = credit_card.stripe_customer_id
            update_card(data)
            del data['cvv']
            db.session.query(CreditCard).filter(CreditCard.user_id==instance.id,
                                                CreditCard.is_active==True).update(data)
        else:
            add_card(data)
            del data['cvv']
            credit_card = CreditCard(**data)
            db.session.add(credit_card)
            db.session.flush()
        db.session.commit()
        return CreditCard.query.filter(CreditCard.id==credit_card.id).first()


def date_validator(form, field):
    try:
        date = datetime.datetime.strptime(field.data, '%Y-%m-%d')
    except ValueError:
        date = False
    if not date:
        raise ValidationError('Wrong date. Please enter yyyy-mm-dd format')


class UpdatePlanDetailsForm(Form):

    plan_level = StringField('Plan Level', validators=[
        DataRequired('Plan level is required')])
    plan_period = StringField('Plan Period', validators=[
        DataRequired('Plan period is required')])
    plan_bought = StringField('Plan Bought', validators=[
        DataRequired('Plan bought is required'), date_validator])
    plan_expires = StringField('Plan Expire', validators=[
        DataRequired('Plan expire is required'), date_validator])
    plan_price = StringField('Plan Price', validators=[
        DataRequired('Plan price is required')])
    plan_trial = StringField('Plan Trial', validators=[
        DataRequired('Plan trail is required')])

    def save(self, instance):
        data = self.data
        data['user_id'] = current_identity.id
        db.session.query(Plan).filter_by(id=instance.id).update(data)
        db.session.commit()
