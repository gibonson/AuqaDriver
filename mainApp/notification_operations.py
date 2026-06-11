import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from configparser import ConfigParser
from mainApp.models.archive import ArchiveAdder
from mainApp.routes import app, flash
from mainApp import logger
import requests


def emailSender(subject, message, flashMessage=False):
    config = ConfigParser()
    config.read("userFiles/config/config_email.ini")
    
    statusMessage = ""
    
    try:
        context = ssl.create_default_context()
        sender = config["EMAIL"]["user_name"]
        receiver = config["EMAIL"]["default_recipient"]
        user = config["EMAIL"]["user_name"]
        password = config["EMAIL"]["password"]

        msg = MIMEMultipart("alternative")
        text = MIMEText(message, "html")
        msg.attach(text)
        msg["Subject"] = subject
        msg["From"] = sender
        msg["To"] = receiver

        with smtplib.SMTP("host157641.hostido.net.pl", 587) as server:
            server.starttls(context=context)
            server.login(user, password)
            server.sendmail(sender, receiver, msg.as_string())
            statusMessage = "Report sent"
            if flashMessage:
                flash(f"Mail successfully sent!", category="success")

    except smtplib.SMTPException as e:
        statusMessage = f"An SMTP error occurred: {str(e)}"
        if flashMessage:
            flash("Failed to send mail.", category="danger")

    except Exception as e:
        statusMessage = f"An error occurred: {str(e)}"
        if flashMessage:
            flash("Failed to send mail.", category="danger")
    
    if statusMessage != "":
        logger.info(statusMessage)
        with app.app_context():
            requestData = {
                    "addInfo": statusMessage,
                    "deviceIP": "127.0.0.1",
                    "deviceName": "Server",
                    "type": "log",
                    "value": "-",
                    "requestID": "emailSender",
                }
            ArchiveAdder(requestData)


def pushoverSender(message, attachment=None):
    config = ConfigParser()
    config.read("userFiles/config/config_email.ini")
    
    statusMessage = ""

    try:
        r = requests.post(
            "https://api.pushover.net/1/messages.json",
            data={
                "token": config["PUSHOVER"]["token"],
                "user": config["PUSHOVER"]["user"],
                "message": message,
            })
        statusMessage = "Pushover notification sent"
    except Exception as e:
        statusMessage = f"Pushover notification error: {str(e)}"
        
    if statusMessage != "":
        logger.info(statusMessage)
        with app.app_context():
            requestData = {
                    "addInfo": statusMessage,
                    "deviceIP": "127.0.0.1",
                    "deviceName": "Server",
                    "type": "log",
                    "value": "-",
                    "requestID": "pushoverSender",
                }
            ArchiveAdder(requestData)