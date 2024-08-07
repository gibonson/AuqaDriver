from mainApp.routes import db
from mainApp import logger

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String())
    deviceIP = db.Column(db.String())
    deviceName = db.Column(db.String())
    addInfo = db.Column(db.String())
    type = db.Column(db.String())
    condition = db.Column(db.String()) # less more equal 
    value = db.Column(db.Integer())
    notificationStatus = db.Column(db.String())# Ready, Not ready
    notificationType = db.Column(db.String()) # email, function
    functionId = db.Column(db.String())
    message = db.Column(db.String())

    def __init__(self, description, deviceIP, deviceName, addInfo, type, condition, value, notificationStatus, notificationType, functionId, message):
        self.description = description
        self.deviceIP = deviceIP
        self.deviceName = deviceName
        self.addInfo = addInfo
        self.type = type
        self.condition = condition
        self.value = value
        self.notificationStatus = notificationStatus
        self.notificationType = notificationType
        self.functionId = functionId
        self.message = message

class NotificationLister():
    def __init__(self):
        try:
            self.notification = Notification.query.all()
        except Exception as e:
            logger.error(f"An error occurred while fetching notification: {e}")
            self.notification = []
    def get_list(self):
        return self.notification
    

class NotificationAdder():
    def __init__(self, formData: dict):
        self.message = 'Notification added'
        logger.info("Adding notification to DB")
        
        try:
            description = formData["description"][0]
            deviceIP = formData["deviceIP"][0]
            deviceName = formData["deviceName"][0]
            addInfo = formData["addInfo"][0]
            type = formData["type"][0]
            condition = formData["condition"][0]
            value = formData["value"][0]
            notificationStatus = formData["notificationStatus"][0]
            notificationType = formData["notificationType"][0]
            functionId = formData["functionId"][0]
            message = formData["message"][0]
            notification_to_add = Notification(description=description, deviceIP=deviceIP, deviceName=deviceName, addInfo =addInfo, type =type, condition =condition, value =value, notificationStatus =notificationStatus, notificationType =notificationType, functionId =functionId, message=message)
            db.session.add(notification_to_add)
            db.session.commit()
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            self.message = "Error: Notification could not be added"
    def __str__(self) -> str:
        return self.message
    

class NotificationManager:
    def __init__(self, id):
        self.id = id
        self.message = ""
        self.notification = Notification.query.filter_by(id=self.id).first()

    def remove_notification(self):
        if self.notification:
            Notification.query.filter(Notification.id == self.id).delete()
            db.session.commit()
            logger.info(f'Notification with ID {self.id} removed')
            self.message = f'Notification with ID {self.id} removed'
        else:
            logger.error(f'Notification with ID {self.id} does not exist')
            self.message = f'Notification with ID {self.id} does not exist'
    
    def change_status(self):
        if self.notification:
            if self.notification.notificationStatus == "Ready":
                self.notification.notificationStatus = "Not ready"
                self.message = "Device status changed to: Not ready"
                logger.info(f'Device with ID {self.id} status changed')
            elif self.notification.notificationStatus == "Not ready":
                self.notification.notificationStatus = "Ready"
                logger.info(f'Notification with ID {self.id} status changed')
                self.message = "Notification status changed to: Ready"
            else:
                logger.info(f'Notification with ID {self.id} status error')
                self.message = "Notification Status error!"
            db.session.commit()
        else:
            logger.error(f'Notification with ID {self.id} does not exist')
            self.message = f'Notification with ID {self.id} does not exist'
    
    def __str__(self) -> str:
        return self.message