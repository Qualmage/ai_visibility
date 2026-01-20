"""
Flask backend for Samsung SEMrush Dashboard.
Proxies API calls to avoid CORS issues.
"""

import os
from pathlib import Path

import requests
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

app = Flask(__name__, static_folder=".")
CORS(app)

SEMRUSH_BASE_URL = "https://api.semrush.com/apis/v4-raw/external-api/v1"
SEMRUSH_API_KEY = os.getenv("SEMRUSH_API_KEY")


@app.route("/")
def index():
    return send_from_directory("dashboards", "v1-api-connected.html")


@app.route("/dashboards/<path:filename>")
def dashboards(filename):
    return send_from_directory("dashboards", filename)


@app.route("/assets/<path:filename>")
def assets(filename):
    return send_from_directory("assets", filename)


@app.route("/assets/fonts/<path:filename>")
def fonts(filename):
    return send_from_directory("assets/fonts", filename)


@app.route("/api/proxy", methods=["POST"])
def proxy():
    """Proxy requests to SEMrush API."""
    if not SEMRUSH_API_KEY:
        return jsonify({"error": "SEMRUSH_API_KEY not set in .env"}), 500

    data = request.json
    endpoint = data.get("endpoint")
    payload = data.get("payload")

    if not endpoint:
        return jsonify({"error": "Missing endpoint"}), 400

    url = f"{SEMRUSH_BASE_URL}{endpoint}"

    headers = {
        "Authorization": f"Apikey {SEMRUSH_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.exceptions.HTTPError as e:
        return jsonify({"error": str(e), "details": e.response.text}), e.response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    print("Starting Samsung SEMrush Dashboard...")
    print("Open http://localhost:5000 in your browser")
    app.run(debug=True, port=5000)
