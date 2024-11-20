from flask_wtf import FlaskForm
from mainApp import app
from mainApp.models.archive_report import ArchiveReport
from wtforms.validators import DataRequired, Length, Optional
from wtforms import StringField, SelectMultipleField, SelectField, SubmitField


class AddArchiveReportFunction(FlaskForm):

    archiveReportIdList = []
    archiveeventStatus = [("Ready", "Ready"),("Not Ready", "Not Ready")]

    def add_archive_report_function_lists_update():
        AddArchiveReportFunction.archiveReportIdList.clear()
        with app.app_context():
            archiveReports = ArchiveReport.query.distinct(
                ArchiveReport.id).group_by(ArchiveReport.id)
            for archiveReport in archiveReports:
                AddArchiveReportFunction.archiveReportIdList.append(
                    (archiveReport.id, archiveReport.title))
                

    title = StringField(label='title', validators = [DataRequired(),Length(min=3, max=20, message='title: must be between 3 and 20 characters.')])
    description = StringField(label='description', validators=[Optional()])
    archiveReportIds = SelectMultipleField(coerce=int, label='archiveReportIds', choices=archiveReportIdList, validators=[DataRequired()])
    eventStatus = SelectField(label='eventStatus',choices = archiveeventStatus, validators=[DataRequired()])
    submit = SubmitField(label='Add Report')