from flask_wtf import FlaskForm
from mainApp import app
from mainApp.models.device import Devices
from wtforms.validators import ValidationError, DataRequired, Length
from wtforms import SelectField, StringField, SubmitField


class AddEvent(FlaskForm):
    eventStatusList = [("Ready", "Ready"),("Not Ready", "Not Ready")]
    deviceIdList = []

    def deviceIdListUpdate():
        AddEvent.deviceIdList.clear()
        with app.app_context():
            devices = Devices.query.filter(Devices.deviceStatus=="Ready").all()
            for device in devices:
                AddEvent.deviceIdList.append(
                    (device.id, device.deviceIP + " " + device.deviceName))

    def validate_eventLink(self, eventLink_to_check):
        if "/"  not in eventLink_to_check.data: 
            raise ValidationError('eventLink: no / in eventLink')


    deviceId = SelectField(label='deviceId',choices = deviceIdList, validators=[DataRequired()])
    eventLink = StringField(label='eventLink - form values "value1=1&value2=1&value3=1&value4=1', validators= [DataRequired(),Length(min=1, max=60, message='eventLink: must be between 1 and 60 characters.')])
    eventDescription = StringField(label='eventDescription', validators = [DataRequired(),Length(min=3, max=100, message='eventDescription: must be between 3 and 20 characters.')])
    eventStatus = SelectField(label='eventStatus',choices = eventStatusList, validators=[DataRequired()])
    submit = SubmitField(label='submit new')
