from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, login_required, current_user, logout_user
from app import app, bcrypt, db
from app.forms import RegisterForm, LoginForm, PasswordResetRequestForm, ResetPasswordForm
from app.models import User
from app.email import send_reset_password_mail



@app.route('/')
@login_required
def index():
    title ="Register"
    return render_template('index.html', title=title) 

@app.route('/register',methods=['get','post'])
def register():
    title ="Register"
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = bcrypt.generate_password_hash(form.password.data)
        user = User(username=username, email=email, password=password)
        db.session.add(user)
        db.session.commit()
        flash("Congrats, Registration success", category='success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form, title= title)

 
@app.route('/login',methods=['get','post'])
def login():
    title ='Login'
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        remember= form.remember.data
        #check if password is matched
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            #User exits and password matched
            login_user(user, remember=remember)
            flash('Login Success', category='info')
            if request.args.get('next'):
                next_page = request.args.get('next')
                return redirect(url_for(next_page))
            return redirect(url_for('index'))
        flash('User does not exist or password not match', category='danger')
    return render_template('login.html', form=form, title= title)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/reset_password_request', methods=['get','post'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    title = 'Reset Password'
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        email = form.email.data
        user = User.query.filter_by(email=email).first()
        token = generate_reset_password_token()
        send_reset_password_token()
    return render_template('reset_password_request.html', form=form, title= title)

@app.route('/reset_password', methods=['get','post'])
def reset_password():
    title = 'Reset Password'
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    return render_template('reset_password_request.html', form=form, title= title)
    

