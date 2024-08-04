from mainApp.routes import db
from mainApp import logger
import time


class Archive(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.Integer())
    deviceIP = db.Column(db.String())
    deviceName = db.Column(db.String())
    addInfo = db.Column(db.String())
    value = db.Column(db.Integer())
    type = db.Column(db.String())

    def __init__(self, timestamp, deviceIP, deviceName, addInfo, value, type):
        self.timestamp = timestamp
        self.deviceIP = deviceIP
        self.deviceName = deviceName
        self.addInfo = addInfo
        self.value = value
        self.type = type


class ArchiveLister():
    def __init__(self):
        try:
            self.archive = Archive.query.order_by(Archive.id.desc()).limit(100)
        except Exception as e:
            logger.error(f"An error occurred while fetching archive: {e}")
            self.archive = []
    def get_list(self):
        return self.archive


class ArchiveAdder():
    def __init__(self, requestData: dict):
        self.message = 'Added to archive'
        logger.info("Adding record to archive")

        try:
            logger.debug("Values to add: %s", requestData)
            timestamp = round(time.time())
            addInfo = requestData["addInfo"]
            deviceName = requestData["deviceName"]
            deviceIP = requestData["deviceIP"]
            type = requestData["type"]
            value = requestData["value"]
            add_to_archiwe = Archive(timestamp=timestamp, deviceIP=deviceIP,
                                    deviceName=deviceName, addInfo=addInfo, value=value, type=type)
            db.session.add(add_to_archiwe)
            db.session.commit()

        except Exception as e:
            logger.error(f"An error occurred: {e}")
            self.message = "Error: Record could not be added to archive"

    def __str__(self) -> str:
        return self.message
    
class ArchiveManager:
    def __init__(self, id):
        self.id = id
        self.message = ""
        self.device = Archive.query.filter_by(id=self.id).first()

    def remove_archive(self):
        if self.device:
            Archive.query.filter(Archive.id == self.id).delete()
            db.session.commit()
            logger.info(f'Record with ID {self.id} removed')
            self.message = f'Record with ID {self.id} removed'
        else:
            logger.error(f'Record with ID {self.id} does not exist')
            self.message = f'Record with ID {self.id} does not exist'

    def __str__(self) -> str:
        return self.message