from flask_wtf import FlaskForm
from mainApp import app
from mainApp.models.device import Device
from mainApp.models.archive_report import ArchiveReport
from wtforms.validators import ValidationError, DataRequired, Length
from wtforms import SelectField, StringField, SubmitField, SelectMultipleField, HiddenField, TextAreaField


class AddEventLink(FlaskForm):
    eventStatusList = [("Ready", "Ready"),("Not Ready", "Not Ready")]
    deviceIdList = []

    def deviceIdListUpdate():
        AddEventLink.deviceIdList.clear()
        with app.app_context():
            devices = Device.query.filter(Device.deviceStatus=="Ready").all()
            AddEventLink.deviceIdList.append((0, "External Link"))
            for device in devices:
                AddEventLink.deviceIdList.append(
                    (device.id, device.deviceIP + " " + device.deviceName))


    deviceId = SelectField(label='deviceId', choices = deviceIdList, validators=[DataRequired()])
    eventLink = StringField(label='eventLink with \ or json or full address')
    eventDescription = StringField(label='eventDescription', validators = [DataRequired(),Length(min=3, max=100, message='eventDescription: must be between 3 and 20 characters.')])
    eventStatus = SelectField(label='eventStatus', choices = eventStatusList, validators=[DataRequired()])
    eventType = HiddenField(default="Link")
    reportIds = HiddenField(default="-")
    submitLink = SubmitField(label='Add event')


class AddEventReport(FlaskForm):
    eventStatusList = [("Ready", "Ready"),("Not Ready", "Not Ready")]
    deviceIdList = [("127.0.0.1","Server")]
    archiveReportIdList = []

    def reportIdListUpdate():
        AddEventReport.archiveReportIdList.clear()
        with app.app_context():
            archiveReports = ArchiveReport.query.distinct(
                ArchiveReport.id).group_by(ArchiveReport.id)
            for archiveReport in archiveReports:
                AddEventReport.archiveReportIdList.append(
                    (archiveReport.id, archiveReport.title))

    deviceId = HiddenField(default=0)
    eventLink = HiddenField(default="-")
    eventDescription = StringField(label='eventDescription', validators = [DataRequired(),Length(min=3, max=100, message='eventDescription: must be between 3 and 20 characters.')])
    eventStatus = SelectField(label='eventStatus',choices = eventStatusList, validators=[DataRequired()])
    eventType = HiddenField(default="Report")
    reportIds = SelectMultipleField(coerce=int, label='reportIds', choices=archiveReportIdList, validators=[DataRequired()])
    submitReport = SubmitField(label='Add event')