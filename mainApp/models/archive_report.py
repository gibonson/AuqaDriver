from mainApp.routes import db
from mainApp import logger

class ArchiveReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String())
    queryString = db.Column(db.String())
    minValue = db.Column(db.Integer())
    okMinValue = db.Column(db.Integer())
    okMaxValue = db.Column(db.Integer())
    maxValue = db.Column(db.Integer())
    unit = db.Column(db.String())
    reportGroupId = db.Column(db.Integer())
    message = db.Column(db.String())

    def __init__(self, title, querryString, minValue, okMinValue, okMaxValue, maxValue, unit, message, reportGroupId):
        self.title = title
        self.queryString = querryString
        self.minValue = minValue
        self.okMinValue = okMinValue
        self.okMaxValue = okMaxValue
        self.maxValue = maxValue
        self.unit = unit
        self.message = message
        self.reportGroupId = reportGroupId

class ArchiveReportLister():
    def __init__(self):
        try:
            self.archiveReport = ArchiveReport.query.all()
        except Exception as e:
            logger.error(f"An error occurred while fetching archive report: {e}")
            self.archiveReport = []
    def get_list(self):
        return self.archiveReport


class ArchiveReporAdder():
    def __init__(self, formData: dict):
        self.message = 'Archive Repor added'
        logger.info("Archive Repor to DB")
        
        try:
            title=formData["title"][0]
            querryString=formData["querryString"][0]
            minValue=formData["minValue"][0]
            okMinValue=formData["okMinValue"][0]
            okMaxValue=formData["okMaxValue"][0]
            maxValue=formData["maxValue"][0]
            unit=formData["unit"][0]
            message=formData["message"][0]
            reportGroupId=formData["reportGroupId"][0]
            srchive_report_to_add = ArchiveReport(title=title,querryString=querryString, minValue=minValue, okMinValue=okMinValue, okMaxValue=okMaxValue, maxValue=maxValue, unit=unit, message=message, reportGroupId=reportGroupId)
            db.session.add(srchive_report_to_add)
            db.session.commit()
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            self.message = "Error: Device could not be added"
    def __str__(self) -> str:
        return self.message