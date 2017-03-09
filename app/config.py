# project/config.py

import os

# from dotenv import load_dotenv, find_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
# load_dotenv(find_dotenv())


class BaseConfig:
    # Base configuration
    SECRET_KEY = os.environ.get('APP_SECRET_KEY')
    PASSWORD_SALT = os.environ.get('APP_PASSWORD_SALT')
    DEBUG = False
    BCRYPT_LOG_ROUNDS = 13
    WTF_CSRF_ENABLED = True
    DEBUG_TB_ENABLED = False
    DEBUG_TB_INTERCEPT_REDIRECTS = False


    # TODO: Switch Preferred URL Scheme
    # PREFERRED_URL_SCHEME = 'https'
    PREFERRED_URL_SCHEME = 'http'

    # mail settings
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False

    # mail credentials
    MAIL_USERNAME = os.environ.get('APP_MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('APP_MAIL_PASSWORD')

    # mail account(s)
    MAIL_DEFAULT_SENDER = os.environ.get('APP_MAIL_SENDER')

    # redis server
    CELERY_BROKER_URL = 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

    @staticmethod
    def init_app(app):
        pass


class DevConfig(BaseConfig):
    # Development configuration
    DEBUG = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'database.sqlite')
    DEBUG_TB_ENABLED = True


class ProdConfig(BaseConfig):
    # Production configuration
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    SECRET_KEY = os.environ.get('APP_SECRET_KEY')
    DB_NAME = os.environ.get('APP_DB_NAME')
    DB_USER = os.environ.get('APP_DB_USER')
    DB_PASSWORD = os.environ.get('APP_DB_PASSWORD')
    SQLALCHEMY_DATABASE_URI = 'postgresql://' + DB_USER + ':' + DB_PASSWORD + '@localhost/' + DB_NAME
    DEBUG_TB_ENABLED = False
    STRIPE_SECRET_KEY = os.environ.get('APP_STRIPE_SECRET_KEY')
    STRIPE_PUBLISHABLE_KEY = os.environ.get('APP_PUBLISHABLE_KEY')

config_type = {
    'dev': DevConfig,
    'prod': ProdConfig,
    'defalt': DevConfig
}
