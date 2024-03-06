from application import app
from flask import render_template, url_for
import pandas as pd
import json
import plotly
import plotly.express as px
import plotly.io as pio
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, text, inspect, func, and_, extract, desc
import plotly.graph_objects as go

# Create database connection, declare a Base and reflect tables
engine = create_engine("sqlite:///../Resources/gamesdb.db")
Base = automap_base()
Base.prepare(autoload_with=engine)
Base.classes.keys()
# Save a reference to the games table as `Games`
Games = Base.classes.games

# Plotly JSON encoder
class PlotlyJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, go.Figure):
            return pio.to_json(obj)
        return json.JSONEncoder.default(self, obj)

# Defining Routes

@app.route("/")
def home():
    return render_template("home.html", title="home")

@app.route("/overview")
def overview():
    return render_template("overview.html", title="Overview")

@app.route("/trends")
def trends():

    session = Session(engine)
    sel = [Games.Genres,
     func.count(Games.Release_Date),
    func.count(Games.Publisher.distinct()),
    func.count(Games.Product_Rating)]
    
    genre_counts_query = session.query(Games.Genres, func.count(Games.Genres)).\
        filter(Games.Release_Date >= '1995-01-01', Games.Release_Date <= '2024-12-31').\
        group_by(Games.Genres).order_by(func.count(Games.Genres).desc())
    genre_counts = genre_counts_query.all()
    
    genre_counts_query_df = pd.DataFrame(genre_counts_query, columns=["Genre", "Counts"])
    genre_counts_json = genre_counts_query_df.to_json(orient='records')

    bar_trace = go.Bar(
    x=genre_counts_query_df['Counts'],  
    y=genre_counts_query_df['Genre'],   
    orientation='h',                   
    hoverinfo='x+y',                   
    marker=dict(color='skyblue'))

# Define layout
    layout = go.Layout(
    title='Genre Counts from 1995 to 2024',
    xaxis=dict(title='Counts'),
    yaxis=dict(title='Genre'),
    bargap=0.1)

    trendfig1 = go.Figure(data=[bar_trace], layout=layout)

# JSON Encoding figure for display  
    trendsgraph1JSON = trendfig1.to_json()
    
    monthly_publisher_count = session.query(func.extract('month', Games.Release_Date).label('Month'),
    func.count(Games.Publisher.distinct()).label('Publisher_Count')).filter(
    Games.Release_Date.between('1995-01-01', '2024-12-31')).group_by(
        func.extract('month', Games.Release_Date)).order_by('Month').all()
    
    monthly_publisher_count_df = pd.DataFrame(monthly_publisher_count, columns=["Month", "Number of Publishers"])
    monthly_publisher_count_json = monthly_publisher_count_df.to_json(orient='records')

    line_trace = go.Scatter(x=monthly_publisher_count_df['Month'], y=monthly_publisher_count_df['Number of Publishers'], mode='lines+markers')
    trendfig2 = go.Figure(data=[line_trace], layout=go.Layout(title='Monthly Number of Publishers (1995-2024)', xaxis=dict(title='Month'), yaxis=dict(title='Number of Publishers')))
    
     # JSON Encoding figure for display  
    trendsgraph2JSON = json.dumps(trendfig2, cls=plotly.utils.PlotlyJSONEncoder)

    query = session.query(extract('year', Games.Release_Date).label('Year'),
    Games.Product_Rating,
        func.count().label('Rating_Count')).filter(
        Games.Release_Date.between('1995-01-01', '2024-12-31')).group_by(extract('year', Games.Release_Date),
        Games.Product_Rating).order_by('Year')
    results = query.all()
    product_rating_counts_df = pd.DataFrame(results, columns=['Year', 'Product_Rating', 'Rating_Count'])
    # Convert DataFrame to JSON
    product_rating_counts_json = product_rating_counts_df.to_json(orient='records')

    trendfig3 = px.line(product_rating_counts_df, x='Year', y='Rating_Count', color='Product_Rating',title='Product Rating Counts by Year', labels={'Year': 'Year', 'Rating_Count': 'Rating Count'})
 
 # JSON Encoding figure for display  
    trendsgraph3JSON = json.dumps(trendfig3, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('trends.html', trendsgraph1JSON=trendsgraph1JSON, trendsgraph2JSON=trendsgraph2JSON, trendsgraph3JSON=trendsgraph3JSON)


@app.route("/ratings")
def ratings():
    return render_template("ratings.html", title = "Ratings")

@app.route("/comparisons")
def comparisons():

    
    # Assigning games class to a variable, creating a session
    Games = Base.classes.games
    session = Session(engine)


    # Figure 1
    # Defining values to select
    sel = [Games.Genres,
      func.sum(Games.Publisher)]

    # group by Genres and order of overall genres published
    genres_published = session.query(*sel).\
        group_by(Games.Genres).\
        order_by(func.sum(Games.Publisher).desc()).limit(10).all()
    
    # Setting DataFrame limit to 10 rows
    top_genres_published_df = pd.DataFrame(genres_published, columns=["Genres","Published"])
    top_genres_published_df.head(10)
    
    # Plotly express stacked bar graph of top 10 Genres Published
    top10_genres_published_df = top_genres_published_df.head(10)
    figc1 = px.bar(top10_genres_published_df, x="Genres", y= "Published", color="Genres")
    figc1.update_layout(title="Top 10 Genres Published")
    
    # JSON Encoding figure for display 
    comparison1graphJSON = json.dumps(figc1, cls=plotly.utils.PlotlyJSONEncoder)


# Figure 2
    # Defining values to select
    sel = [Games.Title,
      func.sum(Games.User_Score)]

    # Group by Title and order by user score
    score_title_by_userscore = session.query(*sel).\
        group_by(Games.Title).\
        order_by(func.sum(Games.User_Score).desc()).limit(20).all()
    
    # Setting DataFrame limit to 10 rows
    score_title_by_userscore_df = pd.DataFrame(score_title_by_userscore, columns=["Titles", "User_Score"])
    score_title_by_userscore_df.head(10)
    
    # Plotly express stacked bar graph of top 10 title by user score
    top10_title_by_userscore_df = score_title_by_userscore_df.head(10)
    figc2 = px.bar(score_title_by_userscore_df.head(10), x="Titles", y= "User_Score", color="User_Score") 
    figc2.update_layout(title="Top 10 Game Titles by User Score")
    
    # JSON Encoding figure for display 
    comparison2graphJSON = json.dumps(figc2, cls=plotly.utils.PlotlyJSONEncoder)


# Figure 3
    # Defining values to select
    sel = [Games.Title,
      func.sum(Games.Mean_Metascore_Across_Platforms)]

    # Group by Title and order by Mean Meta score
    score_title_by_Mean_Metascore = session.query(*sel).\
        group_by(Games.Title).\
        order_by(func.sum(Games.Mean_Metascore_Across_Platforms).desc()).limit(20).all()
    
    # Setting DataFrame limit to 10 rows
    score_title_by_Mean_Metascore_df = pd.DataFrame(score_title_by_Mean_Metascore, columns=["Titles", "Mean_Metascore_Across_Platforms"])
    score_title_by_Mean_Metascore_df.head(10)
    
    # Plotly express stacked bar graph of top 10 title by mean meta score
    top10_title_by_Mean_Metascore_df = score_title_by_Mean_Metascore_df.head(10)
    figc3 = px.bar(top10_title_by_Mean_Metascore_df, x="Titles", y= "Mean_Metascore_Across_Platforms", color="Titles") 
    figc3.update_layout(title="Top 10 Game Title by Mean Meta Score")
    
    # JSON Encoding figure for display 
    comparison3graphJSON = json.dumps(figc3, cls=plotly.utils.PlotlyJSONEncoder)


# Figure 4
    # Defining values to select
    sel = [Games.Title,
        func.sum(Games.User_Score),
        func.sum(Games.Mean_Metascore_Across_Platforms)]

    # Group by Title and order by User & Mean Meta score
    score_by_title = session.query(*sel).\
        group_by(Games.Title).\
        order_by(func.sum(Games.Mean_Metascore_Across_Platforms).desc()).limit(10).all()
    
    # Setting DataFrame limit to 10 rows
    score_by_title_df = pd.DataFrame(score_by_title, columns=["Title", "User_Score", "Mean_Metascore_Across_Platforms"])
    score_by_title_df.head(10)
    
    # Plotly express stacked bar graph of Title comparions by User & Mean Metascore
    score_by_title_df = score_by_title_df.head(10)
    figc4 = px.line(score_by_title_df, x="Title", y= ["User_Score", "Mean_Metascore_Across_Platforms"])
    
    # JSON Encoding figure for display 
    comparison4graphJSON = json.dumps(figc4, cls=plotly.utils.PlotlyJSONEncoder)


# Figure 5
    # Defining values to select
    sel = [Games.Platform,
       func.sum(Games.User_Score)]

    # Group by Platform and order by user score
    score_by_User = session.query(*sel).\
        group_by(Games.Platform).\
        order_by(func.sum(Games.User_Score).desc()).limit(10).all()
    
    # Setting DataFrame limit to 10 rows
    score_by_User_df= pd.DataFrame(score_by_User, columns=["Platform", "User_Score"])
    score_by_User_df.head(10)
    
    # Plotly express stacked bar graph of top 10 Platform User scores
    top10_score_by_User_df = score_by_User_df.head(10)
    figc5 = px.bar(top10_score_by_User_df, x="Platform", y= "User_Score", color="Platform") 
    figc5.update_layout(title="Top 10 Game Platforms by User Score")
    
    # JSON Encoding figure for display 
    comparison5graphJSON = json.dumps(figc5, cls=plotly.utils.PlotlyJSONEncoder)


# Figure 6
    # Defining values to select
    sel = [Games.Platform,
        func.sum(Games.Mean_Metascore_Across_Platforms)]

    # Group by Platform and order by mean meta score
    score_by_Meta = session.query(*sel).\
        group_by(Games.Platform).\
        order_by(func.sum(Games.Mean_Metascore_Across_Platforms).desc()).limit(10).all()
    
    # Setting DataFrame limit to 10 rows
    score_by_MetaScore_df = pd.DataFrame(score_by_Meta, columns=["Platform", "Mean_Metascore_Across_Platforms"])
    score_by_MetaScore_df.head(10)
    
    # Plotly express stacked bar graph of top 10 Platform Mean Meta scores
    top10_score_by_MetaScore_df = score_by_MetaScore_df.head(10)
    figc6 = px.bar(top10_score_by_MetaScore_df, x="Platform", y= "Mean_Metascore_Across_Platforms", color="Mean_Metascore_Across_Platforms") 
    figc6.update_layout(title="Top 10 Game Platforms by Meta Score")
    
    # JSON Encoding figure for display 
    comparison6graphJSON = json.dumps(figc6, cls=plotly.utils.PlotlyJSONEncoder)


# Figure 7
    # Defining values to select
    sel = [Games.Platform,
        func.sum(Games.User_Score),
        func.sum(Games.Mean_Metascore_Across_Platforms)]

    # Group by Platform and order by User & Mean Meta score
    score_by_platform = session.query(*sel).\
        group_by(Games.Platform).\
        order_by(func.sum(Games.Mean_Metascore_Across_Platforms).desc()).limit(10).all()
    
    # Setting DataFrame limit to 10 rows
    score_by_platform_df = pd.DataFrame(score_by_platform, columns=["Platform", "User_Score", "Mean_Metascore_Across_Platforms"])
    score_by_platform_df.head(10)
    
    # Plotly express stacked bar graph of Platform comparions by User & Mean Metascore
    top10_platform_df = score_by_platform_df.head(10)
    figc7 = px.line(top10_platform_df, x="Platform", y= ["User_Score", "Mean_Metascore_Across_Platforms"])
    
    # JSON Encoding figure for display 
    comparison7graphJSON = json.dumps(figc7, cls=plotly.utils.PlotlyJSONEncoder)

    session.close()

    return render_template("comparisons.html", title = "Comparisons", comparison1graphJSON=comparison1graphJSON, comparison2graphJSON=comparison2graphJSON, 
                                                                        comparison3graphJSON=comparison3graphJSON, comparison4graphJSON=comparison4graphJSON, 
                                                                        comparison5graphJSON=comparison5graphJSON, comparison6graphJSON=comparison6graphJSON, comparison7graphJSON=comparison7graphJSON)







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

    
