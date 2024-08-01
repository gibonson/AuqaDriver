from flask_wtf import FlaskForm
from flask_wtf.form import _Auto
from wtforms import StringField, SelectField, IntegerField, SubmitField, HiddenField, DateTimeLocalField, SelectMultipleField, TextAreaField
from wtforms.validators import DataRequired, Length, IPAddress, NumberRange, AnyOf ,ValidationError, Optional
from mainApp import db, app
from mainApp.models.device import Devices

class AddDevice(FlaskForm):
    deviceStatusList = [("Ready", "Ready"),("Not Ready", "Not Ready"),("Old", "Old")]

    def validate_deviceIP(self, deviceIP_to_check):
        deviceIP = Devices.query.filter(Devices.deviceIP == deviceIP_to_check.data).first()
        if deviceIP:
            raise ValidationError('DevieIP already exist')

    deviceIP = StringField(label='deviceIP', validators=[DataRequired(), IPAddress(ipv4=True, ipv6=False, message="deviceIP: wrong IP format")])
    deviceName = StringField(label='deviceName', validators= [DataRequired(),Length(min=3, max=20, message='deviceName: must be between 3 and 20 characters.')])
    deviceStatus = SelectField(label='deviceStatus',choices = deviceStatusList, validators=[DataRequired()])
    submit = SubmitField(label='submit new')

class AddDeviceFunctions(FlaskForm):
    functionStatusList = [("Ready", "Ready"),("Not Ready", "Not Ready")]
    deviceIdList = []

    def deviceIdListUpdate():
        AddDeviceFunctions.deviceIdList.clear()
        with app.app_context():
            devices = Devices.query.all()
            for device in devices:
                AddDeviceFunctions.deviceIdList.append(
                    (device.id, device.deviceIP + " " + device.deviceName + " " + device.deviceStatus))

    def validate_actionLink(self, actionLink_to_check):
        if "/"  not in actionLink_to_check.data: 
            raise ValidationError('actionLink: no / in actionLink')


    deviceId = SelectField(label='deviceId',choices = deviceIdList, validators=[DataRequired()])
    actionLink = StringField(label='actionLink', validators= [DataRequired(),Length(min=1, max=60, message='actionLink: must be between 1 and 60 characters.')])
    functionParameters = StringField(label='functionParameters - form values "value1=1&value2=1&value3=1&value4=1"', validators = [Length(max=100, message='functionParameters: must be between 3 and 20 characters.')])
    functionDescription = StringField(label='functionDescription', validators = [DataRequired(),Length(min=3, max=100, message='functionDescription: must be between 3 and 20 characters.')])
    functionStatus = SelectField(label='functionStatus',choices = functionStatusList, validators=[DataRequired()])
    submit = SubmitField(label='submit new')


class AddFunctionScheduler(FlaskForm):
        
    triggerList = [("interval", "interval"),("date", "date"),("cron", "cron")]
    dayOfWeekList = [(None, None),("mon", "mon"),("tue", "tue"),("wed", "wed"),("thu", "thu"),("fri", "fri"),("sat", "sat")]
    yearList = [(None, None),(2023, 2023),(2024, 2024),(2025, 2025)]
    monthList = [(None,None),(1,"January"),(2,"February"),(3,"March"),(4,"April"),(5,"May"),(6,"June"),(7,"July"),(8,"August"),(9,"September"),(10,"October"),(11,"November"),(12,"December")]
    dayList = [(0,"0"),(1,"1"),(2,"2"),(3,"3"),(4,"4"),(5,"5"),(6,"6"),(7,"7"),(8,"8"),(9,"9"),(10,"10"),(11,"11"),(12,"12"),(13,"13"),(14,"14"),(15,"15"),(16,"16"),(17,"17"),(18,"18"),(19,"19"),(20,"20"),(21,"21"),(22,"22"),(23,"23"),(24,"24"),(25,"25"),(26,"26"),(27,"27"),(28,"28"),(29,"29"),(30,"30"),(31,"31")]
    schedulerStatusList = [("Ready", "Ready"),("Not Ready", "Not Ready")]
    functionIdList = []

    functionId = SelectField(label='functionId',choices = functionIdList, validators=[DataRequired()])
    trigger = SelectField(label='jobType', choices=triggerList)
    schedulerID = HiddenField()
    year = SelectField(label='year', choices = yearList)
    month = SelectField(label='month', choices = monthList)
    day = SelectField(label='day', choices=dayList)
    day_of_week = SelectField(label='dayOfWeekList', choices=dayOfWeekList)
    hour = IntegerField(label='hour',validators= [NumberRange(min=0, max=59, message='hour: must be between 0 and 23.')])
    minute = IntegerField(label='minute',validators= [NumberRange(min=0, max=59, message='minute: must be between 0 and 59.')])
    second = IntegerField(label='second',validators= [NumberRange(min=0, max=59, message='second: must be between 0 and 59.')])
    schedulerStatus = SelectField(label='schedulerStatus', choices=schedulerStatusList)
    submit = SubmitField(label='submit new')

class ArchiveSearch(FlaskForm):
    
    deviceIPList = []
    addInfoList = []
    typeList = []

    limit = IntegerField(label='limit',default=100, validators= [DataRequired(),NumberRange(min=0, max=1000, message='limit: must be between 1 and 1000')])
    timestampStart = DateTimeLocalField(label="Start Date:", format='%Y-%m-%dT%H:%M')
    timestampEnd = DateTimeLocalField(label="End Date:", format='%Y-%m-%dT%H:%M')
    deviceIP = SelectMultipleField(label='deviceIP', choices=deviceIPList, validators=[Optional()])
    addInfo = SelectMultipleField(label='addInfo', choices=addInfoList, validators=[Optional()])
    type = SelectMultipleField(label='type', choices=typeList, validators=[Optional()])
    submit = SubmitField(label='Search')

class EmailForm(FlaskForm):

    subject = StringField(label='subject', validators = [Length(min=3, max=40, message='subject: must be between 3 and 40 characters.')])
    message = TextAreaField(label='Your message')
    submit = SubmitField(label='Send message')

class AddArchiveReport(FlaskForm):
    
    deviceIPList = []
    deviceNameList = []
    addInfoList = []
    typeList = []
    avgOrSumList = [("avg","Average"),("sum","Sum")]
    timerRangeHoursList = [(24,"Day"),(168,"Week"),(720,"30 days"),(8544,"356 days")]
    quantityValuesList = [(0,"0"),(10,"10"),(50,"50"),(100,"100")]

    title = StringField(label='title', validators= [DataRequired(),Length(min=1, max=30, message='title: must be between 1 and 30 characters.')])
    description = StringField(label='description', validators= [DataRequired(),Length(min=1, max=60, message='description: must be between 1 and 60 characters.')])
    deviceIP = SelectField(label='deviceIP', choices=deviceIPList)
    deviceName = SelectField(label='deviceName', choices=deviceNameList)
    addInfo = SelectField(label='addInfo', choices=addInfoList)
    type = SelectField(label='type', choices=typeList)
    avgOrSum = SelectField(label='avgOrSum', choices=avgOrSumList)
    timerRangeHours = SelectField(label='timerRangeHours', choices=timerRangeHoursList)
    quantityValues = SelectField(label='quantityValues', choices=quantityValuesList)
    minValue = IntegerField(label='minValue',validators=[Optional()])
    okMinValue = IntegerField(label='okMinValue',validators=[Optional()])
    okMaxValue = IntegerField(label='okMaxValue',validators=[Optional()])
    maxValue = IntegerField(label='maxValue',validators=[Optional()])
    submit = SubmitField(label='Add Report')

class AddArchiveReportFunction(FlaskForm):

    archiveReportIdList = []
    archiveFunctionStatus = [("Ready", "Ready"),("Not Ready", "Not Ready")]

    title = StringField(label='title', validators = [DataRequired(),Length(min=3, max=20, message='title: must be between 3 and 20 characters.')])
    description = StringField(label='description', validators=[Optional()])
    archiveReportIds = SelectMultipleField(coerce=int, label='archiveReportIds', choices=archiveReportIdList)
    functionStatus = SelectField(label='functionStatus',choices = archiveFunctionStatus, validators=[DataRequired()])
    submit = SubmitField(label='Add Report')


class AddNotification(FlaskForm):

    conditionValuesList = [("less","less"),("more","more"),("equal","equal")]
    notificationStatusValuesList = [("Ready","Ready"),("Not ready","Not ready")]
    notificationTypeValuesList = [("email","email"),("function","function")]

    description = StringField(label='description', validators= [DataRequired(),Length(min=1, max=60, message='description: must be between 1 and 60 characters.')])
    deviceIP = StringField(label='deviceIP', validators=[DataRequired(), IPAddress(ipv4=True, ipv6=False, message="deviceIP: wrong IP format")])
    deviceName = StringField(label='deviceName', validators= [DataRequired(),Length(min=3, max=20, message='deviceName: must be between 3 and 20 characters.')])
    addInfo = StringField(label='addInfo', validators= [DataRequired(),Length(min=3, max=20, message='addInfo: must be between 3 and 20 characters.')])
    type = StringField(label='type', validators= [DataRequired(),Length(min=3, max=20, message='type: must be between 3 and 10 characters.')])
    condition = SelectField(label='condition', choices=conditionValuesList)
    value = IntegerField(label='value',validators= [DataRequired()])
    notificationStatus = SelectField(label='notificationStatus', choices=notificationStatusValuesList) # Ready, Not ready
    notificationType = SelectField(label='notificationType', choices=notificationTypeValuesList) # email, function
    functionId = IntegerField(label='functionId',validators=[Optional()])
    message = StringField(label='message',validators=[Optional()])
    submit = SubmitField(label='Add Report')

