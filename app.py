from flask import Flask, render_template, jsonify, request
from dotenv import load_dotenv
import os
from datetime import datetime, timezone

import requests
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
        "auth": bool(os.getenv("MOVIEGLU_AUTH")),
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
        "x-api-key": os.getenv("MOVIEGLU_API_KEY","").strip(),
        "client": os.getenv("MOVIEGLU_CLIENT", "").strip(),
        "Authorization": os.getenv("MOVIEGLU_AUTH","").strip(),
        "territory": os.getenv("MOVIEGLU_TERRITORY", "").strip(),
        "api-version": os.getenv("MOVIEGLU_API_VERSION", "").strip(),
        "device-datetime": current_device_time
    }

# temp function -- retrieving film detail's information
@app.route('/filmDetails', methods = ["GET"])
def film_details():
    header_list = list(movieglu_headers().keys())
    return jsonify(header_list), 200 

# allows you to look up a film's entire info
@app.route('/filmLiveSearch/', methods =["GET"])  # type: ignore
def film_live_search():
    query = request.args.get("query", "")
    if query == "":
        return {
            "error": "query required"
        }, 400
    
    get_base = os.getenv("MOVIEGLU_API_BASE") 
    build_url = str(get_base) + "/filmLiveSearch/"
    params = {"query": query}
    headers = movieglu_headers()
    response = requests.get(build_url, headers = headers, params=params)

    if response.status_code != 200:
        return {
            "response" :response.status_code, 
            # "body": response.json(),
            "content type": response.headers.get("Content-Type"),
            "text preview": response.text[:200],
            "url": response.url,
            "raw body len": len(response.content),
            "MG Message": response.headers.get("MG-message"),
            "MG-error": response.headers.get("MG-error"),
            "has auth": bool(headers.get("Authorization"))
        }
    if response.status_code == 200:
        return response.json(), 200
    

    
if __name__ == '__main__':
    app.run(debug=True, port=5001)