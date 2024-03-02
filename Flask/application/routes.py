from application import app
from flask import render_template, url_for
import pandas as pd
import json
import plotly
import plotly.express as px


@app.route("/")
def home():

    df= pd.DataFrame({"Game": ["Game1", "Game2", "Game3", "Game4"],
                 "Canada": [4,5,6,7],
                 "EU": [6,3,4,9],
                  "Japan": [2,5,4,6]})
    fig = px.bar(df, x="Game", y=["Canada","EU", "Japan"],
             height=400)

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    return render_template("index.html", graphJSON = graphJSON, title="home")

    

@app.route("/overview")
def overview():
    return render_template("overview.html", title="Overview")