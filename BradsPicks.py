import os
import requests
import numpy as np
from datetime import datetime
import pandas as pd
from scipy.stats import norm
from flask import Flask, jsonify
from requests.exceptions import RequestException

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
    
    if not player_data or "categories" not in player_data:
        return []

    player_stats = []
    for category in player_data["categories"]:
        for player in category.get("athletes", []):  
            name = player.get("athlete", {}).get("displayName", "N/A")
            stats = player.get("stats", [])

            # Extract key stats safely (ensure index matches ESPN's response)
            points = float(stats[0]) if stats else 0
            assists = float(stats[1]) if len(stats) > 1 else 0
            rebounds = float(stats[2]) if len(stats) > 2 else 0

            player_stats.append({
                "name": name,
                "points": points,
                "assists": assists,
                "rebounds": rebounds,
                "game_date": datetime.today().strftime("%Y-%m-%d")  # Assign a date
            })
    
    return player_stats

# Calculate rolling statistics (avg, std, confidence interval)
def calculate_stats(player_data, rolling_window=7):
    if not player_data:
        return pd.DataFrame()  # Return empty DataFrame if no data

    df = pd.DataFrame(player_data)

    # Ensure correct column names exist
    if "game_date" not in df or "points" not in df:
        return pd.DataFrame()

    df["game_date"] = pd.to_datetime(df["game_date"])
    df = df.sort_values("game_date")

    # Handle cases where not enough data exists
    df["rolling_avg"] = df["points"].rolling(window=rolling_window, min_periods=1).mean()
    df["std_dev"] = df["points"].rolling(window=rolling_window, min_periods=1).std().fillna(0)
    df["std_err"] = df["std_dev"] / np.sqrt(rolling_window)

    df["confidence_interval_lower"] = df["rolling_avg"] - 1.96 * df["std_err"]
    df["confidence_interval_upper"] = df["rolling_avg"] + 1.96 * df["std_err"]

    return df

# Assign scores and highlights based on player performance
def assign_scores_and_highlights(df):
    if df.empty:
        return df  # Return unchanged if empty

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
    
    if not espn_data:
        return jsonify({"error": "No data available"}), 500
    
    processed_data = calculate_stats(espn_data)
    if processed_data.empty:
        return jsonify({"error": "Insufficient data"}), 500

    final_data = assign_scores_and_highlights(processed_data)

    return jsonify(final_data.to_dict(orient="records"))  # Convert DataFrame to JSON serializable format

# Ensure Flask runs on the correct port in Cloud Run
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)



