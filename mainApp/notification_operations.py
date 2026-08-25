import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from mainApp.models.archive import ArchiveAdder
from mainApp.routes import app, flash
from mainApp import logger
from mainApp.config_operations import load_config_json
import requests


def loadNotificationConfig():
    try:
        config = load_config_json("config_notification.json")

        return {
            "EMAIL": {
                "USER_NAME": config["EMAIL"]["USER_NAME"],
                "PASSWORD": config["EMAIL"]["PASSWORD"],
                "DEFAULT_RECIPIENT": config["EMAIL"]["DEFAULT_RECIPIENT"],
            },
            "PUSHOVER": {
                "TOKEN": config["PUSHOVER"]["TOKEN"],
                "USER": config["PUSHOVER"]["USER"],
            },
        }

    except Exception as e:
        logger.error(
            f"An error occurred while fetching notification configuration: {e}"
        )
        return None


def emailSender(subject, message, flashMessage=False):
    
    statusMessage = ""

    try:

        config = loadNotificationConfig()

        if not config:
            raise Exception("Notification configuration could not be loaded")

        context = ssl.create_default_context()
        sender = config["EMAIL"]["USER_NAME"]
        receiver = config["EMAIL"]["DEFAULT_RECIPIENT"]
        user = config["EMAIL"]["USER_NAME"]
        password = config["EMAIL"]["PASSWORD"]


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

    statusMessage = ""

    try:

        config = loadNotificationConfig()
        if not config:
            raise Exception("Notification configuration could not be loaded")
        print(config["PUSHOVER"]["TOKEN"])
        print(config["PUSHOVER"]["USER"])

        r = requests.post(
            "https://api.pushover.net/1/messages.json",
            data={
                "token": config["PUSHOVER"]["TOKEN"],
                "user": config["PUSHOVER"]["USER"],
                "message": message,
            },
        )
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
