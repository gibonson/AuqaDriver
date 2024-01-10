from mainApp.routes import db

class Devices(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    deviceIP = db.Column(db.String())
    deviceName = db.Column(db.String())
    deviceDescription = db.Column(db.String())
    deviceStatus = db.Column(db.String())

    def __init__(self, deviceIP, deviceName, deviceDescription, deviceStatus):
        self.deviceIP = deviceIP
        self.deviceName = deviceName
        self.deviceDescription = deviceDescription
        self.deviceStatus = deviceStatus


class DevicesFunctions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    deviceId = db.Column(db.Integer(), db.ForeignKey(Devices.id))
    jobType = db.Column(db.String())
    actionLink = db.Column(db.String())
    functionDescription = db.Column(db.String())
    functionParameters = db.Column(db.String())

    def __init__(self, deviceId, jobType, actionLink, functionDescription, functionParameters):
        self.deviceId = deviceId
        self.jobType = jobType
        self.actionLink = actionLink
        self.functionDescription = functionDescription
        self.functionParameters = functionParameters


class FunctionScheduler(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    functionId = db.Column(db.Integer(), db.ForeignKey(DevicesFunctions.id))
    trigger = db.Column(db.String())
    schedulerID = db.Column(db.String())
    year = db.Column(db.Integer()) #4-digit year
    month = db.Column(db.Integer()) #(1-12)
    day = db.Column(db.Integer()) #(1-31)
    day_of_week = db.Column(db.String()) #mon,tue,wed,thu,fri,sat,sun
    hour = db.Column(db.Integer()) #(0-23)
    minute = db.Column(db.Integer()) #(0-59)
    second = db.Column(db.Integer()) #(0-59)

    def __init__(self, functionId , trigger, schedulerID, year , month , day , day_of_week , hour , minute, second):
        self.functionId = functionId
        self.trigger = trigger
        self.schedulerID = schedulerID
        self.year = year
        self.month = month
        self.day = day
        self.day_of_week = day_of_week
        self.hour = hour
        self.minute = minute
        self.second = second

class TypeAndUnits(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    unitNameFull = db.Column(db.String())
    unitNameShort = db.Column(db.String())
    isActive = db.Column(db.String())

    def __init__(self, name, unitNameFull, unitNameShort, isActive):
        self.name = name
        self.unitNameFull = unitNameFull
        self.unitNameShort = unitNameShort
        self.isActive = isActive

class Archive(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.Integer())
    deviceId = db.Column(db.String())
    value = db.Column(db.Integer())
    unit = db.Column(db.String())
    addInfo = db.Column(db.String())

    def __init__(self, timestamp, deviceId, value, unit, addInfo):
        self.timestamp = timestamp
        self.deviceId = deviceId
        self.value = value
        self.unit = unit
        self.addInfo = addInfo
