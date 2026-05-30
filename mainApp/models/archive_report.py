from mainApp import logger
from mainApp.config_operations import load_json_config


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
    def __init__(self, reportGroupId=None):
        self.reportGroupId = reportGroupId
        self.archiveReport = []
        try:
            report_list = load_json_config('archive_report.json', default=[])
            if not isinstance(report_list, list):
                report_list = []
            for report_data in report_list:
                if not isinstance(report_data, dict):
                    continue
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
            if self.reportGroupId is not None:
                self.archiveReport = [report for report in self.archiveReport if report.reportGroupId == self.reportGroupId]
        except Exception as e:
            logger.error(f"An error occurred while fetching archive report: {e}")
            self.archiveReport = []

    def get_list(self):
        return self.archiveReport


class GetReportIdsListWhenGroupId:
    def __init__(self, reportGroupId):
        self.reportGroupId = reportGroupId
        self.ids = []
        try:
            report_list = load_json_config('archive_reports.json', default=[])
            if not isinstance(report_list, list):
                report_list = []
            self.ids = [report.get('reportName') for report in report_list if isinstance(report, dict) and report.get('reportGroupId') == self.reportGroupId and report.get('status') == 'Ready']
        except Exception as e:
            logger.error(f"An error occurred while fetching report names: {e}")

    def get_ids(self):
        return self.ids
