from flask_wtf import FlaskForm
from mainApp import app
from mainApp import logger
from mainApp.models.device import Devices
from mainApp.models.function import DevicesFunctions
from mainApp.models.archive_functions import ArchiveFunctions
from wtforms.validators import DataRequired, NumberRange
from wtforms import SelectField, SubmitField, HiddenField, IntegerField


class AddFunctionScheduler(FlaskForm):
       
    triggerList = [("interval", "interval"),("date", "date"),("cron", "cron")]
    dayOfWeekList = [(None, None),("mon", "mon"),("tue", "tue"),("wed", "wed"),("thu", "thu"),("fri", "fri"),("sat", "sat")]
    yearList = [(None, None),(2023, 2023),(2024, 2024),(2025, 2025)]
    monthList = [(None,None),(1,"January"),(2,"February"),(3,"March"),(4,"April"),(5,"May"),(6,"June"),(7,"July"),(8,"August"),(9,"September"),(10,"October"),(11,"November"),(12,"December")]
    dayList = [(0,"0"),(1,"1"),(2,"2"),(3,"3"),(4,"4"),(5,"5"),(6,"6"),(7,"7"),(8,"8"),(9,"9"),(10,"10"),(11,"11"),(12,"12"),(13,"13"),(14,"14"),(15,"15"),(16,"16"),(17,"17"),(18,"18"),(19,"19"),(20,"20"),(21,"21"),(22,"22"),(23,"23"),(24,"24"),(25,"25"),(26,"26"),(27,"27"),(28,"28"),(29,"29"),(30,"30"),(31,"31")]
    schedulerStatusList = [("Ready", "Ready"),("Not Ready", "Not Ready")]
    functionIdList = []

    def functionIdListUpdate():
        AddFunctionScheduler.functionIdList.clear()
        with app.app_context():
            devicesFunctions = DevicesFunctions.query.all()
            for devicesFunction in devicesFunctions:
                logger.debug(devicesFunction.__dict__)
                device = Devices.query.get(devicesFunction.deviceId)
                AddFunctionScheduler.functionIdList.append((str(devicesFunction.id), "Sensor: " + str(device.deviceIP) + " - " + str(device.deviceName) + ": " + " " + str(
                    devicesFunction.actionLink) + " " + str(devicesFunction.functionDescription) + " " + str(devicesFunction.functionParameters)))
            
            archiveFunctions = ArchiveFunctions.query.all()
            for archiveFunction in archiveFunctions:
                logger.debug(archiveFunction.__dict__)
                AddFunctionScheduler.functionIdList.append(("R" + str(archiveFunction.id), "Report: " + str(archiveFunction.title) + " - " + archiveFunction.description + " - " + archiveFunction.archiveReportIds))

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
