from flask_wtf import FlaskForm
from mainApp import app
from wtforms.validators import Length, Optional
from wtforms import SelectField, SubmitField, IntegerField, TextAreaField, StringField, IPAddress

class AddArchiveIgnore(FlaskForm):

    status = [("Ready", "Ready"),("Not Ready", "Not Ready"),("Old", "Old")]


    deviceIP = StringField(label='deviceIP', validators=[Optional(), IPAddress(ipv4=True, ipv6=False, message="deviceIP: wrong IP format")])
    deviceName = StringField(label='deviceName', validators= [Optional(),Length(min=3, max=20, message='deviceName: must be between 3 and 20 characters.')])
    addInfo = StringField(label='addInfo',validators= [Optional()])
    value = IntegerField(label='value',validators= [Optional()])
    type = StringField(label='type',validators= [Optional()])
    status = SelectField(label='status',choices = status, validators=[Optional()])
    submit = SubmitField(label='add')
