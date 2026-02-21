from flask import Flask, render_template
from dotenv import load_dotenv
import os
load_dotenv()

app = Flask(__name__)
os.getenv("rRrT3Tvt9paUrglqzJYj39gAHO7mW8DK2vUJvND8")

@app.route('/')
def hello_world():
    return render_template("index.html")

if __name__ == '__main__':
    app.run(debug=True)
    