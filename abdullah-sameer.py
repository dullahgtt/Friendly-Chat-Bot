import flask
import requests
import json

app = flask.Flask(__name__)

@app.route('/')
def main():
    return flask.render_template('chat-bot.html')

app.run(debug=True)