from flask import redirect, url_for, Flask, flash, render_template, request
import os
import requests
import json
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

#App Setup 
app = Flask(__name__)
app.secret_key = 'SPREAD_HATE_NOT_LOVE'
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

#Database Setup 
class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(50), unique=True, nullable = False)
    password = db.Column(db.String(100), nullable = False)
    first_name = db.Column(db.String(100), nullable = False)
    last_name = db.Column(db.String(100), nullable = False)

class Bot_Messages(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    recepient = db.Column(db.String(50), nullable = False)
    message = db.Column(db.String(1000), nullable = False)

class User_Messages(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    sender = db.Column(db.String(50), nullable = False)
    recepient = db.Column(db.String(50), nullable = False)
    message = db.Column(db.String(1000), nullable = False)

with app.app_context():
    db.create_all()

#API
def insult_generator():
    insult = requests.get("https://evilinsult.com/generate_insult.php?lang=en&type=text")
    return insult.text
    
@app.route('/')
def login():
    return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/signup/check', methods = ["GET", "POST"])
def signup_check():
    return redirect(url_for('login'))

@app.route('/login/check', methods = ["GET", "POST"])
def login_check():
    return redirect(url_for('signup'))

@app.route('/home')
def home():
    username = ""
    insult = insult_generator()
    return render_template('index.html', insult = insult, username = username)

app.run()