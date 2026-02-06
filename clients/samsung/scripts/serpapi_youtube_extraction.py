"""
Full YouTube extraction pipeline via SerpAPI.
Fetches video details, comments, and transcripts for all cited YouTube URLs
and uploads to Supabase incrementally with resume support.

Usage:
    uv run python clients/samsung/scripts/serpapi_youtube_extraction.py
    uv run python clients/samsung/scripts/serpapi_youtube_extraction.py --limit 100
    uv run python clients/samsung/scripts/serpapi_youtube_extraction.py --dry-run
"""
import argparse
import json
import os
import re
import sys
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

from dotenv import load_dotenv
from serpapi import GoogleSearch
from supabase import create_client

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

API_KEY = os.getenv('SERPAPI_KEY')
SUPABASE_URL = os.getenv('SUPABASE_URL', 'https://zozzhptqoclvbfysmopg.supabase.co')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

MAX_COMMENT_PAGES = 3
DELAY_BETWEEN_VIDEOS = 0.5  # seconds between videos


def extract_video_id(url):
    """Extract video ID from YouTube URL, preserving the original URL."""
    shorts_match = re.search(r'youtube\.com/shorts/([a-zA-Z0-9_-]+)', url)
    if shorts_match:
        return shorts_match.group(1)

    watch_match = re.search(r'[?&]v=([a-zA-Z0-9_-]+)', url)
    if watch_match:
        return watch_match.group(1)

    short_match = re.search(r'youtu\.be/([a-zA-Z0-9_-]+)', url)
    if short_match:
        return short_match.group(1)

    return None


def extract_handle(link):
    """Extract channel handle from YouTube channel link."""
    if not link:
        return None
    match = re.search(r'youtube\.com/@([a-zA-Z0-9_-]+)', link)
    return f"@{match.group(1)}" if match else None


def serpapi_call(params, retries=2):
    """Make a SerpAPI call with retry on disconnect."""
    for attempt in range(retries + 1):
        try:
            search = GoogleSearch(params)
            return search.get_dict()
        except Exception as e:
            if attempt < retries and "disconnected" in str(e).lower():
                time.sleep(2 ** attempt)
                continue
            raise


def fetch_video_details(video_id):
    """Fetch video details from SerpAPI."""
    params = {
        "api_key": API_KEY,
        "engine": "youtube_video",
        "v": video_id,
        "gl": "us"
    }
    return serpapi_call(params)


def fetch_comments(video_id, next_page_token, max_pages=MAX_COMMENT_PAGES):
    """Fetch comments pages using next_page_token."""
    all_comments = []
    token = next_page_token
    page = 0

    while token and page < max_pages:
        page += 1
        params = {
            "api_key": API_KEY,
            "engine": "youtube_video",
            "v": video_id,
            "next_page_token": token,
            "gl": "us"
        }
        data = serpapi_call(params)

        comments = data.get("comments", [])
        all_comments.extend(comments)

        token = data.get("comments_next_page_token")
        if token:
            time.sleep(0.3)

    return all_comments


def fetch_transcript(video_id):
    """Fetch transcript using youtube_video_transcript engine."""
    params = {
        "api_key": API_KEY,
        "engine": "youtube_video_transcript",
        "v": video_id,
        "language_code": "en"
    }
    data = serpapi_call(params)
    return data.get("transcript", [])


def get_youtube_urls_from_supabase(tag=None):
    """Get all unique YouTube URLs with citation counts, deduped by video ID."""
    all_rows = []
    offset = 0
    page_size = 1000
    rpc_name = 'get_youtube_cited_urls_by_tag' if tag else 'get_youtube_cited_urls'
    rpc_params = {'p_tag': tag} if tag else {}
    while True:
        result = (
            supabase.rpc(rpc_name, rpc_params)
            .range(offset, offset + page_size - 1)
            .execute()
        )
        if not result.data:
            break
        all_rows.extend(result.data)
        if len(result.data) < page_size:
            break
        offset += page_size
    return all_rows


def get_already_fetched():
    """Get set of video_ids already in youtube_videos."""
    all_ids = set()
    offset = 0
    page_size = 1000
    while True:
        result = (
            supabase.table("youtube_videos")
            .select("video_id")
            .range(offset, offset + page_size - 1)
            .execute()
        )
        if not result.data:
            break
        all_ids.update(row["video_id"] for row in result.data)
        if len(result.data) < page_size:
            break
        offset += page_size
    return all_ids


def upsert_channel(channel_data):
    """Upsert channel, return UUID."""
    handle = extract_handle(channel_data.get("link"))
    if not handle:
        return None

    row = {
        "channel_handle": handle,
        "name": channel_data.get("name"),
        "link": channel_data.get("link"),
        "thumbnail": channel_data.get("thumbnail"),
        "subscribers": channel_data.get("subscribers"),
        "extracted_subscribers": channel_data.get("extracted_subscribers"),
        "verified": channel_data.get("verified", False),
        "raw_response": channel_data,
    }

    result = supabase.table("youtube_channels").upsert(
        row, on_conflict="channel_handle"
    ).execute()

    return result.data[0]["id"] if result.data else None


def upsert_video(video_id, url, channel_id, data, comments_list, transcript, transcript_text, citation_count):
    """Upsert video with all data including raw response."""
    channel = data.get("channel") or {}
    if not isinstance(channel, dict):
        channel = {"name": channel}
    desc = data.get("description") or {}
    if isinstance(desc, dict):
        desc_text = desc.get("content", "")
        desc_links = desc.get("links", [])
    else:
        desc_text = str(desc)
        desc_links = []

    row = {
        "video_id": video_id,
        "url": url,
        "channel_id": channel_id,
        "title": data.get("title"),
        "thumbnail": data.get("thumbnail") if isinstance(data.get("thumbnail"), str) else None,
        "views": data.get("extracted_views"),
        "likes": data.get("extracted_likes"),
        "published_date": data.get("published_date"),
        "description": desc_text,
        "description_links": desc_links,
        "chapters": data.get("chapters", []),
        "transcript_text": transcript_text,
        "transcript_segments": transcript,
        "citation_count": citation_count,
        "comments_token": data.get("comments_next_page_token"),
        "raw_response": data,
    }

    supabase.table("youtube_videos").upsert(row, on_conflict="video_id").execute()


def insert_comments(video_id, comments):
    """Insert comments for a video."""
    supabase.table("youtube_comments").delete().eq("video_id", video_id).execute()

    if not comments:
        return 0

    rows = [{
        "video_id": video_id,
        "author": (c.get("channel") or {}).get("name") or c.get("author"),
        "content": c.get("content"),
        "likes": c.get("extracted_vote_count") or c.get("likes"),
        "published_date": c.get("published_date"),
        "reply_count": c.get("reply_count"),
        "raw_response": c,
    } for c in comments]

    for i in range(0, len(rows), 100):
        supabase.table("youtube_comments").insert(rows[i:i + 100]).execute()

    return len(rows)


def process_video(video_id, url, citation_count, skip_comments=False):
    """Process a single video: fetch details, optionally comments, transcript, upload."""
    api_calls = 0

    # 1. Video details
    data = fetch_video_details(video_id)
    api_calls += 1

    # 2. Channel
    channel = data.get("channel") or {}
    if not isinstance(channel, dict):
        channel = {"name": channel}
    channel_id = upsert_channel(channel)

    # 3. Comments (skip if --skip-comments, token saved in upsert_video for later)
    comments = []
    if not skip_comments:
        comments_token = data.get("comments_next_page_token")
        if comments_token:
            comments = fetch_comments(video_id, comments_token)
            api_calls += min(MAX_COMMENT_PAGES, max(1, len(comments) // 20 + (1 if len(comments) % 20 else 0)))

    # 4. Transcript
    transcript = []
    transcript_text = ""
    try:
        transcript = fetch_transcript(video_id)
        api_calls += 1
        if transcript:
            transcript_text = " ".join(
                seg.get("snippet") or seg.get("text") or "" for seg in transcript
            )
    except Exception:
        pass  # Some videos have no transcript

    # 5. Upload
    upsert_video(video_id, url, channel_id, data, comments, transcript, transcript_text, citation_count)
    if not skip_comments:
        insert_comments(video_id, comments)

    return {
        "title": data.get("title"),
        "channel": channel.get("name"),
        "comments": len(comments),
        "transcript_chars": len(transcript_text),
        "api_calls": api_calls,
    }


def process_comments_only(video_id):
    """Fetch and store comments for a video that has a saved comments_token."""
    result = (
        supabase.table("youtube_videos")
        .select("comments_token")
        .eq("video_id", video_id)
        .single()
        .execute()
    )
    token = result.data.get("comments_token") if result.data else None
    if not token:
        return 0

    comments = fetch_comments(video_id, token)
    insert_comments(video_id, comments)
    return len(comments)


def main():
    parser = argparse.ArgumentParser(description="Extract YouTube video data via SerpAPI")
    parser.add_argument("--limit", type=int, default=0, help="Limit number of videos to process (0=all)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be processed without fetching")
    parser.add_argument("--offset", type=int, default=0, help="Skip first N videos")
    parser.add_argument("--tag", type=str, default=None, help="Filter by prompt tag (e.g. 'Mini-LED')")
    parser.add_argument("--workers", type=int, default=5, help="Number of concurrent workers (default 5)")
    args = parser.parse_args()

    tag_label = f" [tag: {args.tag}]" if args.tag else ""
    print(f"[{datetime.now():%H:%M:%S}] Fetching YouTube URLs from Supabase...{tag_label}")
    urls = get_youtube_urls_from_supabase(tag=args.tag)
    print(f"  Found {len(urls)} unique YouTube URLs")

    already_fetched = get_already_fetched()
    print(f"  Already fetched: {len(already_fetched)}")

    # Filter to unfetched, apply offset/limit
    to_process = [u for u in urls if u["video_id"] not in already_fetched]
    to_process = to_process[args.offset:]
    if args.limit:
        to_process = to_process[:args.limit]

    print(f"  To process: {len(to_process)}")
    estimated_calls = len(to_process) * 4  # ~4 API calls per video
    print(f"  Estimated API calls: ~{estimated_calls}")

    if args.dry_run:
        print("\n[DRY RUN] Would process:")
        for i, u in enumerate(to_process[:20]):
            print(f"  {i+1}. {u['source']} ({u['citations']} citations)")
        if len(to_process) > 20:
            print(f"  ... and {len(to_process) - 20} more")
        return

    total_api_calls = 0
    errors = 0
    completed = 0
    lock = threading.Lock()
    start_time = time.time()

    def worker(i, u):
        nonlocal total_api_calls, errors, completed
        url = u["source"]
        citations = u["citations"]
        video_id = u["video_id"]

        try:
            result = process_video(video_id, url, citations)

            with lock:
                total_api_calls += result["api_calls"]
                completed += 1
                elapsed = time.time() - start_time
                rate = completed / elapsed * 3600 if elapsed > 0 else 0
                remaining = (len(to_process) - completed) / (rate / 3600) if rate > 0 else 0
                print(
                    f"  [{completed}/{len(to_process)}] {video_id} ({citations} cit) "
                    f"[{rate:.0f}/hr, ~{remaining/60:.0f}m left] "
                    f"OK - {(result['title'] or '')[:40]} | "
                    f"{result['channel']} | "
                    f"{result['comments']}c {result['transcript_chars']}t"
                )

        except Exception as e:
            with lock:
                errors += 1
                completed += 1
                print(f"  [{completed}/{len(to_process)}] {video_id} ERROR - {e}")

    workers = args.workers
    print(f"  Workers: {workers}")
    print(f"  SerpAPI budget: ~{workers * 4} calls/batch\n")

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(worker, i, u): u for i, u in enumerate(to_process)}
        for future in as_completed(futures):
            future.result()  # Raise any unhandled exceptions
            if errors > 50:
                print(f"\nToo many errors ({errors}), cancelling remaining...")
                executor.shutdown(wait=False, cancel_futures=True)
                break

    elapsed = time.time() - start_time
    print(f"\n{'='*60}")
    print(f"Done in {elapsed/60:.1f} minutes")
    print(f"Processed: {completed}/{len(to_process)}")
    print(f"API calls: {total_api_calls}")
    print(f"Errors: {errors}")


if __name__ == "__main__":
    main()
