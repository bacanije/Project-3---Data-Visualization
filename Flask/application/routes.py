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
    # Assigning vgsales class to a variable, creating a session
    Games = Base.classes.games
    session = Session(engine)

    # Figure 1
    # Defining values to select
    sel = [Games.Publisher,
      func.count(Games.Publisher)]

    publishernum = session.query(*sel).\
        group_by(Games.Publisher).\
        order_by(func.count(Games.Publisher).desc()).all()

    pubnumdf = pd.DataFrame(publishernum, columns=["Publisher", "Number of Games"])
    top10pub = pubnumdf.iloc[:20] 
    
    # Plotly express stacked bar graph of total sales, with game on x-axis and units sold on y-axis, shown by region
    fig1 = px.bar(top10pub, x="Publisher", y="Number of Games", height=900, color="Publisher",
            labels={"value": "Number of Games", "variable":"Region"})
    fig1.update_layout(legend_title="")
    # JSON Encoding figure for display  
    ov1graphJSON = json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder)

    # Chart 2
    bins = [0,11,21,31,41,51,76,101,126,151,201,251,300, 1000]
    names = ["0-10", "11-20", "21-30", "31-40","41-50", "51-75", "76-100", "101-125", "126-150", "151-200", "201-250", '251-300', "300+"]
    pubnumdf["Number of Games Binned"]=pd.cut(pubnumdf["Number of Games"], bins,labels=names, include_lowest=True)
    pubnumdfgrouped = pubnumdf.groupby(['Number of Games Binned'])
    binnedpub = pubnumdfgrouped.count()
    binnedpub1 = binnedpub.reset_index()
    fig2 = px.bar(binnedpub1, x="Number of Games Binned", y=["Number of Games"], height=900, color="Publisher")
    fig2.update_layout(legend_title="")
    fig2.update_layout(yaxis_range=[0,100])
    # JSON Encoding figure for display  
    ov2graphJSON = json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)

    # Chart 3
    sel = [Games.Title, Games.User_Score]
    userscores = session.query(*sel).all()
    scores = pd.DataFrame(userscores, columns=["Title", "User Score"])
    scores = scores.dropna(subset=["User Score"])
    bins = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 11]
    names = ["0-0.9", "1-1.9", "2-2.9", "3-3.9","4-4.9", "5-5.9", "6-6.9", "7-7.9", "8-8.9", "9-10"]
    scores["Number of Games Binned"]=pd.cut(scores["User Score"], bins,labels=names, include_lowest=True)
    scoresgrouped = scores.groupby(['Number of Games Binned'])
    binnedscore = scoresgrouped.count()
    binnedscore1 = binnedscore.reset_index()
    fig3 = px.bar(binnedscore1, x="Number of Games Binned", y=["Title"], height=1000, color="User Score")
    fig3.update_layout(legend_title="")
    # JSON Encoding figure for display  
    ov3graphJSON = json.dumps(fig3, cls=plotly.utils.PlotlyJSONEncoder)










    return render_template("overview.html", ov1graphJSON=ov1graphJSON,ov2graphJSON=ov2graphJSON,ov3graphJSON=ov3graphJSON, title="Overview")

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
    session = Session(engine)
    # Chart 1
    results = session.query(Games.Publisher, func.avg(Games.User_Score))\
                     .group_by(Games.Publisher)\
                     .order_by(func.avg(Games.User_Score).desc())\
                     .limit(100)\
                     .all()
    resultsdf = pd.DataFrame(results, columns=["Publisher", 'Average User Rating'])

    fig = px.bar(resultsdf, x="Publisher", y="Average User Rating",color = "Publisher" )
    fig.update_yaxes( range=[0,10])
    ratings4graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    #Chart 2
    results = session.query(Games.Developer, func.avg(Games.User_Score))\
                     .group_by(Games.Developer)\
                     .order_by(func.avg(Games.User_Score).desc())\
                     .limit(100)\
                     .all()
    resultsdf = pd.DataFrame(results, columns=["Developer", 'Average User Rating'])
    fig = px.bar(resultsdf, x="Developer", y="Average User Rating",color = "Developer" )
    fig.update_yaxes( range=[0,10])
    ratings5graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    session.close()
    return render_template("ratings.html", ratings4graphJSON=ratings4graphJSON,ratings5graphJSON=ratings5graphJSON, title = "Ratings")

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
    
    # Figure 1b
    # Defining values to select
    sel = [func.sum(Sales.NA_Sales),
      func.sum(Sales.EU_Sales),
      func.sum(Sales.JP_Sales),
      func.sum(Sales.Other_Sales)]
    
    # Query the class and create dataframe
    totalgamesales = session.query(*sel).all()
    totalgamesalesdf = pd.DataFrame(totalgamesales, columns=["North America", "Europe", "Japan", "Other"])
    totalgamesalesdf['Sales'] = [""]

    # Plotly express stacked normalized bar chart of totalsales by region
    fig1b = px.histogram(totalgamesalesdf, x=["North America", "Europe", "Japan", "Other"], y='Sales',
                        barnorm='percent', text_auto='.1f', orientation='h', title="",
                       labels={"variable":"Region", "value": "Sales (Millions of Units)"}, height=300, width=950, hover_data={'Sales':False})
    fig1b.update_xaxes(title_text='Sum of Sales Normalized', showticklabels=True, range=[0, 100], showgrid=False)
    fig1b.update_layout(plot_bgcolor="white", title_y=0, hovermode='x')
    fig1b.update_layout(legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    ))
    
    # JSON Encoding figure for display  
    sales1bgraphJSON = json.dumps(fig1b, cls=plotly.utils.PlotlyJSONEncoder)



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
    return render_template("sales.html", sales1graphJSON = sales1graphJSON, sales1bgraphJSON=sales1bgraphJSON, sales2graphJSON=sales2graphJSON, title="Sales")

    
