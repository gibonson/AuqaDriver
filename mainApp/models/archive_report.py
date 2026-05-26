import json
import os

from mainApp.routes import db
from mainApp import logger
from sqlalchemy.orm import synonym
from mainApp.config_operations import get_report_config_path

class ArchiveReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reportName = db.Column('title', db.String(), unique=True, nullable=False)
    title = synonym('reportName')
    reportDescription = db.Column(db.String())
    queryString = db.Column(db.String())
    minValue = db.Column(db.Integer())
    okMinValue = db.Column(db.Integer())
    okMaxValue = db.Column(db.Integer())
    maxValue = db.Column(db.Integer())
    unit = db.Column(db.String())
    reportGroupId = db.Column(db.Integer())
    message = db.Column(db.String())
    status = db.Column(db.String())# Ready, Not ready


    def __init__(self, reportName, queryString, minValue, okMinValue, okMaxValue, maxValue, unit, message, reportGroupId, reportDescription=None):
        self.reportName = reportName
        self.reportDescription = reportDescription
        self.queryString = queryString
        self.minValue = minValue
        self.okMinValue = okMinValue
        self.okMaxValue = okMaxValue
        self.maxValue = maxValue
        self.unit = unit
        self.message = message
        self.reportGroupId = reportGroupId

class ArchiveReportConfig:
    def __init__(
        self,
        reportName,
        reportDescription,
        queryString,
        minValue,
        okMinValue,
        okMaxValue,
        maxValue,
        unit,
        message,
        reportGroupId,
        status,
    ):
        self.reportName = reportName
        self.reportDescription = reportDescription
        self.queryString = queryString
        self.minValue = minValue
        self.okMinValue = okMinValue
        self.okMaxValue = okMaxValue
        self.maxValue = maxValue
        self.unit = unit
        self.message = message
        self.reportGroupId = reportGroupId
        self.status = status


class ArchiveReportLister():
    def __init__(self, reportGroupId=None):
        self.reportGroupId = reportGroupId
        self.archiveReport = []
        try:
            config_path = get_report_config_path()
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as config_file:
                    report_list = json.load(config_file)
                for report_data in report_list:
                    report = ArchiveReportConfig(
                        reportName=report_data.get('reportName'),
                        reportDescription=report_data.get('reportDescription'),
                        queryString=report_data.get('queryString'),
                        minValue=report_data.get('minValue'),
                        okMinValue=report_data.get('okMinValue'),
                        okMaxValue=report_data.get('okMaxValue'),
                        maxValue=report_data.get('maxValue'),
                        unit=report_data.get('unit'),
                        message=report_data.get('message'),
                        reportGroupId=report_data.get('reportGroupId'),
                        status=report_data.get('status'),
                    )
                    self.archiveReport.append(report)
                if self.reportGroupId is not None:
                    self.archiveReport = [report for report in self.archiveReport if report.reportGroupId == self.reportGroupId]
        except Exception as e:
            logger.error(f"An error occurred while fetching archive report: {e}")
            self.archiveReport = []

    def get_list(self):
        return self.archiveReport


class GetReportIdsListWhenGroupId():
    def __init__(self, reportGroupId):
        self.reportGroupId = reportGroupId
        self.ids = []
        try:
            config_path = get_report_config_path()
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as config_file:
                    report_list = json.load(config_file)
                self.ids = [report.get('reportName') for report in report_list if report.get('reportGroupId') == self.reportGroupId and report.get('status') == 'Ready']
        except Exception as e:
            logger.error(f"An error occurred while fetching report names: {e}")
    def get_ids(self):
        return self.ids 


class ArchiveReporAdder():
    def __init__(self, formData: dict):
        self.message = 'Archive Repor added'
        logger.info("Archive Repor to DB")
        
        try:
            reportName=formData["reportName"][0]
            queryString=formData["queryString"][0]
            minValue=formData["minValue"][0]
            okMinValue=formData["okMinValue"][0]
            okMaxValue=formData["okMaxValue"][0]
            maxValue=formData["maxValue"][0]
            unit=formData["unit"][0]
            message=formData["message"][0]
            reportDescription=formData.get("reportDescription", [None])[0]
            reportGroupId=formData["reportGroupId"][0]

            if ArchiveReport.query.filter_by(reportName=reportName).first():
                raise ValueError(f'Report name "{reportName}" już istnieje.')

            srchive_report_to_add = ArchiveReport(reportName=reportName, queryString=queryString, minValue=minValue, okMinValue=okMinValue, okMaxValue=okMaxValue, maxValue=maxValue, unit=unit, message=message, reportGroupId=reportGroupId, reportDescription=reportDescription)
            db.session.add(srchive_report_to_add)
            db.session.commit()
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            self.message = "Error: Report could not be added"
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
                new_report_name = formData["reportName"][0]
                existing_report = ArchiveReport.query.filter_by(reportName=new_report_name).first()
                if existing_report and existing_report.id != self.id:
                    raise ValueError(f'Report name "{new_report_name}" już istnieje.')

                self.ArchiveReport.reportName=new_report_name
                self.ArchiveReport.queryString=formData["queryString"][0]
                self.ArchiveReport.minValue=formData["minValue"][0]
                self.ArchiveReport.okMinValue=formData["okMinValue"][0]
                self.ArchiveReport.okMaxValue=formData["okMaxValue"][0]
                self.ArchiveReport.maxValue=formData["maxValue"][0]
                self.ArchiveReport.unit=formData["unit"][0]
                self.ArchiveReport.message=formData["message"][0]
                self.ArchiveReport.reportDescription=formData.get("reportDescription", [None])[0]
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