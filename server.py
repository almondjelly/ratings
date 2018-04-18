"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import (Flask, render_template, redirect, request,
                   flash, session)
from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db, User, Ratings, Movie


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
    # return "<html><body>Placeholder for the homepage.</body></html>"
    return render_template("homepage.html")


@app.route('/users')
def user_list():
    """SHOW ME THOSE USERS"""

    users = User.query.all()
    return render_template("user_list.html", users=users)


@app.route('/register', methods=['GET'])
def register_form():
    """Let users log in"""

    return render_template("register_form.html")


@app.route('/register', methods=['POST'])
def register_process():
    """Register users who don't have an account yet"""

    user_email = request.form.get('email')
    user_pw = request.form.get('password')

    # check that email is in users table
    if User.query.filter_by(email=user_email):

        # if so, store the user's id in queried_id
        queried_id = User.query.filter_by(email=user_email)[0].user_id

        # check that the password is correct
        if User.query.filter_by(password=user_pw):

            # if so, store the user's id in the flask session; log them
            session["user_id"] = queried_id
            #FLASH TEXT TO CONFIRM LOGIN
            return redirect("/")

        # # if not, alert the user that their password is wrong
        # else:

    # if the email is not in the table, create new user
    else:
        db.session.add(User(email=user_email, password=user_pw))
        db.session.commit()
        # add queried_id to session, log them in (will need to query the table for their generated id)
        session["user_id"] = queried_id

        # FLASH TEXT TO CONFIRM ACCOUNT CREATION + LOGIN
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
