from flask_wtf import FlaskForm
from mainApp import app
from mainApp import logger
from mainApp.models.event import Event
from mainApp.models.event_scheduler import EventScheduler
# from mainApp.models.archive_report_package import ArchiveFunctions
from wtforms.validators import DataRequired, NumberRange
from wtforms import SelectField, SubmitField, HiddenField, IntegerField, ValidationError


class AddEventScheduler(FlaskForm):
       
    triggerList = [("interval", "interval"),("cron", "cron")]
    dayOfWeekList = [(None, None),("mon", "mon"),("tue", "tue"),("wed", "wed"),("thu", "thu"),("fri", "fri"),("sat", "sat")]
    dayList = [(0,"0"),(1,"1"),(2,"2"),(3,"3"),(4,"4"),(5,"5"),(6,"6"),(7,"7"),(8,"8"),(9,"9"),(10,"10"),(11,"11"),(12,"12"),(13,"13"),(14,"14"),(15,"15"),(16,"16"),(17,"17"),(18,"18"),(19,"19"),(20,"20"),(21,"21"),(22,"22"),(23,"23"),(24,"24"),(25,"25"),(26,"26"),(27,"27"),(28,"28"),(29,"29"),(30,"30"),(31,"31")]
    schedulerStatusList = [("Ready", "Ready"),("Not Ready", "Not Ready")]
    eventIdList = []

    # def eventIdListUpdate():
    #     AddEventScheduler.eventIdList.clear()
    #     with app.app_context():
    #         events = Event.query.all()
    #         for event in events:
    #             logger.debug(event.__dict__)
    #             device = Device.query.get(event.deviceId)
    #             if event.eventType == "Report":
    #                 AddEventScheduler.eventIdList.append((str(event.id), "Report: " + str(event.reportIds) + " " + str(event.eventDescription)))
    #             elif event.eventType == "Link":
    #                 if event.deviceId != 0:
    #                     AddEventScheduler.eventIdList.append((str(event.id), "Sensor: " + str(device.deviceIP) + " - " + str(device.deviceName) + ": " + " " + str(
    #                     event.eventLink) + " " + str(event.eventDescription)))
    #                 elif event.deviceId == 0:
    #                     AddEventScheduler.eventIdList.append((str(event.id), "External link: " + str(event.eventLink) + " " + str(event.eventDescription)))


    
    def validate_schedulerId(self, schedulerId_to_check):
            schedulerId_to_check = (str(self.eventId.data) + str(self.trigger.data) +str(self.day.data) + str(self.day_of_week.data) + str(self.hour.data) + str(self.minute.data) + str(self.second.data)).replace("None", "-").replace("interval", "I").replace("cron", "C")
            existing_scheduler = EventScheduler.query.filter_by(schedulerId=schedulerId_to_check).first()
            if existing_scheduler:
                raise ValidationError(f'schedulerId "{schedulerId_to_check}" już istnieje w bazie danych.')

    eventId = SelectField(label='eventId',choices = eventIdList, validators=[DataRequired()])
    trigger = SelectField(label='jobType', choices=triggerList)
    schedulerId = HiddenField()
    day = SelectField(label='day', choices=dayList)
    day_of_week = SelectField(label='dayOfWeekList', choices=dayOfWeekList)
    hour = IntegerField(label='hour',validators= [NumberRange(min=0, max=59, message='hour: must be between 0 and 23.')])
    minute = IntegerField(label='minute',validators= [NumberRange(min=0, max=59, message='minute: must be between 0 and 59.')])
    second = IntegerField(label='second',validators= [NumberRange(min=0, max=59, message='second: must be between 0 and 59.')])
    schedulerStatus = SelectField(label='schedulerStatus', choices=schedulerStatusList)
    submit = SubmitField(label='submit new')
