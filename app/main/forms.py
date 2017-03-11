from flask_wtf import FlaskForm
from wtforms.fields import StringField, SelectField, SubmitField, PasswordField, BooleanField
from wtforms.validators import Email, DataRequired, NoneOf, Optional, Regexp, Length, EqualTo, ValidationError

# from app.main.ismp import experiences, contact_preferences, timezone, skills, availability, timeframe
from app.models import User


# ------------------------------------------------------------------------------
# Lists for Field Selections
# ------------------------------------------------------------------------------

experiences = [('blank', ''),
               ('College Student','College Student'),
               ('Recent Graduate','Recent Graduate'),
               ('Security Hobbyist', 'Security Hobbyist'),
               ('Non-Technical Professional', 'Non-Technical Professional'),
               ('Technical Professional', 'Technical Professional'),
               ('Security Professional', 'Security Professional'),
               ('Security Manager', 'Security Manager'),
               ('Security Executive', 'Security Executive')]

contact_preferences = [('blank',''),
                      ('Email', 'Email'),
                      ('Facetime', 'Facetime'),
                      ('Hangouts', 'Hangouts'),
                      ('Phone', 'Phone'),
                      ('Signal', 'Signal'),
                      ('Skype', 'Skype'),
                      ('Slack', 'Slack') ]

timezone = [('blank', ''),
            ('EST', 'Eastern Time (UTC -5:00)'),
            ('CST', 'Central Time (UTC -6:00)'),
            ('MST', 'Mountain Time (UTC -7:00)'),
            ('PST', 'Pacific Time (UTC -8:00)'),
            ('AKST', 'Alaskan Time (UTC -9:00)'),
            ('HST', 'Hawaiian Time (UTC -10:00)'),
            ('GMT', 'Greenwhich (UTC +00:00)'),
            ('CET', 'Centraul Europe (UTC +01:00)')]

skills = [ ('blank', ''),
          ('Business Enablement', 'Business Enablement').
          ('Career Development', 'Career Development'),
          ('Incident Response', 'Incident Response'),
          ('Intrusion Detection', 'Intrusion Detection'),
          ('Malware Analysis', 'Malware Analysis'),
          ('Network Security', 'Network Security'),
          ('Packet Analysis', 'Packet Analysis'),
          ('Penetration Testing', 'Penetration Testing')
          ('Program Management', 'Program Management'),
          ('Project Management', 'Project Management'),
          ('Reverse Engineering', 'Reverse Engineering'),
          ('Risk Management', 'Risk Management'),
          ('Security Competitions', 'Security Competitions'),
          ('Security Engineering', 'Security Engineering'),
          ('Security Research', 'Security Research'),
          ('Security Strategy', 'Security Strategy'),
          ('Social Engineering', 'Social Engineering'),
          ('Social Networking', 'Social Networking'),
          ('Software Development', 'Software Development'),
          ('Speaking at Conferences', 'Speaking at Conferences'),
          ('Team Management', 'Team Management'),
          ('Threat Intelligence', 'Threat Intelligence'),
          ('Training', 'Training'),
          ('Volunteering', 'Volunteering'),
          ('Web Application Security', 'Web Application Security'),
          ('Wireless Security', 'Wireless Security')]

availability = [ ('1','1'),
                 ('2','2'),
                 ('3','3'),
                 ('4','4'),
                 ('5','5'),
                 ('6','6'),
                 ('7','7'),
                 ('8','8')]

timeframe = [('week','week'),
             ('month','month')]

# ------------------------------------------------------------------------------
# UserPreferences
# ------------------------------------------------------------------------------
class UserPreferences(FlaskForm):
    gravatar = StringField('',
                            validators=[Optional(strip_whitespace=True),
                                        Regexp('^[A-Za-z0-9\_\@\.]{1,128}$', message="Invalid Gravatar email handle")])

    alias = StringField('Name (*):',
                        validators=[ Regexp('^[A-Za-z0-9](?!.*(\.){2,}.*)[A-Za-z0-9\s\.]{1,32}$', message="Please try a different alias"),
                                     DataRequired('You must provide a public Name or Alias')])

    timezone = SelectField('Time Zone (*):', choices=timezone,
                           validators=[NoneOf('blank', 'Please make a selection'),
                                       Regexp('^[A-Za-z0-9\s\(\-\:\)]{1,32}$')])

    public_email = StringField('Public Email:', validators=[Optional(strip_whitespace=True),
                                                            Email(message="Invalid email address")])

    twitter = StringField('https://www.twitter.com/', validators=[Optional(strip_whitespace=True),
                                                         Regexp('^[A-Za-z0-9\_]{1,32}$', message="Invalid Twitter handle")])

    github = StringField('https://www.github.com/', validators=[Optional(strip_whitespace=True),
                                                       Regexp('^[A-Za-z0-9](?!.*(\-){2,}.*)[A-Za-z0-9\-]{1,32}$',
                                                              message="Please try a different alias")])

    experience = SelectField('I am a:', choices=experiences, validators=[NoneOf('blank','Please make a selection'),
                                                                         Regexp('^[A-Za-z\-\s]{1,32}$')])

    mentoring_experience = SelectField('I am comfortable mentoring a:', choices=experiences,
                                                  validators=[NoneOf('blank','Please make a selection'),
                                                              Regexp('^[A-Za-z\-\s]{1,32}$')])

    mentored_experience = SelectField('I would like to be mentored by a:', choices=experiences,
                                       validators=[NoneOf('blank','Please make a selection'),
                                                   Regexp('^[A-Za-z\-\s]{1,32}$')])

    contact_preference = SelectField('I would prefer to meet via:', choices=contact_preferences,
                                     validators=[NoneOf('blank','Please make a selection'),
                                                 Regexp('^[A-Za-z]{1,16}$')])

    mentoring_skill_0 = SelectField('', choices=skills, validators=[NoneOf('blank','Please make a selection'),
                                                                    Regexp('^[A-Za-z\s]{1,64}$')])

    mentoring_skill_1 = SelectField('', choices=skills, validators=[NoneOf('blank','Please make a selection'),
                                                                    Regexp('^[A-Za-z\s]{1,64}$')])

    mentoring_skill_2 = SelectField('', choices=skills, validators=[NoneOf('blank','Please make a selection'),
                                                                    Regexp('^[A-Za-z\s]{1,64}$')])

    mentored_skill_0 = SelectField('', choices=skills, validators=[NoneOf('blank','Please make a selection'),
                                                                    Regexp('^[A-Za-z\s]{1,64}$')])

    mentored_skill_1 = SelectField('', choices=skills, validators=[NoneOf('blank','Please make a selection'),
                                                                    Regexp('^[A-Za-z\s]{1,64}$')])

    mentored_skill_2 = SelectField('', choices=skills, validators=[NoneOf('blank','Please make a selection'),
                                                                    Regexp('^[A-Za-z\s]{1,64}$')])

    mentoring_hours= SelectField('I am available to Mentor others for approximately:', choices=availability,
                                  validators=[Regexp('^[1-8]{1,1}$')])

    mentoring_timeframe = SelectField('hour(s) per', choices=timeframe, validators=[Regexp('^[A-Za-z]{1,5}$')])

    mentored_hours = SelectField('I would like to receive mentorship for approximately:', choices=availability,
                                 validators=[Regexp('^[1-8]{1,1}$')])

    mentored_timeframe = SelectField('hour(s) per', choices=timeframe, validators=[Regexp('^[A-Za-z]{1,5}$')])

    submit = SubmitField()

# ------------------------------------------------------------------------------
# RegisterForm
# ------------------------------------------------------------------------------
class RegisterForm(FlaskForm):
    email_address = StringField('Email Address:', validators=[DataRequired(), Email()])
    password = PasswordField('Password:', validators=[DataRequired(),
                                                      Length(8,64),
                                                      EqualTo('repeated_password', message='Passwords must match')])
    repeated_password = PasswordField('Confirm Password:', validators=[DataRequired()])

    submit = SubmitField('Register')

    def validate_email(self, email):
        if User.query.filter_by(email=email.data).first():
            raise ValidationError('Please check your email for confirmation')

# ------------------------------------------------------------------------------
# LoginForm
# ------------------------------------------------------------------------------
class LoginForm(FlaskForm):
    email_address = StringField('Email Address:', validators=[DataRequired(),
                                                              Email(message="Email Address is Invalid")])
    password = PasswordField('Password:', validators=[DataRequired()])
    set_cookie = BooleanField('Remember Me')
    submit = SubmitField('Log In')


# ------------------------------------------------------------------------------
# ResetForm
# ------------------------------------------------------------------------------
class ResetForm(FlaskForm):
    email_address = StringField('Email Address:', validators =[DataRequired(), Email()])
    submit = SubmitField('Forgot Password')

# ------------------------------------------------------------------------------
# ResetForm
# ------------------------------------------------------------------------------
class PasswordForm(FlaskForm):
    password = PasswordField('Password:', validators=[DataRequired(),
                                                      Length(8,64),
                                                      EqualTo('repeated_password', message='Passwords must match')])
    repeated_password = PasswordField('Confirm Password:', validators=[DataRequired()])
    submit = SubmitField('Reset Password')
