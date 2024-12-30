from mainApp.routes import db
from mainApp import logger
from datetime import datetime, timedelta
import time


class Archive(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.Integer())
    deviceIP = db.Column(db.String())
    deviceName = db.Column(db.String())
    addInfo = db.Column(db.String())
    value = db.Column(db.Integer())
    type = db.Column(db.String())
    comment = db.Column(db.String())


    def __init__(self, timestamp, deviceIP, deviceName, addInfo, value, type, comment):
        self.timestamp = timestamp
        self.deviceIP = deviceIP
        self.deviceName = deviceName
        self.addInfo = addInfo
        self.value = value
        self.type = type
        self.comment = comment


class ArchiveLister():
    def __init__(self):
        try:
            self.archive = Archive.query.order_by(Archive.id.desc()).limit(100)
        except Exception as e:
            logger.error(f"An error occurred while fetching archive: {e}")
            self.archive = []
    def get_list(self):
        return self.archive

class ArchiveSearchList():
    def __init__(self, searchedValues):
        self.archiveSearchList = []
        self.searchedValues = searchedValues

        deviceIP = []
        deviceName = []
        addInfo = []
        type = []
        limit = searchedValues["limit"][0]
        timestampEnd = searchedValues["timestampEnd"][0]
        timestampStart = searchedValues["timestampStart"][0]
        recordType = searchedValues["recordType"][0]

        recordTypeList = recordType.split(" -> ")
        deviceIP.append(recordTypeList[0])
        deviceName.append(recordTypeList[1])
        addInfo.append(recordTypeList[2])
        type.append(recordTypeList[3])

        self.archiveSearchList = Archive.query.filter(
            Archive.deviceIP.in_(deviceIP),
            Archive.addInfo.in_(addInfo),
            Archive.deviceName.in_(deviceName),
            Archive.timestamp >= datetime.strptime(timestampStart, "%Y-%m-%dT%H:%M").timestamp(),
            Archive.timestamp <= datetime.strptime(timestampEnd, "%Y-%m-%dT%H:%M").timestamp(),
            Archive.type.in_(type)
        ).order_by(Archive.id.desc()).limit(limit)

    def get_list(self):
        return self.archiveSearchList


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
            if "comment" in requestData:
                comment = requestData["comment"]
            else:
                comment = "-"
            add_to_archiwe = Archive(timestamp=timestamp, deviceIP=deviceIP,
                                    deviceName=deviceName, addInfo=addInfo, value=value, type=type, comment=comment)
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