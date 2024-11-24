import os
from sqlalchemy import create_engine, text
from mainApp.routes import app


class DashboardData:
    def __init__(self):
        DBFile = os.path.abspath(os.path.dirname(__file__)) + "/../userFiles/db.sqlite"
        self.dbSizeKB = os.path.getsize(DBFile) / 1024
        engine = create_engine(app.config["SQLALCHEMY_DATABASE_URI"], echo=True)
        with engine.connect() as conn:
                sqlSelect = conn.execute(text(
                    'select deviceIP, deviceName, type, addInfo, count(value) as number_of_queries, round(avg(value),2) as average FROM archive GROUP BY deviceIP, type, addInfo'))
                self.sqlTable = []
                for row in sqlSelect:
                    self.sqlTable.append(row)

    def getSqlTable(self):
         return self.sqlTable

    def getDbSizeKB(self):
         return self.dbSizeKB