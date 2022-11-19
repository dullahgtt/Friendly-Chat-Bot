import flask
import os
import requests
import json
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

app = flask.Flask(__name__)
app.secret_key = 'SPREAD_HATE_NOT_LOVE'
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(50), unique=True, nullable = False)
    password = db.Column(db.String(100), nullable = False)
    first_name = db.Column(db.String(100), nullable = False)
    last_name = db.Column(db.String(100), nullable = False)

def insult_generator():
    insult = requests.get("https://evilinsult.com/generate_insult.php?lang=en&type=text")
    return insult.text


@app.route('/')
def login():
    return flask.render_template('login.html')

@app.route('/signup')
def signup():
    return flask.render_template('signup.html')

@app.route('/signup/check', methods = ["GET", "POST"])
def signup_check():
    return 

@app.route('/login/check', methods = ["GET", "POST"])
def login_check():
    return

@app.route('/home')
def home():
    insult = insult_generator()
    return flask.render_template('index.html', insult = insult)

app.run()