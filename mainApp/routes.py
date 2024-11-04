# Standard library imports
from datetime import datetime, timedelta

# Third-party imports
from flask import Markup, flash, jsonify, redirect, render_template, request, url_for
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

# Local application/library specific imports
from mainApp import app, db, logger, sched
from mainApp.dashboard_data import DashboardData
from mainApp.email_operations import emailSender
from mainApp.forms.add_archive_report import AddArchiveReport
from mainApp.forms.add_archive_report_fnction import AddArchiveReportFunction
from mainApp.forms.add_archive_ignore import AddArchiveIgnore
from mainApp.forms.add_device import AddDevice
from mainApp.forms.add_device_functions import AddDeviceFunctions
from mainApp.forms.add_function_scheduler import AddFunctionScheduler
from mainApp.forms.add_notification import AddNotification
from mainApp.forms.archive_search import ArchiveSearch
from mainApp.forms.send_email import EmailSend
from mainApp.forms.add_archive_manual import AddArchiveManualRecord
from mainApp.forms.charts_search import ChartsSearch
from mainApp.models.archive import Archive, ArchiveAdder, ArchiveLister, ArchiveManager
from mainApp.models.archive_ignore import ArchiveIgoneLister, ArchiveIgoneAdder, ArchiveIgnoreManager
from mainApp.models.report_functions import  ArchiveFunctionsLister, ArchiveFunctionsAdder
from mainApp.models.report import ArchiveReportLister, ArchiveReporAdder
from mainApp.models.device import DeviceAdder, DeviceLister, DeviceManager
from mainApp.models.device_function import  DeviceFunctionAdder, DeviceFunctionsLister, DeviceFunctionsManager
from mainApp.models.notification import  NotificationLister, NotificationAdder, NotificationManager
from mainApp.models.scheduler import FunctionScheduler, FunctionSchedulerLister, FunctionSchedulereAdder, FunctionSchedulereManager
from mainApp.report_operations import ReportCreator
from mainApp.notification_operations import NotificationTrigger
from mainApp.scheduler_operations import sched_start
from mainApp.web_operations import LinkCreator, WebContentCollector
from mainApp.charts import Table
from mainApp.response_operation import ResponseTrigger
from mainApp.utils import flash_message, validate_and_log_form


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
    return render_template('404.html', state=str(sched.state))

@app.errorhandler(OperationalError)
def handle_operational_error(error):
    flash_message(f"OperationalError: {error}", 'danger')
    if "no such table" in str(error):
        flash_message(Markup("Try to <a href='/create'>create new DB</a>"), category='danger')
    return render_template('500.html', state=str(sched.state))


# -----------------------------------------
# device section
# -----------------------------------------

@app.route("/device_list", methods=['POST', 'GET'])
def device_list():
    form = AddDevice()
    if validate_and_log_form(form):
        DeviceAdder(request.form.to_dict(flat=False))
    devices = DeviceLister().get_list()
    return render_template("devicesList.html", devices=devices, form=form, state=str(sched.state))

@app.route("/device_remove/<id>")
def device_remove(id):
    manager = DeviceManager(id)
    manager.remove_device()
    flash_message(str(manager), category='success')
    return redirect(url_for("device_list"))

@app.route("/change_device_status/<id>")
def change_device_status(id):
    manager = DeviceManager(id)
    manager.change_status()
    flash_message(str(manager), category='success')
    return redirect(url_for("device_list"))


# -----------------------------------------
# function section
# -----------------------------------------

@app.route("/device_functions_list", methods=['POST', 'GET'])
def device_functions_list():
    AddDeviceFunctions.deviceIdListUpdate()
    form = AddDeviceFunctions()
    if validate_and_log_form(form):
        DeviceFunctionAdder(request.form.to_dict(flat=False))
    devices = DeviceLister().get_list()
    devicesFunctions = DeviceFunctionsLister().get_list()
    return render_template("functionsList.html", devicesFunctions=devicesFunctions, devices=devices, form=form, state=str(sched.state))

@app.route("/device_functions_list_link_creator/<id>")
def device_functions_list_link_creator(id):
    linkCreator = LinkCreator(id).functions_list_link_creator()
    flash(Markup('<a href="' + linkCreator + '">' +
          linkCreator + '</a>'), category='success')
    return redirect(url_for("device_functions_list"))

@app.route("/device_functions_list_web_content_collector/<id>")
def device_functions_list_web_content_collector(id):
    WebContentCollector(LinkCreator(
        id).functions_list_link_creator()).collect()
    flash("Check out some recent records", category='success')
    return redirect(url_for("archive_search"))

@app.route("/device_functions_remove/<id>")
def device_functions_remove(id):
    manager = DeviceFunctionsManager(id)
    manager.remove_device_function()
    flash(str(manager), category='danger')
    return redirect(url_for("device_functions_list"))

@app.route("/change_device_functions_status/<id>")
def change_device_functions_status(id):
    manager = DeviceFunctionsManager(id)
    manager.change_status()
    flash(str(manager), category='danger')
    return redirect(url_for("device_functions_list"))


# -----------------------------------------
# scheduler section
# -----------------------------------------

@app.route("/scheduler_list", methods=['POST', 'GET'])
def scheduler_list():
    AddFunctionScheduler.functionIdListUpdate()
    form = AddFunctionScheduler()
    if validate_and_log_form(form):
        schedulerID = str(form.functionId.data) + str(form.trigger.data) + str(form.year.data) + str(
            form.month.data) + str(form.day.data) + str(form.day_of_week.data) + str(form.hour.data) + str(form.minute.data) + str(form.second.data)
        schedulerID = schedulerID.replace("None", "-")
        number = FunctionScheduler.query.filter_by(schedulerID=schedulerID).first()
        if number:
            flash(form.schedulerID.data +
                  " record exists in the DB", category='warning')
            return redirect(url_for("scheduler_list"))
        FunctionSchedulereAdder(request.form.to_dict(flat=False), schedulerID)
    devices = DeviceLister().get_list()
    devicesFunctions = DeviceFunctionsLister().get_list()
    functionsScheduler = FunctionSchedulerLister().get_list()
    archiveFunctions = ArchiveFunctionsLister().get_list()
    return render_template("schedulerList.html", functionsScheduler=functionsScheduler, devicesFunctions=devicesFunctions, devices=devices, archiveFunctions=archiveFunctions, state=str(sched.state), form=form, startswith=str.startswith, int=int)


# -----------------------------------------
# job section
# -----------------------------------------

@app.route("/get_jobs")
def get_jobs():
    logger.debug(sched.get_jobs())
    for job in sched.get_jobs():
        logger.info("JOB ID:" + job.id + " JOB NAME:" + job.name + " JOB TRIGGER:" +
                    str(job.trigger) + " NEXT JOB:" + str(job.next_run_time))
    return render_template('getJobs.html', get_jobs=sched.get_jobs(), state=str(sched.state))

@app.route("/functions_scheduler_list_get_jobs")
def functions_scheduler_list_get_jobs():
    devices = DeviceLister().get_list()
    devicesFunctions = DeviceFunctionsLister().get_list()
    functionsScheduler = FunctionSchedulerLister().get_list()
    return render_template("SchedulerListWithJobs.html", functionsScheduler=functionsScheduler, devicesFunctions=devicesFunctions, devices=devices, get_jobs=sched.get_jobs(), state=str(sched.state), str=str, int=int)

@app.route("/scheduler_remove/<id>")
def scheduler_remove(id):
    message = FunctionSchedulereManager(id)
    message.remove_function_scheduler()
    flash(str(message), category='danger')
    return redirect(url_for("get_jobs"))

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

@app.route("/start_job/<runSchedulerID>")
def start_job(runSchedulerID):
    if sched.state == 0:
        sched.start()
    sched_start(sched, runSchedulerID)
    return redirect(url_for("get_jobs"))


# -----------------------------------------
# archive section
# -----------------------------------------

@app.route("/archive_search", methods=['POST', 'GET'])
def archive_search():
    ArchiveSearch.archive_search_lists_update()
    form = ArchiveSearch()
    archive = ArchiveLister().get_list()
    currentDate = datetime.now()
    formatedCurrentDate = currentDate.strftime("%Y-%m-%d %H:%M")
    minusOneDayDate = datetime.now() - timedelta(days=1)
    formatedMinusOneDayDate = minusOneDayDate.strftime("%Y-%m-%d %H:%M")

    if form.validate_on_submit():
        logger.debug(str(request.form.to_dict(flat=False)))
        logger.debug("date time to timestampStart: " + str(datetime.timestamp(form.timestampStart.data)))
        logger.debug("date time to timestampEnd: " + str(datetime.timestamp(form.timestampEnd.data)))
        logger.debug("recordType:" + str(form.recordType.data))

        recordTypes = form.recordType.data
        deviceIP = []
        deviceName = []
        addInfo = []
        type = []
        for recordType in recordTypes:
            recordTypeList = recordType.split(" -> ")
            deviceIP.append(recordTypeList[0])
            deviceName.append(recordTypeList[1])
            addInfo.append(recordTypeList[2])
            type.append(recordTypeList[3])

        archive = Archive.query.filter(
            Archive.deviceIP.in_(deviceIP),
            Archive.addInfo.in_(addInfo),
            Archive.deviceName.in_(deviceName),
            Archive.timestamp >= datetime.timestamp(form.timestampStart.data),
            Archive.timestamp <= datetime.timestamp(form.timestampEnd.data),
            Archive.type.in_(type)
        ).order_by(Archive.id.desc()).limit(form.limit.data)
    return render_template("archiveSearch.html", archive=archive, datetime=datetime, form=form, state=str(sched.state), formatedMinusOneDayDate=formatedMinusOneDayDate, formatedCurrentDate=formatedCurrentDate)


@app.route("/archive_remove/<id>")
def archive_remove(id):
    manager = ArchiveManager(id)
    manager.remove_archive()
    flash(str(manager), category='danger')
    return redirect(url_for("archive_search"))

@app.route("/archive_ignore", methods=['POST','GET'])
def archive_ignore():
    form = AddArchiveIgnore()
    if validate_and_log_form(form):
        ArchiveIgoneAdder(request.form.to_dict(flat=False))
    archiveIgoneLister = ArchiveIgoneLister().get_list()
    return render_template("archiveIgnore.html", archiveIgoneLister=archiveIgoneLister, form=form, state=str(sched.state))

@app.route("/archive_ignore_remove/<id>")
def archive_ignore_remove(id):
    manager = ArchiveIgnoreManager(id)
    manager.remove()
    flash(str(manager), category='danger')
    return redirect(url_for("archive_ignore"))

@app.route("/change_archive_ignore_status/<id>")
def change_archive_ignore_status(id):
    manager = ArchiveIgnoreManager(id)
    manager.change_status()
    flash(str(manager), category='danger')
    return redirect(url_for("archive_ignore"))


# -----------------------------------------
# report section
# -----------------------------------------

@app.route("/report_list", methods=['POST', 'GET'])
def report_list():
    AddArchiveReport.add_archive_report_lists_update()
    form = AddArchiveReport()
    if validate_and_log_form(form):
        ArchiveReporAdder(request.form.to_dict(flat=False))
    archiveReportList = ArchiveReportLister().get_list()
    return render_template("archiveReportList.html", archiveReportList=archiveReportList, form=form, state=str(sched.state))

@app.route("/get_report/<id>")
def get_report(id):
    one_line = ReportCreator().create_one_line(id)
    return one_line

@app.route("/get_report_all")
def get_report_all():
    report = ReportCreator().create_all()
    return render_template("archiveReportListAll.html", report=report, state=str(sched.state))


# -----------------------------------------
# report functions section
# -----------------------------------------

@app.route("/report_functions_list", methods=['POST', 'GET'])
def report_functions_list():
    AddArchiveReportFunction.add_archive_report_function_lists_update()
    form = AddArchiveReportFunction()
    if validate_and_log_form(form):
        ArchiveFunctionsAdder(request.form.to_dict(flat=False))
    archiveFunctionsList = ArchiveFunctionsLister().get_list()
    return render_template("reportFunctions.html", archiveFunctionsList=archiveFunctionsList, form=form, datetime=datetime, state=str(sched.state))


# -----------------------------------------
# email sender
# -----------------------------------------

@app.route('/emailSend', methods=['POST', 'GET'])
def email_send():
    form = EmailSend()
    if validate_and_log_form(form):
        emailSender(form.subject.data, form.message.data, flashMessage=True)
    return render_template("emailSend.html", form=form, state=str(sched.state))


# -----------------------------------------
# DB Dashboard
# -----------------------------------------

@app.route('/dashboard')
def dashboard():
    dbSizeKB = DashboardData().getDbSizeKB()
    sqlTable = DashboardData().getSqlTable()
    return render_template("dashboard.html", dbSizeKB=dbSizeKB, sqlTable=sqlTable,  state=str(sched.state))


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
# notification
# -----------------------------------------

@app.route("/notification_list", methods=['POST', 'GET'])
def notification_list():
    form = AddNotification()
    if validate_and_log_form(form):
        NotificationAdder(request.form.to_dict(flat=False))
    notificationList = NotificationLister().get_list()
    return render_template("notificationList.html", notificationList=notificationList, form=form, datetime=datetime, state=str(sched.state))

@app.route("/change_notification_status/<id>")
def change_notification_status(id):
    manager = NotificationManager(id)
    manager.change_status()
    flash(str(manager), category='danger')
    return redirect(url_for("notification_list"))

@app.route("/remove_notification/<id>")
def remove_notification(id):
    manager = NotificationManager(id)
    manager.remove_notification()
    flash(str(manager), category='danger')
    return redirect(url_for("notification_list"))


# -----------------------------------------
# charts
# -----------------------------------------

@app.route("/charts", methods=['POST', 'GET'])
def charts():
    ChartsSearch.archive_search_lists_update()
    form = ChartsSearch()
    currentDate = datetime.now()
    formatedCurrentDate = currentDate.strftime("%Y-%m-%d %H:%M")
    minusOneDayDate = datetime.now() - timedelta(days=1)
    formatedMinusOneDayDate = minusOneDayDate.strftime("%Y-%m-%d %H:%M")

    chart = Table(delta=10, type="%")
    chart.reportGenerator()
    final_chart = chart.get_final_results()
    return render_template("charts.html", final_chart=final_chart, datetime=datetime, form=form, formatedMinusOneDayDate=formatedMinusOneDayDate, formatedCurrentDate=formatedCurrentDate, state=str(sched.state))


# -----------------------------------------
# manually adding to archive
# -----------------------------------------

@app.route("/manually_add_to_archive", methods=['POST', 'GET'])
def manually_add_to_archive():
    AddArchiveManualRecord.deviceListUpdate()
    form = AddArchiveManualRecord()
    if validate_and_log_form(form):
        requestDataRaw = request.form.to_dict(flat=False)
        requestDataRawList = requestDataRaw["device"][0].split(" -> ")
        requestData = {'addInfo': requestDataRaw["addInfo"][0], 'deviceIP': requestDataRawList[0],
                       'deviceName':  requestDataRawList[1], 'type': requestDataRaw["type"][0], 'value': requestDataRaw["value"][0]}
        ResponseTrigger(requestData=requestData)
    return render_template("archiveAddManually.html", form=form, state=str(sched.state))
