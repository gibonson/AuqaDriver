from mainApp.routes import db
from mainApp import logger


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    deviceId = db.Column(db.Integer())
    eventLink = db.Column(db.String())
    eventDescription = db.Column(db.String())
    eventStatus = db.Column(db.String())

    def __init__(self, deviceId, eventLink, eventDescription, eventStatus):
        self.deviceId = deviceId
        self.eventLink = eventLink
        self.eventDescription = eventDescription
        self.eventStatus = eventStatus


class DeviceFunctionsLister():
    def __init__(self):
        try:
            self.deviceFunctions = Event.query.all()
        except Exception as e:
            logger.error(f"An error occurred while fetching devices functions: {e}")
            self.deviceFunctions = []
    def get_list(self):
        return self.deviceFunctions
    

class DeviceFunctionAdder():
    def __init__(self, formData: dict) -> None:
        self.message = 'Event added'
        logger.info("Adding Event to DB")

        try:
            device_id = formData["deviceId"][0]
            event_link = formData["eventLink"][0]
            event_description = formData["eventDescription"][0]
            event_status = formData["eventStatus"][0]
            device_function_to_add = Event(deviceId=device_id, eventLink=event_link, eventDescription=event_description, eventStatus=event_status)
            db.session.add(device_function_to_add)
            db.session.commit()
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            self.message = "Error: Event could not be added"
    def __str__(self) -> str:
        return self.message
    

class DeviceFunctionsManager:
    def __init__(self, id):
        self.id = id
        self.message = ""
        self.deviceFunction = Event.query.filter_by(id=self.id).first()

    def remove_device_function(self):
        if self.deviceFunction:
            Event.query.filter(Event.id == self.id).delete()
            db.session.commit()
            logger.info(f'Event with ID {self.id} removed')
            self.message = f'Event with ID {self.id} removed'
        else:
            logger.error(f'Event with ID {self.id} does not exist')
            self.message = f'Event with ID {self.id} does not exist'
    
    def change_status(self):
        if self.deviceFunction:
            if self.deviceFunction.eventStatus == "Ready":
                self.deviceFunction.eventStatus = "Not ready"
                self.message = "Event status changed to: Not ready"
                logger.info(f'Event with ID {self.id} status changed')
            elif self.deviceFunction.eventStatus == "Not ready":
                self.deviceFunction.eventStatus = "Ready"
                logger.info(f'Event with ID {self.id} status changed')
                self.message = "Event status changed to: Ready"
            else:
                logger.info(f'Event with ID {self.id} status error')
                self.message = "Status error!"
            db.session.commit()
        else:
            logger.error(f'Event with ID {self.id} does not exist')
            self.message = f'Event with ID {self.id} does not exist'

    def __str__(self) -> str:
        return self.message