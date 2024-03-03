from application import app
from flask import render_template, url_for
import pandas as pd
import json
import plotly
import plotly.express as px
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, inspect, func

engine = create_engine("sqlite:///../Resources/gamesdb.db")
inspector = inspect(engine)
inspector.get_table_names()
Base = automap_base()
Base.prepare(autoload_with=engine)
Base.classes.keys()

@app.route("/")
def home():

    df= pd.DataFrame({"Game": ["Game1", "Game2", "Game3", "Game4"],
                 "Canada": [4,5,6,7],
                 "EU": [6,3,4,9],
                  "Japan": [2,5,4,6]})
    fig = px.bar(df, x="Game", y=["Canada","EU", "Japan"],
             height=400)

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    return render_template("home.html", graphJSON = graphJSON, title="home")

    

@app.route("/overview")
def overview():
    return render_template("overview.html", title="Overview")

@app.route("/trends")
def trends():
    return render_template("trends.html", title="Trends")

@app.route("/ratings")
def ratings():
    return render_template("ratings.html", title = "Ratings")

@app.route("/comparisons")
def comparisons():
    return render_template("comparisons.html", title = "Comparisons")



@app.route("/sales")
def sales():
    Sales = Base.classes.vgsales
    session = Session(engine)
    sel = [Sales.Name,
      func.sum(Sales.NA_Sales),
      func.sum(Sales.EU_Sales),
      func.sum(Sales.JP_Sales),
      func.sum(Sales.Other_Sales),
      func.sum(Sales.Global_Sales)]

    gamesales = session.query(*sel).\
        group_by(Sales.Name).\
        order_by(func.sum(Sales.Global_Sales).desc()).limit(50).all()

    session.close()

    top50salesdf = pd.DataFrame(gamesales, columns=["Name", "North America Sales", "Europe Sales", "Japan Sales", "Other Sales", "Global_Sales"])
    fig = px.bar(top50salesdf, x="Name", y=["North America Sales", "Europe Sales", "Japan Sales", "Other Sales"], height=1000, width=950,
                labels={"value": "Million of Copies", "Name":"Game"})
    fig.update_layout(legend_title="")
    fig.update_layout(legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    ))
    
    

    sales1graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    return render_template("sales.html", sales1graphJSON = sales1graphJSON, title="sales")

    
