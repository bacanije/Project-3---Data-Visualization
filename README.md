# Video Game Data Visualization Project
## DataBootCamp Project 3 - Group 2

### Aim:
The aim of this project is to better understand the video game industry through analysis of developers, publishers, user scores, critic scores, genres, and sales.

This project utilized two datasets, located in this repository's [Resources/startercsv](Resources/startercsv) folder.
The first dataset, [all_video_games(cleaned).csv](Resources/startercsv/all_video_games(cleaned).csv), was obtained from [Kaggle.com](https://www.kaggle.com/datasets/beridzeg45/video-games).  The all_video_games(cleaned).csv was further cleaned in jupyter notebook using file [Video_games_cleaning.ipynb](JupyterNotebooks/Video_games_cleaning.ipynb) and exported to csv as [games.csv](Resources/games.csv).
The second dataset, [vgsales.csv](Resources/startercsv/vgsales.csv), was obtained from [Kaggle.com](https://www.kaggle.com/datasets/gregorut/videogamesales).

The games.csv and vgsales.csv were converted into a SQLite database, ["gamesdb.db"](Resources/gamesdb.db), using DB Browser and stored in this repository's Resources folder.

The gamesdb database was queried using SQLalchemy in jupyter notebook or VSCode to create visualizations with [Plotly](https://plotly.com/graphing-libraries/) and [Altair](https://altair-viz.github.io/index.html) libraries.  All figures are displaying in a Flask application.  The [Flask app](Flask) files are all within this Repository's Flask Folder. The app can be run through the [run.py](Flask/run.py) file.  

Part 1: Overview of Data ([Stephanie](JupyterNotebooks/SL_VideoGameSalesFigures.ipynb))
- Counts by Publisher
- Binning by Publisher
- Binning by User Score

Part 2: Trends ([Jessamyn](JupyterNotebooks/Videogame_analysis_final_jess.ipynb))
- Average rating (user score and) by publisher over time
- Count of Genre over time
- Counts of releases from Jan to Dec by publisher 
- Counts of product rating (ESRB) by year 

Part 3: Ratings ([Kajal](JupyterNotebooks/Videogame_comparisions_Analysis_KM.ipynb))
- Top Rated Games via User & Top Rated Games via Metascore
- Highest average user rating for publisher/developer
- Top 10 games released by user rating
- Game of the Year by user rating

Part 4: Comparisons (Allister)
- Top 10 Genres Published
- Top Titles by User score vs Mean Meta Score
- Top Platforms by User score vs Mean Meta Score

Part 5: Sales ([Stephanie](JupyterNotebooks/SL_VideoGameSalesFigures.ipynb))
- Top 50 Games by Units Sold (across platforms)
- Units Sold by Geographic Region
- Units Sold by Genre
- Unit Sales by Release Year and Genre

The Flask app framework was created with the help of a YouTube tutorial:  
Code with Prince (2021) Web Data Dashboard with Plotly express and Flask Python and Javascript. Available at: https://www.youtube.com/watch?v=B97qWOUvlnU (Accessed: 04 March 2023).


