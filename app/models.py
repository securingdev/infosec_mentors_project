from app import db, bcrypt
from flask_login import UserMixin

# -------------------------------------------------------------------------------
# User
#
# Handles Login and Email Validation information
# -------------------------------------------------------------------------------
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    confirmed = db.Column(db.Boolean, default=False)
    last_login = db.Column(db.DateTime, nullable = True)
    email = db.Column(db.String(128), unique = True, nullable = False)
    password_hash = db.Column(db.String, nullable = False)
    registered_on = db.Column(db.DateTime, nullable = True)
    confirmed_on = db.Column(db.DateTime, nullable = True)
    preferences = db.relationship('Profile', backref='user', lazy='dynamic')

    @property
    def password(self):
        raise AttributeError('password: write-only field')

    @password.setter
    def password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password)

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    @staticmethod
    def get_by_username(email):
        return User.query.filter_by(email=email).first()

    def __repr__(self):
        return "<User '{}'>".format(self.username)

# -------------------------------------------------------------------------------
# Profile
#
# Holds all data to display when browsing for a mentor
# -------------------------------------------------------------------------------
class Profile(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    credentials_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)
    available = db.Column(db.Integer, nullable = True)
    gravatar = db.Column(db.String(128), nullable = True)
    alias = db.Column(db.String(64), nullable = False)
    timezone = db.Column(db.String(32), nullable = False)
    public_email = db.Column(db.Text, nullable = True)
    twitter = db.Column(db.Text, nullable = True)
    github = db.Column(db.Text, nullable = True)
    biography = db.Column(db.String(140), nullable = True)

    experience = db.Column(db.String(64), nullable = False)
    mentoring_experience = db.Column(db.String(64), nullable = False)
    mentored_experience = db.Column(db.String(64), nullable = False)
    contact_preference = db.Column(db.Text, nullable = False)

    mentoring_skill_0 = db.Column(db.String(64), nullable = False)
    mentoring_skill_1 = db.Column(db.String(64), nullable = False)
    mentoring_skill_2 = db.Column(db.String(64), nullable = False)
    mentoring_hours = db.Column(db.String(1), nullable = False)
    mentoring_timeframe = db.Column(db.String(5), nullable = False)

    mentored_skill_0 = db.Column(db.String(64), nullable = False)
    mentored_skill_1 = db.Column(db.String(64), nullable = False)
    mentored_skill_2 = db.Column(db.String(64), nullable = False)
    mentored_hours = db.Column(db.String(1), nullable = False)
    mentored_timeframe = db.Column(db.String(5), nullable = False)

# -------------------------------------------------------------------------------
# Mentor
#
# Holds all data associated with Mentorship pairs
# -------------------------------------------------------------------------------
class Mentor(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.Text, nullable = True)
    mentee = db.Column(db.Integer, nullable = True)
    mentee_email = db.Column(db.Text, nullable = True)
    requested_on = db.Column(db.DateTime, nullable = True)
    accepted_on = db.Column(db.DateTime, nullable = True)
    completed_on = db.Column(db.DateTime, nullable = True)

# -------------------------------------------------------------------------------
# Suggestion
#
# Holds all id numbers for suggested Mentors based on matching algorithm
# -------------------------------------------------------------------------------
class Suggestion(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    mentor_0 = db.Column(db.Integer, nullable = True)
    mentor_1 = db.Column(db.Integer, nullable = True)
    mentor_2 = db.Column(db.Integer, nullable = True)
    mentor_3 = db.Column(db.Integer, nullable = True)
    mentor_4 = db.Column(db.Integer, nullable = True)
    mentor_5 = db.Column(db.Integer, nullable = True)
    mentor_6 = db.Column(db.Integer, nullable = True)
    mentor_7 = db.Column(db.Integer, nullable = True)
    mentor_8 = db.Column(db.Integer, nullable = True)
    mentor_9 = db.Column(db.Integer, nullable = True)

# -------------------------------------------------------------------------------
# UserMetrics
#
# Holds all usage data for individual users
# -------------------------------------------------------------------------------
class UserMetrics(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    last_login = db.Column(db.DateTime, nullable = True)
    login_count = db.Column(db.Integer, nullable = True)
    mentorship_accepted_count = db.Column(db.Integer, nullable = True)
    mentorship_declined_count = db.Column(db.Integer, nullable = True)
    avg_mentorship_duration = db.Column(db.Integer, nullable = True)
    mentor_rating = db.Column(db.Float, nullable = True)
    apprenticeship_requested_count = db.Column(db.Integer, nullable = True)
    avg_apprenticeship_duration = db.Column(db.Integer, nullable = True)
    apprentice_rating = db.Column(db.Float, nullable = True)

# -------------------------------------------------------------------------------
# SiteMetrics
#
# Holds all usage data for the site in aggregate
# -------------------------------------------------------------------------------
class SiteMetrics(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    num_registered = db.Column(db.Integer, nullable = True)
    num_users_with_public_email = db.Column(db.Integer, nullable = True)
    num_users_with_twitter = db.Column(db.Integer, nullable = True)
    num_users_with_github = db.Column(db.Integer, nullable = True)
    most_preferred_contact_method = db.Column(db.String(64), nullable = True)
    num1_mentored_skill = db.Column(db.String(128), nullable = True)
    num2_mentored_skill = db.Column(db.String(128), nullable = True)
    num3_mentored_skill = db.Column(db.String(128), nullable = True)
    num1_apprenticed_skill = db.Column(db.String(128), nullable = True)
    num2_apprenticed_skill = db.Column(db.String(128), nullable = True)
    num3_apprenticed_skill = db.Column(db.String(128), nullable = True)
    avg_mentorship_duration = db.Column(db.Float, nullable = True)
    avg_mentorship_availability = db.Column(db.Float, nullable = True)
    avg_apprenticeship_availability = db.Column(db.Float, nullable = True)
