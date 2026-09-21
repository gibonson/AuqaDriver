from datetime import datetime, timedelta

from flask import (
    Blueprint,
    request,
    flash,
    redirect,
    url_for,
)

from mainApp import app
from mainApp.utils import render_template_with_addons
from mainApp.forms.archive_search import ArchiveSearch
from mainApp.models.archive import (
    ArchiveLister,
    ArchiveManager,
    ArchiveSearchList,
)

core_bp = Blueprint("core", __name__, url_prefix="/core")


# -----------------------------------------
# archive section
# -----------------------------------------


@app.route("/archive_search", methods=["POST", "GET"])
def archive_search():
    ArchiveSearch.archive_search_lists_update()
    form = ArchiveSearch()
    archive = ArchiveLister().get_list()
    searchEndDate = datetime.now()
    searchStartDate = datetime.now() - timedelta(days=1)
    formatSearchEndDate = searchEndDate.strftime("%Y-%m-%d %H:%M")
    formatSearchStartDate = searchStartDate.strftime("%Y-%m-%d %H:%M")
    if form.validate_on_submit():
        formatSearchStartDate = form.timestampStart.data
        formatSearchEndDate = form.timestampEnd.data
        archiveSearch = ArchiveSearchList(request.form.to_dict(flat=False))
        archive = archiveSearch.get_list()
    return render_template_with_addons(
        "archive_search.html",
        archive=archive,
        datetime=datetime,
        form=form,
        formatedMinusOneDayDate=formatSearchStartDate,
        formatedCurrentDate=formatSearchEndDate,
    )


@app.route("/archive_remove/<id>")
def archive_remove(id):
    manager = ArchiveManager(id)
    manager.remove_archive()
    flash(str(manager), category="danger")
    return redirect(url_for("archive_search"))
