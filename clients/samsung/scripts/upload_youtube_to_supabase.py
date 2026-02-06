"""Upload YouTube extraction results to Supabase."""
import json
import os
import re
from supabase import create_client
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

SUPABASE_URL = os.getenv('SUPABASE_URL', 'https://zozzhptqoclvbfysmopg.supabase.co')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def extract_handle(link):
    """Extract channel handle from YouTube channel link."""
    if not link:
        return None
    match = re.search(r'youtube\.com/@([a-zA-Z0-9_-]+)', link)
    return f"@{match.group(1)}" if match else None


def upsert_channel(channel_data):
    """Upsert a channel and return its UUID."""
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


def upsert_video(video, channel_id):
    """Upsert a video record."""
    # Build transcript text from segments if not already present
    transcript_text = video.get("transcript_text", "")
    transcript_segments = video.get("transcript", [])

    row = {
        "video_id": video["video_id"],
        "url": video["original_url"],
        "channel_id": channel_id,
        "title": video.get("title"),
        "thumbnail": video.get("thumbnail"),
        "views": video.get("views"),
        "likes": video.get("likes"),
        "published_date": video.get("published_date"),
        "description": video.get("description"),
        "description_links": video.get("description_links", []),
        "chapters": video.get("chapters", []),
        "transcript_text": transcript_text,
        "transcript_segments": transcript_segments,
        "citation_count": video.get("citations", 0),
        "raw_response": video.get("raw_response"),
    }

    supabase.table("youtube_videos").upsert(
        row, on_conflict="video_id"
    ).execute()


def insert_comments(video_id, comments):
    """Insert comments for a video (delete existing first to avoid duplicates)."""
    # Clear existing comments for this video
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

    # Batch insert in chunks of 100
    for i in range(0, len(rows), 100):
        supabase.table("youtube_comments").insert(rows[i:i+100]).execute()

    return len(rows)


def main():
    input_path = os.path.join(os.path.dirname(__file__), 'youtube_top10_results.json')
    with open(input_path, 'r', encoding='utf-8') as f:
        videos = json.load(f)

    print(f"Uploading {len(videos)} videos to Supabase...")

    for v in videos:
        if "error" in v:
            print(f"  SKIP {v['video_id']} - had extraction error")
            continue

        # 1. Upsert channel
        channel_id = upsert_channel(v.get("channel", {}))
        print(f"  Channel: {v['channel']['name']} -> {channel_id}")

        # 2. Upsert video
        upsert_video(v, channel_id)
        print(f"  Video: {v['video_id']} - {v['title']}")

        # 3. Insert comments
        n_comments = insert_comments(v["video_id"], v.get("comments", []))
        print(f"  Comments: {n_comments}")

    print("\nDone!")


if __name__ == "__main__":
    main()
