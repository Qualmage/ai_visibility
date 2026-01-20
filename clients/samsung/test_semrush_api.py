"""Test script for Semrush API."""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("SEMRUSH_API_KEY")
BASE_URL = "https://api.semrush.com/apis/v4-raw/external-api/v1"
WORKSPACE_ID = "a22caad0-2a96-4174-9e2f-59f1542f156b"
ELEMENT_ID = "184a8d65-2248-4030-86e2-288340667f87"


def test_seo_element():
    """Test the SEO element endpoint."""
    url = f"{BASE_URL}/workspaces/{WORKSPACE_ID}/products/seo/elements/{ELEMENT_ID}"

    headers = {
        "accept": "application/json",
        "Authorization": f"Apikey {API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "render_data": {
            "filters": {
                "simple": {
                    "start_date": "2025-12-16",
                    "end_date": "2026-01-14"
                }
            }
        }
    }

    print(f"Making request to: {url}")
    print(f"Payload: {payload}")

    response = requests.post(url, headers=headers, json=payload)

    print(f"\nStatus Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    print(f"\nResponse Body:")

    try:
        print(response.json())
    except Exception:
        print(response.text)

    return response


if __name__ == "__main__":
    test_seo_element()
