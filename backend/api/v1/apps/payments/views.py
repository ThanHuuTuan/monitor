__author__ = 'savad'

from flask_restful import Resource, request
from flask_jwt import jwt_required, current_identity
from werkzeug.datastructures import ImmutableMultiDict

from models import Plan
from forms import UpdatePlanDetailsForm


class UpdatePlanDetailsView(Resource):
    method_decorators = [jwt_required()]

    def put(self):
        data = ImmutableMultiDict(request.json)
        update_plan_form = UpdatePlanDetailsForm(data, csrf_enabled=False)
        if update_plan_form.validate():
            instance = Plan.query.filter(Plan.user_id==current_identity.id).first()
            update_plan_form.save(instance)
            return {"status": "success"}
        return update_plan_form.errors
