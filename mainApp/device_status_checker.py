from mainApp.models.device import DeviceLister
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

