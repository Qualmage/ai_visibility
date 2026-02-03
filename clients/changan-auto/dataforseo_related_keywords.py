"""
DataForSEO Related Keywords API Script for Changan UK

Fetches related keywords for brand and category seed terms,
combining and deduplicating results into a single CSV.
"""

import requests
import json
import csv
from pathlib import Path

# API Configuration
API_URL = "https://api.dataforseo.com/v3/dataforseo_labs/google/related_keywords/live"
HEADERS = {
    'Authorization': 'Basic YWxjaGVteV9zb2Z0d2FyZUBhdG9tc2FuZHNwYWNlLmNvbToyZGY4ZmU4NTA4MzM2OTE3',
    'Content-Type': 'application/json'
}

# Seed keywords
SEED_KEYWORDS = [
    # Brand terms
    "changan",
    "changan uk",
    "changan cars",
    # Category terms
    "chinese electric car uk",
    "chinese ev",
    "affordable ev uk",
]

# Output directory
OUTPUT_DIR = Path(__file__).parent / "data" / "keywords"


def fetch_related_keywords(seed_keyword: str) -> dict:
    """Fetch related keywords for a single seed keyword."""
    payload = [{
        "keyword": seed_keyword,
        "location_code": 2826,  # UK
        "language_code": "en",
        "depth": 4,  # Deeper exploration
        "include_serp_info": True,
        "include_clickstream_data": True,
        "limit": 500,
    }]

    response = requests.post(API_URL, headers=HEADERS, json=payload)
    return response.json()


def parse_keyword_item(item: dict, seed_keyword: str) -> dict:
    """Parse a single keyword item into a flat dictionary.

    Structure: item has 'keyword_data' (dict with keyword info) and
    'related_keywords' (list of strings, just keyword names).
    """
    kw_data = item.get('keyword_data', {}) or {}
    kw_info = kw_data.get('keyword_info', {}) or {}
    kw_props = kw_data.get('keyword_properties', {}) or {}
    serp_info = kw_data.get('serp_info', {}) or {}
    intent_info = kw_data.get('search_intent_info', {}) or {}

    return {
        'keyword': kw_data.get('keyword', ''),
        'seed_keyword': seed_keyword,
        'depth': item.get('depth', ''),
        'search_volume': kw_info.get('search_volume', ''),
        'cpc': kw_info.get('cpc', ''),
        'competition': kw_info.get('competition', ''),
        'competition_level': kw_info.get('competition_level', ''),
        'keyword_difficulty': kw_props.get('keyword_difficulty', ''),
        'main_intent': intent_info.get('main_intent', ''),
        'serp_item_types': ','.join(serp_info.get('serp_item_types', []) or []),
    }


def extract_items(items: list, seed_keyword: str) -> list:
    """Extract keyword items from the API response.

    Each item has keyword_data (full metrics) and related_keywords (list of strings).
    We only use keyword_data since related_keywords are just keyword names without metrics.
    """
    results = []
    for item in items:
        parsed = parse_keyword_item(item, seed_keyword)
        if parsed['keyword']:
            results.append(parsed)
    return results


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    all_keywords = []
    total_cost = 0

    print("DataForSEO Related Keywords - Changan UK")
    print("=" * 50)
    print(f"Seed keywords: {len(SEED_KEYWORDS)}")
    print()

    for seed in SEED_KEYWORDS:
        print(f"Fetching: '{seed}'...", end=" ")

        data = fetch_related_keywords(seed)

        # Save raw JSON
        safe_filename = seed.replace(" ", "_").replace("/", "_")
        json_path = OUTPUT_DIR / f"related_kw_{safe_filename}.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        # Track cost
        cost = data.get('cost', 0) or 0
        total_cost += cost

        status_code = data.get('status_code', 0)
        print(f"Status: {status_code}", end=" ")

        if status_code == 20000 and data.get('tasks'):
            task = data['tasks'][0]
            if task.get('result'):
                result = task['result'][0]
                items = result.get('items', [])

                # Extract keywords from items
                seed_keywords = extract_items(items, seed)

                print(f"- Found {len(seed_keywords)} keywords")
                all_keywords.extend(seed_keywords)
            else:
                print("- No results")
        else:
            print(f"- Error: {data.get('status_message', 'Unknown')}")

    print()
    print(f"Total keywords before dedup: {len(all_keywords)}")

    # Deduplicate by keyword, keeping first occurrence (preserves seed attribution)
    seen = set()
    unique_keywords = []
    for kw in all_keywords:
        keyword_lower = kw['keyword'].lower()
        if keyword_lower not in seen:
            seen.add(keyword_lower)
            unique_keywords.append(kw)

    print(f"Unique keywords after dedup: {len(unique_keywords)}")

    # Sort by search volume (descending)
    unique_keywords.sort(
        key=lambda x: (x.get('search_volume') or 0),
        reverse=True
    )

    # Write combined CSV
    if unique_keywords:
        csv_path = OUTPUT_DIR / "changan_related_keywords.csv"
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=unique_keywords[0].keys())
            writer.writeheader()
            writer.writerows(unique_keywords)

        print()
        print(f"Saved: {csv_path}")

    print()
    print(f"Total API cost: ${total_cost:.4f}")

    # Show sample of top keywords
    print()
    print("Top 10 keywords by search volume:")
    print("-" * 50)
    for kw in unique_keywords[:10]:
        vol = kw.get('search_volume', 'N/A')
        print(f"  {kw['keyword']}: {vol} (from '{kw['seed_keyword']}')")


if __name__ == "__main__":
    main()
