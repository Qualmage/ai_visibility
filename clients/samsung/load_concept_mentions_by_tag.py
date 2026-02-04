"""Load concept mentions by tag from JSON into Supabase.

Reads data/concept_mentions_by_tag.json and loads into semrush_concept_mentions_by_tag table.

Usage:
    uv run load_concept_mentions_by_tag.py
"""

import os
import sys
import json
import argparse
import requests
from dotenv import load_dotenv

load_dotenv()

# Supabase config
SUPABASE_URL = "https://zozzhptqoclvbfysmopg.supabase.co"
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

BATCH_SIZE = 500


def insert_batch(records: list) -> int:
    """Insert a batch of records into Supabase using upsert."""
    url = f"{SUPABASE_URL}/rest/v1/semrush_concept_mentions_by_tag?on_conflict=date,tag,concept,model,brand"

    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal,resolution=merge-duplicates"
    }

    response = requests.post(url, headers=headers, json=records)
    response.raise_for_status()
    return len(records)


def main():
    parser = argparse.ArgumentParser(description="Load concept mentions by tag into Supabase")
    parser.add_argument("--input", default="data/concept_mentions_by_tag.json", help="Input JSON file")
    args = parser.parse_args()

    if not SUPABASE_KEY:
        print("Error: SUPABASE_KEY not set")
        sys.exit(1)

    input_file = args.input

    # Load JSON data
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found")
        print("Run: uv run fetch_concept_mentions_by_tag.py --all")
        sys.exit(1)

    with open(input_file, "r") as f:
        records = json.load(f)

    print(f"Loading data from {input_file}")
    print(f"Loaded {len(records)} records")

    # Deduplicate by (date, tag, concept, model, brand)
    seen = {}
    for r in records:
        key = (r["date"], r["tag"], r["concept"], r["model"], r["brand"])
        if key not in seen:
            seen[key] = r
        else:
            # Keep the one with higher mentions
            if r["mentions"] > seen[key]["mentions"]:
                seen[key] = r

    deduped = list(seen.values())
    print(f"After deduplication: {len(deduped)} unique records")

    # Insert in batches
    total_loaded = 0
    total_batches = (len(deduped) + BATCH_SIZE - 1) // BATCH_SIZE

    for i in range(0, len(deduped), BATCH_SIZE):
        batch = deduped[i:i + BATCH_SIZE]
        batch_num = i // BATCH_SIZE + 1

        try:
            count = insert_batch(batch)
            total_loaded += count
            print(f"Batch {batch_num}/{total_batches}: inserted {count} records (total: {total_loaded})")
        except requests.exceptions.HTTPError as e:
            print(f"Batch {batch_num}/{total_batches}: Error - {e}")
            if hasattr(e, 'response'):
                print(f"  {e.response.text[:500]}")

    print(f"\nDone! Loaded {total_loaded} records into Supabase")


if __name__ == "__main__":
    main()
