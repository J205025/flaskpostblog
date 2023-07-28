#!/usr/bin/env python3
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from config import Config


app = Flask(__name__)
app.config.from_object(Config)
boostrap = Bootstrap(app)
bcrypt = Bcrypt(app)
login = LoginManager(app)
mail = Mail(app)
db = SQLAlchemy(app)
app.app_context().push()
login.login_view ='login'
login.login_message= 'You must login to acess this page'
login.login_message_category = 'info'

from app.routes import *

    