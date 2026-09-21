import os
from datetime import datetime
from collections import deque

from flask import (
    Blueprint,
    flash,
    redirect,
    request,
    url_for,
    abort,
)

from mainApp import app
from mainApp.extensions import db, sched
from mainApp.models.archive_report import ReportManager
from mainApp.models.event import EventManager
from mainApp.models.event_validation import ValidationManager
from mainApp.models.event_scheduler import EventSchedulerManager
from mainApp.models.dashboard import DashboardManager
from mainApp.models.archive import ArchiveAdder
from mainApp.forms.config_json import ConfigForm
from mainApp.scheduler_operations import sched_start
from mainApp.utils import (
    flash_message,
    render_template_with_addons,
    validate_and_log_form,
    DashboardData,
    logger,
)
from mainApp.config_operations import (
    load_config_text,
    save_config_text,
    backup_config_file,
    get_config_file_path,
    parse_config_text,
)

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


# -----------------------------------------
# create DB section
# -----------------------------------------


@app.route("/create")
def create():
    with app.app_context():
        db.create_all()
        requestData = {
            "addInfo": "BD creation",
            "deviceIP": "127.0.0.1",
            "deviceName": "Server",
            "type": "Log",
            "value": 0,
        }
        ArchiveAdder(requestData).save()
        flash_message("New database has been created", "info")
    return redirect(url_for("get_jobs"))


# -----------------------------------------
# table section
# -----------------------------------------


@app.route("/get_table/<tableName>")
def get_table(tableName):
    table = []
    if tableName == "event":
        table = EventManager().get_all()
    elif tableName == "event_scheduler":
        table = EventSchedulerManager().get_all()
    elif tableName == "event_validation":
        table = ValidationManager().get_all()
    elif tableName == "archive_report":
        table = ReportManager().get_all()
    elif tableName == "dashboard":
        table = DashboardManager().get_all()
    return render_template_with_addons(
        f"{tableName}-table.html", table=table, datetime=datetime
    )


# -----------------------------------------
# config section
# -----------------------------------------


@app.route("/config_table/<tableName>", methods=["POST", "GET"])
def config_table(tableName):
    form = ConfigForm()
    if request.method == "GET":
        form.config_json.data = load_config_text(f"{tableName}.json")
    if validate_and_log_form(form=form):
        try:
            parse_config_text(form.config_json.data)  # Walidacja JSON-a
            backup_config_file(f"{tableName}.json")
            save_config_text(f"{tableName}.json", form.config_json.data)
            flash_message(
                f"{tableName}Nowa konfiguracja eventów została zapisana. Aplikacja zostanie zrestartowana.",
                "success",
            )
        except ValueError as validation_error:
            flash_message(str(validation_error), "warning")
    return render_template_with_addons(
        f"{tableName}-config.html",
        form=form,
        config_path=get_config_file_path(f"{tableName}.json"),
    )


# -----------------------------------------
# job section
# -----------------------------------------


@app.route("/get_jobs")
def get_jobs():
    logger.debug(sched.get_jobs())
    for job in sched.get_jobs():
        logger.info(
            "JOB ID:"
            + job.id
            + " JOB NAME:"
            + job.name
            + " JOB TRIGGER:"
            + str(job.trigger)
            + " NEXT JOB:"
            + str(job.next_run_time)
        )
    return render_template_with_addons("get_jobs.html", get_jobs=sched.get_jobs())


@app.route("/pause_job/<id>")
def pause_job(id):
    sched.pause_job(id)
    return redirect(url_for("get_jobs"))


@app.route("/resume_job/<id>")
def resume_job(id):
    sched.resume_job(id)
    return redirect(url_for("get_jobs"))


@app.route("/remove_job/<id>")
def remove_job(id):
    sched.remove_job(id)
    return redirect(url_for("get_jobs"))


@app.route("/start_job/<runschedulerId>")
def start_job(runschedulerId):
    if sched.state == 0:
        sched.start()
    sched_start(sched, runschedulerId)
    return redirect(url_for("get_jobs"))


# -----------------------------------------
# Global Scheduler Operation
# -----------------------------------------


@app.route("/pause")
def pause():
    sched.pause()
    return redirect(url_for("get_jobs"))


@app.route("/resume")
def resume():
    sched.resume()
    return redirect(url_for("get_jobs"))


@app.route("/start")
def start():
    sched.start()
    sched_start(sched)
    return redirect(url_for("get_jobs"))


@app.route("/shutdown")
def shutdown():
    # sched.remove_all_jobs() # sched.pause() # sched.delete_all_jobs() # sched.pause()# sched.shutdown(wait=False)
    return redirect(url_for("get_jobs"))


# -----------------------------------------
# get_logs
# -----------------------------------------


@app.route("/get_logs", methods=["GET"])
def get_logs():
    dbSizeKB = DashboardData().get_placeholder_value("getDbSize")
    logSizeKB = DashboardData().get_placeholder_value("getLogSize")
    sqlTable = DashboardData().getSqlTable()
    log_file_path = os.path.join("userFiles", "app.log")
    if not os.path.exists(log_file_path):
        flash("Log file does not exist!", category="danger")
        abort(404)
    try:
        with open(log_file_path, "r", encoding="utf-8") as log_file:
            # deque z maxlen=200 automatycznie "odrzuca" stare linie, trzymając w RAM tylko najnowsze 200
            last_200_lines = list(deque(log_file, maxlen=200))

            last_200_lines = [line.strip() for line in last_200_lines if line.strip()]
            last_200_lines.reverse()
        return render_template_with_addons(
            "get_logs.html",
            log_lines=last_200_lines,
            dbSizeKB=dbSizeKB,
            logSizeKB=logSizeKB,
            sqlTable=sqlTable,
            state=str(sched.state),
        )

    except Exception as e:
        flash(f"Error reading log file: {str(e)}", category="danger")
        abort(404)
