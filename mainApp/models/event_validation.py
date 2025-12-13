from mainApp.routes import db
from mainApp import logger

class Validation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String())
    deviceIP = db.Column(db.String())
    deviceName = db.Column(db.String())
    addInfo = db.Column(db.String())
    type = db.Column(db.String())
    condition = db.Column(db.String()) # less more equal 
    value = db.Column(db.Integer())
    actionType = db.Column(db.String()) # email, event, ignore
    eventId = db.Column(db.String())
    message = db.Column(db.String())
    status = db.Column(db.String())# Ready, Not ready
        

    def __init__(self, description, deviceIP, deviceName, addInfo, type, condition, value, status, actionType, eventId, message):
        self.description = description
        self.deviceIP = deviceIP
        self.deviceName = deviceName
        self.addInfo = addInfo
        self.type = type
        self.condition = condition
        self.value = value
        self.status = status
        self.actionType = actionType
        self.eventId = eventId
        self.message = message

class ValidationLister():
    def __init__(self, status = "All", actionType = "All"):
        self.Validation = []  # ensure attribute always exists
        try:
            if status == "All" and actionType == "All":
                self.Validation = Validation.query.all()
            if status == "Ready" and actionType == "All":
                self.Validation = Validation.query.all()
            elif status == "Ready" and actionType == "email":
                self.Validation = Validation.query.filter(Validation.status == "Ready", Validation.actionType == "email").all()
            elif status == "Ready" and actionType == "event":
                self.Validation = Validation.query.filter(Validation.status == "Ready", Validation.actionType == "event").all()
            elif status == "Ready" and actionType == "ignore":
                self.Validation = Validation.query.filter(Validation.status == "Ready", Validation.actionType == "ignore").all()
            else:
                # fallback: apply filters if provided
                query = Validation.query
                if status != "All":
                    query = query.filter(Validation.status == status)
                if actionType != "All":
                    query = query.filter(Validation.actionType == actionType)
                self.Validation = query.all()
        except Exception as e:
            logger.error(f"An error occurred while fetching Validation: {e}")
            self.Validation = []
        
    def get_list(self):
        return self.Validation
    


class ValidationAdder():
    def __init__(self, formData: dict):
        self.message = 'Validation added'
        logger.info("Validation noaddes to DB")
        
        try:
            description = formData["description"][0]
            deviceIP = formData["deviceIP"][0]
            deviceName = formData["deviceName"][0]
            addInfo = formData["addInfo"][0]
            type = formData["type"][0]
            condition = formData["condition"][0]
            value = formData["value"][0]
            status = formData["status"][0]
            actionType = formData["actionType"][0]
            eventId = formData["eventId"][0]
            message = formData["message"][0]
            Validation_to_add = Validation(description=description, deviceIP=deviceIP, deviceName=deviceName, addInfo =addInfo, type =type, condition =condition, value =value, status =status, actionType =actionType, eventId =eventId, message=message)
            db.session.add(Validation_to_add)
            db.session.commit()
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            self.message = "Error: Validation could not be added"
    def __str__(self) -> str:
        return self.message
    

class ValidationManager:
    def __init__(self, id):
        self.id = id
        self.message = ""
        self.Validation = Validation.query.filter_by(id=self.id).first()

    def remove_Validation(self):
        if self.Validation:
            Validation.query.filter(Validation.id == self.id).delete()
            db.session.commit()
            logger.info(f'Validation with ID {self.id} removed')
            self.message = f'Validation with ID {self.id} removed'
        else:
            logger.error(f'Validation with ID {self.id} does not exist')
            self.message = f'Validation with ID {self.id} does not exist'
            
    def edit_event_validation(self, formData: dict):
        print("editform")
        if self.Validation:
            try:
                print("edit form")
                self.Validation.description = formData["description"][0]
                self.Validation.deviceIP = formData["deviceIP"][0]
                self.Validation.deviceName = formData["deviceName"][0]
                self.Validation.addInfo = formData["addInfo"][0]
                self.Validation.type = formData["type"][0]
                self.Validation.condition = formData["condition"][0]
                self.Validation.value = formData["value"][0]
                self.Validation.status = formData["status"][0]
                self.Validation.actionType = formData["actionType"][0]
                self.Validation.eventId = formData["eventId"][0]
                self.Validation.message = formData["message"][0]
                db.session.commit()
                self.message = f"Event validation with ID {self.id} successfully updated"
                logger.info(self.message)
            except Exception as e:
                db.session.rollback()
                self.message = f"An error occurred while updating event validation: {e}"
                logger.error(self.message)
        else:
            self.message = f"Event validation with ID {self.id} does not exist"
            logger.error(self.message)
    
    
    
    def change_status(self):
        if self.Validation:
            if self.Validation.status == "Ready":
                self.Validation.status = "Not ready"
                self.message = "Validation status changed to: Not ready"
                logger.info(f'Validation with ID {self.id} status changed')
            elif self.Validation.status == "Not ready":
                self.Validation.status = "Ready"
                logger.info(f'Validation with ID {self.id} status changed')
                self.message = "Validation status changed to: Ready"
            else:
                logger.info(f'Validation with ID {self.id} status error')
                self.message = "Validation Status error!"
            db.session.commit()
        else:
            logger.error(f'Validation with ID {self.id} does not exist')
            self.message = f'Validation with ID {self.id} does not exist'
    
    def __str__(self) -> str:
        return self.message