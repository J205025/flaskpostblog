from threading import Thread
from flask import current_app, render_template
from flask_mail import Message
from app import mail

def send_async_mail(app, msg):
    with app.app_context():
        mail.send(msg)

def send_reset_password_mail(user, token):
    msg = mail.send_message(subject='Reset Your Password',
                      sender=current_app.config['MAIL_USERNAME'],
                      recipients=[user.email],
                      html = render_template('reset_password_gmail.html',user=user, token=token)
    )
    Thread(target=send_reset_password_mail, args=(app, msg, )).start()
   # mail.send(msg)