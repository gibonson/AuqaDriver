from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, IntegerField, SubmitField, HiddenField, DateTimeLocalField, SelectMultipleField
from wtforms.validators import DataRequired, Length, IPAddress, NumberRange, AnyOf ,ValidationError
from mainApp import db

class AddDevice(FlaskForm):

    deviceIP = StringField(label='deviceIP', validators=[DataRequired(), IPAddress(ipv4=True, ipv6=False, message="deviceIP: wrong IP format")])
    deviceName = StringField(label='deviceName', validators= [DataRequired(),Length(min=3, max=20, message='deviceName: must be between 3 and 20 characters.')])
    deviceDescription = StringField(label='deviceDescription', validators= [DataRequired(),Length(min=3, max=20, message='deviceDescription: must be between 3 and 20 characters.')])
    submit = SubmitField(label='submit new')


class AddDeviceFunctionsCollector(FlaskForm):

    deviceIdList = []

    deviceId = SelectField(label='deviceId',choices = deviceIdList, validators=[DataRequired()])
    jobType = HiddenField(label='jobType', default= "jobCollector")
    actionLink = HiddenField(label='actionLink',default= None)
    functionDescription = StringField(label='functionDescription', validators = [DataRequired(),Length(min=3, max=20, message='functionDescription: must be between 3 and 20 characters.')])
    functionParameters = HiddenField(label='functionParameters', default= None)
    submit = SubmitField(label='submit new')


class AddDeviceFunctionsExecutor(FlaskForm):

    deviceIdList = []

    def validate_actionLink(self, actionLink_to_check):
        if "/"  not in actionLink_to_check.data: 
            raise ValidationError('actionLink: no / in actionLink')

    deviceId = SelectField(label='deviceId',choices = deviceIdList, validators=[DataRequired()])
    jobType = HiddenField(label='jobType', default= "jobExecutor")
    actionLink = StringField(label='actionLink', validators= [DataRequired(),Length(min=2, max=60, message='actionLink: must be between 2 and 60 characters.')])
    functionDescription = StringField(label='functionDescription', validators = [DataRequired(),Length(min=3, max=20, message='functionDescription: must be between 3 and 20 characters.')])
    functionParameters = StringField(label='functionParameters - parameter to execute with <...-...,> separator', validators = [Length(min=3, max=100, message='functionParameters: must be between 3 and 20 characters.')])
    submit = SubmitField(label='submit new')


class AddFunctionScheduler(FlaskForm):
        
    triggerList = [("interval", "interval"),("date", "date"),("cron", "cron")]
    dayList = [(None, None),("mon", "mon"),("tue", "tue"),("wed", "wed"),("thu", "thu"),("fri", "fri"),("sat", "sat")]
    yearList = [(None, None),(2023, 2023),(2024, 2024),(2025, 2025)]
    monthList = [(None,None),(1,"January"),(2,"February"),(3,"March"),(4,"April"),(5,"May"),(6,"June"),(7,"July"),(8,"August"),(9,"September"),(10,"October"),(11,"November"),(12,"December")]
    functionIdList = []

    functionId = SelectField(label='functionId',choices = functionIdList, validators=[DataRequired()])
    trigger = SelectField(label='jobType', choices=triggerList)
    schedulerID = StringField(label='schedulerID', validators= [DataRequired(),Length(min=2, max=60, message='actionLink: must be between 2 and 60 characters.')])
    year = SelectField(label='year', choices = yearList)
    month = SelectField(label='month', choices = monthList)
    day = IntegerField(label='day',validators= [NumberRange(min=1, max=31, message='day: must be between 1 and 31.')])
    day_of_week = SelectField(label='dayList', choices=dayList)
    hour = IntegerField(label='hour',validators= [NumberRange(min=0, max=59, message='hour: must be between 0 and 23.')])
    minute = IntegerField(label='minute',validators= [NumberRange(min=0, max=59, message='minute: must be between 0 and 59.')])
    second = IntegerField(label='second',validators= [NumberRange(min=0, max=59, message='second: must be between 0 and 59.')])
    submit = SubmitField(label='submit new')



class ArchiveSearch(FlaskForm):
    
    deviceIdList = []
    addInfoList = []
    unitList = []

    limit = IntegerField(label='limit',default=100, validators= [DataRequired(),NumberRange(min=0, max=1000, message='limit: must be between 1 and 1000')])
    timestampStart = DateTimeLocalField(label="Start Date:", format='%Y-%m-%dT%H:%M')
    timestampEnd = DateTimeLocalField(label="End Date:", format='%Y-%m-%dT%H:%M')
    deviceId = SelectMultipleField(label='deviceId', choices=deviceIdList)
    addInfo = SelectMultipleField(label='addInfo', choices=addInfoList)
    unit = SelectMultipleField(label='unit', choices=unitList)
    submit = SubmitField(label='Search')

