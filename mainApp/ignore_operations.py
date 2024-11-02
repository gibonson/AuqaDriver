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

            archiveIgoneLister = ArchiveIgoneLister(status="Ready")
            archiveIgoneList = archiveIgoneLister.get_list()
            for archiveIgoneRecord in archiveIgoneList:
                if self.deviceIP == archiveIgoneRecord.deviceIP and self.deviceName == archiveIgoneRecord.deviceName and self.type == archiveIgoneRecord.type and self.addInfo == archiveIgoneRecord.addInfo:
                    logger.debug("ArchiveIgone in ready status")

        except Exception as e:
            logger.error(f"An error occurred: {e}")
            self.message = "Error: Record could not be parsed"