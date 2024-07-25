import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from configparser import ConfigParser
from mainApp.models import Archive
from mainApp.routes import db, app, flash
import time

def emailSender(subject, message, flashMessage = False):
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
    msg = MIMEMultipart("alternative")
    text = MIMEText(message, 'html')

    msg.attach(text)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = receiver

    with smtplib.SMTP("host157641.hostido.net.pl", 587) as server:
        server.login(user, password)
        server.sendmail(sender, receiver, msg.as_string())
        if flashMessage != False:
            flash(f'Mail successfully sent!', category='success')

    with app.app_context():
        timestamp = round(time.time())
        addInfo = "Report sent"
        deviceIP = "127.0.0.1"
        deviceName = "Server"
        type = "Log"
        value = 0
        add_to_archiwe = Archive(timestamp=timestamp,deviceIP = deviceIP, deviceName= deviceName, addInfo = addInfo, value= value, type = type)
        db.session.add(add_to_archiwe)
        db.session.commit()