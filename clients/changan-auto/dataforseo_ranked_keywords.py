"""
DataForSEO Ranked Keywords API Script for Changan UK

Fetches keywords that changanuk.com currently ranks for in Google UK,
including position, URL, and traffic estimates.
"""

import requests
import json
import csv
from pathlib import Path

# API Configuration
API_URL = "https://api.dataforseo.com/v3/dataforseo_labs/google/ranked_keywords/live"
HEADERS = {
    'Authorization': 'Basic YWxjaGVteV9zb2Z0d2FyZUBhdG9tc2FuZHNwYWNlLmNvbToyZGY4ZmU4NTA4MzM2OTE3',
    'Content-Type': 'application/json'
}

# Target domain
TARGET_DOMAIN = "changanuk.com"

# Output directory
OUTPUT_DIR = Path(__file__).parent / "data" / "keywords"


def fetch_ranked_keywords() -> dict:
    """Fetch ranked keywords for the target domain."""
    payload = [{
        "target": TARGET_DOMAIN,
        "location_code": 2826,  # UK
        "language_code": "en",
        "include_serp_info": True,
        "include_clickstream_data": True,
        "ignore_synonyms": False,
        "limit": 1000,
        "order_by": ["keyword_data.keyword_info.search_volume,desc"]
    }]

    response = requests.post(API_URL, headers=HEADERS, json=payload)
    return response.json()


def parse_ranked_item(item: dict) -> dict:
    """Parse a single ranked keyword item into a flat dictionary."""
    kw_data = item.get('keyword_data', {}) or {}
    kw_info = kw_data.get('keyword_info', {}) or {}
    kw_props = kw_data.get('keyword_properties', {}) or {}
    serp_info = kw_data.get('serp_info', {}) or {}
    intent_info = kw_data.get('search_intent_info', {}) or {}
    ranked_serp = item.get('ranked_serp_element', {}) or {}

    return {
        'keyword': kw_data.get('keyword', ''),
        'position': ranked_serp.get('serp_item', {}).get('rank_group', ''),
        'position_absolute': ranked_serp.get('serp_item', {}).get('rank_absolute', ''),
        'url': ranked_serp.get('serp_item', {}).get('url', ''),
        'serp_type': ranked_serp.get('serp_item', {}).get('type', ''),
        'is_featured': ranked_serp.get('serp_item', {}).get('is_featured_snippet', False),
        'search_volume': kw_info.get('search_volume', ''),
        'cpc': kw_info.get('cpc', ''),
        'competition': kw_info.get('competition', ''),
        'competition_level': kw_info.get('competition_level', ''),
        'keyword_difficulty': kw_props.get('keyword_difficulty', ''),
        'main_intent': intent_info.get('main_intent', ''),
        'etv': ranked_serp.get('etv', ''),  # Estimated traffic volume
        'estimated_paid_traffic_cost': ranked_serp.get('estimated_paid_traffic_cost', ''),
        'serp_item_types': ','.join(serp_info.get('serp_item_types', []) or []),
    }


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("DataForSEO Ranked Keywords - Changan UK")
    print("=" * 50)
    print(f"Target: {TARGET_DOMAIN}")
    print()

    print("Fetching ranked keywords...", end=" ")
    data = fetch_ranked_keywords()

    # Save raw JSON
    json_path = OUTPUT_DIR / "ranked_keywords_raw.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    status_code = data.get('status_code', 0)
    cost = data.get('cost', 0) or 0
    print(f"Status: {status_code}")
    print(f"API cost: ${cost:.4f}")
    print()

    if status_code == 20000 and data.get('tasks'):
        task = data['tasks'][0]
        if task.get('result'):
            result = task['result'][0]
            items = result.get('items', [])
            total_count = result.get('total_count', 0)
            metrics = result.get('metrics', {}) or {}

            print(f"Total keywords ranking: {total_count}")
            print(f"Downloaded: {len(items)}")
            print()

            # Show metrics summary
            if metrics:
                organic = metrics.get('organic', {}) or {}
                print("Position distribution:")
                print(f"  Pos 1-3:   {organic.get('pos_1', 0) + organic.get('pos_2_3', 0)}")
                print(f"  Pos 4-10:  {organic.get('pos_4_10', 0)}")
                print(f"  Pos 11-20: {organic.get('pos_11_20', 0)}")
                print(f"  Pos 21-30: {organic.get('pos_21_30', 0)}")
                print(f"  Pos 31+:   {organic.get('pos_31_40', 0) + organic.get('pos_41_50', 0) + organic.get('pos_51_60', 0) + organic.get('pos_61_70', 0) + organic.get('pos_71_80', 0) + organic.get('pos_81_90', 0) + organic.get('pos_91_100', 0)}")
                print(f"  Total ETV: {organic.get('etv', 0):.0f}")
                print()

            # Parse items
            rows = [parse_ranked_item(item) for item in items]

            # Write CSV
            if rows:
                csv_path = OUTPUT_DIR / "changanuk_ranked_keywords.csv"
                with open(csv_path, "w", newline="", encoding="utf-8") as f:
                    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
                    writer.writeheader()
                    writer.writerows(rows)

                print(f"Saved JSON: {json_path}")
                print(f"Saved CSV: {csv_path}")
                print()

                # Show top keywords by position
                top_positions = sorted(rows, key=lambda x: x.get('position') or 999)[:15]
                print("Top 15 keywords by position:")
                print("-" * 70)
                print(f"{'Pos':<5} {'Keyword':<35} {'Volume':<10} {'URL'}")
                print("-" * 70)
                for kw in top_positions:
                    keyword = kw['keyword'][:33] + '..' if len(kw['keyword']) > 35 else kw['keyword']
                    url_short = kw['url'].replace('https://www.changanuk.com', '')[:30] if kw['url'] else ''
                    print(f"{kw['position']:<5} {keyword:<35} {kw['search_volume'] or 'N/A':<10} {url_short}")
        else:
            print("No results returned")
    else:
        print(f"Error: {data.get('status_message', 'Unknown')}")


if __name__ == "__main__":
    main()
