# Standard library imports
from datetime import datetime, timedelta
import os

# Third-party imports
from flask import Markup, flash, jsonify, redirect, request, url_for
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

# Local application/library specific imports
from mainApp import app, db, logger, sched
from mainApp.dashboard_data import DashboardData
from mainApp.email_operations import emailSender
from mainApp.forms.add_archive_report import AddArchiveReport
from mainApp.forms.add_validation import AddValidation
from mainApp.forms.add_device import AddDevice
from mainApp.forms.add_event import AddEventLink, AddEventReport
from mainApp.forms.add_scheduler import AddEventScheduler
from mainApp.forms.archive_search import ArchiveSearch
from mainApp.forms.send_email import EmailSend
from mainApp.forms.add_archive_manual import AddArchiveManualRecord
from mainApp.models.archive import ArchiveAdder, ArchiveLister, ArchiveManager, ArchiveSearchList
from mainApp.models.archive_report import ArchiveReportLister, ArchiveReporAdder
from mainApp.models.device import DeviceAdder, DeviceLister, DeviceManager, DeviceListerAll
from mainApp.models.event import  EventAdder, EventLister, EventManager
from mainApp.models.validation import  ValidationLister, ValidationAdder, ValidationManager
from mainApp.models.scheduler import EventSchedulerLister, EventSchedulerAdder, EventSchedulereManager
from mainApp.report_operations import ReportCreator
from mainApp.scheduler_operations import sched_start
from mainApp.web_operations import WebContentCollector, ResponseTrigger
# from mainApp.response_operation import ResponseTrigger
from mainApp.utils import flash_message, validate_and_log_form, render_template_with_addons

# -----------------------------------------
# create new DB
# -----------------------------------------

@app.route("/create")
def create():
    with app.app_context():
        db.create_all()
        requestData = {'addInfo': 'BD creation', 'deviceIP': '127.0.0.1','deviceName': 'Server', 'type': 'Log', 'value': 0}
        ArchiveAdder(requestData)
        flash_message("New database has been created","info")
    return redirect(url_for("get_jobs"))


# -----------------------------------------
# start page and 404
# -----------------------------------------

@app.route("/")
def hello_world():
    return redirect(url_for("get_jobs"))

@ app.errorhandler(404)
def not_found(e):
    flash_message("404!", category="warning")
    return render_template_with_addons('404.html')

@app.errorhandler(OperationalError)
def handle_operational_error(error):
    flash_message(f"OperationalError: {error}", 'danger')
    if "no such table" in str(error):
        flash_message(Markup("Try to <a href='/create'>create new DB</a>"), category='danger')
    return render_template_with_addons('500.html')


# -----------------------------------------
# device section
# -----------------------------------------

@app.route("/device_list", methods=['POST', 'GET'])
def device_list():
    form = AddDevice()
    if validate_and_log_form(form):
        DeviceAdder(request.form.to_dict(flat=False))
    devices = DeviceLister().get_list()
    return render_template_with_addons("device_list.html", devices=devices, form=form)

@app.route("/device_remove/<id>")
def device_remove(id):
    manager = DeviceManager(id)
    manager.remove_device()
    flash_message(str(manager), category='success')
    return redirect(url_for("device_list"))

@app.route("/device_change_status/<id>")
def device_change_status(id):
    manager = DeviceManager(id)
    manager.change_status()
    flash_message(str(manager), category='success')
    return redirect(url_for("device_list"))

@app.route("/device_edit/<id>", methods=['POST'])
def device_edit(id):
    manager = DeviceManager(id)
    manager.device
    form = AddDevice()
    if validate_and_log_form(form):
        manager.edit_device(request.form.to_dict(flat=False))
    return redirect(url_for("device_list"))


# -----------------------------------------
# event section
# -----------------------------------------

@app.route("/event_list", methods=['POST', 'GET'])
def event_list():
    AddEventLink.deviceIdListUpdate()
    formRequest = AddEventLink()
    AddEventReport.reportIdListUpdate()
    formReport = AddEventReport()
    if request.form.get("eventType") == "Link":
        if validate_and_log_form(formRequest):
            EventAdder(request.form.to_dict(flat=False))
    if request.form.get("eventType") == "Report":
        if validate_and_log_form(formReport):
            EventAdder(request.form.to_dict(flat=False))
    devices = DeviceListerAll().get_list()
    events = EventLister().get_list()
    return render_template_with_addons("event_list.html", Events=events, devices=devices, formRequest=formRequest, formReport=formReport)

# @app.route("/event_link_creator/<id>")
# def event_link_creator(id):
#     linkCreator = LinkCreator(id).functions_list_link_creator()
#     flash(Markup('<a href="' + linkCreator + '">' +
#           linkCreator + '</a>'), category='success')
#     return redirect(url_for("event_list"))

# # @app.route("/event_api_collector/<id>")
# # def event_api_collector(id):
# #     linkCreator = LinkCreator(id).functions_api_link_creator()
# #     flash(Markup('<a href="' + linkCreator + '">' +
# #           linkCreator + '</a>'), category='success')
# #     return redirect(url_for("event_list"))

@app.route("/event_web_content_collector/<id>")
def event_web_content_collector(id):
    WebContentCollector(id, requestID= "M").collector()
    flash("Check out some recent records", category='success')
    return redirect(url_for("archive_search"))

@app.route("/event_remove/<id>")
def event_remove(id):
    manager = EventManager(id)
    manager.remove_event()
    flash(str(manager), category='danger')
    return redirect(url_for("event_list"))

@app.route("/event_change_status/<id>")
def event_change_status(id):
    manager = EventManager(id)
    manager.change_status()
    flash(str(manager), category='danger')
    return redirect(url_for("event_list"))


@app.route("/event_edit/<id>", methods=['POST'])
def event_edit(id):
    manager = EventManager(id)
    if manager.eventType == "Link":
        print("AddEventLink")
        form = AddEventLink()
    elif manager.eventType == "Report":
        print("AddEventReport")
        form = AddEventReport()
    else:
        logger.error(f"Unknown event type: {manager.event.eventType}")
        return redirect(url_for("event_list"))
    if validate_and_log_form(form=form):
        manager.edit_event(request.form.to_dict(flat=False))
    return redirect(url_for("event_list"))


# -----------------------------------------
# scheduler section
# -----------------------------------------

@app.route("/scheduler_list", methods=['POST', 'GET'])
def scheduler_list():
    AddEventScheduler.eventIdListUpdate()
    form = AddEventScheduler()
    if validate_and_log_form(form=form):
        schedulerId = (str(form.eventId.data) + str(form.trigger.data) + str(form.day.data) + str(form.day_of_week.data) + str(form.hour.data) + str(form.minute.data) + str(form.second.data)).replace("None", "-").replace("interval", "I").replace("cron", "C")
        EventSchedulerAdder(request.form.to_dict(flat=False), schedulerId)
    device = DeviceLister().get_list()
    event = EventLister().get_list()
    eventSchedulerList = EventSchedulerLister().get_list()
    return render_template_with_addons("scheduler_list.html", eventSchedulerList=eventSchedulerList, event=event, device=device, form=form, startswith=str.startswith, int=int)

@app.route("/scheduler_remove/<id>")
def scheduler_remove(id):
    message = EventSchedulereManager(id)
    message.remove_function_scheduler()
    flash(str(message), category='warning')
    return redirect(url_for("scheduler_list"))

@app.route("/scheduler_change_status/<id>")
def scheduler_change_status(id):
    manager = EventSchedulereManager(id)
    manager.change_status()
    flash(str(manager), category='warning')
    return redirect(url_for("scheduler_list"))


# -----------------------------------------
# job section
# -----------------------------------------

@app.route("/get_jobs")
def get_jobs():
    logger.debug(sched.get_jobs())
    for job in sched.get_jobs():
        logger.info("JOB ID:" + job.id + " JOB NAME:" + job.name + " JOB TRIGGER:" +
                    str(job.trigger) + " NEXT JOB:" + str(job.next_run_time))
    return render_template_with_addons('get_jobs.html', get_jobs=sched.get_jobs())

@app.route("/get_jobs_and_scheduler")
def get_jobs_and_scheduler():
    devices = DeviceLister().get_list()
    event = EventLister().get_list()
    eventSchedulerList = EventSchedulerLister().get_list()
    return render_template_with_addons("get_jobs_and_scheduler.html", eventSchedulerList=eventSchedulerList, event=event, devices=devices, get_jobs=sched.get_jobs(), str=str, int=int)

@app.route("/pause_job/<id>")
def pause_job(id):
    sched.pause_job(id)
    return redirect(url_for("get_jobs"))

@app.route("/resume_job/<id>")
def resume_job(id):
    sched.resume_job(id)
    return redirect(url_for("get_jobs"))

@app.route("/remove_job/<id>")
def remove_job(id):
    sched.remove_job(id)
    return redirect(url_for("get_jobs"))

@app.route("/start_job/<runschedulerId>")
def start_job(runschedulerId):
    if sched.state == 0:
        sched.start()
    sched_start(sched, runschedulerId)
    return redirect(url_for("get_jobs"))


# -----------------------------------------
# archive section
# -----------------------------------------

@app.route("/archive_search", methods=['POST', 'GET'])
def archive_search():
    ArchiveSearch.archive_search_lists_update()
    form = ArchiveSearch()
    archive = ArchiveLister().get_list()
    searchEndDate = datetime.now()
    searchStartDate = datetime.now() - timedelta(days=1)
    formatSearchEndDate = searchEndDate.strftime("%Y-%m-%d %H:%M")
    formatSearchStartDate = searchStartDate.strftime("%Y-%m-%d %H:%M")
    if form.validate_on_submit():
        formatSearchStartDate = form.timestampStart.data
        formatSearchEndDate = form.timestampEnd.data
        archiveSearch = ArchiveSearchList(request.form.to_dict(flat=False))
        archive = archiveSearch.get_list()
    return render_template_with_addons("archive_search.html", archive=archive, datetime=datetime, form=form, formatedMinusOneDayDate=formatSearchStartDate, formatedCurrentDate=formatSearchEndDate)

@app.route("/archive_remove/<id>")
def archive_remove(id):
    manager = ArchiveManager(id)
    manager.remove_archive()
    flash(str(manager), category='danger')
    return redirect(url_for("archive_search"))

# -----------------------------------------
# report section
# -----------------------------------------

@app.route("/report_list", methods=['POST', 'GET'])
def report_list():
    form = AddArchiveReport()
    if validate_and_log_form(form):
        ArchiveReporAdder(request.form.to_dict(flat=False))
    archiveReportList = ArchiveReportLister().get_list()
    return render_template_with_addons("report_list.html", archiveReportList=archiveReportList, form=form)

@app.route("/get_report/<id>")
def get_report(id):
    one_line = ReportCreator().create_one_line(id)
    return one_line

@app.route("/get_report_all")
def get_report_all():
    report = ReportCreator().create_all()
    return render_template_with_addons("get_report_all.html", report=report)


# -----------------------------------------
# email sender
# -----------------------------------------

@app.route('/email_send', methods=['POST', 'GET'])
def email_send():
    form = EmailSend()
    if validate_and_log_form(form):
        emailSender(form.subject.data, form.message.data, flashMessage=True)
    return render_template_with_addons("email_send.html", form=form)


# -----------------------------------------
# DB Dashboard
# -----------------------------------------

@app.route('/get_dashboard')
def get_dashboard():
    dbSizeKB = DashboardData().getDbSizeKB()
    sqlTable = DashboardData().getSqlTable()
    return render_template_with_addons("get_dashboard.html", dbSizeKB=dbSizeKB, sqlTable=sqlTable,  state=str(sched.state))


# -----------------------------------------
# Global Scheduler Operation
# -----------------------------------------

@app.route("/pause")
def pause():
    sched.pause()
    return redirect(url_for("get_jobs"))

@app.route("/resume")
def resume():
    sched.resume()
    return redirect(url_for("get_jobs"))

@app.route("/start")
def start():
    sched.start()
    sched_start(sched)
    return redirect(url_for("get_jobs"))

@app.route("/shutdown")
def shutdown():
    # sched.remove_all_jobs() # sched.pause() # sched.delete_all_jobs() # sched.pause()# sched.shutdown(wait=False)
    return redirect(url_for("get_jobs"))


# -----------------------------------------
# json
# -----------------------------------------

@app.post('/api/addEvent')
def add_event():
    ResponseTrigger(requestData=request.get_json())
    return "OK"


# -----------------------------------------
# validation section
# -----------------------------------------

@app.route("/validation_list", methods=['POST', 'GET'])
def validation_list():
    form = AddValidation()
    if validate_and_log_form(form):
        ValidationAdder(request.form.to_dict(flat=False))
    validationList = ValidationLister().get_list()
    return render_template_with_addons("validation_list.html", validationList=validationList, form=form, datetime=datetime)

@app.route("/change_validation_status/<id>")
def change_validation_status(id):
    manager = ValidationManager(id)
    manager.change_status()
    flash(str(manager), category='danger')
    return redirect(url_for("validation_list"))

@app.route("/remove_validation/<id>")
def remove_validation(id):
    manager = ValidationManager(id)
    manager.remove_validation()
    flash(str(manager), category='danger')
    return redirect(url_for("validation_list"))

# -----------------------------------------
# manually adding to archive
# -----------------------------------------

@app.route("/archive_add_manually", methods=['POST', 'GET'])
def archive_add_manually():
    AddArchiveManualRecord.deviceListUpdate()
    form = AddArchiveManualRecord()
    if validate_and_log_form(form):
        requestDataRaw = request.form.to_dict(flat=False)
        requestDataRawList = requestDataRaw["device"][0].split(" -> ")
        requestData = {'addInfo': requestDataRaw["addInfo"][0], 'deviceIP': requestDataRawList[0],
                       'deviceName':  requestDataRawList[1], 'type': requestDataRaw["type"][0], 'value': requestDataRaw["value"][0], 'comment': requestDataRaw["comment"][0], 'requestID': 'M' + str(int(datetime.now().timestamp()))}
        ResponseTrigger(requestData=requestData)
    return render_template_with_addons("archive_add_manually.html", form=form)

# -----------------------------------------
# get_logs
# -----------------------------------------

@app.route("/get_logs", methods=["GET"])
def get_logs():
    log_file_path = os.path.join("userFiles", "app.log")
    if not os.path.exists(log_file_path):
        flash("Log file does not exist!", category="danger")
        return redirect(url_for("get_dashboard"))
    try:
        with open(log_file_path, "r") as log_file:
            lines = log_file.readlines()
            lines = [line.strip() for line in lines if line.strip()]
            last_200_lines = lines[-200:] if len(lines) > 200 else lines
            last_200_lines.reverse()
        return render_template_with_addons("get_logs.html", log_lines=last_200_lines)

    except Exception as e:
        flash(f"Error reading log file: {str(e)}", category="danger")
        return redirect(url_for("get_dashboard"))
    
    
# -----------------------------------------
# get_logs
# -----------------------------------------

@app.route("/sql_test", methods=["GET"])
def sql_test():


# gibon@GIBON-LAP:~$ for z in /sys/class/thermal/thermal_zone*/temp; do echo "$z: $(cat $z)"; done

    def cpu_temp_os():
        output = os.popen("cat /sys/class/thermal/thermal_zone12/temp").read().strip()
        temp_c = int(output) / 1000.0
        return f"{temp_c:.1f}°C"

    return cpu_temp_os()
    
