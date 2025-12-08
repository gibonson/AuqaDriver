from flask_wtf import FlaskForm
from mainApp import app
from mainApp.models.archive import Archive
from wtforms.validators import DataRequired, Length, Optional
from wtforms import StringField, SelectField, IntegerField, SubmitField


class AddArchiveReport(FlaskForm):

    statusList = [("Ready", "Ready"),("Not Ready", "Not Ready")]


    title = StringField(label='title', validators= [DataRequired(),Length(min=1, max=30, message='title: must be between 1 and 30 characters.')])
    minValue = IntegerField(label='minValue',validators=[Optional()])
    okMinValue = IntegerField(label='okMinValue',validators=[Optional()])
    okMaxValue = IntegerField(label='okMaxValue',validators=[Optional()])
    maxValue = IntegerField(label='maxValue',validators=[Optional()])
    queryString = StringField(label='queryString', validators= [DataRequired(),Length(min=1, max=200, message='queryString: must be between 1 and 200 characters.')])
    unit = StringField(label='unit', validators= [Optional(),Length(min=0, max=20, message='unit: must be between 0 and 20 characters.')])
    message = StringField(label='message', validators= [Optional(),Length(min=0, max=100, message='message: must be between 0 and 100 characters.')])   
    reportGroupId = IntegerField(label='reportGroupId', validators=[Optional()])
    status = SelectField(label='status', choices=statusList, validators=[DataRequired()])
    submit = SubmitField(label='Add Report')