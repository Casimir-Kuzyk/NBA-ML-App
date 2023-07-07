import sqlite3
import pandas as pd
import time
from nba_api.stats.endpoints import boxscoretraditionalv2
from json.decoder import JSONDecodeError
import os

def update_player_data():

    # Get the path of the current script file
    script_path = os.path.dirname(os.path.realpath(__file__))

    # Construct the path to the database file
    db_path = os.path.join(script_path, '..', 'Data', 'nba_games.db')

    conn = sqlite3.connect(db_path)

    # Check if player_box_scores table exists
    table_check = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='player_box_scores'").fetchone()

    if not table_check:
        conn.execute('''
            CREATE TABLE player_box_scores (
                PLAYER_ID INTEGER,
                PLAYER_NAME TEXT,
                NICKNAME TEXT,
                TEAM_ID INTEGER,
                TEAM_ABBREVIATION TEXT,
                TEAM_CITY TEXT,
                PLAYER_POSITION TEXT,
                START_POSITION TEXT,
                COMMENT TEXT,
                MIN TEXT,
                FGM INTEGER,
                FGA INTEGER,
                FG_PCT FLOAT,
                FG3M INTEGER,
                FG3A INTEGER,
                FG3_PCT FLOAT,
                FTM INTEGER,
                FTA INTEGER,
                FT_PCT FLOAT,
                OREB INTEGER,
                DREB INTEGER,
                REB INTEGER,
                AST INTEGER,
                STL INTEGER,
                BLK INTEGER,
                TURNOVER INTEGER,
                PF INTEGER,
                PTS INTEGER,
                PLUS_MINUS INTEGER,
                GAME_ID TEXT,
                GAME_DATE TEXT
            )
        ''')

    # Fetch list of game IDs and dates to gather player data from
    game_ids_dates_df = pd.read_sql_query("SELECT GAME_ID, GAME_DATE FROM games ORDER BY GAME_DATE", conn)
    game_ids_dates_df.drop_duplicates(subset='GAME_ID', inplace=True)


    # Start processing from the last processed game_date
    last_processed_date = pd.read_sql_query("SELECT MAX(GAME_DATE) FROM player_box_scores", conn).iloc[0, 0]

    if last_processed_date is not None:
        # Fetch games with the last_processed_date and exclude the ones already present in the player_box_scores table
        processed_game_ids = pd.read_sql_query("SELECT DISTINCT GAME_ID FROM player_box_scores WHERE GAME_DATE = ?", conn, params=(last_processed_date,))
        unprocessed_games_same_date = game_ids_dates_df[(game_ids_dates_df['GAME_DATE'] == last_processed_date) & (~game_ids_dates_df['GAME_ID'].isin(processed_game_ids['GAME_ID']))]

        # Fetch games with dates strictly greater than the last_processed_date
        games_after_last_processed_date = game_ids_dates_df[game_ids_dates_df['GAME_DATE'] > last_processed_date]

        # Concatenate both DataFrames to form the final game_ids_dates_df
        game_ids_dates_df = pd.concat([unprocessed_games_same_date, games_after_last_processed_date], ignore_index=True)


    # Fetch box score data
    for _, row in game_ids_dates_df.iterrows():
        game_id, game_date = row['GAME_ID'], row['GAME_DATE']
        print(f"Fetching player box score data from game_id {game_id} on {game_date}...")

        try:
            box_score = boxscoretraditionalv2.BoxScoreTraditionalV2(game_id=game_id)
            player_box_scores = box_score.get_data_frames()[0]
            player_box_scores['GAME_DATE'] = game_date  # Add GAME_DATE column
            player_box_scores.rename(columns={'TO': 'TURNOVER'}, inplace=True)
            player_box_scores.to_sql('player_box_scores', conn, if_exists='append', index=False)
        except JSONDecodeError as e:
            print(f"Error fetching data for game_id: {game_id}: {e}")

        time.sleep(0.6)

    print("All player level data has been stored")
