from Get_Data.Get_Game_Data_NBA_API import update_game_data
from Get_Data.Get_Team_Data_NBA_API import update_team_data
from Get_Data.Get_Player_Data_NBA_API import update_player_data
from Evaluation.Evaluate_Model import evaluate_model
from Predict.predict_model import predict

import tensorflow as tf
import pandas as pd
import sqlite3
import numpy as np
import pickle

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from ann_visualizer.visualize import ann_viz

def create_and_train_model(train_data, train_labels, val_data, val_labels):
    # Define the model
    # TODO: The sequential model makes sense to use, but the data should be sorted by date first! need to make sure it is..
    # input_shape will need to increase once I add more features
    # TODO: might need to add regularization (dropout and L1/L2 regularizations)
    model = tf.keras.Sequential([ 
        tf.keras.layers.Dense(units=512, activation='relu', input_shape=(4,)),
        tf.keras.layers.Dense(units=256, activation='relu'), \
        tf.keras.layers.Dense(units=128, activation='relu'),
        tf.keras.layers.Dense(units=64, activation='relu'),
        tf.keras.layers.Dense(units=1, activation='sigmoid') #sigmoid is good for binary classification problems such as this one.. For multi-class problems, use softmax
    ])

    # Compile the model
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

    # Train the model
    model.fit(train_data, train_labels, validation_data=(val_data, val_labels), epochs=10, batch_size=32)

    ann_viz(model, view=True, filename='cconstruct_model', title='CNN — Model 1 — Simple Architecture')

    return model

def main():

    update_data = input("Do you want to update the data before running the machine learning program? (y/n): ")

    if update_data.lower() == 'y':

        #update data for ML model
        print("Updating game data...")
        update_game_data()

        print("Updating team data...")
        update_team_data()

        print("Updating player data...")
        update_player_data()

        print("All data has been updated.")

    db_path = "./Data/nba_games.db"
    conn = sqlite3.connect(db_path)

    update_model = input("Do you want to update the ML Model before making predictions? (y/n): ")

    if update_model.lower() == 'y':
        # Load the data
        games_df = pd.read_sql_query("SELECT TEAM_ID_1, AVG_PTS_1, AVG_PTS_2, AVG_PTS_OPP_1, AVG_PTS_OPP_2, RESULT_1 FROM games", conn)

        # Split the data into training and validation sets
        train_data, val_data, train_labels, val_labels = train_test_split(games_df[['AVG_PTS_1','AVG_PTS_2','AVG_PTS_OPP_1','AVG_PTS_OPP_2']], games_df[['RESULT_1']], test_size=0.2, random_state=42)

        # Scale the data --> this standardizes the features by (x - u)/s where u is the mean, and s is the standard deviation
        #best practice to use the mean and standard deviation from the training data to also standardize the validation data
        scaler = StandardScaler()
        train_data = scaler.fit_transform(train_data)
        val_data = scaler.transform(val_data)

        # Save scaler to disk
        with open('./Models/nba_scaler.pkl', 'wb') as f:
            pickle.dump(scaler, f)

        # Create and train the model
        model = create_and_train_model(train_data, train_labels, val_data, val_labels)
        model.save('./Models/nba_model.h5')

        print("Validation label counts:")
        print(val_labels['RESULT_1'].value_counts())

        # Evaluate the model on the validation set
        evaluate_model(model, val_data, val_labels)

    #predict next games
    model = tf.keras.models.load_model('./Models/nba_model.h5')

    team1_name = input("What is the first team that is playing?")
    team1_odds = float(input("What are the decimal odds of them winning?"))
    team2_name = input("who are they playing?")
    team2_odds = float(input("What are the decimal odds of them winning?"))
    predict(model,team1_name, team2_name, team1_odds, team2_odds, conn)


    conn.close()
    




if __name__ == "__main__":
    main()