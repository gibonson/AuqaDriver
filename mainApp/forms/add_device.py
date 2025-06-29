from flask_wtf import FlaskForm
from mainApp.models.device import Device
from wtforms.validators import (
    ValidationError,
    DataRequired,
    IPAddress,
    Length,
    NumberRange,
)
from wtforms import StringField, SelectField, SubmitField, IntegerField


class AddDevice(FlaskForm):
    deviceStatusList = [("Ready", "Ready"), ("Not Ready", "Not Ready"), ("Old", "Old")]
    deviceSSLList = [("http", "http"), ("https", "https")]
    deviceProtocolList = [("html", "html"), ("json", "json")]
    deviceToScanList = [("True", "True"), ("False", "False")]

    # def validate_deviceIP(self, deviceIP_to_check):
    #     deviceIP = Device.query.filter(Device.deviceIP == deviceIP_to_check.data).first()
    #     if deviceIP:
    #         raise ValidationError('DevieIP already exist')

    deviceIP = StringField(
        label="deviceIP",
        validators=[
            DataRequired(),
            IPAddress(ipv4=True, ipv6=False, message="deviceIP: wrong IP format"),
        ],
    )
    deviceName = StringField(
        label="deviceName",
        validators=[
            DataRequired(),
            Length(
                min=3,
                max=20,
                message="deviceName: must be between 3 and 20 characters.",
            ),
        ],
    )
    deviceStatus = SelectField(
        label="deviceStatus", choices=deviceStatusList, validators=[DataRequired()]
    )
    devicePort = IntegerField(
        label="devicePort",
        validators=[
            NumberRange(
                min=1, max=65535, message="devicePort: must be between 1 and 65535."
            ),
        ],
        default=80,
    )
    deviceSSL = SelectField(
        label="deviceSSL", choices=deviceSSLList, validators=[DataRequired()]
    )
    deviceProtocol = SelectField(
        label="deviceConnectionProtocol",
        choices=deviceProtocolList,
        validators=[DataRequired()],
    )
    deviceToScan = SelectField(
        label="deviceToScan", choices=deviceToScanList, validators=[DataRequired()]
    )
    submit = SubmitField(label="Submit")
