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

#Database Setup 
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(50), unique=True, nullable = False)
    password = db.Column(db.String(100), nullable = False)
    first_name = db.Column(db.String(100), nullable = False)
    last_name = db.Column(db.String(100), nullable = False)

class Bot_Messages(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    recipient = db.Column(db.String(50), nullable = False)
    message = db.Column(db.String(1000), nullable = False)

class User_Messages(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    sender = db.Column(db.String(50), nullable = False)
    recipient = db.Column(db.String(50), nullable = False)
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
    response = requests.get("https://evilinsult.com/generate_insult.php?lang=en&type=json")
    insult = response.json()
    insult = insult['insult']
    insult_db_storer(insult)
    return insult

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
    
    if first_name == "" or last_name == "":
        flash("Input A Valid Name. Please Try Again.")
        return redirect(url_for('signup'))

    if username == "":
        flash("Input A Valid Username. Please Try Again.")
        return redirect(url_for('signup'))
    
    if password == "":
        flash("Input A Valid Password. Please Try Again.")
        return redirect(url_for('signup'))

    if user:
        flash("This Username Already Exists. Please Enter A New Username.")
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

    if username == "":
        flash("Input A Valid Username. Please Try Again.")
        return redirect(url_for('signup'))
    
    if password == "":
        flash("Input A Valid Password. Please Try Again.")
        return redirect(url_for('signup'))

    if not user:
        flash("That Username Does Not Exist. Please Sign Up Or Try Another Username.")
        return redirect(url_for('signup'))

    if not check_password_hash(user.password, password):
        flash("Incorrect Password. Please Try Again.")
    
    login_user(user)
    return redirect(url_for('home'))

@app.route('/insult_getter', methods = ["GET", "POST"])
def get_insult():
    insult = request.form.get("insult")
    recipient_first_name = request.form.get("recipient")
    user_first_name = User.query.filter_by(first_name = recipient_first_name).first()
    
    if user_first_name:
        #This should search for insult by keyword in insult database. Have not put all the logic in yet. 
         print()
         
    else:
        redirect(url_for('insult_page'))

    return

@app.route('/insult_page')
def choose_insult():
    return render_template('make-others-feel-better.html')

@app.route('/messages-for-me', methods = ["GET", "POST"])
def messages_for_me():
    bot_array = []
    user_array = []
    bot_data = Bot_Messages.query.filter_by(recipient = current_user.username)
    user_data = User_Messages.query.filter_by(recipient = current_user.username)

    for i in bot_data:
        bot_array.append(i)
    for i in user_data:
        user_array.append(i)

    return render_template('messages-for-me.html', bot_msgs = bot_array, user_msgs = user_array)

@app.route('/users', methods = ["GET", "POST"])
def users():
    user_array = []
    user_data = User.query.all()
    for i in user_data:
        user_array.append(i)
    return render_template('users.html', users = user_array)

@app.route('/inspiration')
def get_inspiration():
    return render_template('inspiration.html')
    
@app.route('/home')
def home():
    return render_template('feel-better.html', msg = "")

@app.route('/feel-better', methods = ["GET", "POST"])
def feel_better():
    msg = insult_generator()
    
    bot_check = Bot_Messages.query.filter_by(recipient = current_user.username, message = msg)
    if not bot_check:
        bot_msg = Bot_Messages(recipient = current_user.username, message = msg)
        db.session.add(bot_msg)
        db.session.commit()

    insult_check = Insults.query.filter_by(insult = msg)
    if not insult_check:
         insult_db_storer(msg)

    return render_template('feel-better.html', msg = msg)

app.run()