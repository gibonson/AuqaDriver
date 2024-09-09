from flask_wtf import FlaskForm
from mainApp import app
from mainApp.models.archive import Archive
from wtforms.validators import DataRequired, NumberRange, Optional
from wtforms import IntegerField, DateTimeLocalField, SelectMultipleField, SubmitField, SelectField


class ChartsSearch(FlaskForm):

    recordTypeList = []
    intervalTypeList = [("Hour", "hour"),("Day", "day"),("Month", "month")]

    def archive_search_lists_update():
        ChartsSearch.recordTypeList.clear()
        with app.app_context():
            recordTypes = Archive.query.with_entities(
                Archive.deviceIP,
                Archive.deviceName,
                Archive.addInfo,
                Archive.type
            ).distinct().all()
            for recordType in recordTypes:
                ChartsSearch.recordTypeList.append(
                    (recordType.deviceIP + " -> " + recordType.deviceName + " -> " + recordType.addInfo + " -> " + recordType.type, recordType.deviceIP + " -> " + recordType.deviceName + " -> " + recordType.addInfo + " -> " + recordType.type))
            ChartsSearch.recordTypeList.sort()

    limit = IntegerField(label='limit', default=100, validators=[DataRequired(
    ), NumberRange(min=0, max=1000, message='limit: must be between 1 and 1000')])
    timestampStart = DateTimeLocalField(
        label="Start Date:", format='%Y-%m-%dT%H:%M')
    timestampEnd = DateTimeLocalField(
        label="End Date:", format='%Y-%m-%dT%H:%M')
    recordType = SelectMultipleField(
        label='recordType', choices=recordTypeList, validators=[Optional()])
    intervalType= SelectField(
        label='intervalType', choices=intervalTypeList, validators=[Optional()])
    submit = SubmitField(label='Search')