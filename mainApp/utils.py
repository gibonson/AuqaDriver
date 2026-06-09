from flask import render_template

from mainApp import flash
from mainApp import logger
from mainApp.routes import sched
import socket

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
    addons = {
        'state': sched_state,
        'hostname': socket.gethostname()
    }
    kwargs.update(addons)
    return render_template(template_name, **kwargs)


import os
from datetime import datetime
from sqlalchemy import create_engine, text
from mainApp.routes import app


class DashboardData:
    def __init__(self):
        engine = create_engine(app.config["SQLALCHEMY_DATABASE_URI"], echo=True)
        with engine.connect() as conn:
            sqlSelect = conn.execute(text(
                'select deviceIP, deviceName, type, addInfo, count(value) as number_of_queries, round(avg(value),2) as average FROM archive GROUP BY deviceIP, type, addInfo'))
            self.sqlTable = []
            for row in sqlSelect:
                self.sqlTable.append(row)

    def getSqlTable(self):
        return self.sqlTable

    def get_placeholder_value(self, placeholder):
        if placeholder == "date":
            return datetime.now().strftime("%Y-%m-%d")
        
        elif placeholder == "time":
            return datetime.now().strftime("%H:%M:%S")
        
        elif placeholder == "getLogSize":
            LogFile = os.path.abspath(os.path.dirname(__file__)) + "/../userFiles/app.log"
            self.logsSizeKB = os.path.getsize(LogFile) / 1024
            return self.logsSizeKB
            
        elif placeholder == "getDbSize":
            DBFile = os.path.abspath(os.path.dirname(__file__)) + "/../userFiles/db.sqlite"
            print(DBFile)
            self.dbSizeKB = os.path.getsize(DBFile) / 1024
            return self.dbSizeKB
            
        else:
            return "UnknownValue"