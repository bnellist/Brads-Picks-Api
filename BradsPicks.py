import os
import time
import requests
import numpy as np
from flask import Flask, jsonify, request
from requests.exceptions import RequestException

app = Flask(__name__)

# Get API keys from environment variables
FANDUEL_API_KEY = os.getenv("FANDUEL_API_KEY")
THE_SCORE_API_KEY = os.getenv("THE_SCORE_API_KEY")

# ... (API URLs remain the same) ...

def fetch_data(url, api_key, max_retries=3, retry_delay=2):
    headers = {"Authorization": f"Bearer {api_key}"}
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers, timeout=10)  # Add timeout
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            return response.json()
        except RequestException as e:
            if attempt == max_retries - 1:
                print(f"Error fetching data from {url}: {e}")
                return None
            print(f"Error fetching data from {url}, retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)
            retry_delay *= 2  # Exponential backoff

def calculate_betting_insights(fanduel_data, score_data):
    if not fanduel_data or not score_data:
        return {"error": "Failed to fetch data."}
    # Add data validation here...  Check if keys exist before accessing them.

    # ... (Data transformation and calculation logic. Needs to be adapted to your actual data structure) ...

@app.route("/api/nba", methods=["GET"])
def get_nba_picks():
    fanduel_data = fetch_data(NBA_FANDUEL_URL, FANDUEL_API_KEY)
    score_data = fetch_data(NBA_SCORE_URL, THE_SCORE_API_KEY)
    return jsonify(calculate_betting_insights(fanduel_data, score_data))

# ... (Other API endpoints similarly revised) ...

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
