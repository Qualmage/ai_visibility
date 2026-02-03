"""Fetch daily concept mentions from SEMrush API.

Fetches concept mention data for each day since 2025-12-18 across all AI models.
Saves results to data/concept_mentions.json for loading to Supabase.
"""

import os
import sys
import json
import time
import argparse
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import requests
from dotenv import load_dotenv

load_dotenv()

# SEMrush API config
SEMRUSH_API_KEY = os.getenv("SEMRUSH_API_KEY")
SEMRUSH_BASE_URL = "https://api.semrush.com/apis/v4-raw/external-api/v1"
WORKSPACE_ID = "a22caad0-2a96-4174-9e2f-59f1542f156b"
CONCEPT_MENTIONS_ELEMENT_ID = "0ed4bc52-b684-41b5-9436-3f5806266631"
PROJECT_ID = "b7880549-ea08-4d82-81d0-9633f4dcab58"

# Data config
START_DATE = "2025-12-18"  # First day with data
MODELS = ["search-gpt", "google-ai-overview", "google-ai-mode"]
DEFAULT_BRAND = "Samsung"
MAX_WORKERS = 5  # Concurrent API requests
RATE_LIMIT = 0.2  # seconds between requests per worker


def parse_concept(concept: str) -> tuple[str, str, str]:
    """Parse concept into category, subcategory, and concept name.

    Format: "category__subcategory__concept" or just "concept"
    """
    parts = concept.split("__")
    if len(parts) == 3:
        return parts[2], parts[0], parts[1]  # concept, category, subcategory
    elif len(parts) == 2:
        return parts[1], parts[0], None  # concept, category, no subcategory
    else:
        return concept, None, None  # just concept


def fetch_concepts_for_day(date: str, model: str, brand: str) -> list[dict]:
    """Fetch all concept mentions for a specific date, model, and brand."""
    url = f"{SEMRUSH_BASE_URL}/workspaces/{WORKSPACE_ID}/products/ai/elements/{CONCEPT_MENTIONS_ELEMENT_ID}"

    headers = {
        "accept": "application/json",
        "Authorization": f"Apikey {SEMRUSH_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "render_data": {
            "project_id": PROJECT_ID,
            "filters": {
                "simple": {
                    "start_date": date,
                    "end_date": date
                },
                "advanced": {
                    "op": "and",
                    "filters": [
                        {"op": "eq", "val": brand, "col": "CBF_brand"},
                        {"op": "eq", "val": model, "col": "CBF_model"}
                    ]
                }
            }
        }
    }

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    data = response.json()

    rows = data.get("blocks", {}).get("data", [])
    return rows


def transform_row(row: dict, date: str, model: str, brand: str) -> dict:
    """Transform API response row to database format."""
    raw_concept = row.get("concept", "")
    concept, category, subcategory = parse_concept(raw_concept)

    return {
        "date": date,
        "concept": concept,
        "concept_category": category,
        "concept_subcategory": subcategory,
        "mentions": row.get("mentions_end", 0),
        "sentiment_positive": row.get("sentiment_positive", 0),
        "sentiment_negative": row.get("sentiment_negative", 0),
        "sentiment_neutral": row.get("sentiment_neutral", 0),
        "products": row.get("products", []),
        "model": model,
        "brand": brand
    }


def generate_date_range(start_date: str, end_date: str) -> list[str]:
    """Generate list of dates from start to end (inclusive)."""
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")

    dates = []
    current = start
    while current <= end:
        dates.append(current.strftime("%Y-%m-%d"))
        current += timedelta(days=1)

    return dates


def fetch_task(date: str, model: str, brand: str) -> tuple[str, str, list[dict]]:
    """Fetch task for thread pool. Returns (date, model, transformed_rows)."""
    time.sleep(RATE_LIMIT)  # Rate limit
    rows = fetch_concepts_for_day(date, model, brand)
    transformed = [transform_row(row, date, model, brand) for row in rows]
    return (date, model, transformed)


def main():
    parser = argparse.ArgumentParser(description="Fetch daily concept mentions from SEMrush")
    parser.add_argument("--brand", default=DEFAULT_BRAND, help=f"Brand to fetch (default: {DEFAULT_BRAND})")
    parser.add_argument("--start-date", default=START_DATE, help=f"Start date (default: {START_DATE})")
    parser.add_argument("--end-date", default=datetime.now().strftime("%Y-%m-%d"), help="End date (default: today)")
    parser.add_argument("--model", choices=MODELS, help="Fetch only specific model")
    parser.add_argument("--resume", action="store_true", help="Resume from existing checkpoint")
    parser.add_argument("--workers", type=int, default=MAX_WORKERS, help=f"Concurrent workers (default: {MAX_WORKERS})")
    args = parser.parse_args()

    if not SEMRUSH_API_KEY:
        print("Error: SEMRUSH_API_KEY not set")
        sys.exit(1)

    brand = args.brand
    output_file = f"data/concept_mentions_{brand.lower()}.json"

    print(f"Fetching data for brand: {brand}")
    print(f"Output file: {output_file}")
    print(f"Concurrent workers: {args.workers}")

    # Create output directory
    os.makedirs("data", exist_ok=True)

    # Load existing data if resuming
    existing_data = []
    fetched_keys = set()
    if args.resume and os.path.exists(output_file):
        with open(output_file, "r") as f:
            existing_data = json.load(f)
        for row in existing_data:
            key = (row["date"], row["model"])
            fetched_keys.add(key)
        print(f"Resume mode: loaded {len(existing_data)} existing rows")
        print(f"Already fetched: {len(fetched_keys)} date/model combinations")

    # Generate date range
    dates = generate_date_range(args.start_date, args.end_date)
    models = [args.model] if args.model else MODELS

    # Build list of tasks to fetch
    tasks = []
    for date in dates:
        for model in models:
            key = (date, model)
            if key not in fetched_keys:
                tasks.append((date, model))

    total_tasks = len(tasks)
    print(f"Tasks to fetch: {total_tasks} (skipping {len(fetched_keys)} already fetched)")

    if total_tasks == 0:
        print("Nothing to fetch!")
        return

    all_rows = existing_data.copy()
    completed = 0
    errors = 0
    lock = threading.Lock()

    def update_progress(date, model, rows, error=None):
        nonlocal completed, errors
        with lock:
            completed += 1
            if error:
                errors += 1
                print(f"[{completed}/{total_tasks}] {brand} / {date} / {model} - ERROR: {error}")
            else:
                print(f"[{completed}/{total_tasks}] {brand} / {date} / {model} - {len(rows)} concepts")

    # Fetch concurrently
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {}
        for date, model in tasks:
            future = executor.submit(fetch_task, date, model, brand)
            futures[future] = (date, model)

        for future in as_completed(futures):
            date, model = futures[future]
            try:
                _, _, rows = future.result()
                with lock:
                    all_rows.extend(rows)
                update_progress(date, model, rows)
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429:
                    update_progress(date, model, [], f"Rate limited: {e}")
                else:
                    update_progress(date, model, [], str(e))
            except Exception as e:
                update_progress(date, model, [], str(e))

            # Checkpoint save every 20 completed
            if completed % 20 == 0:
                with lock:
                    with open(output_file, "w") as f:
                        json.dump(all_rows, f, indent=2)
                    print(f"  Checkpoint saved: {len(all_rows)} total rows")

    # Final save
    with open(output_file, "w") as f:
        json.dump(all_rows, f, indent=2)

    new_rows = len(all_rows) - len(existing_data)
    print(f"\nDone! Fetched {new_rows} new rows for {brand}")
    print(f"Total rows: {len(all_rows)}")
    print(f"Errors: {errors}")
    print(f"Output file: {output_file}")


if __name__ == "__main__":
    main()
