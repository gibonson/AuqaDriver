from flask_wtf import FlaskForm
from mainApp import app
from mainApp.models.archive import Archive
from wtforms.validators import DataRequired, Length, Optional
from wtforms import StringField, SelectField, IntegerField, SubmitField


class AddArchiveReport(FlaskForm):
    
    deviceIPList = []
    deviceNameList = []
    addInfoList = []
    typeList = []
    avgOrSumList = [("avg","Average"),("sum","Sum")]
    timerRangeHoursList = [(24,"Day"),(168,"Week"),(720,"30 days"),(8544,"356 days")]
    quantityValuesList = [(0,"0"),(10,"10"),(50,"50"),(100,"100")]

    def add_archive_report_lists_update():
        AddArchiveReport.deviceIPList.clear()
        AddArchiveReport.deviceNameList.clear()
        AddArchiveReport.addInfoList.clear()
        AddArchiveReport.typeList.clear()
        with app.app_context():
            deviceIPs = Archive.query.distinct(
                Archive.deviceIP).group_by(Archive.deviceIP)
            for deviceIP in deviceIPs:
                # print(deviceIP.deviceIP)
                AddArchiveReport.deviceIPList.append(
                    (deviceIP.deviceIP, deviceIP.deviceIP))

            deviceNames = Archive.query.distinct(
                Archive.deviceName).group_by(Archive.deviceName)
            for deviceName in deviceNames:
                # print(deviceName.deviceName)
                AddArchiveReport.deviceNameList.append(
                    (deviceName.deviceName, deviceName.deviceName))

            addInfos = Archive.query.distinct(
                Archive.addInfo).group_by(Archive.addInfo)
            for addInfo in addInfos:
                # print(addInfo.addInfo)
                AddArchiveReport.addInfoList.append((addInfo.addInfo, addInfo.addInfo))

            types = Archive.query.distinct(Archive.type).group_by(Archive.type)
            # print(deviceIPs)
            # print("deviceIPs")
            for type in types:
                # print(type.type)
                AddArchiveReport.typeList.append((type.type, type.type))

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