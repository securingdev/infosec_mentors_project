import datetime, hashlib, os, random, re

from flask import render_template, url_for, flash, redirect, request
from flask_login import login_required, login_user, logout_user, current_user
from sqlalchemy import or_, text
from threading import Thread

from . import main
from . forms import UserPreferences, LoginForm, RegisterForm, ResetForm, PasswordForm
from app import create_app, login_manager
from .. import db
from ..tasks import send_email
from ..token import generate_confirmation_token, confirm_token, confirm_request
from ..models import Profile, User, Mentor, Suggestion, UserMetrics, SiteMetrics

app = create_app(os.environ['APP_CONFIG'])

# ##############################################################################
# Helper Functions
# ##############################################################################

# ------------------------------------------------------------------------------
# Login Manager
#
# Helper function for tracking user activity
# ------------------------------------------------------------------------------
@login_manager.user_loader
def load_user(userid):
    return User.query.get(int(userid))

# ------------------------------------------------------------------------------
# md5 Calculator
#
# Helper function used to convert the Gravatar email address to an md5 value
# ------------------------------------------------------------------------------
def md5calc(val):
    str_val = str(val)
    str_val = str_val.lower()
    md5_val = hashlib.md5(str_val).hexdigest()
    return md5_val

# ------------------------------------------------------------------------------
# is relative
#
# Helper function used to check if a "next" link for login is relative
# ------------------------------------------------------------------------------
def is_relative(url):
    return re.match(r"^\/[^\/\\]", url)

# ------------------------------------------------------------------------------
# suggest
#
# Helper function to return a profile id for a suggested mentor
# ------------------------------------------------------------------------------
def suggest(profile):

    # Filter out profiles by skills that match User's desired skills -----------

    # TODO: Change over the mentor_profile filter when the site grows
    # mentor_profile = Profile.query.filter_by( available = '1', experience = profile.mentored_experience )
    mentor_profile = Profile.query.filter_by(available = '1')

    skill_0 = profile.mentored_skill_0
    skill_1 = profile.mentored_skill_1
    skill_2 = profile.mentored_skill_2

    match_0 = mentor_profile.filter(or_( Profile.mentoring_skill_0 == skill_0,
                                         Profile.mentoring_skill_1 == skill_0,
                                         Profile.mentoring_skill_2 == skill_0)).all()

    match_1 = mentor_profile.filter(or_( Profile.mentoring_skill_0 == skill_1,
                                         Profile.mentoring_skill_1 == skill_1,
                                         Profile.mentoring_skill_2 == skill_1)).all()

    match_2 = mentor_profile.filter(or_( Profile.mentoring_skill_0 == skill_2,
                                         Profile.mentoring_skill_1 == skill_2,
                                         Profile.mentoring_skill_2 == skill_2)).all()

    # Create sets for performing logical ANDs to get matched skills ------------
    try:
        setZero = set(match_0)
    except:
        setZero = None

    try:
        setOne = set(match_1)
    except:
        setOne = None

    try:
        setTwo = set(match_2)
    except:
        setTwo = None

    # Perform logical operations and return a match ----------------------------
    if setZero is not None and setOne is not None and setTwo is not None:
        perfect_match = ( setZero & setOne & setTwo )
        if perfect_match != set():
            perfect = random.sample( perfect_match, 1)
            return perfect[0].id

    if setZero is not None and setOne is not None:
        two_match = ( setZero & setOne )
        if two_match != set():
            two = random.sample( two_match, 1)
            return two[0].id

    if setZero is not None and setTwo is not None:
        two_match = ( setZero & setTwo )
        if two_match != set():
            two = random.sample( two_match, 1)
            return two[0].id

    if setOne is not None and setTwo is not None:
        two_match = ( setOne & setTwo )
        if two_match != set():
            two = random.sample( two_match, 1)
            return two[0].id

    if setZero is not None:
        one = random.sample(setZero, 1)
        return one[0].id

    if setOne is not None:
        one = random.sample(setOne, 1)
        return one[0].id

    if setTwo is not None:
        one = random.sample(setTwo, 1)
        return one[0].id

    # If there are no matches, stay on current profile -------------------------
    return profile.id


# ##############################################################################
# View Functions
# ##############################################################################


# ------------------------------------------------------------------------------
# Index
# ------------------------------------------------------------------------------
@main.route('/')
@main.route('/index')
def index():
    # TODO: Prolematic if Profile 1 is deleted
    user = Profile.query.filter_by(id = 1).first()
    if user:
        return redirect(url_for('main.about'))
    # Only used at launch when the database has no users or profiles -----------
    else:
        return redirect(url_for('main.register'), code = 302, Response = None)


# ------------------------------------------------------------------------------
# About
# ------------------------------------------------------------------------------
@main.route('/about')
def about():
    return render_template('about.html')

# ------------------------------------------------------------------------------
# Terms of Service
# ------------------------------------------------------------------------------
@main.route('/tos')
def tos():
    return render_template('tos.html')


# ------------------------------------------------------------------------------
# Register
# ------------------------------------------------------------------------------
@main.route('/register', methods = ['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():

        user_email = form.email_address.data
        user_email = user_email.lower()
        new_user = User.query.filter_by(email = user_email).first()

        if new_user is not None:
            token = generate_confirmation_token(new_user.email)
            confirm_url = url_for('main.confirm_reset', token = token, _external = True)
            html = render_template('reset_request.html', confirm_url = confirm_url)
            subject = 'InfoSec Mentors Project - Password Reset'
            send_email(app, new_user.email, subject, html)
            return render_template('waiting.html')

        # Add the user to the User table, instantiate other columns --------
        user = User(email = user_email,
                    password = form.password.data,
                    registered_on = datetime.datetime.now(),
                    confirmed = False)
        mentor = Mentor(email = user_email)
        suggested = Suggestion()
        userMetrics = UserMetrics()

        # Use a single row for the SiteMetrics table -----------------------
        siteMetrics = db.session.query(SiteMetrics.id).filter_by(id = 1).scalar()
        if siteMetrics is None:
            siteMetrics = SiteMetrics()
            db.session.add(siteMetrics)

        db.session.add(user)
        db.session.add(mentor)
        db.session.add(suggested)
        db.session.add(userMetrics)
        db.session.commit()

        # Generate the confirmation token, validate email ------------------
        token = generate_confirmation_token(user.email)
        confirm_url = url_for('main.confirm_email', token = token, _external = True)
        html = render_template('activate.html', confirm_url = confirm_url)
        subject = "InfoSec Mentors Project - Email Confirmation"
        send_email(app, user.email, subject, html)
        return render_template('waiting.html')

    # Bad Registration Code attempted --------------------------------------
    return render_template("register.html", form = form)

# ------------------------------------------------------------------------------
# Email Validation
# ------------------------------------------------------------------------------
@main.route('/confirm/<token>')
def confirm_email(token):
    try:
        email = confirm_token(token)
    except:
        flash('The confirmation link is invalid or has expired.', 'danger')
        return redirect(url_for('main.index'))

    # If the registration code is valid and unused, modify User table ----------
    user = User.query.filter_by(email = email).first()
    siteMetrics = SiteMetrics.query.filter_by(id = 1).first()
    if user.confirmed:
        flash('Account is already confirmed. Please login.', 'success')
        return redirect(url_for('main.login'))
    elif user:
        user.confirmed = True
        user.confirmed_on = datetime.datetime.now()
        siteMetrics.num_registered = user.id
        db.session.add(user)
        db.session.add(siteMetrics)
        db.session.commit()
        flash('Your account has been confirmed.', 'succes')
        return redirect(url_for('main.login'))
    # If invalid input is provided, go back to the index page ------------------
    else:
        return redirect(url_for('main.index'))


# ------------------------------------------------------------------------------
# Unconfirmed Email
# ------------------------------------------------------------------------------
@main.route('/unconfirmed')
@login_required
def unconfirmed():
    if current_user.confirmed:
        return redirect(url_for('main.user_profile'))
    else:
        return render_template('waiting.html')


# ------------------------------------------------------------------------------
# Login
# ------------------------------------------------------------------------------
@main.route("/login", methods = ['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST':
        if request.form['submit'] == 'Submit':
            if form.validate_on_submit():

                user_email = form.email_address.data
                user_email = user_email.lower()

                # Check if the user exists, proceed if exists ------------------
                dummy = User.query.filter_by(id = 1).first()
                user = User.query.filter_by(email = user_email).first()
                password = 'P@$5W0RD1'
                date = ''
                if user is not None:
                    if user.last_login is not None:
                        date = str(user.last_login.isoformat(' '))
                    else:
                        date = str(datetime.datetime.now())

                # Check for locked account and banned user ---------------------
                if user is not None and ( (date == '1970-01-01 00:13:37') or
                                          (date == '1970-01-01 00:04:55')):
                    dummy.check_password(password)
                elif user is not None and user.check_password(form.password.data):
                    profile = Profile.query.filter_by(credentials_id = user.id).first()
                    user.last_login = datetime.datetime.now()
                    db.session.commit()

                    # If the user has a profile setup --------------------------
                    if profile is not None:
                        login_user(user, form.set_cookie.data)
                        flash('Login Successful as {}'.format(user.email))
                        if request.args.get('next') is not None:
                            next_url = request.args.get('next')
                            relative = is_relative(next_url)
                            if relative is not None:
                                return redirect(request.args.get('next') or url_for('main.user_profile', id = user.id))
                            else:
                                return redirect(url_for('main.index'))
                        else:
                            #TODO: Problematic if Profile 1 is deleted
                            return redirect(url_for('main.user_profile', id = 1))
                    # Force the user to complete their profile -----------------
                    else:
                        login_user(user, form.set_cookie.data)
                        flash('Login Successful as {}'.format(user.email))
                        return redirect(url_for('main.user_preferences', email = user.email))

                elif user is not None and (not (user.check_password(form.password.data))):
                    if (date == '1970-01-01 00:00:00'):
                        user.last_login = datetime.datetime(1970, 01, 01, 00, 00, 01)
                    elif (date == '1970-01-01 00:00:01'):
                        user.last_login = datetime.datetime(1970, 01, 01, 00, 00, 02)
                    elif (date == '1970-01-01 00:00:02'):
                        user.last_login = datetime.datetime(1970, 01, 01, 00, 13, 37)
                    else:
                        user.last_login = datetime.datetime(1970, 01, 01, 00, 00, 00)

                    db.session.commit()

                # Hinder timing based enumeration ------------------------------
                else:
                    dummy.check_password(password)

                flash('Incorrect Email Address or Password')
            return render_template("login.html", form = form)
        elif request.form['submit'] == 'Forgot Password?':
            return redirect(url_for('main.reset_password'))

    return render_template("login.html", form = form)

# ----------g-------------------------------------------------------------------
# Logout
# ------------------------------------------------------------------------------
@main.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'), code = 302, Response = None)

# ------------------------------------------------------------------------------
# Reset
# ------------------------------------------------------------------------------
@main.route("/reset", methods = ['GET', 'POST'])
def reset_password():
    form = ResetForm()

    # Check for User and email a reset token -----------------------------------
    if form.validate_on_submit():

        user_email = form.email_address.data
        user_email = user_email.lower()

        user = User.query.filter_by(email = user_email).first()
        if user is not None:
            token = generate_confirmation_token(user.email)
            confirm_url = url_for('main.confirm_reset', token = token, _external = True)
            html = render_template('reset_request.html', confirm_url = confirm_url)
            subject = 'InfoSec Mentors Project - Password Reset'
            send_email(app, user.email, subject, html)
            return render_template('sent_email.html')
    # If no user, send a link to the registration page -------------------------
        else:
            confirm_url = url_for('main.register', _external = True)
            html = render_template('registration_request.html', confirm_url = confirm_url)
            subject = 'InfoSec Mentors Project - Please Register'
            send_email(app, user_email, subject, html)
            return render_template('sent_email.html')

    return render_template('forgot_password.html', form = form)

# ------------------------------------------------------------------------------
# Confirm Reset
# ------------------------------------------------------------------------------
@main.route("/reset/<token>", methods = ['GET', 'POST'])
def confirm_reset(token):

    # Validate the reset request token -----------------------------------------
    try:
        email = confirm_token(token)
    except:
        flash('The token is either invalid or has expired. Please try again.', 'danger')
        return redirect(url_for('main.index)')) #TODO: Landing page for Time-out of token

    # Validate reset form fields, update user password -------------------------
    form = PasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email = email).first()
        if user is not None:
            date = str(user.last_login.isoformat(' '))
            # Prevent a banned user from resetting their password --------------
            if (date != '1970-01-01 00:04:55'):
                user.last_login = datetime.datetime.now()
                user.password = form.password.data
                db.session.add(user)
                db.session.commit()

            return redirect(url_for('main.login'))
        else:
            return redirect(url_for('main.register'))

    return render_template('reset_password.html', form = form, token = token)

# ------------------------------------------------------------------------------
# Confirm Account Deletion
# ------------------------------------------------------------------------------
@main.route("/request_delete", methods = ['GET', 'POST'])
@login_required
def request_delete():
    if request.method == 'GET':
        return render_template('confirm_delete.html')
    elif request.method == 'POST':
       if request.form['submit'] == 'Yes':
           user = User.query.filter_by(id = current_user.id).first()
           if user is not None:
               profile = Profile.query.filter_by(credentials_id = user.id).first()
               if profile is not None:
                   thr = Thread( target = delete_profile, args = [user.id] )
                   thr.start()
                   logout_user()

               return render_template('account_deleted.html')

    return redirect(url_for('main.index'))

# ------------------------------------------------------------------------------
# Delete Account
# ------------------------------------------------------------------------------
def delete_profile(id):
    with app.app_context():

        # Lock the account until a password reset occurs -----------------------
        user = User.query.filter_by(id = id).first()
        user.last_login = datetime.datetime(1970, 01, 01, 00, 13, 37)
        db.session.commit()

        # Notify the mentor / apprentice that the mentorship has ended ---------
        remove_mentor(id)
        remove_apprentice(id)

        # Delete the User's profile --------------------------------------------
        profile = Profile.query.filter_by(credentials_id = id).first()
        identity = str(profile.id)
        sql = text('DELETE FROM profile WHERE id = ' + identity + ';')
        db.engine.execute(sql)

    return True

# ------------------------------------------------------------------------------
# User Preferences
# ------------------------------------------------------------------------------
@main.route('/user_preferences/<email>', methods = ['GET', 'POST'])
@login_required
def user_preferences(email):
    form = UserPreferences()
    user = User.query.filter_by(email = email).first()
    profile = Profile.query.filter_by(credentials_id = user.id).first()

    # Handle unconfirmed users -------------------------------------------------
    if user.confirmed_on is None:
        logout_user()
        return redirect(url_for('main.unconfirmed'))
    # Handle confirmed users with profiles -------------------------------------
    elif profile is not None:
        return redirect(url_for('main.user_profile', id = user.id))
    # Setup a profile ----------------------------------------------------------
    else:
        id = current_user.id
        if ( id == user.id ):
            if form.validate_on_submit():
                gravatar = form.gravatar.data
                gravatar_md5 = md5calc(gravatar)
                new_user = User.query.filter_by(email = email).first_or_404()
                new_profile = Profile(user = current_user,
                                      credentials_id = new_user.id,
                                      available = 1,
                                      gravatar = gravatar_md5,
                                      alias = form.alias.data,
                                      timezone = form.timezone.data,
                                      public_email = form.public_email.data,
                                      twitter = form.twitter.data,
                                      github = form.github.data,
                                      biography = '',
                                      experience = form.experience.data,
                                      mentoring_experience = form.mentoring_experience.data,
                                      mentored_experience = form.mentored_experience.data,
                                      contact_preference = form.contact_preference.data,
                                      mentoring_skill_0 = form.mentoring_skill_0.data,
                                      mentoring_skill_1 = form.mentoring_skill_1.data,
                                      mentoring_skill_2 = form.mentoring_skill_2.data,
                                      mentored_skill_0 = form.mentored_skill_0.data,
                                      mentored_skill_1 = form.mentored_skill_1.data,
                                      mentored_skill_2 = form.mentored_skill_2.data,
                                      mentoring_hours = form.mentoring_hours.data,
                                      mentoring_timeframe = form.mentoring_timeframe.data,
                                      mentored_hours = form.mentored_hours.data,
                                      mentored_timeframe = form.mentored_timeframe.data)
                db.session.add(new_profile)
                db.session.commit()
                return redirect(url_for('main.user_profile', id = new_profile.id))
            return render_template('user_preferences.html', email = email, form = form)

        # If a user tries to modify another person's preferences ---------------
        else:
            #TODO Problematic if Profile 1 is deleted
            return redirect (url_for('main.user_profile', id = 1))

# ------------------------------------------------------------------------------
# User Settings
# ------------------------------------------------------------------------------
@main.route('/user_settings', methods = ['GET', 'POST'])
@login_required
def user_settings():

    id = 0
    try:
        id = current_user.id
        id = int(id)
    except:
        flash('You must login prior to changing settings.', 'danger')
        return redirect(url_for('main.index'))

    if id > 0:
        user = User.query.filter_by(id = id).first()

        # Handle unconfirmed users ---------------------------------------------
        if user.confirmed_on is None:
            logout_user()
            return redirect(url_for('main.unconfirmed'))

        # Populate the form with the user's profile ----------------------------
        profile = Profile.query.filter_by(credentials_id = id).first()
        mentor = Mentor.query.filter_by(id = id).first()
        mentee = Mentor.query.filter_by(mentee_email = user.email).first()
        teacher = None
        teacher_id = None
        student = None
        student_id = None

        if mentee is not None:
            teacher_user= User.query.filter_by(id = mentee.id).first()
            teacher_profile = Profile.query.filter_by(credentials_id = teacher_user.id).first()
            if teacher_profile is not None:
                teacher = teacher_profile.alias
                teacher_id = teacher_profile.id

        if mentor.mentee_email is not None:
            student_user = User.query.filter_by(email = mentor.mentee_email).first()
            student_profile = Profile.query.filter_by(credentials_id = student_user.id).first()
            student = student_profile.alias
            student_id = student_user.id

        if profile:
            old_gravatar = str(profile.gravatar)
            profile.gravatar = ''
            form = UserPreferences(obj = profile)

            if form.validate_on_submit():
                form.populate_obj(profile)

                # DELETE requests in the CRUD cycle ----------------------------
                if request.form['submit'] == 'Remove Mentor':
                    if mentee is not None:
                        thr = Thread( target = remove_mentor, args = [user.id] )
                        thr.start()

                    return redirect(url_for('main.user_profile', id = profile.id))

                elif request.form['submit'] == 'Remove Apprentice':
                    if mentor.mentee_email is not None:
                        thr = Thread( target = remove_apprentice, args = [user.id] )
                        thr.start()

                    return redirect(url_for('main.user_profile', id = profile.id))

                elif request.form['submit'] == 'Delete Profile':
                    return redirect(url_for('main.request_delete'))

                # Pre-fill the user's Profile Settings and accept input --------
                else:

                    profile.gravatar = old_gravatar

                    new_gravatar = str(form.gravatar.data)
                    if (new_gravatar != ''):
                        profile.gravatar = md5calc(form.gravatar.data)

                    profile.alias = form.alias.data
                    profile.timezone = form.timezone.data
                    profile.public_email = form.public_email.data
                    profile.twitter = form.twitter.data
                    profile.github = form.github.data
                    profile.experience = form.experience.data
                    profile.mentoring_experience = form.mentoring_experience.data
                    profile.mentored_experience = form.mentored_experience.data
                    profile.contact_preference = form.contact_preference.data
                    profile.mentoring_skill_0 = form.mentoring_skill_0.data
                    profile.mentoring_skill_1 = form.mentoring_skill_1.data
                    profile.mentoring_skill_2 = form.mentoring_skill_2.data
                    profile.mentored_skill_0 = form.mentored_skill_0.data
                    profile.mentored_skill_1 = form.mentored_skill_1.data
                    profile.mentored_skill_2 = form.mentored_skill_2.data
                    profile.mentoring_hours = form.mentoring_hours.data
                    profile.mentoring_timeframe = form.mentoring_timeframe.data
                    profile.mentored_hours = form.mentored_hours.data
                    profile.mentored_timeframe = form.mentored_timeframe.data
                    db.session.commit()
                    return redirect(url_for('main.user_profile', id = profile.id))
            return render_template('user_settings.html', form = form,
                                                         teacher_id = teacher_id,
                                                         teacher = teacher,
                                                         student_id = student_id,
                                                         student = student )
        # Profile not setup ----------------------------------------------------
        else:
            return redirect(url_for('main.user_preferences', email = user.email))
    else:
        return redirect(url_for('main.login'))

# ------------------------------------------------------------------------------
# Remove Mentor
# ------------------------------------------------------------------------------
def remove_mentor(id):

    with app.app_context():
        user = User.query.filter_by(id = id).first()
        mentor = Mentor.query.filter_by(id = id).first()
        mentee = Mentor.query.filter_by(mentee_email = user.email).first()

        if mentee is not None:
            teacher = Profile.query.filter_by(credentials_id = mentee.id).first()
            teacher_account = User.query.filter_by(id = mentee.id).first()
            teacher.available = 1
            mentee.mentee = None
            mentee.mentee_email = None

            if teacher_account is not None:
                email = teacher_account.email
                html = render_template('end_apprenticeship.html')
                subject = "InfoSec Mentors Project - Mentorship Completed"
                send_email(app, email, subject, html)

        if mentor is not None:
            mentor.completed_on = datetime.datetime.now()

        db.session.commit()

    return True

# ------------------------------------------------------------------------------
# Remove Apprentice
# ------------------------------------------------------------------------------
def remove_apprentice(id):

    with app.app_context():
        profile = Profile.query.filter_by(credentials_id = id).first()
        mentor = Mentor.query.filter_by(id = id).first()

        if mentor.mentee_email is not None:
            email = mentor.mentee_email
            html = render_template('end_mentorship.html')
            subject = "InfoSec Mentors Project - Mentorship Completed"
            send_email(app, email, subject, html)
            mentor.mentee = None
            mentor.mentee_email = None
            mentor.completed_on = datetime.datetime.now()

        profile.available = 1
        db.session.commit()

    return True

# ------------------------------------------------------------------------------
# User Profile
# ------------------------------------------------------------------------------
@main.route('/user/<id>', methods = ['GET', 'POST'])
def user_profile(id):
    if (id.isdigit() and id > 0):

        if request.method == 'POST':
            identity = int(id)

            # Allow for a user to browse between profiles ----------------------
            if request.form['submit'] == 'prev':
                if identity > 1:
                    prev_user = Profile.query.filter(Profile.id < id).order_by(Profile.id.desc()).first()
                    return redirect(url_for('main.user_profile', id = prev_user.id))
                else:
                    return redirect(url_for('main.user_profile', id = id))
            elif request.form['submit'] == 'next':
                next_user = Profile.query.filter(Profile.id > id).order_by(Profile.id.asc()).first()
                if next_user is not None:
                    return redirect(url_for('main.user_profile', id = next_user.id))
                else:
                    return redirect(url_for('main.user_profile', id = id))

            # When a User requests a mentor from the current user(id) ----------
            elif request.form['submit'] == 'Syn (establish connection)':
                try:
                    requestor = User.query.filter_by(id = current_user.id).first()
                    profile = Profile.query.filter_by(id = id).first()
                    if profile.credentials_id != requestor.id:
                        profile.available = 0
                        db.session.add(profile)
                        mentor = Mentor.query.filter_by(id = profile.credentials_id).first()
                        mentor.mentee = requestor.id
                        mentor.mentee_email = requestor.email
                        mentor.requested_on = datetime.datetime.now()
                        db.session.add(mentor)
                        db.session.commit()
                        requestor_token = generate_confirmation_token(requestor.email)
                        requestor_profile = Profile.query.filter_by(credentials_id = requestor.id).first()
                        confirm_url = url_for('main.confirm_mentorship',
                                              token = requestor_token, _external = True)
                        html = render_template('mentorship_request.html',
                                               confirm_url = confirm_url, id = requestor_profile.id)
                        subject = "InfoSec Mentors Project - Mentorship Request"
                        send_email(app, mentor.email, subject, html)
                        logout_user()
                        return render_template('requested.html')
                    else:
                        return redirect(url_for('main.user_profile', id = id))
                except:
                    return redirect(url_for('main.user_profile', id = id))

            # Suggest a mentor with matched skills -----------------------------
            elif request.form['submit'] == 'suggest':
                try:
                    user = User.query.filter_by(id = current_user.id).first()
                    profile = Profile.query.filter_by(credentials_id = user.id).first()
                    identity = suggest(profile)
                    return redirect(url_for('main.user_profile', id = identity))
                except:
                    return redirect(url_for('main.user_profile', id = id))

            # POST Request made is outside of defined behavior -----------------
            else:
                return redirect(url_for('main.index'))

        # GET Request to display user(id)'s Profile ----------------------------
        else:
            profile = Profile.query.filter_by(id = id).first()

            # Check if the user has a mentor -----------------------------------
            try:
                requestor = User.query.filter_by(id = current_user.id).first()
                requestor_profile = Profile.query.filter_by(credentials_id = requestor.id).first()
                mentored = Mentor.query.filter_by(mentee_email = requestor.email).first()
                if requestor_profile is None:
                    mentored = True
            except:
                mentored = None
                requestor_profile = None

            if profile is not None:
                return render_template('user_profile.html',
                                       user = current_user,
                                       availability = profile.available,
                                       gravatar = profile.gravatar,
                                       alias = profile.alias,
                                       experience = profile.experience,
                                       public_email = profile.public_email,
                                       twitter = profile.twitter,
                                       github = profile.github,
                                       biography = profile.biography,
                                       timezone = profile.timezone,
                                       mentoring_experience = profile.mentoring_experience,
                                       mentored_experience = profile.mentored_experience,
                                       contact_preference = profile.contact_preference,
                                       mentoring_skill_0 = profile.mentoring_skill_0,
                                       mentoring_skill_1 = profile.mentoring_skill_1,
                                       mentoring_skill_2 = profile.mentoring_skill_2,
                                       mentored_skill_0 = profile.mentored_skill_0,
                                       mentored_skill_1 = profile.mentored_skill_1,
                                       mentored_skill_2 = profile.mentored_skill_2,
                                       mentoring_hours = profile.mentoring_hours,
                                       mentoring_timeframe = profile.mentoring_timeframe,
                                       mentored_hours = profile.mentored_hours,
                                       mentored_timeframe = profile.mentored_timeframe,
                                       mentored = mentored)
            else:
                return redirect(url_for('main.index'))
    else:
        return redirect(url_for('main.index'))


# ------------------------------------------------------------------------------
# Confirm Mentorship
# ------------------------------------------------------------------------------
@main.route('/request/<token>')
@login_required
def confirm_mentorship(token):
    try:
        email = confirm_request(token)
    except:
        flash('The Mentorship Request link is invalid or has expired.', 'danger')
        return redirect(url_for('main.index)')) #TODO: Landing page for Time-out of token

    mentorship = Mentor.query.filter_by(mentee_email = email).first()
    if mentorship:
        mentorship.accepted_on = datetime.datetime.now()
        db.session.add(mentorship)
        db.session.commit()
        mentor_email = mentorship.email
        html = render_template('accepted.html', contact = mentor_email)
        subject = "InfoSec Mentors Project - Mentorship Request Accepted"
        send_email(app, mentorship.mentee_email, subject, html)
        return render_template('thank_you.html')
    else:
        return redirect(url_for('main.index'))

# ------------------------------------------------------------------------------
# Decline Mentorship
# ------------------------------------------------------------------------------
@main.route('/decline')
@login_required
def decline_mentorship(token):

    user = User.query.filter_by(id = current_user.id).first()

    if user:
        #TODO: Consider generating a separate email for decline vs. remove apprentice
        remove_apprentice(user.id)
        return render_template('declined.html')

    #TODO: Better redirect logic here
    return redirect(url_for('main.index'))

