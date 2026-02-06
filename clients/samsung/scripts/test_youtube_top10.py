"""Test SerpAPI YouTube extraction on top 10 cited URLs.
Fetches video details, comments, and transcripts.
"""
import json
import re
import os
import time
from serpapi import GoogleSearch
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
API_KEY = os.getenv('SERPAPI_KEY')

# Top 10 cited YouTube URLs from semrush_prompt_urls
TOP_URLS = [
    ("https://www.youtube.com/watch?v=dsdM06Sw64M", 173),
    ("https://www.youtube.com/watch?v=AUxgXzwCo3c", 117),
    ("https://www.youtube.com/watch?v=CX_g8po88cQ", 91),
    ("https://www.youtube.com/watch?v=8sY04k6tfaA", 78),
    ("https://www.youtube.com/watch?v=uAv8yA7T6Og", 71),
    ("https://www.youtube.com/shorts/X5iuP7bjvGs", 71),
    ("https://www.youtube.com/watch?v=3yGvlsGw-7U", 66),
    ("https://www.youtube.com/watch?v=IczxvejwpcI", 64),
    ("https://www.youtube.com/watch?v=jwvD_CqOpvY", 63),
    ("https://www.youtube.com/watch?v=whGEngzVRoc", 63),
]

MAX_COMMENT_PAGES = 3  # Limit pages of comments per video


def extract_video_id(url):
    """Extract video ID from YouTube URL, preserving timestamp if present."""
    shorts_match = re.search(r'youtube\.com/shorts/([a-zA-Z0-9_-]+)', url)
    if shorts_match:
        return shorts_match.group(1), url

    watch_match = re.search(r'[?&]v=([a-zA-Z0-9_-]+)', url)
    if watch_match:
        return watch_match.group(1), url

    short_match = re.search(r'youtu\.be/([a-zA-Z0-9_-]+)', url)
    if short_match:
        return short_match.group(1), url

    return None, url


def fetch_video_details(video_id):
    """Fetch video and channel details from SerpAPI."""
    params = {
        "api_key": API_KEY,
        "engine": "youtube_video",
        "v": video_id,
        "gl": "us"
    }
    search = GoogleSearch(params)
    return search.get_dict()


def fetch_comments(video_id, next_page_token, max_pages=MAX_COMMENT_PAGES):
    """Fetch comments using the comments_next_page_token, paginating up to max_pages."""
    all_comments = []
    token = next_page_token
    page = 0

    while token and page < max_pages:
        page += 1
        print(f"    Comments page {page}...", end=" ", flush=True)
        params = {
            "api_key": API_KEY,
            "engine": "youtube_video",
            "v": video_id,
            "next_page_token": token,
            "gl": "us"
        }
        search = GoogleSearch(params)
        data = search.get_dict()

        comments = data.get("comments", [])
        all_comments.extend(comments)
        print(f"{len(comments)} comments", flush=True)

        token = data.get("comments_next_page_token")
        if token:
            time.sleep(0.5)

    return all_comments


def fetch_transcript(video_id):
    """Fetch video transcript using the youtube_video_transcript engine."""
    params = {
        "api_key": API_KEY,
        "engine": "youtube_video_transcript",
        "v": video_id,
        "language_code": "en"
    }
    search = GoogleSearch(params)
    data = search.get_dict()
    return data.get("transcript", [])


def main():
    results = []

    for url, citations in TOP_URLS:
        video_id, original_url = extract_video_id(url)
        if not video_id:
            print(f"Could not extract video ID from: {url}")
            continue

        print(f"\n{'='*60}")
        print(f"Fetching: {video_id} ({citations} citations)")
        print(f"{'='*60}")

        try:
            # 1. Video details
            print("  [1/3] Video details...", end=" ", flush=True)
            data = fetch_video_details(video_id)

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

            video_info = {
                "original_url": original_url,
                "video_id": video_id,
                "citations": citations,
                "title": data.get("title"),
                "thumbnail": data.get("thumbnail") if isinstance(data.get("thumbnail"), str) else None,
                "channel": {
                    "name": channel.get("name"),
                    "link": channel.get("link"),
                    "thumbnail": channel.get("thumbnail"),
                    "subscribers": channel.get("subscribers"),
                    "extracted_subscribers": channel.get("extracted_subscribers"),
                },
                "views": data.get("extracted_views"),
                "likes": data.get("extracted_likes"),
                "published_date": data.get("published_date"),
                "description": desc_text,
                "description_links": desc_links,
                "chapters": data.get("chapters", []),
            }
            print(f"OK - {video_info['title']}")

            # 2. Comments
            comments_token = data.get("comments_next_page_token")
            if comments_token:
                print("  [2/3] Comments:")
                comments = fetch_comments(video_id, comments_token)
                video_info["comments"] = [{
                    "author": c.get("author"),
                    "content": c.get("content"),
                    "likes": c.get("likes"),
                    "published_date": c.get("published_date"),
                    "reply_count": c.get("reply_count"),
                } for c in comments]
                print(f"    Total: {len(video_info['comments'])} comments")
            else:
                print("  [2/3] Comments: no token available (shorts or disabled)")
                video_info["comments"] = []

            # 3. Transcript
            print("  [3/3] Transcript...", end=" ", flush=True)
            try:
                transcript = fetch_transcript(video_id)
                video_info["transcript"] = transcript
                # Build plain text version
                if transcript:
                    plain_text = " ".join(seg.get("snippet") or seg.get("text") or "" for seg in transcript)
                    video_info["transcript_text"] = plain_text
                    print(f"OK - {len(transcript)} segments, {len(plain_text)} chars")
                else:
                    video_info["transcript_text"] = ""
                    print("empty (no captions)")
            except Exception as e:
                print(f"SKIP - {e}")
                video_info["transcript"] = []
                video_info["transcript_text"] = ""

            results.append(video_info)

        except Exception as e:
            print(f"  ERROR - {e}")
            results.append({
                "original_url": original_url,
                "video_id": video_id,
                "citations": citations,
                "error": str(e)
            })

    # Save full results
    output_path = os.path.join(os.path.dirname(__file__), 'youtube_top10_results.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*60}")
    print(f"Results saved to {output_path}")
    print(f"\nSummary:")
    print(f"{'Citations':>9} | {'Comments':>8} | {'Transcript':>10} | {'Channel':<25} | Title")
    print("-" * 110)
    for r in results:
        if "error" not in r:
            n_comments = len(r.get('comments', []))
            t_len = len(r.get('transcript_text', ''))
            t_display = f"{t_len:,} ch" if t_len else "none"
            print(f"{r['citations']:>9} | {n_comments:>8} | {t_display:>10} | {(r['channel']['name'] or 'Unknown'):<25} | {(r['title'] or 'Unknown')[:35]}")


if __name__ == "__main__":
    main()
