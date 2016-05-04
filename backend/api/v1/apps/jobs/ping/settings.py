__author__ = 'savad'
from flask.ext.wtf import Form
from wtforms.fields.html5 import URLField
from wtforms import StringField, IntegerField
from wtforms.validators import *
from wtforms import ValidationError

from apps import mongo


class PingSettings(Form):
    url = URLField('URL', validators=[DataRequired(), url()])
    timeout = IntegerField('timeout', validators=[DataRequired()])
    regions = StringField('timeout', validators=[DataRequired()])
    time_interval = IntegerField('timeout', validators=[DataRequired()])

    def save(self, instance=None):
        data = self.data
        data['kwargs'] = {"name": "ping"}
        data['crontab'] = {"minute": data["time_interval"], "hour": "*", "days_of_week": "*", "days_of_month": "*", "month_of_year": "*"}
        db = mongo.db
        # db.settings.insert(data)
        # schedule_data = {"_cls": "PeriodicTask", "name": "ping", "task": "trigger_job",
        #                  "queue": "AU-queue", "enabled": "true",
        #                  "interval": { "every": 30, "period": "seconds" },
        #                  "args": [data["_id"]] }
        # db.schedules.insert(schedule_data)

    def get_settings(self):
        return {"url": str(self.url), "timeout": str(self.timeout),
                "time_interval": str(self.time_interval), "regions": str(self.regions)}
