# Standard library imports
from datetime import datetime, timedelta

# Third-party imports
from flask import Flask, Markup, flash, jsonify, redirect, render_template, request, url_for
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

# Local application/library specific imports
from mainApp import app, db, logger, sched
from mainApp.dashboard_data import DashboardData
from mainApp.email_operations import emailSender
from mainApp.forms.add_archive_report import AddArchiveReport
from mainApp.forms.add_archive_report_fnction import AddArchiveReportFunction
from mainApp.forms.add_device import AddDevice
from mainApp.forms.add_device_functions import AddDeviceFunctions
from mainApp.forms.add_function_scheduler import AddFunctionScheduler
from mainApp.forms.add_notification import AddNotification
from mainApp.forms.archive_search import ArchiveSearch
from mainApp.forms.send_email import EmailSend
from mainApp.models.archive import Archive, ArchiveAdder, ArchiveLister, ArchiveManager
from mainApp.models.archive_functions import ArchiveFunctions, ArchiveFunctionsLister, ArchiveFunctionsAdder
from mainApp.models.archive_report import ArchiveReport, ArchiveReportLister, ArchiveReporAdder
from mainApp.models.device import Devices, DeviceAdder, DeviceLister, DeviceManager 
from mainApp.models.function import DevicesFunctions, DeviceFunctionAdder, DeviceFunctionsLister, DeviceFunctionsManager
from mainApp.models.notification import Notification, NotificationLister, NotificationAdder, NotificationManager
from mainApp.models.scheduler import FunctionScheduler, FunctionSchedulerLister, FunctionSchedulereAdder, FunctionSchedulereManager
from mainApp.report_operations import ReportCreator
from mainApp.notification_operations import NotificationTrigger
from mainApp.scheduler_operations import sched_start
from mainApp.web_operations import LinkCreator, WebContentCollector
from mainApp.charts import Table


# -----------------------------------------
# create new DB
# -----------------------------------------

@app.route("/create")
def create():
    with app.app_context():
        db.create_all()
        requestData = {'addInfo': 'BD creation', 'deviceIP': '127.0.0.1', 'deviceName': 'Server', 'type': 'Log', 'value': 0}
        archiveAdder = ArchiveAdder(requestData)
        logger.critical("New database has been created")
    return redirect(url_for("get_jobs"))

# -----------------------------------------
# start page and 404
# -----------------------------------------

@ app.errorhandler(404)
def not_found(e):
    flash(f'404!', category='danger')
    return render_template('404.html', state=str(sched.state))

@app.errorhandler(OperationalError)
def handle_operational_error(error):
    logger.error(f"OperationalError: {error}")
    if "no such table" in str(error):
        flash(Markup("Try to <a href='/create'>create new DB</a>"), category='danger')
        return render_template('500.html', state=str(sched.state))
    return render_template('500.html', state=str(sched.state))

@app.route("/")
def hello_world():
    return redirect(url_for("get_jobs"))

# -----------------------------------------
# device section
# -----------------------------------------

@app.route("/device_list", methods=['POST', 'GET'])
def device_list():
    deviceLister = DeviceLister()
    devices = deviceLister.get_list()
    form = AddDevice()
    if form.validate_on_submit():
        deviceAdder = DeviceAdder(request.form.to_dict(flat=False))
        flash(str(deviceAdder), category='success')
        return redirect(url_for("device_list"))
    if form.errors != {}:
        logger.error("An error occurred while adding : %s", form.errors)
        flash(form.errors, category='danger')
    return render_template("devicesList.html", devices=devices, form=form, state=str(sched.state))

@app.route("/device_remove/<id>")
def device_remove(id):
    manager = DeviceManager(id)
    manager.remove_device()
    flash(str(manager), category='danger')
    return redirect(url_for("device_list"))

@app.route("/change_device_status/<id>")
def change_device_status(id):
    manager = DeviceManager(id)
    manager.change_status()
    flash(str(manager), category='danger')
    return redirect(url_for("device_list"))

# -----------------------------------------
# function section
# -----------------------------------------

@app.route("/functions_list", methods=['POST', 'GET'])
def functions_list():
    deviceFunctionsLister = DeviceFunctionsLister()
    devicesFunctions = deviceFunctionsLister.get_list()
    deviceLister = DeviceLister()
    devices = deviceLister.get_list()
    AddDeviceFunctions.deviceIdListUpdate()
    form = AddDeviceFunctions()
    if form.validate_on_submit():
        deviceFunctionAdder = DeviceFunctionAdder(request.form.to_dict(flat=False))
        flash(str(deviceFunctionAdder), category='success')
        return redirect(url_for("functions_list"))
    if form.errors != {}:
        logger.error("An error occurred while adding : %s", form.errors)
        flash(form.errors, category='danger')
    return render_template("functionsList.html", devicesFunctions=devicesFunctions, devices=devices, form=form, state=str(sched.state))


@app.route("/functions_list_link_creator/<id>")
def functions_list_link_creator(id):
    linkCreator = LinkCreator(id)
    flash(Markup('<a href="' + linkCreator.functions_list_link_creator() + '">' +
          linkCreator.functions_list_link_creator() + '</a>'), category='success')
    return redirect(url_for("functions_list"))


# -----------------------------------------
# scheduler section
# -----------------------------------------

@app.route("/scheduler_list", methods=['POST', 'GET'])
def scheduler_list():
    deviceLister = DeviceLister()
    devices = deviceLister.get_list()
    deviceFunctionsLister = DeviceFunctionsLister()
    devicesFunctions = deviceFunctionsLister.get_list()
    functionSchedulerLister = FunctionSchedulerLister()
    functionsScheduler = functionSchedulerLister.get_list()
    archiveFunctionsLister = ArchiveFunctionsLister()
    archiveFunctions = archiveFunctionsLister.get_list()
    AddFunctionScheduler.functionIdListUpdate()
    form = AddFunctionScheduler()
    if form.validate_on_submit():
        schedulerID = str(form.functionId.data) + str(form.trigger.data) + str(form.year.data) + str(
            form.month.data) + str(form.day.data) + str(form.day_of_week.data) + str(form.hour.data) + str(form.minute.data) + str(form.second.data)
        schedulerID = schedulerID.replace("None","-")
        print(schedulerID)
        number = FunctionScheduler.query.filter_by(
            schedulerID=schedulerID).first()
        if number:
            flash(form.schedulerID.data + " record exists in the DB", category='danger')
            return render_template("schedulerAdd.html", form=form, state=str(sched.state))
        functionSchedulereAdder = FunctionSchedulereAdder(request.form.to_dict(flat=False), schedulerID)
        flash(str(functionSchedulereAdder), category='success')
        return redirect(url_for("scheduler_list"))
    if form.errors != {}:  # validation errors
        logger.error("An error occurred while adding : %s", form.errors)
        flash(form.errors, category='danger')
    return render_template("schedulerList.html", functionsScheduler=functionsScheduler, devicesFunctions=devicesFunctions, devices=devices, archiveFunctions=archiveFunctions, state=str(sched.state), form=form, startswith = str.startswith, int = int)


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
    deviceLister = DeviceLister()
    devices = deviceLister.get_list()
    deviceFunctionsLister = DeviceFunctionsLister()
    devicesFunctions = deviceFunctionsLister.get_list()
    functionSchedulerLister = FunctionSchedulerLister()
    functionsScheduler = functionSchedulerLister.get_list()
    return render_template("SchedulerListWithJobs.html", functionsScheduler=functionsScheduler, devicesFunctions=devicesFunctions, devices=devices, get_jobs=sched.get_jobs(), state=str(sched.state), str = str, int = int)


@app.route("/scheduler_remove/<id>")
def scheduler_remove(id):
    manager = FunctionSchedulereManager(id)
    manager.remove_function_scheduler()
    flash(str(manager), category='danger')
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
    archiveLister=ArchiveLister()
    archive = archiveLister.get_list()
    dataSubOne = datetime.now() - timedelta(days=1)
    dataSubOneDay = dataSubOne.strftime("%Y-%m-%d %H:%M")

    if form.validate_on_submit():
        logger.debug(str(request.form.to_dict(flat=False)))
        logger.debug("date time to timestampStart: "  + str(datetime.timestamp(form.timestampStart.data)))
        logger.debug("date time to timestampStart: "  + str(datetime.timestamp(form.timestampEnd.data)))
        archive = Archive.query.filter(
            Archive.deviceIP.in_(form.deviceIP.data),
            Archive.addInfo.in_(form.addInfo.data),
            Archive.timestamp >= datetime.timestamp(form.timestampStart.data),
            Archive.timestamp <= datetime.timestamp(form.timestampEnd.data),
            Archive.type.in_(form.type.data)
        ).order_by(Archive.id.desc()).limit(form.limit.data)
    return render_template("archiveSearch.html", archive=archive, datetime=datetime, form=form, state=str(sched.state), dataSubOneDay=dataSubOneDay)

@app.route("/archive_remove/<id>")
def archive_remove(id):
    manager = ArchiveManager(id)
    manager.remove_archive()
    flash(str(manager), category='danger')
    return redirect(url_for("archive_list"))

# -----------------------------------------
# archive report section
# -----------------------------------------

@app.route("/archive_report_list", methods=['POST', 'GET'])
def archive_report_list():
    archiveReportLister = ArchiveReportLister()
    archiveReportList = archiveReportLister.get_list()

    AddArchiveReport.add_archive_report_lists_update()
    form = AddArchiveReport()
    if form.validate_on_submit():
        archiveReporAdder = ArchiveReporAdder(request.form.to_dict(flat=False))
        flash(str(archiveReporAdder), category='success')
        return redirect(url_for("archive_report_list"))
    if form.errors != {}:
        logger.error("An error occurred while adding : %s", form.errors)
        flash(form.errors, category='danger')
    return render_template("archiveReportList.html", archiveReportList=archiveReportList, form=form, state=str(sched.state))


# -----------------------------------------
# archive report functions section
# -----------------------------------------

@app.route("/archive_functions_list", methods=['POST', 'GET'])
def archive_functions_list():
    archiveFunctionsLister = ArchiveFunctionsLister()
    archiveFunctionsList = archiveFunctionsLister.get_list()

    AddArchiveReportFunction.add_archive_report_function_lists_update()
    form = AddArchiveReportFunction()
    if form.validate_on_submit():
        archiveFunctionsAdder = ArchiveFunctionsAdder(request.form.to_dict(flat=False))
        flash(str(archiveFunctionsAdder), category='success')
        return redirect(url_for("archive_functions_list"))
    if form.errors != {}:
        logger.error("An error occurred while adding : %s", form.errors)
        flash(form.errors, category='danger')
        return redirect(url_for("archive_report_functions_add"))
    
    return render_template("archiveReportFunctionsList.html", archiveFunctionsList=archiveFunctionsList, form=form, datetime=datetime, state=str(sched.state))

@app.route("/get_archive_report/<id>")
def get_archive_report(id):
    reportCreator = ReportCreator()
    one_line = reportCreator.create_one_line(id)
    return one_line

@app.route("/get_archive_report_all")
def get_archive_report_all():
    reportCreator = ReportCreator()
    report = reportCreator.create_all()
    return render_template("archiveReportListAll.html", report=report, state=str(sched.state))

# -----------------------------------------
# email sender
# -----------------------------------------

@app.route('/emailSend', methods=['POST', 'GET'])
def email_send():
    form = EmailSend()
    if form.validate_on_submit():
        emailSender(form.subject.data, form.message.data, flashMessage=True)
    return render_template("emailSend.html", form=form, state=str(sched.state))

# -----------------------------------------
# DB Dashboard
# -----------------------------------------

@app.route('/dashboard')
def dashboard():
    dashboard_data = DashboardData()
    dbSizeKB = dashboard_data.getDbSizeKB()
    sqlTable = dashboard_data.getSqlTable()
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
    # sched.remove_all_jobs()
    # sched.pause()
    # sched.delete_all_jobs()
    # sched.pause()
    # sched.shutdown(wait=False)
    return redirect(url_for("get_jobs"))

# -----------------------------------------
# json
# -----------------------------------------

@app.post('/api/addEvent')
def create_friend():
    requestData = request.get_json()
    NotificationTrigger(requestData=requestData)
    ArchiveAdder(requestData=requestData)
    return "OK"

# -----------------------------------------
# notification
# -----------------------------------------

@app.route("/notification_list", methods=['POST', 'GET'])
def notification_list():
    notificationLister = NotificationLister()
    notificationList = notificationLister.get_list()
    form = AddNotification()
    if form.validate_on_submit():
        notificationAdder = NotificationAdder(request.form.to_dict(flat=False))
        flash(str(notificationAdder), category='success')
        return redirect(url_for("notification_list"))
    if form.errors != {}:
        logger.error("An error occurred while adding : %s", form.errors)
        flash(form.errors, category='danger')
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
    chart = Table(delta=100)
    chart.reportGenerator()

    return "ok"

