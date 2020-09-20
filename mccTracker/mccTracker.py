import re
import steamAPI
import configparser

from flask_wtf import FlaskForm
from wtforms import StringField
from flask import Flask, render_template, flash
from wtforms.validators import DataRequired

class usernameForm(FlaskForm):
    username = StringField('username', validators=[DataRequired()], render_kw={"placeholder": "SteamID or Account Name"})

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
        steamID = steamAPI.getSteamID(steamID)
        if steamID != 0:
            userData= steamAPI.getUserData(steamID)
            if type(userData) is str:
                flash(f''+userData, 'danger')
                return render_template('master.html', form=form)
            return render_template('master.html', form=form, title=form.username.data, userData=userData)
        else:
            flash(f'Account not found. Only SteamIDs and account names can be used.', 'danger')
            return render_template('master.html', form=form)
    else:
        return render_template('master.html', form=form)


if __name__ == '__main__':
    app.run(debug=True)