import os
from datetime import timedelta


# Use a Class-based config to avoid needing a 2nd file
# os.getenv() enables configuration through OS environment variables
class ConfigClass(object):
    # Flask settings
    SECRET_KEY =               os.getenv('SECRET_KEY',       'awe345frgty5633cfr0nj3m4k4j67')
    SQLALCHEMY_DATABASE_URI =  os.getenv('DATABASE_URL',     'mysql://root:root@localhost/monitdb2')

    MONGO_DBNAME =             'monitdb_job'
    MONGO_HOST =               'localhost'
    MONGO_PORT =                27017

    BASE_DIR =                 os.path.dirname(os.path.dirname(__file__))
    DEFAULT_FILE_STORAGE =     'filesystem'
    UPLOAD_FOLDER =            BASE_DIR + '/../static/'
    STATIC_FOLDER =            '/static/'
    FILE_SYSTEM_STORAGE_FILE_VIEW = 'static'
    ALLOWED_EXTENSIONS =       set(['png', 'jpg', 'JPG', 'jpeg', 'gif'])

    WTF_CSRF_ENABLED =         False
    CSRF_ENABLED =             False
    JWT_EXPIRATION_DELTA =     timedelta(seconds=2592000)
    JWT_AUTH_URL_RULE =        '/api/v1/user/login/'

    # Mail settings
    MAIL_USERNAME =            'noreplayspark@gmail.com'
    MAIL_PASSWORD =            'sparknoreplay'
    EMAIL_DEFAULT =            os.getenv('EMAIL_DEFAULT',  '"Test App" <noreplayspark@gmail.com>')
    MAIL_SERVER =              'smtp.gmail.com'
    MAIL_PORT =                465
    MAIL_USE_SSL =             True
    MAIL_DEFAULT_SENDER =      'noreplayspark@gmail.com'

    APPLICATION_ROOT =         os.getenv('APPLICATION_ROOT',       '/api/v1')

    #Stripe keys
    STRIPE_SECRET_KEY = 'sk_test_FHZwbJwuXSCuASsuYtCyQ0Kw'
    STRIPE_PUBLIC_KEY = 'pk_test_pOkBB1qEq5pfb2gmN3XyVn1y'


class CeleryConfigClass(object):
    CELERY_MONGODB_SCHEDULER_DB = "monitdb_job"
    CELERY_MONGODB_SCHEDULER_COLLECTION = "schedules"
    CELERY_MONGODB_SCHEDULER_URL = "mongodb://celeryuser:123456@localhost:27017"

    CELERY_TIMEZONE = 'UTC'