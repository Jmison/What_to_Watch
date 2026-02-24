from flask import Flask, render_template, jsonify, request
from dotenv import load_dotenv
import os
from datetime import datetime, timezone
load_dotenv()

app = Flask(__name__)

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/ping/')
def ping():
    return jsonify(ok = True), 200

@app.route('/echo')
def echo():
    q = request.args.get("q", "")
    return jsonify(q = q), 200

# checks and sees if the API information is present, returns false if not.
@app.route('/debug/env')
def debug():
    current_device_time = datetime.now(timezone.utc).replace(tzinfo=None).isoformat(timespec="milliseconds")
    list_of_req = {
        "api_key": bool(os.getenv("MOVIEGLU_API_KEY")),
        "client": bool(os.getenv("MOVIEGLU_CLIENT")),
        "auth": bool(os.getenv("MOVIEGLU_AUTH")),``
        "territory": bool(os.getenv("MOVIEGLU_TERRITORY")),
        "api_base": bool(os.getenv("MOVIEGLU_API_BASE")),
        "api_version": bool(os.getenv("MOVIEGLU_API_VERSION")),
        "device-datetime": current_device_time
    }
    return jsonify(list_of_req), 200

# headers information
def movieglu_headers():
    current_device_time = datetime.now(timezone.utc).replace(tzinfo=None).isoformat(timespec="milliseconds")
    return {
        "x-api-key": os.getenv("MOVIEGLU_API_KEY"),
        "client": os.getenv("MOVIEGLU_CLIENT"),
        "authorization": os.getenv("MOVIEGLU_AUTH"),
        "territory": os.getenv("MOVIEGLU_TERRITORY"),
        "api-version": os.getenv("MOVIEGLU_API_VERSION"),
        "device-datetime": current_device_time
    }

# retrieving film detail's information
@app.route('/filmDetails', methods = ["GET"])
def film_details():
    header_list = list(movieglu_headers().keys())
    return jsonify(header_list), 200 

if __name__ == '__main__':
    app.run(debug=True, port=5001)