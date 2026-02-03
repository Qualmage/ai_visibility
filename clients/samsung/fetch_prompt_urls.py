#!/usr/bin/env python3
"""Fetch prompt-to-URL data from SEMrush API and load into Supabase.

This endpoint provides daily data linking prompts to cited URLs with tags.
Data is available from at least 2025-12-18 (can go back further if needed).
"""

import requests
import json
from datetime import datetime, timedelta
from supabase import create_client

# SEMrush API config
SEMRUSH_API_BASE = "https://api.semrush.com/apis/v4-raw/external-api/v1"
SEMRUSH_WORKSPACE_ID = "a22caad0-2a96-4174-9e2f-59f1542f156b"
SEMRUSH_PROJECT_ID = "b7880549-ea08-4d82-81d0-9633f4dcab58"
SEMRUSH_API_KEY = "fef05566690951688a288626dafffb74"
SEMRUSH_ELEMENT_ID = "c0cffe83-8104-4cfb-afac-9b1db673d29e"

# Supabase config
SUPABASE_URL = "https://zozzhptqoclvbfysmopg.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InpvenpocHRxb2NsdmJmeXNtb3BnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjkwNzA2NzksImV4cCI6MjA4NDY0NjY3OX0.3Q9gv49xrtqdmlesJgYDMVYUwjldy45xZw7O-nkASus"


def fetch_day(date_str: str) -> list:
    """Fetch prompt-URL data for a single day."""
    url = f"{SEMRUSH_API_BASE}/workspaces/{SEMRUSH_WORKSPACE_ID}/products/ai/elements/{SEMRUSH_ELEMENT_ID}"

    payload = {
        "render_data": {
            "project_id": SEMRUSH_PROJECT_ID,
            "filters": {
                "simple": {
                    "start_date": date_str,
                    "end_date": date_str
                }
            }
        }
    }

    headers = {
        "accept": "application/json",
        "Authorization": f"Apikey {SEMRUSH_API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()

    data = response.json()
    return data.get("blocks", {}).get("data", [])


def main():
    # Date range: Jan 1, 2026 to today
    start_date = datetime(2026, 1, 1)
    end_date = datetime.now()

    print(f"Fetching data from {start_date.date()} to {end_date.date()}")
    print("Note: Data may be available earlier (from ~2025-12-18)")

    # Connect to Supabase
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

    current_date = start_date
    total_inserted = 0

    while current_date <= end_date:
        date_str = current_date.strftime("%Y-%m-%d")

        try:
            # Fetch data for this day
            rows = fetch_day(date_str)

            if rows:
                # Transform rows for insertion
                records = []
                for row in rows:
                    # Parse date from ISO format
                    row_date = row.get("date", date_str)
                    if "T" in row_date:
                        row_date = row_date.split("T")[0]

                    records.append({
                        "date": row_date,
                        "prompt": row.get("prompt", ""),
                        "source": row.get("source", ""),
                        "tags": row.get("tags"),
                        "model": row.get("model"),
                        "position": row.get("position"),
                        "domain_type": row.get("domain_type")
                    })

                # Insert batch
                result = supabase.table("semrush_prompt_urls").insert(records).execute()
                total_inserted += len(records)
                print(f"{date_str}: Inserted {len(records)} rows (total: {total_inserted})")
            else:
                print(f"{date_str}: No data")

        except Exception as e:
            print(f"{date_str}: Error - {e}")

        current_date += timedelta(days=1)

    print(f"\nDone! Total inserted: {total_inserted} rows")


if __name__ == "__main__":
    main()
