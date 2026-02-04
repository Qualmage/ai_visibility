#!/usr/bin/env python3
"""Fetch full AI response text for tracked prompts from SEMrush API.

This endpoint provides the actual AI-generated response text for each prompt,
filtered by AI model (search-gpt, google-ai-mode, google-ai-overview).

Rate limit: 600 requests/hour
"""

import requests
import time
from datetime import datetime, timedelta
from supabase import create_client

# SEMrush API config
SEMRUSH_API_BASE = "https://api.semrush.com/apis/v4-raw/external-api/v1"
SEMRUSH_WORKSPACE_ID = "a22caad0-2a96-4174-9e2f-59f1542f156b"
SEMRUSH_PROJECT_ID = "b7880549-ea08-4d82-81d0-9633f4dcab58"
SEMRUSH_API_KEY = "fef05566690951688a288626dafffb74"
SEMRUSH_ELEMENT_ID = "f1d71cca-00af-454e-80a6-4af6c5d5117a"  # Prompt responses endpoint

# Supabase config
SUPABASE_URL = "https://zozzhptqoclvbfysmopg.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InpvenpocHRxb2NsdmJmeXNtb3BnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjkwNzA2NzksImV4cCI6MjA4NDY0NjY3OX0.3Q9gv49xrtqdmlesJgYDMVYUwjldy45xZw7O-nkASus"

# AI Models to fetch
MODELS = ["search-gpt", "google-ai-mode", "google-ai-overview"]

# Rate limiting
REQUEST_DELAY = 0.5  # seconds between requests


def get_prompts(supabase) -> list[str]:
    """Get list of unique prompts from semrush_prompt_urls table."""
    all_prompts = set()
    offset = 0
    page_size = 1000

    while True:
        result = (
            supabase.table("semrush_prompt_urls")
            .select("prompt")
            .range(offset, offset + page_size - 1)
            .execute()
        )

        if not result.data:
            break

        for row in result.data:
            all_prompts.add(row["prompt"])

        if len(result.data) < page_size:
            break

        offset += page_size

    return sorted(list(all_prompts))


def fetch_prompt_response(prompt: str, date_str: str, model: str) -> str | None:
    """Fetch AI response text for a specific prompt, date, and model."""
    url = f"{SEMRUSH_API_BASE}/workspaces/{SEMRUSH_WORKSPACE_ID}/products/ai/elements/{SEMRUSH_ELEMENT_ID}"

    payload = {
        "render_data": {
            "project_id": SEMRUSH_PROJECT_ID,
            "filters": {
                "simple": {
                    "keyword": prompt,
                    "end_date": date_str
                },
                "advanced": {
                    "op": "and",
                    "filters": [
                        {"op": "eq", "val": model, "col": "CBF_model"}
                    ]
                }
            }
        }
    }

    headers = {
        "accept": "application/json",
        "Authorization": f"Apikey {SEMRUSH_API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()

    data = response.json()
    values = data.get("blocks", {}).get("value", [])

    if values and len(values) > 0:
        return values[0].get("text", "")
    return None


def check_existing(supabase, date_str: str, prompt: str, model: str) -> bool:
    """Check if data already exists for this date/prompt/model combo."""
    result = (
        supabase.table("semrush_prompt_responses")
        .select("id")
        .eq("date", date_str)
        .eq("prompt", prompt)
        .eq("model", model)
        .limit(1)
        .execute()
    )
    return len(result.data) > 0


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Fetch prompt responses from SEMrush")
    parser.add_argument("--start-date", type=str, default="2026-01-15",
                        help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end-date", type=str, default=None,
                        help="End date (YYYY-MM-DD), defaults to today")
    parser.add_argument("--single-date", type=str, default=None,
                        help="Fetch only a single date (for testing)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be fetched without making API calls")
    parser.add_argument("--skip-existing", action="store_true", default=True,
                        help="Skip prompts that already have data (default: True)")
    parser.add_argument("--model", type=str, default=None,
                        choices=MODELS,
                        help="Fetch only a specific model (default: all)")
    args = parser.parse_args()

    # Parse dates
    if args.single_date:
        start_date = datetime.strptime(args.single_date, "%Y-%m-%d")
        end_date = start_date
    else:
        start_date = datetime.strptime(args.start_date, "%Y-%m-%d")
        end_date = datetime.strptime(args.end_date, "%Y-%m-%d") if args.end_date else datetime.now()

    # Models to fetch
    models_to_fetch = [args.model] if args.model else MODELS

    print(f"Date range: {start_date.date()} to {end_date.date()}")
    print(f"Models: {', '.join(models_to_fetch)}")

    # Connect to Supabase
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

    # Get all prompts
    prompts = get_prompts(supabase)
    print(f"Found {len(prompts)} unique prompts to fetch")

    # Calculate total API calls
    num_days = (end_date - start_date).days + 1
    total_calls = len(prompts) * num_days * len(models_to_fetch)
    estimated_hours = (total_calls * REQUEST_DELAY) / 3600

    print(f"Days: {num_days}")
    print(f"Total API calls: {total_calls}")
    print(f"Estimated time: {estimated_hours:.1f} hours (at {REQUEST_DELAY}s/request)")

    if args.dry_run:
        print("\nDry run - no API calls made")
        return

    # Iterate through dates
    current_date = start_date
    total_inserted = 0
    total_skipped = 0
    total_empty = 0
    request_count = 0

    while current_date <= end_date:
        date_str = current_date.strftime("%Y-%m-%d")
        print(f"\n=== {date_str} ===")

        for model in models_to_fetch:
            print(f"  Model: {model}")
            model_inserted = 0

            for i, prompt in enumerate(prompts):
                # Check if already exists
                if args.skip_existing and check_existing(supabase, date_str, prompt, model):
                    total_skipped += 1
                    continue

                try:
                    # Rate limiting
                    if request_count > 0:
                        time.sleep(REQUEST_DELAY)

                    # Fetch response
                    response_text = fetch_prompt_response(prompt, date_str, model)
                    request_count += 1

                    if response_text:
                        # Insert record
                        supabase.table("semrush_prompt_responses").insert({
                            "date": date_str,
                            "prompt": prompt,
                            "model": model,
                            "response_text": response_text
                        }).execute()
                        total_inserted += 1
                        model_inserted += 1
                    else:
                        total_empty += 1

                    # Progress update every 50 requests
                    if request_count % 50 == 0:
                        print(f"    [{request_count}/{total_calls}] {model_inserted} inserted, "
                              f"{total_empty} empty - Last: {prompt[:40]}...")

                except Exception as e:
                    print(f"    ERROR for '{prompt[:40]}...': {e}")
                    continue

            print(f"    {model}: {model_inserted} responses inserted")

        current_date += timedelta(days=1)

    print(f"\n=== Complete ===")
    print(f"Total inserted: {total_inserted} records")
    print(f"Total skipped (existing): {total_skipped}")
    print(f"Total empty responses: {total_empty}")
    print(f"Total API calls: {request_count}")


if __name__ == "__main__":
    main()
