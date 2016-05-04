__author__ = 'savad'
from celery.task import task
from bson.objectid import ObjectId

from apps import mongo
from workers import entry
from event_processor import EventProcessor


@task(name="trigger_job")
def trigger_job(job_id):
    job = mongo.db.settings.find_one({"_id": ObjectId(job_id)})
    name, status, settings = get_job_arguments(job)
    entry.delay(name, status, settings)


def get_job_arguments(job):
    try:
        job_status = mongo.db.status.find_one({"job_id": ObjectId(job["_id"])})
    except:
        job_status = mongo.db.status.insert({"job_id": ObjectId(job["_id"])})
    previous_status = job_status.get("status", None)
    status_of_other_regions = job_status.get("status_of_other_regions", None)
    kwargs = job.get("kwargs")
    module_name = kwargs["name"]
    settings = dict()
    settings['url'] = job.get('url')
    settings['regions'] = job.get('regions')
    settings['timeout'] = job.get('timeout')
    settings['time_interval'] = job.get('time_interval')
    settings['previous_status'] = previous_status
    settings['status_of_other_regions'] = status_of_other_regions
    return module_name, previous_status, settings



class ResultAction(object):

    def __init__(self, job_settings, status):
        self.job_id = job_settings["job_id"]
        self.job_settings = job_settings
        self.status_data = status

    def status_update(self):
        if self.job_settings["previous_status"]=="down" and self.status_data["status"] == "up"\
                or self.job_settings["previous_status"]==None:
            return True
        return False

    def reschedule_job(self):
        status_of_others = self.job_settings["status_of_other_regions"]

        pass

    def post_execute(self):
        pass

    def metrics_update(self, job_id, status):
        #update status to cassandra db
        pass

    def delete_job(self, job_id):
        pass

