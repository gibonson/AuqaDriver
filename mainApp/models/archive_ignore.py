from mainApp.routes import db
from mainApp import logger


class ArchiveIgone(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    deviceIP = db.Column(db.String())
    deviceName = db.Column(db.String())
    addInfo = db.Column(db.String())
    value = db.Column(db.Integer())
    type = db.Column(db.String())
    status = db.Column(db.String())

    def __init__(self, deviceIP, deviceName, addInfo, value, type, status):
        self.deviceIP = deviceIP
        self.deviceName = deviceName
        self.addInfo = addInfo
        self.value = value
        self.type = type
        self.status = status

class ArchiveIgoneLister():
    def __init__(self, status = "All"):
        if status is "All":
            try:
                self.archiveIgone = ArchiveIgone.query.all()
            except Exception as e:
                logger.error(f"An error occurred while fetching ArchiveIgone: {e}")
                self.archiveIgone = []
        elif status is "Ready":
            try:
                self.archiveIgone = ArchiveIgone.query.filter(ArchiveIgone.status=="Ready").all()
            except Exception as e:
                logger.error(f"An error occurred while fetching ArchiveIgone: {e}")
                self.archiveIgone = []
    def get_list(self):
        return self.archiveIgone


class ArchiveIgoneAdder():
    def __init__(self, requestData: dict):
        self.message = 'Added to ArchiveIgone'
        logger.info("Adding record to ArchiveIgone")

        try:
            logger.debug("Values to add: %s", requestData)
            addInfo = requestData["addInfo"][0]
            deviceName = requestData["deviceName"][0]
            deviceIP = requestData["deviceIP"][0]
            type = requestData["type"][0]
            value = requestData["value"][0]
            status = requestData["status"][0]
            add_to_archiwe_ignore = ArchiveIgone(deviceIP=deviceIP, deviceName=deviceName, addInfo=addInfo, value=value, type=type, status=status)
            db.session.add(add_to_archiwe_ignore)
            db.session.commit()

        except Exception as e:
            logger.error(f"An error occurred: {e}")
            self.message = "Error: Record could not be added to ArchiveIgone"

    def __str__(self) -> str:
        return self.message
    
class ArchiveIgnoreManager:
    def __init__(self, id):
        self.id = id
        self.message = ""
        self.archiveIgone = ArchiveIgone.query.filter_by(id=self.id).first()

    def remove(self):
        if self.archiveIgone:
            ArchiveIgone.query.filter(ArchiveIgone.id == self.id).delete()
            db.session.commit()
            logger.info(f'Record with ID {self.id} removed')
            self.message = f'Record with ID {self.id} removed'
        else:
            logger.error(f'Record with ID {self.id} does not exist')
            self.message = f'Record with ID {self.id} does not exist'

    def change_status(self):
        if self.archiveIgone:
            if self.archiveIgone.status == "Ready":
                self.archiveIgone.status = "Not ready"
                self.message = "archiveIgone status changed to: Not ready"
                logger.info(f'archiveIgone with ID {self.id} status changed')
            elif self.archiveIgone.status == "Not ready":
                self.archiveIgone.status = "Ready"
                logger.info(f'archiveIgone with ID {self.id} status changed')
                self.message = "archiveIgone status changed to: Ready"
            else:
                logger.info(f'archiveIgone with ID {self.id} status error')
                self.message = "Status error!"
            db.session.commit()
        else:
            logger.error(f'archiveIgone with ID {self.id} does not exist')
            self.message = f'archiveIgone with ID {self.id} does not exist'

    def __str__(self) -> str:
        return self.message