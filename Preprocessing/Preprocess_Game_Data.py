import pandas as pd
import sqlite3

def add_result_column(db_path):
    conn = sqlite3.connect(db_path)

    # Read 'games' table into a DataFrame
    games_df = pd.read_sql_query("SELECT * FROM games", conn)

    #TODO: delete games where the minutes was <0 (need to save these game IDs and delete them from the player stats as well)
    #TODO: remove summer league games
    #TODO: differentiate between playoff games and regular season

    #clean up some data
    games_df = games_df.dropna(subset=['WL'])


    # Split the DataFrame into home and away games
    home_games_df = games_df[games_df['MATCHUP'].str.contains('vs.')].sort_values(['TEAM_ID', 'SEASON_ID', 'GAME_DATE'])
    away_games_df = games_df[games_df['MATCHUP'].str.contains('@')].sort_values(['TEAM_ID', 'SEASON_ID', 'GAME_DATE'])

    #restructure data so that each GAME_ID is in a single row. The home team should be labelled _1 and the away team _2

    home_games_df = home_games_df.rename(columns={
        'TEAM_ID' : 'TEAM_ID_1',
        'TEAM_ABBREVIATION' : 'TEAM_ABBREVIATION_1',
        'TEAM_NAME': 'TEAM_NAME_1',
        'WL' : 'WL_1',
        'MIN' : 'MIN_1',
        'PTS' : 'PTS_1',
        'FGM' : 'FGM_1',
        'FGA' : 'FGA_1',
        'FG_PCT' : 'FG_PCT_1',
        'FG3M' : 'FG3M_1',
        'FG3A' : 'FG3A_1',
        'FG3_PCT' : 'FG3_PCT_1',
        'FTM' : 'FTM_1',
        'FTA' : 'FTA_1',
        'FT_PCT' : 'FT_PCT_1',
        'OREB' : 'OREB_1',
        'DREB' : 'DREB_1',
        'REB' : 'REB_1',
        'AST' : 'AST_1',
        'STL' : 'STL_1',
        'BLK' : 'BLK_1',
        'TOV' : 'TOV_1',
        'PF' : 'PF_1',
    })

    away_games_df = away_games_df.rename(columns={
        'TEAM_ID' : 'TEAM_ID_2',
        'TEAM_ABBREVIATION' : 'TEAM_ABBREVIATION_2',
        'TEAM_NAME': 'TEAM_NAME_2',
        'WL' : 'WL_2',
        'MIN' : 'MIN_2',
        'PTS' : 'PTS_2',
        'FGM' : 'FGM_2',
        'FGA' : 'FGA_2',
        'FG_PCT' : 'FG_PCT_2',
        'FG3M' : 'FG3M_2',
        'FG3A' : 'FG3A_2',
        'FG3_PCT' : 'FG3_PCT_2',
        'FTM' : 'FTM_2',
        'FTA' : 'FTA_2',
        'FT_PCT' : 'FT_PCT_2',
        'OREB' : 'OREB_2',
        'DREB' : 'DREB_2',
        'REB' : 'REB_2',
        'AST' : 'AST_2',
        'STL' : 'STL_2',
        'BLK' : 'BLK_2',
        'TOV' : 'TOV_2',
        'PF' : 'PF_2',
    })

    # Calculate the rolling average of points scored
    home_games_df['AVG_PTS_1'] = home_games_df.groupby(['TEAM_ID_1', 'SEASON_ID'])['PTS_1'].expanding().mean().reset_index(level=[0,1], drop=True)
    away_games_df['AVG_PTS_2'] = away_games_df.groupby(['TEAM_ID_2', 'SEASON_ID'])['PTS_2'].expanding().mean().reset_index(level=[0,1], drop=True)


    #drop duplicate columns before merging
    away_games_df = away_games_df.drop(columns=['SEASON_ID', 'GAME_DATE', 'MATCHUP', 'PLUS_MINUS'])

    #merge the data based on game ID 
    games_df = pd.merge(home_games_df, away_games_df, on='GAME_ID')

    #redo the plus_minus, as some of the data seems incorrect
    games_df['PLUS_MINUS_1'] = games_df['PTS_1'] - games_df['PTS_2']
    games_df['PLUS_MINUS_2'] = games_df['PTS_2'] - games_df['PTS_1']

    

    # Calculate the rolling average of points against
    games_df = games_df.sort_values(['TEAM_ID_1', 'SEASON_ID', 'GAME_DATE'])
    games_df['AVG_PTS_OPP_1'] = games_df.groupby(['TEAM_ID_1', 'SEASON_ID'])['PTS_2'].expanding().mean().reset_index(level=[0,1], drop=True)

    games_df = games_df.sort_values(['TEAM_ID_2', 'SEASON_ID', 'GAME_DATE'])
    games_df['AVG_PTS_OPP_2'] = games_df.groupby(['TEAM_ID_2', 'SEASON_ID'])['PTS_1'].expanding().mean().reset_index(level=[0,1], drop=True)




    # Create labels (1 for win, 0 for loss) based on PLUS_MINUS
    games_df['RESULT_1'] = (games_df['PLUS_MINUS_1'] > 0).astype(int)
    games_df['RESULT_2'] = (games_df['PLUS_MINUS_2'] > 0).astype(int)


    # Write the DataFrame back to the SQLite database
    games_df.to_sql('games', conn, if_exists='replace')

    # Close the connection to the SQLite database
    conn.close()
