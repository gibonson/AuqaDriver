from mainApp import app, db, sched
from sqlalchemy import create_engine, text
from flask import Flask, render_template, redirect, url_for, request, flash, Markup, jsonify
from mainApp.forms import AddDevice, AddDeviceFunctions, AddFunctionScheduler, ArchiveSearch, EmailForm, AddArchiveReport, AddArchiveReportFunction, AddNotification
from mainApp.models.model import ArchiveFunctions, Notification
from mainApp.models.archive import Archive, ArchiveAdder, ArchiveLister, ArchiveManager
from mainApp.models.device import Devices, DeviceAdder, DeviceLister, DeviceManager
from mainApp.models.function import DevicesFunctions, DeviceFunctionsLister, DeviceFunctionAdder
from mainApp.models.scheduler import FunctionScheduler, FunctionSchedulerLister, FunctionSchedulereAdder
from mainApp.models.archive_report import ArchiveReport, ArchiveReportLister, ArchiveReporAdder
from mainApp.webContent import LinkCreator, WebContentCollector
from mainApp.report_creator import ReportCreator
from datetime import datetime, timedelta
from mainApp.scheduler_operations import sched_start
from mainApp.email_operations import emailSender
from mainApp.dashboard_data import DashboardData

from mainApp import logger

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

@app.route("/")
def hello_world():
    return redirect(url_for("get_jobs"))

# -----------------------------------------
# device section
# -----------------------------------------

@app.route("/device_add", methods=['POST', 'GET'])
def device_add():
    form = AddDevice()
    if form.validate_on_submit():
        deviceAdder = DeviceAdder(request.form.to_dict(flat=False))
        flash(str(deviceAdder), category='success')
        return redirect(url_for("device_list"))
    if form.errors != {}:
        logger.error("An error occurred while adding : %s", form.errors)
        flash(form.errors, category='danger')
    return render_template("deviceAdd.html", form=form, state=str(sched.state))

@app.route("/device_list")
def device_list():
    deviceLister = DeviceLister()
    devices = deviceLister.get_list()
    return render_template("devicesList.html", devices=devices, state=str(sched.state))

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

@app.route("/function_add", methods=['POST', 'GET'])
def function_add():
    AddDeviceFunctions.deviceIdListUpdate()
    form = AddDeviceFunctions()
    if form.validate_on_submit():
        deviceFunctionAdder = DeviceFunctionAdder(request.form.to_dict(flat=False))
        flash(str(deviceFunctionAdder), category='success')
        return redirect(url_for("functions_list"))
    if form.errors != {}:
        logger.error("An error occurred while adding : %s", form.errors)
        flash(form.errors, category='danger')
    return render_template("functionAdd.html", form=form, state=str(sched.state))


@app.route("/functions_list")
def functions_list():
    deviceFunctionsLister = DeviceFunctionsLister()
    devicesFunctions = deviceFunctionsLister.get_list()
    deviceLister = DeviceLister()
    devices = deviceLister.get_list()
    return render_template("functionsList.html", devicesFunctions=devicesFunctions, devices=devices, state=str(sched.state))


@app.route("/functions_list_link_creator/<id>")
def functions_list_link_creator(id):
    linkCreator = LinkCreator(id)
    flash(Markup('<a href="' + linkCreator.functions_list_link_creator() + '">' +
          linkCreator.functions_list_link_creator() + '</a>'), category='success')
    return redirect(url_for("functions_list"))


# -----------------------------------------
# scheduler section
# -----------------------------------------

@app.route("/scheduler_add", methods=['POST', 'GET'])
def scheduler_add():
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

    return render_template("schedulerAdd.html", form=form, state=str(sched.state))


@app.route("/scheduler_list")
def scheduler_list():
    deviceLister = DeviceLister()
    devices = deviceLister.get_list()
    deviceFunctionsLister = DeviceFunctionsLister()
    devicesFunctions = deviceFunctionsLister.get_list()
    functionSchedulerLister = FunctionSchedulerLister()
    functionsScheduler = functionSchedulerLister.get_list()
    archiveFunctions = ArchiveFunctions.query.all()
    return render_template("schedulerList.html", functionsScheduler=functionsScheduler, devicesFunctions=devicesFunctions, devices=devices, archiveFunctions=archiveFunctions, state=str(sched.state), startswith = str.startswith, int = int)


# -----------------------------------------
# job section
# -----------------------------------------

@app.route("/get_jobs")
def get_jobs():
    print(sched.get_jobs())
    for job in sched.get_jobs():
        print("JOB ID:" + job.id + " JOB NAME:" + job.name + " JOB TRIGGER:" +
              str(job.trigger) + " NEXT JOB:" + str(job.next_run_time))
    return render_template('getJobs.html', get_jobs=sched.get_jobs(), state=str(sched.state))


@app.route("/functions_scheduler_list_get_jobs")
def functions_scheduler_list_get_jobs():
    functionsScheduler = FunctionScheduler.query.all()
    devicesFunctions = DevicesFunctions.query.all()
    devices = Devices.query.all()
    return render_template("SchedulerListWithJobs.html", functionsScheduler=functionsScheduler, devicesFunctions=devicesFunctions, devices=devices, get_jobs=sched.get_jobs(), state=str(sched.state), str = str, int = int)


@app.route("/scheduler_remove/<id>")
def scheduler_remove(id):
    FunctionScheduler.query.filter(FunctionScheduler.id == id).delete()
    db.session.commit()
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

@app.route("/archive_list")
def archive_list():
    archiveLister = ArchiveLister()
    archive = archiveLister.get_list()
    return render_template("archiveList.html", archive=archive, datetime=datetime, state=str(sched.state))

@app.route("/archive_remove/<id>")
def archive_remove(id):
    manager = ArchiveManager(id)
    manager.remove_archive()
    flash(str(manager), category='danger')
    return redirect(url_for("archive_list"))

@app.route("/archive_search", methods=['POST', 'GET'])
def archive_search():
    ArchiveSearch.archive_search_lists_update()
    form = ArchiveSearch()
    archive = Archive.query.order_by(Archive.id.desc()).limit(100)
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


@app.route("/archive_report_add", methods=['POST', 'GET'])
def archive_report_add():
    AddArchiveReport.add_archive_report_lists_update()
    form = AddArchiveReport()
    if form.validate_on_submit():
        archiveReporAdder = ArchiveReporAdder(request.form.to_dict(flat=False))
        flash(str(archiveReporAdder), category='success')
        return redirect(url_for("archive_report_list"))
    if form.errors != {}:
        logger.error("An error occurred while adding : %s", form.errors)
        flash(form.errors, category='danger')
    return render_template("archiveReportAdd.html", form=form, state=str(sched.state))


@app.route("/archive_report_functions_add", methods=['POST', 'GET'])
def archive_report_functions_add():
    AddArchiveReportFunction.archiveReportIdList.clear()

    archiveReports = ArchiveReport.query.all()
    for archiveReport in archiveReports:
        AddArchiveReportFunction.archiveReportIdList.append(
            (archiveReport.id, archiveReport.title))
    form = AddArchiveReportFunction()

    if form.validate_on_submit():
        print(request.form.to_dict(flat=False))
        archive_report_function_to_add = ArchiveFunctions(title=form.title.data, description=form.description.data, archiveReportIds=str(form.archiveReportIds.data), functionStatus=form.functionStatus.data,)
        db.session.add(archive_report_function_to_add)
        db.session.commit()
        flash('Archive Report Functions added', category='success')
        return redirect(url_for("archive_report_functions_add"))

    return render_template("archiveReportFunctionsAdd.html", form=form, state=str(sched.state))

@app.route("/archive_functions_list")
def archive_functions_list():
    archiveFunctionsList = ArchiveFunctions.query.order_by(ArchiveFunctions.id.desc()).all()
    return render_template("archiveReportFunctionsList.html", archiveFunctionsList=archiveFunctionsList, datetime=datetime, state=str(sched.state))

@app.route("/archive_report_list")
def archive_report_list():
    archiveReportLister = ArchiveReportLister()
    archiveReportList = archiveReportLister.get_list()
    return render_template("archiveReportList.html", archiveReportList=archiveReportList, state=str(sched.state))

@app.route("/get_archive_report/<id>")
def get_archive_report(id):
    reportCreator = ReportCreator()
    reportCreator.create(id)
    return reportCreator.create(id)

@app.route("/get_archive_report_all")
def get_archive_report_all():
    reportCreator = ReportCreator()
    report = reportCreator.createAll()
    return render_template("archiveReportListAll.html", report=report, state=str(sched.state))

# -----------------------------------------
# email sender
# -----------------------------------------

@app.route('/emailSend', methods=['POST', 'GET'])
def email_send():
    form = EmailForm()
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
    ArchiveAdder(requestData)
    return "OK"

# -----------------------------------------
# notification
# -----------------------------------------

@app.route("/notification_add", methods=['POST', 'GET'])
def notification_add():
    form = AddNotification()
    if form.validate_on_submit():
        notification_to_add = Notification(description=form.description.data, deviceIP=form.deviceIP.data, deviceName=form.deviceName.data, addInfo =form.addInfo.data, type =form.type.data, condition =form.condition.data, value =form.value.data, notificationStatus =form.notificationStatus.data, notificationType =form.notificationType.data, functionId =form.functionId.data, message=form.message.data)
        db.session.add(notification_to_add)
        db.session.commit()
        flash('Notification added', category='success')
        return redirect(url_for("notification_add"))
    return render_template("notificationAdd.html", form=form, state=str(sched.state))

@app.route("/notification_list")
def notification_list():
    notificationList = Notification.query.order_by(Notification.id.desc()).all()
    return render_template("notificationList.html", notificationList=notificationList, datetime=datetime, state=str(sched.state))

@app.route("/change_notification_status/<id>")
def change_notification_status(id):
    notification = Notification.query.filter_by(id = id).first()
    if notification.notificationStatus == "Ready":
        notification.notificationStatus = "Not ready"
        flash('ID: '+ id + ', Notification status chnged to: ' +' Not ready', category='info')
        db.session.commit()
    elif notification.notificationStatus == "Not ready":
        notification.notificationStatus = "Ready"
        db.session.commit()
        flash('ID: '+ id + ', Notification status chnged to: ' + ' Ready', category='info')
    else:
        flash('ID: '+ id + ', Status error: ', category='info')
    return redirect(url_for("notification_list"))