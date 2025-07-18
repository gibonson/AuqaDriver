from mainApp.routes import db
from mainApp import logger


class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    deviceIP = db.Column(db.String())
    devicePort = db.Column(db.Integer())
    deviceSSL = db.Column(db.String())
    deviceProtocol = db.Column(db.String())
    deviceToScan = db.Column(db.String())
    deviceName = db.Column(db.String())
    deviceStatus = db.Column(db.String())

    def __init__(self, deviceIP, deviceName, deviceStatus, devicePort, deviceSSL, deviceProtocol, deviceToScan):
        self.deviceIP = deviceIP
        self.deviceName = deviceName
        self.deviceStatus = deviceStatus
        self.devicePort = devicePort
        self.deviceSSL = deviceSSL
        self.deviceProtocol = deviceProtocol
        self.deviceToScan = deviceToScan


class DeviceLister():
    def __init__(self):
        try:
            self.devices = Device.query.filter(Device.deviceStatus != "Old").all()
        except Exception as e:
            logger.error(f"An error occurred while fetching device: {e}")
            self.devices = []
    def get_list(self):
        return self.devices

class DeviceListerAll():
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
            device_port = formData["devicePort"][0]
            device_ssl = formData["deviceSSL"][0]
            device_protocol = formData["deviceProtocol"][0]
            device_to_scan = formData["deviceToScan"][0]
            device_to_add = Device(deviceIP=device_ip, deviceName=device_name, deviceStatus=device_status, 
                                   devicePort=device_port, deviceSSL=device_ssl, deviceProtocol=device_protocol, 
                                   deviceToScan=device_to_scan)
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
            self.device.deviceIP = ""
            self.device.deviceName = ""
            self.device.deviceStatus = "Old"
            # Device.query.filter(Device.id == self.id).delete()
            db.session.commit()
            self.message = f'Device with ID {self.id} removed'
            logger.info(self.message)
        else:
            self.message = f'Device with ID {self.id} does not exist'
            logger.error(self.message)

    def edit_device(self, formData: dict):
        if self.device:
            try:
                self.device.deviceIP = formData["deviceIP"][0]
                self.device.deviceName = formData["deviceName"][0]
                self.device.deviceStatus = formData["deviceStatus"][0]
                self.device.devicePort = formData["devicePort"][0]
                self.device.deviceSSL = formData["deviceSSL"][0]
                self.device.deviceProtocol = formData["deviceProtocol"][0]
                self.device.deviceToScan = formData["deviceToScan"][0]
                db.session.commit()
                self.message = f"Device with ID {self.id} successfully updated"
                logger.info(self.message)
            except Exception as e:
                db.session.rollback()
                self.message = f"An error occurred while updating device: {e}"
                logger.error(self.message)
        else:
            self.message = f"Device with ID {self.id} does not exist"
            logger.error(self.message)
    
    def change_status(self):
        if self.device:
            if self.device.deviceStatus == "Ready":
                self.device.deviceStatus = "Not Ready"
                self.message = f'Device with ID {self.id} status changed to Not Ready'
                logger.info(self.message)
            elif self.device.deviceStatus == "Not Ready":
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