"""Fetch prompts for each URL from SEMrush API.

For each URL in semrush_cited_pages, fetches the prompts that cite it.
Saves results to individual JSON files for checkpoint/resume support.
"""

import os
import sys
import json
import time
import hashlib
import argparse
import requests
from dotenv import load_dotenv

load_dotenv()

# SEMrush API config
SEMRUSH_API_KEY = os.getenv("SEMRUSH_API_KEY")
SEMRUSH_BASE_URL = "https://api.semrush.com/apis/v4-raw/external-api/v1"
WORKSPACE_ID = "a22caad0-2a96-4174-9e2f-59f1542f156b"
URL_PROMPTS_ELEMENT_ID = "777346b4-6777-40fe-9356-4a5d63a70ef8"

# Supabase config
SUPABASE_URL = "https://zozzhptqoclvbfysmopg.supabase.co"
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Data config
COUNTRY = "us"
DOMAIN = "samsung.com"
OUTPUT_DIR = "data/url_prompts"
RATE_LIMIT = 6.0  # seconds between requests (600 req/hour limit)


def get_urls_from_supabase(limit: int = None) -> list:
    """Fetch URLs from semrush_cited_pages table, ordered by prompts_count DESC."""
    url = f"{SUPABASE_URL}/rest/v1/semrush_cited_pages"

    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
    }

    params = {
        "select": "url,prompts_count",
        "order": "prompts_count.desc",
        "country": f"eq.{COUNTRY}"
    }

    if limit:
        params["limit"] = limit

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()


def url_to_filename(url: str) -> str:
    """Convert URL to safe filename using hash."""
    url_hash = hashlib.md5(url.encode()).hexdigest()[:12]
    return f"{url_hash}.json"


def fetch_prompts_for_url(url: str) -> dict:
    """Fetch all prompts that cite a specific URL."""
    api_url = f"{SEMRUSH_BASE_URL}/workspaces/{WORKSPACE_ID}/products/ai/elements/{URL_PROMPTS_ELEMENT_ID}"

    headers = {
        "accept": "application/json",
        "Authorization": f"Apikey {SEMRUSH_API_KEY}",
        "Content-Type": "application/json",
    }

    all_prompts = []
    offset = 0
    limit = 1000

    while True:
        payload = {
            "render_data": {
                "statistics": {
                    "rowCount": {"col": "*", "func": "count"}
                },
                "pagination": {
                    "limit": limit,
                    "offset": offset
                },
                "filters": {
                    "simple": {
                        "competitor_domains": [DOMAIN],
                        "url": url
                    },
                    "advanced": {
                        "op": "and",
                        "filters": [
                            {"op": "eq", "val": COUNTRY, "col": "CBF_country"},
                            {"op": "eq", "val": " ", "col": "CBF_model"},
                            {"op": "eq", "val": "MENTIONS_TARGET", "col": "CBF_category"}
                        ]
                    }
                }
            }
        }

        response = requests.post(api_url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()

        rows = data.get("blocks", {}).get("data", [])
        stats = data.get("blocks", {}).get("data_statistics", [{}])[0]
        total = stats.get("rowCount", 0)

        all_prompts.extend(rows)

        if len(all_prompts) >= total or not rows:
            break

        offset += limit
        time.sleep(RATE_LIMIT)

    return {
        "url": url,
        "total_prompts": len(all_prompts),
        "prompts": all_prompts,
        "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }


def main():
    parser = argparse.ArgumentParser(description="Fetch prompts for URLs from SEMrush")
    parser.add_argument("--limit", type=int, help="Limit number of URLs to process")
    parser.add_argument("--resume", action="store_true", help="Skip already fetched URLs")
    args = parser.parse_args()

    if not SEMRUSH_API_KEY:
        print("Error: SEMRUSH_API_KEY not set")
        sys.exit(1)

    if not SUPABASE_KEY:
        print("Error: SUPABASE_KEY not set")
        sys.exit(1)

    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Get URLs from Supabase
    print(f"Fetching URLs from Supabase (limit={args.limit})...")
    urls = get_urls_from_supabase(limit=args.limit)
    print(f"Found {len(urls)} URLs to process")

    # Get already processed files
    processed = set()
    if args.resume:
        processed = set(os.listdir(OUTPUT_DIR))
        print(f"Resume mode: {len(processed)} URLs already processed")

    # Process each URL
    total_prompts = 0
    for i, row in enumerate(urls):
        url = row["url"]
        expected_count = row["prompts_count"]
        filename = url_to_filename(url)

        # Skip if already processed
        if filename in processed:
            print(f"[{i+1}/{len(urls)}] Skipping (already done): {url[:60]}...")
            continue

        print(f"[{i+1}/{len(urls)}] Fetching: {url[:60]}... (expected: {expected_count})")

        try:
            result = fetch_prompts_for_url(url)
            total_prompts += result["total_prompts"]

            # Save to file
            filepath = os.path.join(OUTPUT_DIR, filename)
            with open(filepath, "w") as f:
                json.dump(result, f, indent=2)

            print(f"  -> Got {result['total_prompts']} prompts, saved to {filename}")

        except Exception as e:
            print(f"  -> Error: {e}")
            continue

        time.sleep(RATE_LIMIT)

    print(f"\nDone! Fetched {total_prompts} total prompts")
    print(f"Output files in: {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
