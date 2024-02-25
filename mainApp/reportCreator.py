from mainApp.models import Archive, ArchiveReport
import time
from mainApp.routes import app, create_engine, text
from datetime import datetime, timedelta

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
        report = "<td>" + archiveReportConfig.title + "</td>"
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
                if sqlTable[0][0] < archiveReportConfig.minValue:
                    print("za malo")
                    report = report + '<td><progress value="5" max="100">' + str(sqlTable[0][0]) + '</progress></td>'
                elif archiveReportConfig.minValue <= sqlTable[0][0] < archiveReportConfig.okMinValue:
                    print("srednio zamało")
                    report = report + '<td><progress value="25" max="100">' + str(sqlTable[0][0]) + '</progress></td>'
                elif archiveReportConfig.okMinValue <= sqlTable[0][0] <= archiveReportConfig.okMaxValue:
                    print("ok")
                    report = report + '<td><progress value="50" max="100">' + str(sqlTable[0][0]) + '</progress></td>'
                elif archiveReportConfig.okMaxValue < sqlTable[0][0] <= archiveReportConfig.maxValue:
                    print("sredno za duzoa")
                    report = report + '<td><progress value="75" max="100">' + str(sqlTable[0][0]) + '</progress></td>'
                elif archiveReportConfig.maxValue < sqlTable[0][0]:
                    report = report + '<td><progress value="95" max="100">' + str(sqlTable[0][0]) + '</progress></td>'
        report = report + "</tr>"
        return report
        
