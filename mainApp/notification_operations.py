from mainApp.models.notification import NotificationLister
from mainApp.email_operations import emailSender
from mainApp import logger
import time


class NotificationTrigger:
    def __init__(self, requestData: dict) -> None:
        logger.debug("Notification to check: %s", requestData)
        try:
            self.timestamp = round(time.time())
            self.addInfo = requestData["addInfo"]
            self.deviceName = requestData["deviceName"]
            self.deviceIP = requestData["deviceIP"]
            self.type = requestData["type"]
            self.value = requestData["value"]
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            self.message = "Error: Record could not be parsed"
        
        notificationLister = NotificationLister(status="Ready")
        notificationList = notificationLister.get_list()
        for readyNotification in notificationList:
            print(readyNotification)
            # print(readyNotification.deviceIP)
            # print(readyNotification.deviceName)
            # print(readyNotification.addInfo)
            # print(readyNotification.type)
            # print(readyNotification.condition)
            # print(readyNotification.value)
            # print(readyNotification.notificationStatus)
            # print(readyNotification.notificationType)
            # print(readyNotification.functionId)
            # print(readyNotification.message)
            if self.deviceIP == readyNotification.deviceIP and self.deviceName == readyNotification.deviceName and self.type == readyNotification.type and self.addInfo == readyNotification.addInfo:
                print("toto")
                # condition less
                # condition more
                # condition equal 

                # email
                # function

        

