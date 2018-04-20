"""Movie Ratings."""

from jinja2 import StrictUndefined
from flask import (Flask, render_template, redirect, request,
                   flash, session)
from flask_debugtoolbar import DebugToolbarExtension
from model import connect_to_db, db, User, Ratings, Movie
import pdb

app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""

    if request.args.get("logout") == 'logout':
        del session['user_id']
        flash("You've logged out :(")
        return redirect('/')

    else:
        return render_template("homepage.html")


@app.route('/users')
def user_list():
    """SHOW ME THOSE USERS"""

    users = User.query.all()
    return render_template("user_list.html", users=users)


@app.route('/users/<user_id>')
def user_page(user_id):
    """Display information about an individual user."""

    user_info = User.query.filter_by(user_id=user_id).first()
    user_ratings = User.query.filter_by(user_id=user_id).all()

    # UPDATE JINJA FOR LOOP TO POPULATE RATINGS + MOVIE TITLES :) :) YOU CAN DO IT!!!!
    return render_template("user_page.html", user_info=user_info, user_ratings=
        user_ratings)


@app.route('/register', methods=['GET'])
def register_form():
    """Displays the registration and login form."""

    return render_template("register_form.html")


@app.route('/register', methods=['POST'])
def register_process():
    """Register users who don't have an account yet OR logs in users
    who are already in the db."""

    user_email = request.form.get('email')
    user_pw = request.form.get('password')

    # check that email is in users table
    if User.query.filter_by(email=user_email).first():

        # if so, store the user's id in queried_id
        queried_id = User.query.filter_by(email=user_email).first().user_id

        # check that the password is correct
        if User.query.filter_by(email=user_email).first().password == user_pw:

            # if password matches, store the user's id in the flask session; log them in
            session["user_id"] = queried_id

            #FLASH TEXT TO CONFIRM LOGIN
            flash("You've successfully logged in! Hoorayyyyy!")
            return redirect("/")

        # if password doesn't match, alert the user that their password is wrong
        else:
            flash("That password is not correct. Try again!")
            return redirect("/register")

    # if the email doesn't already exist in the table, create new user
    else:
        db.session.add(User(email=user_email, password=user_pw))
        db.session.commit()
        # add queried_id to session, log them in
        queried_id = User.query.filter_by(email=user_email).first().user_id
        session["user_id"] = queried_id

        # FLASH TEXT TO CONFIRM ACCOUNT CREATION + LOGIN
        flash("You've successfully created your account! You're now logged in!")
        return redirect("/")


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    # make sure templates, etc. are not cached in debug mode
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')
