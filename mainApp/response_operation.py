from mainApp.models.archive import ArchiveAdder
from mainApp.notification_operations import NotificationTrigger
from mainApp.ignore_operations import IgnoreTrigger
from mainApp import logger


class ResponseTrigger:
    def __init__(self, requestData: dict) -> None:
        logger.debug(f"Request to validation: {requestData}")
        try:
            self.addInfo = requestData["addInfo"]
            self.deviceName = requestData["deviceName"]
            self.deviceIP = requestData["deviceIP"]
            self.type = requestData["type"]
            self.value = requestData["value"]

            
            if IgnoreTrigger(requestData=requestData).get_request_to_ignore() == False:
                NotificationTrigger(requestData=requestData)
                ArchiveAdder(requestData=requestData)

        except Exception as e:
            logger.error(f"An error occurred: {e}")
            self.message = "Error: Record could not be parsed"


