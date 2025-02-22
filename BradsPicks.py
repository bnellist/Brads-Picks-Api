import os
import requests
import numpy as np
from datetime import datetime, timedelta
from requests.exceptions import RequestException
import pandas as pd
from scipy.stats import norm
from flask import Flask, jsonify

app = Flask(__name__)

# ESPN API URL
ESPN_NBA_URL = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/statistics/players"

# Fetch data from ESPN
def fetch_espn_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except RequestException as e:
        print(f"Error fetching ESPN data: {e}")
        return None

# Get NBA player stats from ESPN
def get_espn_nba_player_stats():
    player_data = fetch_espn_data(ESPN_NBA_URL)
    if player_data:
        players = player_data['players']
        player_stats = []
        for player in players:
            name = player.get('displayName', 'N/A')
            points = player.get('stats', {}).get('points', 0)
            assists = player.get('stats', {}).get('assists', 0)
            rebounds = player.get('stats', {}).get('rebounds', 0)
            player_stats.append({
                'name': name,
                'points': points,
                'assists': assists,
                'rebounds': rebounds
            })
        return player_stats
    else:
        return []

# Calculate rolling statistics (avg, std, confidence interval)
def calculate_stats(player_data, rolling_window=7):
    df = pd.DataFrame(player_data)
    df["game_date"] = pd.to_datetime(df["game_date"]) 
    df = df.sort_values("game_date")
    df["rolling_avg"] = df["points"].rolling(window=rolling_window, min_periods=1).mean()
    df["std_dev"] = df["points"].rolling(window=rolling_window, min_periods=1).std()
    df["std_err"] = df["std_dev"] / np.sqrt(rolling_window)

    df["confidence_interval_lower"] = df["rolling_avg"] - 1.96 * df["std_err"]
    df["confidence_interval_upper"] = df["rolling_avg"] + 1.96 * df["std_err"]
    return df

# Assign scores and highlights based on player performance
def assign_scores_and_highlights(df):
    df["exceeded_avg"] = df["points"] > df["rolling_avg"]
    df["score"] = df.apply(lambda row: assign_score(row), axis=1)
    df["highlight"] = df.apply(lambda row: assign_highlight(row), axis=1)
    df["status"] = df.apply(lambda row: assign_status(row), axis=1)
    return df

# Example scoring logic
def assign_score(row):
    if row['points'] > row['rolling_avg'] + 5:
        return "A"
    elif row['points'] > row['rolling_avg']:
        return "B"
    return "C"

def assign_highlight(row):
    return "green" if row['exceeded_avg'] else "red"

def assign_status(row):
    if row['exceeded_avg']:
        return "heating up"
    return "cold"

# API route for NBA picks
@app.route("/api/nba", methods=["GET"])
def get_nba_picks():
    espn_data = get_espn_nba_player_stats()

    # Process data to calculate stats and assign scores
    processed_data = calculate_stats(espn_data)
    final_data = assign_scores_and_highlights(processed_data)

    return jsonify(final_data)

if __name__ == "__main__":
    app.run(debug=True)



