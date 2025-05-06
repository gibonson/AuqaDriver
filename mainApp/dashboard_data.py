import os
from datetime import datetime
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

    def get_date(self):
        """
        Zwraca aktualną datę w formacie YYYY-MM-DD.
        """
        return datetime.now().strftime("%Y-%m-%d")

    def get_time(self):
        """
        Zwraca aktualny czas w formacie HH:MM:SS.
        """
        return datetime.now().strftime("%H:%M:%S")

    def get_placeholder_value(self, placeholder):
        """
        Obsługuje dowolny placeholder i zwraca jego wartość.

        Args:
            placeholder (str): Nazwa placeholdera.

        Returns:
            str: Wartość placeholdera lub "UnknownValue", jeśli nieobsługiwany.
        """
        if placeholder == "date":
            return self.get_date()
        elif placeholder == "time":
            return self.get_time()
        elif placeholder == "dbSize":
            return self.getDbSizeKB()
        else:
            return "UnknownValue"