from flask_wtf import FlaskForm
from wtforms.validators import Length
from wtforms import StringField, TextAreaField, SubmitField

class EmailSend(FlaskForm):

    subject = StringField(label='subject', validators = [Length(min=3, max=40, message='subject: must be between 3 and 40 characters.')])
    message = TextAreaField(label='Your message')
    submit = SubmitField(label='Send message')