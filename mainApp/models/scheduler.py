from mainApp.routes import db
from mainApp import logger


class FunctionScheduler(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    functionId = db.Column(db.String())
    trigger = db.Column(db.String())
    schedulerID = db.Column(db.String())
    year = db.Column(db.Integer()) #4-digit year
    month = db.Column(db.Integer()) #(1-12)
    day = db.Column(db.Integer()) #(1-31)
    day_of_week = db.Column(db.String()) #mon,tue,wed,thu,fri,sat,sun
    hour = db.Column(db.Integer()) #(0-23)
    minute = db.Column(db.Integer()) #(0-59)
    second = db.Column(db.Integer()) #(0-59)
    schedulerStatus = db.Column(db.String())

    def __init__(self, functionId , trigger, schedulerID, year , month , day , day_of_week , hour , minute, second, schedulerStatus):
        self.functionId = functionId
        self.trigger = trigger
        self.schedulerID = schedulerID
        self.year = year
        self.month = month
        self.day = day
        self.day_of_week = day_of_week
        self.hour = hour
        self.minute = minute
        self.second = second
        self.schedulerStatus = schedulerStatus

class FunctionSchedulerLister():
    def __init__(self):
        try:
            self.functionScheduler = FunctionScheduler.query.all()
        except Exception as e:
            logger.error(f"An error occurred while fetching FunctionScheduler: {e}")
            self.functionScheduler = []
    def get_list(self):
        return self.functionScheduler
    

class FunctionSchedulereAdder():
    def __init__(self, formData: dict, schedulerID):
        self.message = 'FunctionScheduler added'
        logger.info("Adding FunctionScheduler to DB")

        try:
            functionId = formData["functionId"][0]
            trigger = formData["trigger"][0]
            schedulerID = schedulerID
            year = formData["year"][0]
            month = formData["month"][0]
            day = formData["day"][0]
            day_of_week = formData["day_of_week"][0]
            hour = formData["hour"][0]
            minute = formData["minute"][0]
            second = formData["second"][0]
            schedulerStatus = formData["schedulerStatus"][0]
            scheduler_to_add = FunctionScheduler(functionId=functionId, trigger=trigger, schedulerID=schedulerID, year=year, month=month,
                                             day=day, day_of_week=day_of_week, hour=hour, minute=minute, second=second, schedulerStatus=schedulerStatus)
            db.session.add(scheduler_to_add)
            db.session.commit()
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            self.message = "Error: FunctionScheduler could not be added"
    def __str__(self) -> str:
        return self.message
    

class FunctionSchedulereManager:
    def __init__(self, id):
        self.id = id
        self.message = ""
        self.functionScheduler = FunctionScheduler.query.filter_by(id=self.id).first()

    def remove_function_scheduler(self):
        if self.functionScheduler:
            FunctionScheduler.query.filter(FunctionScheduler.id == self.id).delete()
            db.session.commit()
            logger.info(f'functionScheduler with ID {self.id} removed')
            self.message = f'functionScheduler with ID {self.id} removed'
        else:
            logger.error(f'functionScheduler with ID {self.id} does not exist')
            self.message = f'functionScheduler with ID {self.id} does not exist'
    
    def change_status(self):
        if self.device:
            if self.functionScheduler.schedulerStatus == "Ready":
                self.functionScheduler.schedulerStatus = "Not ready"
                self.message = "functionScheduler status changed to: Not ready"
                logger.info(f'functionScheduler with ID {self.id} status changed')
            elif self.functionScheduler.schedulerStatus == "Not ready":
                self.functionScheduler.schedulerStatus = "Ready"
                logger.info(f'functionScheduler with ID {self.id} status changed')
                self.message = "functionScheduler status changed to: Ready"
            else:
                logger.info(f'functionScheduler with ID {self.id} status error')
                self.message = "Status error!"
            db.session.commit()
        else:
            logger.error(f'functionScheduler with ID {self.id} does not exist')
            self.message = f'functionScheduler with ID {self.id} does not exist'
    
    def __str__(self) -> str:
        return self.message