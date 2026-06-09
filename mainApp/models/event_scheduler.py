from mainApp import logger
from mainApp.config_operations import load_config_json


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
        self.reportList = reportList or []
        self.eventList = eventList or []
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
            scheduler_list = load_config_json('event_scheduler.json')
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
    
    
class EventSchedulerGetBySchedulerName():
    def __init__(self, schedulerName):
        self.schedulerName = schedulerName

    def get_event(self):
        eventSchedulerListerist = EventSchedulerLister().get_list()
        for eventScheduler in eventSchedulerListerist:
            if eventScheduler.schedulerName == self.schedulerName:
                print(eventScheduler)
                return eventScheduler
        return None
