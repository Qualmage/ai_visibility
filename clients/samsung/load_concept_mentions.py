"""Load concept mentions from JSON into Supabase.

Reads data/concept_mentions_{brand}.json and loads into semrush_concept_mentions table.

Usage:
    uv run load_concept_mentions.py --brand LG
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

DEFAULT_BRAND = "Samsung"
BATCH_SIZE = 500


def insert_batch(records: list) -> int:
    """Insert a batch of records into Supabase using upsert."""
    url = f"{SUPABASE_URL}/rest/v1/semrush_concept_mentions?on_conflict=date,concept,model,brand"

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
    parser = argparse.ArgumentParser(description="Load concept mentions into Supabase")
    parser.add_argument("--brand", default=DEFAULT_BRAND, help=f"Brand to load (default: {DEFAULT_BRAND})")
    args = parser.parse_args()

    if not SUPABASE_KEY:
        print("Error: SUPABASE_KEY not set")
        sys.exit(1)

    brand = args.brand
    input_file = f"data/concept_mentions_{brand.lower()}.json"

    # Load JSON data
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found")
        print(f"Run: uv run fetch_concept_mentions.py --brand {brand}")
        sys.exit(1)

    with open(input_file, "r") as f:
        records = json.load(f)

    print(f"Loading {brand} data from {input_file}")
    print(f"Loaded {len(records)} records")

    # Deduplicate by (date, concept, model, brand)
    seen = {}
    for r in records:
        key = (r["date"], r["concept"], r["model"], r["brand"])
        if key not in seen:
            seen[key] = r
        else:
            # Keep the one with higher mentions (in case of duplicates)
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

    print(f"\nDone! Loaded {total_loaded} {brand} records into Supabase")


if __name__ == "__main__":
    main()
