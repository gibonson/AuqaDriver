from mainApp.models.model import ArchiveFunctions
from mainApp.models.archive import Archive
from mainApp.models.archive_report import ArchiveReport
import time
from mainApp.routes import app, create_engine, text
from datetime import datetime, timedelta
from mainApp import app, db, flash
from mainApp.email_operations import emailSender


class ReportCreator:

    def createAll(self):
        archiveReportConfig = ArchiveReport.query.all()
        reportAll = '<style>table, th, td {  border: 1px solid black;  border-collapse: collapse;}"<table style="width:100%"></style><table style="width:50%">'
        for report in archiveReportConfig:
            print(report.id)
            id = str(report.id)
            reportAll = reportAll + ReportCreator.create(self, id)

        reportAll = reportAll + '</table>'
        return reportAll


    def create(self, id):
        archiveReportConfig = ArchiveReport.query.filter_by(id = id).first()
        dateTo = time.time()
        dateFrom = dateTo - (archiveReportConfig.timerRangeHours * 60 * 60)
        dateFrom = str(dateFrom)
        print(dateFrom)
        formatedDateTo =  datetime.fromtimestamp(int(float(dateTo)))
        formatedDateFrom =  datetime.fromtimestamp(int(float(dateFrom)))
        print(formatedDateTo)
        print(formatedDateFrom)
        report = "<tr>"
        report = report + "<td>" + archiveReportConfig.title + "</td>"
        report = report + "<td>" + archiveReportConfig.description + "</td>"
        engine = create_engine(app.config["SQLALCHEMY_DATABASE_URI"], echo=True)
        with engine.connect() as conn:
            if archiveReportConfig.avgOrSum == "avg":
                report = report + "<td>średnia</td>"
                querry = ' select round(avg(value),2) FROM archive WHERE timestamp > "'+ dateFrom +'" AND deviceName ="' + archiveReportConfig.deviceName + '" AND addInfo ="' + archiveReportConfig.addInfo + '" AND type ="' + archiveReportConfig.type + '" AND deviceIP ="' + archiveReportConfig.deviceIP + '";'
            elif archiveReportConfig.avgOrSum == "sum":
                report = report + "<td>suma</td>"
                querry = ' select round(sum(value),2) FROM archive WHERE timestamp > "'+ dateFrom +'" AND deviceName ="' + archiveReportConfig.deviceName + '" AND addInfo ="' + archiveReportConfig.addInfo + '" AND type ="' + archiveReportConfig.type + '" AND deviceIP ="' + archiveReportConfig.deviceIP + '";'
            elif archiveReportConfig.avgOrSum == "min":
                report = report + "<td>min</td>"
                querry = ' select round(min(value),2) FROM archive WHERE timestamp > "'+ dateFrom +'" AND deviceName ="' + archiveReportConfig.deviceName + '" AND addInfo ="' + archiveReportConfig.addInfo + '" AND type ="' + archiveReportConfig.type + '" AND deviceIP ="' + archiveReportConfig.deviceIP + '";'
            elif archiveReportConfig.avgOrSum == "max":
                report = report + "<td>max</td>"
                querry = ' select round(max(value),2) FROM archive WHERE timestamp > "'+ dateFrom +'" AND deviceName ="' + archiveReportConfig.deviceName + '" AND addInfo ="' + archiveReportConfig.addInfo + '" AND type ="' + archiveReportConfig.type + '" AND deviceIP ="' + archiveReportConfig.deviceIP + '";'
            else:
                querry = ""
            sqlSelect = conn.execute(text(querry))
            # print(sqlSelect)
            sqlTable = []
            for row in sqlSelect:
                print(row)
                sqlTable.append(row)
            print(sqlTable[0][0])
            if sqlTable[0][0] is None:
                report = report + "<td>błąd</td>"
            else:
                report = report + "<td>" + str(sqlTable[0][0]) + " " + archiveReportConfig.type + "</td>"
                if sqlTable[0][0] < archiveReportConfig.minValue: #za malo
                    report = report + "<td><span style='height: 20px;  width: 20px;  background-color: red;  border-radius: 50%;  display: inline-block;'></span>↓↓</td>"
                elif archiveReportConfig.minValue <= sqlTable[0][0] < archiveReportConfig.okMinValue: #srednio za malo
                    report = report + "<td><span style='height: 20px;  width: 20px;  background-color: yellow;  border-radius: 50%;  display: inline-block;'></span>↓</td>"
                elif archiveReportConfig.okMinValue <= sqlTable[0][0] <= archiveReportConfig.okMaxValue: #ok
                    report = report + "<td><span style='height: 20px;  width: 20px;  background-color: green;  border-radius: 50%;  display: inline-block;'></span>↔</td>"
                elif archiveReportConfig.okMaxValue < sqlTable[0][0] <= archiveReportConfig.maxValue: # srednio za duzo
                    report = report + "<td><span style='height: 20px;  width: 20px;  background-color: yellow;  border-radius: 50%;  display: inline-block;'></span>↑</td>"
                elif archiveReportConfig.maxValue < sqlTable[0][0]: #za duzo
                    report = report + "<td><span style='height: 20px;  width: 20px;  background-color: red;  border-radius: 50%;  display: inline-block;'></span>↑↑</td>"
        report = report + "</tr>"
        return report
        
class ReportSender:
    def __init__(self, functionId):
        print(functionId)
        functionId = str(functionId).replace("R","")
        print(functionId)
        self.functionId = functionId

    def collectAndSend(self):
        with app.app_context():
            archiveFunctions = ArchiveFunctions.query.filter_by(id=self.functionId).first()
            print(archiveFunctions.archiveReportIds)
            idToReportList = archiveFunctions.archiveReportIds.replace("[","").replace("]","").replace(" ","")
            print(idToReportList)
            idToReportList = idToReportList.split(',')
            reportAll = '<html><body><style>table, th, td {  border: 1px solid black;  border-collapse: collapse;}"<table style="width:100%"></style><table style="width:50%">'

            for idToReport in idToReportList:
                print(idToReport)
                archiveReportConfig = ArchiveReport.query.filter_by(id = idToReport).first()
                print(archiveReportConfig)
                print(archiveReportConfig.id)
                id = str(archiveReportConfig.id)
                reportAll = reportAll + ReportCreator.create(self, id)

            reportAll = reportAll + '</table></body></html>'
            print(reportAll)
            emailSender( "raport", reportAll)
