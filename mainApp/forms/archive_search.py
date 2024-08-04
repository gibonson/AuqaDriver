from flask_wtf import FlaskForm
from mainApp import app
from mainApp.models.archive import Archive
from wtforms.validators import DataRequired, NumberRange, Optional
from wtforms import IntegerField, DateTimeLocalField, SelectMultipleField, SubmitField


class ArchiveSearch(FlaskForm):
    
    deviceIPList = []
    addInfoList = []
    typeList = []

    def archive_search_lists_update():
        ArchiveSearch.deviceIPList.clear()
        ArchiveSearch.addInfoList.clear()
        ArchiveSearch.typeList.clear()
        with app.app_context():
            archiveAddInfos = Archive.query.distinct(
                Archive.addInfo).group_by(Archive.addInfo)
            for archiveAddInfo in archiveAddInfos:
                # print(archiveAddInfo.addInfo)
                ArchiveSearch.addInfoList.append(
                    (archiveAddInfo.addInfo, archiveAddInfo.addInfo))

            deviceIds = Archive.query.distinct(
                Archive.deviceIP).group_by(Archive.deviceIP)
            for deviceId in deviceIds:
                # print(deviceId.deviceIP)
                ArchiveSearch.deviceIPList.append(
                    (deviceId.deviceIP, deviceId.deviceIP))

            types = Archive.query.distinct(Archive.type).group_by(Archive.type)
            for type in types:
                # print(type.type)
                ArchiveSearch.typeList.append((type.type, type.type))

    limit = IntegerField(label='limit',default=100, validators= [DataRequired(),NumberRange(min=0, max=1000, message='limit: must be between 1 and 1000')])
    timestampStart = DateTimeLocalField(label="Start Date:", format='%Y-%m-%dT%H:%M')
    timestampEnd = DateTimeLocalField(label="End Date:", format='%Y-%m-%dT%H:%M')
    deviceIP = SelectMultipleField(label='deviceIP', choices=deviceIPList, validators=[Optional()])
    addInfo = SelectMultipleField(label='addInfo', choices=addInfoList, validators=[Optional()])
    type = SelectMultipleField(label='type', choices=typeList, validators=[Optional()])
    submit = SubmitField(label='Search')