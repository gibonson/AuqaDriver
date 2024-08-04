from mainApp.routes import db


# class ArchiveReport(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     title = db.Column(db.String())
#     description = db.Column(db.String())
#     deviceIP = db.Column(db.String())
#     deviceName = db.Column(db.String())
#     addInfo = db.Column(db.String())
#     type = db.Column(db.String())
#     avgOrSum = db.Column(db.String())
#     timerRangeHours = db.Column(db.Integer())
#     quantityValues = db.Column(db.Integer())
#     minValue = db.Column(db.Integer())
#     okMinValue = db.Column(db.Integer())
#     okMaxValue = db.Column(db.Integer())
#     maxValue = db.Column(db.Integer())

#     def __init__(self, deviceIP, title, description, deviceName, addInfo, type, avgOrSum, timerRangeHours, quantityValues, minValue, okMinValue, okMaxValue, maxValue):
#         self.deviceIP = deviceIP
#         self.title = title
#         self.description = description
#         self.deviceName = deviceName
#         self.addInfo = addInfo
#         self.type = type
#         self.avgOrSum = avgOrSum
#         self.timerRangeHours = timerRangeHours
#         self.quantityValues = quantityValues
#         self.minValue = minValue
#         self.okMinValue = okMinValue
#         self.okMaxValue = okMaxValue
#         self.maxValue = maxValue

class ArchiveFunctions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String())
    description = db.Column(db.String())
    archiveReportIds = db.Column(db.String())
    functionStatus = db.Column(db.String())

    def __init__(self, title, description, archiveReportIds, functionStatus):
        self.title = title
        self.description = description
        self.archiveReportIds = archiveReportIds
        self.functionStatus = functionStatus

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String())
    deviceIP = db.Column(db.String())
    deviceName = db.Column(db.String())
    addInfo = db.Column(db.String())
    type = db.Column(db.String())
    condition = db.Column(db.String()) # less more equal 
    value = db.Column(db.Integer())
    notificationStatus = db.Column(db.String())# Ready, Not ready
    notificationType = db.Column(db.String()) # email, function
    functionId = db.Column(db.String())
    message = db.Column(db.String())

    def __init__(self, description, deviceIP, deviceName, addInfo, type, condition, value, notificationStatus, notificationType, functionId, message):
        self.description = description
        self.deviceIP = deviceIP
        self.deviceName = deviceName
        self.addInfo = addInfo
        self.type = type
        self.condition = condition
        self.value = value
        self.notificationStatus = notificationStatus
        self.notificationType = notificationType
        self.functionId = functionId
        self.message = message