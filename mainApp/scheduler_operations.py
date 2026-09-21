from mainApp import logger
import os
from mainApp.extensions import sched
from mainApp.report_operations import ReportSender
from mainApp.models.event_scheduler import EventSchedulerManager
from mainApp.models.archive import ArchiveCleaner


def event_trigger(schedulerName):
    from mainApp import app
    from mainApp.web_operations import WebContentCollector

    with app.app_context():
        eventSchedulerDetail = EventSchedulerManager().get_by_name(schedulerName)
        if not eventSchedulerDetail:
            logger.error(f"Scheduler {schedulerName} not found in config.")
            return

        logger.debug(f"Scheduler to run: {schedulerName}")

        for eventId in eventSchedulerDetail.eventList:
            webContentCollector = WebContentCollector(eventId)
            webContentCollector.collector()

        if eventSchedulerDetail.reportList != []:
            reportSender = ReportSender(eventSchedulerDetail.reportList)
            reportSender.collect_and_send()

        # for reportID in eventSchedulerDetail.reportList:
        #     print(reportID)

        # reportSender = ReportSender(archiveDetail.get_ids())
        # reportSender.collect_and_send()


def system_db_cleanup():
    from mainApp import app

    with app.app_context():
        logger.info("Starting scheduled database cleanup...")
        ArchiveCleaner.remove_old_records(days=7)

        log_file_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "userFiles", "app.log")
        )
        if (
            os.path.exists(log_file_path)
            and os.path.getsize(log_file_path) > 10 * 1024 * 1024
        ):
            with open(log_file_path, "w") as f:
                f.write("--- LOG FILE ROTATED BY SYSTEM CLEANUP ---\n")
            logger.info("app.log file was larger than 10MB and has been cleared.")


def sched_start(schedulerNameToRun=None):
    logger.info("Scheduler starts running")
    eventSchedulerLister = []

    if schedulerNameToRun == None:
        eventSchedulerLister = EventSchedulerManager().get_all()
    else:
        eventSchedulerDetail = EventSchedulerManager().get_by_name(schedulerNameToRun)
        if eventSchedulerDetail:
            eventSchedulerLister.append(eventSchedulerDetail)

    for eventScheduler in eventSchedulerLister:
        if eventScheduler.schedulerStatus != "Ready":
            continue

        logger.debug(f"Adding job: {eventScheduler.schedulerName}")

        add_job_to_scheduler(
            func_to_run=event_trigger,
            scheduler_id=eventScheduler.schedulerName,
            args=eventScheduler.schedulerName,
            trigger=eventScheduler.trigger,
            day=eventScheduler.day,
            day_of_week=eventScheduler.day_of_week,
            hour=eventScheduler.hour,
            minute=eventScheduler.minute,
            second=eventScheduler.second,
        )

    if schedulerNameToRun is None:
        try:
            sched.add_job(
                id="system_db_cleanup",
                func=system_db_cleanup,
                trigger="cron",
                hour=3,  # run on 3:00 at nigft
                minute=0,
                replace_existing=True,
                max_instances=1,
                coalesce=True,
            )
            logger.info("System job 'system_db_cleanup' scheduled for 03:00 AM daily.")
        except Exception as e:
            logger.error(f"Failed to schedule system_db_cleanup: {e}")


def add_job_to_scheduler(
    func_to_run, scheduler_id, args, trigger, day, day_of_week, hour, minute, second
):
    try:
        if trigger == "interval":
            h = int(hour) if hour else 0
            m = int(minute) if minute else 0
            s = int(second) if second else 0

            if h == 0 and m == 0 and s == 0:
                logger.error(f"Scheduler '{scheduler_id}' ma interwał 0. Pomijam.")
                return

            sched.add_job(
                id=scheduler_id,
                func=func_to_run,
                args=[args],
                trigger=trigger,
                hours=hour,
                minutes=minute,
                seconds=second,
                max_instances=1,
                replace_existing=True,
                coalesce=True,
            )
            if int(hour) == 0 and int(minute) == 0 and int(second) == 0:
                logger.error(
                    f"Scheduler '{scheduler_id}' ma ustawiony interwał 0. Pomijam."
                )
                return
        elif trigger == "cron":
            if day > 0:
                sched.add_job(
                    id=scheduler_id,
                    func=func_to_run,
                    args=[args],
                    trigger=trigger,
                    day=day,
                    hour=hour,
                    minute=minute,
                    second=second,
                    max_instances=1,
                    replace_existing=True,
                    coalesce=True,
                )
            elif day_of_week != "None":
                sched.add_job(
                    id=scheduler_id,
                    func=func_to_run,
                    args=[args],
                    trigger=trigger,
                    day_of_week=day_of_week,
                    hour=hour,
                    minute=minute,
                    second=second,
                    max_instances=1,
                    replace_existing=True,
                    coalesce=True,
                )
            else:
                sched.add_job(
                    id=scheduler_id,
                    func=func_to_run,
                    args=[args],
                    trigger=trigger,
                    hour=hour,
                    minute=minute,
                    second=second,
                    max_instances=1,
                    replace_existing=True,
                    coalesce=True,
                )
        else:
            logger.error("Invalid job type")
    except Exception as e:
        logger.error(f"Error adding job to scheduler: {e}")
