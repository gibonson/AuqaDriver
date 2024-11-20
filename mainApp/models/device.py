from mainApp.routes import db
from mainApp import logger


class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    deviceIP = db.Column(db.String())
    deviceName = db.Column(db.String())
    deviceStatus = db.Column(db.String())

    def __init__(self, deviceIP, deviceName, deviceStatus):
        self.deviceIP = deviceIP
        self.deviceName = deviceName
        self.deviceStatus = deviceStatus


class DeviceLister():
    def __init__(self):
        try:
            self.devices = Device.query.all()
        except Exception as e:
            logger.error(f"An error occurred while fetching device: {e}")
            self.devices = []
    def get_list(self):
        return self.devices


class DeviceAdder():
    def __init__(self, formData: dict):
        self.message = 'Success: Device added'
        logger.info(msg="Adding device to DB")
        try:
            device_ip = formData["deviceIP"][0]
            device_name = formData["deviceName"][0]
            device_status = formData["deviceStatus"][0]
            device_to_add = Device(deviceIP=device_ip, deviceName=device_name, deviceStatus=device_status)
            db.session.add(device_to_add)
            db.session.commit()
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            self.message = "Error: Device could not be added"
    def __str__(self) -> str:
        return self.message


class DeviceManager:
    def __init__(self, id):
        self.id = id
        self.message = ""
        self.device = Device.query.filter_by(id=self.id).first()

    def remove_device(self):
        if self.device:
            Device.query.filter(Device.id == self.id).delete()
            db.session.commit()
            self.message = f'Device with ID {self.id} removed'
            logger.info(self.message)
        else:
            self.message = f'Device with ID {self.id} does not exist'
            logger.error(self.message)
    
    def change_status(self):
        if self.device:
            if self.device.deviceStatus == "Ready":
                self.device.deviceStatus = "Not ready"
                self.message = f'Device with ID {self.id} status changed to Not Ready'
                logger.info(self.message)
            elif self.device.deviceStatus == "Not ready":
                self.device.deviceStatus = "Ready"
                self.message = f'Device with ID {self.id} status changed to Ready'
                logger.info(self.message)
            else:
                self.message = f'Device with ID {self.id} status error'
                logger.error(self.message)
            db.session.commit()
        else:
            self.message = f'Device with ID {self.id} does not exist'
            logger.error(self.message)
    
    def __str__(self) -> str:
        return self.message