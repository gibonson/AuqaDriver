from mainApp.routes import db
from mainApp import logger


class EventScheduler(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    groupId = db.Column(db.String())
    trigger = db.Column(db.String())
    schedulerId = db.Column(db.String())
    day = db.Column(db.Integer()) #(1-31)
    day_of_week = db.Column(db.String()) #mon,tue,wed,thu,fri,sat,sun
    hour = db.Column(db.Integer()) #(0-23)
    minute = db.Column(db.Integer()) #(0-59)
    second = db.Column(db.Integer()) #(0-59)
    schedulerStatus = db.Column(db.String())

    def __init__(self, groupId , trigger, schedulerId , day , day_of_week , hour , minute, second, schedulerStatus):
        self.groupId = groupId
        self.trigger = trigger
        self.schedulerId = schedulerId
        self.day = day
        self.day_of_week = day_of_week
        self.hour = hour
        self.minute = minute
        self.second = second
        self.schedulerStatus = schedulerStatus

class EventSchedulerLister():
    def __init__(self, schedulerStatus = "All"):
        if schedulerStatus == "All":
            try:
                self.EventScheduler = EventScheduler.query.all()
            except Exception as e:
                logger.error(f"An error occurred while fetching EventScheduler: {e}")
                self.EventScheduler = []
        elif schedulerStatus == "Ready":
            try:
                self.EventScheduler = EventScheduler.query.filter(EventScheduler.schedulerStatus=="Ready").all()
            except Exception as e:
                logger.error(f"An error occurred while fetching EventScheduler: {e}")
                self.EventScheduler = []
    def get_list(self):
        return self.EventScheduler

class EventSchedulerAdder():
    def __init__(self, formData: dict, schedulerId):
        self.message = 'EventScheduler added'
        logger.info("Adding EventScheduler to DB")

        try:
            groupId = formData["groupId"][0]
            trigger = formData["trigger"][0]
            schedulerId = schedulerId
            day = formData["day"][0]
            day_of_week = formData["day_of_week"][0]
            hour = formData["hour"][0]
            minute = formData["minute"][0]
            second = formData["second"][0]
            schedulerStatus = formData["schedulerStatus"][0]
            scheduler_to_add = EventScheduler(groupId=groupId, trigger=trigger, schedulerId=schedulerId, day=day, day_of_week=day_of_week, hour=hour, minute=minute, second=second, schedulerStatus=schedulerStatus)
            db.session.add(scheduler_to_add)
            db.session.commit()
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            self.message = "Error: EventScheduler could not be added"
    def __str__(self) -> str:
        return self.message
    

class EventSchedulereManager:
    def __init__(self, id):
        self.id = id
        self.message = ""
        self.EventScheduler = EventScheduler.query.filter_by(id=self.id).first()

    def remove_function_scheduler(self):
        if self.EventScheduler:
            EventScheduler.query.filter(EventScheduler.id == self.id).delete()
            db.session.commit()
            logger.info(f'EventScheduler with ID {self.id} removed')
            self.message = f'EventScheduler with ID {self.id} removed'
        else:
            logger.error(f'EventScheduler with ID {self.id} does not exist')
            self.message = f'EventScheduler with ID {self.id} does not exist'
    
    def change_status(self):
        if self.EventScheduler:
            if self.EventScheduler.schedulerStatus == "Ready":
                self.EventScheduler.schedulerStatus = "Not ready"
                self.message = "EventScheduler status changed to: Not ready"
                logger.info(f'EventScheduler with ID {self.id} status changed')
            elif self.EventScheduler.schedulerStatus == "Not ready":
                self.EventScheduler.schedulerStatus = "Ready"
                logger.info(f'EventScheduler with ID {self.id} status changed')
                self.message = "EventScheduler status changed to: Ready"
            else:
                logger.info(f'EventScheduler with ID {self.id} status error')
                self.message = "Status error!"
            db.session.commit()
        else:
            logger.error(f'EventScheduler with ID {self.id} does not exist')
            self.message = f'EventScheduler with ID {self.id} does not exist'
    
    def __str__(self) -> str:
        return self.message