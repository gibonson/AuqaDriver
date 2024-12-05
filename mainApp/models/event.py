from mainApp.routes import db
from mainApp import logger


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    eventType = db.Column(db.String())
    eventDescription = db.Column(db.String())
    deviceId = db.Column(db.Integer())
    eventLink = db.Column(db.String())
    reportIds = db.Column(db.String())
    eventStatus = db.Column(db.String())


    def __init__(self, eventDescription, eventType, deviceId, eventLink, reportIds, eventStatus):
        self.eventType = eventType
        self.eventDescription = eventDescription
        self.deviceId = deviceId
        self.eventLink = eventLink
        self.reportIds = reportIds
        self.eventStatus = eventStatus


class EventLister():
    def __init__(self):
        try:
            self.events = Event.query.all()
        except Exception as e:
            logger.error(f"An error occurred while fetching devices functions: {e}")
            self.events = []
    def get_list(self):
        return self.events
    

class EventAdder():
    def __init__(self, formData: dict) -> None:
        self.message = 'Event added'
        logger.info("Adding Event to DB")

        try:
            device_id = formData["deviceId"][0]
            event_link = formData["eventLink"][0]
            event_description = formData["eventDescription"][0]
            event_status = formData["eventStatus"][0]
            event_type = formData["eventType"][0]
            report_ids = formData["reportIds"]
            device_function_to_add = Event(deviceId=device_id, eventLink=event_link, eventDescription=event_description, eventStatus=event_status, eventType= event_type, reportIds = str(report_ids))
            db.session.add(device_function_to_add)
            db.session.commit()
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            self.message = "Error: Event could not be added"
    def __str__(self) -> str:
        return self.message
    

class EventManager:
    def __init__(self, id):
        self.id = id
        self.message = ""
        self.event = Event.query.filter_by(id=self.id).first()
        self.eventType = self.event.eventType

    def remove_event(self):
        if self.event:
            Event.query.filter(Event.id == self.id).delete()
            db.session.commit()
            logger.info(f'Event with ID {self.id} removed')
            self.message = f'Event with ID {self.id} removed'
        else:
            logger.error(f'Event with ID {self.id} does not exist')
            self.message = f'Event with ID {self.id} does not exist'
    

    def edit_event(self, formData: dict):
        if self.event:
            try:
                self.event.eventDescription = formData["eventDescription"][0]
                self.event.deviceId = formData["deviceId"][0]
                self.event.eventLink = formData["eventLink"][0]
                self.event.reportIds = str(formData["reportIds"])
                self.event.eventStatus = formData["eventStatus"][0]
                self.event.eventType = formData["eventType"][0]
                db.session.commit()
                self.message = f"Event with ID {self.id} successfully updated"
                logger.info(self.message)
            except Exception as e:
                db.session.rollback()
                self.message = f"An error occurred while updating event: {e}"
                logger.error(self.message)
        else:
            self.message = f"Event with ID {self.id} does not exist"
            logger.error(self.message)

    def change_status(self):
        if self.event:
            if self.event.eventStatus == "Ready":
                self.event.eventStatus = "Not ready"
                self.message = "Event status changed to: Not ready"
                logger.info(f'Event with ID {self.id} status changed')
            elif self.event.eventStatus == "Not ready":
                self.event.eventStatus = "Ready"
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