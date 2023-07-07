import pandas as pd
import sqlite3
from datetime import datetime
import time
import os


from nba_api.stats.static import teams
from nba_api.stats.endpoints import leaguegamefinder
from Preprocessing.Preprocess_Game_Data import add_result_column
from sbrscrape import Scoreboard



def update_game_data():
    # Get the path of the current script file
    script_path = os.path.dirname(os.path.realpath(__file__))

    # Construct the path to the database file
    db_path = os.path.join(script_path, 'Data', 'testodds.db')
    print(db_path)
    conn = sqlite3.connect(db_path)

    nba_teams = teams.get_teams()
    # I am choosing the start year as 2010 because this is deemed the 'current era', where the game has become offense heavy, guard dominated league.
    # it also makes the dataset more manageable.
    start_year = 2010
    end_year = datetime.now().year

    #now fetch odds data from sbrodds
    # sport="NBA"
    # date = "2023-05-05"
    # spread_url = f"https://www.sportsbookreview.com/betting-odds/{sport.lower()}-basketball/?date={date}"
    # print(f"Spread URL: {spread_url}")

    
    
    # scoreboard = Scoreboard(sport=sport, date=date, current_line=False)

    # for game in scoreboard.games:
    #     print(game)
    year = [2022, 2023]
    month1 = 3
    day1 = 5
    end_year_pointer = year[0]
    sb = Scoreboard(date=f"{end_year_pointer}-{month1:02}-{day1:02}")

    for game in sb.games:
        print(game)
    conn.close()

    print("game-level data has been saved to nba_games.db")

update_game_data()