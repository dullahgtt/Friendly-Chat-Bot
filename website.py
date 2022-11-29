from flask import Flask, redirect, url_for, flash, render_template, request
import os
import requests
import json
import random
import html 
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, current_user, login_required, logout_user
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

button_msgs = ["Click For Happiness!", 
               "Positivity Awaits!", 
               "Feel Loved!", 
               "Brighten Your Day!", 
               "This Click Will Change Your Life!", 
               "Find Joy!", 
               "Press The Therapeutic Button!"]

temp_username = ""

#Database Setup 
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(50), unique = True, nullable = False)
    password = db.Column(db.String(100), nullable = False)
    first_name = db.Column(db.String(100), nullable = False)
    last_name = db.Column(db.String(100), nullable = False)

class Bot_Messages(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    recipient = db.Column(db.String(50), nullable = False)
    message = db.Column(db.String(10000), nullable = False)

class User_Messages(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    sender = db.Column(db.String(50), nullable = False)
    recipient = db.Column(db.String(50), nullable = False)
    message = db.Column(db.String(10000), nullable = False)

class Insults(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    insult = db.Column(db.String(10000), nullable = False)

with app.app_context():
    db.create_all()

#Get a button message to display
def get_button_msg():
    size = len(button_msgs) - 1
    r = random.randint(0, size)
    return button_msgs[r]

#Stores all unique insults generated for easy retrieval 
def insult_db_storer(insult):
    check = Insults.query.filter_by(insult = insult).first()
    if not check:
        new_insult = Insults(insult = insult)
        db.session.add(new_insult)
        db.session.commit()

#API
def insult_generator():
    response = requests.get("https://evilinsult.com/generate_insult.php?lang=en&type=text")
    insult = html.unescape(response.text)
    insult_db_storer(insult)
    return insult

#App Routing 
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def login():
    return render_template('login.html', uname = temp_username)

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/logout', methods = ["GET", "POST"])
def logout():
    logout_user()
    flash("You Have Been Logged Out")
    return redirect(url_for('login'))

@app.route('/delete-account', methods = ["GET", "POST"])
def delete():
    confirmation = request.form.get("username")
    if confirmation == "":
        flash("Please enter your username and try again")
        return redirect(url_for('profile'))
    if confirmation != current_user.username:
        flash("Incorrect username. Please try again.")
        return redirect(url_for('profile'))

    user = User.query.filter_by(username = current_user.username).first()
    bot_msgs = Bot_Messages.query.filter_by(recipient = current_user.username).all()
    logout_user()
    db.session.delete(user)
    for i in bot_msgs:
        db.session.delete(i)
    db.session.commit()
    flash("Your account has been deleted.")
    return redirect(url_for('signup'))
    
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
    global temp_username
    username = request.form.get("username")
    password = request.form.get("password")
    user = User.query.filter_by(username = username).first()

    if username == "":
        flash("Input A Valid Username. Please Try Again.")
        return redirect(url_for('login'))

    if not user:
        flash("That Username Does Not Exist. Please Sign Up Or Try Another Username.")
        return redirect(url_for('login'))
    
    if password == "":
        flash("Input A Valid Password. Please Try Again.")
        temp_username = username
        return redirect(url_for('login'))

    if not check_password_hash(user.password, password):
        flash("Incorrect Password. Please Try Again.")
        temp_username = username
        return redirect(url_for('login'))
    
    login_user(user)
    temp_username = ""
    return redirect(url_for('home'))

@app.route('/send_msg', methods = ["GET", "POST"])
def send_msg():
    recipient_name = request.form.get("username")
    msg = request.form.get("message")
    approval = request.form.get("approval")

    if recipient_name == "":
        flash("Please enter a username and try again.")
        return redirect(url_for('make_others_feel_better'))

    if msg == "":
        flash("Please enter a message and try again.")
        return redirect(url_for('make_others_feel_better'))
        
    if approval is None:
        flash("Please indicate if you want your message added.")
        return redirect(url_for('make_others_feel_better'))
    
    user_check = User.query.filter_by(username = recipient_name).first()
    if not user_check:
        flash("That username does not exist. Please see the users page for a list of website users.")
        return redirect(url_for('make_others_feel_better'))
    
    if approval == "Yes":
        insult_db_storer(msg)
    
    user_msg = User_Messages(sender = current_user.username, recipient = recipient_name, message = msg)
    db.session.add(user_msg)
    db.session.commit()
    flash(f"{recipient_name} will see your message when they visits the website.")
    return redirect(url_for('make_others_feel_better'))

@app.route('/make-others-feel-better')
def make_others_feel_better():
    return render_template('make-others-feel-better.html')

@app.route('/messages-for-me', methods = ["GET", "POST"])
def messages_for_me():
    bot_array = []
    user_array = []
    bot_data = Bot_Messages.query.filter_by(recipient = current_user.username).all()
    user_data = User_Messages.query.filter_by(recipient = current_user.username).all()

    for i in bot_data:
        bot_array.append(i)
    for i in user_data:
        user_array.append(i)

    return render_template('messages-for-me.html', bot_msgs = bot_array, user_msgs = user_array)

@app.route('/messages-i-sent', methods=["GET", "POST"])
def messages_i_sent():
    user_array = []
    user_data = User_Messages.query.filter_by(sender = current_user.username).all()

    for i in user_data:
        user_array.append(i)

    return render_template('messages-i-sent.html', user_msgs = user_array)

@app.route('/users', methods = ["GET", "POST"])
def users():
    user_array = []
    user_data = User.query.all()
    for i in user_data:
        user_array.append(i)
    return render_template('users.html', users = user_array)

#This function helps the get_inspiration function access the databases for possible 
# insults based on inputs from users for relative "quotes".
@app.route('/search_insults', methods = ["GET", "POST"])
def possible_inspirations():
    keyword = request.form.get("insult_keyword")
    insults = Insults.query.filter(Insults.insult.contains(keyword)).all()
    temp = 1 
    if not insults:
        flash("No Insult Was Found", 'error')
        return redirect(url_for('get_inspiration'))
    
    for i in insults:
        flash(f"{temp}. {i.insult}", 'message')
        temp = temp + 1
    return redirect(url_for('get_inspiration'))

@app.route('/inspiration')
def get_inspiration():
    return render_template('inspiration.html')

@app.route('/profile')
def profile():
    uname = current_user.username
    fname = current_user.first_name 
    lname = current_user.last_name 
    return render_template('profile.html', username = uname, firstname = fname, lastname = lname)

@app.route('/feel-better', methods = ["GET", "POST"])
def feel_better():
    reason_for_sadness = request.form.get("why_feel_sad")
    this = "Oh no! I am so sorry " + reason_for_sadness +  " happened to you... Here, have a cookie:"
    
    if reason_for_sadness == "" or reason_for_sadness.isspace():
        flash("Input a reason so William knows how to help you!")
        return redirect(url_for('home'))
    
    msg = insult_generator()

    bot_check = Bot_Messages.query.filter_by(recipient = current_user.username, message = msg).first() 
    if not bot_check:
        bot_msg = Bot_Messages(recipient = current_user.username, message = msg)
        db.session.add(bot_msg)
        db.session.commit()

    return render_template('feel-better.html', this = this, msg = msg, button_msg = get_button_msg())

@app.route('/home')
def home():
    return render_template('feel-better.html', msg = "", button_msg = get_button_msg())

app.run()