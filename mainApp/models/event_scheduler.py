import json
import os

from mainApp.config_operations import get_scheduler_config_path
from mainApp import logger


class EventScheduler():
    def __init__(
        self,
        schedulerName,
        schedulerDescription=None,
        reportList=None,
        eventList=None,
        trigger=None,
        day=None,
        day_of_week=None,
        hour=None,
        minute=None,
        second=None,
        schedulerStatus=None,
    ):
        self.schedulerName = schedulerName
        self.schedulerDescription = schedulerDescription
        self.ReportList = reportList or []
        self.EventList = eventList or []
        self.trigger = trigger
        self.day_of_week = day_of_week
        self.day = day
        self.hour = hour
        self.minute = minute
        self.second = second
        self.schedulerStatus = schedulerStatus


class EventSchedulerLister():
    def __init__(self):
        self.eventScheduler = []
        try:
            config_path = get_scheduler_config_path()
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as config_file:
                    scheduler_list = json.load(config_file)
                for scheduler_data in scheduler_list:
                    scheduler = EventScheduler(
                        schedulerName=scheduler_data.get('schedulerName'),
                        schedulerDescription=scheduler_data.get('schedulerDescription'),
                        reportList=scheduler_data.get('reportList'),
                        eventList=scheduler_data.get('eventList'),
                        trigger=scheduler_data.get('trigger'),
                        day=scheduler_data.get('day'),
                        day_of_week=scheduler_data.get('day_of_week'),
                        hour=scheduler_data.get('hour'),
                        minute=scheduler_data.get('minute'),
                        second=scheduler_data.get('second'),
                        schedulerStatus=scheduler_data.get('schedulerStatus'),
                    )
                    self.eventScheduler.append(scheduler)
        except Exception as e:
            logger.error(f"An error occurred while fetching EventScheduler: {e}")

    def get_list(self):
        return self.eventScheduler
