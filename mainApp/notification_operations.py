from mainApp.models.notification import NotificationLister
from mainApp.email_operations import emailSender
# from mainApp.web_operations import LinkCreator, WebContentCollector
from mainApp import logger
import time
from datetime import datetime


class NotificationTrigger:
    def __init__(self, requestData: dict) -> None:
        try:
            self.timestamp = round(time.time())
            self.addInfo = requestData["addInfo"]
            self.deviceName = requestData["deviceName"]
            self.deviceIP = requestData["deviceIP"]
            self.type = requestData["type"]
            self.value = requestData["value"]

            logger.debug("Checking notification condition list")
            notificationLister = NotificationLister(notificationStatus="Ready")
            notificationList = notificationLister.get_list()
            for readyNotification in notificationList:
                if self.deviceIP == readyNotification.deviceIP and self.deviceName == readyNotification.deviceName and self.type == readyNotification.type and self.addInfo == readyNotification.addInfo:
                    logger.debug("Notification condition checking")
                    if readyNotification.condition == "less" and int(readyNotification.value) > int(self.value):
                        logger.debug("Less condition")
                        self.handle_notification(readyNotification=readyNotification)
                    elif readyNotification.condition == "more"and int(readyNotification.value) < int(self.value):
                        logger.debug("More condition")
                        self.handle_notification(readyNotification=readyNotification)
                    elif readyNotification.condition == "equal" and int(readyNotification.value) == int(self.value):
                        logger.debug("Equal condition")
                        self.handle_notification(readyNotification=readyNotification)
                    else:
                        logger.debug("Wrong condition")

        except Exception as e:
            logger.error(f"An error occurred: {e}")
            self.message = "Error: Record could not be parsed"


    def handle_notification(self, readyNotification):
        from mainApp.web_operations import LinkCreator, WebContentCollector
        from mainApp.models.archive import ArchiveAdder

        message = readyNotification.message
        message = message.replace("<addInfo>",readyNotification.addInfo)
        message = message.replace("<type>",readyNotification.type)
        message = message.replace("<condition>",readyNotification.condition)
        message = message.replace("<value>",str(readyNotification.value))
        message = message.replace("<self.value>",str(self.value))
        message = message.replace("<date>",str(datetime.now().strftime('%Y-%m-%d')))
        message = message.replace("<time>",str(datetime.now().strftime('%H:%M:%S')))


        if readyNotification.notificationType == "email":
            subject = "Notification: " + readyNotification.type + " for " + readyNotification.deviceName
            logger.debug("Email to send. subject: " + subject + ", and message: " + message)
            requestData = {'addInfo': 'Automatic-> email sent', 'deviceIP': readyNotification.deviceIP, 'deviceName': readyNotification.deviceName, 'type': 'Info', 'value': '-'}
            ArchiveAdder(requestData)
            # emailSender(subject=subject, message=message)
        elif readyNotification.notificationType == "function":
            requestData = {'addInfo': 'Automatic -> event start: ' + readyNotification.eventId , 'deviceIP': readyNotification.deviceIP, 'deviceName': readyNotification.deviceName, 'type': 'Info', 'value': '-'}
            ArchiveAdder(requestData)
            logger.debug("ID function to run: " + readyNotification.eventId)
            WebContentCollector(LinkCreator(readyNotification.eventId, message).functions_list_link_creator()).collect()
