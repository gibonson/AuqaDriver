from flask import Blueprint

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


@app.route("/archive_add_manually", methods=["POST", "GET"])
def archive_add_manually():
    form = AddArchiveManualRecord()
    if validate_and_log_form(form):
        requestDataRaw = request.form.to_dict(flat=False)
        requestData = {
            "addInfo": requestDataRaw["addInfo"][0],
            "deviceIP": requestDataRaw["deviceIP"][0],
            "deviceName": requestDataRaw["deviceName"][0],
            "type": requestDataRaw["type"][0],
            "value": requestDataRaw["value"][0],
            "comment": requestDataRaw["comment"][0],
            "requestID": "M" + str(int(datetime.now().timestamp())),
        }
        ResponseTrigger(requestData=requestData)
    return render_template_with_addons("archive_add_manually.html", form=form)
