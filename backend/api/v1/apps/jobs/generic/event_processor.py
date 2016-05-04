__author__ = 'savad'
from bson.objectid import ObjectId

from apps import mongo
from alert_processor import AlertProcessor

def ep_entry(report):

    ep = EventProcessor(report)
    if report.status_update:
        ep.update_job_status_to_settings_db()
        ep.update_job_status_to_status_db()


class EventProcessor(object):

    def __init__(self, report):
        self.report = report

    def update_job_status_to_settings_db(self):
        db = mongo.db
        db.settings.update({'_id': ObjectId(self.report.job_id)},
                           {"$set": {"status": self.report.status_data["status"]}})

    def update_job_status_to_status_db(self):
        db = mongo.db
        db.status.insert({"job_id": self.report.job_id, "status": self.report.status_data["status"]})

    def update_status_to_metrics_db(self):
        pass

    def need_to_alert(self):
        AlertProcessor(self.report)

    def reschedule_job(self):
        pass
