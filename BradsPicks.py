import os
import requests
import numpy as np
from datetime import datetime, timedelta
from requests.exceptions import RequestException

# ... (API URLs and API key retrieval from environment variables) ...

def fetch_fanduel_data(url, api_key):
    # Add error handling (retries, exception handling)
    headers = {"Authorization": f"Bearer {api_key}"}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
        return response.json()
    except RequestException as e:
        print(f"Error fetching FanDuel data: {e}")
        return None


def fetch_the_score_data(url, api_key):
    # Add error handling (retries, exception handling)
    headers = {"Authorization": f"Bearer {api_key}"}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        return response.json()
    except RequestException as e:
        print(f"Error fetching The Score data: {e}")
        return None

# Example Usage (adapt to your specific API endpoints)
fanduel_data = fetch_fanduel_data(FANDUEL_NBA_URL, FANDUEL_API_KEY)
the_score_data = fetch_the_score_data(THE_SCORE_NBA_URL, THE_SCORE_API_KEY)

def clean_data(fanduel_data, the_score_data):
    # Filter for today's games (adapt based on your API data structures)
    todays_games = [game for game in fanduel_data.get("games", []) if is_todays_game(game)]

    # Combine FanDuel and The Score data (needs careful mapping based on your API data)
    combined_data = []
    for game in todays_games:
        # ... (Logic to map FanDuel game data with The Score player/team data) ...
        # This will require careful consideration of how your APIs represent data, such as team names and player IDs.
        combined_data.extend(create_game_data(game, the_score_data))  

    # Remove injured and non-starting players
    cleaned_data = [player for player in combined_data if player.get("is_injured", False) is False and player.get("is_starter", False) is True]
    return cleaned_data

def is_todays_game(game):
    game_date_str = game.get("date") # Adapt to actual key name from your API
    if game_date_str:
        try:
            game_date = datetime.fromisoformat(game_date_str)  # Adapt to date format
            return game_date == datetime.now().date()
        except ValueError:
            return False
    return False

def create_game_data(game, score_data):
    #Implementation to map game and player data based on how your APIs are structured.
    #This is the most critical part and highly dependent on your API response structures.  
    #You'll likely need to extract team names and player IDs from FanDuel and match them with 
    #corresponding data in The Score to create a single combined data entry for each player.
    pass
import pandas as pd
from scipy.stats import norm

def calculate_stats(player_data, rolling_window=7):
    df = pd.DataFrame(player_data)
    df["game_date"] = pd.to_datetime(df["game_date"]) #Adapt column name to the actual column storing dates
    df = df.sort_values("game_date")
    df["rolling_avg"] = df["points"].rolling(window=rolling_window, min_periods=1).mean()
    df["std_dev"] = df["points"].rolling(window=rolling_window, min_periods=1).std()
    df["std_err"] = df["std_dev"] / np.sqrt(rolling_window)

    #Confidence interval (95%) using normal distribution
    df["confidence_interval_lower"] = df["rolling_avg"] - 1.96 * df["std_err"]
    df["confidence_interval_upper"] = df["rolling_avg"] + 1.96 * df["std_err"]
    return df

def assign_scores_and_highlights(df):
    df["exceeded_avg"] = df["points"] > df["rolling_avg"]
    df["score"] = df.apply(lambda row: assign_score(row), axis=1) #Function to generate score (A,B,C)
    df["highlight"] = df.apply(lambda row: assign_highlight(row), axis=1) #Function to generate color
    df["status"] = df.apply(lambda row: assign_status(row), axis=1) #Function to generate status (heating up, on fire, cold)
    return df

def assign_score(row):
    # Your logic to assign A, B, or C scores based on the calculated stats
    pass

def assign_highlight(row):
    # Your logic to assign green or red based on exceeded_avg
    pass

def assign_status(row):
    # Your logic to assign "heating up", "on fire", or "cold" based on exceeded_avg count
    pass
@app.route("/api/nba", methods=["GET"])
def get_nba_picks():
    fanduel_data = fetch_fanduel_data(FANDUEL_NBA_URL, FANDUEL_API_KEY)
    the_score_data = fetch_the_score_data(THE_SCORE_NBA_URL, THE_SCORE_API_KEY)
    cleaned_data = clean_data(fanduel_data, the_score_data)
    processed_data = calculate_stats(cleaned_data)
    final_data = assign_scores_and_highlights(processed_data)
    return jsonify(final_data)

# ... (Other API endpoints similar to above) ...



