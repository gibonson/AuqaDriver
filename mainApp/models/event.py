import json
import os

from mainApp.config_operations import get_config_file_path
from mainApp import logger


class Event:
    def __init__(
        self,
        eventName,
        eventAddress,
        eventDescription,
        eventPayload,
        eventStatus
    ):
        self.eventName = eventName
        self.eventAddress = eventAddress
        self.eventDescription = eventDescription
        self.eventPayload = eventPayload
        self.eventStatus = eventStatus

   
    
class EventListerJson():
    def __init__(self):
        self.events = []
        try:
            config_path = get_config_file_path('events.json')
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as config_file:
                    event_list = json.load(config_file)
                for event_data in event_list:
                        event = Event(
                            eventName=event_data.get('eventName'),
                            eventAddress=event_data.get('eventAddress'),
                            eventDescription=event_data.get('eventDescription'),
                            eventPayload=event_data.get('eventPayload'),
                            eventStatus=event_data.get('eventStatus')
                        )
                        self.events.append(event)
        except Exception as e:
            logger.error(f"An error occurred while fetching devices functions: {e}")

    def get_list(self):
        return self.events