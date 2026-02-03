import requests
import json
import csv
from pathlib import Path

url = "https://api.dataforseo.com/v3/dataforseo_labs/google/keywords_for_site/live"

payload = [{
    "target": "www.changanuk.com",
    "location_code": 2826,  # UK
    "language_code": "en",
    "include_serp_info": True,
    "include_subdomains": True,
    "ignore_synonyms": False,
    "include_clickstream_data": False,
    "limit": 1000,
    "order_by": ["keyword_info.search_volume,desc"]
}]

headers = {
    'Authorization': 'Basic YWxjaGVteV9zb2Z0d2FyZUBhdG9tc2FuZHNwYWNlLmNvbToyZGY4ZmU4NTA4MzM2OTE3',
    'Content-Type': 'application/json'
}

response = requests.post(url, headers=headers, json=payload)
data = response.json()

# Save raw JSON response
output_dir = Path(__file__).parent / "data" / "keywords"
output_dir.mkdir(parents=True, exist_ok=True)

with open(output_dir / "keywords_raw.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)

print(f"Status: {data['status_code']} - {data['status_message']}")
print(f"Cost: ${data.get('cost', 'N/A')}")

# Parse and save to CSV
if data['status_code'] == 20000 and data['tasks']:
    task = data['tasks'][0]
    if task['result']:
        result = task['result'][0]
        items = result.get('items', [])

        print(f"Total available: {result.get('total_count', 'N/A')}")
        print(f"Downloaded: {len(items)}")

        # Prepare CSV data
        csv_rows = []
        for item in items:
            kw_info = item.get('keyword_info', {}) or {}
            kw_props = item.get('keyword_properties', {}) or {}
            serp_info = item.get('serp_info', {}) or {}
            intent_info = item.get('search_intent_info', {}) or {}

            row = {
                'keyword': item.get('keyword', ''),
                'search_volume': kw_info.get('search_volume', ''),
                'cpc': kw_info.get('cpc', ''),
                'competition': kw_info.get('competition', ''),
                'competition_level': kw_info.get('competition_level', ''),
                'keyword_difficulty': kw_props.get('keyword_difficulty', ''),
                'main_intent': intent_info.get('main_intent', ''),
                'foreign_intent': ','.join(intent_info.get('foreign_intent', []) or []),
                'low_top_of_page_bid': kw_info.get('low_top_of_page_bid', ''),
                'high_top_of_page_bid': kw_info.get('high_top_of_page_bid', ''),
                'serp_item_types': ','.join(serp_info.get('serp_item_types', []) or []),
                'se_results_count': serp_info.get('se_results_count', ''),
                'monthly_trend': kw_info.get('search_volume_trend', {}).get('monthly', '') if kw_info.get('search_volume_trend') else '',
                'quarterly_trend': kw_info.get('search_volume_trend', {}).get('quarterly', '') if kw_info.get('search_volume_trend') else '',
                'yearly_trend': kw_info.get('search_volume_trend', {}).get('yearly', '') if kw_info.get('search_volume_trend') else '',
            }
            csv_rows.append(row)

        # Write CSV
        csv_path = output_dir / "changanuk_keywords.csv"
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=csv_rows[0].keys())
            writer.writeheader()
            writer.writerows(csv_rows)

        print(f"\nSaved JSON: {output_dir / 'keywords_raw.json'}")
        print(f"Saved CSV: {csv_path}")
else:
    print(f"Error: {data}")
