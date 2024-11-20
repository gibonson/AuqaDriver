from datetime import datetime
import time
from mainApp import app, logger
from mainApp.routes import create_engine, text
from mainApp.models.archive_report import ArchiveReport
from mainApp.models.event import Event
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
                        <th>Name</th>
                        <th>Description</th>
                        <th>Time Range</th>
                        <th>Type</th>
                        <th>Value</th>
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
    HTML_TOO_LOW = "<span style='height: 20px;  width: 20px;  background-color: red;  border-radius: 50%;  display: inline-block;'></span>↓↓"
    HTML_LOW = "<span style='height: 20px;  width: 20px;  background-color: yellow;  border-radius: 50%;  display: inline-block;'></span>↓"
    HTML_OPTIMAL = "<span style='height: 20px;  width: 20px;  background-color: green;  border-radius: 50%;  display: inline-block;'></span>↔"
    HTML_HIGH = "<span style='height: 20px;  width: 20px;  background-color: yellow;  border-radius: 50%;  display: inline-block;'></span>↑"
    HTML_TOO_HIGH = "<span style='height: 20px;  width: 20px;  background-color: red;  border-radius: 50%;  display: inline-block;'></span>↑↑"
    HTML_ROW_START = "<tr>"
    HTML_ROW_END = "</tr>"
    HTML_COLUMN_START = "<td>"
    HTML_COLUMN_END =  "</td>"

    @staticmethod
    def row_creator(title, description, time_range, avgOrSum, value, unit_type, indicator):
        tableText = f'''
                    {HtmlBuilder.HTML_ROW_START}
                        {HtmlBuilder.HTML_COLUMN_START}{title}{HtmlBuilder.HTML_COLUMN_END}
                        {HtmlBuilder.HTML_COLUMN_START}{description}{HtmlBuilder.HTML_COLUMN_END}
                        {HtmlBuilder.HTML_COLUMN_START}{time_range} h{HtmlBuilder.HTML_COLUMN_END}
                        {HtmlBuilder.HTML_COLUMN_START}{avgOrSum}{HtmlBuilder.HTML_COLUMN_END}
                        {HtmlBuilder.HTML_COLUMN_START}{value} {unit_type}{HtmlBuilder.HTML_COLUMN_END}
                        {HtmlBuilder.HTML_COLUMN_START}{indicator}{HtmlBuilder.HTML_COLUMN_END}
                    {HtmlBuilder.HTML_ROW_END}
        '''
        return tableText


class ReportCreator:

    def create_all(self):
        archive_report_id_list = ArchiveReport.query.all()
        reportAll =  HtmlBuilder.HTML_START
        for archive_report_id in archive_report_id_list:
            reportAll += self.create_one_line(str(archive_report_id.id))
        reportAll += HtmlBuilder.HTML_END
        # logger.debug(reportAll)
        return reportAll


    def create_from_list(self, archive_report_id_list):
        reportAll =  HtmlBuilder.HTML_START
        for archive_report_id in archive_report_id_list:
            reportAll += self.create_one_line(archive_report_id)
        reportAll += HtmlBuilder.HTML_END
        return reportAll


    def create_one_line(self, id):
        archiveReportConfig = ArchiveReport.query.filter_by(id = id).first()
        dateTo = time.time()
        dateFrom = dateTo - (archiveReportConfig.timerRangeHours * 60 * 60)
        dateFrom = str(dateFrom)
        formatedDateTo =  datetime.fromtimestamp(int(float(dateTo)))
        formatedDateFrom =  datetime.fromtimestamp(int(float(dateFrom)))
        logger.debug(f"date from: {formatedDateTo}")
        logger.debug(f"date from: {formatedDateFrom}")
        time_range = archiveReportConfig.timerRangeHours
        indicator = ""
        unit_type = ""
        condition_type = ""
        value = ""
        engine = create_engine(app.config["SQLALCHEMY_DATABASE_URI"], echo=True)
        with engine.connect() as conn:
            if archiveReportConfig.avgOrSum == "avg":
                condition_type = HtmlBuilder.HTML_AVG
                query = f'SELECT ROUND(AVG(value), 2) FROM archive WHERE timestamp > "{dateFrom}" AND deviceName ="{archiveReportConfig.deviceName}" AND addInfo ="{archiveReportConfig.addInfo}" AND type ="{archiveReportConfig.type}" AND deviceIP ="{archiveReportConfig.deviceIP}";'
            elif archiveReportConfig.avgOrSum == "sum":
                condition_type = HtmlBuilder.HTML_SUM
                query = f'SELECT ROUND(SUM(value), 2) FROM archive WHERE timestamp > "{dateFrom}" AND deviceName ="{archiveReportConfig.deviceName}" AND addInfo ="{archiveReportConfig.addInfo}" AND type ="{archiveReportConfig.type}" AND deviceIP ="{archiveReportConfig.deviceIP}";'
            elif archiveReportConfig.avgOrSum == "min":
                condition_type = HtmlBuilder.HTML_MIN
                query = f'SELECT ROUND(MIN(value), 2) FROM archive WHERE timestamp > "{dateFrom}" AND deviceName ="{archiveReportConfig.deviceName}" AND addInfo ="{archiveReportConfig.addInfo}" AND type ="{archiveReportConfig.type}" AND deviceIP ="{archiveReportConfig.deviceIP}";'
            elif archiveReportConfig.avgOrSum == "max":
                condition_type = HtmlBuilder.HTML_MAX
                query = f'SELECT ROUND(MAX(value), 2) FROM archive WHERE timestamp > "{dateFrom}" AND deviceName ="{archiveReportConfig.deviceName}" AND addInfo ="{archiveReportConfig.addInfo}" AND type ="{archiveReportConfig.type}" AND deviceIP ="{archiveReportConfig.deviceIP}";'
            else:
                query = ""
            sqlSelect = conn.execute(text(query ))
            sqlTable = []
            for row in sqlSelect:
                sqlTable.append(row)
            value = sqlTable[0][0]

            if value is None:
                value = HtmlBuilder.HTML_VALUE_ERROR
            else:
                unit_type = archiveReportConfig.type
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
            table_row = HtmlBuilder.row_creator(title = archiveReportConfig.title, description = archiveReportConfig.description, time_range = time_range, avgOrSum = condition_type, value = value, unit_type = unit_type ,indicator = indicator)
        return table_row
        
class ReportSender:
    def __init__(self, functionId):
        self.functionId = str(functionId).replace("R","")

    def collect_and_send(self):
        with app.app_context():
            event = Event.query.filter_by(id=self.functionId).first()
            logger.debug("Report ids to schow: " + event.archiveReportIds)
            archive_report_id_list = event.archiveReportIds.replace("[","").replace("]","").replace(" ","").replace("'","").split(',')
            reportCreator = ReportCreator()
            report = reportCreator.create_from_list(archive_report_id_list=archive_report_id_list)
            emailSender( "raport", report)