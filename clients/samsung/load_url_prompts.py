"""Load URL prompts from JSON files into Supabase.

Reads JSON files from data/url_prompts/ and loads into semrush_url_prompts table.
"""

import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

# Supabase config
SUPABASE_URL = "https://zozzhptqoclvbfysmopg.supabase.co"
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

INPUT_DIR = "data/url_prompts"
COUNTRY = "us"
BATCH_SIZE = 500


def insert_batch(records: list) -> int:
    """Insert a batch of records into Supabase using upsert."""
    url = f"{SUPABASE_URL}/rest/v1/semrush_url_prompts?on_conflict=url,prompt_hash,country"

    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal,resolution=merge-duplicates"
    }

    response = requests.post(url, headers=headers, json=records)
    response.raise_for_status()
    return len(records)


def dedupe_batch(records: list) -> list:
    """Remove duplicates from batch based on (url, prompt_hash, country) key."""
    seen = set()
    deduped = []
    for r in records:
        key = (r["url"], r["prompt_hash"], r["country"])
        if key not in seen:
            seen.add(key)
            deduped.append(r)
    return deduped


def main():
    if not SUPABASE_KEY:
        print("Error: SUPABASE_KEY not set")
        return

    # Get all JSON files
    files = [f for f in os.listdir(INPUT_DIR) if f.endswith(".json")]
    print(f"Found {len(files)} JSON files to load")

    # First, collect ALL records and dedupe globally
    all_records = {}  # Use dict keyed by (url, prompt_hash, country) for deduping

    for i, filename in enumerate(files):
        filepath = os.path.join(INPUT_DIR, filename)

        with open(filepath, "r") as f:
            data = json.load(f)

        url = data["url"]
        prompts = data["prompts"]

        print(f"[{i+1}/{len(files)}] Reading: {url[:50]}... ({len(prompts)} prompts)")

        for prompt in prompts:
            key = (url, prompt["prompt_hash"], COUNTRY)
            if key not in all_records:
                all_records[key] = {
                    "url": url,
                    "prompt": prompt["prompt"],
                    "prompt_hash": prompt["prompt_hash"],
                    "topic": prompt.get("topic"),
                    "llm": prompt.get("llm"),
                    "volume": prompt.get("volume"),
                    "mentioned_brands_count": prompt.get("mentioned_brands_count"),
                    "used_sources_count": prompt.get("used_sources_count"),
                    "serp_id": prompt.get("serp_id"),
                    "country": COUNTRY
                }

    records_list = list(all_records.values())
    print(f"\nTotal unique records to insert: {len(records_list)}")

    # Insert in batches
    total_loaded = 0
    for i in range(0, len(records_list), BATCH_SIZE):
        batch = records_list[i:i + BATCH_SIZE]
        batch_num = i // BATCH_SIZE + 1
        total_batches = (len(records_list) + BATCH_SIZE - 1) // BATCH_SIZE

        try:
            count = insert_batch(batch)
            total_loaded += count
            print(f"Batch {batch_num}/{total_batches}: inserted {count} records (total: {total_loaded})")
        except requests.exceptions.HTTPError as e:
            print(f"Batch {batch_num}/{total_batches}: Error - {e}")
            if hasattr(e, 'response'):
                print(f"  {e.response.text[:300]}")

    print(f"\nDone! Loaded {total_loaded} records into Supabase")


if __name__ == "__main__":
    main()
