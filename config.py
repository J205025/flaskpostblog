import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    #SECRET KEY
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a-long-password'
    
    #RECAPTCHA_KEY
    #RECAPTCHA_PUBLIC_KEY = os.environ.get('RECAPTCHA_PUBLIC_KEY') or '6LfZrF4nAAAAAMomAX9jcV6RtE40MX8G6PkXP6Kd'
    #RECAPTCHA_PRIVATE_KKEY = os.environ.get('RECAPTCHA_PRIVATE_KEY') or '6LfZrF4nAAAAAMomAX9jcV6RtE40MX8G6PkXP6Kd'
    
    #Database configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS =  False
    
    #Flask Mail Gmail Config
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.environ.get('GMAIL_USERNAME')or 'j207031'
    MAIL_PASSWORD = os.environ.get('GMAIL_PASSWORD')or 'Xintias80'
       