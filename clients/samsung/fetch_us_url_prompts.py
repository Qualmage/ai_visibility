"""Fetch prompts for all US URLs overnight.

Fetches prompts for all samsung.com/us/ URLs from SEMrush API.
Respects 600 req/hour rate limit. Resumes automatically on restart.

Usage:
    uv run clients/samsung/fetch_us_url_prompts.py
"""

import os
import json
import time
import hashlib
import requests
from dotenv import load_dotenv

load_dotenv()

SEMRUSH_API_KEY = os.getenv("SEMRUSH_API_KEY")
SUPABASE_URL = "https://zozzhptqoclvbfysmopg.supabase.co"
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
WORKSPACE_ID = "a22caad0-2a96-4174-9e2f-59f1542f156b"
ELEMENT_ID = "777346b4-6777-40fe-9356-4a5d63a70ef8"

OUTPUT_DIR = "data/url_prompts"
RATE_LIMIT = 6.0  # 600 req/hour = 1 every 6 seconds
BATCH_SIZE = 500  # Supabase insert batch size


def get_us_urls():
    """Fetch all US URLs from Supabase, ordered by prompts_count DESC."""
    all_urls = []
    offset = 0
    limit = 1000

    while True:
        resp = requests.get(
            f"{SUPABASE_URL}/rest/v1/semrush_cited_pages",
            headers={"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"},
            params={
                "select": "url,prompts_count",
                "url": "like.*samsung.com/us/*",
                "order": "prompts_count.desc",
                "limit": limit,
                "offset": offset
            }
        )
        rows = resp.json()
        if not rows:
            break
        all_urls.extend(rows)
        offset += limit

    return all_urls


def url_to_filename(url):
    return hashlib.md5(url.encode()).hexdigest()[:12] + ".json"


def fetch_prompts(url):
    """Fetch all prompts for a URL (handles pagination)."""
    api_url = f"https://api.semrush.com/apis/v4-raw/external-api/v1/workspaces/{WORKSPACE_ID}/products/ai/elements/{ELEMENT_ID}"
    headers = {
        "accept": "application/json",
        "Authorization": f"Apikey {SEMRUSH_API_KEY}",
        "Content-Type": "application/json",
    }

    all_prompts = []
    offset = 0

    while True:
        payload = {
            "render_data": {
                "statistics": {"rowCount": {"col": "*", "func": "count"}},
                "pagination": {"limit": 1000, "offset": offset},
                "filters": {
                    "simple": {"competitor_domains": ["samsung.com"], "url": url},
                    "advanced": {
                        "op": "and",
                        "filters": [
                            {"op": "eq", "val": "us", "col": "CBF_country"},
                            {"op": "eq", "val": " ", "col": "CBF_model"},
                            {"op": "eq", "val": "MENTIONS_TARGET", "col": "CBF_category"}
                        ]
                    }
                }
            }
        }

        resp = requests.post(api_url, headers=headers, json=payload)
        resp.raise_for_status()
        data = resp.json()

        rows = data.get("blocks", {}).get("data", [])
        stats = data.get("blocks", {}).get("data_statistics", [{}])[0]
        total = stats.get("rowCount", 0)

        all_prompts.extend(rows)

        if len(all_prompts) >= total or not rows:
            break

        offset += 1000
        time.sleep(RATE_LIMIT)

    return all_prompts


def upload_batch(records):
    """Upload a batch to Supabase."""
    resp = requests.post(
        f"{SUPABASE_URL}/rest/v1/semrush_url_prompts?on_conflict=url,prompt_hash,country",
        headers={
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal,resolution=merge-duplicates"
        },
        json=records
    )
    resp.raise_for_status()


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Get all US URLs
    print("Fetching US URLs from Supabase...")
    urls = get_us_urls()
    print(f"Total US URLs: {len(urls)}")

    # Check which are already fetched
    existing = set(os.listdir(OUTPUT_DIR))
    remaining = [(u["url"], u["prompts_count"]) for u in urls if url_to_filename(u["url"]) not in existing]
    print(f"Already fetched: {len(urls) - len(remaining)}")
    print(f"Remaining: {len(remaining)}")
    print(f"Estimated hours: {len(remaining) * RATE_LIMIT / 3600:.1f}")
    print()

    # Process URLs
    upload_buffer = []
    for i, (url, expected) in enumerate(remaining):
        filename = url_to_filename(url)
        filepath = os.path.join(OUTPUT_DIR, filename)

        try:
            prompts = fetch_prompts(url)

            # Save to file
            with open(filepath, "w") as f:
                json.dump({
                    "url": url,
                    "total_prompts": len(prompts),
                    "prompts": prompts,
                    "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
                }, f)

            # Add to upload buffer
            for p in prompts:
                upload_buffer.append({
                    "url": url,
                    "prompt": p["prompt"],
                    "prompt_hash": p["prompt_hash"],
                    "topic": p.get("topic"),
                    "llm": p.get("llm"),
                    "volume": p.get("volume"),
                    "mentioned_brands_count": p.get("mentioned_brands_count"),
                    "used_sources_count": p.get("used_sources_count"),
                    "serp_id": p.get("serp_id"),
                    "country": "us"
                })

            done = len(urls) - len(remaining) + i + 1
            print(f"[{done}/{len(urls)}] {len(prompts):>4} prompts | {url[30:75]}")

            # Upload when buffer is big enough
            if len(upload_buffer) >= BATCH_SIZE:
                # Dedupe buffer
                seen = {}
                for r in upload_buffer:
                    key = (r["url"], r["prompt_hash"], r["country"])
                    seen[key] = r
                deduped = list(seen.values())

                for j in range(0, len(deduped), BATCH_SIZE):
                    batch = deduped[j:j + BATCH_SIZE]
                    try:
                        upload_batch(batch)
                    except Exception as e:
                        print(f"  Upload error: {e}")
                upload_buffer = []

        except Exception as e:
            print(f"[{len(urls) - len(remaining) + i + 1}/{len(urls)}] ERROR: {url[:50]} - {e}")

        time.sleep(RATE_LIMIT)

    # Upload remaining buffer
    if upload_buffer:
        seen = {}
        for r in upload_buffer:
            key = (r["url"], r["prompt_hash"], r["country"])
            seen[key] = r
        deduped = list(seen.values())
        for j in range(0, len(deduped), BATCH_SIZE):
            batch = deduped[j:j + BATCH_SIZE]
            try:
                upload_batch(batch)
            except Exception as e:
                print(f"  Upload error: {e}")

    print(f"\nDone! Processed {len(urls)} URLs")


if __name__ == "__main__":
    main()
