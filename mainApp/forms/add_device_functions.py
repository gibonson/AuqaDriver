from flask_wtf import FlaskForm
from mainApp import app
from mainApp.models.device import Devices
from wtforms.validators import ValidationError, DataRequired, Length
from wtforms import SelectField, StringField, SubmitField


class AddDeviceFunctions(FlaskForm):
    functionStatusList = [("Ready", "Ready"),("Not Ready", "Not Ready")]
    deviceIdList = []

    def deviceIdListUpdate():
        AddDeviceFunctions.deviceIdList.clear()
        with app.app_context():
            devices = Devices.query.filter(Devices.deviceStatus=="Ready").all()
            for device in devices:
                AddDeviceFunctions.deviceIdList.append(
                    (device.id, device.deviceIP + " " + device.deviceName))

    def validate_actionLink(self, actionLink_to_check):
        if "/"  not in actionLink_to_check.data: 
            raise ValidationError('actionLink: no / in actionLink')


    deviceId = SelectField(label='deviceId',choices = deviceIdList, validators=[DataRequired()])
    actionLink = StringField(label='actionLink', validators= [DataRequired(),Length(min=1, max=60, message='actionLink: must be between 1 and 60 characters.')])
    functionParameters = StringField(label='functionParameters - form values "value1=1&value2=1&value3=1&value4=1"', validators = [Length(max=100, message='functionParameters: must be between 3 and 20 characters.')])
    functionDescription = StringField(label='functionDescription', validators = [DataRequired(),Length(min=3, max=100, message='functionDescription: must be between 3 and 20 characters.')])
    functionStatus = SelectField(label='functionStatus',choices = functionStatusList, validators=[DataRequired()])
    submit = SubmitField(label='submit new')
