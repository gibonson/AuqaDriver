from mainApp.models.archive_ignore import ArchiveIgoneLister
from mainApp import logger

class IgnoreTrigger:
    def __init__(self, requestData: dict) -> None:
        try:
            self.addInfo = requestData["addInfo"]
            self.deviceName = requestData["deviceName"]
            self.deviceIP = requestData["deviceIP"]
            self.type = requestData["type"]
            self.value = requestData["value"]
            self.request_to_ignore = False

            logger.debug("Checking Ignore list")
            archiveIgoneLister = ArchiveIgoneLister(status="Ready")
            archiveIgoneList = archiveIgoneLister.get_list()
            for archiveIgoneRecord in archiveIgoneList:
                if (self.deviceIP, self.deviceName, self.type, self.addInfo, self.value) == (archiveIgoneRecord.deviceIP, archiveIgoneRecord.deviceName, archiveIgoneRecord.type, archiveIgoneRecord.addInfo, archiveIgoneRecord.value):
                    logger.debug("Validation Ignore list: Request to ignore")
                    self.request_to_ignore = True


        except Exception as e:
            logger.error(f"An error occurred: {e}")
            self.message = "Error: Request could not be parsed"

    def get_request_to_ignore(self)->bool:
        return self.request_to_ignore