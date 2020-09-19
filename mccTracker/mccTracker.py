import re
import steamAPI
import configparser

from flask_wtf import FlaskForm
from wtforms import StringField
from flask import Flask, render_template, flash
from wtforms.validators import DataRequired


import json

class usernameForm(FlaskForm):
    username = StringField('username', validators=[DataRequired()])

parser = configparser.ConfigParser()
parser.read('config.ini')

app = Flask(__name__)
app.config['SECRET_KEY'] = parser.get('keys','SECRET_KEY')

@app.route('/', methods=['GET','POST'])
@app.route('/home', methods=['GET','POST'])
def home():
    form = usernameForm()
    if form.username.data:
        steamID = form.username.data
        if re.search(r"^\d{17}$",steamID):
            flash(f'Acount loaded!', 'success')
            return render_template('master.html', form=form, title=form.username.data, userData= steamAPI.getUserData(steamID))
        else:
            steamID = steamAPI.getSteamID(steamID)
            if steamID != 0:
                flash(f'Acount loaded!', 'success')
                return render_template('master.html', form=form, title=form.username.data, userData= steamAPI.getUserData(steamID))
            else:
                flash(f'Acount not found. Only SteamIDs and account names cane be used.', 'danger')
                return render_template('master.html', form=form)
    else:
        return render_template('master.html', form=form)
if __name__ == '__main__':
    app.run(debug=True)