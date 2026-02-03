"""Test script for Semrush API."""

import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("SEMRUSH_API_KEY")
BASE_URL = "https://api.semrush.com/apis/v4-raw/external-api/v1"
WORKSPACE_ID = "a22caad0-2a96-4174-9e2f-59f1542f156b"


def test_ai_element():
    """Test the AI element endpoint with advanced filters."""
    element_id = "3c29aa85-4f06-4f14-a376-b02333c6e3fa"
    project_id = "b7880549-ea08-4d82-81d0-9633f4dcab58"

    url = f"{BASE_URL}/workspaces/{WORKSPACE_ID}/products/ai/elements/{element_id}"

    headers = {
        "accept": "application/json",
        "Authorization": f"Apikey {API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "render_data": {
            "project_id": project_id,
            "filters": {
                "simple": {
                    "start_date": "2026-01-16",
                    "end_date": "2026-01-22"
                },
                "advanced": {
                    "op": "and",
                    "filters": [
                        {
                            "op": "eq",
                            "val": "search-gpt",
                            "col": "CBF_model"
                        }
                    ]
                }
            }
        }
    }

    print(f"Making request to: {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")

    response = requests.post(url, headers=headers, json=payload)

    print(f"\nStatus Code: {response.status_code}")
    print(f"\nResponse Body:")

    try:
        print(json.dumps(response.json(), indent=2))
    except Exception:
        print(response.text)

    return response


if __name__ == "__main__":
    test_ai_element()
