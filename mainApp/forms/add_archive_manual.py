from flask_wtf import FlaskForm
from mainApp import app
from wtforms.validators import DataRequired, Length, Optional
from wtforms import SelectField, SubmitField, IntegerField, TextAreaField, StringField


class AddArchiveManualRecord(FlaskForm):

    addInfoList= [("Add water[l]","Add water[l]"),("Take Water[l]","Take Water[l]"),("New plant[pcs]","New plant[pcs]"),("New Animal[pcs]","New Animal[pcs]"),("Status","Status")]
    typeList = [("Manual","Manual")]
    deviceList = []


    deviceIP = StringField(label='deviceIP', validators= [DataRequired()])
    deviceName = StringField(label='deviceName', validators= [DataRequired()])  
    addInfo = StringField(label='addInfo',validators= [DataRequired()])
    value = IntegerField(label='value',validators= [DataRequired()])
    type = SelectField(label='type',validators= [DataRequired()], choices=typeList)
    comment = TextAreaField(label='comment', validators= [Optional(),Length(min=3, max=20, message='comment: must be between 1 and 100 characters.')])
    submit = SubmitField(label='Add Report')
