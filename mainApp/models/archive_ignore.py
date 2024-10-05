from mainApp.routes import db
from mainApp import logger
import time


class ArchiveIgone(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    deviceIP = db.Column(db.String())
    deviceName = db.Column(db.String())
    addInfo = db.Column(db.String())
    value = db.Column(db.Integer())
    type = db.Column(db.String())
    status = db.Column(db.String())

    def __init__(self, timestamp, deviceIP, deviceName, addInfo, value, type, status):
        self.timestamp = timestamp
        self.deviceIP = deviceIP
        self.deviceName = deviceName
        self.addInfo = addInfo
        self.value = value
        self.type = type
        self.status = status

class ArchiveIgoneLister():
    def __init__(self):
        try:
            self.archive = ArchiveIgone.query.order_by(ArchiveIgone.id.desc()).limit(100)
        except Exception as e:
            logger.error(f"An error occurred while fetching ArchiveIgone: {e}")
            self.archive = []
    def get_list(self):
        return self.archive


class ArchiveIgoneAdder():
    def __init__(self, requestData: dict):
        self.message = 'Added to ArchiveIgone'
        logger.info("Adding record to ArchiveIgone")

        try:
            logger.debug("Values to add: %s", requestData)
            addInfo = requestData["addInfo"]
            deviceName = requestData["deviceName"]
            deviceIP = requestData["deviceIP"]
            type = requestData["type"]
            value = requestData["value"]
            status = requestData["status"]
            add_to_archiwe = ArchiveIgone(deviceIP=deviceIP, deviceName=deviceName, addInfo=addInfo, value=value, type=type, status=status)
            db.session.add(add_to_archiwe)
            db.session.commit()

        except Exception as e:
            logger.error(f"An error occurred: {e}")
            self.message = "Error: Record could not be added to ArchiveIgone"

    def __str__(self) -> str:
        return self.message
    
class AArchiveIgoneManager:
    def __init__(self, id):
        self.id = id
        self.message = ""
        self.device = ArchiveIgone.query.filter_by(id=self.id).first()

    def remove(self):
        if self.device:
            ArchiveIgone.query.filter(ArchiveIgone.id == self.id).delete()
            db.session.commit()
            logger.info(f'Record with ID {self.id} removed')
            self.message = f'Record with ID {self.id} removed'
        else:
            logger.error(f'Record with ID {self.id} does not exist')
            self.message = f'Record with ID {self.id} does not exist'

    def change_status(self):
        if self.deviceFunction:
            if self.deviceFunction.functionStatus == "Ready":
                self.deviceFunction.functionStatus = "Not ready"
                self.message = "Device Function status changeD to: Not ready"
                logger.info(f'Device Function with ID {self.id} status changed')
            elif self.deviceFunction.functionStatus == "Not ready":
                self.deviceFunction.functionStatus = "Ready"
                logger.info(f'Device Function with ID {self.id} status changed')
                self.message = "Device Function status changed to: Ready"
            else:
                logger.info(f'Device Function with ID {self.id} status error')
                self.message = "Status error!"
            db.session.commit()
        else:
            logger.error(f'Device Function with ID {self.id} does not exist')
            self.message = f'Device Function with ID {self.id} does not exist'

    def __str__(self) -> str:
        return self.message