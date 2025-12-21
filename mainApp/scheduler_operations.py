from mainApp.web_operations import WebContentCollector
from mainApp.report_operations import ReportSender
from mainApp import app, db, logger
from datetime import datetime
from mainApp.models.event import Event, EventLister, GetIdsListWhenGroupId
from mainApp.models.archive_report import ArchiveReport, ArchiveReportLister
from mainApp.models.event_scheduler import EventScheduler, EventSchedulerLister, EveentSchedulerGetter

def event_trigger(schedulerId):
    print("Event trigger called: " + schedulerId)
    with app.app_context():

        eventSchedulerDetail = EveentSchedulerGetter(schedulerId)
        eventSchedulerDetail = eventSchedulerDetail.get_scheduler()
        print(eventSchedulerDetail)
        if "EventGroup:" in eventSchedulerDetail.groupId:
            print("Event Group: " + eventSchedulerDetail.groupId)
            eventListByGroup = GetIdsListWhenGroupId(eventSchedulerDetail.groupId.replace("EventGroup:",""))
            print(eventListByGroup.get_ids())
            for eventId in eventListByGroup.get_ids():
                print("Triggering event ID: " + str(eventId))
                webContentCollector = WebContentCollector(eventId)
                webContentCollector.collector()
            
        elif "ReportGroup:" in eventSchedulerDetail.groupId:
            print("Report Group: " + eventSchedulerDetail.groupId)
            archiveDetail = ArchiveReportLister(reportGroupId=eventSchedulerDetail.groupId.replace("ReportGroup:",""))
            archiveDetail = archiveDetail.get_list()
            print(archiveDetail)
            
        else: 
            print("Single not found")

# def report_sender(scheduler_id):
#     print("Report sender called")
#     logger.info(f"Report sending: {scheduler_id}")
#    logger.info(f"Report sends: {scheduler_id}")
#    reportSender = ReportSender(scheduler_id)
#    reportSender.collect_and_send()
#    logger.info(f"Report sent")


def sched_start(sched, schedulerIdToRun = None):
   logger.info("Scheduler starts running")
   with app.app_context():
      if schedulerIdToRun == None:
         eventSchedulerLister = EventSchedulerLister("Ready").get_list()
      else:
         eventSchedulerLister = EventScheduler.query.filter_by(schedulerId=schedulerIdToRun)
      eventList = EventLister().get_list()

      for eventScheduler in eventSchedulerLister:
        print(eventScheduler.schedulerId)
        print(eventScheduler.groupId)
        schedulerId = eventScheduler.schedulerId
        
        job_type = "event_trigger"

        trigger = eventScheduler.trigger
        day = eventScheduler.day
        day_of_week = eventScheduler.day_of_week
        hour = eventScheduler.hour
        minute = eventScheduler.minute
        second = eventScheduler.second

        logger.debug(f"schedulerId = {schedulerId} - trigger = {trigger}, day = {day}, day_of_week = {day_of_week}, hour = {hour}, minute = {minute}, second = {second}")
        add_job_to_scheduler(sched, job_type, schedulerId, schedulerId, trigger, day, day_of_week, hour, minute, second)


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