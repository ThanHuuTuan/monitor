from flask import Flask
from flask_restful import Api
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand
from flask.ext.cors import CORS
from flask.ext.babel import Babel
from flask_mail import Mail
from flask.ext.pymongo import PyMongo
from celery import Celery

from config import ConfigClass, CeleryConfigClass


app = Flask(__name__)
app.config.from_object(ConfigClass)
CORS(app)
babel = Babel(app)
mail = Mail(app)

app.config['MONGO_HOST'] = 'localhost'
app.config['MONGO_PORT'] = 27017
app.config['MONGO_DBNAME'] = 'monitdb_job'

mongo = PyMongo(app, config_prefix='MONGO')

celery_app = Celery('tasks', broker='amqp://celeryuser:celeryuser@localhost:5672/celeryhost', backend='amqp')
celery_app.config_from_object(CeleryConfigClass)


# Load local_settings.py if file exists
try: app.config.from_object('local_settings')
except: pass

db = SQLAlchemy(app)
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

api = Api(app, app.config['APPLICATION_ROOT'])
from apps.urls import add_resource
add_resource()
