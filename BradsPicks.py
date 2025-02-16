from flask import Flask, jsonify
import requests
import numpy as np

BradsPicks = Flask(__name__)

# API Endpoints (Replace with actual API URLs & keys)
FANDUEL_API_KEY = "your_fanduel_api_key"
THE_SCORE_API_KEY = "your_thescore_api_key"

NBA_FANDUEL_URL = "https://api.fanduel.com/v1/odds/nba"  # Example URL
NBA_SCORE_URL = "https://api.thescore.com/v1/nba/stats"  # Example URL

NCAA_FANDUEL_URL = "https://api.fanduel.com/v1/odds/ncaab"  # Example URL
NCAA_SCORE_URL = "https://api.thescore.com/v1/ncaab/stats"  # Example URL

# Function to fetch odds & player props
def fetch_data(fanduel_url, score_url):
    headers = {"Authorization": f"Bearer {FANDUEL_API_KEY}"}
    fanduel_response = requests.get(fanduel_url, headers=headers)
    
    headers = {"Authorization": f"Bearer {THE_SCORE_API_KEY}"}
    score_response = requests.get(score_url, headers=headers)

    if fanduel_response.status_code == 200 and score_response.status_code == 200:
        return fanduel_response.json(), score_response.json()
    
    return None, None

# Function to calculate betting insights
def calculate_betting_insights(fanduel_data, score_data):
    if not fanduel_data or not score_data:
        return {"error": "Failed to fetch data from FanDuel or The Score."}

    insights = []
    
    for game in fanduel_data["games"]:
        teams = game["teams"]
        spread = game["spread"]
        total = game["total"]

        team_stats = [team for team in score_data["teams"] if team["name"] in teams]
        if len(team_stats) < 2:
            continue

        team1, team2 = team_stats
        team1_avg_pts = np.mean(team1["last_10_games"]["points"])
        team2_avg_pts = np.mean(team2["last_10_games"]["points"])
        expected_total = team1_avg_pts + team2_avg_pts

        spread_confidence = abs(team1_avg_pts - team2_avg_pts) / spread
        total_confidence = expected_total / total

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

# NBA Picks API
@BradsPicks.route("/api/nba", methods=["GET"])
def get_nba_picks():
    fanduel_data, score_data = fetch_data(NBA_FANDUEL_URL, NBA_SCORE_URL)
    return jsonify(calculate_betting_insights(fanduel_data, score_data))

# NCAA Picks API
@BradsPicks.route("/api/ncaa", methods=["GET"])
def get_ncaa_picks():
    fanduel_data, score_data = fetch_data(NCAA_FANDUEL_URL, NCAA_SCORE_URL)
    return jsonify(calculate_betting_insights(fanduel_data, score_data))

# Smart API - Returns NBA picks, but defaults to NCAA if no NBA games are available
@BradsPicks.route("/api/stats", methods=["GET"])
def get_smart_picks():
    fanduel_data, score_data = fetch_data(NBA_FANDUEL_URL, NBA_SCORE_URL)
    insights = calculate_betting_insights(fanduel_data, score_data)

    if not insights["top_bets"]:  # If no NBA picks, try NCAA
        fanduel_data, score_data = fetch_data(NCAA_FANDUEL_URL, NCAA_SCORE_URL)
        insights = calculate_betting_insights(fanduel_data, score_data)

    return jsonify(insights)

if __name__ == "__main__":
    BradsPicks.run(host="0.0.0.0", port=8080)
