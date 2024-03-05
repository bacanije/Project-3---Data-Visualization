# Video Games Data Visualization Project
DataBootCamp Project 3 - Group 2

Aim:
This projects aims to gain a better understanding of the video game industry.  

This project utilized two datasets, located in this Repository's [Resources/startercsv](Resources/startercsv) folder.
The first dataset, [all_video_games(cleaned).csv](Resources/startercsv/all_video_games(cleaned).csv), was obtained from [Kaggle.com](https://www.kaggle.com/datasets/beridzeg45/video-games).  The all_video_games(cleaned).csv was further cleaned in jupyter notebook using file [Video_games_cleaning.ipynb](JupyterNotebooks/Video_games_cleaning.ipynb) and exported to csv as [games.csv](Resources/games.csv).
The second dataset, [vgsales.csv](Resources/startercsv/vgsales.csv), was obtained from [Kaggle.com](https://www.kaggle.com/datasets/gregorut/videogamesales).

The games.csv and vgsales.csv were converted into a [SQLite database](Resources/gamesdb.db) using DB Browser and stored in this Repository's Resources folder.

The gamesdb Database was queried using SQLalchemy in jupyter notebook or VSCode to create visualizations in a Flask app.  The [Flask app](Flask) files are all within this Repository's Flask Folder. The app can be run through the [run.py](Flask/application/run.py) file.

Part 1: Overview of Data (Mike)  

Part 2: Trends (Jessamyn)  

Part 3: Ratings (Kajal)  

Part 4: Comparisons (Allister)  

Part 5: Sales ([Stephanie](JupyterNotebooks/SL_VideoGamesSalesFigures.ipynb)  
- Top 50 Games by Units Sold (across platforms)
- Units Sold by Genre
- Unit Sales by Year by Genre
