from mainApp.models.notification import NotificationLister
from mainApp.email_operations import emailSender
from mainApp import logger
import time


class NotificationTrigger:
    def __init__(self, requestData: dict) -> None:
        try:
            self.timestamp = round(time.time())
            self.addInfo = requestData["addInfo"]
            self.deviceName = requestData["deviceName"]
            self.deviceIP = requestData["deviceIP"]
            self.type = requestData["type"]
            self.value = requestData["value"]
            print("value self" + str(self.value))

            notificationLister = NotificationLister(notificationStatus="Ready")
            notificationList = notificationLister.get_list()
            for readyNotification in notificationList:
                if self.deviceIP == readyNotification.deviceIP and self.deviceName == readyNotification.deviceName and self.type == readyNotification.type and self.addInfo == readyNotification.addInfo:
                    logger.debug("Notification in ready status")
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
                        logger.debug("wrong condition")

        except Exception as e:
            logger.error(f"An error occurred: {e}")
            self.message = "Error: Record could not be parsed"
        


    def handle_notification(self, readyNotification):
        if readyNotification.notificationType == "email":
            subject = "Notification: " + readyNotification.type + " for " + readyNotification.deviceName
            message = readyNotification.message
            message = message.replace("<addInfo>",readyNotification.addInfo)
            message = message.replace("<type>",readyNotification.type)
            message = message.replace("<condition>",readyNotification.condition)
            message = message.replace("<value>",str(readyNotification.value))
            message = message.replace("<self.value>",str(self.value))
            logger.debug("Email to send. subject: " + subject + ", and message: " + message)
            emailSender(subject=subject, message=message)
        elif readyNotification.notificationType == "function":
            logger.debug("ID function to run: " + readyNotification.functionId)
