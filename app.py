#!/usr/bin/python
# -*- coding: utf-8 -*-
# A very simple Flask Hello World app for you to get started with...

from flask import Flask, render_template, request, redirect, session, \
    jsonify
from flask.helpers import url_for

# from flask_mail import Mail, Message

from flask_sqlalchemy import SQLAlchemy
from datetime import date, timedelta

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ff00ff'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)
db = SQLAlchemy(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['UPLOAD_FOLDER'] = '/logo'
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024
h = 'hello'


class Leads(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    logo = db.Column(db.Text, nullable=True)
    type = db.Column(db.String(10), nullable=False)
    buy_price = db.Column(db.String(30), nullable=False)
    sell_price = db.Column(db.String(30), nullable=False)
    profit = db.Column(db.String(10), nullable=False)
    good_for_trade = db.Column(db.Boolean, nullable=False, default=True)
    date = db.Column(db.String(100), nullable=False,
                     default=date.today().strftime('%d/%m/%Y'))


class Users(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(50), nullable=False)
    mname = db.Column(db.String(50), nullable=True,
                      default='No_name_Provided')
    lname = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=False)
    add1 = db.Column(db.Text, nullable=False)
    add2 = db.Column(db.Text, nullable=True, default='No Second Address'
                     )
    city = db.Column(db.String(50), nullable=False)
    state = db.Column(db.String(50), nullable=False)
    pin = db.Column(db.String(10), nullable=False)
    password = db.Column(db.Text, nullable=False)
    subscribed = db.Column(db.Boolean, nullable=False, default=False)
    notifications = db.relationship('Notifications', backref='user',
                                    lazy=True)


class Notifications(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                        nullable=False)
    name = db.Column(db.String(50), nullable=False)
    date = db.Column(db.String(100), nullable=False,
                     default=date.today().strftime('%d/%m/%Y'))
    subject = db.Column(db.String(100), nullable=False)
    body = db.Column(db.Text, nullable=False)


class AllNotifications(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), nullable=False, default='all')
    name = db.Column(db.String(50), nullable=False)
    date = db.Column(db.String(100), nullable=False,
                     default=date.today().strftime('%d/%m/%Y'))
    subject = db.Column(db.String(100), nullable=False)
    body = db.Column(db.Text, nullable=False)


# Making Models For databse

@app.route('/')
def home():
    if 'email' in session:
        if session['subscribed'] == True:
            return redirect(url_for('short_leads'))
    return render_template('index.html')


@app.route('/subscribe')
def subscribe():
    if 'email' in session:
        if session['subscribed'] == True:
            return redirect(url_for('short_leads'))
        else :
            return redirect(url_for('login'))
    return render_template('subscribe.html')


@app.route('/subscribe-user', methods=['POST'])
def subscribe_user():
    data = request.form
    if 'email' in session:
        if session['subscribed'] == True:
            return redirect(url_for('short_leads'))
    if Users.query.filter_by(email=data.get('email')).all():
        return render_template('subscribe.html',
                               error='User Is Already Registered. Please Login'
                               )
    if data.get('pass') != data.get('conpass'):
        return render_template('subscribe.html',
                               error='Both Passwords Doesnot Match.')
    user = Users(
        fname=data.get('fname'),
        mname=data.get('mname'),
        lname=data.get('lname'),
        email=data.get('email'),
        add1=data.get('add1'),
        add2=data.get('add2'),
        city=data.get('city'),
        state=data.get('state'),
        pin=data.get('pin'),
        password=data.get('pass'),
        )
    db.sesssion.add(user)
    db.sesssion.commit()
    sesssion['email'] = data.get('email')
    return redirect(url_for('short_leads'))


@app.route('/login')
def login():
    if 'email' in session:
        if session['subscribed'] == True:
            return redirect(url_for('short_leads'))
    return render_template('login.html')


@app.route('/login/verify', methods=['POST'])
def login_user():
    data = request.form
    if not Users.query.filter_by(email=data.get('email')).all():
        return 'invalid'
    user = Users.query.filter_by(email=data.get('email')).first()
    if user.password != data.get('pass'):
        return 'incorrect'

    # if user.subscribed == False :
    #     return "please pay to us"

    user.subscribed = True
    db.session.commit()
    session['email'] = user.email
    session['subscribed'] = user.subscribed
    return redirect(url_for('short_leads'))


@app.route('/notifications')
def notifications():
    if 'email' not in session:
        return redirect(url_for('login'))
    user = Users.query.filter_by(email=session['email']).first()
    notifications = AllNotifications.query.all()
    list = []
    for a in user.notifications:
        b = {
            'id': a.id,
            'name': a.name,
            'date': a.date,
            'subject': a.subject,
            'body': a.body,
            }
        list.append(b)
    notifications = notifications + list
    return render_template('notification.html',
                           notifications=notifications,
                           date=date.today().strftime('%d/%m/%Y'))


@app.route('/short-term-leads')
def short_leads():
    if 'email' not in session:
        return redirect(url_for('login'))
    return render_template('short_leads.html',
                           leads=Leads.query.filter_by(type='short'
                           ).all())


@app.route('/long-term-leads')
def long_leads():
    if 'email' not in session:
        return redirect(url_for('login'))
    return render_template('long_leads.html',
                           leads=Leads.query.filter_by(type='long'
                           ).all())


@app.route('/logout')
def logout():
    session.pop('email', None)
    session.pop('subscribed', None)
    return redirect(url_for('home'))


@app.route('/admin')
def admin():
    return render_template('admin_login.html')


@app.route('/admin/verify', methods=['POST'])
def verify_admin():
    data = request.form
    if data.get('uname') == 'name@example.com' and data.get('pass') \
        == '824210':
    session['admin'] = True
    return redirect(url_for('admin_leads'))
    else:
        return 'You Are Not Admin'


@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    return redirect(url_for('admin'))


@app.route('/admin/leads')
def admin_leads():
    if 'admin' not in session:
        return redirect(url_for('admin'))
    leads = Leads.query.all()
    return render_template('admin_leads.html', leads=leads)


@app.route('/admin/leads/edit/<int:id>')
def edit_lead(id):
    if 'admin' not in session:
        return redirect(url_for('admin'))
    lead = Leads.query.get(id)
    return render_template('admin_edit_lead.html', lead=lead)


@app.route('/admin/leads/edit/confirm/<int:id>', methods=['POST'])
def confirm_edit_lead(id):
    data = request.form
    lead = Leads.query.get(id)
    lead.name = data.get('name')
    lead.type = data.get('type')
    lead.buy_price = data.get('buy_price')
    lead.sell_price = data.get('sell_price')
    db.session.commit()
    return redirect(url_for('admin_leads'))


@app.route('/admin/leads/add')
def add_lead():
    if 'admin' not in session:
        return redirect(url_for('admin'))
    return render_template('admin_new_lead.html')


@app.route('/admin/leads/add/verify', methods=['POST'])
def verify_add_lead():
    data = request.form
    if data.get('good') == 'yes':
        lead = Leads(
            name=data.get('name'),
            logo=data.get('logourl'),
            type=data.get('type'),
            buy_price=str(float(data.get('buy_price'))),
            sell_price=str(float(data.get('sell_price'))),
            profit=str((float(data.get('sell_price'))
                       - float(data.get('buy_price')))
                       / float(data.get('buy_price'))),
            good_for_trade=True,
            )
    else:
        lead = Leads(
            name=data.get('name'),
            logo=data.get('logourl'),
            type=data.get('type'),
            buy_price=str(float(data.get('buy_price'))),
            sell_price=str(float(data.get('sell_price'))),
            profit=str((float(data.get('sell_price'))
                       - float(data.get('buy_price')))
                       / float(data.get('buy_price'))),
            good_for_trade=False,
            )
    db.session.add(lead)
    db.session.commit()
    return redirect(url_for('admin_leads'))


@app.route('/admin/leads/delete/<int:id>')
def delete_lead(id):
    if 'admin' not in session:
        return redirect(url_for('admin'))
    lead = Leads.query.get(id)
    db.session.delete(lead)
    db.session.commit()
    return redirect(url_for('admin_leads'))


@app.route('/admin/notifications')
def admin_notifications():
    if 'admin' not in session:
        return redirect(url_for('admin'))
    notifications = AllNotifications.query.all() \
        + Notifications.query.all()
    return render_template('admin_notification.html',
                           notifications=notifications)


@app.route('/admin/notifications/add')
def add_notification():
    if 'admin' not in session:
        return redirect(url_for('admin'))
    users = Users.query.filter_by(subscribed=True).all()
    return render_template('admin_create_notification.html',
                           users=users)


@app.route('/admin/notifications/add/verify', methods=['POST'])
def verify_add_notification():
    data = request.form
    if data.get('users') == 'all':
        notifi = AllNotifications(name=data.get('name'),
                                  subject=data.get('subject'),
                                  body=data.get('body'))
        db.session.add(notifi)
        db.session.commit()
    else:
        notifi = Notifications(user_id=int(data.get('users')),
                               name=data.get('name'),
                               subject=data.get('subject'),
                               body=data.get('body'))
        db.session.add(notifi)
        db.session.commit()
    return redirect(url_for('admin_notifications'))


@app.route('/admin/notifications/delete/personal/<int:id>')
def delete_personal_notification(id):
    if 'admin' not in session:
        return redirect(url_for('admin'))
    notifi = Notifications.query.get(id)
    db.session.delete(notifi)
    db.session.commit()
    return redirect(url_for('admin_notifications'))


@app.route('/admin/notifications/delete/public/<int:id>')
def delete_public_notification(id):
    if 'admin' not in session:
        return redirect(url_for('admin'))
    notifi = AllNotifications.query.get(id)
    db.session.delete(notifi)
    db.session.commit()
    return redirect(url_for('admin_notifications'))


@app.route('/add-all')
def add():
    for i in range(10):
        lead = Leads(
            name='amazon Lead' + str(i),
            logo='../static/logo.png',
            type='short',
            buy_price='255',
            sell_price='855',
            profit='60',
            good_for_trade=True,
            )
        db.session.add(lead)
    for i in range(10):
        lead = Leads(
            name='apple Lead' + str(i),
            logo='../static/logo.png',
            type='long',
            buy_price='255',
            sell_price='855',
            profit='60',
            good_for_trade=True,
            )
        db.session.add(lead)
    for i in range(10):
        notifi = AllNotifications(name='amazon stock drop' + str(i),
                                  subject='just a testing subject',
                                  body='just to test tis is some body for anytinjhgjhgsdfj'
                                  )
        db.session.add(notifi)
    for i in range(10):
        notifi = AllNotifications(name='amazon stock drop' + str(i),
                                  date='43/54/2002',
                                  subject='just a testing subject',
                                  body='just to test tis is some body for anytinjhgjhgsdfj'
                                  )
        db.session.add(notifi)
    db.session.commit()
    return redirect(url_for('home'))


@app.route('/delete-all')
def delete():
    session.pop('email', None)
    session.pop('subscribed', None)
    notis = Notifications.query.all()
    for noti in notis:
        db.sesssion.delete(noti)
    users = Users.query.all()
    for user in users:
        db.session.delete(user)
    anotis = AllNotifications.query.all()
    for anoti in anotis:
        db.session.delete(anoti)
    leads = Leads.query.all()
    for ld in leads:
        db.session.delete(ld)
    db.session.commit()
    return redirect(url_for('admin'))

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
