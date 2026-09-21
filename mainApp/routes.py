# Standard library imports
from datetime import datetime, timedelta
import os
import glob

# Third-party imports
from flask import (
    Markup,
    flash,
    jsonify,
    redirect,
    request,
    url_for,
    abort,
    send_from_directory,
)
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from collections import deque

# Local application/library specific imports
from mainApp import app, db, logger, sched
from mainApp.notification_operations import emailSender, pushoverSender
from mainApp.forms.archive_search import ArchiveSearch
from mainApp.forms.config_json import ConfigForm
from mainApp.forms.add_archive_manual import AddArchiveManualRecord
from mainApp.models.archive import (
    ArchiveAdder,
    ArchiveLister,
    ArchiveManager,
    ArchiveSearchList,
)
from mainApp.config_operations import (
    load_config_text,
    save_config_text,
    backup_config_file,
    get_config_file_path,
    restart_application,
    parse_config_text,
)
from mainApp.models.archive_report import ReportManager
from mainApp.models.event import EventManager
from mainApp.models.event_validation import ValidationManager
from mainApp.models.event_scheduler import EventSchedulerManager
from mainApp.models.dashboard import DashboardManager
from mainApp.report_operations import ReportCreator
from mainApp.scheduler_operations import sched_start
from mainApp.web_operations import WebContentCollector, ResponseTrigger
from mainApp.utils import (
    flash_message,
    validate_and_log_form,
    render_template_with_addons,
    DashboardData,
)

# -----------------------------------------
# start page and 404
# -----------------------------------------


@app.route("/")
def hello_world():
    return redirect(url_for("get_jobs"))


@app.errorhandler(404)
def not_found(e):
    flash_message("404!", category="warning")
    return render_template_with_addons("404.html")


@app.errorhandler(OperationalError)
def handle_operational_error(error):
    flash_message(f"OperationalError: {error}", "danger")
    if "no such table" in str(error):
        flash_message(
            Markup("Try to <a href='/create'>create new DB</a>"), category="danger"
        )
    return render_template_with_addons("500.html")





