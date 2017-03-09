#! /usr/bin/env python
# manage.py

#-------------------------------------------------------------------------------
# imports
#-------------------------------------------------------------------------------
import os
from app import create_app, db
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager, prompt_bool

#-------------------------------------------------------------------------------
# configuration and management
#-------------------------------------------------------------------------------
app = create_app(os.environ.get('APP_CONFIG'))

migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)

@manager.command
def initdb():
    db.create_all()
    db.session.commit()
    print 'Database initialized'

@manager.command
def dropdb():
    if prompt_bool(
        "Are you sure you want to drop the database?"):
        db.drop_all()
        print "Database has been dropped"

if __name__ == '__main__':
    manager.run()
