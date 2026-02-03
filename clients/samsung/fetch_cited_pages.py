"""Fetch SEMrush Cited Pages data and save to JSON.

This script fetches all cited pages from SEMrush API and saves to a local JSON file.
The data can then be loaded into Supabase via the MCP SQL tool.
"""

import os
import json
import time
import requests
from dotenv import load_dotenv

load_dotenv()

# SEMrush API config
SEMRUSH_API_KEY = os.getenv("SEMRUSH_API_KEY")
SEMRUSH_BASE_URL = "https://api.semrush.com/apis/v4-raw/external-api/v1"
WORKSPACE_ID = "a22caad0-2a96-4174-9e2f-59f1542f156b"
CITED_PAGES_ELEMENT_ID = "9dd09001-1d0e-4d28-b675-53670a2af5b0"

# Data filters
COUNTRY = "us"
CATEGORY = "OWNED_BY_TARGET"
DOMAIN = "samsung.com"
LIMIT = 1000  # Max rows per API request

OUTPUT_FILE = "data/cited_pages.json"


def fetch_cited_pages(offset: int = 0) -> dict:
    """Fetch a batch of cited pages from SEMrush API."""
    url = f"{SEMRUSH_BASE_URL}/workspaces/{WORKSPACE_ID}/products/ai/elements/{CITED_PAGES_ELEMENT_ID}"

    headers = {
        "accept": "application/json",
        "Authorization": f"Apikey {SEMRUSH_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "render_data": {
            "statistics": {
                "rowCount": {"col": "*", "func": "count"}
            },
            "pagination": {
                "limit": LIMIT,
                "offset": offset,
                "sort_columns": ["prompts_count desc"]
            },
            "filters": {
                "simple": {
                    "competitor_domains": [DOMAIN]
                },
                "advanced": {
                    "op": "and",
                    "filters": [
                        {"op": "eq", "val": COUNTRY, "col": "CBF_country"},
                        {"op": "eq", "val": CATEGORY, "col": "CBF_category"},
                        {"op": "eq", "val": " ", "col": "CBF_model"}
                    ]
                }
            }
        }
    }

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()


def main():
    """Main fetch function."""
    if not SEMRUSH_API_KEY:
        print("Error: SEMRUSH_API_KEY not set in .env")
        return

    print("Fetching SEMrush Cited Pages...")
    print(f"  Country: {COUNTRY}")
    print(f"  Category: {CATEGORY}")
    print(f"  Domain: {DOMAIN}")
    print()

    all_rows = []
    offset = 0
    total_available = None

    while True:
        print(f"Fetching batch at offset {offset}...")

        try:
            data = fetch_cited_pages(offset)
        except requests.exceptions.HTTPError as e:
            print(f"Error fetching from SEMrush: {e}")
            break

        # Extract rows from response (data is in blocks.data)
        rows = data.get("blocks", {}).get("data", [])
        stats = data.get("blocks", {}).get("data_statistics", [{}])[0]

        if total_available is None:
            total_available = stats.get("rowCount", 0)
            print(f"  Total available: {total_available}")

        if not rows:
            print("No more rows to fetch.")
            break

        all_rows.extend(rows)
        print(f"  Got {len(rows)} rows (total fetched: {len(all_rows)})")

        # Check if we've fetched all rows
        if len(all_rows) >= total_available:
            print(f"\nCompleted! Fetched all {len(all_rows)} rows.")
            break

        offset += LIMIT

        # Rate limiting - be nice to APIs
        time.sleep(0.3)

    # Save to JSON file
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

    output_data = {
        "metadata": {
            "country": COUNTRY,
            "category": CATEGORY,
            "domain": DOMAIN,
            "total_rows": len(all_rows),
            "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        },
        "rows": all_rows
    }

    with open(OUTPUT_FILE, "w") as f:
        json.dump(output_data, f, indent=2)

    print(f"\nSaved {len(all_rows)} rows to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
