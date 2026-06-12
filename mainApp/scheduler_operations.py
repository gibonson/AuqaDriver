from mainApp.web_operations import WebContentCollector
from mainApp.report_operations import ReportSender
from mainApp import logger
from mainApp.models.event_scheduler import EventSchedulerGetBySchedulerName, EventSchedulerLister

def event_trigger(schedulerName):
        eventSchedulerDetail = EventSchedulerGetBySchedulerName(schedulerName).get_event()
        logger.debug(f"Scheduler to run: {schedulerName}")
        for eventId in eventSchedulerDetail.eventList:
            webContentCollector = WebContentCollector(eventId)
            webContentCollector.collector()
        
        reportSender = ReportSender(eventSchedulerDetail.reportList)
        reportSender.collect_and_send()

        
        
        # for reportID in eventSchedulerDetail.reportList:
        #     print(reportID)
            
            # reportSender = ReportSender(archiveDetail.get_ids())
            # reportSender.collect_and_send()


def sched_start(sched, schedulerNameToRun = None):
    logger.info("Scheduler starts running")
    eventSchedulerLister = []
    if schedulerNameToRun == None:
        eventSchedulerLister = EventSchedulerLister().get_list()
    else:
        eventSchedulerDetail = EventSchedulerGetBySchedulerName(schedulerNameToRun).get_event()
        eventSchedulerLister.append(eventSchedulerDetail)

    for eventScheduler in eventSchedulerLister:
        job_type = "event_trigger"
        schedulerName = eventScheduler.schedulerName
        trigger = eventScheduler.trigger
        day = eventScheduler.day
        day_of_week = eventScheduler.day_of_week
        hour = eventScheduler.hour
        minute = eventScheduler.minute
        second = eventScheduler.second
        if eventScheduler.schedulerStatus != "Ready":
            continue
        
        logger.debug(f"schedulerId = {schedulerName} - trigger = {trigger}, day = {day}, day_of_week = {day_of_week}, hour = {hour}, minute = {minute}, second = {second}")
        add_job_to_scheduler(sched, job_type, schedulerName, schedulerName, trigger, day, day_of_week, hour, minute, second)


def add_job_to_scheduler(sched, job_type, scheduler_id, args, trigger, day, day_of_week, hour, minute, second):
    try:
        if trigger == "interval":
            sched.add_job(id=scheduler_id, func=globals()[job_type], args=[args], trigger=trigger, hours=hour, minutes=minute, seconds=second, max_instances=10)
        elif trigger == "cron":
            if day > 0:
                sched.add_job(id=scheduler_id, func=globals()[job_type], args=[args], trigger=trigger, day=day, hour=hour, minute=minute, second=second, max_instances=10)
            elif day_of_week != "None":
                sched.add_job(id=scheduler_id, func=globals()[job_type], args=[args], trigger=trigger, day_of_week=day_of_week, hour=hour, minute=minute, second=second, max_instances=10)
            else:
                sched.add_job(id=scheduler_id, func=globals()[job_type], args=[args], trigger=trigger, hour=hour, minute=minute, second=second, max_instances=10)
        else:
            logger.error("Invalid job type")
    except Exception as e:
        logger.error(f"Error adding job to scheduler: {e}")