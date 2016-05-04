from apps import db


class CreditCard(db.Model):
    __tablename__ = 'credit_card'

    id = db.Column(db.Integer, primary_key=True)
    card_holders_name = db.Column(db.String(255))
    card_number = db.Column(db.String(16))
    card_type= db.Column(db.String(25))
    expiration_month = db.Column(db.String(2))
    expiration_year = db.Column(db.String(4))
    billing_company = db.Column(db.String(255))
    billing_address = db.Column(db.String(255))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    zip_code = db.Column(db.String(20))
    country = db.Column(db.String(120))
    stripe_customer_id = db.Column(db.String(120))
    is_active = db.Column(db.Boolean, server_default='1')
    user_id = db.Column(db.Integer(), db.ForeignKey('auth_user.id', ondelete='CASCADE'))


class Plan(db.Model):
    __tablename__ = 'plan'

    id = db.Column(db.Integer, primary_key=True)
    plan_level = db.Column(db.String(20))
    plan_period = db.Column(db.String(20))
    plan_bought= db.Column(db.Date)
    plan_expires = db.Column(db.Date)
    plan_last_change = db.Column(db.DateTime, default=db.func.current_timestamp(),
                                 onupdate=db.func.current_timestamp())
    plan_price = db.Column(db.String(10))
    plan_trial = db.Column(db.Boolean)
    user_id = db.Column(db.Integer(), db.ForeignKey('auth_user.id', ondelete='CASCADE'))
