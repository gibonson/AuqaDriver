from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length


class EventConfigForm(FlaskForm):
    config_json = TextAreaField(
        label='Konfiguracja eventów (JSON)',
        validators=[
            DataRequired(message='Wprowadź konfigurację JSON.'),
            Length(min=2, message='Konfiguracja JSON jest za krótka.')
        ]
    )
    submit = SubmitField(label='Zapisz konfigurację')


class SchedulerConfigForm(FlaskForm):
    config_json = TextAreaField(
        label='Konfiguracja schedulerów (JSON)',
        validators=[
            DataRequired(message='Wprowadź konfigurację JSON.'),
            Length(min=2, message='Konfiguracja JSON jest za krótka.')
        ]
    )
    submit = SubmitField(label='Zapisz konfigurację')


class ReportConfigForm(FlaskForm):
    config_json = TextAreaField(
        label='Konfiguracja raportów (JSON)',
        validators=[
            DataRequired(message='Wprowadź konfigurację JSON.'),
            Length(min=2, message='Konfiguracja JSON jest za krótka.')
        ]
    )
    submit = SubmitField(label='Zapisz konfigurację')
