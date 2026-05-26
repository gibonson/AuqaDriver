# Standard library imports
from datetime import datetime, timedelta
import os

# Third-party imports
from flask import Markup, flash, jsonify, redirect, request, url_for, abort
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

# Local application/library specific imports
from mainApp import app, db, logger, sched
from mainApp.dashboard_data import DashboardData
from mainApp.email_operations import emailSender, pushoverSender
from mainApp.forms.add_validation import AddValidation
from mainApp.forms.add_event import AddEventLink
from mainApp.forms.add_scheduler import AddEventScheduler
from mainApp.forms.archive_search import ArchiveSearch
from mainApp.forms.config_json import EventConfigForm, SchedulerConfigForm, ReportConfigForm
from mainApp.forms.send_email import EmailSend
from mainApp.forms.add_archive_manual import AddArchiveManualRecord
from mainApp.models.archive import ArchiveAdder, ArchiveLister, ArchiveManager, ArchiveSearchList
from mainApp.config_operations import load_event_config, load_scheduler_config, load_report_config, validate_event_config_text, backup_event_config, save_event_config, get_event_config_path, restart_application
from mainApp.config_operations import backup_scheduler_config, save_scheduler_config, get_scheduler_config_path, validate_scheduler_config_text, backup_report_config, save_report_config, get_report_config_path, validate_report_config_text
from mainApp.models.archive_report import ArchiveReportLister
from mainApp.models.event import EventListerJson
from mainApp.models.event_validation import  ValidationLister, ValidationAdder, ValidationManager
from mainApp.models.event_scheduler import EventSchedulerLister
from mainApp.models.dashboard import DashboardLister
from mainApp.report_operations import ReportCreator
# from mainApp.scheduler_operations import sched_start
from mainApp.web_operations import WebContentCollector, ResponseTrigger
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
    return redirect(url_for("dashboard"))

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
# event section
# -----------------------------------------

@app.route("/event_list_json", methods=['POST', 'GET'])
def event_list_json():
    events = EventListerJson().get_list()
    return render_template_with_addons("event_list_json.html", Events=events)

@app.route("/event_open/<eventName>")
def event_open(eventName):
    WebContentCollector(eventName, requestID= "Manual").collector()
    flash("Check out some recent records", category='success')
    return redirect(url_for("archive_search"))

@app.route("/config_events", methods=['POST', 'GET'])
def config_events():
    form = EventConfigForm()
    if request.method == 'GET':
        form.config_json.data = load_event_config()

    if validate_and_log_form(form=form):
        try:
            validate_event_config_text(form.config_json.data)
            backup_event_config()
            save_event_config(form.config_json.data)
            flash_message('Nowa konfiguracja eventów została zapisana. Aplikacja zostanie zrestartowana.', 'success')
        except ValueError as validation_error:
            flash_message(str(validation_error), 'warning')
    return render_template_with_addons('config_events.html', form=form, config_path=get_event_config_path())


# -----------------------------------------
# scheduler section
# -----------------------------------------

@app.route("/scheduler_list", methods=['POST', 'GET'])
def scheduler_list():
    eventSchedulerList = EventSchedulerLister().get_list()
    return render_template_with_addons("scheduler_list_json.html", eventSchedulerList=eventSchedulerList, startswith=str.startswith, int=int)

@app.route("/config_scheduler", methods=['POST', 'GET'])
def config_scheduler():
    form = SchedulerConfigForm()
    if request.method == 'GET':
        form.config_json.data = load_scheduler_config()

    if validate_and_log_form(form=form):
        try:
            validate_scheduler_config_text(form.config_json.data)
            backup_scheduler_config()
            save_scheduler_config(form.config_json.data)
            flash_message('Nowa konfiguracja schedulerów została zapisana. Aplikacja zostanie zrestartowana.', 'success')
        except ValueError as validation_error:
            flash_message(str(validation_error), 'warning')

    return render_template_with_addons('config_scheduler.html', form=form, config_path=get_scheduler_config_path())


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

@app.route("/report_list")
def report_list():
    archiveReportList = ArchiveReportLister().get_list()
    return render_template_with_addons("report_list.html", archiveReportList=archiveReportList)

@app.route("/config_reports", methods=['POST', 'GET'])
def config_reports():
    form = ReportConfigForm()
    if request.method == 'GET':
        form.config_json.data = load_report_config()

    if validate_and_log_form(form=form):
        try:
            validate_report_config_text(form.config_json.data)
            backup_report_config()
            save_report_config(form.config_json.data)
            flash_message('Nowa konfiguracja raportów została zapisana.', 'success')
        except ValueError as validation_error:
            flash_message(str(validation_error), 'warning')

    return render_template_with_addons(
        'config_reports.html',
        form=form,
        config_path=get_report_config_path()
    )

@app.route("/get_report/<reportName>")
def get_report(reportName):
    one_line = ReportCreator().create_one_line(reportName)
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

@app.route("/event_validation_edit/<id>", methods=['POST'])
def event_validation_edit(id):
    manager = ValidationManager(id)
    form = AddValidation()
    if validate_and_log_form(form=form):
        manager.edit_event_validation(request.form.to_dict(flat=False))
    return redirect(url_for("validation_list"))

# -----------------------------------------
# manually adding to archive
# -----------------------------------------

@app.route("/archive_add_manually", methods=['POST', 'GET'])
def archive_add_manually():
    form = AddArchiveManualRecord()
    if validate_and_log_form(form):
        requestDataRaw = request.form.to_dict(flat=False)
        requestData = {'addInfo': requestDataRaw["addInfo"][0], 'deviceIP': requestDataRaw["deviceIP"][0],
                       'deviceName':  requestDataRaw["deviceName"][0], 'type': requestDataRaw["type"][0], 'value': requestDataRaw["value"][0], 'comment': requestDataRaw["comment"][0], 'requestID': 'M' + str(int(datetime.now().timestamp()))}
        ResponseTrigger(requestData=requestData)
    return render_template_with_addons("archive_add_manually.html", form=form)

# -----------------------------------------
# get_logs
# -----------------------------------------

@app.route("/get_logs", methods=["GET"])
def get_logs():
    dbSizeKB = DashboardData().getDbSizeKB()
    logSizeKB = DashboardData().getLogsSizeKB()
    sqlTable = DashboardData().getSqlTable()
    log_file_path = os.path.join("userFiles", "app.log")
    if not os.path.exists(log_file_path):
        flash("Log file does not exist!", category="danger")
        abort(404)
    try:
        with open(log_file_path, "r") as log_file:
            lines = log_file.readlines()
            lines = [line.strip() for line in lines if line.strip()]
            last_200_lines = lines[-200:] if len(lines) > 200 else lines
            last_200_lines.reverse()
        return render_template_with_addons("get_logs.html", log_lines=last_200_lines, dbSizeKB=dbSizeKB, logSizeKB=logSizeKB, sqlTable=sqlTable,  state=str(sched.state))

    except Exception as e:
        flash(f"Error reading log file: {str(e)}", category="danger")
        abort(404)
    
    
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
    
@app.route("/pushover_test", methods=["GET"])
def pushover_test():
    pushoverSender("Testowa wiadomość z AuqaDriver")
    return "done"
    
@app.route("/dashboard", methods=["GET"])
def dashboard():
    dashboardList = DashboardLister().get_list()
    
    dashboardList.sort(key=lambda x: x.panelLocation)
    
    for dashboard in dashboardList:
        if dashboard.panelCode is None:
            dashboard.panelCode = ""
        if dashboard.panelType == "Report":
            dashboard.panelCode = str(dashboard.panelCode) + "</br>" + ReportCreator().create_one_line(dashboard.panelItemId)
        elif dashboard.panelType == "Event":
            dashboard.panelCode = dashboard.panelCode + "</br>" + '<a href="' + "/event_open/" + str(dashboard.panelItemId) + '" class="btn btn-success btn-lg active"role="button" aria-pressed="true">Open</a>'
        elif dashboard.panelType == "HTML":
            dashboard.panelCode = dashboard.panelCode
        else:
            dashboard.panelCode = "UNKNOWN TYPE"
    
    
    return render_template_with_addons("dashboard.html", dashboardList = dashboardList, state=str(sched.state))



ESP32_STREAM_URL = "http://192.168.0.235:81/stream"

import requests
from flask import Response, render_template
import re
def mjpeg_proxy():
    r = requests.get(ESP32_STREAM_URL, stream=True)

    content_type = r.headers.get("Content-Type", "")
    match = re.search("boundary=(.*)", content_type)
    if not match:
        raise RuntimeError("Brak boundary w Content-Type")

    boundary = match.group(1).encode()
    boundary = b"--" + boundary

    buffer = b""

    for chunk in r.iter_content(chunk_size=2048):
        buffer += chunk

        while boundary in buffer:
            part, buffer = buffer.split(boundary, 1)
            if b"Content-Type: image/jpeg" in part:
                yield boundary + part

@app.route('/video_feed')
def video_feed():
    return Response(
        mjpeg_proxy(),
        mimetype="multipart/x-mixed-replace; boundary=" + 
                 "123456789000000000000987654321"
    )
    
    
@app.route('/video')
def index():
    return render_template("stream.html")