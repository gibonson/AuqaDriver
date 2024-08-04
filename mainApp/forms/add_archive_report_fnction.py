from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Length, Optional
from wtforms import StringField, SelectMultipleField, SelectField, SubmitField


class AddArchiveReportFunction(FlaskForm):

    archiveReportIdList = []
    archiveFunctionStatus = [("Ready", "Ready"),("Not Ready", "Not Ready")]

    title = StringField(label='title', validators = [DataRequired(),Length(min=3, max=20, message='title: must be between 3 and 20 characters.')])
    description = StringField(label='description', validators=[Optional()])
    archiveReportIds = SelectMultipleField(coerce=int, label='archiveReportIds', choices=archiveReportIdList)
    functionStatus = SelectField(label='functionStatus',choices = archiveFunctionStatus, validators=[DataRequired()])
    submit = SubmitField(label='Add Report')