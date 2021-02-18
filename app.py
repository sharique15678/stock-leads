
# A very simple Flask Hello World app for you to get started with...

from flask import Flask, render_template, request, redirect, session, jsonify
from flask.helpers import url_for
# from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SECRET_KEY"] = "ff00ff"
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=30)

db = SQLAlchemy(app)

@app.route('/')
def home():
    return render_template('register.html')
@app.route('/register-user',methods=["POST"])
def register_user():
	session["data"] = request.form
	fname = data.get('fname')
	mname = data.get('mname')
	lname = data.get('lname')
	email = data.get('email')
	add1 = data.get('add1')
	add2 = data.get('add2')
	city = data.get('city')
	state = data.get('state')
	pin = data.get('pin')
	password = data.get('pass')
	conrfirm_password = data.get('conpass')
	return render_template('index.html')

