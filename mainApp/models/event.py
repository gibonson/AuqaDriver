from mainApp import logger
from mainApp.config_operations import load_config_json


class Event:
    def __init__(
        self,
        eventName,
        eventAddress,
        eventDescription,
        eventPayload,
        eventType,
        eventStatus,
    ):
        self.eventName = eventName
        self.eventAddress = eventAddress
        self.eventDescription = eventDescription
        self.eventPayload = eventPayload
        self.eventType = eventType
        self.eventStatus = eventStatus


class EventManager:
    def __init__(self):
        self.events = []
        try:
            event_list = load_config_json("event.json")
            for event_data in event_list:
                event = Event(
                    eventName=event_data.get("eventName"),
                    eventAddress=event_data.get("eventAddress"),
                    eventDescription=event_data.get("eventDescription"),
                    eventType=event_data.get("eventType"),
                    eventPayload=event_data.get("eventPayload"),
                    eventStatus=event_data.get("eventStatus"),
                )
                self.events.append(event)
        except Exception as e:
            logger.error(f"An error occurred while fetching devices functions: {e}")

    def get_all(self):
        return self.events

    def get_by_name(self, eventName):
        for event in self.events:
            if event.eventName == eventName:
                return event
        return None
