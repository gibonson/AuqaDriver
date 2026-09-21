from flask import Blueprint

dev_bp = Blueprint("dev", __name__, url_prefix="/dev")


# -----------------------------------------
# test section
# -----------------------------------------


@app.route("/event_open/<eventName>")
def event_open(eventName):
    WebContentCollector(eventName, requestID="Manual").collector()
    flash("Check out some recent records", category="success")
    return redirect(url_for("archive_search"))


@app.route("/get_report/<reportName>")
def get_report(reportName):
    one_line = ReportCreator().create_one_line(reportName)
    return one_line


@app.route("/get_report_all")
def get_report_all():
    report = ReportCreator().create_all()
    return report


@app.route("/email_send", methods=["POST", "GET"])
def email_send():
    emailSender(subject="test", message="wiadomosc testowa")
    pushoverSender("Testowa wiadomość z AuqaDriver")
    return "check email and phone"


# -----------------------------------------
# experimental dashboard
# -----------------------------------------


@app.route("/media/<path:filename>")
def serve_media(filename):
    media_folder = os.path.abspath("userFiles/media")
    return send_from_directory(media_folder, filename)


@app.route("/dashboard", methods=["GET"])
def dashboard():
    dashboardList = DashboardManager().get_ready()

    dashboardList.sort(key=lambda x: x.panelLocation)

    for dashboard in dashboardList:
        if dashboard.panelCode is None:
            dashboard.panelCode = ""
        if dashboard.panelType == "Report":
            dashboard.panelCode = (
                str(dashboard.panelCode)
                + "</br>"
                + ReportCreator().create_one_line(dashboard.panelCode)
            )
        elif dashboard.panelType == "Event":
            dashboard.panelCode = (
                '<a href="'
                + "/event_open/"
                + str(dashboard.panelCode)
                + '" class="btn btn-success btn-lg active"role="button" aria-pressed="true">Open event: '
                + dashboard.panelCode
                + "</a>"
            )
        elif dashboard.panelType == "Photo":
            DIR_PATH = "userFiles/media"
            search_pattern = os.path.join(DIR_PATH, "cam1*")
            matching_files = glob.glob(search_pattern)

            if not matching_files:
                dashboard.panelCode = "<p>Brak zdjęć do wyświetlenia</p>"

            else:
                newest_file_path = max(matching_files, key=os.path.getmtime)
                file_name = os.path.basename(newest_file_path)
                dashboard.panelCode = (
                    f'<img src="/media/{file_name}" alt="pic" style="max-width:100%;">'
                )

        elif dashboard.panelType == "Stream":
            dashboard.panelCode = (
                f'<a href="/video_feed/{dashboard.panelCode}" class="btn btn-success btn-sm">'
                f'<img src="/video_feed/{dashboard.panelCode}" width="320"></a>'
            )

        elif dashboard.panelType == "HTML":
            dashboard.panelCode = dashboard.panelCode
        else:
            dashboard.panelCode = "UNKNOWN TYPE"

    return render_template_with_addons(
        "main.html", dashboardList=dashboardList, state=str(sched.state)
    )


# -----------------------------------------
# experimental stream/capture
# -----------------------------------------

import requests
from flask import Response, render_template
import re


@app.route("/video_feed/<ESP32_STREAM_URL>")
def video_feed(ESP32_STREAM_URL):
    return Response(
        mjpeg_proxy(ESP32_STREAM_URL),
        mimetype="multipart/x-mixed-replace; boundary="
        + "123456789000000000000987654321",
    )


def mjpeg_proxy(ESP32_STREAM_URL):
    if not ESP32_STREAM_URL.startswith("192.168."):
        print("Odrzucono próbę połączenia z nieznanym adresem IP.")
        yield b""
        return

    stream_url = "http://" + ESP32_STREAM_URL + "/stream"

    try:
        r = requests.get(stream_url, stream=True, timeout=5)

        content_type = r.headers.get("Content-Type", "")
        match = re.search("boundary=(.*)", content_type)
        if not match:
            boundary_str = "123456789000000000000987654321"
        else:
            boundary_str = match.group(1)

        boundary = b"--" + boundary_str.encode()
        buffer = b""

        for chunk in r.iter_content(chunk_size=4096):
            buffer += chunk

            while boundary in buffer:
                part, buffer = buffer.split(boundary, 1)
                if b"Content-Type: image/jpeg" in part:
                    yield boundary + part

    except requests.exceptions.RequestException as e:
        print(f"Błąd połączenia ze strumieniem wideo ({ESP32_STREAM_URL}): {e}")
        yield b""


@app.route("/video/<ESP32_STREAM_URL>")
def video(ESP32_STREAM_URL):
    return render_template_with_addons(
        "stream.html", ESP32_STREAM_URL=ESP32_STREAM_URL, state=str(sched.state)
    )


@app.route("/capture")
def capture():
    url = "http://192.168.0.235/capture"
    SAVE_DIR = "userFiles/media"

    os.makedirs(SAVE_DIR, exist_ok=True)
    response = requests.get(url, timeout=5)
    if response.status_code == 200:
        filename = datetime.now().strftime("%Y%m%d_%H%M%S.jpg")
        filepath = os.path.join(SAVE_DIR, filename)

        with open(filepath, "wb") as f:
            f.write(response.content)

        print(f"Picture saver: {filepath}")
    else:
        print("Error:", response.status_code)

    return "done"
