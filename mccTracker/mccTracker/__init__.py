import configparser

from flask import Flask


parser = configparser.ConfigParser()
parser.read('config.ini')

app = Flask(__name__)
app.config['SECRET_KEY'] = parser.get('keys','SECRET_KEY')

from mccTracker import routes