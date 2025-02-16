from flask import Flask, jsonify
import requests
import numpy as np

BradsPicks = Flask(__name__)

# FanDuel API Endpoint (Replace with actual API URL & key)
FANDUEL_API_URL = "https://api.fanduel.com/v1/odds"  # Example URL
FANDUEL_API_KEY = "your_fanduel_api_key"

# The Score API Endpoint (Replace with actual API URL & key)
THE_SCORE_API_URL = "https://api.thescore.com/v1/nba/stats"  # Example URL
THE_SCORE_API_KEY = "your_thescore_api_key"

# Function to fetch odds & player props from FanDuel
def fetch_fanduel_data():
    headers = {"Authorization": f"Bearer {FANDUEL_API_KEY}"}
    response = requests.get(FANDUEL_API_URL, headers=headers)
    if response.status_code == 200:
        return response.json()
    return None

# Function to fetch player & team stats from The Score
def fetch_the_score_data():
    headers = {"Authorization": f"Bearer {THE_SCORE_API_KEY}"}
    response = requests.get(THE_SCORE_API_URL, headers=headers)
    if response.status_code == 200:
        return response.json()
    return None

# Function to calculate betting insights
def calculate_betting_insights():
    fanduel_data = fetch_fanduel_data()
    score_data = fetch_the_score_data()
    
    if not fanduel_data or not score_data:
        return {"error": "Failed to fetch data from FanDuel or The Score."}

    insights = []
    
    for game in fanduel_data["games"]:
        teams = game["teams"]
        spread = game["spread"]
        total = game["total"]

        # Fetch team stats from The Score
        team_stats = [team for team in score_data["teams"] if team["name"] in teams]
        
        if len(team_stats) < 2:
            continue
        
        team1, team2 = team_stats

        # Calculate rolling averages & probabilities
        team1_avg_pts = np.mean(team1["last_10_games"]["points"])
        team2_avg_pts = np.mean(team2["last_10_games"]["points"])
        expected_total = team1_avg_pts + team2_avg_pts

        # Determine betting edge
        spread_confidence = abs(team1_avg_pts - team2_avg_pts) / spread
        total_confidence = expected_total / total

        # Assign a grade (A+ to C-)
        spread_grade = "A+" if spread_confidence > 1.2 else "B" if spread_confidence > 1.0 else "C-"
        total_grade = "A+" if total_confidence > 1.2 else "B" if total_confidence > 1.0 else "C-"

        insights.append({
            "matchup": f"{teams[0]} vs {teams[1]}",
            "spread_pick": teams[0] if team1_avg_pts > team2_avg_pts else teams[1],
            "spread_grade": spread_grade,
            "over_under_pick": "Over" if expected_total > total else "Under",
            "total_grade": total_grade
        })

    return {"top_bets": insights}

# API Endpoint to Get Betting Picks
@BradsPicks.route("/api/stats", methods=["GET"])
def get_stats():
    return jsonify(calculate_betting_insights())

if __name__ == "__main__":
    BradsPicks.run(host="0.0.0.0", port=8080)
