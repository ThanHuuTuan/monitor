__author__ = 'savad'
import datetime, time
from functools import wraps

from flask_jwt import jwt_required, current_identity
from flask_restful import abort

from models import User


def plan_not_expired():

    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            user = User.query.filter(User.id==current_identity.id).first()
            try:
                plan_expires = user.plan[0].plan_expires
            except:
                parent_user = User.query.filter(User.id==user.parent)
                plan_expires = parent_user.plan[0].plan_expires
            if plan_expires < datetime.date.today():
                abort(406, message="Plan expired")
            return fn(*args, **kwargs)
        return decorator
    return wrapper