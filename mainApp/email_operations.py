import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from configparser import ConfigParser
from mainApp.models.archive import ArchiveAdder
from mainApp.routes import app, flash
from mainApp import logger


def emailSender(subject, message, flashMessage = False):
    config = ConfigParser()
    config.read("userFiles/config_email.ini")

    try:
        context = ssl.create_default_context()
        sender = config['EMAIL']['user_name']
        receiver = config['EMAIL']['default_recipient']
        user = config['EMAIL']['user_name']
        password = config['EMAIL']['password']
        
        msg = MIMEMultipart("alternative")
        text = MIMEText(message, 'html')
        msg.attach(text)
        msg['Subject'] = subject
        msg['From'] = sender
        msg['To'] = receiver

        with smtplib.SMTP("host157641.hostido.net.pl", 587) as server:
            server.starttls(context=context)
            server.login(user, password)
            server.sendmail(sender, receiver, msg.as_string())
            logger.info("Report sent")
            if flashMessage != False:
                flash(f'Mail successfully sent!', category='success')
            with app.app_context():
                requestData = {'addInfo': 'Report sent', 'deviceIP': '127.0.0.1', 'deviceName': 'Server', 'type': 'Log', 'value': 0}
                archiveAdder = ArchiveAdder(requestData)

    except Exception as e:
        logger.error("An error occurred: %s", str(e))
        with app.app_context():
            requestData = {'addInfo': 'Report sent error', 'deviceIP': '127.0.0.1', 'deviceName': 'Server', 'type': 'Log', 'value': 0}
            archiveAdder = ArchiveAdder(requestData)
        if flashMessage != False:
            flash('Failed to send mail.', category='danger')