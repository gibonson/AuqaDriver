from mainApp import app, logger
from mainApp.models.archive import Archive
from sqlalchemy import func, extract, desc
from datetime import datetime, timedelta

class Table:
    def __init__(self, delta) -> None:
        self.delta = delta

    def reportGenerator(self):
        today = datetime.now().date()
        start_date = today - timedelta(days=self.delta)
        with app.app_context():
            results = Archive.query.with_entities(
                func.date(Archive.timestamp).label('day'),  # Wyodrębnienie daty z timestampu
                func.avg(Archive.value).label('average_temp')  # Obliczenie średniej temperatury
            ).filter(
                Archive.timestamp >= start_date,  # Filtr dla ostatnich 10 dni
                Archive.timestamp < today + timedelta(days=1),  # Filtr do dzisiejszego dnia włącznie
                Archive.type == 'stC'  # Warunek, że type musi być równe 'stC'
            ).group_by(
                func.date(Archive.timestamp)  # Grupowanie po dacie
            ).order_by(
                desc('day')  # Sortowanie wyników od najnowszych do najstarszych
            ).all()
            # results = Archive.query.filter(Archive.type == '%').all()
            # print(f"Liczba rekordów z type='stC': {len(results)}")
            print(results)

            # Wyświetlenie wyników
            for result in results:
                print(f"Średnia temperatura dla {result.day}: {result.average_temp:.2f}°C")