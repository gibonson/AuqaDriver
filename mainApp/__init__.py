from mainApp.extensions import db, sched
from flask import Flask, flash
from sqlalchemy import insert, exc
from sqlalchemy_utils.functions import database_exists

import time
import os

from mainApp.logging_config import setup_logging

__version__ = "0.5.1"
__description__ = "AquaDriver - Home IoT Automation Hub"

logger = setup_logging()
logger.critical("\n")
logger.critical(f"App start v{__version__}: {__description__}")


class Config(object):
    baseDir = os.path.abspath(os.path.dirname(__file__)) + "/../userFiles"
    logger.debug("Path to DB: " + baseDir)
    # Config app
    SECRET_KEY = os.environ.get("SECRET_KEY", os.urandom(24))
    # Config scheduler
    SCHEDULER_API_ENABLED = True
    JSONIFY_PRETTYPRINT_REGULAR = True
    # Config DB
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(baseDir, "db.sqlite")
    SQLALCHEMY_TRACK_MODIFICATIONS = False


# Init app
app = Flask(__name__, static_folder="../static")
app.config.from_object(Config())

# Init db
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
            query = text("""
                INSERT INTO archive (timestamp, deviceIP, deviceName, addInfo, value, type) 
                VALUES (:timestamp, :deviceIP, :deviceName, :addInfo, :value, :type)
            """)
            
            conn.execute(query, {
                "timestamp": timestamp,
                "deviceIP": deviceIP,
                "deviceName": deviceName,
                "addInfo": addInfo,
                "value": value,
                "type": type
            })
            conn.commit()    

        except exc.SQLAlchemyError as e:
            logger.error(f"Database error: {e}")
else:
    logger.critical("Database does not exist")

# Init scheduler
sched.init_app(app)

from mainApp.routes_core import core_bp
from mainApp.routes_admin import admin_bp
from mainApp.routes_api import api_bp
from mainApp.routes_dev import dev_bp


from mainApp import routes

app.register_blueprint(core_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(api_bp)
app.register_blueprint(dev_bp)

from mainApp.scheduler_operations import sched_start

# # start process in scheduler
try:
    sched_start()
    sched.start()
    logger.critical("Scheduler started")
except exc.OperationalError:
    logger.critical("Scheduler startup error")
