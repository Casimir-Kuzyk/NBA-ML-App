from sklearn.preprocessing import StandardScaler
import numpy as np
import sqlite3
import pandas as pd
import pickle


scaler = StandardScaler()

def get_team1_avg_pts(team_name, conn):
    # Write a SQL query to fetch the latest AVG_PTS and AVG_PTS_OPP for the given team_name
    #TODO: this is vulnerable to SQL injections.. currently assuming this chunk of code won't be used in the webapp
    query = f"""
    SELECT AVG_PTS_1, AVG_PTS_OPP_1
    FROM games
    WHERE TEAM_NAME_1 = '{team_name}'
    ORDER BY GAME_DATE DESC
    LIMIT 1
    """
    
    # Execute the query and fetch the result
    result = pd.read_sql_query(query, conn)
    
    # Check if the query returned a result
    if len(result) > 0:
        return result.iloc[0]['AVG_PTS_1'], result.iloc[0]['AVG_PTS_OPP_1']
    else:
        print(f"No data found for team_name {team_name}")
        return None, None
    
def get_team2_avg_pts(team_name, conn):
    # Write a SQL query to fetch the latest AVG_PTS and AVG_PTS_OPP for the given team_name
    #TODO: this is vulnerable to SQL injections.. currently assuming this chunk of code won't be used in the webapp
    query = f"""
    SELECT AVG_PTS_2, AVG_PTS_OPP_2
    FROM games
    WHERE TEAM_NAME_2 = '{team_name}'
    ORDER BY GAME_DATE DESC
    LIMIT 1
    """
    
    # Execute the query and fetch the result
    result = pd.read_sql_query(query, conn)
    
    # Check if the query returned a result
    if len(result) > 0:
        return result.iloc[0]['AVG_PTS_2'], result.iloc[0]['AVG_PTS_OPP_2']
    else:
        print(f"No data found for team_name {team_name}")
        return None, None

def predict(model, team1_name, team2_name, team1_odds, team2_odds, conn):
    # Get the AVG_PTS and AVG_PTS_OPP for both teams
    team1_avg_pts, team1_avg_pts_opp = get_team1_avg_pts(team1_name, conn)
    team2_avg_pts, team2_avg_pts_opp = get_team2_avg_pts(team2_name, conn)
    print(f'team 1 average points: {team1_avg_pts}, team 1 avg points against: {team1_avg_pts_opp}, team 2 avg points: {team2_avg_pts}, team 2 avg points against: {team2_avg_pts_opp}')
    
    # Create an array with the data
    data = np.array([[team1_avg_pts, team2_avg_pts, team1_avg_pts_opp, team2_avg_pts_opp]])
    data_df = pd.DataFrame(data, columns=['AVG_PTS_1', 'AVG_PTS_2', 'AVG_PTS_OPP_1', 'AVG_PTS_OPP_2'])

    # Load scaler from disk
    with open('./Models/nba_scaler.pkl', 'rb') as f:
        scaler = pickle.load(f)

    # Normalize the data
    data = scaler.transform(data_df)
    
    # Use the model to make a prediction
    #TODO: this model considers the game between two teams as two separate instances - one from the perspective of team1 and the other from the perspective of team2. 
    # This might not be the best approach for a game prediction model. Ideally, we should have features indicating the two teams playing the game and predict the outcome in a single instance.
    prediction = model.predict(data)
    print(f"The model predicts that {team1_name} has a {prediction[0]*100}% chance of winning against {team2_name}")


    #now calculate the expected value for each team.
    team1_EV = (prediction[0]*(team1_odds-1) - (1 - prediction[0]))*100
    team2_EV = ((1 - prediction[0])*(team2_odds-1) - (prediction[0]))*100

    print(f"The expected value for {team1_name} is {team1_EV}% and for {team2_name} is {team2_EV}%")

    #calculate expected value https://www.pinnacle.com/en/betting-articles/Betting-Strategy/how-to-calculate-expected-value/EES2VE46TM4HTT32
    #(Probability of Winning) x (Amount Won per Bet) – (Probability of Losing) x (Amount Lost per Bet)
    #Where the probability of winning is based on our ML model prediction
    # i.e. if Miami odds are 2.35 (100/2.35 = 42.55% chance of winning), and Knicks odds are 1.64 (60.97% chance of winning), but the ML model predicts that Miami chance of winning is 46.75%, then..
    #(0.4675) * (10 * 2.35 - 10) - (0.5325) * (10) = 0.98625 ==> positive number indicates this is a good bet! (you would on average $0.98 per bet if you were to place a $10 bet on this infinite times..)


    return prediction
