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

# Create database connection, declare a Base and reflect tables
engine = create_engine("sqlite:///../Resources/gamesdb.db")
Base = automap_base()
Base.prepare(autoload_with=engine)
Base.classes.keys()
# Save a reference to the games table as `Games`
Games = Base.classes.games

# Defining Routes

@app.route("/")
def home():
    return render_template("home.html", title="home")

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

    session = Session(engine)
    sel = [Games.Genres,
      func.sum(Games.Publisher)]

    genres_published = session.query(*sel).\
        group_by(Games.Genres).\
        order_by(func.sum(Games.Publisher).desc()).limit(10).all()
    top10_genres_published_df = pd.DataFrame(genres_published, columns=["Genres","Published"])
    figc1 = px.bar(top10_genres_published_df, x="Genres", y= "Published", color="Genres")
            
    figc1.update_layout(title="Top 10 Genres Published")
    comparison1graphJSON = json.dumps(figc1, cls=plotly.utils.PlotlyJSONEncoder)

    session.close()

    return render_template("comparisons.html", title = "Comparisons", comparison1graphJSON=comparison1graphJSON)

@app.route("/sales")
def sales():

    # Assigning vgsales class to a variable, creating a session
    Sales = Base.classes.vgsales
    session = Session(engine)

    # Figure 1
    # Defining values to select
    sel = [Sales.Name,
      func.sum(Sales.NA_Sales),
      func.sum(Sales.EU_Sales),
      func.sum(Sales.JP_Sales),
      func.sum(Sales.Other_Sales),
      func.sum(Sales.Global_Sales)]

    # Grouping by Game, sorting by total global sales totals (some games have multiple entries from different platforms)
    gamesales = session.query(*sel).\
        group_by(Sales.Name).\
        order_by(func.sum(Sales.Global_Sales).desc()).limit(50).all()
    
    # Plotly express stacked bar graph of total sales, with game on x-axis and units sold on y-axis, shown by region
    top50salesdf = pd.DataFrame(gamesales, columns=["Name", "North America", "Europe", "Japan", "Other", "Global_Sales"])
    fig1 = px.bar(top50salesdf, x="Name", y=["North America", "Europe", "Japan", "Other"], height=1000, width=950,
                labels={"value": "Sales (Millions of Units)", "Name":"Game", "variable":"Region"})
    fig1.update_layout(legend_title="")
    fig1.update_layout(legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    ))
    
    # JSON Encoding figure for display  
    sales1graphJSON = json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder)
    
    # Figure 2
    # Defining values to select
    sel = [Sales.Genre,
      func.sum(Sales.NA_Sales),
      func.sum(Sales.EU_Sales),
      func.sum(Sales.JP_Sales),
      func.sum(Sales.Other_Sales),
      func.sum(Sales.Global_Sales)]

    # Query for number of games sold by genre, and region
    genresales = session.query(*sel).\
        group_by(Sales.Genre).\
        order_by(func.sum(Sales.Global_Sales).desc()).all()


    # Plotly Express plot of query
    genresalesdf = pd.DataFrame(genresales, columns=["Genre", "North America", "Europe", "Japan", "Other", "Global_Sales"])
    fig2 = px.bar(genresalesdf, x="Genre", y=["North America", "Europe", "Japan", "Other",], labels={"value": "Sales (Millions of Units)","variable":"Region"})
    fig2.update_layout(legend_title="")
    fig2.update_layout(legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    ))



    session.close()

    # JSON Encoding figure for display  
    sales2graphJSON = json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)
    
    # Returning sales.html template with the two figures
    return render_template("sales.html", sales1graphJSON = sales1graphJSON, sales2graphJSON=sales2graphJSON, title="Sales")

    
