
# A very simple Flask Hello World app for you to get started with...

from flask import Flask, render_template, request, redirect, session, jsonify
from flask.helpers import url_for
# from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy
from datetime import date, timedelta

app = Flask(__name__)
app.config["SECRET_KEY"] = "ff00ff"
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=30)
db = SQLAlchemy(app)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"


class Leads(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    logo = db.Column(db.Text, nullable=True)
    type = db.Column(db.String(10), nullable=False)
    buy_price = db.Column(db.String(30), nullable=False)
    sell_price = db.Column(db.String(30), nullable=False)
    profit = db.Column(db.String(10), nullable=False)
    good_for_trade = db.Column(db.Boolean, nullable=False, default=True)
    date = db.Column(db.String(100), nullable=False, default=date.today().strftime("%d/%m/%Y"))

class Users(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	fname = db.Column(db.String(50), nullable=False)
	mname = db.Column(db.String(50), nullable=True , default="No_name_Provided")
	lname = db.Column(db.String(50), nullable=False)
	email = db.Column(db.String(100), nullable=False,unique=False)
	add1 = db.Column(db.Text, nullable=False)
	add2 = db.Column(db.Text, nullable=True,default="No Second Address")
	city = db.Column(db.String(50), nullable=False)
	state = db.Column(db.String(50), nullable=False)
	pin = db.Column(db.String(10), nullable=False)
	password = db.Column(db.Text, nullable=False)
	subscribed =db.Column(db.Boolean, nullable=False ,default=False)
	notifications = db.relationship("Notifications", backref="user", lazy=True)

class Notifications(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
	name = db.Column(db.String(50), nullable=False)
	date = db.Column(db.String(100), nullable=False, default=date.today().strftime("%d/%m/%Y"))
	subject = db.Column(db.String(100), nullable=False)
	body = db.Column(db.Text, nullable=False)

class AllNotifications(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(50), nullable=False)
	date = db.Column(db.String(100), nullable=False, default=date.today().strftime("%d/%m/%Y"))
	subject = db.Column(db.String(100), nullable=False)
	body = db.Column(db.Text, nullable=False)

#Making Models For databse
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/subscribe')
def subscribe():
	return render_template('subscribe.html')
@app.route('/subscribe-user',methods=["POST"])
def subscribe_user():
	data = request.form
	session["data"] = data
	session.permanent = True
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
	return redirect(url_for('short_leads'))

@app.route('/notifications')
def notifications():
	# user = Users.query.filter_by(email=session["data"]['email'])
	# notifications = user.notifications + AllNotifications.query.all()
	return render_template('notification.html',notification=notifications , date = date.today().strftime("%d/%m/%Y"))
@app.route('/short-term-leads')
def short_leads():
	return render_template('short_leads.html')
@app.route('/long-term-leads')
def long_leads():
	return render_template('long_leads.html')