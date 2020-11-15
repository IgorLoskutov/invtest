# -*- coding: utf-8 -*-
from flask import render_template, request, redirect, url_for, flash
from flask_login import current_user, login_user, logout_user, login_required

from werkzeug.urls import url_parse

from app import app, db

from app.models import Users
from app.forms import login_form, payment_form
from app.payment import Payment

@app.route('/', methods=['POST', 'GET'])
@app.route('/index', methods=['POST', 'GET'])
@login_required
def index():
    print(request.method)
    if request.method == 'GET' and request.args:
        payment = Payment(dict(request.args))
        prepared =  payment.prepare()
        url =  prepared['url']
        return redirect(url)
    form = payment_form()
    if form.validate_on_submit():
        payment = Payment(form.data)
        prepared =  payment.prepare()
        if prepared.get('url'):
            return redirect(prepared.get('url'))
        return render_template(prepared['tpl'], form=prepared['data'], data=prepared['data']) 
    return render_template('payment.html', title='Payment', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = login_form()
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = login_form()
    if form.validate_on_submit():
        if request.method == 'POST':
            password = request.form['password']
            username = request.form['username']
            exist = Users.query.filter_by(username=username).all()
            print('exist', exist)
        if exist:
                flash('Unable to register')
                return redirect('/register')
        curr_user = Users(username=username)
        curr_user.set_password(password)
        db.session.add(curr_user)
        db.session.commit()
        return redirect('/register')
    return render_template('register.html', title='Register', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))