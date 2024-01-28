from mainApp import app, db, sched
from flask import Flask, render_template ,redirect, url_for, request, flash
from mainApp.forms import AddDevice, AddDeviceFunctions, AddFunctionScheduler, ArchiveSearch
from mainApp.models import Devices, DevicesFunctions, FunctionScheduler, Archive
from mainApp.webContent import LinkCreator, WebContentCollector
import time
from datetime import datetime, timedelta
from mainApp.job_operations import schedStart

# -----------------------------------------
# create new DB
# -----------------------------------------
@app.route("/create")
def create():
    with app.app_context():
        db.create_all()
        timestamp = round(time.time())
        addInfo = "BD creation"
        deviceName = "Server"
        deviceIP = "127.0.0.1"
        type = "Log"
        value = 0
        add_to_archiwe = Archive(timestamp=timestamp,deviceIP = deviceIP, deviceName= deviceName, addInfo = addInfo, value= value, type = type)
        db.session.add(add_to_archiwe)
        db.session.commit()
        flash('DB creation Success', category='success')
    return redirect(url_for("get_jobs"))


# -----------------------------------------
# device section
# -----------------------------------------

@app.route("/device_add", methods=['POST', 'GET'])
def device_add():
    form = AddDevice()
    if form.validate_on_submit():
        devcice_to_add = Devices(deviceIP=form.deviceIP.data, deviceName=form.deviceName.data, deviceStatus=form.deviceStatus.data)
        db.session.add(devcice_to_add)
        db.session.commit()
        flash('Device added', category='success')
        return redirect(url_for("device_list"))
    
    if form.errors != {}:  # validation errors
        print(form.errors)
        flash(form.errors, category='danger')
        # for err_msg in form.errors.values():
        #     print(err_msg)
        #     flash(err_msg[0], category='danger')
    return render_template("deviceAdd.html", form = form, state = str(sched.state))

@app.route("/device_list")
def device_list():
    devices = Devices.query.all()
    return render_template("devicesList.html", devices = devices, state = str(sched.state))


# -----------------------------------------
# function section
# -----------------------------------------

@app.route("/function_add", methods=['POST', 'GET'])
def function_add():
    AddDeviceFunctions.deviceIdList.clear()
    devices = Devices.query.all()
    for device in devices:
        print(device.id)
        print(device.deviceIP)
        print(device.deviceName)
        print(device.deviceStatus)
        AddDeviceFunctions.deviceIdList.append((device.id, device.deviceIP + " " + device.deviceName + " " + device.deviceStatus))

    form = AddDeviceFunctions()
    if form.validate_on_submit():
        function_to_add = DevicesFunctions(deviceId=form.deviceId.data, actionLink=form.actionLink.data, functionDescription=form.functionDescription.data, functionParameters=form.functionParameters.data, functionStatus=form.functionStatus.data)
        db.session.add(function_to_add)
        db.session.commit()
        flash('OK', category='success')
        return redirect(url_for("functions_list"))
       
    if form.errors != {}:  # validation errors
        print(form.errors)
        flash(form.errors, category='danger')

    return render_template("functionAdd.html", form = form, state = str(sched.state))


@app.route("/functions_list")
def functions_list():
    devicesFunctions = DevicesFunctions.query.all()
    devices = Devices.query.all()
    return render_template("functionsList.html", devicesFunctions = devicesFunctions, devices = devices, state = str(sched.state))


@app.route("/functions_list_link_creator/<id>")
def functions_list_link_creator(id):
    linkCreator = LinkCreator(id)
    flash(linkCreator.functions_list_link_creator(), category='success')
    return redirect(url_for("functions_list"))


# -----------------------------------------
# scheduler section
# -----------------------------------------

@app.route("/scheduler_add", methods=['POST', 'GET'])
def scheduler_add():
    AddFunctionScheduler.functionIdList.clear()

    devicesFunctions = DevicesFunctions.query.all()
    for devicesFunction in devicesFunctions:
        print(devicesFunction.id)
        print(devicesFunction.deviceId)
        print(devicesFunction.actionLink)
        print(devicesFunction.functionDescription)
        print(devicesFunction.functionParameters)
        device = Devices.query.get(devicesFunction.deviceId)
        AddFunctionScheduler.functionIdList.append((devicesFunction.id, str(device.deviceIP) + " - " + str(device.deviceName) + ": " +  " " + str(devicesFunction.actionLink) + " " + str(devicesFunction.functionDescription) + " " + str(devicesFunction.functionParameters) ))

    form = AddFunctionScheduler()
    if form.validate_on_submit():
        # scheduler_to_add = FunctionScheduler(functionId = str(form.functionId.data), trigger = form.trigger.data, schedulerID = form.schedulerID.data, year = form.year.data, month = form.month.data, day = form.day.data, day_of_week = form.day_of_week.data, hour = form.hour.data, minute = form.minute.data, second = form.second.data, schedulerStatus = form.schedulerStatus.data)
        schedulerID = str(form.functionId.data) + str(form.trigger.data) + str(form.year.data) + str(form.month.data) + str(form.day.data) + str(form.day_of_week.data) + str(form.hour.data) + str(form.minute.data) + str(form.second.data)
        number = FunctionScheduler.query.filter_by(schedulerID=schedulerID).first()
        if number:
            flash(schedulerID + " record exists in the DB", category='danger')
            return render_template("schedulerAdd.html", form = form, state = str(sched.state))

        scheduler_to_add = FunctionScheduler(functionId = str(form.functionId.data), trigger = form.trigger.data, schedulerID = schedulerID, year = form.year.data, month = form.month.data, day = form.day.data, day_of_week = form.day_of_week.data, hour = form.hour.data, minute = form.minute.data, second = form.second.data, schedulerStatus = form.schedulerStatus.data)
        db.session.add(scheduler_to_add)
        db.session.commit()
        flash('OK', category='success')
        return redirect(url_for("scheduler_list"))
    
    if form.errors != {}:  # validation errors
        print(form.errors)
        flash(form.errors, category='danger')

    return render_template("schedulerAdd.html", form = form, state = str(sched.state))


# -----------------------------------------
# archive section
# -----------------------------------------

@app.route("/archive_list")
def archive_list():
    # archive = Archive.query.all()
    archive = Archive.query.order_by(Archive.id.desc()).limit(10)
    return render_template("archiveList.html", archive = archive, datetime = datetime, state = str(sched.state))

@app.route("/archive_search", methods=['POST', 'GET'])
def archive_search():
    ArchiveSearch.deviceIPList.clear()
    ArchiveSearch.addInfoList.clear()
    ArchiveSearch.typeList.clear()

    archiveAddInfos = Archive.query.distinct(Archive.addInfo).group_by(Archive.addInfo)
    for archiveAddInfo in archiveAddInfos:
        print(archiveAddInfo.addInfo)
        ArchiveSearch.addInfoList.append((archiveAddInfo.addInfo, archiveAddInfo.addInfo))

    deviceIds = Archive.query.distinct(Archive.deviceIP).group_by(Archive.deviceIP)
    for deviceId in deviceIds:
        print(deviceId.deviceIP)
        ArchiveSearch.deviceIPList.append((deviceId.deviceIP, deviceId.deviceIP))

    types = Archive.query.distinct(Archive.type).group_by(Archive.type)
    for type in types:
        print(type.type)
        ArchiveSearch.typeList.append((type.type, type.type))

    form = ArchiveSearch()
    # archive = Archive.query.all()
    archive = Archive.query.order_by(Archive.id.desc()).limit(100)
    dataSubOne = datetime.now() - timedelta(days=1)
    dataSubOneDay = dataSubOne.strftime("%Y-%m-%d %H:%M")

    if form.validate_on_submit():
        print(form.limit.data)
        print(form.timestampStart.data)
        print(datetime.timestamp(form.timestampStart.data))
        print(form.timestampEnd.data)
        print(datetime.timestamp(form.timestampEnd.data))
        print(form.deviceIP.data)
        print(form.addInfo.data)
        print(form.type.data)
        archive = Archive.query.filter(
            Archive.deviceIP.in_(form.deviceIP.data),
            Archive.addInfo.in_(form.addInfo.data),
            Archive.timestamp >= datetime.timestamp(form.timestampStart.data),
            Archive.timestamp <= datetime.timestamp(form.timestampEnd.data),
            Archive.type.in_(form.type.data)
            ).order_by(Archive.id.desc()).limit(form.limit.data)
    return render_template("archiveSearch.html",archive = archive, datetime = datetime, form = form, state = str(sched.state), dataSubOneDay = dataSubOneDay)



















@app.route("/scheduler_remove/<id>")
def scheduler_remove(id):
    FunctionScheduler.query.filter(FunctionScheduler.id == id).delete()
    db.session.commit()
    return redirect(url_for("get_jobs"))


@app.route("/scheduler_list")
def scheduler_list():
    functionsScheduler = FunctionScheduler.query.all()
    devicesFunctions = DevicesFunctions.query.all()
    devices = Devices.query.all()
    return render_template("schedulerList.html", functionsScheduler = functionsScheduler, devicesFunctions = devicesFunctions, devices = devices, state = str(sched.state))


@app.route("/functions_scheduler_list_get_jobs")
def functions_scheduler_list_get_jobs():
    functionsScheduler = FunctionScheduler.query.all()
    devicesFunctions = DevicesFunctions.query.all()
    devices = Devices.query.all()
    return render_template("SchedulerListWithJobs.html", functionsScheduler = functionsScheduler, devicesFunctions = devicesFunctions, devices = devices, get_jobs=sched.get_jobs(), state = str(sched.state))





@app.route("/")
def hello_world():
    return redirect(url_for("get_jobs"))


@app.route("/get_jobs")
def get_jobs():
    print(sched.get_jobs())
    for job in sched.get_jobs():
        print("JOB ID:" + job.id + " JOB NAME:" + job.name + " JOB TRIGGER:" + str(job.trigger) + " NEXT JOB:" + str(job.next_run_time))
    return render_template('getJobs.html', get_jobs=sched.get_jobs(), state = str(sched.state))


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
    schedStart(sched, runSchedulerID)
    return redirect(url_for("get_jobs"))


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
    schedStart(sched)
    return redirect(url_for("get_jobs"))


@app.route("/shutdown")
def shutdown():
    # sched.remove_all_jobs()
    # sched.pause()
    # sched.delete_all_jobs()
    # sched.pause()
    # sched.shutdown(wait=False)
    return redirect(url_for("get_jobs"))
