import os
from app import create_app
from itsdangerous import URLSafeTimedSerializer

app = create_app(os.environ['APP_CONFIG'])

def generate_confirmation_token(email):
    serializer =  URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return serializer.dumps(email, salt = app.config['PASSWORD_SALT'])

def confirm_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    try:
        email = serializer.loads(token, salt = app.config['PASSWORD_SALT'], max_age = expiration)
    except:
        return False
    return email

def confirm_request(token, expiration=172800):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    try:
        email = serializer.loads(token, salt = app.config['PASSWORD_SALT'], max_age = expiration)
    except:
        return False
    return email
