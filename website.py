import flask
import os
import requests
import json
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

app = flask.Flask(__name__)

def insult_generator():
    insult = requests.get("https://evilinsult.com/generate_insult.php?lang=en&type=text")
    
    return insult.text

@app.route('/')
def main():
    insult = insult_generator()
    return flask.render_template('index.html', insult = insult)

app.run()