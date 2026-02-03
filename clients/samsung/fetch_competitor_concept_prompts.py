#!/usr/bin/env python3
"""Fetch concept-to-prompts data for competitor brands from SEMrush API.

Fetches LG, Sony, TCL, Hisense data to enable true competitive SoV analysis.
Rate limit: 600 requests/hour - this script uses ~116 calls (29 days × 4 brands).

Usage:
    uv run clients/samsung/fetch_competitor_concept_prompts.py
"""

import requests
import time
from datetime import datetime, timedelta
from supabase import create_client

# SEMrush API config
SEMRUSH_API_BASE = "https://api.semrush.com/apis/v4-raw/external-api/v1"
SEMRUSH_WORKSPACE_ID = "a22caad0-2a96-4174-9e2f-59f1542f156b"
SEMRUSH_PROJECT_ID = "b7880549-ea08-4d82-81d0-9633f4dcab58"
SEMRUSH_API_KEY = "fef05566690951688a288626dafffb74"
SEMRUSH_ELEMENT_ID = "6c914007-60fd-4105-911a-9fb8861be2ec"

# Supabase config
SUPABASE_URL = "https://zozzhptqoclvbfysmopg.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InpvenpocHRxb2NsdmJmeXNtb3BnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjkwNzA2NzksImV4cCI6MjA4NDY0NjY3OX0.3Q9gv49xrtqdmlesJgYDMVYUwjldy45xZw7O-nkASus"

# Competitor brands to fetch
BRANDS = ["LG", "Sony", "TCL", "Hisense"]

# Rate limiting (be conservative)
REQUEST_DELAY = 1.0  # seconds between requests


def fetch_day(date_str: str, brand: str) -> list:
    """Fetch concept-prompts data for a single day and brand."""
    url = f"{SEMRUSH_API_BASE}/workspaces/{SEMRUSH_WORKSPACE_ID}/products/ai/elements/{SEMRUSH_ELEMENT_ID}"

    payload = {
        "render_data": {
            "project_id": SEMRUSH_PROJECT_ID,
            "filters": {
                "simple": {
                    "start_date": date_str,
                    "end_date": date_str
                },
                "advanced": {
                    "op": "and",
                    "filters": [
                        {"op": "eq", "val": brand, "col": "CBF_brand"}
                    ]
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
    # Date range: Jan 1, 2026 to Jan 29, 2026 (match existing Samsung data)
    start_date = datetime(2026, 1, 1)
    end_date = datetime(2026, 1, 29)

    days = (end_date - start_date).days + 1
    total_calls = days * len(BRANDS)

    print(f"Fetching concept-prompts for competitors: {', '.join(BRANDS)}")
    print(f"Date range: {start_date.date()} to {end_date.date()} ({days} days)")
    print(f"Total API calls: {total_calls}")
    print(f"Estimated time: {total_calls * REQUEST_DELAY / 60:.1f} minutes")
    print("-" * 60)

    # Connect to Supabase
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

    total_inserted = 0
    call_count = 0
    start_time = time.time()

    for brand in BRANDS:
        brand_inserted = 0
        current_date = start_date

        print(f"\n{'='*60}")
        print(f"Fetching {brand}...")
        print(f"{'='*60}")

        while current_date <= end_date:
            date_str = current_date.strftime("%Y-%m-%d")
            call_count += 1

            try:
                # Fetch data for this day
                rows = fetch_day(date_str, brand)

                if rows:
                    # Transform rows for insertion
                    records = []
                    for row in rows:
                        records.append({
                            "date": date_str,
                            "brand_name": row.get("brand_name", brand),
                            "concept": row.get("concept", ""),
                            "product": row.get("product"),
                            "prompt": row.get("prompt", ""),
                            "quote": row.get("quote"),
                            "sentiment": row.get("sentiment")
                        })

                    # Insert in batches of 500
                    batch_size = 500
                    for i in range(0, len(records), batch_size):
                        batch = records[i:i + batch_size]
                        supabase.table("semrush_concept_prompts").insert(batch).execute()

                    brand_inserted += len(records)
                    total_inserted += len(records)

                    elapsed = time.time() - start_time
                    rate = call_count / elapsed * 60 if elapsed > 0 else 0
                    print(f"[{call_count}/{total_calls}] {brand} {date_str}: {len(records):,} rows (total: {total_inserted:,}, {rate:.0f} calls/min)")
                else:
                    print(f"[{call_count}/{total_calls}] {brand} {date_str}: No data")

            except Exception as e:
                print(f"[{call_count}/{total_calls}] {brand} {date_str}: Error - {e}")

            current_date += timedelta(days=1)
            time.sleep(REQUEST_DELAY)

        print(f"\n{brand} complete: {brand_inserted:,} rows inserted")

    elapsed = time.time() - start_time
    print(f"\n{'='*60}")
    print(f"DONE!")
    print(f"Total inserted: {total_inserted:,} rows")
    print(f"Time elapsed: {elapsed/60:.1f} minutes")
    print(f"Average rate: {call_count / elapsed * 60:.0f} calls/min")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
