from datetime import datetime, timedelta

from mainApp.models.device import DeviceLister
from mainApp.models.archive import Archive
from mainApp.scheduler_operations import add_job_to_scheduler
from mainApp import app, logger

class DeviceStatusChecker:
    def __init__(self, sched):
        with app.app_context():
            devices = DeviceLister().get_list()
            for device in devices:
                scheduler_id = "DeviceChecker:" + device.deviceName
                if device.deviceStatus == "Ready":
                    add_job_to_scheduler(sched,"job_collector",scheduler_id, "http://" + device.deviceIP + "/check","interval",0,0,0,0,0,10,0)
                    logger.debug(scheduler_id + " Started")
                else:
                    add_job_to_scheduler(sched,"job_collector",scheduler_id, "http://" + device.deviceIP + "/check","interval",0,0,0,0,0,10,0)
                    sched.pause_job(scheduler_id)
                    logger.debug(scheduler_id + " Waiting")

class ConnectionStatus:
    def __init__(self):
        self.deviceStatusList = []
        with app.app_context():
            devices = DeviceLister().get_list()
            currentDate = str(datetime.timestamp(datetime.now()))
            minusOneDayDate = str(datetime.timestamp(datetime.now() - timedelta(days=1)))
            
            for device in devices:
                counterNOK = Archive.query.filter(
                    Archive.deviceIP == device.deviceIP,
                    Archive.addInfo == "Connection error",
                    Archive.timestamp >= minusOneDayDate,
                    Archive.timestamp <= currentDate).count()
                counterAll = Archive.query.filter(
                    Archive.deviceIP == device.deviceIP,
                    Archive.timestamp >= minusOneDayDate,
                    Archive.timestamp <= currentDate).count()
                if counterAll != 0 and counterAll != counterNOK:
                    successRate = round(((counterAll - counterNOK)/counterAll)*100)
                elif counterAll != 0 and counterAll == counterNOK:
                    successRate = -1
                else:
                    successRate = None
                self.deviceStatusList.append({"ip": device.deviceIP,"successRate": successRate})

    def getDeviceStatusList(self):
        return self.deviceStatusList
