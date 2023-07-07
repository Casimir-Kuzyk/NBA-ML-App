import sqlite3
import pandas as pd
import time
from nba_api.stats.static import teams
from nba_api.stats.endpoints import teamdashboardbygeneralsplits
from json.decoder import JSONDecodeError
import os

def update_team_data():

    # Get the path of the current script file
    script_path = os.path.dirname(os.path.realpath(__file__))

    # Construct the path to the database file
    db_path = os.path.join(script_path, '..', 'Data', 'nba_games.db')

    conn = sqlite3.connect(db_path)

    nba_teams = teams.get_teams()

    # Get the current season
    current_year = pd.to_datetime('today').year
    current_season = f"{current_year}-{str(current_year + 1)[2:]}"

    # Check the latest season in the database
    latest_season_in_db = pd.read_sql_query("SELECT MAX(SEASON) FROM teams", conn).iloc[0, 0]

    # If the database is empty, set the latest_season_in_db to 2009-10
    if latest_season_in_db is None:
        latest_season_in_db = '2009-10'

    # Calculate the range of seasons to fetch data for
    start_year = int(latest_season_in_db[:4])
    seasons_to_fetch = list(range(start_year, current_year))

    # Delete the most recent season's data in the database
    conn.execute("DELETE FROM teams WHERE SEASON = ?", (latest_season_in_db,))

    for year in seasons_to_fetch:
        season = f"{year}-{str(year + 1)[2:]}"

        all_team_data = []
        print(f"Fetching Team data for {season} season...")

        for team in nba_teams:
            print(f"Fetching Team data for {team['full_name']}...")
            try:
                team_dashboard = teamdashboardbygeneralsplits.TeamDashboardByGeneralSplits(team_id=team['id'], season=season)
                team_data = team_dashboard.get_data_frames()[0]

                # Add team_id and season to the dataframe
                team_data['TEAM_ID'] = team['id']
                team_data['SEASON'] = season

                all_team_data.append(team_data)
            except JSONDecodeError as e:
                print(f"Error fetching Team data for {team['full_name']} in {season}: {e}")

            time.sleep(0.6)

        all_team_data_df = pd.concat(all_team_data, ignore_index=True)

        # Append the new data to the table
        all_team_data_df.to_sql('teams', conn, if_exists='append', index=False)

    conn.close()

    print("team-level data has been updated for the latest season and appended for the newer seasons")
