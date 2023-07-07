import pandas as pd
import sqlite3
from datetime import datetime
import time
import os


from nba_api.stats.static import teams
from nba_api.stats.endpoints import leaguegamefinder
from Preprocessing.Preprocess_Game_Data import add_result_column

def update_game_data():
    # Get the path of the current script file
    script_path = os.path.dirname(os.path.realpath(__file__))

    # Construct the path to the database file
    db_path = os.path.join(script_path, '..', 'Data', 'nba_games.db')
    conn = sqlite3.connect(db_path)

    nba_teams = teams.get_teams()
    # I am choosing the start year as 2010 because this is deemed the 'current era', where the game has become offense heavy, guard dominated league.
    # it also makes the dataset more manageable.
    start_year = 2010
    end_year = datetime.now().year

    print('number of teams fetched: {}'.format(len(nba_teams)))

    all_games = []

    for team in nba_teams:
        print(f"Fetching Game data for {team['full_name']}...")
        gamefinder = leaguegamefinder.LeagueGameFinder(team_id_nullable=team['id'])
        games = gamefinder.get_data_frames()[0]
        #filter the games for start_year to end_year
        games['GAME_DATE'] = pd.to_datetime(games['GAME_DATE'])
        games = games[(games['GAME_DATE'].dt.year >= start_year) & (games['GAME_DATE'].dt.year <= end_year)]

        all_games.append(games)
        time.sleep(2) #avoid overloading the API

    all_games_df = pd.concat(all_games, ignore_index=True)

    all_games_df.to_sql('games', conn, if_exists='replace', index=False)

    #call functions for preprocessing the data
    add_result_column('Data/nba_games.db')

    conn.close()

    print("game-level data has been saved to nba_games.db")
