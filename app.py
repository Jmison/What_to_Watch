from flask import Flask, render_template, jsonify, request
from dotenv import load_dotenv
import os
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
    list_of_req = {
        "api_key": bool(os.getenv("MOVIEGLU_API_KEY")),
        "client": bool(os.getenv("MOVIEGLU_CLIENT")),
        "auth": bool(os.getenv("MOVIEGLU_AUTH")),
        "territory": bool(os.getenv("MOVIEGLU_TERRITORY")),
        "api_base": bool(os.getenv("MOVIEGLU_API_BASE"))
    }
    return jsonify(list_of_req), 200

# first real end-point grabbing from MOVIEGLU
@app.route('/movie-details')
def movie_details():
    return jsonify("placeholder: text"), 200 #placeholders

if __name__ == '__main__':
    app.run(debug=True, port=5001)