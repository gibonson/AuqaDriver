from flask import Flask, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import insert, exc
from sqlalchemy_utils.functions import database_exists
from flask_apscheduler import APScheduler

import time 
import os

from mainApp.logging_config import setup_logging
logger = setup_logging()
logger.critical("\n")
logger.critical("App start")


class Config(object):
    baseDir = os.path.abspath(os.path.dirname(__file__))   + "/../userFiles"
    logger.debug("Path to DB: " + baseDir)
    # Config app
    SECRET_KEY = '7d441f27d441f27567d441f2b6176a'
    # Config scheduler
    SCHEDULER_API_ENABLED = True
    JSONIFY_PRETTYPRINT_REGULAR = True
    # Config DB
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(baseDir, 'db.sqlite')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

# Init app
app = Flask(__name__, static_folder='../static')
app.config.from_object(Config())

# Init db
db = SQLAlchemy()
db.init_app(app)

if database_exists(app.config["SQLALCHEMY_DATABASE_URI"]):
    logger.info("Database exists")
    from sqlalchemy import create_engine, text
    engine = create_engine(app.config["SQLALCHEMY_DATABASE_URI"], echo=True)
    with engine.connect() as conn:
        timestamp = str(round(time.time()))
        addInfo = "App Start"
        deviceName = "Server"
        deviceIP = "127.0.0.1"
        type = "Log"
        value = 0
        try:
            conn.execute(text('INSERT INTO archive (timestamp, deviceIP, deviceName, addInfo, value, type) VALUES ("' +
                     timestamp + '" , "' + deviceIP + '" , "' + deviceName + '" ," ' + addInfo + '", "0", "Log")'))
            conn.commit()
        except exc.SQLAlchemyError as e:
            logger.error(f"Database error: {e}")
else:
    logger.critical("Database does not exist")

# Init scheduler
sched = APScheduler()

from mainApp import routes
from mainApp.scheduler_operations import sched_start
from mainApp.device_status_checker import DeviceStatusChecker

# start process in scheduler
try:
    sched_start(sched)
    DeviceStatusChecker = DeviceStatusChecker(sched)
    sched.start()
    logger.critical("Scheduler started")
except exc.OperationalError:
    logger.critical("Scheduler startup error")
