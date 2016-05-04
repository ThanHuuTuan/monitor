__author__ = 'savad'
import imp
import importlib

from flask import jsonify
from flask_jwt import JWT
from flask_restful import Resource, request, abort
from flask_jwt import jwt_required, current_identity
from werkzeug.datastructures import ImmutableMultiDict

from apps.jobs.generic.job_manager import trigger_job


class JobSettingsView(Resource):

    def get(self, job_name):
        module = load_module(job_name)
        settings = module.ModuleSettings()
        return jsonify({"status": "success", "data": settings.get_settings()})

    def post(self, job_name):
        module = load_module(job_name)
        data = ImmutableMultiDict(request.json)
        settings = module.ModuleSettings(data, csrf_enabled=False)
        if settings.validate():
            settings.save()
            trigger_job('56681bc19eb52a2040ff7362')
            return jsonify({"status": "success"})
        return settings.errors


def load_module(name):
    try:
        module = importlib.import_module("apps.jobs."+name)
    except:
        abort(404, message="Job {} doesn't exist".format(name))
    return module
