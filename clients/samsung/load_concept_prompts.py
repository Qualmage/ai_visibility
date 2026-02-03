#!/usr/bin/env python3
"""Load concept-to-prompts data into Supabase."""

import json
import os
from supabase import create_client

SUPABASE_URL = "https://zozzhptqoclvbfysmopg.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InpvenpocHRxb2NsdmJmeXNtb3BnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjkwNzA2NzksImV4cCI6MjA4NDY0NjY3OX0.3Q9gv49xrtqdmlesJgYDMVYUwjldy45xZw7O-nkASus"

def main():
    # Load JSON data
    data_path = os.path.join(os.path.dirname(__file__), "data", "concept_prompts.json")
    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    rows = data["blocks"]["data"]
    print(f"Loaded {len(rows)} rows from JSON")

    # Connect to Supabase
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

    # Transform rows for insertion
    records = []
    for row in rows:
        records.append({
            "brand_name": row.get("brand_name", "Samsung"),
            "concept": row.get("concept", ""),
            "product": row.get("product"),
            "prompt": row.get("prompt", ""),
            "quote": row.get("quote"),
            "sentiment": row.get("sentiment")
        })

    # Insert in batches of 500
    batch_size = 500
    total_inserted = 0

    for i in range(0, len(records), batch_size):
        batch = records[i:i + batch_size]
        try:
            result = supabase.table("semrush_concept_prompts").insert(batch).execute()
            total_inserted += len(batch)
            print(f"Inserted batch {i // batch_size + 1}: {len(batch)} rows (total: {total_inserted})")
        except Exception as e:
            print(f"Error inserting batch {i // batch_size + 1}: {e}")

    print(f"\nDone! Total inserted: {total_inserted} rows")

if __name__ == "__main__":
    main()
