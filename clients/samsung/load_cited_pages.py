"""Load SEMrush Cited Pages data into Supabase.

Loads data from the local JSON file (fetched by fetch_cited_pages.py) into Supabase.
"""

import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

# Supabase config
SUPABASE_URL = "https://zozzhptqoclvbfysmopg.supabase.co"
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

INPUT_FILE = "data/cited_pages.json"
BATCH_SIZE = 500  # Rows per insert request


def insert_batch(rows: list, metadata: dict) -> int:
    """Insert a batch of rows into Supabase."""
    url = f"{SUPABASE_URL}/rest/v1/semrush_cited_pages"

    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates"
    }

    records = []
    for row in rows:
        records.append({
            "url": row["url"],
            "prompts_count": row["prompts_count"],
            "country": metadata["country"],
            "category": metadata["category"],
            "domain": metadata["domain"]
        })

    response = requests.post(url, headers=headers, json=records)
    response.raise_for_status()
    return len(records)


def main():
    if not SUPABASE_KEY:
        print("Error: SUPABASE_KEY not set in .env")
        return

    # Load JSON data
    print(f"Loading data from {INPUT_FILE}...")
    with open(INPUT_FILE, "r") as f:
        data = json.load(f)

    metadata = data["metadata"]
    rows = data["rows"]

    print(f"Found {len(rows)} rows to load")
    print(f"  Country: {metadata['country']}")
    print(f"  Category: {metadata['category']}")
    print(f"  Domain: {metadata['domain']}")
    print()

    total_loaded = 0

    for i in range(0, len(rows), BATCH_SIZE):
        batch = rows[i:i + BATCH_SIZE]
        batch_num = i // BATCH_SIZE + 1
        total_batches = (len(rows) + BATCH_SIZE - 1) // BATCH_SIZE

        try:
            count = insert_batch(batch, metadata)
            total_loaded += count
            print(f"Batch {batch_num}/{total_batches}: inserted {count} rows (total: {total_loaded})")
        except requests.exceptions.HTTPError as e:
            print(f"Error on batch {batch_num}: {e}")
            if hasattr(e, 'response'):
                print(f"Response: {e.response.text[:500]}")
            break

    print(f"\nDone! Loaded {total_loaded} rows into Supabase")


if __name__ == "__main__":
    main()
