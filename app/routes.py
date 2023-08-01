from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, login_required, current_user, logout_user
from app import app, bcrypt, db
from app.forms import RegisterForm, LoginForm, PasswordResetRequestForm, ResetPasswordForm, PostTextForm
from app.models import User, Post
from app.email import send_reset_password_mail



@app.route('/')
@login_required
def index():
    title ="Register"
    return render_template('index.html', title=title) 

@app.route('/post',methods=['get','post'])
@login_required
def post():
    title ="Post Text"
    form = PostTextForm()
    if form.validate_on_submit():
        body = form.text.data
        post = Post(body=body)
        current_user.posts.append(post)
        db.session.commit()
        flash('Suscess Post', category='info')
    return render_template('post.html', form=form, title=title) 
    
    
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
            #if request.args.get('next'):
            #    next_page = request.args.get('next')
            #    return redirect(url_for(next_page))
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
        token = user.generate_reset_password_token()
        send_reset_password_mail(user, token)
        flash('Password reset request mail is sent, please check ypur mail', category='info')
    return render_template('reset_password_request.html', form=form, title= title)

@app.route('/reset_password/<token>', methods=['get','post'])
def reset_password():
    title = 'Reset Password'
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_summit():
        user = User.check_reset_password_token(token)
        if user:
            user.password = bcrypt.generate_password(form.password.data)
            db.session.commit()
            flash('Your password has benn reset, you can login now', category='info')
            redirect(url_for('login'))
        else:
            flash('This user does not exist', category='info')
            return redirect(url_for('login'))
    return render_template('reset_password_request.html', form=form, title= title)
    

