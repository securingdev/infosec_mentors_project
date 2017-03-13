import os

from app import create_app

application = create_app(os.environ.get('APP_CONFIG'))
if __name__ == "__main__":
    print 'wsgi::__main__'
    application.run()