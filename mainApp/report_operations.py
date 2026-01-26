from datetime import datetime
import time
from mainApp import app, logger
from mainApp.routes import create_engine, text
from mainApp.models.archive_report import ArchiveReport
from mainApp.email_operations import emailSender

class HtmlBuilder:
    HTML_START = '''
            <!DOCTYPE html>
            <html>
                <body>
                    <style>
                        table {
                            color: #000000;
                            width: 50%;
                            border-collapse: collapse;
                            border-radius: 15px;
                            overflow: hidden;
                            margin-left:  auto;
                            margin-right:  auto;
                        }
                        th, td {
                            border: 1px solid black;
                            padding: 10px;
                        }
                        th {
                            background-color: #e6e6e6;
                        }
                        td {
                            background-color: #f9f9f9;
                        }
                        h2 {
                            font-family: Arial, sans-serif;
                            color: grey;
                        }
                    </style>           
                    <h2>Home system report</h2>
                    <table>
                    <tr>
                        <th>Title</th>
                        <th>Message</th>
                        <th>Value</th>
                        <th>Unit</th>
                        <th>Indicator</th>
                    </tr>
            '''
    HTML_END = '''
                    </table>
                </body>
            </html>
        '''
    HTML_AVG = "Average"
    HTML_SUM = "Sum"
    HTML_MIN = "Minimum"
    HTML_MAX = "Maximum"
    HTML_VALUE_ERROR = "Empty value"
    HTML_SQL_ERROR = "SQL Error"
    HTML_TOO_LOW = "<span style='height: 20px;  width: 20px;  background-color: darkblue;  border-radius: 50%;  display: inline-block;'></span>"
    HTML_LOW = "<span style='height: 20px;  width: 20px;  background-color: blue;  border-radius: 50%;  display: inline-block;'></span>"
    HTML_OPTIMAL = "<span style='height: 20px;  width: 20px;  background-color: green;  border-radius: 50%;  display: inline-block;'></span>"
    HTML_HIGH = "<span style='height: 20px;  width: 20px;  background-color: yellow;  border-radius: 50%;  display: inline-block;'></span>"
    HTML_TOO_HIGH = "<span style='height: 20px;  width: 20px;  background-color: red;  border-radius: 50%;  display: inline-block;'></span>"
    HTML_ROW_START = "<tr>"
    HTML_ROW_END = "</tr>"
    HTML_COLUMN_START = "<td>"
    HTML_COLUMN_END =  "</td>"

    @staticmethod
    def row_creator(title, message, unit, value ,indicator):
        tableText = f'''
                    {HtmlBuilder.HTML_ROW_START}
                        {HtmlBuilder.HTML_COLUMN_START}{title}{HtmlBuilder.HTML_COLUMN_END}
                        {HtmlBuilder.HTML_COLUMN_START}{message}{HtmlBuilder.HTML_COLUMN_END}
                        {HtmlBuilder.HTML_COLUMN_START}{value}{HtmlBuilder.HTML_COLUMN_END}
                        {HtmlBuilder.HTML_COLUMN_START}{unit}{HtmlBuilder.HTML_COLUMN_END}
                        {HtmlBuilder.HTML_COLUMN_START}{indicator}{HtmlBuilder.HTML_COLUMN_END}
                    {HtmlBuilder.HTML_ROW_END}
        '''
        return tableText


class ReportCreator:
    def __init__(self, archive_report_id_list = None):
        self.archive_report_id_list = archive_report_id_list

    def create_all(self):
        archive_report_id_list = ArchiveReport.query.all()
        reportAll =  HtmlBuilder.HTML_START
        for archive_report_id in archive_report_id_list:
            reportAll += self.create_one_line(str(archive_report_id.id))
        reportAll += HtmlBuilder.HTML_END
        # logger.debug(reportAll)
        return reportAll


    def create_from_list(self): 
        reportAll =  HtmlBuilder.HTML_START
        for archive_report_id in self.archive_report_id_list:
            reportAll += self.create_one_line(archive_report_id)
        reportAll += HtmlBuilder.HTML_END
        return reportAll


    def create_one_line(self, id):
        archiveReportConfig = ArchiveReport.query.filter_by(id = id).first()
        value = ""
        if not archiveReportConfig:
            table_row = "report id not found"
        else:
            engine = create_engine(app.config["SQLALCHEMY_DATABASE_URI"], echo=True)
            with engine.connect() as conn:
                query = archiveReportConfig.queryString
                try:
                    sqlSelect = conn.execute(text(query))
                    sqlTable = []
                    for row in sqlSelect:
                        sqlTable.append(row)
                    value = sqlTable[0][0]
                except Exception as e:
                    logger.error(f"Error executing query: {e}")
                    value = None

                if value is None:
                    value = HtmlBuilder.HTML_VALUE_ERROR
                    indicator = HtmlBuilder.HTML_SQL_ERROR
                else:
                    unit = archiveReportConfig.unit
                    if value < archiveReportConfig.minValue:
                        indicator = HtmlBuilder.HTML_TOO_LOW
                    elif archiveReportConfig.minValue <= value < archiveReportConfig.okMinValue:
                        indicator = HtmlBuilder.HTML_LOW
                    elif archiveReportConfig.okMinValue <= value <= archiveReportConfig.okMaxValue:
                        indicator = HtmlBuilder.HTML_OPTIMAL
                    elif archiveReportConfig.okMaxValue < value <= archiveReportConfig.maxValue:
                        indicator = HtmlBuilder.HTML_HIGH
                    elif archiveReportConfig.maxValue < value:
                        indicator = HtmlBuilder.HTML_TOO_HIGH
                table_row = HtmlBuilder.row_creator(title = archiveReportConfig.title, message = archiveReportConfig.message, value= value, unit = archiveReportConfig.unit ,indicator = indicator)
        return table_row
        
class ReportSender:
    def __init__(self, reportIds):
        self.reportIds = reportIds

    def collect_and_send(self):
        with app.app_context():
            reportCreator = ReportCreator(archive_report_id_list= self.reportIds)
            report = reportCreator.create_from_list()
            logger.debug(f"Message to sent: {report}")
            emailSender( "raport", report)