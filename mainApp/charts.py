from mainApp import app, logger, db
from mainApp.models.archive import Archive
from sqlalchemy import func, extract, desc
from datetime import datetime, timedelta


from sqlalchemy import func, extract


class Table:
    def __init__(self, delta, type) -> None:
        self.delta = delta
        self.type = type
        self.final_results = {}

    def reportGenerator(self):
        today = datetime.now().date()
        print(today.strftime('%Y-%m-%d'))
        for day in range(self.delta):
            print(day)
            start_date = today - timedelta(days=day)
            self.final_results[start_date.strftime('%Y-%m-%d')] = 0

        with app.app_context():
            results = (
                db.session.query(
                    func.strftime(
                        '%Y-%m-%d', func.datetime(Archive.timestamp, 'unixepoch')).label('day'),
                    func.avg(Archive.value).label('average_value')
                )
                .filter(
                    # Archive.type.like(self.type),
                    Archive.type == self.type,
                    func.strftime(
                        '%Y-%m-%d', func.datetime(Archive.timestamp, 'unixepoch')) >= start_date
                )
                .group_by(func.strftime('%Y-%m-%d', func.datetime(Archive.timestamp, 'unixepoch')))
                .order_by('day')
                .all()
            )

            for result in results:
                print(str(result[0]) + " " + str(result[1]))
                self.final_results[result[0]] = round(result[1], 2)

            for final_result in self.final_results:
                print(
                    f"klucz: {final_result} wartosc:{self.final_results[final_result]}")

    def get_final_results(self):
        return self.final_results
