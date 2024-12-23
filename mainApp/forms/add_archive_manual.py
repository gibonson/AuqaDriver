from flask_wtf import FlaskForm
from mainApp import app
from mainApp.models.device import Device
from wtforms.validators import DataRequired, Length, Optional
from wtforms import SelectField, SubmitField, IntegerField, TextAreaField


class AddArchiveManualRecord(FlaskForm):

    addInfoList= [("Add water[l]","Add water[l]"),("Take Water[l]","Take Water[l]"),("New plant[pcs]","New plant[pcs]"),("New Animal[pcs]","New Animal[pcs]"),("Status","Status")]
    typeList = [("Manual","Manual")]
    deviceList = []


    def deviceListUpdate():
        AddArchiveManualRecord.deviceList.clear()
        with app.app_context():
            devices = Device.query.filter(Device.deviceStatus=="Ready").all()
            for device in devices:
                AddArchiveManualRecord.deviceList.append(
                    ( device.deviceIP +  " -> " + device.deviceName, device.deviceIP +  " -> " + device.deviceName))


    device = SelectField(label='deviceIP -> name', validators= [DataRequired()], choices=deviceList)
    addInfo = SelectField(label='addInfo',validators= [DataRequired()], choices=addInfoList)
    value = IntegerField(label='value',validators= [DataRequired()])
    type = SelectField(label='type',validators= [DataRequired()], choices=typeList)
    comment = TextAreaField(label='comment', validators= [Optional(),Length(min=3, max=20, message='comment: must be between 1 and 100 characters.')])
    submit = SubmitField(label='Add Report')
