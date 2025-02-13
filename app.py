import time
import threading
import requests
from flask import Flask, render_template, jsonify

app = Flask(__name__)

# Define your tokens (you could also load this from a file or environment variable)
TOKENS = [
    {"address": "token_address_1", "chain": "solana"},
    {"address": "token_address_2", "chain": "solana"},
    # Add more tokens as needed
]

# Cache for token data
token_data_cache = {}

def fetch_token_data(token):
    token_address = token["address"]
    chain = token["chain"]
    url_api = f"https://api.dexscreener.com/tokens/v1/{chain}/{token_address}"
    try:
        response = requests.get(url_api)
        data = response.json()
        if isinstance(data, list):
            if len(data) == 0:
                raise ValueError("No token data returned")
            token_info = data[0]
        elif isinstance(data, dict):
            token_info = data.get("token")
            if not token_info:
                raise ValueError("No token data returned")
        else:
            raise ValueError("Unexpected API response format")
        return token_info
    except Exception as e:
        print(f"Error fetching data for {token_address}: {e}")
        return {"error": str(e)}

def update_token_data_cache():
    """Continuously update token_data_cache every second."""
    global token_data_cache
    while True:
        for token in TOKENS:
            token_data_cache[token["address"]] = fetch_token_data(token)
        # Wait 1 second before updating again
        time.sleep(1)

@app.route("/")
def index():
    # The template can refresh itself every second
    return render_template("index.html", token_data=token_data_cache)

@app.route("/api/data")
def api_data():
    # Optional: provide an API endpoint that returns the JSON data
    return jsonify(token_data_cache)

if __name__ == "__main__":
    # Start the background thread to update token data
    threading.Thread(target=update_token_data_cache, daemon=True).start()
    # Run Flask on port 8080 (Cloud Run expects this)
    app.run(host="0.0.0.0", port=8080)
