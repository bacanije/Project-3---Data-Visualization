from application import app
from flask import render_template, url_for
import pandas as pd
import json
import plotly
import plotly.express as px


@app.route("/")
def home():
    return render_template("index.html", title = "Home")

@app.route("/overview")
def overview():
    return render_template("overview.html", title="Overview")