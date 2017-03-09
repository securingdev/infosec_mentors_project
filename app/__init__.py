# ------------------------------------------------------------------------------
# imports
# ------------------------------------------------------------------------------
import os

from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy

from celery import Celery

from config import config_type

# ------------------------------------------------------------------------------
# initialize flask add-on instances
# ------------------------------------------------------------------------------
mail = Mail()
bcrypt = Bcrypt()
celery = Celery()
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.session_protection = "strong"
login_manager.login_view = "main.login"

# ------------------------------------------------------------------------------
# app factory
# ------------------------------------------------------------------------------
def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config_type[config_name])
    config_type[config_name].init_app(app)

    celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)

    db.init_app(app)
    mail.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
