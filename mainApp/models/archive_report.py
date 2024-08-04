from mainApp.routes import db
from mainApp import logger

class ArchiveReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String())
    description = db.Column(db.String())
    deviceIP = db.Column(db.String())
    deviceName = db.Column(db.String())
    addInfo = db.Column(db.String())
    type = db.Column(db.String())
    avgOrSum = db.Column(db.String())
    timerRangeHours = db.Column(db.Integer())
    quantityValues = db.Column(db.Integer())
    minValue = db.Column(db.Integer())
    okMinValue = db.Column(db.Integer())
    okMaxValue = db.Column(db.Integer())
    maxValue = db.Column(db.Integer())

    def __init__(self, deviceIP, title, description, deviceName, addInfo, type, avgOrSum, timerRangeHours, quantityValues, minValue, okMinValue, okMaxValue, maxValue):
        self.deviceIP = deviceIP
        self.title = title
        self.description = description
        self.deviceName = deviceName
        self.addInfo = addInfo
        self.type = type
        self.avgOrSum = avgOrSum
        self.timerRangeHours = timerRangeHours
        self.quantityValues = quantityValues
        self.minValue = minValue
        self.okMinValue = okMinValue
        self.okMaxValue = okMaxValue
        self.maxValue = maxValue

class ArchiveReportLister():
    def __init__(self):
        try:
            self.archiveReport = ArchiveReport.query.all()
        except Exception as e:
            logger.error(f"An error occurred while fetching archive report: {e}")
            self.archiveReport = []
    def get_list(self):
        return self.archiveReport