from __future__ import absolute_import

from flask_jwt import current_identity
from flask_restful import abort
import stripe

from apps import app


STRIPE_KEY = app.config['STRIPE_SECRET_KEY']


# Main functionality
def add_card(cc):
    """
    Adds a card on stripe.

    Parameters:
        cc: CreditCard form data in json

    Returns:
        The customer object created on Stripe for the credit card
    """

    # Set the key
    stripe.api_key = STRIPE_KEY

    customer_data = {
        'email': current_identity.email,
        'description': "Credit card for %s" % current_identity.username,
        'card': {
            'number': cc.get('card_number', None),
            'address_zip': cc.get('zip_code', None),
            'exp_month': cc.get('expiration_month', None),
            'exp_year': cc.get('expiration_year', None),
            'cvc': cc.get('cvv', None),
            'name': cc.get('card_holders_name', None)
        }
    }

    # Get the response and check for errors
    try:
        resp = stripe.Customer.create(**customer_data)
    except stripe.CardError, e:
        if e.code in ('incorrect_number', 'invalid_number'):
            abort(406, message="Invalid card number")
        elif e.code == 'invalid_expiry_month':
            abort(406, message="Invalid expiry date")
        elif e.code == 'invalid_expiry_year':
            abort(406, message="Invalid expiry date")
        else:
            abort(406, message="Invalid verification code")
    except stripe.InvalidRequestError, e:
        if e.param == 'number':
            abort(406, message="Invalid card number")

    active_card = resp.get('sources', None)
    active_card = active_card['data'][0]

    # The card wasn't attached for some reason
    if active_card is None:
        abort(406, message="Problem processing the card")

    # The postcode doesn't match the records
    if active_card.get('address_zip_check', None) == 'fail':
        abort(406, message="Zip code error")

    # The verification code failed
    if active_card.get('cvc_check', None) == 'fail':
        abort(406, message="CVV error")

    # Update the CreditCard with the information received from stripe
    cc['stripe_customer_id'] = resp['id']
    cc['card_type'] = active_card['brand']
    return resp


def update_card(cc):
    """
    Updates the credit card details of user in stripe.

    Parameters:
        exp_month: The Month when the card gets expired 
        exp_year: The Year of card expiring
        cvc: The Card Verification Code of Credit Card

    Returns:
        The saved card details from stripe

    """
    # Set the key
    stripe.api_key = STRIPE_KEY

    try:
        customer = stripe.Customer.retrieve(cc.get('stripe_customer_id', None))
        card_id = customer['sources']['data'][0]['id']
        card = customer.sources.retrieve(card_id)
        card.exp_month = cc.get('expiration_month', None)
        card.exp_year = cc.get('expiration_year', None)
        resp = card.save()
    except stripe.CardError, e:
        if e.code in ('incorrect_number', 'invalid_number'):
            abort(406, message="Invalid card number")
        elif e.code == 'invalid_expiry_month':
            abort(406, message="Invalid expiry date")
        elif e.code == 'invalid_expiry_year':
            abort(406, message="Invalid expiry date")
        else:
            abort(406, message="Problem processing the card")
    except stripe.InvalidRequestError, e:
        if e.param == 'number':
            abort(406, message="Invalid card number")
    return resp
