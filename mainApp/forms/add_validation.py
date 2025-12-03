from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Length, IPAddress, Optional
from wtforms import StringField, SelectField, IntegerField, SubmitField


class AddValidation(FlaskForm):

    conditionValuesList = [("less","less"),("more","more"),("equal","equal")]
    statusValuesList = [("Ready","Ready"),("Not ready","Not ready")]
    actionTypeValuesList = [("email","email"),("event","event"),("ignore","ignore")]

    description = StringField(label='description', validators= [DataRequired(),Length(min=1, max=60, message='description: must be between 1 and 60 characters.')])
    deviceIP = StringField(label='deviceIP', validators=[DataRequired(), IPAddress(ipv4=True, ipv6=False, message="deviceIP: wrong IP format")])
    deviceName = StringField(label='deviceName', validators= [DataRequired(),Length(min=3, max=20, message='deviceName: must be between 3 and 20 characters.')])
    addInfo = StringField(label='addInfo', validators= [DataRequired(),Length(min=3, max=20, message='addInfo: must be between 3 and 20 characters.')])
    type = StringField(label='type', validators= [DataRequired(),Length(min=3, max=20, message='type: must be between 3 and 10 characters.')])
    condition = SelectField(label='condition', choices=conditionValuesList)
    value = IntegerField(label='value',validators= [DataRequired()])
    actionType = SelectField(label='actionType', choices=actionTypeValuesList) # email, function
    eventId = IntegerField(label='eventId',validators=[Optional()])
    message = StringField(label='message',validators=[Optional()])
    status = SelectField(label='status', choices=statusValuesList) # Ready, Not ready
    submit = SubmitField(label='Add Report')