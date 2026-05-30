from flask_wtf import FlaskForm
from mainApp import app
from wtforms.validators import DataRequired, Length, Optional
from wtforms import SelectField, StringField, SubmitField, IntegerField, TextAreaField


class AddEventLink(FlaskForm):
    eventStatusList = [("Ready", "Ready"),("Not Ready", "Not Ready")]

    eventAddress = StringField(label='eventAddress', validators = [DataRequired(),Length(min=3, max=100, message='eventAddress: must be between 3 and 100 characters.')])
    eventDescription = StringField(label='eventDescription', validators = [Optional()])
    eventPayload = StringField(label='eventPayload', validators = [Optional()])
    eventGroupId = IntegerField(label='eventGroupId', validators = [Optional()])
    eventStatus = SelectField(label='eventStatus', choices = eventStatusList, validators=[DataRequired()])
    submit = SubmitField(label='Add Event')