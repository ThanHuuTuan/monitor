__author__ = 'savad'
import imp, importlib
from celery import Celery
from celery.task import task

class CeleryConfigClass(object):
    CELERY_MONGODB_SCHEDULER_DB = "monitdb_job"
    CELERY_MONGODB_SCHEDULER_COLLECTION = "schedules"
    CELERY_MONGODB_SCHEDULER_URL = "mongodb://monituser:123456@localhost:27017"
    CELERY_TIMEZONE = 'UTC'
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_ACCEPT_CONTENT = ['json']
    CELERY_RESULT_SERIALIZER = 'json'
    # CELERY_IMPORTS = "apps.jobs.generic.workers.entry"

celery_app = Celery('workers', broker='amqp://monituser:123456@localhost:5672/myvhost', backend='amqp')
celery_app.config_from_object(CeleryConfigClass)

@task(name="entry")
def entry(module_name, status, settings):
    print "entryyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy"
    if not module_is_exist(module_name):
        print "jjjjjjj"
        return module_not_exist()
    print "hhhhhh"
    module = load_module(module_name)
    return module.execute(settings)


def module_is_exist(name):
    try:
        imp.find_module(name)
        print "haiiiiiiiiiiiiiiiiiii", name
        return True
    except ImportError:
        print "errrrrrrrrrrrrrrrrrrrr", name
        return False

def module_not_exist():
    return ""

def load_module(name):
    return imp.load_module(name)



