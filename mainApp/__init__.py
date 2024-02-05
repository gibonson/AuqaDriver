from flask import Flask, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import insert, exc
from sqlalchemy_utils.functions import database_exists
from flask_apscheduler import APScheduler

import time 
import os

class Config(object):
    baseDir = os.path.abspath(os.path.dirname(__file__))   + "/../userFiles"

    print(baseDir)
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
    print('-=DB exist!=-')
    from sqlalchemy import create_engine, text
    engine = create_engine(app.config["SQLALCHEMY_DATABASE_URI"], echo=True)
    with engine.connect() as conn:
        timestamp = str(round(time.time()))
        addInfo = "App Start"
        deviceName = "Server"
        deviceIP = "127.0.0.1"
        type = "Log"
        value = 0
        conn.execute(text('INSERT INTO archive (timestamp, deviceIP, deviceName, addInfo, value, type) VALUES ("' +
                     timestamp + '" , "' + deviceIP + '" , "' + deviceName + '" ," ' + addInfo + '", "0", "Log")'))
        conn.commit()
else:
    print('-=db does not exist=-')

# Init scheduler
sched = APScheduler()


from mainApp import routes
from mainApp.jobOperations import schedStart

# start process in scheduler
try:
    schedStart(sched)
    sched.start()
except exc.OperationalError:
        print("-=db does not exist=-")
