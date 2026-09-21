from flask import request, Blueprint

from mainApp import app
from mainApp.web_operations import ResponseTrigger

api_bp = Blueprint("api", __name__, url_prefix="/api")


# -----------------------------------------
# json
# -----------------------------------------


@app.post("/api/addEvent")
def add_event():
    ResponseTrigger(requestData=request.get_json()).execute()
    return "OK"
