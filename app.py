from flask import Flask, render_template, jsonify, request
from dotenv import load_dotenv
import os
load_dotenv()

app = Flask(__name__)
os.getenv("rRrT3Tvt9paUrglqzJYj39gAHO7mW8DK2vUJvND8")

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/ping')
def ping():
    return jsonify(ok = True), 200

@app.route('/echo')
def echo():
    q = request.args.get("q", "")
    return jsonify(q = q), 200

if __name__ == '__main__':
    app.run(debug=True)