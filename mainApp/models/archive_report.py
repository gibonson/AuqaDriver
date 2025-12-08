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
    status = db.Column(db.String())# Ready, Not ready


    def __init__(self, title, queryString, minValue, okMinValue, okMaxValue, maxValue, unit, message, reportGroupId):
        self.title = title
        self.queryString = queryString
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
            queryString=formData["queryString"][0]
            minValue=formData["minValue"][0]
            okMinValue=formData["okMinValue"][0]
            okMaxValue=formData["okMaxValue"][0]
            maxValue=formData["maxValue"][0]
            unit=formData["unit"][0]
            message=formData["message"][0]
            reportGroupId=formData["reportGroupId"][0]
            srchive_report_to_add = ArchiveReport(title=title,queryString=queryString, minValue=minValue, okMinValue=okMinValue, okMaxValue=okMaxValue, maxValue=maxValue, unit=unit, message=message, reportGroupId=reportGroupId)
            db.session.add(srchive_report_to_add)
            db.session.commit()
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            self.message = "Error: Device could not be added"
    def __str__(self) -> str:
        return self.message
    
    
class ArchiveReportManager:
    def __init__(self, id):
        self.id = id
        self.message = ""
        self.ArchiveReport = ArchiveReport.query.filter_by(id=self.id).first()

    def edit(self, formData: dict):
        if self.ArchiveReport:
            try:
                self.ArchiveReport.title=formData["title"][0]
                self.ArchiveReport.queryString=formData["queryString"][0]
                self.ArchiveReport.minValue=formData["minValue"][0]
                self.ArchiveReport.okMinValue=formData["okMinValue"][0]
                self.ArchiveReport.okMaxValue=formData["okMaxValue"][0]
                self.ArchiveReport.maxValue=formData["maxValue"][0]
                self.ArchiveReport.unit=formData["unit"][0]
                self.ArchiveReport.message=formData["message"][0]
                self.ArchiveReport.status=formData["status"][0]
                self.ArchiveReport.reportGroupId=formData["reportGroupId"][0]
                db.session.commit()
                self.message = f"ArchiveReport with ID {self.id} successfully updated"
                logger.info(self.message)
            except Exception as e:
                db.session.rollback()
                self.message = f"An error occurred while updating ArchiveReport: {e}"
                logger.error(self.message)
        else:
            self.message = f"ArchiveReport with ID {self.id} does not exist"
            logger.error(self.message)



    def remove(self):
        if self.ArchiveReport:
            ArchiveReport.query.filter(ArchiveReport.id == self.id).delete()
            db.session.commit()
            logger.info(f'ArchiveReport with ID {self.id} removed')
            self.message = f'ArchiveReport with ID {self.id} removed'
        else:
            logger.error(f'ArchiveReport with ID {self.id} does not exist')
            self.message = f'ArchiveReport with ID {self.id} does not exist'
    
    def change_status(self):
        if self.ArchiveReport:
            if self.ArchiveReport.status == "Ready":
                self.ArchiveReport.status = "Not ready"
                self.message = "ArchiveReport status changed to: Not ready"
                logger.info(f'ArchiveReport with ID {self.id} status changed')
            elif self.ArchiveReport.status == "Not ready":
                self.ArchiveReport.status = "Ready"
                logger.info(f'ArchiveReport with ID {self.id} status changed')
                self.message = "ArchiveReport status changed to: Ready"
            else:
                logger.info(f'ArchiveReport with ID {self.id} status error')
                self.message = "Status error!"
            db.session.commit()
        else:
            logger.error(f'ArchiveReport with ID {self.id} does not exist')
            self.message = f'ArchiveReport with ID {self.id} does not exist'
    
    def __str__(self) -> str:
        return self.message