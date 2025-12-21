from mainApp.routes import db
from mainApp import logger


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    eventAddress = db.Column(db.String())
    eventDescription = db.Column(db.String())
    eventPayload = db.Column(db.String())
    eventGroupId = db.Column(db.Integer())
    eventStatus = db.Column(db.String())


    def __init__(self, eventAddress, eventDescription, eventPayload, eventGroupId, eventStatus):
        self.eventAddress = eventAddress
        self.eventDescription = eventDescription
        self.eventPayload = eventPayload
        self.eventGroupId = eventGroupId
        self.eventStatus = eventStatus


class EventLister():
    def __init__(self, eventGroupId=None):
        self.eventGroupId = eventGroupId
        self.events = []
        try:
            if self.eventGroupId:
                self.events = Event.query.filter_by(eventGroupId=self.eventGroupId).all()
            else:
                self.events = Event.query.all()
        except Exception as e:
            logger.error(f"An error occurred while fetching devices functions: {e}")
    def get_list(self):
        return self.events
    

class GetEventIdsListWhenGroupId():
    def __init__(self, eventGroupId):
        self.eventGroupId = eventGroupId
        self.ids = []
        try:
            lsitNoFlat = db.session.query(Event.id).filter(Event.eventGroupId == self.eventGroupId, Event.eventStatus == 'Ready').all()
            self.ids = [row[0] for row in lsitNoFlat]
        except Exception as e:
            logger.error(f"An error occurred while fetching event IDs: {e}")
    def get_ids(self):
        return self.ids 
    
    

class EventAdder():
    def __init__(self, formData: dict) -> None:
        self.message = 'Event added'
        logger.info("Adding Event to DB")

        try:
            eventAddress = formData["eventAddress"][0]
            eventDescription = formData["eventDescription"][0]
            eventPayload = formData["eventPayload"][0]
            eventGroupId = formData["eventGroupId"][0]
            eventStatus = formData["eventStatus"][0]
            device_function_to_add = Event(eventAddress=eventAddress, eventDescription=eventDescription, eventPayload=eventPayload, eventGroupId=eventGroupId, eventStatus=eventStatus)
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
        print("editform")
        if self.event:
            try:
                self.event.eventAddress = formData["eventAddress"][0]
                self.event.eventDescription = formData["eventDescription"][0]
                self.event.eventPayload = formData["eventPayload"][0]
                self.event.eventGroupId = formData["eventGroupId"][0]
                self.event.eventStatus = formData["eventStatus"][0]
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