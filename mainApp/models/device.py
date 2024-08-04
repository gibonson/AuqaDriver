from mainApp.routes import db
from mainApp import logger


class Devices(db.Model):
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
            self.devices = Devices.query.all()
        except Exception as e:
            logger.error(f"An error occurred while fetching devices: {e}")
            self.devices = []
    def get_list(self):
        return self.devices


class DeviceAdder():
    def __init__(self, formData: dict):
        self.message = 'Device added'
        logger.info("Adding device to DB")
        
        try:
            device_ip = formData["deviceIP"][0]
            device_name = formData["deviceName"][0]
            device_status = formData["deviceStatus"][0]
            device_to_add = Devices(deviceIP=device_ip, deviceName=device_name, deviceStatus=device_status)
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
        self.device = Devices.query.filter_by(id=self.id).first()

    def remove_device(self):
        if self.device:
            Devices.query.filter(Devices.id == self.id).delete()
            db.session.commit()
            logger.info(f'Device with ID {self.id} removed')
            self.message = f'Device with ID {self.id} removed'
        else:
            logger.error(f'Device with ID {self.id} does not exist')
            self.message = f'Device with ID {self.id} does not exist'
    
    def change_status(self):
        if self.device:
            if self.device.deviceStatus == "Ready":
                self.device.deviceStatus = "Not ready"
                self.message = "Device status changed to: Not ready"
                logger.info(f'Device with ID {self.id} status changed')
            elif self.device.deviceStatus == "Not ready":
                self.device.deviceStatus = "Ready"
                logger.info(f'Device with ID {self.id} status changed')
                self.message = "Device status changed to: Ready"
            else:
                logger.info(f'Device with ID {self.id} status error')
                self.message = "Status error!"
            db.session.commit()
        else:
            logger.error(f'Device with ID {self.id} does not exist')
            self.message = f'Device with ID {self.id} does not exist'
    
    def __str__(self) -> str:
        return self.message