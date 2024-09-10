from mainApp.routes import db
from mainApp import logger


class DevicesFunctions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    deviceId = db.Column(db.Integer())
    actionLink = db.Column(db.String())
    functionParameters = db.Column(db.String())
    functionDescription = db.Column(db.String())
    functionStatus = db.Column(db.String())

    def __init__(self, deviceId, actionLink, functionParameters, functionDescription, functionStatus):
        self.deviceId = deviceId
        self.actionLink = actionLink
        self.functionParameters = functionParameters
        self.functionDescription = functionDescription
        self.functionStatus = functionStatus


class DeviceFunctionsLister():
    def __init__(self):
        try:
            self.deviceFunctions = DevicesFunctions.query.all()
        except Exception as e:
            logger.error(f"An error occurred while fetching devices functions: {e}")
            self.deviceFunctions = []
    def get_list(self):
        return self.deviceFunctions
    

class DeviceFunctionAdder():
    def __init__(self, formData: dict) -> None:
        self.message = 'Device Function added'
        logger.info("Adding device function to DB")

        try:
            device_id = formData["deviceId"][0]
            action_link = formData["actionLink"][0]
            function_description = formData["functionDescription"][0]
            function_parameters = formData["functionParameters"][0]
            function_status = formData["functionStatus"][0]
            device_function_to_add = DevicesFunctions(deviceId=device_id, actionLink=action_link, functionDescription=function_description,
                                           functionParameters=function_parameters, functionStatus=function_status)
            db.session.add(device_function_to_add)
            db.session.commit()
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            self.message = "Error: Device function could not be added"
    def __str__(self) -> str:
        return self.message
    

class DeviceFunctionsManager:
    def __init__(self, id):
        self.id = id
        self.message = ""
        self.deviceFunction = DevicesFunctions.query.filter_by(id=self.id).first()

    def remove_device_function(self):
        if self.deviceFunction:
            DevicesFunctions.query.filter(DevicesFunctions.id == self.id).delete()
            db.session.commit()
            logger.info(f'DevicesFunctions with ID {self.id} removed')
            self.message = f'DevicesFunctions with ID {self.id} removed'
        else:
            logger.error(f'DevicesFunctions with ID {self.id} does not exist')
            self.message = f'DevicesFunctions with ID {self.id} does not exist'
    
    def change_status(self):
        if self.deviceFunction:
            if self.deviceFunction.functionStatus == "Ready":
                self.deviceFunction.functionStatus = "Not ready"
                self.message = "Device Function status changeD to: Not ready"
                logger.info(f'Device Function with ID {self.id} status changed')
            elif self.deviceFunction.functionStatus == "Not ready":
                self.deviceFunction.functionStatus = "Ready"
                logger.info(f'Device Function with ID {self.id} status changed')
                self.message = "Device Function status changed to: Ready"
            else:
                logger.info(f'Device Function with ID {self.id} status error')
                self.message = "Status error!"
            db.session.commit()
        else:
            logger.error(f'Device Function with ID {self.id} does not exist')
            self.message = f'Device Function with ID {self.id} does not exist'

    def __str__(self) -> str:
        return self.message