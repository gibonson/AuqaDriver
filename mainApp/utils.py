from flask import render_template

from mainApp import flash
from mainApp import logger
from mainApp.routes import sched
from mainApp.device_status_checker import ConnectionStatus

def flash_message(message, category='info'):
    if category == "info":
        logger.debug(message)
    elif category == "success":
        logger.info(message)
    elif category == "warning":
        logger.warning(message)
    elif category == "danger":
        logger.error(message)
    flash(message, category=category)


def validate_and_log_form(form):
    if form.validate_on_submit():
        message = f"The form has been successfully processed."
        flash_message(message, "success")
        return True
    if form.errors:
        message = f"An error occurred while processing the form: {form.errors}"
        flash_message(message, "warning")
    return False


# info = DEBUG - wszystkie detale
# success = INFO - jak poszlo ok 
# warning = WARNING - blad usera
# danger = ERROR - blad systemu
# danger = CRITICAL - armagedon

def render_template_with_addons(template_name, **kwargs):
    sched_state = str(sched.state)
    connectionStatus = ConnectionStatus()
    deviceStatusList =connectionStatus.getDeviceStatusList()
    addons = {
        'state': sched_state,
        'deviceStatusList' : deviceStatusList
    }
    kwargs.update(addons)
    return render_template(template_name, **kwargs)
