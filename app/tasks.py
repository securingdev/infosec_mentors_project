# project/email.py

import os
from threading import Thread
from flask_mail import Message
from app import create_app, mail, celery

app = create_app(os.environ['APP_CONFIG'])

@celery.task
def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

# @celery.task
def send_email( app, to, subject, template ):
    msg = Message( subject,
                   recipients=[to],
                   html=template,
                   sender=app.config['MAIL_DEFAULT_SENDER'])
    # with app.app_context():
    #     mail.send(msg)
    thr = Thread( target = send_async_email, args = [app, msg])
    thr.start()
