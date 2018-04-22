"""Movie Ratings."""

from jinja2 import StrictUndefined
from flask import (Flask, render_template, redirect, request,
                   flash, session, jsonify)
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

    try:
        if request.args.get("logout") == 'logout':
            del session['user_id']
            flash("You've logged out :(")
            return redirect('/')

        else:
            return render_template("homepage.html")
    except:
        flash("You haven't logged in yet, dummy!")
        return redirect('/')

@app.route('/movies')
def movie_list():
    """SHOW ME THOSE MOVIES"""

    movie_list = Movie.query.order_by('title').all()
    return render_template("movies.html", movie_list=movie_list)

@app.route('/movies/<movie_id>')
def movie_page(movie_id):
    """Show details about a specific movie"""

    all_movie_data = db.session.query(Movie.title,
                                      Movie.release_date,
                                      Movie.imdb_url,
                                      Movie.movie_id,
                                      Ratings.user_id,
                                      Ratings.score).filter_by(movie_id=movie_id
                                      ).join(Ratings).all()

    # check if user is logged in
    try:
        if session['user_id']:
            login_yesno = "true"
    except:
        login_yesno = "false"

    return render_template("movie_details.html", all_movie_data=all_movie_data, login_yesno=login_yesno)

@app.route('/display_rating')
def display_rating():
    """Display that rating, yo!"""

    movie_id = request.args.get("movie_id")

    # queries database (ratings table) for object, filtered on movie and user
    user_rating = db.session.query(Ratings.score).filter_by(movie_id=movie_id, user_id=session['user_id']).all()

    # jsonified user_rating is passed into displayRateOption()
    return jsonify(user_rating)


@app.route('/add-rating', methods=['POST'])
def add_rating():
    """Add or update user rating for a movie."""

    # grabs new_rating & movie_id values from incoming post request sent by addRating
    # function on the html side
    new_rating = request.form.get('new_rating')
    movie_id = request.form.get('movie_id')
    # queries database (ratings table) for object, filtered on movie and user
    user_rating = Ratings.query.filter_by(movie_id=movie_id, user_id=session['user_id']).first()
    if user_rating:
        # updates user's score with the new rating
        user_rating.score = new_rating

    # if user has not rated the movie yet, then create a new row in the Ratings
    else:
        new_rating_object = Ratings(user_id=session['user_id'],
                                    movie_id=movie_id,
                                    score=new_rating
                                    )
        db.session.add(new_rating_object)
    db.session.commit()

    # new_rating is passed into updateRating()
    return new_rating


@app.route('/users')
def user_list():
    """SHOW ME THOSE USERS"""

    users = User.query.all()
    return render_template("user_list.html", users=users)


@app.route('/users/<user_id>')
def user_page(user_id):
    """Display information about an individual user."""

    user_info = User.query.filter_by(user_id=user_id).first()
    user_ratings = db.session.query(Ratings.score,
                                    Movie.title,
                                    Movie.imdb_url).filter_by(user_id=user_id
                                    ).join(Movie).order_by('title').all()

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
