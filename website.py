from flask import Flask, redirect, url_for, flash, render_template, request
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

#Current username var
global curr_user

#Database Setup 
class User(db.Model, UserMixin):
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

class Insults(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    insult = db.Column(db.String(1000), nullable = False)

with app.app_context():
    db.create_all()

#Stores all insults generated for easy retrieval 
def insult_db_storer(insult):
    new_insult = Insults(insult = insult)
    db.session.add(new_insult)
    db.session.commit()

#API
def insult_generator():
    insult = requests.get("https://evilinsult.com/generate_insult.php?lang=en&type=text")
    insult_db_storer(insult)
    return insult.text

#App Routing 
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/signup/check', methods = ["GET", "POST"])
def signup_check():
    first_name = request.form.get("first name")
    last_name = request.form.get("last name")
    username = request.form.get("username")
    password = request.form.get("password")
    user = User.query.filter_by(username = username).first()

    if user:
        flash("This Username Already Exists. Please Enter A New Username.")
        return redirect(url_for('signup'))
    
    if password == "":
        flash("Input A Valid Password. Please Try Again.")
        return redirect(url_for('signup'))
    
    if first_name == "" or last_name == "":
        flash("Input A Valid Name. Please Try Again.")
        return redirect(url_for('signup'))
                
    new_user = User(username = username, password = generate_password_hash(password, method='sha256'), 
                    first_name = first_name, last_name = last_name)
    db.session.add(new_user)
    db.session.commit()
    
    flash("You were signed up.")
    return redirect(url_for('login'))

@app.route('/login/check', methods = ["GET", "POST"])
def login_check():
    username = request.form.get("username")
    password = request.form.get("password")
    user = User.query.filter_by(username = username).first()

    if not user:
        flash("That Username Does Not Exist. Please Sign Up Or Try Another Username.")
        return redirect(url_for('signup'))
    if not check_password_hash(user.password, password):
        flash("Incorrect Password. Please Try Again.")
    
    curr_user = username
    login_user(user)
    return redirect(url_for('home'))

@app.route('/home')
def home():
    insult = insult_generator()
    return render_template('index.html', insult = insult, username = curr_user)

app.run()