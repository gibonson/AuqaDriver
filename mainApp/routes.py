from flask import (
    redirect,
    url_for,
)
from sqlalchemy.exc import OperationalError

from mainApp import app
from mainApp.utils import (
    flash_message,
    render_template_with_addons,
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
