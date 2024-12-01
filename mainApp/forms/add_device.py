from flask_wtf import FlaskForm
from mainApp.models.device import Device
from wtforms.validators import ValidationError, DataRequired, IPAddress, Length
from wtforms import StringField, SelectField, SubmitField


class AddDevice(FlaskForm):
    deviceStatusList = [("Ready", "Ready"),("Not Ready", "Not Ready"),("Old", "Old")]

    def validate_deviceIP(self, deviceIP_to_check):
        deviceIP = Device.query.filter(Device.deviceIP == deviceIP_to_check.data).first()
        if deviceIP:
            raise ValidationError('DevieIP already exist')

    deviceIP = StringField(label='deviceIP', validators=[DataRequired(), IPAddress(ipv4=True, ipv6=False, message="deviceIP: wrong IP format")])
    deviceName = StringField(label='deviceName', validators= [DataRequired(),Length(min=3, max=20, message='deviceName: must be between 3 and 20 characters.')])
    deviceStatus = SelectField(label='deviceStatus',choices = deviceStatusList, validators=[DataRequired()])
    submit = SubmitField(label='Submit')