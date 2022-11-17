import flask
import requests
import json

app = flask.Flask(__name__)

def insult_generator():
    insult = requests.get("https://evilinsult.com/generate_insult.php?lang=en&type=text")
    
    return insult.text

@app.route('/')
def main():
    insult = insult_generator()
    return flask.render_template('chat-bot.html', insult = insult)

app.run(debug=True)