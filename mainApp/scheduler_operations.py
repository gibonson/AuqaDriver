from mainApp.web_operations import WebContentCollector, LinkCreator
from mainApp.report_operations import ReportSender
from mainApp import app, db, logger
from datetime import datetime
from mainApp.models.archive_report_package import ArchiveFunctions
from mainApp.models.device import Devices
from mainApp.models.event import Event
from mainApp.models.scheduler import FunctionScheduler

def job_collector(http_address):
   logger.info(f"Job collects: {http_address}")
   webContentCollector = WebContentCollector(http_address)
   webContentCollector.collect()
   logger.info(f"Job collected")


def report_sender(scheduler_id):
   logger.info(f"Report sends: {scheduler_id}")
   reportSender = ReportSender(scheduler_id)
   reportSender.collect_and_send()
   logger.info(f"Report sent")


def sched_start(sched, scheduler_id_to_run = None):
   logger.info("Scheduler starts running")
   with app.app_context():
      if scheduler_id_to_run == None:
         functions_scheduler = FunctionScheduler.query.all()
      else:
         functions_scheduler = FunctionScheduler.query.filter_by(schedulerID=scheduler_id_to_run)
      devices_functions = Event.query.all()

      for function_scheduler in functions_scheduler:
         logger.debug("\n")
         scheduler_id = function_scheduler.schedulerID
         logger.debug("schedulerID = " + scheduler_id)
         
         if str(function_scheduler.functionId).startswith("R"):
            job_type = "report_sender"
            http_link = function_scheduler.functionId
         else:
            job_type = "job_collector"
            linkCreator = LinkCreator(devices_functions[int(function_scheduler.functionId.replace("S",""))-1].id)
            http_link =  linkCreator.functions_list_link_creator()

         logger.debug(f"job_type = {job_type}, httpLink = {http_link}")

         trigger = function_scheduler.trigger
         year = function_scheduler.year
         month = function_scheduler.month
         day = function_scheduler.day
         day_of_week = function_scheduler.day_of_week
         hour = function_scheduler.hour
         minute = function_scheduler.minute
         second = function_scheduler.second

         logger.debug(f"trigger = {trigger}, year = {year}, month = {month}, day = {day}, day_of_week = {day_of_week}")
         logger.debug(f"hour = {hour}, minute = {minute}, second = {second}")

         add_job_to_scheduler(sched, job_type, scheduler_id, http_link, trigger, year, month, day, day_of_week, hour, minute, second)


def add_job_to_scheduler(sched, job_type, scheduler_id, http_link, trigger, year, month, day, day_of_week, hour, minute, second):
    try:
        if trigger == "interval":
            sched.add_job(id=scheduler_id, func=globals()[job_type], args=[http_link], trigger=trigger, hours=hour, minutes=minute, seconds=second, max_instances=10)
        elif trigger == "date":
            sched.add_job(id=scheduler_id, func=globals()[job_type], args=[http_link], trigger=trigger, run_date=datetime(year, month, day, hour, minute, second), max_instances=10)
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