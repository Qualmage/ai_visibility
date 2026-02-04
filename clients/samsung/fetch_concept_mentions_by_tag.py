"""Fetch concept mentions by tag from SEMrush API.

Fetches concept mentions filtered by each junior tag from the tag hierarchy.
Prioritizes TV Features and TV Models tags first.

Usage:
    uv run fetch_concept_mentions_by_tag.py --group tv-features
    uv run fetch_concept_mentions_by_tag.py --group tv-models
    uv run fetch_concept_mentions_by_tag.py --group tv-reviews
    uv run fetch_concept_mentions_by_tag.py --group tv-sizes
    uv run fetch_concept_mentions_by_tag.py --all
"""

import os
import sys
import json
import time
import argparse
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import requests

# SEMrush API config
SEMRUSH_API_KEY = "458717b81c2b8c976998f2cee61a9116"
SEMRUSH_BASE_URL = "https://api.semrush.com/apis/v4-raw/external-api/v1"
WORKSPACE_ID = "a22caad0-2a96-4174-9e2f-59f1542f156b"
CONCEPT_MENTIONS_ELEMENT_ID = "0ed4bc52-b684-41b5-9436-3f5806266631"
PROJECT_ID = "b7880549-ea08-4d82-81d0-9633f4dcab58"

# Data config
TARGET_DATE = "2026-01-31"
MODELS = ["search-gpt", "google-ai-overview", "google-ai-mode"]
BRANDS = ["Samsung", "LG", "Sony", "Hisense", "TCL"]
MAX_WORKERS = 5
RATE_LIMIT = 0.3  # seconds between requests

# Tag groups - prioritized order
TAG_GROUPS = {
    "tv-features": [
        "TV Features__AI",
        "TV Features__Anti-Glare",
        "TV Features__Art Mode",
        "TV Features__Brightness",
        "TV Features__Connectivity",
        "TV Features__HDR",
        "TV Features__Input Lag",
        "TV Features__Motion Handling",
        "TV Features__Panel Technology",
        "TV Features__Picture Settings",
        "TV Features__Refresh Rate",
        "TV Features__Resolution",
        "TV Features__Resolution__4K",
        "TV Features__Resolution__8K",
        "TV Features__Smart Features",
        "TV Features__Sound",
        "TV Features__Viewing Angles",
    ],
    "tv-models": [
        "TV Models__Art TV",
        "TV Models__Gaming TVs",
        "TV Models__Micro RGB",
        "TV Models__Mini-LED",
        "TV Models__Movies & Cinema",
        "TV Models__OLED",
        "TV Models__Outdoor TV",
        "TV Models__QLED",
        "TV Models__Smart TV",
        "TV Models__Sports TVs",
    ],
    "tv-reviews": [
        "TV Reviews & Brand__Affordable",
        "TV Reviews & Brand__Best Of",
        "TV Reviews & Brand__Brand",
        "TV Reviews & Brand__Brand TV Model Reviews",
        "TV Reviews & Brand__Brand__TV Features__AI",
        "TV Reviews & Brand__Brand__TV Features__Smart Features",
        "TV Reviews & Brand__Brand__TV Features__Streaming",
        "TV Reviews & Brand__Brand__TV Models__Crystal UHD",
        "TV Reviews & Brand__Brand__TV Models__Micro RGB",
        "TV Reviews & Brand__Brand__TV Models__MovingStyle",
        "TV Reviews & Brand__Brand__TV Models__Neo QLED",
        "TV Reviews & Brand__Brand__TV Models__Smart TV",
        "TV Reviews & Brand__Brand__TV Models__The Frame",
        "TV Reviews & Brand__Buying Guides",
        "TV Reviews & Brand__Comparison",
        "TV Reviews & Brand__Deals",
        "TV Reviews & Brand__Year Reviews__2025",
        "TV Reviews & Brand__Year Reviews__2026",
    ],
    "tv-sizes": [
        "TV Sizes__Large Size",
        "TV Sizes__Medium Size",
        "TV Sizes__Small Size",
        "TV Sizes__Super Size",
        "TV Sizes__Viewing Distance",
    ],
}


def parse_concept(concept: str) -> tuple[str, str, str]:
    """Parse concept into category, subcategory, and concept name."""
    parts = concept.split("__")
    if len(parts) == 3:
        return parts[2], parts[0], parts[1]
    elif len(parts) == 2:
        return parts[1], parts[0], None
    else:
        return concept, None, None


def fetch_concepts_for_tag(date: str, tag: str, model: str, brand: str) -> list[dict]:
    """Fetch all concept mentions for a specific date, tag, model, and brand."""
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
                        {"op": "or", "filters": [
                            {"col": "CBF_tags", "op": "eq", "val": tag}
                        ]},
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


def transform_row(row: dict, date: str, tag: str, model: str, brand: str) -> dict:
    """Transform API response row to database format."""
    raw_concept = row.get("concept", "")
    concept, category, subcategory = parse_concept(raw_concept)

    return {
        "date": date,
        "tag": tag,
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


def fetch_task(date: str, tag: str, model: str, brand: str) -> tuple[str, str, str, str, list[dict]]:
    """Fetch task for thread pool."""
    time.sleep(RATE_LIMIT)
    rows = fetch_concepts_for_tag(date, tag, model, brand)
    transformed = [transform_row(row, date, tag, model, brand) for row in rows]
    return (date, tag, model, brand, transformed)


def main():
    parser = argparse.ArgumentParser(description="Fetch concept mentions by tag from SEMrush")
    parser.add_argument("--group", choices=list(TAG_GROUPS.keys()), help="Tag group to fetch")
    parser.add_argument("--all", action="store_true", help="Fetch all tag groups")
    parser.add_argument("--date", default=TARGET_DATE, help=f"Date to fetch (default: {TARGET_DATE})")
    parser.add_argument("--workers", type=int, default=MAX_WORKERS, help=f"Concurrent workers (default: {MAX_WORKERS})")
    parser.add_argument("--resume", action="store_true", help="Resume from existing checkpoint")
    args = parser.parse_args()

    if not args.group and not args.all:
        parser.error("Please specify --group or --all")

    # Determine which tags to fetch
    if args.all:
        # Prioritized order: tv-features, tv-models, tv-reviews, tv-sizes
        tags = []
        for group in ["tv-features", "tv-models", "tv-reviews", "tv-sizes"]:
            tags.extend(TAG_GROUPS[group])
    else:
        tags = TAG_GROUPS[args.group]

    output_file = "data/concept_mentions_by_tag.json"
    os.makedirs("data", exist_ok=True)

    print(f"Fetching concept mentions by tag")
    print(f"Date: {args.date}")
    print(f"Tags: {len(tags)}")
    print(f"Models: {len(MODELS)}")
    print(f"Brands: {len(BRANDS)}")
    print(f"Total API calls: {len(tags) * len(MODELS) * len(BRANDS)}")
    print(f"Workers: {args.workers}")
    print()

    # Load existing data if resuming
    existing_data = []
    fetched_keys = set()
    if args.resume and os.path.exists(output_file):
        with open(output_file, "r") as f:
            existing_data = json.load(f)
        for row in existing_data:
            key = (row["date"], row["tag"], row["model"], row["brand"])
            fetched_keys.add(key)
        print(f"Resume mode: loaded {len(existing_data)} existing rows")
        print(f"Already fetched: {len(fetched_keys)} combinations")

    # Build list of tasks
    tasks = []
    for tag in tags:
        for model in MODELS:
            for brand in BRANDS:
                key = (args.date, tag, model, brand)
                if key not in fetched_keys:
                    tasks.append((args.date, tag, model, brand))

    total_tasks = len(tasks)
    print(f"Tasks to fetch: {total_tasks}")

    if total_tasks == 0:
        print("Nothing to fetch!")
        return

    all_rows = existing_data.copy()
    completed = 0
    errors = 0
    lock = threading.Lock()

    def update_progress(date, tag, model, brand, rows, error=None):
        nonlocal completed, errors
        with lock:
            completed += 1
            if error:
                errors += 1
                print(f"[{completed}/{total_tasks}] {tag} / {brand} / {model} - ERROR: {error}")
            else:
                print(f"[{completed}/{total_tasks}] {tag} / {brand} / {model} - {len(rows)} concepts")

    # Fetch concurrently
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {}
        for date, tag, model, brand in tasks:
            future = executor.submit(fetch_task, date, tag, model, brand)
            futures[future] = (date, tag, model, brand)

        for future in as_completed(futures):
            date, tag, model, brand = futures[future]
            try:
                _, _, _, _, rows = future.result()
                with lock:
                    all_rows.extend(rows)
                update_progress(date, tag, model, brand, rows)
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429:
                    update_progress(date, tag, model, brand, [], f"Rate limited: {e}")
                else:
                    update_progress(date, tag, model, brand, [], str(e))
            except Exception as e:
                update_progress(date, tag, model, brand, [], str(e))

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
    print(f"\nDone! Fetched {new_rows} new rows")
    print(f"Total rows: {len(all_rows)}")
    print(f"Errors: {errors}")
    print(f"Output file: {output_file}")


if __name__ == "__main__":
    main()
