from mainApp import logger
from mainApp.config_operations import load_config_json


class ArchiveReport:
    def __init__(
        self,
        reportName,
        queryString,
        minValue,
        okMinValue,
        okMaxValue,
        maxValue,
        unit,
        message,
        reportGroupId,
        reportDescription=None,
        status=None,
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


class ArchiveReportLister:
    def __init__(self):
        self.archiveReport = []
        try:
            report_list = load_config_json('archive_report.json')
            for report_data in report_list:
                report = ArchiveReport(
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
        except Exception as e:
            logger.error(f"An error occurred while fetching archive report: {e}")

    def get_list(self):
        return self.archiveReport
