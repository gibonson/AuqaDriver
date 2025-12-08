from mainApp.web_operations import WebContentCollector
from mainApp.report_operations import ReportSender
from mainApp import app, db, logger
from datetime import datetime
# from mainApp.models.device import Device
from mainApp.models.event import Event, EventLister
from mainApp.models.event_scheduler import EventScheduler, EventSchedulerLister

def job_collector(scheduler_id):
   logger.info(f"Job collects: {scheduler_id}")
   webContentCollector = WebContentCollector(scheduler_id)
   webContentCollector.collector()
   logger.info(f"Job collected")


def report_sender(scheduler_id):
   logger.info(f"Report sends: {scheduler_id}")
   reportSender = ReportSender(scheduler_id)
   reportSender.collect_and_send()
   logger.info(f"Report sent")


def sched_start(sched, schedulerIdToRun = None):
   logger.info("Scheduler starts running")
   with app.app_context():
      if schedulerIdToRun == None:
         eventSchedulerLister = EventSchedulerLister("Ready").get_list()
      else:
         eventSchedulerLister = EventScheduler.query.filter_by(schedulerId=schedulerIdToRun)
      eventList = EventLister().get_list()

      for eventScheduler in eventSchedulerLister:
        # scheduler_id = eventScheduler.schedulerId
        # logger.debug(f"schedulerId = {scheduler_id}")
        # if eventList[int(eventScheduler.groupId)-1].eventType  == "Report":
        #     job_type = "report_sender"
        #     http_link = eventScheduler.groupId
        #     logger.debug(f"schedulerId = {scheduler_id} - job_type = {job_type}, httpLink = {http_link}")
        # if eventList[int(eventScheduler.groupId)-1].eventType  == "Link":
        #     job_type = "job_collector"
        #     http_link = eventScheduler.groupId
        #     # linkCreator = LinkCreator(eventScheduler.groupId)
        #     # http_link =  linkCreator.functions_list_link_creator()
        #     # logger.debug(f"schedulerId = {scheduler_id} - job_type = {job_type}, httpLink = {http_link}")

        trigger = eventScheduler.trigger
        day = eventScheduler.day
        day_of_week = eventScheduler.day_of_week
        hour = eventScheduler.hour
        minute = eventScheduler.minute
        second = eventScheduler.second

        # logger.debug(f"schedulerId = {scheduler_id} - trigger = {trigger}, day = {day}, day_of_week = {day_of_week}, hour = {hour}, minute = {minute}, second = {second}")
        # add_job_to_scheduler(sched, job_type, scheduler_id, http_link, trigger, day, day_of_week, hour, minute, second)


def add_job_to_scheduler(sched, job_type, scheduler_id, http_link, trigger, day, day_of_week, hour, minute, second):
    print("Adding job to scheduler")
    try:
        if trigger == "interval":
            sched.add_job(id=scheduler_id, func=globals()[job_type], args=[http_link], trigger=trigger, hours=hour, minutes=minute, seconds=second, max_instances=10)
        elif trigger == "cron":
            if day > 0:
                sched.add_job(id=scheduler_id, func=globals()[job_type], args=[http_link], trigger=trigger, day=day, hour=hour, minute=minute, second=second, max_instances=10)
            elif day_of_week != "None":
                sched.add_job(id=scheduler_id, func=globals()[job_type], args=[http_link], trigger=trigger, day_of_week=day_of_week, hour=hour, minute=minute, second=second, max_instances=10)
            else:
                sched.add_job(id=scheduler_id, func=globals()[job_type], args=[http_link], trigger=trigger, hour=hour, minute=minute, second=second, max_instances=10)
        else:
            logger.debug("Invalid job type")
    except Exception as e:
        logger.error(f"Error adding job to scheduler: {e}")