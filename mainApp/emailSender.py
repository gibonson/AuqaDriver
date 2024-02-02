import smtplib, ssl
from email.mime.text import MIMEText
from configparser import ConfigParser
from mainApp.routes import flash


def emailTestSender():
    config = ConfigParser()
    config.read("userFiles/config_email.ini")
    print(config.sections())
    print(list(config['EMAIL']))


    sender = config['EMAIL']['user_name']
    receiver = config['EMAIL']['default_recipient']
    user = config['EMAIL']['user_name']
    password = config['EMAIL']['password']
    context = ssl.create_default_context()

    msg = MIMEText('notificacion example')

    msg['Subject'] = 'Test mail'
    msg['From'] = sender
    msg['To'] = receiver

    with smtplib.SMTP("host157641.hostido.net.pl", 587) as server:

        server.login(user, password)
        server.sendmail(sender, receiver, msg.as_string())
        flash(f'Mail successfully sent!', category='success')


def emailSender(subject, message):
    print(subject)
    print(message)
    config = ConfigParser()
    config.read("userFiles/config_email.ini")
    print(config.sections())
    print(list(config['EMAIL']))


    sender = config['EMAIL']['user_name']
    receiver = config['EMAIL']['default_recipient']
    user = config['EMAIL']['user_name']
    password = config['EMAIL']['password']
    context = ssl.create_default_context()

    msg = MIMEText(message)

    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = receiver

    with smtplib.SMTP("host157641.hostido.net.pl", 587) as server:

        server.login(user, password)
        server.sendmail(sender, receiver, msg.as_string())
        flash(f'Mail successfully sent!', category='success')