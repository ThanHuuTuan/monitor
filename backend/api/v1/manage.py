# manage.py

from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand

from apps import app, db

migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)

@manager.command
def runserver():
    app.run(host='127.0.0.1', port=5000, debug=True)

@manager.command
def syncdb():
    with app.test_request_context():
        from apps.users.models import User
        db.create_all()

@manager.command
def clean_pyc():
    import os
    os.system('find . -name "*.pyc" -exec rm -rf {} \;')

@manager.command
def create_admin():
    """Creates the admin user."""
    from apps.users.models import User
    try:
        db.session.add(User(
            username='admin',
            email="anoop.ps@sparksupport.com",
            password="admin",
            is_admin=True
        ))
        db.session.commit()
    except Exception as e:
        print "\n",e.message

if __name__ == "__main__":
    manager.run()