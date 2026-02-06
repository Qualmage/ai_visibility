# Build Log

A detailed journal of the General Analytics development process. Each session documents what was done, problems encountered, and how they were solved.

**Purpose:** Capture the full context of development decisions so future-you (or anyone else) can understand not just WHAT was done, but HOW and WHY.

**Format:** Each entry has:
- Technical details for developers
- "Plain English" explanations for non-developers

---

## 2026-02-06 (Session 21): YouTube Data Quality Audit, Backfill & Handoff Documentation

### Session Goals
Audit the full YouTube data pipeline for data quality gaps, backfill missing comment fields from raw API responses, fix field mapping bugs in the extraction scripts, and create handoff documentation so a colleague can pick up remaining work.

---

### Part 1: Data Quality Audit

#### What Was Audited

After scaling the YouTube extraction from the initial 164 Mini-LED videos (Session 19) to 700 videos across all tags, a full audit was performed against all three YouTube Supabase tables.

| Table | Total Rows | Context |
|-------|-----------|---------|
| `youtube_videos` | 700 | Top 700 videos by citation count (out of 2,300 total cited YouTube URLs) |
| `youtube_channels` | 293 | All unique channels from those 700 videos; all have subscriber counts |
| `youtube_comments` | 19,460 | Comments across 592 of the 700 videos (108 videos had comments disabled or no comments) |

#### Field-Level Coverage

| Field | Coverage | Gap Reason |
|-------|----------|------------|
| Video title/views | 688/700 (98%) | 12 videos are deleted or set to private on YouTube |
| Channel linkage | 680/700 (97%) | 20 videos have no @handle in their YouTube URL, so `channel_id` could not be resolved |
| Transcripts | 627/700 (90%) | 73 videos have captions disabled by the uploader |
| Comment author | 14,991/19,460 (77%) | Backfilled from `raw_response`; 4,469 comments from the old batch (first 164 videos) have no raw data |
| Comment likes | 8,622/19,460 (44%) | SerpAPI omits the `likes` field entirely when a comment has 0 votes |
| Comment sentiment | 0/19,460 | Not yet implemented -- columns (`sentiment`, `sentiment_score`) exist in schema but are empty |
| Raw API responses | 690 videos, 250 channels, 14,991 comments | The original 164-video batch was extracted before the `raw_response` column was added |

#### Plain English
Think of the data quality audit like checking a filing cabinet after a big data collection project. We opened every drawer and counted what was complete versus what had missing pages. Most drawers (98% of videos, 97% of channels) were fully filled out. The biggest gaps were in the comments drawer: about 23% of comments were missing the author's name, and 56% were missing the "likes" count. The reason for the likes gap turned out to be that our data supplier (SerpAPI) simply does not include the likes field when a comment has zero likes -- they leave it out entirely rather than saying "0". The author gap was caused by a field naming mismatch that we fixed (see Part 2).

---

### Part 2: SerpAPI Comment Field Mapping Fix

#### What Happened
Comments extracted in the initial 164-video batch had empty `author` and `likes` fields. When the extraction script was first written, it looked for fields called `author` and `likes` in SerpAPI's response, but SerpAPI actually uses different field names.

#### Technical Cause
SerpAPI's YouTube video response nests comment data with non-obvious field names:
- The comment author's name is at `comment.channel.name` (not `comment.author`)
- The comment like count is at `comment.extracted_vote_count` (not `comment.likes`)

The extraction script was mapping the wrong keys, resulting in `NULL` values being stored in Supabase.

#### Plain English Cause
Imagine ordering a filing cabinet from a supplier, and the label on the "Author" drawer actually says "Channel Name" on their end. We were looking in the right cabinet but reading the wrong label. Once we learned what SerpAPI actually calls these fields, we updated our script to look in the right place.

#### Fix Applied
Updated the field mapping in both extraction scripts:
- `serpapi_youtube_extraction.py` -- Changed comment parsing to read `channel.name` for author and `extracted_vote_count` for likes
- `upload_youtube_to_supabase.py` -- Same mapping fix for the standalone uploader

#### Backfill from raw_response
For the newer batch of comments (536 videos, 14,991 comments), the full SerpAPI response had been stored in the `raw_response` jsonb column. This allowed backfilling the `author` and `likes` fields directly from the stored data without making any new API calls.

The older batch (164 videos, 4,469 comments) was extracted before the `raw_response` column existed, so those comments cannot be backfilled without re-fetching from SerpAPI (~550 API calls).

#### Plain English
For the newer comments, we had kept a photocopy of the original SerpAPI response in our database. So we could go back to that photocopy, find the author name and likes count in the right place, and fill in the blanks. For the older comments, we did not keep photocopies, so the only way to fill in the blanks would be to go back to SerpAPI and ask again (which costs API credits).

---

### Part 3: Schema Changes

#### `raw_response jsonb` Column Added

Added a `raw_response` column (type: jsonb) to two tables that were missing it:
- `youtube_channels` -- Stores the full SerpAPI channel response
- `youtube_comments` -- Stores the full SerpAPI comment response

The `youtube_videos` table already had this column from Session 19.

#### Why This Matters
Storing the raw API response is insurance against future problems like the field mapping bug. If a field is mapped incorrectly or a new field becomes available, the raw data can be re-processed without re-calling the API.

#### Plain English
This is like keeping the original receipt after a purchase. Even if you file the purchase under the wrong category in your spreadsheet, you can always go back to the receipt and correct it. Without the receipt (raw_response), you would have to go back to the store (SerpAPI) and ask for a copy -- which takes time and may cost money.

---

### Part 4: Pipeline Status Summary (Handoff Reference)

#### Current State

The YouTube data pipeline has three Supabase tables populated with data from SerpAPI:

**`youtube_videos` (700 rows):**
These are the top 700 YouTube videos by citation count from the 2,300 unique YouTube URLs found in AI responses. Each row contains video metadata (title, views, likes, publish date), the full transcript text and timestamped segments, and a link to the channel that uploaded it.

**`youtube_channels` (293 rows):**
The 293 unique YouTube channels that uploaded those 700 videos. Each has subscriber count, verification status, and channel handle.

**`youtube_comments` (19,460 rows):**
Comments from 592 of the 700 videos. Contains comment text, author name (77% populated), likes count (44% populated), and publish date.

#### What Still Needs Doing

1. **Comment sentiment analysis** (highest value, no API cost)
   - 19,460 comments need to be classified as positive, neutral, or negative
   - The database columns `sentiment` (text) and `sentiment_score` (float) already exist and are empty
   - Could use an LLM (like Claude or GPT) to batch-classify, or a lighter NLP library like TextBlob or VADER

2. **Re-fetch comments for original 137 videos** (moderate value, ~550 SerpAPI calls)
   - Would fill the 4,469 comments that are missing author and likes fields
   - Command: `uv run python clients/samsung/scripts/serpapi_youtube_extraction.py --comments-only`
   - Note: the `--comments-only` flag needs implementation or the videos can be manually re-run

3. **Fetch remaining 1,623 videos** (low priority)
   - All remaining videos have 5 or fewer citations each
   - The extraction script has built-in resume support and will automatically skip already-fetched videos
   - Command: `uv run python clients/samsung/scripts/serpapi_youtube_extraction.py`

4. **Additional slides**
   - Current 5 slides focus on Mini-LED tag
   - Could create similar decks for other tags (OLED, Gaming TVs, etc.)
   - Comment sentiment slides would be possible once sentiment analysis is complete

#### Scripts Reference

| Script | What It Does | How to Run |
|--------|-------------|------------|
| `serpapi_youtube_extraction.py` | Main pipeline: fetches video details, comments, and transcripts from SerpAPI, uploads to Supabase. Supports `--tag`, `--workers`, `--limit`, `--offset`, `--dry-run`, `--skip-comments` flags. Has resume support (skips already-fetched videos). | `uv run python clients/samsung/scripts/serpapi_youtube_extraction.py` |
| `upload_youtube_to_supabase.py` | Uploads YouTube data from a local JSON file to Supabase. Used for initial test batch. | `uv run python clients/samsung/scripts/upload_youtube_to_supabase.py` |
| `test_youtube_top10.py` | Tests SerpAPI response structure for YouTube videos. | `uv run python clients/samsung/scripts/test_youtube_top10.py` |

#### Slides Reference

Five slides were built in Session 20, all at `clients/samsung/slides/youtube_citations/`:

| Slide | File | Content |
|-------|------|---------|
| 1 | `1-overview.html` | KPI scorecards (videos, citations, channels, views, comments) + Mini-LED prompt bar chart |
| 2 | `2-influencer-channels.html` | Top YouTube channels table ranked by citation count + bar chart |
| 3 | `3-top-videos.html` | Top individual videos table with mini bar visualizations |
| 4 | `4-timestamp-citations.html` | Cards showing specific transcript moments that AI models reference |
| 5 | `5-transcript-insights.html` | Themes, word frequency analysis, and representative quote cards |

---

### Session Summary

| Aspect | Detail |
|--------|--------|
| Primary task | Data quality audit and handoff documentation |
| Videos audited | 700 (of 2,300 cited URLs) |
| Channels audited | 293 |
| Comments audited | 19,460 |
| Bug fixed | SerpAPI comment field mapping (`channel.name` to `author`, `extracted_vote_count` to `likes`) |
| Schema changes | Added `raw_response jsonb` to `youtube_channels` and `youtube_comments` |
| Backfill completed | 14,991 comments had author/likes populated from raw_response |
| Backfill gap | 4,469 comments (old batch) still missing author/likes -- need SerpAPI re-fetch |
| Documentation | Pipeline status section added to DEVELOPMENT.md; handoff notes in both doc files |

### Files Modified
- `clients/samsung/scripts/serpapi_youtube_extraction.py` -- Fixed comment field mapping
- `clients/samsung/scripts/upload_youtube_to_supabase.py` -- Fixed comment field mapping

### Supabase Changes
- Added `raw_response jsonb` column to `youtube_channels` table
- Added `raw_response jsonb` column to `youtube_comments` table
- Backfilled 14,991 comment rows with author and likes from raw_response

### Lessons Learned

1. **Always store the raw API response.** The `raw_response` column saved us from needing ~550 API calls to backfill comment fields. The original 164-video batch did not store raw responses for comments/channels, and those records now have permanent gaps unless re-fetched. The cost of storing a few KB of JSON per row is trivial compared to the cost of re-calling an API.

2. **API field names are not always intuitive.** SerpAPI uses `channel.name` for comment author and `extracted_vote_count` for likes. These are not obvious mappings. When integrating with any API, always inspect the actual response structure rather than guessing field names from documentation alone.

3. **"Missing" vs "zero" is ambiguous in API responses.** SerpAPI omits the `likes` field entirely when a comment has 0 votes, rather than returning `likes: 0`. This means a missing field could mean "zero" or "not fetched" -- two very different things. When designing schemas, consider adding a `fetched_at` timestamp or a `raw_response` column to distinguish between "we never asked" and "the answer was nothing."

---

## 2026-02-06 (Session 20): YouTube Citations 5-Slide Presentation Build

### Session Goals
Build the complete 5-slide YouTube Citations presentation deck at `clients/samsung/slides/youtube_citations/`, implementing the plan from Session 19. Query Supabase for YouTube citation data and hardcode it inline following the existing Samsung slide pattern.

---

### Part 1: Data Preparation

#### What Was Queried

Data was pulled from four Supabase tables to populate the slides:

| Table | What It Provided |
|-------|-----------------|
| `youtube_videos` | Video metadata: titles, views, likes, publish dates, transcripts, transcript_segments (JSONB with timestamps) |
| `youtube_channels` | Channel names, subscriber counts, verification status |
| `youtube_comments` | Comment counts per video |
| `semrush_prompt_urls` | Which AI prompts cite YouTube URLs and how many times |

The resulting dataset covers 164 videos cited by AI models, from 86 unique YouTube channels, with 3,175 total citations across AI prompts, 4,469 comments, and 18.2 million combined views.

#### Plain English
We gathered data from four different filing cabinets in our database. One cabinet had details about each video (title, how many people watched it, what was said in the video). Another had information about the YouTube channels that made those videos. A third had all the viewer comments. And the fourth had records of which questions people asked AI models that resulted in these videos being recommended. Combining all four gave us the complete picture for the presentation.

---

### Part 2: Slide-by-Slide Build

#### Slide 1: Overview (`1-overview.html`)

**Content:** Five KPI scorecards across the top (videos cited, total citations, unique channels, total views, total comments) followed by a horizontal bar chart showing the top prompts that trigger YouTube citations, plus a key insights panel.

**Technical:** KPI cards use the standard Samsung card pattern from `slides.css`. The bar chart is built with D3.js v7, rendering horizontal bars sized proportionally to citation count. Insights are presented as bullet points in a styled panel below the chart.

**Plain English:** This is the "big picture" slide. It answers: "How much YouTube content are AI models recommending?" The KPI cards give five headline numbers at a glance, the bar chart shows which questions people ask that lead to YouTube videos being cited, and the insights highlight the most important takeaways.

#### Slide 2: Influencer Channels (`2-influencer-channels.html`)

**Content:** A table of the top 15 YouTube channels ranked by how often their videos are cited by AI models, showing channel name, subscriber count, number of videos cited, total citations, and total views. Accompanied by a bar chart and insights panel.

**Technical:** The table uses the standard slide table styling. Bar chart rendered with D3.js. Channel data was aggregated by joining `youtube_videos` with `youtube_channels` on `channel_id`, then grouping by channel to sum citations and views.

**Plain English:** This slide answers: "Which YouTube creators does AI trust the most?" If a channel like RTINGS or MKBHD has many of its videos recommended by AI, that tells us AI models view that channel as an authority on the topic. The table ranks these channels so Samsung can see who the key influencers are in the AI recommendation ecosystem.

#### Slide 3: Top Videos (`3-top-videos.html`)

**Content:** A table of the top 15 individual videos ranked by citation count, showing title, channel, views, likes, and citations. Each row includes mini bar visualizations for views and citations to make comparisons visual.

**Technical:** Mini bars are inline SVG elements rendered proportionally within table cells. This approach avoids full D3.js chart overhead while still providing visual comparison. Video data comes directly from `youtube_videos` table ordered by `citation_count DESC`.

**Plain English:** This slide answers: "Which specific videos do AI models recommend the most?" While the previous slide looked at channels (the creators), this one looks at individual videos. A single viral review video might be cited dozens of times. This helps Samsung identify exactly which content pieces AI models are sending people to.

#### Slide 4: Timestamp Citations (`4-timestamp-citations.html`)

**Content:** 12 cards, each showing a specific moment in a video that AI models reference. Each card displays the video title, channel name, timestamp, and the exact transcript quote at that moment.

**Technical:** Transcript snippets were extracted using SQL by matching the `start_ms` field within the `transcript_segments` JSONB column in `youtube_videos`. Each segment has a `start_ms` (milliseconds) and `snippet` (text) field. The query finds the segment closest to the cited timestamp and extracts a window of surrounding segments to form a coherent quote.

**Plain English:** This is the most granular slide. When AI models cite a YouTube video, they sometimes reference a specific moment -- like "at 3:45 in this video, the reviewer explains why Mini-LED backlighting reduces blooming." This slide shows exactly what was said at those moments. It is like having someone watch 164 videos for you and mark the exact quotes that AI models think are most important.

#### Slide 5: Transcript Insights (`5-transcript-insights.html`)

**Content:** A themes chart showing major topics discussed across all cited video transcripts, a word frequency analysis highlighting the most common technical terms, and 6 representative quote cards pulled from transcripts.

**Technical:** Themes and word frequency were derived from transcript analysis of the top-cited videos. The themes chart uses D3.js horizontal bars. Word frequency data was computed by tokenizing `transcript_text`, removing stop words, and counting occurrences of relevant technical terms. Quote cards are manually selected representative excerpts that illustrate key themes.

**Plain English:** This slide answers: "What are all these YouTube videos actually talking about?" Instead of watching 164 videos, this slide summarizes the common themes (like "backlighting technology" or "picture quality comparison"), shows which words come up most often (revealing what topics dominate the conversation), and highlights 6 representative quotes that capture the overall narrative. It is like reading a book summary instead of the whole book.

---

### Part 3: Design Decisions

#### Inline Data Pattern

All data is hardcoded directly into each HTML file rather than fetching from Supabase at runtime. This matches the established pattern across all Samsung slide decks (`slides/qled/`, `slides/tv_ai_visibility/`, `slides/mini_led_deepdive/`, `slides/genai/`).

**Why this works:** These slides are snapshot analyses meant for presentations. The data represents a specific point in time and does not need to update dynamically. Hardcoding means the slides work offline, load instantly, have no API dependencies, and can be shared as standalone files.

**Plain English:** Think of these slides like printed photographs rather than live camera feeds. A photograph captures a moment perfectly and works anywhere -- you can email it, print it, show it on any screen. A live camera feed needs a network connection and a server running. For presentations, photographs (hardcoded data) are more reliable.

#### Transcript Timestamp Extraction

The most technically interesting part was extracting transcript quotes at specific timestamps. YouTube transcripts are stored as JSONB arrays where each segment has:
- `start_ms`: when the segment starts (in milliseconds)
- `snippet`: the text spoken during that segment

To get a readable quote, we could not just take one segment (they are often only 2-5 words). Instead, we took a window of surrounding segments (typically 3-5 before and after the target timestamp) and concatenated their `snippet` fields to form a coherent sentence or paragraph.

**Plain English:** YouTube transcripts are chopped into tiny pieces -- sometimes just a few words each, with a timestamp for when each piece was spoken. To get a meaningful quote, we could not just grab one piece ("reduces the" is not useful). Instead, we grabbed the pieces before and after the target moment and stitched them together into a complete thought, like assembling puzzle pieces around a center point.

---

### Session Summary

| Aspect | Detail |
|--------|--------|
| Primary deliverable | 5-slide YouTube Citations presentation deck |
| Location | `clients/samsung/slides/youtube_citations/` |
| Data scope | 164 videos, 86 channels, 3,175 citations, 4,469 comments, 18.2M views |
| Data sources | `youtube_videos`, `youtube_channels`, `youtube_comments`, `semrush_prompt_urls` |
| Pattern followed | Existing Samsung slide pattern (standalone HTML, D3.js v7, `../css/slides.css`, inline data) |
| Slides built | 5 of 5 (overview, channels, videos, timestamps, transcript insights) |
| Status | Complete |

### Files Created
- `clients/samsung/slides/youtube_citations/1-overview.html` -- KPI scorecards + top prompts bar chart
- `clients/samsung/slides/youtube_citations/2-influencer-channels.html` -- Top 15 channels table + bar chart
- `clients/samsung/slides/youtube_citations/3-top-videos.html` -- Top 15 videos table with mini bars
- `clients/samsung/slides/youtube_citations/4-timestamp-citations.html` -- 12 timestamp citation cards with transcript quotes
- `clients/samsung/slides/youtube_citations/5-transcript-insights.html` -- Themes chart + word frequency + quote cards

### Lessons Learned

1. **JSONB timestamp extraction needs windowing.** A single transcript segment is usually too short (2-5 words) to be meaningful. Always extract a window of surrounding segments to form coherent quotes. The `start_ms` field is in milliseconds, not seconds -- a common source of off-by-1000x errors.

2. **Inline data slides are faster to build than live-data slides.** No loading states, error handling, or API configuration needed. For snapshot analyses that represent a specific point in time, hardcoding is the pragmatic choice.

3. **Mini bar visualizations in tables are highly effective.** Simple inline SVG bars within table cells provide instant visual comparison without the overhead of a full charting library. They make numeric tables much easier to scan.

---

## 2026-02-06 (Session 19): YouTube Data Extraction Pipeline & Slide Planning

### Session Goals
Build a complete pipeline to extract YouTube video data (details, comments, transcripts) for videos cited in AI responses, store it in Supabase, and plan a 5-slide presentation for YouTube citation analysis. Also continued investigating the Supabase RPC timeout issue documented in Session 18.

---

### Part 1: YouTube Citation Discovery

#### What Was Found
The `semrush_prompt_urls` table contains 4,070 unique YouTube URLs with 15,363 total citations across AI responses. After deduplicating by video ID (extracting the `v=` parameter from URLs), this reduced to 2,324 unique videos. The difference comes from URL variants -- the same video can be cited with different tracking parameters, mobile URLs (`m.youtube.com`), short URLs (`youtu.be`), or timestamp links (`&t=123`).

The data spans 34 distinct dates from 2026-01-01 to 2026-02-03.

#### Plain English
When AI models like ChatGPT or Google AI recommend YouTube videos in their responses, the same video often shows up with slightly different web addresses. For example, one video might appear as `youtube.com/watch?v=abc123`, `m.youtube.com/watch?v=abc123` (the mobile version), or `youtube.com/watch?v=abc123&t=45` (linking to a specific timestamp). All of these are the same video, just with different "decorations" on the address. We found 4,070 different addresses pointing to 2,324 actual videos.

---

### Part 2: SerpAPI YouTube Extraction Pipeline

#### Architecture

The extraction script (`clients/samsung/scripts/serpapi_youtube_extraction.py`) uses SerpAPI as a data intermediary rather than the YouTube Data API directly. SerpAPI provides a unified interface that returns video details, comments, and transcripts in structured JSON.

**Two SerpAPI engines used:**
1. `youtube_video` -- Returns video metadata (title, views, likes, published date, description, chapters) and comments (with pagination via `next_page_token`)
2. `youtube_video_transcript` -- Returns the full transcript with timestamps and text segments

**Extraction flow per video:**
1. Call SerpAPI `youtube_video` engine with the video ID
2. Parse video details (title, views, likes, description, chapters)
3. Extract channel info and upsert into `youtube_channels` (create if new, update if exists)
4. Parse comments from the response
5. If more comments exist (`next_page_token`), paginate to fetch additional pages
6. Call SerpAPI `youtube_video_transcript` engine for the transcript
7. Combine transcript segments into full text
8. Upload everything to Supabase (video record, channel record, comment records)

#### Plain English
Think of SerpAPI as a librarian who goes to YouTube on our behalf. Instead of us going to YouTube directly (which has strict rules about how many books we can check out), we ask the librarian to fetch the information. For each video, the librarian gets us four things: the video's details (title, how many people watched it, when it was posted), the channel that posted it, what people said in the comments, and a written transcript of everything said in the video. The librarian puts all of this into a neat package that we then store in our database.

#### CLI Flags

The script supports several command-line options:
- `--tag <tag>` -- Only extract videos cited in prompts with this tag (e.g., `--tag "Mini-LED"`)
- `--workers <n>` -- Number of concurrent extraction threads (default: 2)
- `--limit <n>` -- Maximum number of videos to process
- `--offset <n>` -- Skip the first N videos (for resuming)
- `--dry-run` -- Show what would be extracted without actually calling APIs
- `--skip-comments` -- Extract video details and transcript only, skip comments

#### Concurrency and Retry Logic

The script uses Python's `ThreadPoolExecutor` for concurrent processing. Initially 10 workers were tried, but SerpAPI frequently returned "Server disconnected without sending a response" errors. Reducing to 3 was borderline. 2 workers proved stable at approximately 200 videos per hour.

A retry wrapper (`serpapi_call()`) handles transient failures:
- On disconnect, waits with exponential backoff (2s, 4s, 8s)
- Retries up to 3 times before giving up on a video
- Logs all retries for debugging

#### Plain English
Imagine sending 10 research assistants to the same library at the same time. The library gets overwhelmed and starts closing the door on some of them ("Server disconnected"). We reduced to 2 assistants going at a time, which the library could handle. If an assistant gets turned away, they wait a bit (starting at 2 seconds, then doubling) and try again up to 3 times before giving up on that particular book.

#### Resume Support

The script checks which video IDs already exist in the `youtube_videos` table before starting. Any videos already extracted are skipped automatically. This means you can stop the script and restart it without re-processing completed videos.

---

### Part 3: Supabase Schema Design

#### Three New Tables

**`youtube_channels`**
| Column | Type | Purpose |
|--------|------|---------|
| id | bigint (PK) | Auto-generated ID |
| channel_handle | text (UNIQUE) | YouTube handle (e.g., `@MKBHD`); used as dedup key |
| name | text | Display name |
| link | text | Full channel URL |
| thumbnail | text | Channel avatar URL |
| subscribers | text | Raw subscriber text (e.g., "18.2M subscribers") |
| extracted_subscribers | bigint | Parsed numeric value (e.g., 18200000) |
| verified | boolean | Whether channel is verified |
| fetched_at | timestamptz | When data was fetched |

**`youtube_videos`**
| Column | Type | Purpose |
|--------|------|---------|
| id | bigint (PK) | Auto-generated ID |
| video_id | text (UNIQUE) | YouTube video ID (the `v=` parameter) |
| url | text | Canonical URL |
| channel_id | bigint (FK) | Reference to youtube_channels |
| title | text | Video title |
| thumbnail | text | Thumbnail URL |
| views | bigint | View count |
| likes | bigint | Like count |
| published_date | text | Publication date string |
| description | text | Video description text |
| description_links | jsonb | Links extracted from description |
| chapters | jsonb | Video chapter markers |
| transcript_text | text | Full transcript as concatenated text |
| transcript_segments | jsonb | Individual transcript segments with timestamps |
| citation_count | bigint | Number of AI citations for this video |
| comments_token | text | Token for fetching additional comments later |
| raw_response | jsonb | Complete SerpAPI response for future use |
| fetched_at | timestamptz | When data was fetched |

**`youtube_comments`**
| Column | Type | Purpose |
|--------|------|---------|
| id | bigint (PK) | Auto-generated ID |
| video_id | text (FK) | Reference to youtube_videos.video_id |
| author | text | Comment author name |
| content | text | Comment text |
| likes | bigint | Comment like count |
| published_date | text | When comment was posted |
| reply_count | integer | Number of replies |
| sentiment | text | Placeholder for future sentiment analysis |
| sentiment_score | real | Placeholder for future sentiment score |
| fetched_at | timestamptz | When data was fetched |

All tables have Row Level Security (RLS) enabled with `anon` read policies for dashboard access.

#### Plain English
We created three filing cabinets in our database:

1. **Channels cabinet** -- One folder per YouTube channel (like MKBHD or Linus Tech Tips). Contains the channel's name, how many subscribers they have, and their profile picture. Each channel gets a unique folder so we never create duplicates.

2. **Videos cabinet** -- One folder per video. Contains everything about the video: its title, how many views and likes it has, the full transcript (everything said in the video), any chapter markers, and links in the description. We also store a "comments token" -- think of it as a bookmark that tells us where to pick up if we want to fetch more comments later.

3. **Comments cabinet** -- One entry per comment on each video. Contains who wrote the comment, what they said, how many likes the comment got, and when it was posted. We also reserved space for future sentiment analysis (is the comment positive or negative?).

#### RPC Functions

Two SQL functions were created:

1. **`get_youtube_cited_urls()`** -- Takes all YouTube URLs from `semrush_prompt_urls`, extracts the video ID from each URL, groups them together, and counts total citations across all URL variants. Returns a list of unique videos with their aggregated citation counts.

2. **`get_youtube_cited_urls_by_tag(p_tag)`** -- Same as above but only looks at URLs from prompts tagged with a specific topic (e.g., "Mini-LED"). This lets us focus extraction on videos relevant to a particular analysis.

#### Plain English
These are pre-built database queries that do the hard work of URL deduplication. Instead of the dashboard having to figure out that `youtube.com/watch?v=abc123` and `m.youtube.com/watch?v=abc123&t=45` are the same video, the database handles this automatically and tells the dashboard "this video was cited 15 times total across all its URL variants."

---

### Part 4: Extraction Results

#### Mini-LED Prioritized Extraction

We started with videos tagged under "Mini-LED" prompts since this was the immediate analysis need. Results:

| Metric | Count |
|--------|-------|
| Videos extracted | 164 |
| Channels discovered | 86 |
| Comments collected | 4,469 |
| Processing rate | ~200 videos/hour |
| API calls per 20 videos | ~75 (avg ~4 per video) |

The ~4 API calls per video breaks down as: 1 for video details + 1-2 for comment pages + 1 for transcript. Some videos have no transcript (unavailable) which saves a call.

#### Plain English
We processed 164 YouTube videos that AI models cite when people ask about Mini-LED TVs. For each video, we collected who made it, what was said, and what viewers think (via comments). At our processing speed of ~200 videos per hour, the full set of 164 took less than an hour.

---

### Part 5: Bugs Encountered and Fixed

#### Bug 1: Description Field Type Error

**What happened:** The script crashed with a type error when trying to store the video description.

**Technical cause:** SerpAPI returns the `description` field as a dictionary `{"content": "...", "links": [...]}` rather than a plain string. The code assumed it was a string and tried to insert it directly into a text column.

**Plain English:** We expected the description to be a simple block of text, but it came wrapped in a package with both the text AND a list of links. It would be like receiving a letter inside a box when you expected just the letter -- you need to open the box first.

**Fix:** Added an `isinstance()` check: if the description is a dictionary, extract the `content` field for the text column and the `links` field for the separate `description_links` jsonb column. If it is already a string, use it directly.

#### Bug 2: Transcript Field Name Mismatch

**What happened:** The transcript text was empty even though segments were being returned.

**Technical cause:** The code joined segments using `segment['text']` but SerpAPI transcript segments use the key `snippet` not `text`.

**Plain English:** We were looking for the transcript text under the label "text" but SerpAPI filed it under "snippet." It is like looking for a file labeled "Notes" when it is actually labeled "Memo" -- the content is the same, just the label differs.

**Fix:** Changed the join expression from `segment['text']` to `segment['snippet']`.

#### Bug 3: RPC Return Type Mismatch

**What happened:** The `get_youtube_cited_urls()` function failed after being updated with new columns.

**Technical cause:** PostgreSQL does not allow changing the return type of an existing function. You must drop the old function first and recreate it.

**Plain English:** Imagine you have a report template that produces a table with 3 columns. If you want to change it to 5 columns, you cannot just edit the template -- you have to throw away the old one and create a brand new template. That is how PostgreSQL treats function signatures.

**Fix:** Added `DROP FUNCTION IF EXISTS get_youtube_cited_urls()` before the `CREATE OR REPLACE FUNCTION` statement.

#### Bug 4: Numeric vs Bigint Type Mismatch

**What happened:** The RPC function returned an error about incompatible types.

**Technical cause:** PostgreSQL's `SUM()` aggregate function returns `numeric` type, but the function's return type declared the column as `bigint`. These types are not automatically compatible in function return types.

**Plain English:** The database calculated a sum and got a number like "15363" but stored it in a general-purpose number format. Our function expected a specific integer format. Even though they look the same, the database treats them as different types -- like the difference between writing "15,363" (formatted number) and "15363" (plain integer).

**Fix:** Added explicit `::bigint` casts to all `SUM()` expressions in the function.

#### Bug 5: Supabase 1000 Row Limit

**What happened:** Only 1,000 cited URLs were returned even though the actual count was higher.

**Technical cause:** The Supabase JavaScript client library caps RPC results at 1,000 rows by default. This is a client-side limit, not a database limit.

**Plain English:** Supabase only delivers results in batches of 1,000. If you have 2,324 results, you get the first 1,000 and the rest are silently dropped. It is like a delivery truck that can only carry 1,000 packages -- anything beyond that needs a second trip.

**Fix:** Added a pagination loop that calls the RPC with `LIMIT 1000 OFFSET n` incrementally until no more rows are returned, then combines all pages.

#### Bug 6: SerpAPI Server Disconnects

**What happened:** With 10 concurrent workers, many requests failed with "Server disconnected without sending a response."

**Technical cause:** SerpAPI's servers could not handle 10 simultaneous requests from the same client. The server simply dropped connections under load.

**Plain English:** We were making too many phone calls to SerpAPI at the same time. Their switchboard got overwhelmed and started hanging up on us. By reducing from 10 simultaneous calls to 2, the switchboard could handle the load.

**Fix:** Reduced workers from 10 to 2 and added a retry wrapper with exponential backoff (wait 2s, then 4s, then 8s between retries).

#### Bug 7: Python Output Buffering

**What happened:** When running the script in the background, no output appeared in the log file for long periods.

**Technical cause:** Python buffers stdout by default. When output is redirected to a file (not a terminal), it only flushes when the buffer is full (~4KB) or the program exits.

**Plain English:** Python was writing its progress reports into a holding pen instead of sending them out immediately. It would wait until it had enough to fill a page before actually writing to the log file. For a slow-running script, this meant no visible progress for minutes at a time.

**Fix:** Run with `python -u` flag which disables output buffering, causing each print statement to appear immediately.

---

### Part 6: YouTube Citation Slide Plan

#### Planned Slides

Five HTML slides were planned for the YouTube citations presentation at `clients/samsung/slides/youtube_citations/`:

| # | File | Content |
|---|------|---------|
| 1 | `1-overview.html` | KPI scorecards (total videos cited, total citations, unique channels, avg views) + horizontal bar chart of top prompts that cite YouTube |
| 2 | `2-influencer-channels.html` | Table of top channels by citation count with subscriber counts and verification badges + bar chart of citations per channel |
| 3 | `3-top-videos.html` | Table of top videos by citation count with views, likes, publish date, and channel name |
| 4 | `4-timestamp-citations.html` | Cards showing transcript excerpts at the specific timestamps cited by AI models |
| 5 | `5-transcript-insights.html` | Aggregated themes from transcripts, word frequency analysis, representative quotes |

These follow the existing Samsung slide pattern (standalone HTML files with inline data, Samsung branding, D3.js charts) established in Sessions 14-15.

#### Plain English
We planned five presentation slides that tell the story of "Which YouTube videos do AI models recommend when people ask about Mini-LED TVs?" The slides go from broad to specific:
1. The big picture numbers (how many videos, how many citations)
2. Which YouTube channels are most cited (the influencers AI trusts)
3. Which specific videos are most cited
4. What exact moments in videos are being referenced (transcript quotes)
5. Common themes across all the transcripts (what topics come up repeatedly)

---

### Session Summary

| Aspect | Detail |
|--------|--------|
| Primary deliverable | YouTube data extraction pipeline |
| Script | `clients/samsung/scripts/serpapi_youtube_extraction.py` |
| API used | SerpAPI (`youtube_video` + `youtube_video_transcript` engines) |
| New Supabase tables | `youtube_channels`, `youtube_videos`, `youtube_comments` |
| New RPC functions | `get_youtube_cited_urls()`, `get_youtube_cited_urls_by_tag(p_tag)` |
| Data extracted | 164 videos, 86 channels, 4,469 comments (Mini-LED tag) |
| Total YouTube URLs found | 4,070 (2,324 unique videos after dedup) |
| Bugs fixed | 7 (description type, transcript field, RPC signature, numeric cast, row limit, concurrency, buffering) |
| Slide plan | 5 slides at `clients/samsung/slides/youtube_citations/` |
| Status | Pipeline complete; Mini-LED extraction done; slides planned but not yet built |

### Files Created
- `clients/samsung/scripts/serpapi_youtube_extraction.py` -- Main extraction pipeline
- `clients/samsung/scripts/upload_youtube_to_supabase.py` -- Initial test upload helper
- `clients/samsung/scripts/test_youtube_top10.py` -- SerpAPI response structure validation

### Lessons Learned

1. **SerpAPI rate limits are connection-based, not key-based.** Reducing concurrent connections matters more than spacing out requests. 2 workers was the sweet spot for stability.

2. **Always check API response field types.** SerpAPI documentation does not always match reality. The description field being a dict instead of a string was undocumented. Always use `isinstance()` checks when mapping API responses to database columns.

3. **PostgreSQL function signatures are immutable.** You cannot change the return type of an existing function with `CREATE OR REPLACE`. You must `DROP FUNCTION` first. This is different from modifying the function body, which `CREATE OR REPLACE` handles fine.

4. **Supabase RPC has a client-side 1000 row limit.** This is not a database limit -- it is the JavaScript client library default. Always implement pagination when RPC results might exceed 1000 rows.

5. **Save raw API responses.** Storing the complete `raw_response` in a jsonb column costs minimal storage but provides enormous value: you can re-extract fields, debug mapping issues, and discover new data without re-calling the API.

6. **Deduplicate at the database level.** YouTube URLs have many variants (tracking params, mobile URLs, timestamps). Deduplicating in SQL with regex video_id extraction is more reliable and reusable than doing it in Python.

7. **Use `python -u` for background scripts.** Output buffering causes log files to appear empty during long-running processes. The `-u` flag forces immediate output, which is essential for monitoring progress.

---

## 2026-02-06 (Session 18): Supabase RPC Timeout Investigation on Samsung Geo Dashboard

### Session Goals
Investigate and document an intermittent 500 error on the Samsung GEO Dashboard caused by a Supabase RPC function timing out under concurrent load. This was a diagnostic session -- the fix has been identified but deferred.

---

### Part 1: The Symptom

#### What Happened
When loading the Samsung GEO Dashboard (`clients/samsung/dashboards/geo-dashboard.html`), users sometimes see the error:

```
Error loading data: Supabase RPC error: 500 - {"code":"57014","details":null,"hint":null,"message":"canceling statement due to statement timeout"}
```

The error is intermittent -- refreshing the page often makes it go away.

#### Plain English
Imagine you walk into a restaurant and order 10 dishes at the same time. The kitchen has a strict rule: every dish must be ready within 3 minutes or it gets thrown away. Most of the time, each dish takes about 1.7 minutes, so they all finish in time. But when the kitchen is busy preparing all 10 dishes simultaneously, some dishes take longer than 3 minutes and get cancelled. If you order again (refresh), the kitchen remembers the recipes from last time (they are still on the counter), so everything comes out faster and nothing gets cancelled.

That is exactly what is happening with the dashboard's database queries.

---

### Part 2: Root Cause Analysis

#### The Technical Chain of Events

1. **The dashboard fires 10 RPC calls simultaneously.** On line 3755 of `geo-dashboard.html`, the `loadDashboard()` function uses `Promise.all` to fire all data-fetching functions at once. This is normally a good practice -- it loads data in parallel instead of one-at-a-time.

2. **One of those calls is `get_samsung_country_citations()`.** This RPC function queries the `semrush_prompt_urls` table (317,789 rows, 151 MB total). It runs 6 regex operations per row to extract country codes from URLs across roughly 23,000 "Owned" domain rows.

3. **The `anon` role has a 3-second statement timeout.** Supabase assigns different timeout limits based on the database role making the request:
   - `anon` role: **3 seconds** (used by the public dashboard)
   - `authenticated` role: **8 seconds** (used by logged-in users)
   - `service_role`: **unlimited** (used by backend admin tasks)

4. **Under ideal conditions, the query takes ~1.7 seconds.** That is well within the 3-second limit. But when 10 queries hit the database simultaneously, they compete for CPU, memory, and disk I/O. The country citations query -- being the heaviest -- gets pushed past 3 seconds and gets killed by Postgres.

5. **On refresh, it works.** After the first attempt, Postgres has loaded the relevant data pages into its buffer cache (RAM). The second attempt reads from cache instead of disk, making it significantly faster -- fast enough to finish within 3 seconds even under concurrent load.

#### Plain English
The dashboard asks the database 10 questions at once. One of those questions is particularly hard -- it has to scan through 300,000+ rows and run pattern-matching on each one. The database has a 3-second deadline for answering questions from anonymous users. Usually the hard question finishes in about 1.7 seconds, but when the database is also answering the other 9 questions at the same time, it sometimes takes longer than 3 seconds and gets cut off. When you refresh the page, the database has already loaded the relevant data into its fast memory, so the same question now takes less than a second.

#### What the Error Code Means
- **PostgreSQL error code `57014`**: "canceling statement due to statement timeout"
- This is Postgres saying: "I stopped running your query because it took too long according to the timeout configured for your role."

---

### Part 3: Why This Specific Query Is Slow

#### The `get_samsung_country_citations()` Function

This function does the following:
1. Filters `semrush_prompt_urls` to rows where `domain_type = 'Owned'` (about 23,000 rows)
2. Runs **6 regex operations per row** to extract country codes from Samsung URLs (e.g., `samsung.com/us/` becomes `/us/`, `design.samsung.com` becomes `design.samsung.com`)
3. Groups the results by country code and counts citations

The table statistics:
- Total rows: **317,789**
- Total table size: **151 MB**
- Rows matching `domain_type = 'Owned'`: **~23,000**
- Regex operations per matching row: **6**
- Effective regex evaluations: **~138,000** per query execution

#### Plain English
Think of it like searching through a filing cabinet with 300,000 folders. First, you pull out the 23,000 folders labeled "Owned." Then for each of those 23,000 folders, you open them up and run 6 different pattern-matching tests to figure out which country the folder belongs to. That is 138,000 pattern-matching operations. On a good day, you can finish this in 1.7 seconds. On a busy day when you are also doing 9 other searches at the same time, it takes over 3 seconds.

---

### Part 4: Role Timeout Configuration

#### Supabase Role Timeouts
Supabase uses PostgreSQL's `statement_timeout` setting per role:

| Role | Timeout | Used By |
|------|---------|---------|
| `anon` | 3 seconds | Public-facing dashboards (no login required) |
| `authenticated` | 8 seconds | Logged-in users |
| `service_role` | Unlimited | Backend admin tasks, Edge Functions |

The Samsung GEO Dashboard uses the `anon` key (no authentication required), which means all queries must complete within 3 seconds.

#### Plain English
The database treats different types of users differently. Anonymous visitors (people who just open the dashboard without logging in) get a strict 3-second limit. Logged-in users get 8 seconds. Admin tools have no limit. Our dashboard is public, so it gets the strictest limit.

---

### Part 5: Planned Fix (Deferred)

#### Option A: Materialized View (Primary Fix)
Create a materialized view that pre-computes the country citation aggregations. Instead of running regex on 23,000 rows every time someone loads the dashboard, the results would be calculated once and stored. The dashboard query would then read the pre-computed results instantly.

**Before (current):** Every dashboard load runs ~138,000 regex evaluations in real time.
**After (with materialized view):** Every dashboard load reads ~30 pre-computed rows. Instant.

The materialized view would need to be refreshed periodically (e.g., after new data is loaded), but this refresh would run as `service_role` with no timeout.

#### Option B: Bump `anon` Timeout to 8 Seconds (Safety Net)
As an additional safety measure, the `anon` role timeout could be increased from 3 seconds to 8 seconds. This would match the `authenticated` role's timeout and give all queries more breathing room. However, this alone does not fix the underlying inefficiency -- it just raises the threshold.

#### Why Deferred
The dashboard is functional -- the error only occurs intermittently on first load, and a refresh resolves it. The materialized view approach requires creating the view definition, testing it, setting up a refresh trigger, and verifying the dashboard code works with the new data source. This work is planned but not yet scheduled.

#### Plain English
The long-term solution is to do the hard calculation once ahead of time and save the results, rather than doing it fresh every time someone opens the dashboard. Think of it like pre-making a summary report each night instead of pulling every file and counting from scratch every time someone asks. We have not done this yet because the dashboard works most of the time -- it only fails occasionally on the first load, and refreshing fixes it.

---

### Session Summary

| Aspect | Detail |
|--------|--------|
| Issue | Intermittent 500 timeout on geo-dashboard.html |
| Error code | PostgreSQL `57014` (statement timeout) |
| Root cause | `anon` role 3s timeout + heavy regex query + 10 concurrent RPC calls |
| Affected function | `get_samsung_country_citations()` |
| Affected file | `clients/samsung/dashboards/geo-dashboard.html` (line 3755) |
| Affected table | `semrush_prompt_urls` (317,789 rows, 151 MB) |
| Status | Investigated, fix deferred |
| Planned fix | Materialized view for pre-computed country citations |
| Safety net | Consider bumping `anon` timeout from 3s to 8s |

### Files Investigated (Not Modified)
- `clients/samsung/dashboards/geo-dashboard.html` -- line 3755, `Promise.all` fires 10 RPC calls simultaneously
- Supabase RPC function `get_samsung_country_citations()` -- runs 6 regex operations per row across ~23k rows

### Lessons Learned

1. **Supabase role timeouts are strict.** The `anon` role's 3-second timeout is aggressive for queries involving regex operations across large tables. Always check role timeout limits when designing RPC functions for public-facing dashboards.

2. **Concurrent queries compete for resources.** A query that runs fine in isolation may fail when 9 other queries are running at the same time. `Promise.all` is great for performance but increases database contention.

3. **Postgres buffer cache masks the problem.** The fact that "refresh fixes it" is a classic sign of a cold-cache vs warm-cache issue. The first load hits disk; subsequent loads hit cache. This can make intermittent timeout bugs hard to reproduce consistently.

4. **Regex in SQL is expensive at scale.** Running 6 regex operations per row across 23,000 rows is ~138,000 evaluations. Pre-computing these results (materialized view) is almost always the right approach when the underlying data does not change between requests.

5. **Know your role timeouts.** Different Supabase roles (anon, authenticated, service_role) have different timeout settings. Designing queries for the `anon` role requires keeping them fast or pre-computing heavy aggregations.

---

## 2026-02-04 (Session 17): Samsung Slide Refinements for PowerPoint

### Session Goals
Polish multiple Samsung presentation slides to improve PowerPoint compatibility, remove unnecessary content, update terminology for clarity, and ensure slides fit well when exported to PPT format. This was a refinement session rather than new feature development.

---

### Part 1: Aspect Ratio Improvements for PowerPoint

#### The Problem
The methodology slide had KPI definitions stacked vertically, making the slide too tall for comfortable PowerPoint viewing. When slides are too long, they either get cut off or require scrolling when exported.

#### What Was Changed
**File:** `clients/samsung/slides/tv_ai_visibility/methodology.html`
- Changed KPI items from a vertical stack to a 2-column grid layout
- Reduced padding, font sizes, and gaps throughout the slide
- Made the overall slide more compact

#### Technical Details
The CSS change involved switching from `display: block` (stacking items top to bottom) to a CSS Grid layout with `grid-template-columns: 1fr 1fr` (two equal columns side by side).

#### Plain English
Think of it like organizing items on a shelf. Instead of stacking books on top of each other (making a tall pile), we arranged them side by side in two columns. This uses the same horizontal space but reduces the vertical height, making the slide fit better in PowerPoint's fixed dimensions.

---

### Part 2: Terminology Update - "Direct" to "No Referrer"

#### The Problem
The term "Direct (GenAI)" was misleading. In web analytics, "direct" traffic traditionally means someone typed the URL directly or used a bookmark. But AI traffic that shows as "direct" is actually traffic where the AI platform did not send a referrer header - a technical distinction that was being obscured by the label.

#### What Was Changed
**File:** `clients/samsung/slides/genai/2-source-breakdown.html`
- Renamed "Direct (GenAI)" to "GenAI (No referrer)" in the table and JavaScript data
- Changed the callout title from "Direct Attribution Gap" to "No Referrer Attribution Gap"
- Updated callout description from "show as Direct" to "have no referrer"

#### Technical Details
When you click a link from some AI platforms, the browser does not tell the destination website where you came from (no HTTP Referer header). This traffic gets bucketed as "direct" in analytics tools because there is no referral information. It is not truly "direct" - the user did not type the URL - but the analytics tool cannot tell the difference.

#### Plain English
Imagine you are a store owner trying to figure out where your customers heard about you. Some customers come in and say "I saw your ad on Facebook" (referral traffic). Others come in but have no idea how they found you (direct). Now imagine Facebook started hiding the fact that it sent customers - they still came from Facebook, but the store owner cannot tell anymore. That is what "no referrer" traffic is: we know it came from AI, but the AI platform did not leave a calling card.

#### Why This Matters
Using "No Referrer" instead of "Direct" is more accurate and does not confuse stakeholders who know "direct" has a specific meaning in analytics. It also explains WHY we cannot attribute this traffic rather than implying the users typed the URL.

---

### Part 3: Content Trimming - Removing "Movies & Cinema"

#### What Was Changed
Two slides had their "Movies & Cinema" row removed:
- `clients/samsung/slides/tv_ai_visibility/sov_mentions.html` - Removed from HTML table
- `clients/samsung/slides/tv_ai_visibility/citations_vs_competitors.html` - Removed from both HTML table and JavaScript data array

#### Why
The "Movies & Cinema" category was likely deemed irrelevant to the core TV AI visibility narrative or had insufficient data. Removing low-value rows keeps slides focused and easier to read.

#### Plain English
When preparing a presentation, you want every row in a table to earn its place. If "Movies & Cinema" was not adding insight to the TV AI visibility story, removing it makes the remaining data more impactful. Less noise, more signal.

---

### Part 4: Platform Breakdown Slide Restructure

#### What Was Changed
**File:** `clients/samsung/slides/tv_ai_visibility/platform_breakdown.html`

Major changes:
1. **Removed "Platform Volume Insights" panel entirely** - The panel was redundant or not adding value
2. **Expanded Brand Index table to full width** - Without the insights panel, the table can use all available horizontal space
3. **Added "Overall SOV" column to Brand Index table** - New metric showing each brand's total Share of Voice
4. **Reordered brands by SOV** - Now sorted Samsung, LG, TCL, Sony, Hisense (descending by Share of Voice)
5. **Reduced chart height** - From 220px to 180px
6. **Reduced font sizes** - "Total Mentions" label and value now smaller
7. **Reduced padding and gaps** - Overall slide is shorter/more compact

#### Plain English
This slide got a significant cleanup. An entire panel was removed because it was not earning its space. The main table was expanded to fill the gap and got a new column showing overall Share of Voice. The brands were reordered so Samsung (the client) appears first, followed by competitors in descending order of their share. Finally, everything was made more compact to fit better in PowerPoint.

#### Why Reorder by SOV?
Putting Samsung first (as the brand being analyzed) and then showing competitors in descending SOV order creates a natural narrative: "Here is Samsung, and here are the competitors ranked by how much of the AI conversation they own."

---

### Part 5: Mini-LED Deep Dive Content Refinements

#### What Was Changed

**File 1:** `clients/samsung/slides/mini_led_deepdive/executive_summary.html`
- Removed the quote: "Mini-LED is to TCL what OLED is to LG"

**File 2:** `clients/samsung/slides/mini_led_deepdive/competitor_deepdive.html`
- Changed "exploit with Neo QLED messaging" to "address with Mini-LED messaging"

#### Why Remove the Quote
The quote "Mini-LED is to TCL what OLED is to LG" was likely seen as either:
- Too provocative or confrontational for a client presentation
- Not directly relevant to Samsung's Mini-LED strategy
- Giving too much brand association to competitors

#### Why Change "Exploit" to "Address"
The word "exploit" has negative connotations (taking unfair advantage). "Address" is more professional and focuses on solving a market opportunity rather than taking advantage of competitors. The change also specified "Mini-LED messaging" instead of "Neo QLED messaging" to be more precise about the product category.

#### Plain English
These were tone adjustments. The quote was removed because it might have been too bold for a formal presentation. The word "exploit" was changed to "address" because it sounds less aggressive. Instead of "we will exploit their weakness", it is now "we will address this opportunity" - same idea, more professional language.

---

### Part 6: Pulling Colleague's Work from GitHub

#### What Was Done
Pulled `clients/samsung/slides/tv_ai_visibility/kpi_scorecards.html` from GitHub - a new slide created by a colleague.

#### Plain English
Another team member created a new slide and pushed it to the shared repository. We pulled their changes to get the latest version. This is normal collaborative development using Git.

---

### Session Summary

| Change Type | Count | Description |
|-------------|-------|-------------|
| Aspect ratio improvements | 1 | methodology.html made more compact |
| Terminology updates | 1 | "Direct" renamed to "No referrer" |
| Content removals | 3 | Movies & Cinema rows, quote, insights panel |
| Structural changes | 1 | platform_breakdown.html restructured |
| Messaging updates | 1 | "exploit" changed to "address" |
| External pulls | 1 | Colleague's kpi_scorecards.html |

### Files Modified

- `clients/samsung/slides/tv_ai_visibility/methodology.html` - Aspect ratio improvements
- `clients/samsung/slides/genai/2-source-breakdown.html` - Terminology update
- `clients/samsung/slides/tv_ai_visibility/sov_mentions.html` - Removed Movies & Cinema row
- `clients/samsung/slides/tv_ai_visibility/platform_breakdown.html` - Major restructure
- `clients/samsung/slides/tv_ai_visibility/citations_vs_competitors.html` - Removed Movies & Cinema row
- `clients/samsung/slides/mini_led_deepdive/executive_summary.html` - Removed quote
- `clients/samsung/slides/mini_led_deepdive/competitor_deepdive.html` - Messaging update

### Files Pulled from GitHub

- `clients/samsung/slides/tv_ai_visibility/kpi_scorecards.html`

### Lessons Learned

1. **PowerPoint constraints matter:** When creating HTML slides that will be exported to PPT, vertical space is at a premium. Using grid layouts instead of stacked layouts helps fit more content.

2. **Terminology precision:** Using accurate technical terms ("no referrer") instead of simplified-but-misleading terms ("direct") prevents confusion when presenting to analytics-savvy stakeholders.

3. **Less is more in presentations:** Removing low-value content (the quotes, the insights panel, the Movies & Cinema rows) makes the remaining content more impactful.

4. **Professional tone:** Words like "exploit" might seem fine in internal discussions but should be replaced with neutral terms like "address" in client-facing materials.

---

## 2026-02-04 (Session 16): TV AI Visibility Presentation - Methodology Slide

### Session Goals
Create a methodology slide for the TV AI Visibility presentation that explains where the data comes from, how KPIs are calculated, and which AI platforms are tracked. This slide provides essential context for stakeholders viewing the presentation.

---

### Part 1: Why a Methodology Slide?

#### The Problem
Presentations showing AI visibility metrics often raise questions from stakeholders: "Where does this data come from?", "What exactly does Share of Voice mean?", "Are we tracking ChatGPT or just Google?" Without a methodology slide, these questions interrupt the flow and require verbal explanations that may be inconsistent.

#### The Solution
A dedicated methodology slide that:
1. Lists all data sources with what each provides
2. Defines every KPI with its formula
3. Shows which AI platforms are tracked by each source
4. Acknowledges known data limitations upfront

#### Plain English
Think of it like the "fine print" section of a financial report, but made readable and placed upfront. Instead of stakeholders wondering "how did you calculate this?", they can reference a single slide that explains everything. It builds trust because it shows transparency about both what we measure and what we cannot measure.

---

### Part 2: The Methodology Slide Structure

#### Data Sources Section

The slide explains two primary data sources:

**SEMrush AI Visibility:**
- Tracks when Samsung is mentioned in AI responses
- Monitors brand mentions, concepts, sentiment, and citations
- Captures which prompts trigger Samsung appearances

**Adobe Analytics:**
- Tracks actual traffic and revenue from AI referrals
- Measures conversion rates and order values
- Shows business impact of AI visibility

#### Plain English
SEMrush tells us "how often do AI assistants talk about Samsung?" while Adobe Analytics tells us "when AI sends people to Samsung.com, do they buy anything?" One measures visibility (are we being seen?), the other measures results (is it working?).

---

### Part 3: KPI Definitions

The slide defines all metrics used throughout the presentation:

| KPI | Definition | Plain English |
|-----|------------|---------------|
| Mentions | Count of times Samsung appears in AI responses | How many times AI assistants say "Samsung" |
| Share of Voice (SOV) | Samsung mentions / Total brand mentions x 100 | What percentage of the conversation is about us vs competitors |
| Citations | Count of Samsung URLs linked by AI | How many times AI assistants link to Samsung.com |
| Visibility Score | Cited URLs / Total tracked URLs x 100 | What percentage of our pages are being referenced by AI |
| CVR (Conversion Rate) | Purchases / Sessions x 100 | What percentage of AI-referred visitors buy something |
| AOV (Average Order Value) | Revenue / Number of orders | How much the average AI-referred customer spends |
| Revenue | Total sales from AI-referred traffic | Actual dollars generated from AI visibility |

#### Why Define Every KPI?
Different stakeholders may interpret "Share of Voice" differently. A PR person might think it means media coverage; a marketing person might think it means ad impressions. By defining it explicitly as "Samsung mentions divided by total brand mentions in AI responses", everyone is aligned.

---

### Part 4: AI Platforms Tracked

The slide shows which AI platforms are monitored by each data source:

**SEMrush Tracks:**
- ChatGPT
- Google AI Overview
- Google AI Mode
- Perplexity
- Claude

**Adobe Analytics Tracks:**
- Referral traffic from ai.com, chatgpt.com domains
- Referral traffic from AI-related Google properties
- Referral traffic from perplexity.ai

#### Plain English
SEMrush monitors what AI assistants say about Samsung across five major platforms. Adobe Analytics monitors when people click links from those AI assistants and visit Samsung.com. Together they paint a complete picture: visibility (SEMrush) and impact (Adobe).

---

### Part 5: Data Limitations Section

The slide includes a placeholder section for documenting known caveats. This is intentionally left for the user to fill in based on their specific context. Common limitations might include:

- Date range limitations (e.g., "Data starts from December 2025")
- Platform coverage gaps (e.g., "Bing Copilot not yet tracked")
- Attribution challenges (e.g., "Some AI referrals may be misclassified as direct traffic")
- Data refresh frequency (e.g., "Updated weekly, may lag 24-48 hours")

#### Why Include Limitations?
Acknowledging what you cannot measure builds more trust than pretending everything is perfect. Stakeholders appreciate honesty about data boundaries.

---

### Part 6: Files Created and Modified

#### Files Created
| File | Purpose |
|------|---------|
| `clients/samsung/slides/tv_ai_visibility/methodology.html` | Methodology slide explaining data sources, KPIs, and platforms |

#### Files Modified
| File | Changes |
|------|---------|
| `clients/samsung/docs/tv_ai_visibility.md` | Added slide #6 documentation |

---

### Session Summary

| Task | Status |
|------|--------|
| Create methodology slide HTML | Complete |
| Add data sources section | Complete |
| Add KPI definitions section | Complete |
| Add AI platforms section | Complete |
| Add data limitations placeholder | Complete |
| Update presentation documentation | Complete |

### Decisions Made

| Decision | Why | Alternative Rejected |
|----------|-----|---------------------|
| Separate methodology slide | Dedicated space for context, referenceable | Inline notes on each slide (scattered, repetitive) |
| Two data source categories | Clear distinction between visibility and impact | Single merged list (confuses what each provides) |
| Table format for KPIs | Easy to scan, clear formula column | Paragraph text (harder to reference) |
| Placeholder for limitations | User knows their specific caveats better | Pre-filled generic limitations (may not apply) |

### Lessons Learned

1. **Methodology slides build trust** - Transparency about data sources makes stakeholders more confident in the numbers
2. **Define KPIs explicitly** - Different roles interpret the same term differently; explicit definitions align everyone
3. **Acknowledge limitations** - Admitting what you cannot measure is more credible than pretending completeness

---

## 2026-02-02 (Session 15): Samsung TV Panel Type Slides - 5-Slide Restructure (QLED Prototype)

### Session Goals
Restructure the panel type presentation from a single 3-section page into 5 focused slides, using QLED as the prototype. Each slide addresses a specific analytical question with dedicated visualizations and real data from Supabase.

---

### Part 1: Why Restructure to 5 Slides?

#### The Problem with 3 Sections
The original single-page design with 3 sections (Platform Breakdown, Concepts & Sentiment, Competitive Analysis) crammed too much information into one view. Stakeholders often asked follow-up questions that required scrolling back and forth.

#### The 5-Slide Solution
Breaking into 5 slides allows:
1. Each slide to answer ONE question clearly
2. More room for supporting details (like actual quotes)
3. Natural presentation flow with pause points for discussion
4. Deeper drill-downs where needed (trends, citations)

#### Plain English
Think of it like presenting a business report. Instead of one dense page with three cramped sections, you create a slide deck where each slide makes ONE point clearly. The audience can absorb each insight before moving to the next.

---

### Part 2: The 5-Slide Structure

#### Slide 1: Platform Distribution (`1-platform.html`)

**What It Shows:**
Two side-by-side donut charts comparing Mentions vs Citations by AI platform.

**Technical Details:**
- **Left donut (Mentions):** Brand mentions in AI responses, grouped by `llm`
- **Right donut (Citations):** Samsung URLs cited, grouped by `llm`
- Data sources: `semrush_concept_prompts` (mentions), `semrush_prompt_urls` (citations)

**Key Insight from QLED Data:**
- Mentions: ChatGPT leads at 46%
- Citations: Google AI Overview dominates at 72%
- This tells us ChatGPT talks about Samsung QLED a lot, but Google AI Overview actually cites Samsung URLs more

**Plain English:**
Imagine two questions: "Who talks about us?" vs "Who links to our website?" These can have very different answers. ChatGPT might mention Samsung in 46% of QLED conversations, but when it comes to actually citing Samsung.com URLs, Google AI Overview does it 72% of the time. This matters for SEO strategy.

---

#### Slide 2: Concepts & Sentiment (`2-concepts.html`)

**What It Shows:**
Horizontal stacked bars showing sentiment breakdown for top 10 QLED concepts, plus 5 real AI quotes.

**Technical Details:**
- Bars show positive (green), neutral (gray), negative (red) percentages per concept
- Concepts sorted by total mention count
- Quotes pulled from `semrush_concept_prompts.quote` column
- Quote mix: 2 positive, 1 neutral, 2 negative for balance

**Chart Function:**
```javascript
renderConceptBars(containerId, data)
// data = [{ concept: "Picture Quality", positive: 65, neutral: 25, negative: 10 }, ...]
```

**Plain English:**
This slide shows WHAT AI models say about QLED TVs and HOW they feel about it. The horizontal bars are like survey results - "65% positive, 25% neutral, 10% negative" for each topic. The quotes below are actual examples so stakeholders can see the exact words AI uses.

---

#### Slide 3: Citations (`3-citations.html`)

**What It Shows:**
Table of top cited Samsung URLs with the prompts that triggered citations.

**Technical Details:**
- Data source: `semrush_prompt_urls` filtered by `tag = 'QLED'` and `domain LIKE '%samsung.com%'`
- Columns: URL, Citation Count, Top Prompts
- Clean table format for scanning

**Why Table Instead of Cards:**
Tables are better for comparing many items. Stakeholders can scan URLs quickly, see which pages are cited most, and understand what questions drive traffic to each page.

**Plain English:**
This answers "Which Samsung web pages are AI models linking to, and why?" If you see `/us/televisions/qled-tv/` cited 150 times for prompts like "best QLED TV for gaming", that tells you this page is doing well for gaming-related AI queries.

---

#### Slide 4: Trends (`4-trends.html`)

**What It Shows:**
Multi-line time series chart showing how concept mentions evolved over time.

**Technical Details:**
- X-axis: Date (Dec 18, 2025 to Jan 29, 2026)
- Y-axis: Mention count
- Each line represents a different concept
- Data source: `semrush_concept_prompts` grouped by `date` and `concept_name`

**Chart Function:**
```javascript
renderTrendLines(containerId, data)
// data = { dates: [...], series: [{ name: "Picture Quality", values: [...] }, ...] }
```

**Key Insight:**
The data shows a significant spike around January 15, 2026. This aligns with when new prompts were added to the SEMrush tracking. Understanding this pattern prevents misinterpreting the spike as organic growth.

**Plain English:**
This is like a stock chart but for brand mentions. You can see if Samsung's visibility is growing, shrinking, or spiking on certain dates. The Jan 15 spike isn't viral fame - it's when we started tracking more prompts. Knowing this context prevents wrong conclusions.

---

#### Slide 5: Competitive Analysis (`5-competitive.html`)

**What It Shows:**
Dual bar charts comparing Samsung vs competitors on Branded vs Generic prompts.

**Technical Details:**
- **Branded prompts:** Contain brand/model names (e.g., "Samsung QLED vs LG OLED")
- **Generic prompts:** No brand references (e.g., "best TV for bright rooms")
- Regex filtering on `semrush_concept_prompts.prompt` column:
  ```sql
  WHERE prompt ~* '(samsung|lg|sony|tcl|hisense|qled|oled|neo qled)'  -- Branded
  WHERE prompt !~* '(samsung|lg|sony|tcl|hisense|qled|oled|neo qled)' -- Generic
  ```

**Chart Function:**
```javascript
renderDualCompetitorBars(containerId, brandedData, genericData)
// brandedData = [{ brand: "Samsung", value: 156 }, { brand: "LG", value: 89 }, ...]
// genericData = [{ brand: "Samsung", value: 234 }, { brand: "LG", value: 178 }, ...]
```

**Why This Matters:**
- Winning on **branded prompts** = defensive positioning (people searching for you find you)
- Winning on **generic prompts** = offensive positioning (people searching for the category find you)
- A brand might dominate branded searches but lose generic searches to competitors

**Plain English:**
When someone asks "Is Samsung QLED good?" (branded), you want Samsung to win. But when someone asks "What's the best TV for gaming?" (generic), the competition is fiercer. This slide shows if Samsung wins the "home game" (branded) AND the "away game" (generic).

---

### Part 3: Files Created

| File | Purpose |
|------|---------|
| `clients/samsung/slides/qled/1-platform.html` | Dual donut: Mentions vs Citations by platform |
| `clients/samsung/slides/qled/2-concepts.html` | Stacked sentiment bars + AI quotes |
| `clients/samsung/slides/qled/3-citations.html` | Table of top cited URLs |
| `clients/samsung/slides/qled/4-trends.html` | Multi-line time series |
| `clients/samsung/slides/qled/5-competitive.html` | Branded vs Generic comparison |
| `clients/samsung/slides/css/slides.css` | Shared CSS for all slides |

---

### Part 4: New Chart Functions Added to `slide-charts.js`

| Function | Purpose |
|----------|---------|
| `renderConceptBars(containerId, data)` | Horizontal stacked sentiment bars |
| `renderCitationList(containerId, data)` | URL cards with prompts (replaced by table) |
| `renderTrendLines(containerId, data)` | D3 multi-line time series |
| `renderDualCompetitorBars(containerId, branded, generic)` | Side-by-side branded/generic bars |
| `renderSimpleBars(containerId, data)` | Helper for horizontal bars |
| `renderDonut(containerId, data, centerLabel)` | Updated to accept custom center text |

---

### Part 5: Key Data Discoveries

#### Prompt Counts
- Total unique prompts in `concept_prompts` table: **380**
- Prompts relating to QLED specifically: **266**
- This high percentage (70%) shows QLED is a major topic in the tracked prompts

#### Platform Differences (QLED Data)
| Metric | ChatGPT | Google AI Overview | Google AI Mode |
|--------|---------|-------------------|----------------|
| Mentions | 46% | 32% | 22% |
| Citations | 18% | 72% | 10% |

**Insight:** ChatGPT mentions Samsung often but rarely cites URLs. Google AI Overview cites URLs frequently. This has implications for content strategy.

#### Terminology Clarification
- **Citations** = AI response links to a Samsung URL
- **Mentions** = AI response references Samsung brand/products in text

These are NOT the same thing. A response can mention Samsung without citing any URL, or cite a Samsung URL without explicitly mentioning the brand in surrounding text.

---

### Part 6: Pending Work

**Task #7:** Replicate the 5-slide structure to remaining 5 panel type categories:
- OLED
- Mini-LED
- Micro RGB
- Gaming TVs
- Sports TVs

Each category will get its own subfolder under `clients/samsung/slides/` with the same 5 HTML files, parameterized for that category's data.

---

### Session Summary

| Task | Status |
|------|--------|
| Design 5-slide structure | Complete |
| Create QLED prototype slides (5 files) | Complete |
| Create shared CSS file | Complete |
| Add chart functions to slide-charts.js | Complete |
| Replicate to other 5 categories | Pending |

### Decisions Made

| Decision | Why | Alternative Rejected |
|----------|-----|---------------------|
| 5 slides instead of 3 sections | Clearer focus per slide, better for presentations | Single dense page (overwhelming), 10+ slides (too many) |
| Dual donut for platform | Visualizes Mentions vs Citations distinction | Single donut with toggle (loses comparison) |
| Horizontal stacked bars for concepts | Shows sentiment breakdown per concept clearly | Treemap (loses % precision), vertical bars (truncates names) |
| Real quotes on concepts slide | Concrete evidence, actionable for PR | Separate quotes slide (loses context) |
| Table for citations | Easy to scan, sortable | Cards (wastes space) |
| Branded vs Generic for competitive | Most actionable competitive split | Overall SOV (misses nuance) |

### Lessons Learned

1. **Mentions and Citations are different metrics** - Don't conflate them; they tell different stories about brand visibility
2. **Data spikes need context** - The Jan 15 spike is data collection growth, not organic growth
3. **5 slides > 3 sections** - Breaking into more slides allows each to breathe and tell one story
4. **Real quotes add credibility** - Stakeholders want to see actual AI language, not just percentages

---

## 2026-02-02 (Session 14): Samsung TV Panel Type Slides (Initial 3-Section Version)

### Session Goals
Create presentation-ready HTML slides for Samsung TV panel type analysis. Each slide focuses on a specific TV category (Gaming TVs, QLED, Sports TVs, OLED, Mini-LED, Micro RGB) and displays three D3.js visualizations showing AI platform distribution, concept sentiment, and competitive positioning.

---

### Part 1: Why Panel-Type-Specific Slides?

#### The Problem
The GEO Dashboard provides comprehensive AI visibility data, but it shows everything at once. For stakeholder presentations, product managers need focused views that answer: "How is Samsung performing specifically in the OLED TV category?" or "Which AI models mention our Gaming TVs most?"

#### Plain English
Imagine you run a restaurant with multiple cuisines (Italian, Mexican, Japanese). Your main dashboard shows overall ratings, but when presenting to your Italian chef, you want a focused report on just Italian dishes. These slides are like "per-cuisine" reports - each one zooms in on a specific TV panel type so the right team sees only the data relevant to them.

---

### Part 2: Slide Structure

Each of the 6 slides follows the same three-section layout:

#### Section 1: Platform Breakdown (Donut Chart)

**What It Shows:**
A donut chart displaying the distribution of AI model mentions for prompts tagged with that panel type.

**Technical Details:**
- Data source: `semrush_prompt_urls` table filtered by tag
- Groups by `llm` column (AI model name)
- Shows percentage of total mentions per model

**Plain English:**
This chart answers "Which AI assistants (ChatGPT, Google AI, etc.) talk about this TV type the most?" If SearchGPT mentions OLED TVs 60% of the time but Google AI Overview only 20%, we know where Samsung is more visible.

#### Section 2: Concepts & Sentiment (Treemap)

**What It Shows:**
A treemap visualization where each rectangle represents a Samsung concept (product feature, attribute, or topic). Rectangle size shows mention frequency; color shows sentiment (green=positive, gray=neutral, red=negative).

**Technical Details:**
- Data source: `semrush_concept_prompts` table filtered by tag
- Groups by `concept_name` column
- Color mapping: positive (#4CAF50), neutral (#9E9E9E), negative (#F44336)
- Size mapping: `mentions` count

**Plain English:**
This shows what AI models are saying about Samsung in this TV category. Big green boxes are good (popular positive features). Big red boxes are problems to address (frequently mentioned negatives). Small boxes are niche topics that get less attention.

#### Section 3: Competitive Analysis (Radar Chart)

**What It Shows:**
A radar (spider) chart comparing Samsung against competitors (LG, Sony, TCL, Hisense) across multiple metrics.

**Technical Details:**
- Data source: `semrush_concept_prompts` joined with competitive brand data
- Metrics: Share of Voice, Positive Sentiment %, Citation Count, Visibility Score
- Each brand plotted as a separate line on the radar

**Plain English:**
This answers "How does Samsung compare to competitors in this TV category?" If Samsung's line covers more area than LG's line, Samsung is winning overall. If LG's line extends further on the "Positive Sentiment" axis, LG has better PR in this category.

---

### Part 3: Files Created

| File | Purpose |
|------|---------|
| `clients/samsung/slides/gaming-tvs.html` | Gaming TVs panel type slide |
| `clients/samsung/slides/qled.html` | QLED TV panel type slide |
| `clients/samsung/slides/sports-tvs.html` | Sports TVs panel type slide |
| `clients/samsung/slides/oled.html` | OLED TV panel type slide |
| `clients/samsung/slides/mini-led.html` | Mini-LED TV panel type slide |
| `clients/samsung/slides/micro-rgb.html` | Micro RGB TV panel type slide |
| `clients/samsung/slides/js/slide-charts.js` | Shared D3.js chart library |

---

### Part 4: The Shared Chart Library

#### Why a Shared Library?

Instead of copying chart code into each slide, we created `slide-charts.js` with three reusable functions:

```javascript
// Donut chart for platform distribution
renderDonut(containerId, data)
// data = [{ label: "SearchGPT", value: 45 }, ...]

// Treemap for concepts with sentiment coloring
renderTreemap(containerId, data)
// data = [{ name: "brightness", value: 120, sentiment: "positive" }, ...]

// Radar chart for competitive comparison
renderRadar(containerId, data)
// data = { metrics: ["SOV", "Sentiment", ...], brands: [{ name: "Samsung", values: [80, 65, ...] }, ...] }
```

#### Plain English
Think of this like a box of LEGO bricks. Instead of building each chart from scratch, we created reusable "bricks" (chart functions) that any slide can use. If we want to change how the radar chart looks, we change it once in the library and all 6 slides automatically get the update.

---

### Part 5: Design Decisions

| Decision | Why | Alternatives Rejected |
|----------|-----|----------------------|
| Separate HTML file per panel type | Self-contained slides easy to share; no URL parameters needed; works offline | Single parameterized page (harder to share), tabs (less focused), PDF (loses interactivity) |
| D3.js for all visualizations | Consistent rendering; full control over radar/treemap; already used in sunburst | Chart.js (no native treemap/radar), multiple libraries (larger bundle) |
| Three charts per slide | Covers platform, sentiment, and competition; fits on one screen; answers key questions | More charts (overwhelming), fewer (incomplete) |
| Shared chart library | DRY principle; easier maintenance; guaranteed visual consistency | Inline code per slide (duplication, drift) |

---

### Part 6: How the Slides Query Data

Each slide queries Supabase with a tag filter matching its panel type:

```javascript
// Example for OLED slide
const tag = 'OLED';

// Platform breakdown query
const { data: platformData } = await supabase
  .from('semrush_prompt_urls')
  .select('llm, count(*)')
  .eq('tag', tag)
  .group('llm');

// Concepts query
const { data: conceptData } = await supabase
  .from('semrush_concept_prompts')
  .select('concept_name, mentions, sentiment')
  .eq('tag', tag);
```

**Plain English:**
Each slide asks Supabase: "Give me all the data, but only for [this TV type]." The OLED slide only sees OLED data. The Gaming TVs slide only sees Gaming data. Same database, different filters.

---

### Lessons Learned

1. **Separate slides are easier to present than a filtered dashboard** - Stakeholders want to screenshot or print a slide, not navigate a complex UI with filters.

2. **D3.js treemaps require hierarchical data** - The treemap expects data in a nested format (`{ name: "root", children: [...] }`), not a flat array. We had to transform the Supabase response before rendering.

3. **Radar charts need normalized data** - Raw values (Samsung: 10,000 mentions, Hisense: 500 mentions) make the chart unreadable. We normalize to 0-100 scale so all metrics are comparable.

4. **Shared libraries pay off quickly** - Even with just 6 slides, the shared library saved significant time and ensures that fixing a bug in one chart fixes it everywhere.

---

## 2026-02-02 (Session 13): Samsung Competitive AI Visibility Analysis

### Session Goals
Load competitor brand data into Supabase and create RPC functions to enable competitive analysis. This allows Samsung to measure true Share of Voice against LG, Sony, TCL, and Hisense on generic (non-branded) prompts where all brands compete.

---

### Part 1: Why Competitive Analysis Matters

#### The Problem
The existing Samsung dashboard only tracked Samsung's own performance. While we knew Samsung appeared in X% of prompts, we had no way to answer: "How does Samsung compare to LG on OLED-related prompts?" or "Which brand has the most negative sentiment?"

Share of Voice on brand-specific prompts (e.g., "Samsung TV reviews") is always 100% Samsung - not useful. The real competitive insight comes from generic prompts like "best 65 inch TV" where all brands compete.

#### Plain English
Imagine you are a restaurant tracking your own reviews. You know you have 4.2 stars, but is that good or bad? Without knowing your competitors have 4.5 stars (or 3.8 stars), your rating is just a number. Competitive analysis turns your isolated metrics into meaningful comparisons.

---

### Part 2: Loading Competitor Data

#### What Was Fetched
The script `fetch_competitor_concept_prompts.py` fetched concept prompt data for 4 competitor brands:

| Brand | Concept ID | Rows Loaded |
|-------|-----------|-------------|
| LG | 13802 | ~43K |
| Sony | 13803 | ~43K |
| TCL | 13804 | ~43K |
| Hisense | 13805 | ~43K |
| **Total** | | **174,029** |

#### API Call Pattern
```python
# For each brand, fetch each day in the range
for brand_id in [13802, 13803, 13804, 13805]:
    for date in date_range("2026-01-01", "2026-01-29"):
        response = semrush_api.get_concept_prompts(
            concept_id=brand_id,
            date=date
        )
        # Insert rows into semrush_concept_prompts
```

#### Performance
- 116 API calls total (29 days x 4 brands)
- 12.8 minutes to complete
- Average 1,500 rows per call

#### Plain English
We asked SEMrush: "For each competitor brand, on each day of January 2026, show me every AI prompt where that brand was mentioned, along with what was said about them (positive, negative, neutral)." The script ran this query 116 times and loaded all the results into our database.

---

### Part 3: Database State After Load

#### semrush_concept_prompts Table Summary

| Brand | Total Rows | % of Table |
|-------|-----------|-----------|
| Samsung | 164,730 | 48.6% |
| LG | 49,712 | 14.7% |
| Sony | 44,891 | 13.3% |
| TCL | 41,234 | 12.2% |
| Hisense | 38,192 | 11.3% |
| **Total** | **338,759** | 100% |

Samsung has more rows because they are the primary tracked brand with more historical data.

#### Plain English
Our database now contains nearly 340,000 records of what AI models say about TV brands. Almost half of these records are about Samsung (our main client), and the other half is split across four competitors. This gives us a complete picture of the competitive landscape.

---

### Part 4: Competitive RPC Functions Created

#### Function 1: get_competitive_sov(p_prompt_type)

**Purpose:** Calculate Share of Voice (mention frequency) by brand.

**Parameters:**
- `p_prompt_type`: 'generic' (non-branded prompts only) or 'all'

**Returns:**
| brand | mention_count | prompt_count | sov_pct |
|-------|--------------|--------------|---------|
| Samsung | 12,456 | 12,567 | 99.2% |
| LG | 10,891 | 12,444 | 87.5% |
| ... | ... | ... | ... |

**How It Works:**
```sql
-- Generic prompts = prompts without brand names in the text
WHERE (p_prompt_type = 'all'
   OR prompt NOT ILIKE '%samsung%'
   AND prompt NOT ILIKE '%lg%'
   AND prompt NOT ILIKE '%sony%'
   ...)
```

**Plain English:** This function answers "Of all the AI prompts about TVs, what percentage mention each brand?" The 'generic' filter focuses on prompts like "best 4K TV" rather than "Samsung TV reviews" to show true competitive visibility.

---

#### Function 2: get_brand_sentiment_comparison(p_prompt_type)

**Purpose:** Compare sentiment breakdown across brands.

**Returns:**
| brand | positive_pct | neutral_pct | negative_pct |
|-------|-------------|-------------|--------------|
| Samsung | 55.2% | 41.8% | 3.0% |
| LG | 58.1% | 41.2% | 0.7% |
| Sony | 61.3% | 38.0% | 0.7% |
| ... | ... | ... | ... |

**Plain English:** This shows whether AI models are saying positive or negative things about each brand. Samsung has more negative mentions (3%) than competitors (<1%), which is an important finding for the PR team.

---

#### Function 3: get_negative_concepts_by_brand(p_brand, p_limit)

**Purpose:** Find what AI models criticize about a specific brand.

**Example for Samsung:**
| concept | negative_count | sample_quote |
|---------|---------------|--------------|
| Dolby Vision | 89 | "Samsung TVs lack Dolby Vision support..." |
| price | 67 | "Samsung TVs are more expensive than..." |
| burn-in | 45 | "OLED TVs including Samsung have burn-in risk..." |

**Plain English:** This drills down into why a brand has negative sentiment. For Samsung, the top complaints are about missing Dolby Vision support, high prices, and burn-in concerns. This gives the PR team specific talking points to address.

---

#### Function 4: get_prompt_brand_comparison(p_prompt, p_tag)

**Purpose:** Compare brands head-to-head on a specific prompt or topic tag.

**Example for "best OLED TV 2026":**
| brand | mentioned | position_avg | sentiment |
|-------|-----------|-------------|-----------|
| LG | Yes | 1.2 | Positive |
| Samsung | Yes | 2.8 | Neutral |
| Sony | Yes | 3.1 | Positive |

**Plain English:** When someone asks "best OLED TV 2026", which brand does the AI recommend first? This shows LG typically appears in position 1 (recommended first) while Samsung appears around position 3.

---

#### Function 5: get_competitive_landscape()

**Purpose:** Quick executive summary of all brands.

**Returns:**
| brand | total_mentions | unique_prompts | positive_pct | negative_pct |
|-------|---------------|----------------|--------------|--------------|
| Samsung | 164,730 | 36,765 | 55.2% | 3.0% |
| LG | 49,712 | 12,444 | 58.1% | 0.7% |
| ... | ... | ... | ... | ... |

**Plain English:** A single-glance overview showing each brand's total presence and sentiment. Good for executive dashboards or quick comparisons.

---

### Part 5: Key Competitive Findings

#### Share of Voice on Generic Prompts

| Brand | SOV % | Interpretation |
|-------|-------|---------------|
| Samsung | 99.2% | Mentioned in almost every generic TV prompt |
| LG | 87.5% | Strong presence, especially OLED |
| Sony | 71.3% | Premium segment focus |
| TCL | 68.9% | Budget segment strength |
| Hisense | 52.1% | Growing but less established |

**Insight:** Samsung dominates generic prompt visibility, but this includes neutral mentions ("Samsung and LG both offer..."). The quality of mentions matters as much as quantity.

#### Sentiment Comparison

| Brand | Positive | Neutral | Negative |
|-------|----------|---------|----------|
| Samsung | 55.2% | 41.8% | **3.0%** |
| LG | 58.1% | 41.2% | 0.7% |
| Sony | 61.3% | 38.0% | 0.7% |
| TCL | 52.4% | 46.8% | 0.8% |
| Hisense | 49.1% | 50.1% | 0.8% |

**Insight:** Samsung has 3-4x more negative sentiment than competitors. This is significant and warrants investigation.

#### Tag-Level Performance

| Tag | Leader | Samsung Position |
|-----|--------|-----------------|
| Gaming | Samsung | 1st |
| OLED | LG | 2nd |
| Budget | TCL | 4th |
| Picture Quality | Sony | 2nd |

**Insight:** Samsung leads in Gaming but trails in OLED (LG's strength) and Budget (TCL's strength).

#### Samsung's Strengths (from positive quotes)
- QD-OLED technology
- Brightness (4500 nits)
- Anti-glare screen coating
- Bright room performance
- Gaming features (120Hz, VRR)

#### Samsung's Weaknesses (from negative quotes)
- No Dolby Vision support
- Higher burn-in risk mentioned
- Premium pricing
- Complex smart TV interface

#### Plain English
Samsung appears in almost every TV-related AI response, but gets criticized more often than competitors. The main complaints are about missing Dolby Vision and price. Samsung wins on gaming features and brightness but loses to LG on OLED quality perception and to TCL on value.

---

### Part 6: Files Created

| File | Purpose |
|------|---------|
| `clients/samsung/fetch_competitor_concept_prompts.py` | Python script to fetch competitor data from SEMrush API and load into Supabase |
| `clients/samsung/docs/competitive-analysis.md` | Documentation of analysis methodology and findings |

---

### Part 7: Supabase Changes

| Change Type | Item | Description |
|-------------|------|-------------|
| Data | `semrush_concept_prompts` | Added 174,029 rows for LG, Sony, TCL, Hisense |
| Function | `get_competitive_sov()` | Share of Voice by brand |
| Function | `get_brand_sentiment_comparison()` | Sentiment breakdown by brand |
| Function | `get_negative_concepts_by_brand()` | Top negative concepts for a brand |
| Function | `get_prompt_brand_comparison()` | Head-to-head brand comparison |
| Function | `get_competitive_landscape()` | Executive summary of all brands |

---

### Lessons Learned

1. **Generic prompts reveal true competition:** Brand-specific prompts (e.g., "Samsung TV reviews") always show 100% Samsung. The competitive insight comes from generic prompts where all brands compete for visibility.

2. **Sentiment percentage matters more than volume:** Samsung has 3x more negative mentions than competitors. Even though it is only 3%, this is 4x higher than the 0.7% industry average and represents a PR opportunity.

3. **Tag-level analysis shows niche leadership:** Aggregate SOV hides important details. Samsung leads gaming but trails OLED. Without tag-level breakdown, you would miss these strategic insights.

4. **Negative concept drilldown provides action items:** Knowing "Samsung has 3% negative" is abstract. Knowing "89 negative mentions about Dolby Vision" is actionable - the PR team can prepare talking points about HDR10+ as an alternative.

5. **Competitor data loading is fast:** 174K rows in 12.8 minutes (~230 rows/second) is acceptable for periodic batch updates. No need for real-time streaming.

---

### Part 8: URL Citation Analysis (Continuation)

This section extends the competitive analysis by examining which websites AI models cite when answering generic TV prompts.

#### What Was Analyzed
Using the `semrush_prompt_urls` table, we analyzed URL-level citations to understand:
1. Which domains get cited most on generic (non-branded) prompts
2. How brand websites compare against each other
3. Which sources dominate the critical top-3 citation positions
4. How citation patterns differ across AI models

---

#### Finding 1: Top Cited Domains on Generic Prompts

| Rank | Domain | Citations | Avg Position |
|------|--------|-----------|--------------|
| 1 | rtings.com | 14,414 | 7.1 |
| 2 | samsung.com | 12,012 | - |
| 3 | techradar.com | - | - |
| 4 | youtube.com | - | - |
| 5 | tomsguide.com | - | - |

**Insight:** RTings leads all domains in total citations, appearing as the most authoritative third-party source for TV information. Samsung.com ranks second, showing strong organic visibility even on generic prompts.

**Plain English:** When someone asks an AI "what is the best TV to buy", the AI looks for sources to cite. RTings.com (a TV review site known for detailed testing) is cited most often - over 14,000 times. Samsung's own website comes second with 12,000 citations. This is impressive because these are generic questions, not Samsung-specific ones.

---

#### Finding 2: Brand Website Citations on Generic Prompts

| Brand Website | Total Citations | Prompts Appearing In |
|---------------|-----------------|---------------------|
| samsung.com | 14,986 | 332 |
| lg.com | 3,372 | - |
| tcl.com | 2,170 | - |
| sony.com | 1,480 | - |
| hisense.com | 76 | - |

**Key Ratio:** Samsung.com receives **4.4x more citations** than lg.com on generic prompts.

**Insight:** Samsung's website SEO for AI visibility is significantly stronger than competitors. When AI models need to cite a brand source for generic TV questions, they disproportionately choose Samsung's content.

**Plain English:** Think of this as asking a librarian for general TV advice. When the librarian pulls manufacturer brochures to reference, they reach for Samsung's materials 4-5 times more often than LG's. This suggests Samsung's website content is better optimized for AI discovery - it is easier to find, more comprehensive, or more authoritative in the AI's view.

---

#### Finding 3: Top-3 Position Dominance

Citations in the top 3 positions carry the most weight - users are most likely to click these, and AI models treat early citations as most relevant.

| Domain | Top-3 Citations |
|--------|-----------------|
| rtings.com | 3,987 |
| samsung.com | - |
| lg.com | - |

**Key Ratio:** samsung.com appears in top-3 positions **4x more often** than lg.com.

**Insight:** Samsung not only gets more citations overall, but also gets more premium positions. This compounds the visibility advantage.

**Plain English:** If citations were a race, Samsung is not just running more races than LG - they are also finishing on the podium (top 3) much more frequently. Being mentioned first or second in an AI response is far more valuable than being mentioned tenth.

---

#### Finding 4: Citations by AI Model

Different AI models have different citation patterns:

| Model | Key Observation |
|-------|-----------------|
| Google AI Overview | Cites samsung.com, rtings.com heavily |
| Google AI Mode | Similar to AI Overview |
| SearchGPT | Only model that cites lg.com |
| ChatGPT | Varies by query type |
| Perplexity | Heavy on review sites |

**Notable Finding:** lg.com is **only cited by SearchGPT**, not by any Google AI models. This suggests LG's content may not be optimized for Google's AI systems.

**Another Finding:** samsung.com is **not cited on direct comparison queries** (e.g., "Samsung vs LG TV"). This is expected - AI models avoid citing a brand's own website when asked to compare brands, preferring neutral third-party sources.

**Plain English:**
- Different AI assistants use different libraries. Google's AI assistants never seem to pull from LG's website, while SearchGPT does. This could mean LG's website is not structured in a way Google's AI can easily understand.
- When you ask "Samsung vs LG which is better?", the AI deliberately avoids quoting Samsung.com or LG.com because those sources would be biased. Instead, it quotes review sites like RTings that tested both.

---

#### Strategic Implications

1. **Samsung's AI SEO is working:** 4.4x more brand website citations than the nearest competitor demonstrates effective content optimization for AI discovery.

2. **Opportunity for position improvement:** While Samsung has strong citation volume, focusing on moving more citations into top-3 positions could further increase visibility value.

3. **Competitor weakness:** LG's absence from Google AI citations represents a significant gap Samsung can maintain or widen.

4. **Neutral content strategy:** For comparison queries, Samsung cannot rely on samsung.com. Instead, they should focus on earned media (influencer relationships, PR with review sites) to ensure positive coverage when their own site cannot be cited.

---

### Files Updated

| File | Change |
|------|--------|
| `clients/samsung/docs/competitive-analysis.md` | Added URL citation analysis findings (4 new sections) |

---

## 2026-01-30 (Session 12): Samsung Dashboard System Architecture Documentation

### Session Goals
Create a comprehensive system architecture documentation page for the Samsung AI Visibility Dashboard. This page serves as a technical reference for developers and stakeholders to understand how data flows from SEMrush APIs through Supabase to the frontend dashboard.

---

### Part 1: Why Architecture Documentation Matters

#### The Problem
As the Samsung dashboard grew in complexity (11 charts, 5 tables, 8 RPC functions, 7 database tables, 8 Python scripts), it became difficult to answer basic questions:
- "What data feeds the Share of Voice chart?"
- "Which filters affect which components?"
- "What is the difference between semrush_cited_pages and semrush_prompt_urls?"

Without documentation, this knowledge lived only in the code and in the heads of developers who built it.

#### Plain English
Imagine building a house without blueprints. The electrician, plumber, and carpenter each know their part, but nobody has the full picture. When something breaks, everyone has to trace wires and pipes to figure out how things connect. Architecture documentation is like having blueprints on the wall - anyone can look at them and understand how the system works.

---

### Part 2: What Was Created

#### File Created
`clients/samsung/dashboards/architecture.html` - A self-contained HTML page with Samsung branding that documents the entire system.

#### Sections Included

1. **System Overview**
   - ASCII diagram showing data flow: SEMrush API -> Python Scripts -> Supabase -> Dashboard
   - Three-column summary cards explaining Data Sources, Data Pipeline, and Frontend

2. **Database Schema**
   - Table inventory with row counts (e.g., semrush_prompt_urls: 249,307 rows)
   - Detailed column schemas for primary tables
   - Purpose and key columns for each table

3. **RPC Functions**
   - 8 Supabase functions documented with parameters and return types
   - Example JavaScript code showing how to call functions
   - Example REST API call format

4. **Dashboard Component Inventory**
   - 11 charts listed with chart types (Doughnut, Bar, Line, etc.)
   - 5 tables listed with features (Sortable, Hierarchical, Paginated)
   - 4 KPI cards with live/placeholder status badges

5. **Data Flow**
   - Visual 5-step flow diagram for loadDashboard() orchestration
   - Parallel API fetch code pattern documented
   - Shows how 10 parallel calls are made for performance

6. **Filter System**
   - Main filters: Date Range, Model, Topic, Domain Type, Sentiment
   - Secondary section-specific filters
   - Filter Impact Matrix showing which filters affect which components

7. **Data Pipeline Scripts**
   - 8 Python scripts documented (fetch_*.py and load_*.py)
   - Purpose and output file/table for each
   - Typical data refresh workflow with commands

8. **Technology Stack**
   - Frontend: HTML5/CSS3, Chart.js, D3.js, Vanilla JavaScript
   - Backend: Supabase (PostgreSQL), Edge Functions, REST API + RPC
   - Data Pipeline: Python 3.12+, httpx, supabase-py, SEMrush API

---

### Part 3: Technical Details

#### Page Structure
The architecture page uses the same design system as other dashboard pages:
- Samsung fonts (Samsung Sharp Sans, Samsung One)
- Samsung color palette (primary blue #1428A0, accent colors)
- Design tokens (CSS custom properties for consistent styling)
- Responsive layout that works on mobile/tablet/desktop

#### Navigation
Added to header navigation alongside:
- GEO Dashboard (main dashboard)
- Data Definitions (glossary)
- Architecture (new page)

#### Styling Approach
Used existing component classes from the Samsung design system:
- `.chart-card` - Section containers with titles and borders
- `.schema-table` - Styled tables with alternating rows
- `.component-card` - Summary cards in grid layouts
- `.badge` - Status badges with color variants
- `.diagram-container` - Monospace code/ASCII art containers

---

### Part 4: Database Schema Documentation

#### Tables by Data Volume

| Table | Rows | Purpose |
|-------|------|---------|
| semrush_prompt_urls | 249,307 | URL citations per prompt with position and date |
| semrush_concept_mentions | 151,787 | Brand/concept mentions with sentiment breakdown |
| semrush_concept_prompts | 145,337 | Prompts with quotes and sentiment per brand |
| semrush_cited_pages | 84,856 | Cited Samsung URLs with citation counts |
| semrush_domains | 69,974 | Domain classifications (owned/earned/competitor) |
| semrush_url_prompts | 43,842 | URL-prompt relationships with volume and topic |
| tv_topics | 41 | Topic taxonomy (categories and tags) |

#### Plain English
Think of these tables like different filing cabinets:
- **prompt_urls**: Every time an AI cites a URL, we record it here (biggest cabinet - 249K records)
- **concept_mentions**: When an AI mentions "Samsung" or "picture quality", we count it here
- **cited_pages**: Summary of which Samsung pages are getting cited most
- **domains**: Our classification of websites (is cnet.com "earned media" or "competitor"?)
- **tv_topics**: The categories we use to organize prompts (TV Features, TV Models, etc.)

---

### Part 5: RPC Function Documentation

#### Functions and Their Uses

| Function | What It Does | Used By |
|----------|--------------|---------|
| get_daily_mentions | Aggregates mentions by date, brand, model | KPI Cards, Trend Charts, Share of Voice |
| get_top_categories | Top N categories with sentiment | Topics Bar Chart (now Topics Tree) |
| get_samsung_country_citations | Citations by Samsung country site | Samsung Country Sites Chart |
| get_sources_by_topic | Domains for a specific topic tag | Sources by Topic Table |
| get_cited_urls | Paginated URL list with prompts | Cited URLs Table |
| get_cited_urls_count | Total count for pagination | Cited URLs pagination controls |
| get_negative_quotes | Negative sentiment quotes | PR Action Center |
| get_concept_sentiment_summary | Sentiment breakdown by concept | Concept Mix Charts |

#### Plain English
RPC functions are like asking a librarian a specific question instead of searching the whole library yourself. Instead of the dashboard downloading thousands of records and calculating totals in JavaScript, it asks the database: "Hey, what are the top 10 categories by mention count?" The database does the heavy lifting and returns just the answer.

---

### Part 6: Filter Impact Matrix

#### Which Filters Affect Which Components

| Component | Date | Model | Topic | Domain Type | Sentiment |
|-----------|------|-------|-------|-------------|-----------|
| KPI Cards | Yes | Yes | - | - | - |
| Share of Voice | Yes | Yes | - | - | - |
| Trend Line | Yes | Yes | - | - | - |
| Topics Tree | Yes | Yes | Yes | - | - |
| Citation Sources | - | - | Yes | Yes | - |
| Cited URLs | - | - | - | Yes | - |
| PR Action Center | - | - | - | Yes | Yes |

#### Plain English
Not every filter affects every chart. When you change the date range, the KPI cards and trend chart update, but the Citation Sources table does not (it shows all-time data). The filter impact matrix is like a TV remote guide - it tells you which buttons control which parts of the screen.

---

### Part 7: Why This Matters

#### Benefits of Architecture Documentation

1. **Faster Onboarding:** New developers can understand the system in hours instead of days
2. **Easier Debugging:** When something breaks, you know where to look
3. **Better Planning:** Adding new features starts with understanding existing structure
4. **Stakeholder Communication:** Non-developers can understand what the system does
5. **Living Documentation:** The page can be updated as the system evolves

#### Plain English
Architecture documentation is like a map for a city. You can explore a city without a map, but it takes longer and you might get lost. With a map, you know where you are, how things connect, and how to get where you want to go. This architecture page is our map for the Samsung dashboard system.

---

### Files Created

| File | Purpose |
|------|---------|
| `clients/samsung/dashboards/architecture.html` | System architecture documentation page with database schema, RPC functions, component inventory, data flow diagrams, and filter documentation |

---

### Lessons Learned

1. **Documentation as code:** Treating documentation as a first-class artifact (with version control, styling, and structure) makes it more likely to be maintained.

2. **Plain English matters:** Technical documentation that only developers can read limits its usefulness. Adding "Plain English" explanations makes it accessible to product managers, stakeholders, and future-you.

3. **Visual hierarchy helps:** Using diagrams, tables, badges, and clear section headers makes dense technical content scannable and approachable.

4. **Documentation location matters:** Putting the architecture page in the dashboards folder (rather than a separate docs folder) keeps it close to the code it documents and makes it discoverable.

---

## 2026-01-30 (Session 11): Samsung Country Sites Citation Analysis Chart

### Session Goals
Add a visualization showing which Samsung country sites and subdomains are being cited in AI responses. This helps answer: "Is the US Samsung site being cited appropriately for US market queries, or are AI models pulling from other country sites?"

---

### Part 1: The Business Question

#### What We Needed to Answer
Samsung has country-specific websites for different markets:
- `samsung.com/us/` - US market
- `samsung.com/uk/` - UK market
- `samsung.com/de/` - Germany
- Plus subdomains like `design.samsung.com`, `developer.samsung.com`, `news.samsung.com`

When AI models (ChatGPT, Google AI Overview, etc.) answer questions about Samsung TVs for US users, which Samsung sites are they citing?

#### Why This Matters
- **Wrong country = potentially wrong info:** A German product page might have different pricing, availability, or even different product variants
- **Subdomains reveal content gaps:** If `developer.samsung.com` is being cited for consumer TV questions, that suggests a content gap on the main consumer site
- **Competitive insight:** Understanding citation patterns helps optimize content strategy

#### Plain English
Imagine you ask a US librarian for information about Samsung TVs. You would expect them to hand you brochures from the US Samsung office, not from the Korean or German offices. This chart shows which "offices" the AI librarians are actually pulling information from.

---

### Part 2: The Database Solution

#### New RPC Function: `get_samsung_country_citations()`

This function extracts the country code or subdomain from each Samsung URL and counts how many times each appears:

```sql
CREATE OR REPLACE FUNCTION get_samsung_country_citations()
RETURNS TABLE (
    site text,
    citations bigint,
    unique_urls bigint
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        -- Extract country code like /us/, /uk/, /de/ from URL
        -- OR extract subdomain like design.samsung.com
        CASE
            WHEN url ~ 'samsung\.com/[a-z]{2}/' THEN
                '/' || substring(url from 'samsung\.com/([a-z]{2})/') || '/'
            WHEN url ~ '^https?://([a-z]+)\.samsung\.com' THEN
                substring(url from '^https?://([a-z]+)\.samsung\.com')
            ELSE 'other'
        END as site,
        COUNT(*) as citations,
        COUNT(DISTINCT url) as unique_urls
    FROM semrush_prompt_urls
    WHERE domain_type = 'Owned'
      AND url LIKE '%samsung.com%'
    GROUP BY 1
    ORDER BY 2 DESC;
END;
$$ LANGUAGE plpgsql;
```

#### How the URL Parsing Works

| URL Example | Extracted Site |
|-------------|---------------|
| `https://www.samsung.com/us/televisions/` | `/us/` |
| `https://www.samsung.com/uk/tvs/qled/` | `/uk/` |
| `https://design.samsung.com/global/contents/` | `design` |
| `https://developer.samsung.com/smarttv/` | `developer` |
| `https://news.samsung.com/global/` | `news` |

#### Plain English
The database function looks at every Samsung URL that has been cited by AI models. For each URL, it figures out if it is a country site (like /us/ or /uk/) or a subdomain (like design.samsung.com). Then it counts how many times each site appears and how many unique pages were cited.

---

### Part 3: The JavaScript Implementation

#### New Functions Added

```javascript
// Instance variable to hold the chart (for cleanup on re-render)
let samsungCountryChart = null;

// Fetch citation data from Supabase
async function fetchSamsungCountryCitations() {
    const { data, error } = await supabase.rpc('get_samsung_country_citations');
    if (error) {
        console.error('Error fetching Samsung country citations:', error);
        return [];
    }
    return data;
}

// Render the horizontal bar chart
function renderSamsungCountryChart(data) {
    // Destroy existing chart if present
    if (samsungCountryChart) {
        samsungCountryChart.destroy();
    }

    // Take top 15 sites for readability
    const top15 = data.slice(0, 15);

    // Prepare chart data
    const labels = top15.map(d => d.site);
    const values = top15.map(d => d.citations);

    // Color coding: US site in Samsung blue, others in secondary colors
    const colors = labels.map(label => {
        if (label === '/us/') return '#1428A0';  // Samsung blue for US
        if (label.startsWith('/')) return '#8091df';  // Lighter purple for other countries
        return '#9e9e9e';  // Gray for subdomains
    });

    // Create Chart.js horizontal bar chart
    const ctx = document.getElementById('samsung-country-chart').getContext('2d');
    samsungCountryChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                data: values,
                backgroundColor: colors,
                borderWidth: 0
            }]
        },
        options: {
            indexAxis: 'y',  // Horizontal bars
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: (context) => {
                            const item = top15[context.dataIndex];
                            return `Citations: ${item.citations.toLocaleString()} | URLs: ${item.unique_urls.toLocaleString()}`;
                        }
                    }
                }
            },
            scales: {
                x: { beginAtZero: true }
            }
        }
    });
}
```

#### Wiring It Up

Added to the `loadDashboard()` function's `Promise.all`:

```javascript
Promise.all([
    // ... existing fetches ...
    fetchSamsungCountryCitations()
]).then(([..., samsungCountryData]) => {
    // ... existing renders ...
    renderSamsungCountryChart(samsungCountryData);
});
```

#### Plain English
The JavaScript does three things:
1. **Asks the database** for the citation counts per Samsung site
2. **Decides on colors:** US site gets the prominent Samsung blue, other country sites get a lighter purple, and subdomains get gray
3. **Draws a horizontal bar chart** where each bar represents a Samsung site, and the bar length shows how many times it was cited

---

### Part 4: Visual Design Decisions

#### Color Coding Logic

| Site Type | Color | Hex Code | Rationale |
|-----------|-------|----------|-----------|
| `/us/` (US site) | Samsung Blue | #1428A0 | Primary target market - deserves visual emphasis |
| Other countries (`/uk/`, `/de/`, etc.) | Light Purple | #8091df | Related to main brand but secondary importance |
| Subdomains (`design`, `developer`, etc.) | Gray | #9e9e9e | Supporting sites, different content category |

#### Why Horizontal Bars?
- Country codes like "/us/" are short labels that read better on the left
- Long bars extending right create clear visual comparison
- Matches other dashboard charts for consistency

#### Top 15 Limit
With potentially 50+ Samsung sites globally, showing all would be overwhelming. Top 15 captures the most significant patterns while keeping the chart readable.

#### Plain English
The US site bar stands out in bold blue because that is what we care about most for US market analysis. Other country sites are purple (still Samsung family, but less important here). Subdomains are gray because they are different types of content entirely. This color scheme lets you spot the key insight immediately: "Is the blue bar the longest?"

---

### Part 5: Sample Results

Based on the current data:

| Site | Citations | Unique URLs |
|------|-----------|-------------|
| `/us/` | 10,180 | 847 |
| `/uk/` | 2,341 | 312 |
| `/de/` | 1,892 | 256 |
| `developer` | 1,456 | 89 |
| `/au/` | 1,234 | 178 |
| `design` | 987 | 45 |
| `/in/` | 876 | 134 |
| `news` | 654 | 32 |
| ... | ... | ... |

#### Insights from This Data
1. **US site dominates (good):** At 10,180 citations, the US site is cited 4x more than the next highest
2. **UK and Germany are secondary:** Expected for English-language and major European markets
3. **Developer subdomain is notable:** Suggests AI models are citing SDK/API documentation in response to TV queries - potential content gap or misattribution

#### Plain English
The numbers show that AI models are mostly citing the US Samsung site when answering US user questions - that is good. But they are also citing the UK, German, and Australian sites fairly often, which might mean content is missing from the US site. The developer subdomain appearing high on the list is surprising and worth investigating.

---

### Files Modified

| File | Changes |
|------|---------|
| `clients/samsung/dashboards/geo-dashboard.html` | Added chart section HTML; added `samsungCountryChart` variable; added `fetchSamsungCountryCitations()` function; added `renderSamsungCountryChart()` function; updated `loadDashboard()` Promise.all |

### Supabase Changes

| Change Type | Item |
|-------------|------|
| Created | `get_samsung_country_citations()` RPC function - extracts country codes/subdomains from samsung.com URLs, returns citation and unique URL counts |

---

### Lessons Learned

1. **URL parsing in SQL is powerful:** Using PostgreSQL regex functions (`~`, `substring`) allows extracting patterns directly in the database query, avoiding the need to process URLs in JavaScript.

2. **Color coding conveys meaning:** Instead of using arbitrary colors, mapping colors to categories (target market vs. other countries vs. subdomains) makes the chart self-explanatory.

3. **Tooltips add depth:** Showing both citation count AND unique URL count in the tooltip provides context - a site could have high citations but few pages (one page cited many times) or many pages (broad content being cited).

---

## 2026-01-30 (Session 10): Topics Tree Table UI Improvement

### Session Goals
Replace the basic "Top Topics by Mentions" bar chart with a more informative expandable tree table that shows the full topic hierarchy (categories and their child tags) with all available metrics. Remove redundant sections to simplify the dashboard.

---

### Part 1: The Problem - Bar Chart Limitations

#### What Was Wrong
The existing "Top Topics by Mentions" section used a horizontal bar chart (Chart.js) that showed only 4 bars - one for each category (TV Features, TV Models, TV Reviews & Brand, TV Sizes). This had several limitations:

1. **No tag-level detail:** Users could see "TV Features" had X mentions but could not see which specific tags (like "Smart TV Features" or "Picture Quality") drove those numbers
2. **Only one metric:** The bar chart showed mention counts but not citations, unique sources, or sentiment breakdown
3. **No drill-down:** Users had to look at a separate "Sources by Topic with Sentiment" table to see tag-level data, which was confusing

#### Plain English
Imagine a restaurant menu that only shows "Appetizers: 12 items" and "Main Courses: 20 items" without listing what those items are. You know how many dishes exist in each category, but you cannot see what they are. The old bar chart was like that - it showed category totals but hid the interesting details underneath.

---

### Part 2: The Solution - Expandable Tree Table

#### What We Built
A tree table that shows topic data in a collapsible hierarchy:

```
[+] TV Features (3,245 prompts | 12,456 citations | 89 sources | 72% positive)
    ├── Smart TV Features (1,234 prompts | 5,678 citations | 45 sources | 68% positive)
    ├── Picture Quality (987 prompts | 4,321 citations | 32 sources | 81% positive)
    └── Sound Features (1,024 prompts | 2,457 citations | 28 sources | 65% positive)

[+] TV Models (2,890 prompts | 9,876 citations | 67 sources | 78% positive)
    ├── OLED TVs (1,456 prompts | 5,432 citations | 34 sources | 82% positive)
    └── ...
```

#### Key Features
- **Collapsed by default:** Shows clean overview with just 4 category rows
- **Click to expand:** Click a category to reveal its child tags
- **Expand All / Collapse All buttons:** Quick way to see everything or reset view
- **Full metrics:** Every row shows prompt count, citations, unique sources, and sentiment percentages
- **Color-coded sentiment:** Positive (green), neutral (gray), negative (red) percentages

#### Plain English
The new tree table is like a file explorer on your computer. You see top-level folders (categories) at first, and you can click to expand them and see the files (tags) inside. Each row shows all the important numbers so you can compare tags at a glance without clicking around.

---

### Part 3: Database Changes

#### New Table: `summary_topics_tree`

This table stores pre-computed metrics for each category and tag combination:

| Column | Type | Description |
|--------|------|-------------|
| `category` | text | The parent category (e.g., "TV Features") |
| `tag` | text | The specific tag within the category (e.g., "Smart TV Features") |
| `prompt_count` | integer | Number of unique prompts related to this tag |
| `citations` | integer | Total citation count |
| `unique_sources` | integer | Number of distinct sources citing this tag |
| `positive_pct` | decimal | Percentage of positive sentiment |
| `neutral_pct` | decimal | Percentage of neutral sentiment |
| `negative_pct` | decimal | Percentage of negative sentiment |

#### New RPC Function: `get_topics_tree_data()`

A simple function that returns all rows from `summary_topics_tree` ordered by category and tag:

```sql
CREATE OR REPLACE FUNCTION get_topics_tree_data()
RETURNS TABLE (
    category text,
    tag text,
    prompt_count integer,
    citations integer,
    unique_sources integer,
    positive_pct decimal,
    neutral_pct decimal,
    negative_pct decimal
) AS $$
BEGIN
    RETURN QUERY
    SELECT * FROM summary_topics_tree
    ORDER BY category, tag;
END;
$$ LANGUAGE plpgsql;
```

#### Plain English
Instead of calculating topic metrics on every page load (which would query 249,000 rows), we pre-calculate the numbers and store them in a summary table. When the dashboard loads, it just reads from this small summary table - like reading from a cheat sheet instead of re-doing all the math from scratch.

---

### Part 4: JavaScript Changes

#### Functions Removed

These functions were part of the old implementation and are no longer needed:

```javascript
// OLD - Fetched topic/source data for the separate table
function fetchSourcesByTopic(date, tag) { ... }

// OLD - Rendered the separate "Sources by Topic with Sentiment" table
function renderSourcesByTopicTable(data) { ... }

// OLD - Added sorting to the separate table columns
function setupSourcesByTopicSorting() { ... }

// OLD - Rendered the Chart.js bar chart
function renderTopicsChartFromData(topicsData) { ... }
```

#### Functions Added

```javascript
// NEW - Fetches tree data from Supabase RPC
async function fetchTopicsTreeData() {
    const { data, error } = await supabase.rpc('get_topics_tree_data');
    return data;
}

// NEW - Renders the tree table HTML
function renderTopicsTree(data) {
    // Groups data by category
    // Creates category rows (with expand icons)
    // Creates tag rows (hidden by default)
    // Appends to #topics-tree-container
}

// NEW - Toggles a category's expanded/collapsed state
function toggleTopicCategory(categoryName) {
    // Finds all tag rows for this category
    // Shows or hides them
    // Updates the expand icon (+/-)
}

// NEW - Expands all categories at once
function expandAllTopics() {
    document.querySelectorAll('.topic-tag-row').forEach(row => {
        row.style.display = 'table-row';
    });
    // Update all icons to "-"
}

// NEW - Collapses all categories at once
function collapseAllTopics() {
    document.querySelectorAll('.topic-tag-row').forEach(row => {
        row.style.display = 'none';
    });
    // Update all icons to "+"
}
```

#### Plain English
We removed 4 functions that powered the old bar chart and separate table. We added 5 new functions that power the tree table:
- One function gets the data from the database
- One function draws the table on the page
- Three functions handle user interactions (expand one, expand all, collapse all)

---

### Part 5: CSS Changes

#### New Styles Added

```css
/* Category rows - bold, clickable, has expand icon */
.topic-category-row {
    font-weight: bold;
    cursor: pointer;
    background-color: #f8f9fa;
}

.topic-category-row:hover {
    background-color: #e9ecef;
}

/* Tag rows - indented, initially hidden */
.topic-tag-row {
    display: none;  /* Hidden until category expanded */
}

.topic-tag-row td:first-child {
    padding-left: 32px;  /* Indent to show hierarchy */
}

/* Expand/collapse icon (+/-) */
.expand-icon {
    display: inline-block;
    width: 20px;
    font-family: monospace;
    color: #6c757d;
}
```

#### Plain English
The CSS makes category rows stand out (bold, gray background) and clickable (cursor changes on hover). Tag rows are hidden by default and indented to show they belong under a category. The expand icon (+/-) uses a fixed-width font so the plus and minus signs take up the same space.

---

### Part 6: Section Removal

#### Removed: "Sources by Topic with Sentiment" Section

This section had a table showing sources (domains) filtered by the selected topic, with sentiment breakdown. It has been removed because:

1. **Redundant:** The new tree table shows sentiment percentages per tag
2. **Confusing:** Having two topic-related sections was confusing ("which one do I look at?")
3. **Limited value:** The source-level detail is available in other sections (Citation Sources, Domain Sentiment)

#### Plain English
We had two sections both trying to answer "how are topics performing?" - one with a chart and one with a table. The new tree table combines both into a single, clearer view. Less is more.

---

### Files Modified

| File | Changes |
|------|---------|
| `clients/samsung/dashboards/geo-dashboard.html` | Replaced Topics bar chart with tree table; removed Sources by Topic section; added 5 new JavaScript functions; added 4 new CSS classes |

### Supabase Changes

| Change Type | Item |
|-------------|------|
| Created | `summary_topics_tree` table with columns: category, tag, prompt_count, citations, unique_sources, positive_pct, neutral_pct, negative_pct |
| Created | `get_topics_tree_data()` RPC function |

---

### Lessons Learned

1. **Pre-computed summaries enable rich UI:** Without the `summary_topics_tree` table, displaying all these metrics would require complex JOINs across 249K rows. Pre-computing allows instant loading.

2. **Combine related visualizations:** Having a bar chart AND a separate table for the same data (topics) was confusing. A single tree table that shows hierarchy AND metrics is clearer.

3. **Collapsed-by-default is user-friendly:** Showing all data at once overwhelms users. Letting them expand categories they care about keeps the UI clean while preserving access to details.

4. **Remove before adding:** Before building the tree table, we removed the redundant section. This prevented the dashboard from getting even more cluttered during development.

---

## 2026-01-30 (Session 9): PR Action Center Fixes and Cited URLs Supabase Migration

### Session Goals
Fix broken filters in the PR Action Center and migrate the Cited URLs table from the SEMrush API proxy to direct Supabase queries for better performance and filtering capabilities.

---

### Part 1: The Problem - PR Action Center Filters Not Working

#### What Was Wrong
The PR Action Center filters were broken because of Supabase function issues:

1. **Missing `date` field in return type:** The `get_negative_quotes` function was not returning the `date` field, which meant the quotes table could not show when each quote was recorded.

2. **Ambiguous function overloads:** PostgreSQL had multiple versions of the same functions with different parameter signatures:
   - `get_negative_quotes(integer, text, text)` (old version)
   - `get_negative_quotes(p_limit integer, p_offset integer, ...)` (new version)
   - `get_concept_sentiment_summary(integer)` (old version)
   - `get_concept_sentiment_summary(p_limit integer, p_tag text)` (new version)

   When the dashboard called these functions, PostgreSQL could not determine which version to use, resulting in "ambiguous function call" errors.

#### Plain English
Imagine you have two phone numbers for the same person - one is their old number and one is their new number. If you try to call them without specifying which number, your phone does not know which one to dial. Similarly, the database had old and new versions of the same functions, and when the dashboard tried to call them, the database did not know which version to use.

#### The Solution
1. Added `date` field to the return type of `get_negative_quotes`
2. Dropped the old function overloads:
   - `DROP FUNCTION get_negative_quotes(integer, text, text)`
   - `DROP FUNCTION get_concept_sentiment_summary(integer)`

Now only the new, correct versions of the functions exist, and the database knows exactly which one to call.

---

### Part 2: Migrating Cited URLs from SEMrush API to Supabase

#### The Previous Architecture
```
Dashboard -> Supabase Edge Function (semrush-proxy) -> SEMrush API -> Response
```

The Cited URLs table fetched data from the SEMrush API through a proxy Edge Function. This had several limitations:
- **Latency:** Every request went through the proxy to SEMrush
- **Limited Filtering:** Could only filter by what SEMrush API supported
- **No Pagination:** Had to fetch all results and paginate client-side

#### The New Architecture
```
Dashboard -> Supabase RPC -> semrush_prompt_urls table -> Response
```

The data already exists in the `semrush_prompt_urls` table (249K rows). Querying it directly via Supabase RPC is faster and more flexible.

#### Plain English
Instead of asking a middleman (the proxy) to call SEMrush every time, we now ask our own database directly. The data is already there - we loaded it previously - so there is no need to keep fetching it from SEMrush. It is like having a book on your shelf versus going to the library every time you want to read it.

---

### Part 3: New Supabase Functions for Cited URLs

#### Functions Created

**1. `get_cited_urls(p_limit, p_offset, p_date_from, p_date_to, p_tag, p_domain_type, p_domain)`**

Returns aggregated URL data with filtering and pagination:
- `p_limit` / `p_offset`: Pagination parameters
- `p_date_from` / `p_date_to`: Date range filter
- `p_tag`: Topic filter (joins with `tv_topics` table)
- `p_domain_type`: Filter by Owned/Earned/Competitors/Other
- `p_domain`: Filter by specific domain

Returns: url, domain, domain_type, citations, mentions, visibility_pct

**2. `get_cited_urls_count(p_date_from, p_date_to, p_tag, p_domain_type, p_domain)`**

Returns the total count of URLs matching the filter criteria. Used for pagination to show "Page 1 of 17" style navigation.

**3. `get_top_cited_domains(p_limit)`**

Returns the top domains by citation count, grouped by domain type. Used to populate the domain filter dropdown with options like:
- Earned: rtings.com (1,234), techradar.com (987)
- Competitors: lg.com (543), sony.com (321)

#### Plain English
We created three helper functions in the database:
1. **Get the data:** Fetch URLs with all the filters applied, 15 at a time
2. **Count the total:** Tell us how many URLs match so we can show page numbers
3. **Get domain list:** Show which domains have data so users can filter by them

---

### Part 4: New JavaScript Functions in geo-dashboard.html

#### Functions Added

```javascript
// Fetch paginated URL data from Supabase
async function fetchCitedUrls(limit, offset) {
    // Calls get_cited_urls RPC with current filter state
    // Returns: { data: [...], error: null }
}

// Fetch total count for pagination
async function fetchCitedUrlsCount() {
    // Calls get_cited_urls_count RPC
    // Returns: { count: 247, error: null }
}

// Populate domain filter dropdown
async function loadCitedUrlsDomainFilter() {
    // Calls get_top_cited_domains RPC
    // Groups results by domain_type in dropdown
}

// Reload table when filters change
function reloadCitedUrls() {
    // Resets to page 1 and fetches fresh data
}

// Handle pagination clicks
function changeCitedUrlsPage(direction) {
    // direction: 'prev' or 'next'
    // Updates current page and fetches new data
}
```

#### Plain English
These are the functions that make the Cited URLs table interactive:
- When you change a filter, the table reloads with matching data
- When you click "Next Page", it shows the next 15 URLs
- When you pick a domain from the dropdown, it only shows URLs from that domain

---

### Part 5: Filters and Pagination Added

#### Filter Hierarchy

**Global Filters (affect multiple sections):**
- Date Range: Last 7 days, 14 days, 30 days, Custom
- Topic: TV Features, TV Models, TV Reviews, etc.
- Domain Type: Owned, Earned, Competitors, Other

**Section-Level Filter (Cited URLs only):**
- Domain: Top 30 domains grouped by type

#### Pagination
- 15 items per page
- Shows: "Page 1 of 17"
- Previous/Next buttons
- Resets to page 1 when filters change

#### Plain English
The table now responds to the same filters as other sections (date range, topic, domain type), plus it has its own domain filter for drilling down. Instead of showing all 249K URLs at once (which would crash the browser), it shows 15 at a time with buttons to see more.

---

### Files Modified

| File | Changes |
|------|---------|
| `clients/samsung/dashboards/geo-dashboard.html` | Added 5 new JavaScript functions, domain filter dropdown, pagination controls |

### Supabase Changes

| Change Type | Item |
|-------------|------|
| Fixed | `get_negative_quotes` return type now includes `date` field |
| Dropped | `get_negative_quotes(integer, text, text)` old overload |
| Dropped | `get_concept_sentiment_summary(integer)` old overload |
| Created | `get_cited_urls(p_limit, p_offset, p_date_from, p_date_to, p_tag, p_domain_type, p_domain)` |
| Created | `get_cited_urls_count(...)` |
| Created | `get_top_cited_domains(p_limit)` |

---

### Lessons Learned

1. **PostgreSQL function overloading is tricky:** Unlike some languages where you can have multiple functions with the same name but different parameters, PostgreSQL matches by parameter count first, then by type. Having old and new versions of the same function causes "ambiguous function call" errors. Best to drop old versions when creating new ones.

2. **Proxy data you already have is wasteful:** If the data already exists in your database (249K rows in `semrush_prompt_urls`), there is no need to fetch it from an external API every time. Query your own database directly.

3. **Section-level filters reduce global filter clutter:** Not every filter needs to be in the global filter bar. If a filter only affects one section (like domain filtering for Cited URLs), put it in that section.

---

## 2026-01-30 (Session 8): Data Definitions Page Restructured for GEO Dashboard

### Session Goals
Bring the data definitions documentation page into alignment with the actual GEO Dashboard metrics, replacing outdated placeholder content with accurate definitions.

---

### Part 1: The Problem - Outdated Documentation

#### What Was Wrong
The `clients/samsung/dashboards/data-definitions.html` file contained metric definitions from an earlier dashboard design that no longer existed:

**Old Sections (Removed):**
- Dual-Metric KPIs (Prompt Mentions, Top Product Position, Products Win/Lose, Position Distribution)
- Prompt Tracking Metrics (Topic Volume, Visibility Score, Position, Position Change)
- Position Metrics (Average Position, Top 3 Rate)

These sections contained placeholder text like `[TBD]` and `[Description to be provided]`, and the metrics described did not appear anywhere in the live GEO Dashboard.

#### Plain English
Imagine you have a user manual for a car, but the manual describes a different model. It mentions features your car does not have and ignores features it does have. Someone trying to understand the dashboard by reading this documentation would be confused - the metrics they see on screen would not match what the documentation describes.

---

### Part 2: New Structure Matching Live Dashboard

#### What Was Added
Created 7 new metric sections that match exactly what appears in the GEO Dashboard:

**1. Primary KPIs**
| Metric | Formula | Description |
|--------|---------|-------------|
| Share of Voice | `(Samsung Mentions / Total Brand Mentions) x 100` | Percentage of all AI mentions that reference Samsung |
| Visibility Score | `(Cited URLs / Total Tracked URLs) x 100` | How often Samsung URLs appear in AI responses |
| Sentiment Score | `((Positive - Negative) / Total Mentions) x 100` | Net sentiment balance |
| Total Mentions | Count of all Samsung mentions | Raw volume metric |

**2. Domain Sentiment Analysis**
- Sentiment by Domain (how positive/negative is coverage on RTINGS vs TechRadar vs CNET)
- Domain Type Breakdown (Owned vs Earned vs Competitor sentiment)
- Domain Performance Summary (overall domain metrics)

**3. Citation Metrics**
- Citations (number of times Samsung URLs are cited)
- Mentions (number of times Samsung brand is mentioned)
- Visibility % (citation rate across all prompts)
- URLs Cited (unique Samsung URLs appearing in AI responses)

**4. Concept Analysis**
- Concept Mentions (how often each topic like "picture quality" or "price" appears)
- Top Positive/Negative Concepts (which topics drive positive/negative sentiment)
- Concept Sentiment Mix (positive/neutral/negative breakdown per concept)

**5. Platform Metrics**
- Platform Mentions (mentions per AI model)
- Platform Trend (how mentions change over time per model)
- AI Model Pills: ChatGPT, Google AI Overview, Google AI Mode

**6. Trend Metrics**
- Mentions Over Time (daily/weekly visibility trends)
- Period Comparison (current period vs previous period)

**7. PR Action Center**
- Negative Quotes (actual negative statements from AI responses)
- Negative Concept Frequency (which topics generate the most negative coverage)
- Prompts with Negative Quotes (which questions trigger negative responses)

#### Plain English
The documentation now describes exactly what users see. When someone looks at the "Share of Voice" KPI on the dashboard, they can look it up in the documentation and find: what it means, how it is calculated, and where the data comes from.

---

### Part 3: Understanding the Data Section

#### What Was Added
A new "Understanding the Data" section with info boxes explaining key concepts:

**1. Mentions vs Citations**
- **Mentions:** When an AI model references Samsung by name in its response
- **Citations:** When an AI model includes a Samsung URL as a source

**2. Sentiment Classification**
How Semrush determines if a mention is positive, neutral, or negative. Based on the surrounding context and language used.

**3. Data Freshness**
When the data updates (typically daily from Semrush API).

**4. Position/Ranking**
How ranking is calculated when Samsung appears in a list of recommendations.

**5. AI Model Coverage**
Which AI platforms are tracked: ChatGPT, Google AI Overview, Google AI Mode.

#### Plain English
These info boxes answer the questions that non-technical stakeholders ask:
- "What is the difference between a mention and a citation?"
- "How does the system know if something is negative?"
- "How often does the data update?"
- "Which AI assistants are we tracking?"

Without this section, users would need to ask these questions repeatedly, or worse, misinterpret the data.

---

### Part 4: Formula Accuracy

#### Technical Implementation
Ensured all documented formulas match the actual JavaScript calculations in `supabase-data.js`:

```javascript
// Share of Voice calculation (from supabase-data.js)
const shareOfVoice = (samsungMentions / totalBrandMentions) * 100;

// Visibility Score calculation
const visibilityScore = (citedUrls / totalTrackedUrls) * 100;

// Sentiment Score calculation
const sentimentScore = ((positive - negative) / totalMentions) * 100;
```

The data definitions page now documents these exact formulas, so developers can verify calculations and stakeholders can understand what they mean.

#### Plain English
When you look up "Visibility Score" in the documentation, the formula you see is the exact formula used in the code. There is no gap between what the documentation says and what the dashboard actually does.

---

### Part 5: Navigation and Polish

#### What Was Fixed
- **Back Link:** Changed from pointing to `scom-overview.html` (old dashboard) to `geo-dashboard.html` (current dashboard)
- **Table of Contents:** Completely rewritten to list the 7 new sections with working anchor links
- **Data Source Badges:** Standardized to show "Semrush" as the data source (previously had inconsistent or missing badges)
- **Placeholders Removed:** All `[TBD]` and `[Description to be provided]` text replaced with actual content

#### Plain English
Small fixes that improve usability:
- Clicking "Back to Dashboard" now takes you to the right page
- The table of contents actually matches the sections on the page
- Every metric shows where its data comes from (Semrush)
- No more placeholder text that makes the documentation look unfinished

---

### Files Modified

| File | Changes |
|------|---------|
| `clients/samsung/dashboards/data-definitions.html` | Complete restructure with new sections, formulas, and explanatory content |

---

### Session Summary

**What Changed:** The data definitions documentation page was completely restructured to match the live GEO Dashboard. Old placeholder sections were removed, new accurate sections were added, formulas were verified against actual code, and explanatory content was added for non-technical users.

**Why It Matters:** Documentation that does not match the product causes confusion and undermines trust. Stakeholders looking up metrics now find accurate definitions that match what they see on screen.

**Lesson Learned:** Documentation should be updated whenever the dashboard changes. The gap between the old data-definitions.html and the live dashboard had grown because documentation updates were deferred during rapid development.

---

## 2026-01-30 (Session 7): Data Context, KPI Changes, Topic Filter, and Deployment

### Session Goals
Add transparency about data coverage and measurement limitations, implement period-over-period change indicators for KPIs, add topic filtering capability to more dashboard sections, and deploy updates to production.

---

### Part 1: Data Coverage Section

#### What Was Added
A new "Data Coverage" section after the KPI cards showing the scope of data being tracked:

- **36,765 Samsung prompts** - From Semrush's database of 250M+ prompts
- **383 tracked prompts** - Focused specifically on TV-related queries
- **3 AI surfaces monitored** - ChatGPT, Google AI Overview, Google AI Mode

#### Plain English
Users viewing the dashboard need context about what data they're seeing. This section answers: "How much of the AI conversation are we actually tracking?" The answer is: a focused sample of TV-related questions across three major AI platforms, drawn from Semrush's massive database of AI prompts.

---

### Part 2: Measurement Caveats (Amber Box)

#### What Was Added
An amber-colored box documenting the limitations of the data:

1. **Sample-based tracking** - We track a subset of possible questions, not every question ever asked
2. **Surface coverage gaps** - Missing Perplexity, Claude, Copilot, and other AI platforms
3. **Response variability** - The same prompt can return different answers each time
4. **Prompt diversity** - Users phrase questions infinitely different ways

#### Why This Matters
Stakeholders might assume "36,765 prompts" means comprehensive coverage. The caveats explain why AI visibility is fundamentally harder to measure than traditional search - AI responses are probabilistic, not deterministic.

#### Plain English
This is like a disclaimer on a survey: "We asked 1,000 people." You need to know the sample size and limitations to interpret results correctly. For AI visibility:
- We're tracking 3 AI platforms, but there are many more (Perplexity, Claude's chat, Microsoft Copilot)
- Even if we ask the same question twice, we might get different brand mentions
- People ask about TVs in thousands of different ways we might not track

---

### Part 3: Improving Measurement (Green Box)

#### What Was Added
A green-colored box with future measurement enhancement paths:

1. **Model probing** - Directly querying AI models to understand brand positioning
2. **Model mechanistic interpretability analysis** - Understanding why models say what they say
3. **Adobe Analytics referral analysis** - Tracking traffic from AI surfaces to Samsung.com
4. **Adobe Analytics user journey tracking** - Understanding how AI-referred visitors behave

#### Plain English
This tells stakeholders "we know the limitations, and here's how we plan to get better data." It's a roadmap for improving measurement, not just acknowledging problems.

---

### Part 4: KPI Change Indicators

#### Technical Implementation
Updated `calculateKPIs()` function to compute period-over-period changes:

```javascript
// Split data into two periods
const midpoint = Math.floor(filteredData.length / 2);
const firstHalf = filteredData.slice(0, midpoint);
const secondHalf = filteredData.slice(midpoint);

// Calculate metrics for each period
const firstHalfMetrics = calculatePeriodMetrics(firstHalf);
const secondHalfMetrics = calculatePeriodMetrics(secondHalf);

// Compute percentage changes
const changes = {
    citationShare: ((secondHalfMetrics.citationShare - firstHalfMetrics.citationShare) / firstHalfMetrics.citationShare) * 100,
    avgPosition: ((secondHalfMetrics.avgPosition - firstHalfMetrics.avgPosition) / firstHalfMetrics.avgPosition) * 100,
    // ... etc
};
```

Updated `updateKPICard()` to display change badges:

```javascript
function updateKPICard(cardId, value, change) {
    const card = document.getElementById(cardId);
    const valueEl = card.querySelector('.kpi-value');
    const changeEl = card.querySelector('.kpi-change');

    valueEl.textContent = formatValue(value);

    if (change !== null && change !== undefined) {
        const isPositive = change > 0;
        changeEl.textContent = `${isPositive ? '+' : ''}${change.toFixed(1)}%`;
        changeEl.className = `kpi-change ${isPositive ? 'positive' : 'negative'}`;
        changeEl.style.display = 'inline-block';
    } else {
        changeEl.style.display = 'none';
    }
}
```

#### Plain English
KPIs now show whether things are getting better or worse. If citation share went from 15% to 18%, you'll see "18%" with a green "+20%" badge. This helps stakeholders quickly spot trends without digging into the data.

The "period" is determined by splitting the current date range in half - if you're looking at the last 30 days, it compares days 1-15 to days 16-30.

---

### Part 5: Topic Filter Support

#### What Was Added
The topic filter (e.g., "8K TVs", "OLED", "Gaming") now filters more dashboard sections:

**New RPC Function Parameters:**
- `get_negative_quotes` - Added `p_tag` parameter
- `get_concept_sentiment_summary` - Added `p_tag` parameter

**New RPC Functions:**
- `get_prompts_by_tag(p_tag)` - Returns prompts matching a tag
- `get_domain_sentiment_by_tag(p_tag)` - Returns domain sentiment filtered by tag

**Sections Now Filtered by Topic:**
- Negative Quotes (PR Action Center)
- Concept Sentiment
- Citation Sources
- Cited URLs

**Sections NOT Yet Filtered:**
- KPIs (would need pre-computed summary tables per tag)
- Domain Sentiment (slow for filtered queries; pre-computation needed)

#### Technical Challenge
The `get_domain_sentiment_by_tag` function works but is slow because it can't use pre-computed summary tables. For real-time filtering, we'd need to create `summary_domain_sentiment_by_tag` tables with pre-aggregated data for each tag combination.

#### New JavaScript Function

```javascript
async function fetchPromptsByTag(tag) {
    const response = await fetch(
        `${SUPABASE_URL}/rest/v1/rpc/get_prompts_by_tag`,
        {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                apikey: SUPABASE_ANON_KEY
            },
            body: JSON.stringify({ p_tag: tag })
        }
    );
    return response.json();
}
```

#### Plain English
Previously, changing the "Topic" dropdown only affected some charts. Now, most sections respond to topic selection:
- Select "8K TVs" and the negative quotes show only 8K-related criticisms
- The concept sentiment shows concepts mentioned in 8K TV prompts
- Citation sources show which domains are cited when discussing 8K

Some sections (KPIs, Domain Sentiment) still show all-topic data because filtering them in real-time would be too slow. This would require building pre-computed summary tables for every topic combination.

---

### Part 6: Hisense Brand Color Fix

#### What Changed
Updated Hisense brand color from `#00A0DF` (blue) to `#00a4a0` (teal).

#### Why
The previous color was Samsung-style blue, which created visual confusion in competitor comparison charts. Hisense's actual brand color is a teal/cyan, making it visually distinct from Samsung.

---

### Part 7: Production Deployment

#### What Was Deployed
All changes pushed to DigitalOcean server via standard deployment process.

#### Production URL
https://robotproof.io/samsung/ai-visibility/geo-dashboard.html

#### Plain English
The dashboard is now live and accessible to Samsung stakeholders. Changes include the data context section, measurement caveats, KPI change indicators, and topic filtering.

---

### Session Summary

| Category | Items |
|----------|-------|
| New Sections | Data Coverage, Measurement Caveats, Improving Measurement |
| Enhanced Features | KPI change indicators, Topic filter support |
| Bug Fixes | Hisense brand color |
| New RPC Functions | `get_prompts_by_tag`, `get_domain_sentiment_by_tag` |
| Updated RPC Functions | `get_negative_quotes` (p_tag), `get_concept_sentiment_summary` (p_tag) |
| Deployment | https://robotproof.io/samsung/ai-visibility/geo-dashboard.html |

### Files Modified

- `clients/samsung/dashboards/geo-dashboard.html` - All UI and JavaScript changes
- Supabase migrations for RPC function updates

### Lessons Learned

1. **Transparency builds trust** - Showing data limitations alongside data makes stakeholders trust the data more, not less
2. **Pre-computation vs real-time** - Some filters are too slow without pre-computed summary tables; decide upfront which filter combinations to support
3. **Period-over-period requires data** - Change indicators only work when there's enough data to split into two periods; hide the badge when data is insufficient

---

## 2026-01-30 (Session 6): PR Action Center Fixes and Domain Filter Feature

### Session Goals
Fix the PR Action Center which was showing only 1 concept with duplicate quotes, and add domain filtering capability so users can see negative quotes from specific sources.

---

### Part 1: The Problem - Cartesian Join Bug

#### What Was Happening
The PR Action Center was supposed to show the top negative concepts and their quotes. Instead, it showed:
- Only 1 concept: "interface"
- The same quote repeated 20 times (once for each domain)

#### Technical Root Cause
The `get_negative_quotes` Supabase RPC function had a problematic JOIN chain:

```sql
-- BROKEN: This creates a cartesian product
SELECT DISTINCT cp.concept, cp.quote, d.domain
FROM semrush_concept_prompts cp
JOIN semrush_prompt_urls pu ON cp.prompt = pu.prompt
JOIN domains d ON pu.url LIKE '%' || d.domain || '%'
WHERE cp.sentiment = 'negative'
```

The problem:
1. One prompt can appear in `semrush_prompt_urls` many times (once per URL)
2. One prompt can appear in `semrush_concept_prompts` many times (once per concept)
3. Multiple URLs can match the same domain
4. Result: 1 quote x 20 domains = 20 duplicate rows

#### Plain English
Imagine you have a quote from a restaurant review. That review appears on 20 different food websites. When the database tried to find "negative quotes from a specific domain," it joined every quote with every website, creating 20 copies of each quote. The DISTINCT keyword was supposed to remove duplicates, but it couldn't because each row had a different domain attached.

It's like asking "show me all the reviews from Yelp" and getting back every review 20 times because the database was confused about which website each review came from.

---

### Part 2: The Data Reality

#### What We Actually Have (verified via Supabase MCP)
- **4,308 unique negative quotes** in `semrush_concept_prompts`
- **919 unique negative concepts** (product features that got criticized)
- Top negative concepts by mention count:
  - remote control: 188 negative mentions
  - price: 172 negative mentions
  - contrast: 157 negative mentions
  - viewing angles: 139 negative mentions

#### Plain English
There's plenty of negative feedback data - almost 1,000 different product features that AI models have criticized, with over 4,300 actual negative quotes. The problem wasn't missing data; it was the query returning duplicates instead of unique quotes.

---

### Part 3: The Fix - Rewritten RPC Function

#### Technical Solution
Rewrote `get_negative_quotes` to:
1. Query `semrush_concept_prompts` directly (no unnecessary JOINs)
2. Use DISTINCT to get unique quotes
3. Add optional `p_domain` parameter
4. Use EXISTS subquery for domain filtering (no cartesian product)

```sql
CREATE OR REPLACE FUNCTION get_negative_quotes(
    p_limit INT DEFAULT 100,
    p_domain TEXT DEFAULT NULL
)
RETURNS TABLE (
    concept TEXT,
    quote TEXT,
    prompt TEXT,
    sentiment TEXT
)
AS $$
BEGIN
    RETURN QUERY
    SELECT DISTINCT
        cp.concept,
        cp.quote,
        cp.prompt,
        cp.sentiment
    FROM semrush_concept_prompts cp
    WHERE cp.sentiment = 'negative'
      AND cp.quote IS NOT NULL
      AND cp.quote != ''
      AND (p_domain IS NULL OR EXISTS (
          SELECT 1 FROM semrush_prompt_urls pu
          WHERE pu.prompt = cp.prompt
            AND pu.url LIKE '%' || p_domain || '%'
      ))
    ORDER BY cp.concept
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;
```

#### Why EXISTS Instead of JOIN
- JOIN: "Give me all combinations of quotes and URLs" (multiplicative)
- EXISTS: "Does at least one URL match this domain?" (yes/no filter)

EXISTS returns a boolean, not rows. It doesn't multiply the result set.

#### Plain English
The old query said "connect every quote to every URL to every domain" which created thousands of connections. The new query says "for each quote, check if it appears on at least one URL from this domain - if yes, include it once."

It's the difference between "list everyone at the party who knows someone from Texas" (list each person once) versus "list every connection between partygoers and Texans" (list the same person multiple times if they know multiple Texans).

---

### Part 4: Domain Filter Feature

#### What Was Added
A new dropdown in the PR Action Center to filter quotes by domain:

```html
<div class="filter-group">
    <label for="prDomainFilter">Filter by Domain</label>
    <select id="prDomainFilter" onchange="reloadPRActionCenter()">
        <option value="">All Domains</option>
        <optgroup label="Earned Media">
            <option value="rtings.com">rtings.com (358 negative)</option>
            <option value="techradar.com">techradar.com (245 negative)</option>
            ...
        </optgroup>
        <optgroup label="Competitors">
            <option value="lg.com">lg.com (89 negative)</option>
            ...
        </optgroup>
    </select>
</div>
```

#### JavaScript Implementation

```javascript
// Populate the domain filter dropdown
async function loadPRDomainFilter() {
    const response = await fetch(
        `${SUPABASE_URL}/rest/v1/summary_domain_sentiment?select=domain,domain_type,negative_prompts`,
        { headers: { apikey: SUPABASE_ANON_KEY } }
    );
    const domains = await response.json();

    // Group by domain type
    const grouped = {
        earned: domains.filter(d => d.domain_type === 'earned'),
        owned: domains.filter(d => d.domain_type === 'owned'),
        competitor: domains.filter(d => d.domain_type === 'competitor'),
        other: domains.filter(d => d.domain_type === 'other')
    };

    // Build optgroups
    const select = document.getElementById('prDomainFilter');
    for (const [type, list] of Object.entries(grouped)) {
        const optgroup = document.createElement('optgroup');
        optgroup.label = type.charAt(0).toUpperCase() + type.slice(1);
        list.forEach(d => {
            const option = document.createElement('option');
            option.value = d.domain;
            option.textContent = `${d.domain} (${d.negative_prompts} negative)`;
            optgroup.appendChild(option);
        });
        select.appendChild(optgroup);
    }
}

// Reload only the PR Action Center when filter changes
async function reloadPRActionCenter() {
    const domain = document.getElementById('prDomainFilter').value;
    const quotes = await fetchNegativeQuotes({ domain }, 1, 10);
    renderQuoteBrowser(quotes);
    // Also reload the charts
    const conceptData = await fetchConceptSentiment({ domain });
    renderNegativeConceptsChart(conceptData);
}
```

#### Plain English
The dropdown shows all the domains that have negative quotes, grouped by type (news sites, Samsung's own site, competitor sites, etc.). Each domain shows how many negative mentions it has, so you can quickly see which sources have the most problems.

When you select a domain, only the PR Action Center reloads - not the whole dashboard. This makes it fast to investigate specific sources.

---

### Part 5: Quote Browser Updates

#### Changes Made
1. Renamed "Domain" column to "Prompt"
2. Updated `renderQuoteBrowser()` to show the prompt that triggered the quote
3. Updated `exportQuotesToCSV()` to include the prompt column

#### Why This Change
Quotes don't come from domains - they come from AI model responses to search prompts. Showing the prompt gives actionable context: "When people search for 'best TV for gaming', AI says negative things about Samsung's remote control."

#### Technical Implementation

```javascript
function renderQuoteBrowser(quotes) {
    const table = document.getElementById('quoteBrowserTable');
    table.innerHTML = `
        <tr>
            <th>Concept</th>
            <th>Quote</th>
            <th>Prompt</th>  <!-- Changed from "Domain" -->
        </tr>
        ${quotes.map(q => `
            <tr>
                <td>${q.concept}</td>
                <td>${q.quote}</td>
                <td>${q.prompt}</td>  <!-- Changed from q.domain -->
            </tr>
        `).join('')}
    `;
}
```

#### Plain English
Before, the table showed which website the quote came from, but that was misleading because the quotes are from AI models, not from websites. Now it shows what search query triggered the negative response, which is much more useful for understanding why AI is saying negative things.

---

### Part 6: New Supabase Functions Created

#### `get_negative_quotes(p_limit, p_domain)`
- **Purpose:** Returns unique negative quotes, optionally filtered by domain
- **Parameters:**
  - `p_limit` (INT, default 100): Maximum quotes to return
  - `p_domain` (TEXT, default NULL): Domain to filter by (e.g., 'rtings.com')
- **Returns:** Table with concept, quote, prompt, sentiment columns

#### `get_concept_sentiment_summary(p_limit)`
- **Purpose:** Aggregates concepts by their sentiment counts
- **Parameters:**
  - `p_limit` (INT, default 50): Maximum concepts to return
- **Returns:** Table with concept, positive_count, neutral_count, negative_count columns

---

### Part 7: Lessons Learned

#### Lesson 1: JOINs Can Explode Row Counts
When joining tables with many-to-many relationships, the result set multiplies. If Table A has 100 rows matching Table B, and Table B has 50 rows matching Table C, you could get 100 x 50 = 5,000 rows, not 100 rows.

**Plain English:** It's like asking for everyone who went to both the party and the concert. If 10 people went to the party and 20 went to the concert, but only 5 went to both, a bad query might give you 200 combinations instead of 5 people.

#### Lesson 2: EXISTS vs JOIN for Filtering
Use EXISTS when you only need to check "does this exist?" without needing the data from the other table. EXISTS returns true/false and doesn't multiply rows.

**Plain English:** If you're checking IDs at a door, you don't need to list every person they've ever met - you just need to know "are they on the guest list?"

#### Lesson 3: Test RPC Functions via MCP First
Before assuming an RPC function works in the dashboard, test it directly using the Supabase MCP. This shows the actual data returned and helps identify issues like duplicate rows.

**Plain English:** Before serving a new dish to customers, taste it yourself in the kitchen. Don't wait for complaints.

---

### Part 8: Concept Filter Addition

#### What Was Added
A second dropdown filter in the PR Action Center, allowing users to filter quotes by concept (product feature):

```html
<div class="filter-group">
    <label for="prConceptFilter">Filter by Concept</label>
    <select id="prConceptFilter" onchange="reloadPRActionCenter()">
        <option value="">All Concepts</option>
        <option value="remote control">remote control (188 negative)</option>
        <option value="price">price (172 negative)</option>
        <option value="contrast">contrast (157 negative)</option>
        <!-- ... more concepts -->
    </select>
</div>
```

#### Supabase RPC Update
Added `p_concept` parameter to `get_negative_quotes`:

```sql
CREATE OR REPLACE FUNCTION get_negative_quotes(
    p_limit INT DEFAULT 100,
    p_domain TEXT DEFAULT NULL,
    p_concept TEXT DEFAULT NULL  -- NEW PARAMETER
)
RETURNS TABLE (
    concept TEXT,
    quote TEXT,
    prompt TEXT,
    sentiment TEXT
)
AS $$
BEGIN
    RETURN QUERY
    SELECT DISTINCT
        cp.concept,
        cp.quote,
        cp.prompt,
        cp.sentiment
    FROM semrush_concept_prompts cp
    WHERE cp.sentiment = 'negative'
      AND cp.quote IS NOT NULL
      AND cp.quote != ''
      AND (p_domain IS NULL OR EXISTS (
          SELECT 1 FROM semrush_prompt_urls pu
          WHERE pu.prompt = cp.prompt
            AND pu.url LIKE '%' || p_domain || '%'
      ))
      AND (p_concept IS NULL OR cp.concept = p_concept)  -- NEW FILTER
    ORDER BY cp.concept
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;
```

#### JavaScript Implementation

```javascript
// Populate the concept filter dropdown
async function loadPRConceptFilter() {
    // Call RPC to get concept sentiment summary
    const response = await fetch(
        `${SUPABASE_URL}/rest/v1/rpc/get_concept_sentiment_summary`,
        {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                apikey: SUPABASE_ANON_KEY
            },
            body: JSON.stringify({ p_limit: 100 })
        }
    );
    const concepts = await response.json();

    // Filter to only concepts with negative mentions
    const negativeConcepts = concepts.filter(c => c.negative_count > 0);

    // Sort by negative count descending
    negativeConcepts.sort((a, b) => b.negative_count - a.negative_count);

    // Build dropdown options
    const select = document.getElementById('prConceptFilter');
    negativeConcepts.forEach(c => {
        const option = document.createElement('option');
        option.value = c.concept;
        option.textContent = `${c.concept} (${c.negative_count} negative)`;
        select.appendChild(option);
    });
}

// Updated: Reload with both filters
async function reloadPRActionCenter() {
    const domain = document.getElementById('prDomainFilter').value;
    const concept = document.getElementById('prConceptFilter').value;

    const quotes = await fetchNegativeQuotes({ domain, concept }, 1, 10);
    renderQuoteBrowser(quotes);

    // Update filter description
    let description = `${quotes.length} quotes`;
    if (domain) description += ` for ${domain}`;
    if (concept) description += ` + '${concept}'`;
    document.getElementById('filterDescription').textContent = description;
}

// Updated: Include concept in export filename
function exportQuotesToCSV() {
    const domain = document.getElementById('prDomainFilter').value;
    const concept = document.getElementById('prConceptFilter').value;

    // Build filename
    let filename = 'samsung_negative_quotes';
    if (domain) filename += '_' + domain.replace(/\./g, '_');
    if (concept) filename += '_' + concept.replace(/\s+/g, '_');
    filename += '_' + new Date().toISOString().split('T')[0] + '.csv';

    // ... rest of export logic
}
```

#### Plain English

The concept filter is like adding a "topic" filter to a review system. Before, you could only filter by which website had negative reviews. Now you can also filter by what product feature the review is about.

For example:
- "Show me all negative quotes about the remote control" - just pick "remote control" from the concept dropdown
- "Show me what RTINGS says about the price" - pick "rtings.com" from domain AND "price" from concept
- "Export all complaints about viewing angles" - pick "viewing angles" and click Export

The filters work together, so you can narrow down to very specific questions like "What does TechRadar think about Samsung's contrast ratio?"

#### Use Cases (Business Value)

| Question | How to Answer |
|----------|--------------|
| "What does RTINGS say about our remote control?" | Domain: rtings.com, Concept: remote control |
| "All negative quotes about price across all sources" | Concept: price |
| "What are TechRadar's criticisms?" | Domain: techradar.com |
| "Export competitor criticism of our viewing angles" | Domain: lg.com (competitor), Concept: viewing angles, then Export |

---

### Files Modified

- `clients/samsung/dashboards/geo-dashboard.html` - Added domain filter, concept filter, updated Quote Browser, fixed chart labels, added loadPRConceptFilter(), updated reloadPRActionCenter() and exportQuotesToCSV()
- Supabase migrations - Created/updated `get_negative_quotes` (added p_concept parameter) and `get_concept_sentiment_summary` RPC functions

---

## 2026-01-30 (Session 5): GEO Dashboard Sentiment Analysis Enhancement

### Session Goals
Transform the Samsung GEO Dashboard (`geo-dashboard.html`) from a basic visibility dashboard into a comprehensive sentiment analysis tool by implementing the UI requirements documented in Session 3. Add new sections for domain analysis, PR action, and concept analysis with interactive filtering.

---

### Part 1: What Was Built - Overview

#### Technical Summary
Applied the UI requirements plan to `clients/samsung/dashboards/geo-dashboard.html`, adding 4 new dashboard sections with ~1100 lines of new code. The dashboard now supports sentiment-based filtering and provides actionable insights for PR teams.

#### Plain English
The dashboard went from showing "how much visibility does Samsung have?" to answering deeper questions like "which review sites are saying negative things?" and "what product features get the most complaints?" This turns raw data into actionable information for marketing and PR teams.

---

### Part 2: Enhanced Filter Bar

#### Technical Implementation
Added two new filter dropdowns to the existing sticky filter bar:

```html
<!-- Domain Type Filter -->
<select id="domainTypeFilter">
    <option value="">All Domain Types</option>
    <option value="owned">Owned (samsung.com)</option>
    <option value="earned">Earned (media sites)</option>
    <option value="competitor">Competitors</option>
    <option value="other">Other</option>
</select>

<!-- Sentiment Filter -->
<select id="sentimentFilter">
    <option value="">All Sentiments</option>
    <option value="positive">Positive</option>
    <option value="neutral">Neutral</option>
    <option value="negative">Negative</option>
</select>
```

Both filters are integrated into the `loadDashboard()` function, passing selected values to all data fetching functions.

#### Plain English
Users can now quickly filter the entire dashboard by:
- **Domain Type**: See only owned sites (samsung.com), earned media (RTINGS, TechRadar), competitor sites (LG, Sony), or other sources
- **Sentiment**: Focus on positive coverage to find strengths, or negative coverage to identify problems

This is like adding "show only good reviews" or "show only competitor mentions" buttons to the dashboard.

---

### Part 3: Domain Sentiment Analysis Section

#### What It Contains

1. **Sentiment by Domain Chart** - Horizontal stacked bar chart showing positive/neutral/negative breakdown for each domain
2. **Owned vs Earned vs Competitor Chart** - Aggregate comparison of domain types
3. **Domain Performance Summary Table** - Sortable table with all domain metrics

#### Technical Implementation

```javascript
// Fetch domain sentiment data
async function fetchDomainSentiment(filters) {
    const response = await fetch(
        `${SUPABASE_URL}/rest/v1/summary_domain_sentiment?select=*`,
        { headers: { apikey: SUPABASE_ANON_KEY } }
    );
    return response.json();
}

// Render stacked bar chart
function renderDomainSentimentChart(data) {
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: domains,
            datasets: [
                { label: 'Positive', data: positiveData, backgroundColor: '#4CAF50' },
                { label: 'Neutral', data: neutralData, backgroundColor: '#FFC107' },
                { label: 'Negative', data: negativeData, backgroundColor: '#F44336' }
            ]
        },
        options: {
            indexAxis: 'y',  // Horizontal bars
            scales: { x: { stacked: true }, y: { stacked: true } }
        }
    });
}
```

#### Plain English
This section answers questions like:
- "Which domains mention Samsung most positively?" (RTINGS has 358 positive prompts)
- "Are competitor sites more negative than review sites?"
- "How does our owned content compare to earned media?"

The stacked bars make it easy to see at a glance which sites have mostly positive coverage (long green bars) versus mostly negative coverage (long red bars).

---

### Part 4: PR Action Center Section

#### What It Contains

1. **Top Negative Concepts Chart** - Bar chart showing which product features/concepts get the most negative mentions
2. **Negative Coverage by Source Chart** - Which domains have the most negative content
3. **Quote Browser Table** - Actual negative quotes with pagination
4. **Export CSV Button** - Download quotes for PR team review

#### Technical Implementation

```javascript
// Fetch negative quotes from Supabase view
async function fetchNegativeQuotes(filters, page = 1, pageSize = 10) {
    const offset = (page - 1) * pageSize;
    const response = await fetch(
        `${SUPABASE_URL}/rest/v1/vw_sentiment_quotes?sentiment=eq.negative&order=created_at.desc&limit=${pageSize}&offset=${offset}`,
        { headers: { apikey: SUPABASE_ANON_KEY } }
    );
    return response.json();
}

// Pagination controls
function renderPagination(currentPage, totalPages, onPageChange) {
    // Creates Previous/Next buttons and page indicator
}

// CSV Export
function exportQuotesToCSV(quotes) {
    const csv = quotes.map(q =>
        `"${q.domain}","${q.concept}","${q.quote}","${q.created_at}"`
    ).join('\n');
    // Trigger download
}
```

#### Plain English
This is the "fire alarm" section of the dashboard. It shows:
- **What's wrong**: Top negative concepts (e.g., "remote control" gets complained about most)
- **Who's saying it**: Which review sites have the most negative coverage
- **Exact quotes**: The actual negative statements from AI responses

The PR team can export these quotes to a spreadsheet, review them, and decide which ones need a response. It's like a to-do list of reputation issues.

---

### Part 5: Concept Analysis Section

#### What It Contains

1. **Top Positive Concepts Chart** - Which product features are mentioned positively most often
2. **Concept Sentiment Mix Chart** - Stacked bar showing sentiment distribution per concept

#### Technical Implementation

```javascript
// Fetch concept sentiment data
async function fetchConceptSentiment(filters) {
    const response = await fetch(
        `${SUPABASE_URL}/rest/v1/rpc/get_concept_sentiment`,
        {
            method: 'POST',
            headers: { apikey: SUPABASE_ANON_KEY },
            body: JSON.stringify(filters)
        }
    );
    return response.json();
}

// Render concept sentiment mix
function renderConceptSentimentChart(data) {
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: concepts,
            datasets: [
                { label: 'Positive', data: positiveData },
                { label: 'Neutral', data: neutralData },
                { label: 'Negative', data: negativeData }
            ]
        },
        options: { scales: { x: { stacked: true }, y: { stacked: true } } }
    });
}
```

#### Plain English
This section answers:
- "What product features do AI models praise most?" (e.g., "picture quality", "gaming performance")
- "Which features have mixed reviews?" (long bar with multiple colors)
- "Are there any features that are always mentioned positively?"

It's like a report card for each product feature, showing which ones are doing well and which need improvement.

---

### Part 6: Topic Deep Dive Enhancement

#### What Changed
The existing "Top Topics" section was enhanced with:
- Section header with "Questions this section answers" display
- Sentiment breakdown per tag (topic)

#### Plain English
Before, the section just showed which topics were mentioned most. Now it also shows whether those mentions are positive or negative. For example, "Gaming TVs" might have high mentions but mostly negative sentiment, which would be important to know.

---

### Part 7: "Questions This Section Answers" Feature

#### Technical Implementation
Each new section includes a visible question list:

```html
<div class="section-questions">
    <h4>Questions this section answers:</h4>
    <ul>
        <li>Which domains mention Samsung most positively?</li>
        <li>How does owned content compare to earned media?</li>
        <li>Which review sites have the most negative coverage?</li>
    </ul>
</div>
```

```css
.section-questions {
    background: #f5f5f5;
    border-left: 4px solid #1428a0;
    padding: 12px 16px;
    margin-bottom: 20px;
}
.section-questions h4 {
    margin: 0 0 8px 0;
    font-size: 14px;
    color: #666;
}
.section-questions li {
    font-size: 13px;
    color: #333;
    margin-bottom: 4px;
}
```

#### Plain English
This is like putting a "what you can learn here" sign at the start of each section. Instead of users guessing what each chart shows, they can read the questions and immediately know if this section has what they're looking for.

---

### Part 8: Technical Summary

#### New CSS Classes Added (~15)
- `.section-header` - Section title with border divider
- `.section-questions` - Question list container
- `.question-list` - Styled list of questions
- `.chart-container-half` - Half-width chart container for side-by-side charts
- `.table-pagination` - Pagination controls container
- `.pagination-btn` - Page navigation buttons
- `.export-btn` - CSV export button styling
- `.quote-text` - Quote display formatting
- `.sentiment-badge-positive/neutral/negative` - Sentiment indicator badges
- Plus responsive variants for mobile/tablet

#### New JavaScript Functions Added (17 total)
**Data Fetching (8):**
- `fetchDomainSentiment(filters)` - Get domain sentiment from summary table
- `fetchDomainTypeSentiment(filters)` - Get aggregate by domain type
- `fetchNegativeQuotes(filters, page, pageSize)` - Get negative quotes with pagination
- `fetchNegativeConcepts(filters)` - Get top negative concepts
- `fetchNegativeSources(filters)` - Get sources with most negative coverage
- `fetchPositiveConcepts(filters)` - Get top positive concepts
- `fetchConceptSentiment(filters)` - Get sentiment mix per concept
- `fetchTagSentiment(filters)` - Get sentiment per topic tag

**Chart Rendering (9):**
- `renderDomainSentimentChart(data)` - Horizontal stacked bar by domain
- `renderDomainTypeChart(data)` - Owned/Earned/Competitor comparison
- `renderDomainTable(data)` - Sortable domain performance table
- `renderNegativeConceptsChart(data)` - Top negative concepts bar chart
- `renderNegativeSourcesChart(data)` - Negative coverage by source
- `renderQuoteBrowser(quotes, page, total)` - Quote table with pagination
- `renderPositiveConceptsChart(data)` - Top positive concepts bar chart
- `renderConceptSentimentChart(data)` - Concept sentiment mix stacked bar
- `renderTagSentimentChart(data)` - Topic sentiment breakdown

#### File Size Change
- Before: ~1940 lines
- After: ~3022 lines
- Added: ~1082 lines of new code

---

### Part 9: Data Sources Used

| Component | Data Source | Why This Source |
|-----------|-------------|-----------------|
| Domain Sentiment Chart | `summary_domain_sentiment` table | Pre-computed aggregations for fast loading |
| Domain Type Chart | `summary_domain_sentiment` with GROUP BY | Aggregates on pre-computed data |
| Quote Browser | `vw_sentiment_quotes` view | Provides full quote text with domain/concept context |
| Negative Concepts | `summary_domain_sentiment` or RPC | Aggregated concept counts by sentiment |
| Tag Sentiment | Existing RPC functions | Already built for topic analysis |

#### Plain English
The dashboard uses two types of data:
1. **Summary tables** - Pre-calculated totals that load instantly (like a report that's already written)
2. **Views** - Live queries that can be filtered but are slightly slower (like running a search)

For the main charts, we use summary tables for speed. For the quote browser where users need to see actual text, we use views that provide the full details.

---

### Part 10: Files Modified

| File | Changes |
|------|---------|
| `clients/samsung/dashboards/geo-dashboard.html` | Added 4 new sections, 2 new filters, ~15 CSS classes, 17 JS functions |

---

### Part 11: Lessons Learned

#### Technical Lessons
1. **Organize functions by purpose** - Grouping fetch functions separately from render functions makes the code easier to navigate
2. **Use summary tables for chart data** - Pre-computed aggregations make dashboards feel instant
3. **Pagination is essential for tables** - Even 50 quotes becomes overwhelming without pagination

#### Plain English Lessons
1. **Show the questions, not just the answers** - Users understand data better when they know what question it answers
2. **Separate "explore" from "act"** - Domain analysis is for understanding; PR Action Center is for doing something about it
3. **Export features matter** - Dashboards are great for discovery, but teams need to take data elsewhere for actual work

---

## 2026-01-30 (Session 4): Critical Cartesian Product Fix in Domain Sentiment Views

### Session Goals
Fix a critical data bug where the domain sentiment summary tables were showing millions of "mentions" (e.g., 69M positive mentions for Samsung, 4.9M for RTINGS) when the actual numbers should be in the thousands. The root cause was a cartesian product explosion when joining two large tables.

---

### Part 1: The Problem - What is a Cartesian Product?

#### Technical Explanation
When you JOIN two tables without proper aggregation, every row from Table A matches with every row from Table B that shares the join key. If prompt "P1" appears:
- 651 times in `semrush_prompt_urls` (once for each source URL that prompt cites)
- 386 times in `semrush_concept_prompts` (once for each concept that prompt discusses)

Then joining on `prompt = 'P1'` creates 651 x 386 = 251,286 rows for that ONE prompt.

With 383 unique prompts, this explodes the result set from thousands of meaningful records to hundreds of millions of duplicate combinations.

#### Plain English
Imagine you have a guest list for a wedding:
- Guest "Alice" is friends with 5 bridesmaids
- Guest "Alice" also knows 10 groomsmen

If you ask "list all friend connections for Alice," you expect 15 rows (5 + 10). But if you accidentally ask "list all combinations of bridesmaids AND groomsmen that Alice knows," you get 50 rows (5 x 10) - most of which are meaningless pairs.

That's what happened here: the database was counting every combination of (URL, concept) for each prompt, not the actual number of prompts or sources.

---

### Part 2: The Data Structure

#### What the Tables Contain

| Table | Rows | What Each Row Represents |
|-------|------|-------------------------|
| `semrush_prompt_urls` | 249,307 | One prompt + one source URL that prompt cites |
| `semrush_concept_prompts` | 145,337 | One prompt + one concept mentioned + sentiment |

#### The Join Problem

The original code did:
```sql
SELECT domain, sentiment, COUNT(*) as mentions
FROM semrush_prompt_urls pu
JOIN semrush_concept_prompts cp ON pu.prompt = cp.prompt
WHERE pu.source LIKE '%rtings.com%'
GROUP BY domain, sentiment;
```

This creates the cartesian product because:
- Each prompt in `pu` that cites RTINGS appears ~651 times (once per URL)
- Each matching prompt in `cp` appears ~386 times (once per concept)
- JOIN multiplies: 651 x 386 = 251,286 rows per prompt

#### Plain English
The code was accidentally asking: "For every URL cited by RTINGS and every concept discussed in that prompt, count 1." That's like counting a book as many times as it has pages multiplied by chapters, instead of just counting the book once.

---

### Part 3: The Fix - Two-Step Aggregation

#### The Correct Approach

Instead of joining the full tables, we:
1. **First:** Get distinct prompts that cite a domain (from `semrush_prompt_urls`)
2. **Then:** Join those distinct prompts with concepts to get sentiment breakdown (from `semrush_concept_prompts`)
3. **Count:** DISTINCT prompts and DISTINCT concepts, not raw row counts

#### New Function: `refresh_single_domain_sentiment_v2()`

```sql
-- Step 1: Get distinct prompts that cite this domain
WITH domain_prompts AS (
    SELECT DISTINCT prompt
    FROM semrush_prompt_urls
    WHERE source ILIKE '%' || p_domain || '%'
),
-- Step 2: Get distinct URLs cited by those prompts
url_counts AS (
    SELECT COUNT(DISTINCT source) as unique_urls
    FROM semrush_prompt_urls
    WHERE source ILIKE '%' || p_domain || '%'
),
-- Step 3: Join with concepts and count DISTINCT values
sentiment_breakdown AS (
    SELECT
        cp.sentiment,
        COUNT(DISTINCT dp.prompt) as unique_prompts,
        COUNT(DISTINCT cp.concept) as unique_concepts
    FROM domain_prompts dp
    JOIN semrush_concept_prompts cp ON dp.prompt = cp.prompt
    GROUP BY cp.sentiment
)
-- Final result uses unique_prompts as the "mentions" count
```

#### Plain English
The fix is like counting books properly:
1. First, make a list of all unique book titles on the RTINGS shelf
2. Then, for each book, note whether its review is positive, neutral, or negative
3. Count each book once, not once per page

---

### Part 4: Before and After Comparison

#### RTINGS Example

| Metric | Before (Wrong) | After (Correct) | What It Means |
|--------|----------------|-----------------|---------------|
| Positive mentions | 4,958,931 | 358 | 358 prompts cite RTINGS with positive sentiment |
| Neutral mentions | 2,007,680 | N/A | (Not tracked separately) |
| Negative mentions | 96,738 | N/A | (Not tracked separately) |
| Unique URLs | N/A | 2,344 | 2,344 distinct RTINGS URLs are cited |
| Unique concepts | 7,949 | 7,949 | 7,949 concepts are discussed (unchanged) |

#### Why the Concept Count Stayed the Same
The concept count was always using `COUNT(DISTINCT concept)`, so it was already correct. Only the "mentions" count was wrong because it was using `COUNT(*)` on the joined rows.

---

### Part 5: Key Insight - What Should "Mentions" Mean?

#### The Question
When the dashboard shows "RTINGS has 358 positive mentions," what does that actually mean?

#### The Answer
It means **358 distinct prompts (questions asked to AI models) cite RTINGS and have positive sentiment**.

This is the meaningful unit because:
- A prompt is a question a user asked (e.g., "What's the best 65-inch TV?")
- If RTINGS is cited in that prompt's answer, that's one "mention"
- The same prompt might cite 5 different RTINGS URLs, but it's still ONE question mentioning RTINGS
- The same prompt might discuss 10 different concepts (price, picture quality, etc.), but it's still ONE mention

#### Plain English
If someone asks "What's the best TV?" and the AI mentions RTINGS 5 times in the answer, that's ONE mention of RTINGS (one question asked), not 5 mentions.

---

### Part 6: Updated Functions and Data Refresh

#### Functions Modified

| Function | Change |
|----------|--------|
| `refresh_single_domain_sentiment_v2(domain)` | New function with correct aggregation logic |
| `refresh_all_summaries()` | Updated to use v2 function |

#### Domains Refreshed
All 12 key domains were refreshed with correct counts:
- Review sites: rtings.com, techradar.com, tomsguide.com, cnet.com, whathifi.com
- Business: forbes.com, businessinsider.com, bestbuy.com
- Owned: samsung.com, news.samsung.com
- Competitors: lg.com, sony.com

---

### Part 7: Lessons Learned

#### Technical Lessons
1. **Always check for cartesian products** when joining tables with many-to-many relationships through a shared key
2. **Use DISTINCT counts** when the meaningful unit is unique values, not row combinations
3. **Test with known values** - if you know RTINGS has ~2,000 URLs, seeing 5M "mentions" is a red flag

#### Plain English Lessons
1. **Ask "what are we actually counting?"** - The word "mentions" could mean prompts, URLs, concepts, or combinations. Define it clearly.
2. **Sanity check the numbers** - If a tech review site shows more "mentions" than all the words ever written about TVs, something is wrong.
3. **Separate counting from combining** - First count unique things, then combine them. Don't try to do both in one query.

---

### Files Modified
- Supabase function: `refresh_single_domain_sentiment_v2()` (created)
- Supabase function: `refresh_all_summaries()` (updated to use v2)
- Supabase table: `summary_domain_sentiment` (data refreshed for all 12 domains)

---

## 2026-01-30 (Session 3): Dashboard Demo Questions and UI Requirements Documentation

### Session Goals
Create comprehensive documentation to ensure the Samsung AI Visibility dashboard can answer all questions clients will ask. This involves documenting demo questions, running sample queries to understand data patterns, and specifying UI requirements for the dashboard.

---

### Part 1: Why Documentation Before Implementation?

#### The Problem
Building a dashboard without knowing what questions it needs to answer leads to:
- Features nobody uses
- Missing critical functionality
- Performance problems discovered late
- Scope creep during development

#### The Solution
Document everything upfront:
1. What questions will clients ask? (Demo Questions)
2. What data do we have to answer them? (Sample Queries)
3. What UI components are needed? (UI Requirements)

#### Plain English
Imagine building a car without knowing if the customer needs a sedan, a truck, or a sports car. You might build something, but it probably won't be what they wanted. The demo questions document is like the customer saying "I need to carry lumber, tow a boat, and drive off-road" - now you know to build a truck, not a sports car.

---

### Part 2: Demo Questions Document

#### What It Contains
The file `clients/samsung/docs/dashboard-demo-questions.md` contains 60+ questions organized into 10 categories:

| Category | Example Question | What It Tests |
|----------|-----------------|---------------|
| Domain | "What does RTINGS say vs TechRadar?" | Domain comparison chart |
| Domain Type | "How do Owned vs Earned sources differ?" | Domain type breakdown |
| Sentiment | "What are the top negative concepts?" | Sentiment filtering |
| Tag | "How does 'Gaming TVs' sentiment vary by domain?" | Tag + domain cross-filter |
| Concept | "What specific issues do reviews mention?" | Concept drill-down |
| Brand | "How many positive vs negative Samsung mentions?" | Brand sentiment summary |
| Product | "Which products get the most mentions?" | Product leaderboard |
| PR Action | "What negative quotes need a response?" | Quote browser with sentiment filter |
| Time | "How has sentiment changed over 30 days?" | Time series charts |
| Cross-dimensional | "Gaming TVs + Earned sites + Negative sentiment?" | Multi-filter combinations |

#### Plain English
This is a "test script" for the dashboard. If we can answer all 60+ questions using the dashboard UI, we know we built the right thing. If a question cannot be answered, we know we need to add a feature or query.

---

### Part 3: Sample Queries to Understand Data

#### Queries Executed
We ran real queries against the Supabase views to understand what data is available:

**Domain Comparison:**
```sql
SELECT domain, citations, mentions, positive_pct, negative_pct, neutral_pct
FROM vw_domain_sentiment
WHERE domain IN ('www.rtings.com', 'www.techradar.com', 'www.tomsguide.com', 'www.cnet.com')
ORDER BY citations DESC;
```

**Domain Type Breakdown:**
```sql
SELECT domain_type, citations, mentions, positive_pct, negative_pct, neutral_pct
FROM vw_domain_type_sentiment
ORDER BY citations DESC;
```

**Top Negative Concepts:**
```sql
SELECT concept, COUNT(*) as negative_count
FROM semrush_concept_prompts
WHERE sentiment = 'negative'
GROUP BY concept
ORDER BY negative_count DESC
LIMIT 10;
```
Result: remote control, price, contrast, viewing angles, etc.

**Negative Quotes from Review Sites:**
```sql
SELECT domain, quote, concept
FROM vw_sentiment_quotes
WHERE domain_type = 'Earned' AND sentiment = 'negative'
LIMIT 50;
```

**Brand Mentions with Sentiment:**
```sql
SELECT brand,
       SUM(CASE WHEN sentiment = 'positive' THEN mentions ELSE 0 END) as positive,
       SUM(CASE WHEN sentiment = 'neutral' THEN mentions ELSE 0 END) as neutral,
       SUM(CASE WHEN sentiment = 'negative' THEN mentions ELSE 0 END) as negative
FROM semrush_concept_prompts
GROUP BY brand;
```
Result: Samsung has 69M positive, 26M neutral, 2.6M negative mentions

**Available Tags:**
```sql
SELECT DISTINCT tag, category FROM tv_topics ORDER BY category, tag;
```
Result: 39 tags in 4 categories (TV Features, TV Models, TV Reviews & Brand, TV Sizes)

**Available Domains:**
```sql
SELECT DISTINCT domain, domain_type FROM semrush_domains ORDER BY domain_type, domain;
```
Result: 12 key domains in 4 types (Owned, Earned, Competitor, Other)

#### What We Learned
- Data is sufficient for all demo questions
- Summary tables make aggregated queries instant
- Filtered queries on views perform well
- 39 tags and 12 domains provide good filter options

#### Plain English
We tested the "plumbing" before building the "faucets." Running these queries confirmed that the Supabase views and tables contain all the data needed to answer client questions. We also discovered the exact numbers (39 tags, 12 domains, 69M positive mentions) which will inform UI design.

---

### Part 4: UI Requirements Document

#### What It Contains
The file `clients/samsung/docs/dashboard-ui-requirements.md` specifies:

**1. Filter Components:**
| Filter | Type | Source |
|--------|------|--------|
| Domain | Multi-select dropdown | `semrush_domains` table |
| Domain Type | Single-select (Owned/Earned/Competitor/Other) | Hardcoded or `semrush_domains` |
| Sentiment | Single-select (Positive/Neutral/Negative/All) | Hardcoded |
| Date Range | Date picker with presets | 7/14/30 days, custom range |
| Tag | Multi-select with categories | `tv_topics` table |
| Concept | Autocomplete search | `semrush_concept_prompts` concepts |

**2. KPI Cards:**
- Total Citations (count)
- Total Mentions (count)
- Positive Sentiment % (percentage)
- Negative Sentiment % (percentage)

**3. Chart Types Required:**
| Chart | Purpose | Data Source |
|-------|---------|-------------|
| Sentiment Donut | Overall sentiment breakdown | `vw_domain_type_sentiment` |
| Domain Comparison Bar | Compare domains side-by-side | `vw_domain_sentiment` |
| Domain Type Breakdown | Owned vs Earned vs Competitor | `vw_domain_type_sentiment` |
| Tag Sentiment Heatmap | Sentiment by tag | `vw_tag_sentiment` |
| Concept Cloud | Top concepts by volume | `semrush_concept_prompts` |
| Time Series Line | Trends over time | `semrush_concept_prompts` with date filter |

**4. Table Types Required:**
| Table | Purpose | Key Columns |
|-------|---------|-------------|
| Quote Browser | PR action items | Domain, Quote, Sentiment, Concept |
| Domain Summary | Aggregated metrics | Domain, Type, Citations, Sentiment % |
| Product Leaderboard | Top products | Product, Mentions, Positive %, Rank |

**5. Page Structure (5 Views):**
1. **Overview** - KPI cards + high-level charts
2. **Domain Detail** - Drill into specific domain's data
3. **Topic Analysis** - Tag/concept exploration
4. **PR Action Center** - Negative quotes requiring response
5. **Competitive Analysis** - Samsung vs competitors

**6. Performance Considerations:**
- Use `summary_domain_sentiment` for domain charts (instant)
- Use `summary_domain_type_sentiment` for type breakdowns (instant)
- Use filtered views for drill-downs (fast with WHERE clause)
- Call `refresh_all_summaries()` after data imports

#### Plain English
This is the "blueprint" for the dashboard. Instead of describing it vaguely ("we need some charts"), it specifies exactly:
- What filters the user can click
- What numbers appear in each KPI card
- What chart types are needed and what data feeds them
- What tables show detailed data
- How pages are organized
- Which queries to use for best performance

A developer reading this document knows exactly what to build without guessing.

---

### Part 5: Drill-Down Paths

#### Interactive Exploration
Users should be able to click and explore:

```
Overview Page
    |
    +-- Click domain in bar chart --> Domain Detail Page
    |       |
    |       +-- Click tag in heatmap --> Tag Detail (filtered by domain)
    |
    +-- Click "Negative" in donut --> Quote Browser (filtered to negative)
    |
    +-- Click product in leaderboard --> Product Detail Page
```

#### Plain English
Like Google Maps, users should be able to zoom in and out. Starting with the big picture (Overview), they can click to drill down into specific domains, tags, or products. Each click adds a filter, and a "breadcrumb" trail shows where they are. A "Reset Filters" button returns to the big picture.

---

### Part 6: Files Created

| File | Purpose | Location |
|------|---------|----------|
| `dashboard-demo-questions.md` | 60+ questions to validate dashboard | `clients/samsung/docs/` |
| `dashboard-ui-requirements.md` | Complete UI specification | `clients/samsung/docs/` |

---

### Part 7: Next Steps

1. **Design mockups** - Create wireframes based on UI requirements
2. **Build Overview page** - Start with KPI cards and high-level charts
3. **Add filters** - Implement filter bar with all specified options
4. **Build detail pages** - Domain Detail, Topic Analysis, PR Action Center
5. **Connect drill-downs** - Wire up click interactions between components
6. **Performance testing** - Verify queries use summary tables where appropriate

---

### Lesson Learned

**Always document requirements before implementation.** The time spent writing demo questions and UI requirements upfront prevents wasted effort building the wrong thing. It also creates a "contract" between the developer and stakeholder - both parties know exactly what "done" looks like.

---

## 2026-01-30 (Session 2): Supabase View Optimizations - Summary Tables for Performance

### Session Goals
The views created earlier today were timing out on aggregated queries. Implement a summary table architecture with pre-computed aggregations to make dashboard queries instant.

---

### Part 1: The Problem

#### What Happened
After creating the 7 views earlier today, we discovered that `vw_domain_sentiment` and `vw_domain_type_sentiment` were timing out when queried directly. These views aggregate across 249K+ rows in `semrush_prompt_urls`, and computing that on every request is too slow for dashboard use.

#### Technical Cause
The views used inline aggregations like:
```sql
SELECT domain, COUNT(*) as citations,
       AVG(CASE WHEN sentiment = 'positive' THEN 1 ELSE 0 END) as positive_pct
FROM semrush_prompt_urls pu
JOIN semrush_concept_prompts cp ON pu.prompt = cp.prompt
GROUP BY domain
```

With 249K rows in one table and 145K in another, plus a JOIN, plus aggregation - Supabase times out before completion.

#### Plain English
Imagine asking someone to count all the red, blue, and green marbles in a jar of 250,000 marbles every single time you want to know the color breakdown. It takes too long. The solution is to count them once, write down the totals, and just read the piece of paper next time.

---

### Part 2: The Solution - Summary Tables

#### Architecture Overview

We implemented a **summary table pattern**:
1. Create tables that store pre-computed aggregations
2. Update the views to read from summary tables (instant)
3. Provide refresh functions to update the summaries when source data changes

#### New Tables Created

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| `semrush_domains` | Domain lookup with pre-computed domain names | `source`, `domain`, `domain_type` |
| `summary_domain_sentiment` | Pre-aggregated sentiment per domain | `domain`, `citations`, `positive_pct`, `negative_pct`, `neutral_pct` |
| `summary_domain_type_sentiment` | Pre-aggregated sentiment by domain type | `domain_type`, `citations`, `positive_pct`, `negative_pct`, `neutral_pct` |
| `summary_tag_sentiment` | Structure for tag-level aggregation | `tag`, `mentions`, `positive_pct`, etc. |
| `summary_tag_domain_sentiment` | Structure for tag+domain combinations | `tag`, `domain`, `citations`, etc. |

#### Plain English
Instead of counting marbles every time, we now have a cheat sheet:
- **Domain lookup table** - Pre-extracts "techradar.com" from "https://www.techradar.com/reviews/samsung-tv" so we don't have to parse URLs repeatedly
- **Summary tables** - Store the actual counts: "techradar.com has 1,247 citations, 68% positive, 12% negative, 20% neutral"
- **Refresh functions** - Commands to re-count the marbles when we add new ones to the jar

---

### Part 3: Domain Lookup Table (`semrush_domains`)

#### Why It Exists
The original queries were doing `SPLIT_PART(source, '/', 3)` on every row to extract the domain from a URL. With 249K rows, that is 249K string parsing operations per query.

#### What It Contains
```sql
CREATE TABLE semrush_domains (
  source TEXT PRIMARY KEY,      -- Full URL
  domain TEXT NOT NULL,         -- Extracted domain (e.g., "www.techradar.com")
  domain_type TEXT              -- Owned/Earned/Competitor/Other
);
```

#### Indexes Added
- `idx_domains_domain` on `domain`
- `idx_domains_domain_type` on `domain_type`

#### Plain English
Instead of reading a full web address and extracting the website name 249K times, we do it once and store the results in a simple lookup table. Now we just match URLs to their pre-extracted domain names.

---

### Part 4: Summary Tables

#### `summary_domain_sentiment`

**Purpose:** Stores pre-computed sentiment aggregations for the 12 most important domains.

**Key Domains Pre-populated:**
- **Review Sites:** www.rtings.com, www.techradar.com, www.tomsguide.com, www.cnet.com, www.whathifi.com
- **Business/News:** www.forbes.com, www.businessinsider.com, www.bestbuy.com
- **Owned:** www.samsung.com, news.samsung.com
- **Competitors:** www.lg.com, www.sony.com

**Schema:**
```sql
CREATE TABLE summary_domain_sentiment (
  domain TEXT PRIMARY KEY,
  citations BIGINT,
  mentions BIGINT,
  positive_count BIGINT,
  negative_count BIGINT,
  neutral_count BIGINT,
  positive_pct NUMERIC,
  negative_pct NUMERIC,
  neutral_pct NUMERIC,
  sample_positive TEXT,
  sample_negative TEXT,
  updated_at TIMESTAMP DEFAULT NOW()
);
```

#### `summary_domain_type_sentiment`

**Purpose:** Stores pre-computed sentiment by domain classification (Owned/Earned/Competitor/Other).

**Schema:**
```sql
CREATE TABLE summary_domain_type_sentiment (
  domain_type TEXT PRIMARY KEY,
  citations BIGINT,
  mentions BIGINT,
  positive_pct NUMERIC,
  negative_pct NUMERIC,
  neutral_pct NUMERIC,
  updated_at TIMESTAMP DEFAULT NOW()
);
```

#### Plain English
These are the "cheat sheets" with pre-counted totals. Instead of querying 249K rows, the dashboard just reads these small tables (12 rows and 4 rows respectively).

---

### Part 5: Updated Views

#### `vw_domain_sentiment` - Now Instant

**Before (slow):**
```sql
-- Computed aggregations from 249K rows on every query
SELECT domain, COUNT(*) as citations, ...
FROM semrush_prompt_urls ...
GROUP BY domain
```

**After (instant):**
```sql
-- Just reads from 12-row summary table
SELECT * FROM summary_domain_sentiment;
```

#### `vw_domain_type_sentiment` - Now Instant

**Before (slow):**
```sql
-- Computed aggregations across all domain types
SELECT domain_type, COUNT(*) as citations, ...
FROM semrush_prompt_urls ...
GROUP BY domain_type
```

**After (instant):**
```sql
-- Just reads from 4-row summary table
SELECT * FROM summary_domain_type_sentiment;
```

#### Plain English
The views are now "thin wrappers" around the summary tables. They look exactly the same to the dashboard, but behind the scenes they are reading from pre-computed data instead of crunching 249K rows.

---

### Part 6: Refresh Functions

#### `refresh_single_domain_sentiment(domain_name TEXT)`

**Purpose:** Recompute the summary for a single domain.

**When to Use:** When you know only one domain's data has changed.

**Example:**
```sql
SELECT refresh_single_domain_sentiment('www.techradar.com');
```

#### `refresh_all_summaries()`

**Purpose:** Recompute all 12 key domain summaries plus the domain type summary.

**When to Use:** After bulk data imports or periodic maintenance.

**Example:**
```sql
SELECT refresh_all_summaries();
```

**What It Does:**
1. Loops through all 12 key domains
2. Calls `refresh_single_domain_sentiment()` for each
3. Recomputes the domain type summary table

#### Plain English
These are commands to "re-count the marbles." You run them after adding new data. The dashboard always shows instant results because it reads from the cheat sheet, and you update the cheat sheet periodically (not on every request).

---

### Part 7: New Indexes

#### Indexes Added to `semrush_prompt_urls`
- `idx_prompt_urls_domain_type` on `domain_type` column
- `idx_prompt_urls_source` on `source` column

#### Why These Indexes
- The `domain_type` column is used in GROUP BY and WHERE clauses
- The `source` column is used in JOINs with the domain lookup table

#### Plain English
Indexes are like bookmarks in a big book. Instead of reading every page to find "Chapter 5: Competitors", the bookmark takes you directly there. These indexes help the database quickly find rows matching specific domain types or source URLs.

---

### Part 8: Performance Results

| Query Type | Before | After |
|------------|--------|-------|
| `SELECT * FROM vw_domain_sentiment` | **Timeout** | **Instant** |
| `SELECT * FROM vw_domain_type_sentiment` | **Timeout** | **Instant** |
| `SELECT * FROM vw_tag_sentiment WHERE tag = 'OLED'` | Slow | Fast |
| `SELECT * FROM vw_tag_domain_sentiment WHERE tag = 'OLED'` | Slow | Fast |

#### Plain English
- Dashboard-level queries (show me all domains, show me all domain types) are now instant
- Filtered queries (show me data for OLED specifically) are still fast because filters reduce the data volume

---

### Part 9: Dashboard Integration Guide

#### For Aggregated Data (Use Summary Views)
```javascript
// Domain sentiment - instant
const { data } = await supabase
  .from('vw_domain_sentiment')
  .select('*');

// Domain type sentiment - instant
const { data } = await supabase
  .from('vw_domain_type_sentiment')
  .select('*');
```

#### For PR Action Items (Use Filtered Queries)
```javascript
// Negative quotes from review sites
const { data } = await supabase
  .from('vw_sentiment_quotes')
  .select('*')
  .eq('domain_type', 'Earned')
  .eq('sentiment', 'negative')
  .limit(50);
```

#### For Data Refresh (Periodic Maintenance)
```javascript
// Call after data imports
const { data, error } = await supabase
  .rpc('refresh_all_summaries');
```

---

### Part 10: Objects Created Summary

#### Tables
- `semrush_domains` - Domain lookup with pre-computed domain names
- `summary_domain_sentiment` - Pre-aggregated sentiment per domain (12 rows)
- `summary_domain_type_sentiment` - Pre-aggregated sentiment by type (4 rows)
- `summary_tag_sentiment` - Structure ready for tag aggregation
- `summary_tag_domain_sentiment` - Structure ready for tag+domain aggregation

#### Functions
- `refresh_single_domain_sentiment(TEXT)` - Refresh one domain
- `refresh_all_summaries()` - Refresh all summaries

#### Indexes
- `idx_prompt_urls_domain_type` on `semrush_prompt_urls(domain_type)`
- `idx_prompt_urls_source` on `semrush_prompt_urls(source)`
- `idx_domains_domain` on `semrush_domains(domain)`
- `idx_domains_domain_type` on `semrush_domains(domain_type)`

#### Views Updated
- `vw_domain_sentiment` - Now reads from summary table
- `vw_domain_type_sentiment` - Now reads from summary table

---

### Session Summary

**Problem:** Views timing out when computing aggregations across 249K rows
**Solution:** Summary table architecture with pre-computed aggregations and refresh functions
**Result:** Dashboard queries now instant; filtered queries remain fast
**Maintenance:** Call `refresh_all_summaries()` periodically after data imports

---

---

## 2026-01-30: Samsung Supabase Views - Flexible Query Layer

### Session Goals
Create PostgreSQL views in Supabase to enable flexible querying across the full Samsung AI visibility data chain. The goal is to make it easy to answer complex questions like "What negative things do review sites say about Samsung?" without writing complex JOIN queries each time.

---

### Part 1: Overview

#### What Was Done
Created 7 PostgreSQL views that join data from three main tables:
- `semrush_prompt_urls` (249,307 rows) - Which prompts cite which URLs
- `semrush_concept_prompts` (145,337 rows) - Brand mentions with sentiment and quotes
- `tv_topics` (41 rows) - Topic/tag categories

#### Plain English
Think of the raw data tables like three separate spreadsheets:
1. One spreadsheet lists "this question led to this website being cited"
2. Another lists "this question mentioned Samsung with positive/negative/neutral sentiment"
3. A third lists "topic categories like Gaming TVs, OLED, etc."

The problem is: to answer "What do review sites say about Samsung?", you need to manually connect all three spreadsheets every time. Views are like pre-built connections - they create a single "super spreadsheet" that already has everything linked together. Now you can just filter by "review sites" and "negative sentiment" and get your answer immediately.

---

### Part 2: Views Created

#### View 1: `vw_prompt_url_sentiment` (Core Linked View)

**Purpose:** The foundation view that links the full chain: prompt -> URL -> sentiment

**What It Joins:**
- `semrush_prompt_urls` (the prompt-to-URL mapping)
- `semrush_concept_prompts` (the sentiment data)

**Key Columns:**
- `prompt`, `url`, `domain`, `domain_type`
- `sentiment`, `quote`, `concept`
- `position` (where the URL appeared in results)
- `snapshot_date`

**Plain English:** This is the master view. For every prompt, it shows which URLs were cited AND what the sentiment was. It is the building block for all other views.

---

#### View 2: `vw_domain_sentiment`

**Purpose:** Aggregate sentiment by domain (website)

**What It Shows:**
- Domain name
- Total citations for that domain
- Positive/negative/neutral percentages
- Sample quotes

**Example Output:**
| domain | citations | positive_pct | negative_pct | neutral_pct |
|--------|-----------|--------------|--------------|-------------|
| techradar.com | 1,247 | 68% | 12% | 20% |
| reddit.com | 892 | 45% | 35% | 20% |

**Plain English:** "Which websites are being cited most, and are they saying nice things about Samsung?" This view answers that question with one query.

---

#### View 3: `vw_domain_type_sentiment`

**Purpose:** Sentiment breakdown by domain classification

**Domain Types:**
- **Owned** - Samsung's own websites (samsung.com)
- **Earned** - Third-party sites that cite Samsung (techradar.com, cnet.com)
- **Competitor** - Competitor websites (lg.com, sony.com)
- **Social** - Social platforms (reddit.com, youtube.com)
- **Other** - Everything else

**Plain English:** "Are review sites (Earned) more positive or negative about Samsung compared to social media (Social)?" This view groups all the sentiment data by these categories.

---

#### View 4: `vw_sentiment_quotes`

**Purpose:** All quotes with their sentiment, filterable by domain

**Key Columns:**
- `quote` - The actual text that was positive/negative/neutral
- `sentiment` - Positive, Negative, or Neutral
- `domain` - Which website the quote came from
- `concept` - What feature/attribute was being discussed

**Example Use Case:**
```sql
SELECT quote, concept FROM vw_sentiment_quotes
WHERE domain LIKE '%reddit%' AND sentiment = 'negative'
```

**Plain English:** "Show me all the negative things Reddit says about Samsung." This view makes that query trivial.

---

#### View 5: `vw_prompt_tags_expanded`

**Purpose:** Normalize the tag data - one row per tag instead of comma-separated

**Background:** The source data has tags stored like "Gaming TVs, OLED, 4K" in a single field. This view splits them into separate rows so you can filter by individual tags.

**Before (raw data):**
| prompt | tags |
|--------|------|
| Best gaming TV? | Gaming TVs, 4K, Low Latency |

**After (this view):**
| prompt | tag | category |
|--------|-----|----------|
| Best gaming TV? | Gaming TVs | TV Type |
| Best gaming TV? | 4K | Resolution |
| Best gaming TV? | Low Latency | Features |

**Plain English:** Tags were crammed together. This view separates them so you can ask "show me all prompts about Gaming TVs" without doing text searching.

---

#### View 6: `vw_tag_sentiment`

**Purpose:** Sentiment aggregated by tag

**What It Shows:**
For each tag (like "Gaming TVs" or "OLED"):
- Total mentions
- Positive/negative/neutral percentages

**Example Output:**
| tag | mentions | positive_pct | negative_pct |
|-----|----------|--------------|--------------|
| Gaming TVs | 2,341 | 72% | 8% |
| OLED | 4,567 | 81% | 5% |
| Budget TVs | 1,234 | 45% | 32% |

**Plain English:** "How does sentiment differ by topic?" Gaming TVs might have very positive sentiment while Budget TVs might be more mixed. This view shows that at a glance.

---

#### View 7: `vw_tag_domain_sentiment`

**Purpose:** The most detailed view - combines tags, domains, and sentiment

**What It Shows:**
For each combination of tag + domain:
- How many citations
- Sentiment breakdown

**Example Use Case:**
"For Gaming TVs specifically, which domains are most positive?"

| tag | domain | citations | positive_pct |
|-----|--------|-----------|--------------|
| Gaming TVs | rtings.com | 234 | 89% |
| Gaming TVs | reddit.com | 156 | 62% |
| Gaming TVs | lg.com | 45 | 12% |

**Plain English:** This is the ultimate "slice and dice" view. Pick a topic, see which sites are friends and which are foes.

---

### Part 3: Why Views Instead of RPC Functions

#### Technical Decision

We already have `get_sources_by_topic` as an RPC function. Why create views instead of more RPC functions?

**Views are better when:**
- You want flexibility to combine filters in ways you have not thought of yet
- The query is a simple JOIN without complex parameters
- You want to use the data in reporting tools that can query views directly

**RPC Functions are better when:**
- You need complex aggregations with multiple parameters
- The query involves calculations that are hard to express in a view
- You want to enforce specific parameter validation

**Plain English:** RPC functions are like ordering a specific meal at a restaurant - you get exactly what the chef designed. Views are like a buffet - you can combine things however you want. These views give us buffet-style flexibility while the RPC function handles the one complex calculation we needed.

---

### Part 4: Tables Involved - Reference

| Table | Rows | Role in Views |
|-------|------|---------------|
| `semrush_prompt_urls` | 249,307 | Source of prompt-to-URL mappings, domains, positions |
| `semrush_concept_prompts` | 145,337 | Source of sentiment, quotes, concepts |
| `tv_topics` | 41 | Tag/category reference data |

---

### Part 5: Example Queries Now Possible

#### Query 1: "What negative things do review sites say about Samsung?"
```sql
SELECT quote, concept, domain
FROM vw_sentiment_quotes
WHERE domain_type = 'Earned'
  AND sentiment = 'negative'
LIMIT 50;
```

#### Query 2: "Which concepts get positive sentiment on owned domains?"
```sql
SELECT concept, COUNT(*) as mentions
FROM vw_sentiment_quotes
WHERE domain_type = 'Owned'
  AND sentiment = 'positive'
GROUP BY concept
ORDER BY mentions DESC;
```

#### Query 3: "What's the sentiment breakdown for Gaming TVs?"
```sql
SELECT * FROM vw_tag_sentiment
WHERE tag = 'Gaming TVs';
```

#### Query 4: "Top 10 domains by positive sentiment for OLED topic"
```sql
SELECT domain, positive_pct, citations
FROM vw_tag_domain_sentiment
WHERE tag = 'OLED'
ORDER BY positive_pct DESC
LIMIT 10;
```

---

### Session Summary

**Created:** 7 PostgreSQL views in Supabase
**Purpose:** Enable flexible querying across the full data chain (Tag -> Prompt -> URL/Domain -> Concept -> Sentiment)
**Benefit:** Complex questions that previously required writing multi-table JOINs can now be answered with simple WHERE clauses

---

---

## 2026-01-29 (Session 3): Documentation Sync - Supabase Tables, RPC Functions, and GEO Dashboard Features

### Session Goals
Synchronize documentation to capture all Supabase infrastructure and GEO Dashboard features that exist but were not fully documented. This includes new tables, RPC functions, and dashboard components that were built but not recorded in the build log.

---

### Part 1: Overview

#### What Was Done
A comprehensive documentation audit and update to ensure DEVELOPMENT.md, build-log.md, and DATA-REQUIREMENTS.md accurately reflect the current state of the Supabase database and GEO Dashboard. Several tables, an RPC function, and dashboard features were found to be undocumented or had outdated information.

#### Plain English
Think of this like doing an inventory check at a warehouse. We built a lot of shelves and storage systems over several sessions, but not everything got written down on the master inventory list. This session was about walking through the warehouse, counting what is actually there, and updating the inventory sheets so they match reality.

---

### Part 2: Supabase Tables - Complete Inventory

#### What We Found
Six tables now exist in Supabase for the Samsung GEO Dashboard. Three were well-documented, three were partially or not documented.

#### Full Table Inventory

| Table | Rows | Status | Purpose |
|-------|------|--------|---------|
| `semrush_concept_mentions` | 151,787 | Was documented | Brand mentions with sentiment, grouped by date and AI model |
| `semrush_cited_pages` | 84,856 | Was documented | URLs that get cited when AI answers questions |
| `semrush_url_prompts` | 43,842 | Was documented | Which prompts lead to which URLs being cited |
| `semrush_concept_prompts` | 145,337 | **Newly documented** | Brand mentions with the actual prompt text and sentiment |
| `semrush_prompt_urls` | 249,307 | **Newly documented** | Date-stamped mapping of prompts to source URLs with position |
| `tv_topics` | 41 | Was documented | TV topic categories for the filter dropdown |

#### Plain English
We have 6 "filing cabinets" in our cloud database:
1. **concept_mentions** - Records every time an AI mentions Samsung or a competitor, along with whether it was positive/negative
2. **cited_pages** - Records which websites get referenced when AI answers questions
3. **url_prompts** - Connects specific questions to the websites they cite
4. **concept_prompts** - The actual text of prompts and what brands they mention (this is the raw conversation data)
5. **prompt_urls** - A timestamped record of which prompt led to which URL, including where in the list it appeared
6. **tv_topics** - A simple list of TV categories for the dropdown filter (like "OLED", "Gaming TVs", etc.)

---

### Part 3: NEW RPC Function - get_sources_by_topic

#### What It Does
This RPC (Remote Procedure Call) function answers the question: "For a given topic and date, which websites are being cited, and what is the sentiment of their coverage?"

#### Why It Exists
The GEO Dashboard needed to show a table of sources filtered by topic. This requires joining data from two tables:
- `semrush_prompt_urls` - Which domains are cited (and how many times)
- `semrush_concept_prompts` - What is the sentiment of mentions from each domain

Doing this join in the browser would be slow (249K + 145K rows). An RPC function runs the query on the server and returns only the aggregated result.

#### Function Signature
```sql
get_sources_by_topic(p_date date, p_tag text)
RETURNS TABLE (
  domain text,
  domain_type text,
  citations bigint,
  mentions bigint,
  positive_pct numeric,
  negative_pct numeric,
  neutral_pct numeric
)
```

#### Parameters
- `p_date` - The date to filter by (e.g., '2026-01-29')
- `p_tag` - The topic/tag to filter by (e.g., 'OLED', 'Gaming TVs')

#### What It Returns
For each domain that was cited for the given topic/date:
- `domain` - The website (e.g., "techradar.com")
- `domain_type` - Classification: Owned, Earned, Social, Competitor, Other
- `citations` - How many times this domain was cited
- `mentions` - How many brand mentions came from content on this domain
- `positive_pct` - Percentage of mentions that were positive
- `negative_pct` - Percentage that were negative
- `neutral_pct` - Percentage that were neutral

#### Plain English
Imagine you ask: "For the topic 'Gaming TVs' on January 29th, which websites did AI chatbots cite, and were those websites saying nice things about Samsung or not?"

This function goes into the database, finds all the prompts about Gaming TVs from that date, looks up which websites were cited, then cross-references those with the sentiment data. Instead of sending you 400,000 rows to figure this out yourself, it does the math and sends back a neat summary: "TechRadar was cited 45 times with 72% positive sentiment, Reddit was cited 23 times with 45% positive sentiment, etc."

---

### Part 4: GEO Dashboard - Cited URLs Table

#### What It Is
A table in the GEO Dashboard that shows which specific URLs (not just domains) are being cited by AI models.

#### SEMrush Element ID
`3c29aa85-4f06-4f14-a376-b02333c6e3fa`

#### Data Shown
- URL path
- Domain
- Number of prompts that cited this URL
- The actual prompts that triggered citations

#### How It Differs from Citation Sources Table
- **Citation Sources Table** - Aggregated by domain (e.g., "techradar.com has 156 citations total")
- **Cited URLs Table** - Shows individual URLs (e.g., "techradar.com/reviews/samsung-s95d has 23 citations")

#### Plain English
If Citation Sources tells you "TechRadar is a popular source", Cited URLs tells you "specifically, this TechRadar article about the S95D TV gets cited a lot." This helps the client know exactly which content is driving their AI visibility, not just which websites.

---

### Part 5: GEO Dashboard - Sources by Topic with Sentiment Table

#### What It Is
A table that combines source citation data with sentiment analysis, filtered by the selected topic.

#### Data Source
Uses the `get_sources_by_topic` RPC function (documented in Part 3 above).

#### How It Works
1. User selects a date and topic from the dashboard filters
2. Dashboard calls `get_sources_by_topic(date, topic)`
3. RPC function queries both `semrush_prompt_urls` and `semrush_concept_prompts`
4. Returns aggregated data per domain
5. Dashboard renders table with sentiment color-coding

#### Columns Displayed
| Column | Description |
|--------|-------------|
| Domain | Website URL |
| Type | Owned/Earned/Social/Competitor badge |
| Citations | Number of times cited for this topic |
| Mentions | Number of brand mentions from this source |
| Sentiment | Bar showing positive (green) / neutral (gray) / negative (red) split |

#### Use Case
Answers the client question: "For Gaming TVs, which sources are helping us, and are they helping us well?"

If techradar.com has 45 citations but 60% negative sentiment, that might be worse than rtings.com with 20 citations but 85% positive sentiment.

#### Plain English
This table helps Samsung understand not just "who is talking about us" but "who is talking about us AND saying good things." A news site that mentions Samsung 100 times but always negatively is not as valuable as a site that mentions Samsung 30 times but always positively.

---

### Part 6: supabase-data.js Module Documentation

#### What It Is
A centralized JavaScript module at `clients/samsung/dashboards/js/supabase-data.js` that handles all Supabase data fetching for the dashboard.

#### Why It Was Created
Instead of each dashboard component having its own fetch logic, this module provides a single source of truth for:
- Supabase connection settings (URL, anon key)
- Color configurations for charts
- Date range helpers
- Data fetching functions
- KPI calculation functions
- Chart data transformations

#### Key Functions Provided
```javascript
// Color configurations
getColorConfig()           // Returns brand colors, sentiment colors, model colors

// API helpers
callRPC(functionName, params)  // Calls Supabase RPC functions
fetchTable(tableName, query)   // Fetches from REST API

// Date helpers
getDateRange(period)       // Converts "7d", "30d" to date objects
formatDate(date)           // Formats for Supabase queries

// Data fetching
fetchDailyMentions(dateFrom, modelFilter)   // Calls get_daily_mentions RPC
fetchTopCategories(dateFrom, modelFilter)    // Calls get_top_categories RPC
fetchSourcesByTopic(date, tag)               // Calls get_sources_by_topic RPC
fetchCitedPages(filters)                     // Fetches from semrush_cited_pages

// KPI calculations
calculateShareOfVoice(data)     // Samsung mentions / total mentions
calculateVisibilityScore(data)  // Composite visibility metric
calculateSentimentScore(data)   // Weighted sentiment calculation

// Chart transformations
transformForLineChart(data)     // Formats for Chart.js line charts
transformForDonutChart(data)    // Formats for Chart.js donut charts
transformForBarChart(data)      // Formats for Chart.js bar charts
```

#### Plain English
Instead of every part of the dashboard knowing how to talk to the database, we created a "helper library." Dashboard components say "I need KPI data" or "I need the top categories chart data" and the helper library handles:
- Where to find the data
- How to ask for it
- What to do if something goes wrong
- How to format it for the chart

This keeps the dashboard code clean and means if we ever need to change how we get data, we only change one file.

---

### Part 7: Files Updated in This Session

| File | Changes |
|------|---------|
| `DEVELOPMENT.md` | Added Session 3 summary documenting tables, RPC functions, dashboard features |
| `docs/build-log.md` | Added this detailed session entry with Plain English explanations |
| `clients/samsung/dashboards/DATA-REQUIREMENTS.md` | Added missing tables and RPC function |

---

### Part 8: Complete RPC Function Reference

For reference, here are all three RPC functions now available:

| Function | Parameters | Returns | Used For |
|----------|------------|---------|----------|
| `get_daily_mentions` | `date_from`, `model_filter` | date, model, brand, total_mentions, sentiment breakdown | KPI cards, trend charts |
| `get_top_categories` | `date_from`, `model_filter`, `limit_count` | concept_category, total_mentions, sentiment breakdown | Top Topics bar chart |
| `get_sources_by_topic` | `p_date`, `p_tag` | domain, domain_type, citations, mentions, sentiment percentages | Sources by Topic table |

---

### Lessons Learned

1. **Documentation must happen as you build:** Features built across multiple sessions can easily become undocumented if the build log is not updated immediately. This session was necessary because several features were built but not recorded.

2. **RPC functions are the key to dashboard performance:** With tables containing 150K-250K rows, doing joins in the browser is not feasible. Server-side RPC functions that return aggregated results are essential for responsive dashboards.

3. **Keep a table inventory updated:** Knowing exactly what tables exist, their row counts, and their purpose makes it easier to plan new features and troubleshoot issues.

4. **Plain English documentation serves multiple audiences:** The client, project managers, and future developers all benefit from having non-technical explanations alongside the technical details.

---

## 2026-01-29 (Session 2): GEO Dashboard - Supabase Edge Function and Live Data Migration

### Session Goals
Move the GEO Dashboard from static/local data sources to live Supabase and SEMrush data. Create a proxy to handle CORS issues when calling SEMrush from the browser. Migrate the Topic filter from a static JSON file to a Supabase table.

---

### Part 1: Overview

#### What Was Done
This session focused on infrastructure improvements to make the GEO Dashboard fully data-driven. We created a Supabase Edge Function to proxy SEMrush API calls (solving browser CORS restrictions), migrated the Topic filter data to a Supabase table, and connected the Citation Sources table to live SEMrush data.

#### Plain English
Imagine the dashboard was like a display board with printed cards pinned to it. Before this update, changing the data meant reprinting the cards. Now, the display board has digital screens that automatically update from a central database. We also added a "translator" in the cloud that fetches data from SEMrush (which normally refuses to talk directly to web browsers) and passes it along to our dashboard.

---

### Part 2: Supabase Edge Function - semrush-proxy

#### What We Built
A serverless function hosted on Supabase that acts as a middleman between the browser and SEMrush API.

#### Why This Was Needed
Web browsers have security rules (called CORS - Cross-Origin Resource Sharing) that prevent JavaScript from calling APIs on different domains. SEMrush does not allow browser requests directly. By routing through our own Edge Function, we can add the necessary CORS headers.

#### Technical Details
```javascript
// Edge Function endpoint
POST https://zozzhptqoclvbfysmopg.supabase.co/functions/v1/semrush-proxy

// Request body
{
  "element_id": "28977430-d565-4529-97eb-2dfe2959b86b",
  "project_id": "68917",
  "filters": {
    "CBF_country": "us",
    "CBF_model": "search-gpt"
  }
}

// The Edge Function:
// 1. Receives the request from the browser
// 2. Adds the SEMrush API key (stored securely on server)
// 3. Calls SEMrush API
// 4. Adds CORS headers to response
// 5. Returns data to browser
```

#### CORS Handling
```javascript
// Edge Function handles CORS preflight (OPTIONS request)
const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
  'Access-Control-Allow-Methods': 'POST, OPTIONS'
};

// Returns 200 for OPTIONS requests (preflight check)
if (req.method === 'OPTIONS') {
  return new Response('ok', { headers: corsHeaders });
}
```

#### Plain English
When your browser tries to fetch data from a website other than the one you are on, the browser first asks "Am I allowed to do this?" (that is the CORS check). SEMrush says "No, I do not talk to browsers." So instead, we created our own helper service that the browser IS allowed to talk to. The helper then talks to SEMrush on behalf of the browser and passes the data back.

---

### Part 3: Supabase Table - tv_topics

#### What We Built
A database table to store the TV topic categories for the filter dropdown.

#### Why This Was Needed
Previously, topics were stored in a static JSON file (`tv_prompts.json`). If we wanted to add or change topics, we would need to update the file and redeploy. Now topics live in a database table that can be edited via the Supabase dashboard without any code changes.

#### Table Schema
| Column | Type | Description |
|--------|------|-------------|
| id | integer | Auto-incrementing primary key |
| category | text | Topic category (e.g., "TV Features") |
| tag | text | Topic tag (e.g., "OLED", "Gaming TVs") |
| prompt_count | integer | Number of prompts using this topic |
| created_at | timestamp | When the record was created |

#### Data Loaded
41 topics across 4 categories:
- **TV Features:** OLED, QLED, Mini-LED, Anti-Glare, 8K Resolution, HDR, etc.
- **TV Models:** Neo QLED, The Frame, Crystal UHD, Micro LED, etc.
- **TV Reviews & Brand:** Samsung TV Reviews, Best TVs 2025, TV Comparisons, etc.
- **TV Sizes:** 55 inch, 65 inch, 75 inch, 85 inch, etc.

#### Plain English
Before: Topics were written on a piece of paper (JSON file) that came with the dashboard.
Now: Topics are stored in a spreadsheet in the cloud (Supabase table) that anyone with access can edit. The dashboard reads from this spreadsheet every time it loads.

---

### Part 4: Citation Sources - Live Data Integration

#### What Changed
The Citation Sources table now fetches real data from SEMrush instead of using placeholder data.

#### Technical Details
```javascript
// Before: Static placeholder data
const citationSources = [
  { domain: 'techradar.com', type: 'Earned', citations: 156 },
  { domain: 'reddit.com', type: 'Social', citations: 89 },
  // ... hardcoded sample data
];

// After: Live data from SEMrush via proxy
async function fetchCitationSources() {
  const response = await fetch(SUPABASE_EDGE_URL + '/semrush-proxy', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      element_id: '28977430-d565-4529-97eb-2dfe2959b86b',
      project_id: '68917',
      filters: buildFilters()
    })
  });

  const data = await response.json();
  return data.blocks.data;  // 1,833 domains returned
}
```

#### SEMrush Element IDs Discovered
| Element ID | Name | Description |
|-----------|------|-------------|
| `28977430-d565-4529-97eb-2dfe2959b86b` | Source Visibility by Domain | Returns domains with their type, mentions, citations, visibility |
| `3c29aa85-4f06-4f14-a376-b02333c6e3fa` | Cited URLs | Returns specific URLs that have been cited, with prompts |
| `3a16b2b2-b227-4a41-9ef2-9c657e64d47e` | Topics | Returns topics with citation counts |

#### Response Data Structure
```javascript
// Each domain in the response has:
{
  "domain": "techradar.com",
  "domain_type": "Earned",     // Owned, Earned, Competitor, Social, Other
  "mentions": 234,             // Number of times domain mentioned
  "citations": 156,            // Number of citations from this domain
  "visibility": 72.5           // Visibility percentage
}
```

#### Plain English
Before: The table showed example data that never changed (like a demo mode).
Now: The table shows real data from SEMrush - 1,833 actual domains that are citing or mentioning Samsung in AI responses. When you change filters (date range, AI model), the data updates to match.

---

### Part 5: Topic Filter - Database Migration

#### What Changed
The Topic filter dropdown now loads topics from Supabase instead of a JSON file.

#### Technical Details
```javascript
// Before: Load from static JSON file
async function loadTopicFilter() {
  const response = await fetch('../assets/tv_prompts.json');
  const data = await response.json();
  populateDropdown(data.tagTree);
}

// After: Load from Supabase table
async function loadTopicFilter() {
  const response = await fetch(
    `${SUPABASE_URL}/rest/v1/tv_topics?select=category,tag&order=category,tag`,
    { headers: { 'apikey': ANON_KEY } }
  );
  const topics = await response.json();

  // Group by category and populate dropdown
  const grouped = groupByCategory(topics);
  populateDropdown(grouped);
}
```

#### Plain English
Before: The topic list was baked into a file that shipped with the dashboard.
Now: The topic list is pulled from our database each time the page loads. This means we can add new topics (like when Samsung releases a new TV model) without touching the dashboard code.

---

### Part 6: Files Modified

| File | Changes |
|------|---------|
| `clients/samsung/dashboards/geo-dashboard.html` | Updated Topic filter to query Supabase; Updated Citation Sources to use Edge Function proxy |

### New Supabase Resources Created

| Resource | Type | Purpose |
|----------|------|---------|
| `semrush-proxy` | Edge Function | Proxies SEMrush API calls with CORS headers |
| `tv_topics` | Table | Stores 41 TV topics for filter dropdown |

---

### Lessons Learned

1. **Edge Functions solve browser CORS issues elegantly:** Instead of complex workarounds or backend infrastructure, a simple serverless function can proxy API calls and add the necessary headers. The function is free for low traffic and scales automatically.

2. **Migrating static data to database enables dynamic updates:** Moving topics from a JSON file to a database table means content updates no longer require code deployments. This is especially useful for data that changes occasionally (new products, renamed categories).

3. **JWT verification can be disabled for public dashboards:** When building read-only public dashboards, requiring authentication adds unnecessary friction. Supabase Edge Functions can be configured to skip JWT verification for specific use cases.

4. **SEMrush API uses Element IDs for different data views:** Each "element" in the SEMrush dashboard (tables, charts) has a unique ID that can be queried via API. Inspecting network requests in browser DevTools reveals these IDs.

---

## 2026-01-29: GEO Dashboard - Topic Filter and Citation Sources Table

### Session Goals
Enhance the GEO Performance Dashboard with a Topic filter dropdown to filter data by TV-related topics, and add a Citation Sources table showing which domains are citing Samsung along with their type classification and sentiment data.

---

### Part 1: Overview

#### What Was Done
Added two major features to the GEO Dashboard: (1) a Topic filter that loads TV-related categories from a JSON file, and (2) a Citation Sources table that aggregates data from Supabase to show which websites are citing Samsung, what type of source they are, and whether the coverage is positive or negative.

#### Plain English
Think of the dashboard like a TV remote control. Before this update, you could only change the channel (date range) and volume (model filter). Now you can also filter by what show you want to watch (topic filter - like "OLED TVs" or "Gaming TVs"). Plus, we added a new display that shows you which websites are talking about Samsung, whether they are Samsung's own sites, news sites, social media, or competitor sites, and whether they are saying nice things or not.

---

### Part 2: Topic Filter

#### What We Built
A new dropdown filter in the filter bar that lets users filter the dashboard data by TV-related topics.

#### Technical Details
```javascript
// The filter loads topics from a JSON file
async function loadTopicFilter() {
  const response = await fetch('../assets/tv_prompts.json');
  const data = await response.json();

  // tagTree contains hierarchical categories
  const tagTree = data.tagTree;

  // Populate dropdown with optgroups for each category
  for (const category of Object.keys(tagTree)) {
    const optgroup = document.createElement('optgroup');
    optgroup.label = category;
    for (const tag of tagTree[category]) {
      const option = document.createElement('option');
      option.value = tag;
      option.textContent = tag;
      optgroup.appendChild(option);
    }
    topicSelect.appendChild(optgroup);
  }
}
```

#### Topic Categories
| Category | Example Tags |
|----------|-------------|
| TV Features | OLED, QLED, Mini-LED, Anti-Glare, 8K Resolution, HDR |
| TV Models | Neo QLED, The Frame, Crystal UHD, Micro LED |
| TV Reviews & Brand | Samsung TV Reviews, Best TVs 2025, TV Comparisons |
| Use Cases | Gaming TVs, Smart Home, Outdoor TV, Soundbar |

#### Plain English
The Topic filter is like a menu at a restaurant organized by food type. Instead of scrolling through a giant list of 58 different TV-related topics, they are organized into 4 main categories (Features, Models, Reviews, Use Cases). When you pick a category, you see only the topics in that group. This makes it much easier to find what you are looking for.

---

### Part 3: Citation Sources Table

#### What We Built
A sortable data table showing which domains (websites) are citing Samsung in AI responses, classified by source type with sentiment scores.

#### Technical Details
The table fetches data from two Supabase tables:
1. `semrush_cited_pages` - Contains citation counts per domain
2. `semrush_concept_mentions` - Contains sentiment data per domain

```javascript
async function fetchCitationSources() {
  // Fetch citations aggregated by domain
  const citationsResponse = await fetch(
    `${SUPABASE_URL}/rest/v1/semrush_cited_pages?select=domain,prompts_count`,
    { headers: { 'apikey': ANON_KEY } }
  );

  // Aggregate by domain and classify each one
  const domainData = {};
  for (const row of citations) {
    const domain = row.domain;
    if (!domainData[domain]) {
      domainData[domain] = {
        domain,
        type: classifyDomain(domain),
        citations: 0,
        mentions: 0,
        sentiment: null
      };
    }
    domainData[domain].citations += row.prompts_count;
  }
}
```

#### Domain Classification Logic
```javascript
function classifyDomain(domain) {
  if (domain.includes('samsung.com')) return 'Owned';
  if (['lg.com', 'sony.com', 'tcl.com', 'hisense.com'].some(d => domain.includes(d))) return 'Competitor';
  if (['reddit.com', 'youtube.com'].some(d => domain.includes(d))) return 'Social';
  return 'Earned';  // Default: news/media sites
}
```

#### Table Columns
| Column | Description | Sortable |
|--------|-------------|----------|
| Domain | Website URL (e.g., techradar.com) | Yes |
| Type | Owned / Earned / Social / Competitor | Yes |
| Citations | Number of times this domain cited Samsung | Yes |
| Mentions | Number of brand mentions from this domain | Yes |
| Sentiment | Percentage positive (green), negative (red), or neutral (gray) | Yes |

#### Sorting Implementation
```javascript
function setupTableSorting() {
  const headers = document.querySelectorAll('.citation-table th[data-sort]');
  headers.forEach(header => {
    header.addEventListener('click', () => {
      const column = header.dataset.sort;
      const currentOrder = header.dataset.order || 'desc';
      const newOrder = currentOrder === 'desc' ? 'asc' : 'desc';

      // Sort the data and re-render
      sortedData.sort((a, b) => {
        if (newOrder === 'asc') return a[column] - b[column];
        return b[column] - a[column];
      });

      renderCitationTable(sortedData);
    });
  });
}
```

#### Plain English
The Citation Sources table answers three questions the client asked:
1. **WHO is citing Samsung?** - The Domain column shows which websites (like techradar.com, reddit.com, samsung.com) appear when AI chatbots answer questions about TVs.
2. **WHAT type of source is it?** - The Type column shows whether it is Samsung's own website (Owned), a news/review site (Earned), social media (Social), or a competitor's site (Competitor).
3. **Is the coverage good or bad?** - The Sentiment column shows a colored badge: green means mostly positive, red means mostly negative, gray means neutral.

You can click any column header to sort the table. Click once to sort high-to-low, click again to sort low-to-high.

---

### Part 4: CSS Styles Added

#### Source Type Badges
```css
.source-type-badge {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.source-type-badge.owned { background: #e3f2fd; color: #1565c0; }
.source-type-badge.earned { background: #e8f5e9; color: #2e7d32; }
.source-type-badge.social { background: #fff3e0; color: #ef6c00; }
.source-type-badge.competitor { background: #fce4ec; color: #c62828; }
```

#### Sentiment Badges
```css
.sentiment-badge {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.sentiment-badge.positive { background: #c8e6c9; color: #2e7d32; }
.sentiment-badge.negative { background: #ffcdd2; color: #c62828; }
.sentiment-badge.neutral { background: #e0e0e0; color: #616161; }
```

#### Plain English
We added visual labels to make the data easier to scan:
- **Type badges** use different background colors so you can instantly tell the difference between Samsung's own content (blue), news coverage (green), social media (orange), and competitor sites (red).
- **Sentiment badges** use traffic light colors: green for good, red for bad, gray for neutral.

---

### Part 5: Files Modified

| File | Changes |
|------|---------|
| `clients/samsung/dashboards/geo-dashboard.html` | Added Topic filter dropdown, Citation Sources table, new CSS styles, new JavaScript functions |

---

### Part 6: Data Sources

#### tv_prompts.json Structure
```json
{
  "tagTree": {
    "TV Features": ["OLED", "QLED", "Mini-LED", "Anti-Glare", ...],
    "TV Models": ["Neo QLED", "The Frame", "Crystal UHD", ...],
    "TV Reviews & Brand": ["Samsung TV Reviews", "Best TVs 2025", ...],
    "Use Cases": ["Gaming TVs", "Smart Home", "Outdoor TV", ...]
  }
}
```

#### Supabase Tables Used
| Table | Purpose |
|-------|---------|
| `semrush_cited_pages` | Citation counts per URL/domain |
| `semrush_concept_mentions` | Sentiment data aggregated by domain |

---

### Lessons Learned

1. **Optgroups improve UX for long dropdowns:** Instead of a flat list of 58 topics, using `<optgroup>` to organize them into 4 categories makes the dropdown much easier to navigate.

2. **Domain classification should be explicit:** Rather than trying to use complex regex or external services, a simple list-based classification (Owned = samsung.com, Social = reddit/youtube, Competitor = lg/sony/etc., Earned = everything else) is clear and maintainable.

3. **Sortable tables need visual feedback:** Users need to know which column is currently sorted and in which direction. We use data attributes on headers to track sort state and toggle between ascending/descending on each click.

4. **Color-coded badges work better than numbers for quick scanning:** A green "72%" badge is faster to interpret than just "72%" in plain text when you are scanning a table for positive vs. negative sentiment.

---

## 2026-01-29: Samsung AI Visibility Dashboard - Supabase Integration and D3.js Visualizations

### Session Goals
Connect the Samsung AI Visibility Dashboard to live Supabase data and create new D3.js visualization templates for advanced chart types (heatmap, treemap, radar, sankey). Update existing components with live data fetching and document what data is available versus placeholder.

---

### Part 1: Overview

#### What Was Done
This session focused on making the Samsung dashboard "real" by connecting it to live data from Supabase and creating visualization templates for advanced chart types that Chart.js cannot handle. We also documented the current data status so developers know which parts use live data and which still need data sources.

#### Plain English
Think of the dashboard like a car dashboard. Before this update, all the gauges showed sample numbers that never changed. Now, some gauges (KPIs, line charts) show real numbers from our database. We also designed new gauges (heatmap, treemap, radar, sankey) for showing more complex information. And we created a document explaining which gauges work and which are still waiting for data.

---

### Part 2: Supabase Data Service Module

#### What We Created
A new JavaScript file at `clients/samsung/dashboards/js/supabase-data.js` that handles all communication with Supabase.

#### Why a Separate Module?
Before this, each component that needed data would have its own fetch code. This caused problems:
1. **Code duplication** - Same API URL and key repeated everywhere
2. **Inconsistent error handling** - Some components might crash, others might show blank
3. **Hard to update** - If the API changes, you would need to update many files

#### How It Works
```javascript
// The module provides functions like:
async function fetchKPIData(dateRange) { ... }
async function fetchMentionsTrend(dateRange, model) { ... }
async function fetchConceptData(dateRange) { ... }
```

Components import these functions and call them. The module handles:
- API authentication (Supabase anon key)
- Error handling (returns placeholder data on failure)
- Date filtering
- Response parsing

#### Plain English
Instead of every part of the dashboard knowing how to talk to the database, we created a "translator" that sits in between. Dashboard components say "I need the KPI numbers" and the translator handles all the technical details of getting that data from Supabase. If something goes wrong, the translator provides backup sample data so the dashboard does not break.

---

### Part 3: Main Dashboard KPI Cards - Live Data

#### What Changed
The 4 KPI cards at the top of the main dashboard now fetch real data from Supabase:
- Share of Voice
- Source Visibility
- Referral Traffic
- AI Visibility Score

#### Technical Details
```javascript
// Before: Static placeholder
const shareOfVoice = 65;

// After: Live data with fallback
const data = await fetchKPIData(selectedDateRange);
const shareOfVoice = data.shareOfVoice ?? 65; // Uses 65 if API fails
```

#### Data Source
KPI data comes from the `semrush_concept_mentions` table:
- Share of Voice: Calculated from Samsung mentions vs total mentions
- AI Visibility Score: Derived from visibility across AI models
- Other KPIs: Still placeholder (see Data Requirements section below)

#### Plain English
The big numbers at the top of the dashboard now update with real data. When you load the dashboard, it asks Supabase "what are Samsung's current numbers?" and displays them. If the database is down or slow, the dashboard shows sample numbers instead of crashing or showing nothing.

---

### Part 4: New D3.js Visualization Templates

#### Why D3.js for These Charts?
Chart.js is great for standard charts (bar, line, pie, donut). But some visualization types need more control:
- **Heatmap** - Grid of colored cells showing intensity
- **Treemap** - Rectangles sized by value, nested by category
- **Radar** - Spider/web chart comparing multiple dimensions
- **Sankey** - Flow diagram showing how values move between categories

Chart.js does not support treemap or sankey out of the box. D3.js lets us build exactly what we need.

#### Plain English
Chart.js is like a pre-built IKEA bookshelf - easy to assemble, looks good, but you cannot change the dimensions. D3.js is like raw lumber and tools - you can build anything, but it takes more work. For specialized charts like sankey diagrams (which show how things flow from one category to another), we need the lumber-and-tools approach.

---

### Part 5: Brand Comparison Heatmap

#### Template File
`clients/samsung/templates/brand-heatmap.html`

#### What It Shows
A grid where:
- Rows = Brands (Samsung, LG, Sony, TCL, Hisense)
- Columns = Concept categories (Picture Quality, Smart Features, Gaming, etc.)
- Cell color = Visibility score (darker = higher visibility)

#### Use Case
Quickly see where Samsung leads or lags compared to competitors. For example: "Samsung dominates Picture Quality and Smart Features, but LG leads in Gaming."

#### Technical Details
- Uses D3.js `d3.scaleSequential` for color gradients
- Hover reveals exact values
- Click on cell to filter related prompts (future feature)

#### Plain English
Imagine a spreadsheet where instead of numbers, each cell is colored based on the value - light green for low, dark green for high. This makes it easy to spot patterns at a glance. "Where is Samsung winning? Look for the darkest cells in the Samsung row."

---

### Part 6: Sentiment Treemap

#### Template File
`clients/samsung/templates/sentiment-treemap.html`

#### What It Shows
Rectangles representing sentiment categories:
- Large rectangles = More mentions
- Colors: Green = Positive, Gray = Neutral, Red = Negative
- Nested: Can drill into categories (e.g., Positive > Picture Quality > OLED)

#### Use Case
Understand what drives positive and negative sentiment. "Most positive mentions are about picture quality. Most negative mentions are about price."

#### Technical Details
- Uses D3.js `d3.treemap()` layout algorithm
- Rectangles sized by mention count
- Click to zoom into subcategory

#### Plain English
If you had to organize boxes in a room, you would give bigger boxes to bigger items. The treemap does this with data - bigger rectangles mean more mentions. The color tells you if those mentions are good (green), neutral (gray), or bad (red). Click on a box to zoom in and see what is inside.

---

### Part 7: Model Performance Radar Chart

#### Template File
`clients/samsung/templates/model-radar.html`

#### What It Shows
A spider/web chart comparing AI models across dimensions:
- Axes: Visibility, Mention Volume, Sentiment, Position, Citation Rate
- Lines: One per AI model (SearchGPT, Google AI Overview, Google AI Mode)

#### Use Case
See which AI model treats Samsung best overall. "Google AI Overview gives higher visibility but worse positions. SearchGPT gives better positions but lower volume."

#### Technical Details
- Uses D3.js with polar coordinates
- Each axis scaled 0-100
- Hover on line to highlight that model
- Legend toggles models on/off

#### Plain English
Think of comparing athletes across different skills - speed, strength, endurance, etc. A radar chart shows all skills at once as a shape. A well-rounded athlete has a big, even shape. A specialist has spikes in certain areas. This chart shows how Samsung performs across different metrics on each AI platform.

---

### Part 8: Citation Flow Sankey Diagram

#### Template File
`clients/samsung/templates/citation-sankey.html`

#### What It Shows
Flowing lines showing how content leads to citations:
- Left side: Content types (Blog posts, Product pages, Support articles)
- Middle: Topics (OLED TV, Smart TV Features, Gaming)
- Right side: Citation types (Direct citation, Paraphrase, Link)

#### Use Case
Understand which content generates citations. "Product pages generate most direct citations, but blog posts get more paraphrased citations."

#### Technical Details
- Uses D3-sankey plugin
- Flow width = number of citations
- Hover highlights specific flow
- Colors by content type

#### Plain English
Imagine water flowing through pipes. The sankey diagram shows how "mentions" flow from Samsung's content through topics to citations. Thick pipes mean more flow. You can trace the path: "This blog post about OLED TVs led to these direct citations in ChatGPT responses."

---

### Part 9: Line Charts Live Data Update

#### What Changed
The existing line charts template (`templates/line-charts.html`) now fetches data from Supabase instead of using hardcoded sample data.

#### Technical Changes
```javascript
// Added Supabase fetch with fallback
async function loadChartData() {
  try {
    const response = await fetch(
      `${SUPABASE_URL}/rest/v1/semrush_concept_mentions?select=date,llm,mentions&order=date.asc`,
      { headers: { 'apikey': SUPABASE_ANON_KEY } }
    );
    const data = await response.json();
    return processForChart(data);
  } catch (error) {
    console.warn('Using placeholder data:', error);
    return PLACEHOLDER_DATA;
  }
}
```

#### What the Charts Show
- Daily mentions trend by AI model
- 43 days of data (2025-12-18 to 2026-01-29)
- Separate lines for SearchGPT, Google AI Overview, Google AI Mode

#### Plain English
The line charts that show "mentions over time" used to show fake sample data that never changed. Now they show real data from our database. If the database is unavailable, they fall back to the sample data so the chart still renders.

---

### Part 10: Placeholder Data Notes

#### Where Notes Were Added
Several dashboard sections now display notes indicating placeholder data status:

1. **Sunburst Chart Section**
   - Note: "Prompt category data will be populated from SEMrush URL Prompts table"
   - Data exists in Supabase but transformation logic not yet implemented

2. **Prompt Rankings Section**
   - Note: "Position and visibility data require additional SEMrush API integration"
   - Position data not currently available from SEMrush endpoints we have tested

3. **Source Analysis Section**
   - Note: "Citation and referral data require GA4 integration"
   - Referral traffic needs Google Analytics connection

#### Why Add These Notes?
Stakeholders viewing the dashboard need to know what is real vs sample. Developers need to know what work remains.

#### Plain English
When you look at a dashboard, you expect the numbers to be real. These notes are like labels saying "sample data - real numbers coming soon." This prevents confusion where someone makes a business decision based on placeholder numbers.

---

### Part 11: GEO Dashboard D3.js Preparation

#### What Changed
Added the D3.js v7 script tag to `dashboards/geo-dashboard.html`:

```html
<script src="https://d3js.org/d3.v7.min.js"></script>
```

#### Why?
The GEO dashboard currently uses Chart.js for all visualizations. This works well. But the main dashboard (`scom-overview.html`) uses D3.js for complex charts. Adding D3 to the GEO dashboard:
1. Prepares for future migration if needed
2. Enables adding D3-specific charts later
3. Maintains consistency with main dashboard approach

#### Current State
- GEO dashboard still uses Chart.js for all 5 charts
- GEO dashboard connects to live Supabase data (already working)
- D3.js is available but not yet used

#### Plain English
Adding the D3 library is like installing a new app on your phone but not opening it yet. The GEO dashboard works fine with Chart.js. But if we want to add a sankey diagram or heatmap later, D3 is ready to go without needing another update.

---

### Part 12: Component Library Updates

#### File Modified
`clients/samsung/templates/base/components.html`

#### CSS Added
New styles for the 4 visualization types:

```css
/* Heatmap */
.heatmap-cell { ... }
.heatmap-axis { ... }
.heatmap-legend { ... }

/* Treemap */
.treemap-rect { ... }
.treemap-label { ... }

/* Radar */
.radar-axis { ... }
.radar-polygon { ... }

/* Sankey */
.sankey-node { ... }
.sankey-link { ... }
```

#### Why in components.html?
This file contains reusable styles for all dashboard components. By adding visualization styles here, any dashboard can use them by including components.html.

#### Plain English
The components.html file is like a CSS recipe book. When you want to make a heatmap, you include this file and the styling is ready. No need to rewrite colors, spacing, and hover effects for each new heatmap.

---

### Part 13: Style Guide Updates

#### File Modified
`clients/samsung/dashboards/style-guide.html`

#### Sections Added
Documentation for each new visualization type:
- Brand Comparison Heatmap section with example and configuration options
- Sentiment Treemap section with usage notes
- Model Performance Radar section with axis configuration
- Citation Flow Sankey section with node/link styling

#### Purpose
The style guide serves as a reference for developers and designers. Adding these sections ensures future implementers understand how to use the new visualizations correctly.

#### Plain English
The style guide is like an instruction manual for the dashboard. When someone new joins the team and needs to add a heatmap, they check the style guide to see how it should look and what options are available.

---

### Part 14: DATA-REQUIREMENTS.md Created

#### New File
`clients/samsung/DATA-REQUIREMENTS.md`

#### Contents
A comprehensive document listing:

1. **Available Data (Live from Supabase)**
   - `semrush_concept_mentions` - 57,831 rows, concepts by model by date
   - `semrush_cited_pages` - 84,856 rows, URLs and citation counts
   - `semrush_url_prompts` - 37,234 rows, prompts per URL

2. **Placeholder Data (Not Yet Available)**
   - Referral Traffic - Requires GA4 integration
   - Position Data - Not available from current SEMrush endpoints
   - Sentiment by Brand - Available in API but not loaded to Supabase

3. **Component Status Matrix**
   | Component | Data Source | Status |
   |-----------|-------------|--------|
   | KPI Cards (SoV) | concept_mentions | Live |
   | KPI Cards (Referral) | GA4 | Placeholder |
   | Line Charts | concept_mentions | Live |
   | Sunburst | url_prompts | Needs transform |
   | Prompt Rankings | SEMrush API | Placeholder |
   | Source Analysis | GA4 + cited_pages | Partial |

4. **Integration Roadmap**
   - Priority 1: Complete sunburst data transformation
   - Priority 2: Add GA4 integration for referral metrics
   - Priority 3: Fetch position data from SEMrush (if endpoint exists)

#### Plain English
This document is like an inventory checklist for the dashboard. It says "we have these ingredients in the pantry" (live data), "we need to buy these ingredients" (placeholder data), and "here is what we can cook with what we have" (component status). Developers use it to know what work remains.

---

### Part 15: Files Summary

#### Files Created (6)
| File | Description |
|------|-------------|
| `clients/samsung/dashboards/js/supabase-data.js` | Centralized Supabase data fetching module |
| `clients/samsung/templates/brand-heatmap.html` | D3.js Brand Comparison Heatmap template |
| `clients/samsung/templates/sentiment-treemap.html` | D3.js Sentiment Treemap template |
| `clients/samsung/templates/model-radar.html` | D3.js Model Performance Radar Chart template |
| `clients/samsung/templates/citation-sankey.html` | D3.js Citation Flow Sankey Diagram template |
| `clients/samsung/DATA-REQUIREMENTS.md` | Data availability and integration status document |

#### Files Modified (6)
| File | Changes |
|------|---------|
| `clients/samsung/templates/line-charts.html` | Added Supabase fetch with placeholder fallback |
| `clients/samsung/templates/sunburst-prompts.html` | Added placeholder data note |
| `clients/samsung/templates/base/components.html` | Added CSS for heatmap, treemap, radar, sankey |
| `clients/samsung/dashboards/style-guide.html` | Added documentation for new visualization types |
| `clients/samsung/dashboards/geo-dashboard.html` | Added D3.js v7 script tag |
| `clients/samsung/dashboards/scom-overview.html` | Added placeholder notes to sections |

---

### Part 16: Data Status Summary

#### What Works Now (Live Data)
| Component | Data Table | Rows |
|-----------|------------|------|
| Share of Voice KPI | semrush_concept_mentions | 57,831 |
| Line Charts (Mentions Trend) | semrush_concept_mentions | 57,831 |
| GEO Dashboard (all charts) | semrush_concept_mentions | 57,831 |

#### What Needs Work (Placeholder)
| Component | Needed Data | Blocker |
|-----------|-------------|---------|
| Referral Traffic KPI | GA4 sessions | No GA4 integration |
| Position Data (all) | SEMrush positions | API endpoint unknown |
| Prompt Rankings Table | Prompt performance | Multiple data sources needed |
| Source Analysis | Citations + GA4 | GA4 integration + transform |

#### What is Ready but Not Connected
| Component | Data Available | Status |
|-----------|----------------|--------|
| Sunburst Categories | semrush_url_prompts | Transform logic needed |
| Cited Pages Analysis | semrush_cited_pages | Component needs update |

#### Plain English
About 40% of the dashboard now shows real data (KPIs and line charts). The other 60% shows sample data while we figure out how to get position metrics and connect Google Analytics. The good news is we have most of the raw data in Supabase - we just need to transform and connect it.

---

### Lessons Learned

1. **Centralized data modules prevent duplication.** When multiple components need the same data, a shared module is easier to maintain than copy-pasted fetch calls.

2. **Fallback patterns are essential.** Dashboards that crash when data is unavailable frustrate users. Always have sample data ready as a fallback.

3. **D3.js vs Chart.js is not either/or.** Use Chart.js for standard charts (fast, easy), D3.js for custom visualizations (flexible, more work). Both can coexist.

4. **Document data status explicitly.** A data requirements document prevents confusion about what is real vs placeholder. Stakeholders appreciate knowing what they are looking at.

5. **Prepare for future needs.** Adding D3.js to the GEO dashboard costs nothing now but saves time later if we need advanced visualizations.

6. **Sample data should look realistic.** Placeholder numbers should be in reasonable ranges so stakeholders can see how the dashboard will look with real data.

---

## 2026-01-29: SEMrush Data Definitions Documented

### Session Goals
Document the official SEMrush definitions for Concepts and Topics based on direct communication with SEMrush support. This clarifies how SEMrush measures AI visibility metrics and validates our current data interpretation.

---

### Part 1: Why This Matters

#### The Question We Had
When looking at the concept mentions data, Samsung had 44.8% Share of Voice while competitors ranged from 9.8% to 19.0%. We needed to understand: Is this real, or is there a data problem?

#### Plain English
Imagine you are tracking how often different TV brands get mentioned in AI chatbot conversations. Samsung shows up nearly half the time, while LG only shows up 19% of the time. That seems like a big gap. Is Samsung really that dominant, or is something wrong with how we are counting?

---

### Part 2: SEMrush Concepts Definition

#### Official Definition (from SEMrush Support)
Concepts are the specific qualities and features AI models use when describing products and brands. SEMrush analyzes AI answers to understand the different themes and attributes AI is using to evaluate a product.

#### Examples
| Product Type | Example Concepts |
|--------------|------------------|
| Mascara | "clump-free application", "volume", "lengthening" |
| SUV | "safety features", "fuel efficiency", "cargo space" |
| TV | "picture quality", "smart TV features", "OLED technology" |

#### Key Detail: Sentiment
Each concept-product relationship carries sentiment, revealing whether AI frames that attribute positively, neutrally, or negatively. For example, AI might mention Samsung's "picture quality" positively but mention a competitor's "price point" negatively.

#### Plain English
Think of concepts like the vocabulary AI uses to describe products. When ChatGPT talks about TVs, it might say things like "Samsung TVs have excellent picture quality" or "this model has great smart TV features." Each of those qualities (picture quality, smart TV features) is a concept. SEMrush tracks which concepts get associated with which brands, and whether the AI is saying good or bad things about them.

---

### Part 3: SEMrush Topics Definition

#### Official Definition (from SEMrush Support)
Topics are used to estimate Volume for prompts. Unlike keywords, individual prompts are often too specific and unique to measure directly. SEMrush calculates topic-level volume by grouping related prompts that move in the same "semantic direction."

#### How Volume is Estimated
1. SEMrush combines third-party data on real user interactions with AI platforms
2. They apply machine learning models to the data
3. Topics are generated from their database of over 250 million prompts
4. Individual prompts are associated with these topics to provide volume estimates

#### Plain English
When someone types "What is the best 65-inch OLED TV for gaming?" into ChatGPT, that exact phrase probably has not been searched enough times to measure. But SEMrush groups it with similar questions like "Best gaming TV 2026" and "OLED vs QLED for gaming" into a Topic called something like "Gaming TVs." Then they can estimate how popular that topic is overall by looking at real usage data from AI platforms.

---

### Part 4: Current Data in Supabase

#### Table: `semrush_concept_mentions`
| Metric | Value |
|--------|-------|
| Total records | ~152,000 |
| Date range | 2025-12-18 to 2026-01-29 (43 days) |
| AI models tracked | ChatGPT (search-gpt), Google AI Overview, Google AI Mode |

#### Brand Breakdown
| Brand | Share of Voice | Unique Concepts |
|-------|---------------|-----------------|
| Samsung | 44.8% | 12,884 |
| LG | 19.0% | 6,894 |
| TCL | 14.7% | 5,234 |
| Sony | 11.8% | 4,567 |
| Hisense | 9.8% | 3,778 |

#### Why Samsung Has Higher Share of Voice
Samsung's 44.8% SoV is legitimate. It reflects that AI models discuss Samsung with more product attributes and features than competitors. Samsung has 12,884 unique concepts associated with it, nearly double the next competitor (LG with 6,894). This could be because:
1. Samsung has a broader product range (TVs, phones, appliances, etc.)
2. Samsung appears more frequently in training data for AI models
3. Samsung's products have more features worth discussing

#### Plain English
Samsung is not "cheating" the system. When AI chatbots talk about TVs, they simply have more things to say about Samsung than about other brands. Samsung might get mentioned for picture quality, smart features, gaming mode, design, and price, while a smaller brand might only get mentioned for price and basic features. More concepts = more mentions = higher Share of Voice.

---

### Part 5: Files Updated

| File | Changes |
|------|---------|
| `DEVELOPMENT.md` | Added session summary and changelog entry |
| `docs/build-log.md` | Added this detailed session entry |
| `clients/samsung/docs/data-definitions.md` | Added official SEMrush definitions section |

---

### Lessons Learned

1. **Always verify metrics with the source:** When data looks surprising (Samsung at 44.8% vs others at 10-19%), do not assume it is wrong. Check with the data provider to understand the methodology.

2. **Share of Voice is about depth, not just frequency:** Higher SoV does not just mean "mentioned more often" - it means AI models have more to say about you. This is a content richness signal.

3. **Topics vs Keywords:** Unlike traditional SEO where you can measure exact keyword volumes, AI prompt volume must be estimated at the topic level because individual prompts are too specific and varied.

4. **Document external context:** Information from vendor support conversations is valuable context that should be captured in documentation, not just stored in email threads.

---

## 2026-01-29: GEO Performance Dashboard Created

### Session Goals
Build a GEO (Generative Engine Optimization) Performance Dashboard for Samsung that visualizes AI visibility metrics from the Supabase `semrush_concept_mentions` table. The dashboard should show KPIs, trends, and breakdowns by AI model.

---

### Part 1: What Was Done

#### Overview
Created a complete, self-contained dashboard at `clients/samsung/dashboards/geo-dashboard.html` with 4 KPI cards and 5 interactive Chart.js visualizations. The dashboard connects directly to Supabase to fetch live data from the concept mentions table (~58k rows).

#### Plain English
We built a dashboard that shows how visible Samsung is across different AI chatbots (like ChatGPT and Google AI Overview). Think of it like a scoreboard that answers questions like: "How often does Samsung get mentioned by AI?", "Is sentiment positive or negative?", and "Which topics are most associated with Samsung?" The dashboard updates with real data from our database.

---

### Part 2: KPI Cards

#### The 4 KPIs
| KPI | Description | Plain English |
|-----|-------------|---------------|
| Share of Voice | Percentage of Samsung mentions vs competitors | If all AI chatbot mentions about TVs were a pie, how big is Samsung's slice? |
| Visibility Score | Composite metric of AI presence (0-100) | A single number summarizing how visible Samsung is across all AI platforms |
| Sentiment Score | Positive/neutral/negative breakdown | Are AI chatbots saying good or bad things about Samsung? |
| Total Mentions | Raw count of mentions | Simply, how many times did AI chatbots mention Samsung? |

#### Implementation Notes
- Each KPI card shows a main value, a trend indicator (up/down arrow), and a sparkline
- Cards are responsive and stack on mobile devices
- Currently showing placeholder values; will be calculated from aggregated data in future iterations

---

### Part 3: Chart.js Visualizations

#### Why Chart.js Instead of D3.js
The previous Samsung dashboard (`scom-overview.html`) used D3.js for complex visualizations like sunburst charts. For this dashboard, we chose Chart.js because:
1. **Simpler API** - Standard chart types (donut, bar, line) do not need D3's low-level control
2. **Faster implementation** - Chart.js handles animations, tooltips, and legends automatically
3. **Smaller learning curve** - Easier for future maintainers to modify

#### Plain English
D3.js is like having a professional kitchen with every tool imaginable - powerful but complex. Chart.js is like a well-equipped home kitchen - easier to use and perfectly adequate for everyday cooking. Since we only needed standard charts (donuts, bars, lines), the simpler tool was the better choice.

---

### Part 4: The 5 Visualizations

#### 1. Share of Voice Donut Chart
- **Shows:** Model breakdown when single brand (how mentions split across SearchGPT vs Google AI Overview vs Google AI Mode)
- **Future:** Will show brand comparison when competitor data is added (Samsung vs LG vs Sony)
- **Colors:** Uses Samsung brand palette

#### 2. Sentiment Distribution Donut Chart
- **Shows:** Positive / Neutral / Negative mention breakdown
- **Colors:** Green for positive, gray for neutral, red for negative
- **Center:** Displays total or dominant sentiment percentage

#### 3. Visibility by AI Model Bar Chart
- **Shows:** Horizontal bars comparing visibility scores across AI platforms
- **Models:** SearchGPT, Google AI Overview, Google AI Mode
- **Plain English:** Which AI chatbot talks about Samsung the most?

#### 4. Mentions Trend Line Chart
- **Shows:** Daily Samsung mention count over time
- **Period:** 2025-12-18 to 2026-01-29 (43 days)
- **Plain English:** Is Samsung getting mentioned more or less over time?

#### 5. Top Topics Horizontal Bar Chart
- **Shows:** Top 10 concept categories by total mention count
- **Examples:** "OLED TV technology", "Smart TV features", "TV comparison"
- **Plain English:** What topics does AI associate most with Samsung?

---

### Part 5: Filter Bar

#### Filter Controls
| Filter | Options | Default |
|--------|---------|---------|
| Date Range | Last 7 days, Last 14 days, Last 30 days, All time | All time |
| Model | All models, SearchGPT, Google AI Overview, Google AI Mode | All models |

#### How Filters Work
1. User selects filter option
2. JavaScript refetches data from Supabase with filter applied
3. All charts update simultaneously with new data
4. Filter state is preserved during the session

#### Plain English
The filter bar lets you slice the data different ways. Want to see just the last week? Click "Last 7 days". Want to see only what ChatGPT (SearchGPT) is saying? Select it from the model dropdown. All the charts update instantly to show you that specific view.

---

### Part 6: Supabase Integration

#### Technical Details
| Setting | Value |
|---------|-------|
| URL | `https://[project-ref].supabase.co` |
| Table | `semrush_concept_mentions` |
| Auth | Anon key (public read-only) |
| Rows | ~58,000 |
| Date range | 2025-12-18 to 2026-01-29 |

#### Query Pattern
```javascript
// Fetch mentions grouped by model for a date range
const response = await fetch(
  `${SUPABASE_URL}/rest/v1/semrush_concept_mentions?select=llm,mentions&date=gte.${startDate}&date=lte.${endDate}`,
  { headers: { 'apikey': ANON_KEY } }
);
```

#### Plain English
The dashboard talks directly to our Supabase database to get the latest data. It uses a public read-only key, which means anyone can view the data but nobody can modify it. This is safe because the concept mentions data is not sensitive.

---

### Part 7: Design Decisions

#### 1. Single HTML File (No Template Assembly)
Previous Samsung dashboards use a template assembly system where components are stored separately and combined by a Python script. For this dashboard, we used a single self-contained HTML file because:
- Simpler deployment (just copy one file)
- No build step required
- Easier to iterate quickly during development
- All dependencies loaded via CDN

#### 2. Graceful Single-Brand Handling
Currently, the database only contains Samsung data. The Share of Voice chart handles this gracefully by showing model breakdown instead of brand comparison. When competitor data is added later, the chart will automatically switch to brand comparison mode.

#### 3. Responsive Design
The dashboard uses CSS Grid with media queries to adapt to different screen sizes:
- **Desktop:** 2-column chart layout
- **Tablet:** Mixed layout
- **Mobile:** Single column, stacked components

---

### Part 8: Files Created

| File | Description |
|------|-------------|
| `clients/samsung/dashboards/geo-dashboard.html` | Complete GEO Performance Dashboard (single file, ~800 lines) |

---

### Part 9: Data Source

#### semrush_concept_mentions Table
This dashboard uses data from the concept mentions pipeline completed earlier today:

| Metric | Value |
|--------|-------|
| Total rows | 57,831 |
| Date range | 2025-12-18 to 2026-01-29 |
| Models | search-gpt, google-ai-mode, google-ai-overview |

The data shows how often different concepts (topics) appear in AI model responses. See the "Concept Mentions Data Pipeline Complete" session entry below for full details on how this data was collected.

---

### Lessons Learned

1. **Chart.js vs D3.js tradeoff:** D3.js gives total control but requires more code. Chart.js is faster for standard charts. Choose based on complexity needs.

2. **Single-file simplicity:** For standalone dashboards that do not need to share components, a single HTML file is easier to develop and deploy.

3. **Graceful degradation:** Design for the data you have, but make it ready for the data you will have. The brand comparison will "just work" when competitor data arrives.

4. **CDN dependencies:** Loading Chart.js from CDN means no local dependencies to manage, but requires internet connectivity.

5. **Anon key security:** Supabase anon keys are designed for public read access. Safe for non-sensitive data, but do not expose write-enabled keys.

---

## 2026-01-29: Concept Mentions Data Pipeline Complete

### Session Goals
Build a complete data pipeline to fetch and store SEMrush Concept Mentions data in Supabase. This data tracks how frequently specific concepts (topics like "OLED TV" or "smart TV features") appear across different AI model responses over time.

---

### Part 1: What Was Done

#### Overview
Created a Supabase table via migration, built fetch and load scripts, and successfully loaded 57,831 rows of concept mention data. This was significantly more data than the initial estimate of 19,350 rows because the actual date range and concept counts exceeded expectations.

#### Plain English
We wanted to track how often different topics (concepts) appear when AI chatbots answer questions. For example, how many times does "OLED TV" get mentioned by ChatGPT versus Google AI Overview? This data helps Samsung understand which product concepts are most visible in AI responses and how that changes over time.

---

### Part 2: Database Setup

#### Supabase Table: semrush_concept_mentions

Created via Supabase migration with the following schema:

| Column | Type | Description |
|--------|------|-------------|
| id | uuid | Auto-generated primary key |
| concept | text | The concept/topic name (e.g., "OLED TV technology") |
| llm | text | AI model name (search-gpt, google-ai-mode, google-ai-overview) |
| mentions | integer | Number of times the concept was mentioned |
| date | date | The date of the data point |
| fetched_at | timestamptz | When the data was fetched from SEMrush |

#### Constraints and Indexes
- **Unique constraint:** `(concept, llm, date)` - Prevents duplicate entries for the same concept/model/date combination
- **Indexes:** concept, llm, date - Enables fast filtering and aggregation queries

#### Plain English
The database table stores one row for each combination of concept + AI model + date. For example, there would be separate rows for "OLED TV" on Google AI Overview on January 15 and "OLED TV" on SearchGPT on January 15. The unique constraint means if we fetch the same data again, it updates the existing row instead of creating a duplicate.

---

### Part 3: Fetch Script

#### Script: fetch_concept_mentions.py
Location: `clients/samsung/fetch_concept_mentions.py`

#### SEMrush API Details
| Parameter | Value |
|-----------|-------|
| Base URL | `https://api.semrush.com/apis/v4-raw/external-api/v1` |
| Product | `ai` |
| Element ID | `e0f20fc8-83e6-4c66-a55b-23bf64a2ac6f` |
| Element Name | Concept Mentions |

#### How It Works
1. Queries the SEMrush Concept Mentions endpoint for each date in the range
2. Iterates through all three AI models (search-gpt, google-ai-mode, google-ai-overview)
3. Saves all data to a single JSON file: `clients/samsung/data/concept_mentions.json`
4. Handles pagination for dates with many concepts

#### Plain English
The fetch script asks SEMrush "what concepts were mentioned by each AI model on each day?" It goes through every day from December 18 to January 29 and saves all the answers to a JSON file. This is like downloading a daily report for each AI chatbot showing which topics they talked about.

---

### Part 4: Load Script

#### Script: load_concept_mentions.py
Location: `clients/samsung/load_concept_mentions.py`

#### How It Works
1. Reads the JSON file created by the fetch script
2. Transforms each record into the Supabase table format
3. Upserts records in batches using the Supabase REST API
4. Uses the unique constraint to update existing records instead of creating duplicates

#### Plain English
The load script reads the JSON file and pushes the data into Supabase. It uses "upsert" which means "insert if new, update if exists." This makes it safe to run the script multiple times without creating duplicate data.

---

### Part 5: Results Summary

#### Data Loaded
| Metric | Value |
|--------|-------|
| **Total rows** | 57,831 |
| **Date range** | 2025-12-18 to 2026-01-29 |
| **Days covered** | 43 days |

#### Breakdown by Model
| AI Model | Rows |
|----------|------|
| google-ai-mode | 21,652 |
| search-gpt | 19,837 |
| google-ai-overview | 16,342 |

#### Why More Than Expected
Initial estimate was 19,350 rows based on ~150 concepts/day x 3 models x 43 days. Actual count was 57,831 because:
1. Concept count per day varied significantly
2. Major spike around January 15 increased concept counts ~5x

---

### Part 6: Major Finding - January 15 Spike

#### The Discovery
While loading data, we observed that concept counts jumped dramatically around January 15:

| Period | Concepts/Day/Model |
|--------|-------------------|
| Before Jan 15 | ~150 |
| After Jan 15 | ~1,000 |

This is approximately a **5x increase** in tracked concepts per day per model.

#### Possible Explanations
1. **SEMrush expanded tracking:** They may have added more concepts to their monitoring
2. **AI model behavior change:** The AI models may have started mentioning more diverse concepts
3. **Data coverage change:** SEMrush may have started covering a larger set of prompts

#### Plain English
Something big happened around January 15. Before that date, SEMrush was tracking about 150 different concepts per AI model per day. After that date, they were tracking about 1,000 concepts per day. This is either because SEMrush started tracking more topics, or because the AI chatbots suddenly started talking about more diverse topics. Either way, the data after January 15 is much richer and more detailed.

---

### Part 7: Files Created

| File | Description |
|------|-------------|
| `clients/samsung/fetch_concept_mentions.py` | Script to fetch data from SEMrush API |
| `clients/samsung/load_concept_mentions.py` | Script to load JSON data into Supabase |
| `clients/samsung/data/concept_mentions.json` | Raw data file (57,831 records) |

---

### Part 8: Documentation Updates

#### semrush-api-endpoints.md
Added Concept Mentions endpoint documentation:
- Element ID and product
- Request payload structure
- Response field descriptions
- Model values (search-gpt, google-ai-mode, google-ai-overview)

#### docs/data-definitions.md
Added `semrush_concept_mentions` table documentation:
- Full schema with all columns
- Unique constraint explanation
- Index definitions
- Example queries for analysis

---

### Lessons Learned

1. **Estimates can be way off:** Initial estimate of 19,350 rows turned into 57,831 actual rows. Always account for variability in data volumes.

2. **Look for anomalies:** The January 15 spike was unexpected but significant. Anomalies in data often reveal important changes in the source system.

3. **Document date ranges:** The data starts on 2025-12-18, not earlier. This is an important limitation to note for analysis.

4. **Model naming inconsistency:** SEMrush uses different model names in different endpoints (e.g., "search-gpt" here vs "CHAT_GPT" in Citations by Model). Need to map these when joining data.

5. **Upsert is essential:** For data pipelines that may run multiple times, always use upsert to avoid duplicates.

---

## 2026-01-29: SEMrush Citations by Model API Testing

### Session Goals
Test and document the SEMrush Citations by Model API endpoint to understand how citation counts are distributed across different AI models (ChatGPT, Gemini, Google AI Overview, etc.) over time.

---

### Part 1: What Was Done

#### Overview
Tested the SEMrush Citations by Model endpoint (`c57c36a4-cb53-49c3-bbe6-6467881206e3`) to understand its response structure, date filtering behavior, and data characteristics. Discovered that the endpoint returns a fixed time series regardless of the date filter passed.

#### Plain English
We wanted to find out which AI chatbots cite Samsung content the most. SEMrush tracks this data across different AI models like ChatGPT, Google Gemini, and Google AI Overview. We tested the API to understand what data it returns and found some surprising behavior: the date filter does not actually filter the data, it always returns the same historical snapshots.

---

### Part 2: Endpoint Details

#### API Information
| Parameter | Value |
|-----------|-------|
| Base URL | `https://api.semrush.com/apis/v4-raw/external-api/v1` |
| Product | `ai` |
| Element ID | `c57c36a4-cb53-49c3-bbe6-6467881206e3` |
| Element Name | Citations by Model |

#### Response Structure
The API returns 20 rows organized as:
- **4 time points** (historical snapshots)
- **5 AI models** per time point
- Fields: `bar` (model name), `value` (citation count)

#### AI Models Tracked
| Model | Description |
|-------|-------------|
| UNSPECIFIED | Citations from unidentified AI sources |
| GOOGLE_AI_OVERVIEW | Google AI Overview in search results |
| GEMINI | Google Gemini chatbot |
| CHAT_GPT | OpenAI ChatGPT |
| GOOGLE_AI_MODE | Google AI Mode |

#### Plain English
The API tells us how many times Samsung pages were cited by each AI model. It tracks 5 different AI services and provides 4 data snapshots over time. "UNSPECIFIED" means the citation came from an AI source that could not be identified.

---

### Part 3: Date Filter Discovery

#### The Problem
We expected the `date` filter to control which time period the API returns. Testing revealed this is NOT the case.

#### Testing Performed
| Date Passed | Result |
|-------------|--------|
| 2025-11-30 | Returns same 20 rows |
| 2025-12-15 | Returns same 20 rows |
| 2025-12-31 | Returns same 20 rows |

All three dates returned **identical data**. The response always includes the same 4 historical time points regardless of what date is specified.

#### Conclusion
The `date` filter has **no effect** on this endpoint. The API returns a fixed time series snapshot that represents whatever historical data SEMrush has collected.

#### Plain English
We tried asking for data from different dates (November, mid-December, end of December) but always got exactly the same answer. This means the "date filter" does not actually filter anything for this endpoint. It is like ordering a pizza and asking for "no olives" but getting the same pizza every time regardless. This is either a bug or the endpoint is designed to always return the full historical data.

---

### Part 4: Sample Data Analysis

#### Latest Time Point Citation Counts
| Model | Citations | Percentage |
|-------|-----------|------------|
| UNSPECIFIED | 398,339 | 50.1% |
| GOOGLE_AI_OVERVIEW | 167,121 | 21.0% |
| GEMINI | 86,641 | 10.9% |
| CHAT_GPT | 73,616 | 9.3% |
| GOOGLE_AI_MODE | 70,961 | 8.9% |
| **Total** | **796,678** | **100%** |

#### Key Observations

1. **UNSPECIFIED dominates:** Half of all citations come from unidentified AI sources. This could be AI tools that do not clearly identify themselves, or edge cases in SEMrush's tracking.

2. **Google products combined:** Google AI Overview + Gemini + AI Mode = 324,723 citations (40.8% of total). Google's AI ecosystem cites Samsung more than any single identified competitor.

3. **ChatGPT is fourth:** Despite ChatGPT's popularity, it accounts for only 9.3% of identified citations. Google's AI products combined cite Samsung 4.4x more than ChatGPT.

#### Plain English
The biggest category is "unknown AI sources" - SEMrush cannot tell which chatbot made half the citations. Of the ones we can identify, Google's various AI tools (AI Overview in search, Gemini chatbot, AI Mode) together cite Samsung way more than ChatGPT does. This suggests Samsung content is well-optimized for Google's AI but may have room to improve for ChatGPT.

---

### Part 5: Time Series Trends

#### Trend Analysis Across 4 Time Points

| Trend | Models | Observation |
|-------|--------|-------------|
| Growing | UNSPECIFIED, GOOGLE_AI_OVERVIEW, GOOGLE_AI_MODE | Citations increasing over time |
| Declining | CHAT_GPT | Citations decreasing over time |
| New Entrant | GEMINI | Was 0 at early time points, appeared at time point 3 |

#### What This Means
- Google's AI presence is expanding rapidly
- ChatGPT's share of Samsung citations is shrinking
- Gemini is a recent addition to the tracking (data starts mid-timeline)

#### Plain English
Over time, more Samsung content is being cited by Google AI products while fewer citations come from ChatGPT. This could mean Google's AI is getting better at finding Samsung content, or ChatGPT is citing fewer external sources, or both. Gemini only started appearing in the data recently, which makes sense since it is a newer product.

---

### Part 6: Documentation Updates

#### Files Modified

| File | Change |
|------|--------|
| `clients/samsung/semrush-api-endpoints.md` | Added Citations by Model endpoint to table and full documentation section |

#### Documentation Added
- Endpoint ID and product
- Request payload example
- Response structure with sample data
- Date filter behavior warning
- Model value definitions
- Time series trend observations
- Plain English explanation

---

### Lessons Learned

1. **Always test filter parameters:** The date filter looked like it should work but had no effect. Never assume a filter works as expected without testing multiple values.

2. **Document unexpected behavior:** The date filter non-functionality is important to record so future developers do not waste time trying to filter by date.

3. **Check all response rows:** The API returns 20 rows (4 time points x 5 models) which initially looks like a large response. Understanding the structure (time series x categories) makes the data meaningful.

4. **UNSPECIFIED is significant:** Half of citations being "unspecified" means analysis should acknowledge this limitation. Drawing conclusions about specific models is based on only half the data.

5. **Google dominates AI citations:** For Samsung content, Google's AI ecosystem (AI Overview, Gemini, AI Mode) combined is far more important than ChatGPT for citation tracking.

---

## 2026-01-28: Fetch Prompts Per URL from SEMrush

### Session Goals
Create scripts to fetch the prompts associated with each Samsung URL from the SEMrush API. This complements the Cited Pages data by answering the reverse question: instead of "which URLs are cited?" we now ask "for a given URL, which prompts mention it?"

---

### Part 1: What Was Done

#### Overview
Created two Python scripts to fetch and load URL prompt data: `fetch_url_prompts.py` queries the SEMrush URL Prompts API endpoint for each URL and saves the prompt data to JSON files, while `load_url_prompts.py` loads that data into a new Supabase table `semrush_url_prompts`. Also applied the canonical HE (Home Entertainment) filter to identify TV-specific URLs for focused analysis.

#### Plain English
Think of this like looking at the problem from the other direction. Previously, we asked "which Samsung pages do AI chatbots cite?" Now we are asking "for each Samsung page, what questions (prompts) does it appear in?" This helps us understand which content performs well in AI responses. For example, if a Samsung TV review page appears in 500 different prompts about TV buying decisions, that page is very valuable for AI visibility.

---

### Part 2: SEMrush URL Prompts API

#### API Details
| Parameter | Value |
|-----------|-------|
| Base URL | `https://api.semrush.com/apis/v4-raw/external-api/v1` |
| Product | `ai` (AI Overview data) |
| Element ID | `777346b4-6777-40fe-9356-4a5d63a70ef8` |
| Element Name | URL Prompts |
| Rate Limit | 600 requests/hour per workspace |

#### Filter: MENTIONS_TARGET vs OWNED_BY_TARGET
| Filter | Used For | Description |
|--------|----------|-------------|
| `CBF_category=MENTIONS_TARGET` | URL Prompts | Returns prompts where the URL is **mentioned** by AI |
| `CBF_category=OWNED_BY_TARGET` | Cited Pages | Returns prompts where Samsung **owns** the cited source |

This is a critical distinction: MENTIONS_TARGET finds prompts that reference a URL, while OWNED_BY_TARGET finds prompts that cite Samsung-owned content.

#### Response Fields
| Field | Description |
|-------|-------------|
| `prompt` | The AI prompt text (user question) |
| `prompt_hash` | Unique identifier for the prompt |
| `topic` | Topic category (e.g., "TVs and Screen Sizes") |
| `llm` | AI model (GOOGLE_AI_OVERVIEW, GOOGLE_AI_MODE, etc.) |
| `volume` | Search volume for the prompt |
| `mentioned_brands_count` | Number of brands mentioned in AI response |
| `used_sources_count` | Number of sources cited in AI response |
| `serp_id` | SERP identifier |

#### Plain English
The URL Prompts API is like asking "for this specific Samsung page, what questions does Google's AI use it to answer?" Each prompt record tells us the question, which AI model used it, how popular the question is (search volume), and how many other brands and sources were also mentioned in the answer.

---

### Part 3: Fetching the Data

#### Script: fetch_url_prompts.py
Location: `clients/samsung/fetch_url_prompts.py`

#### How It Works
1. Reads list of URLs to query (either from Supabase or local JSON)
2. For each URL, sends POST request to URL Prompts endpoint with MENTIONS_TARGET filter
3. Respects rate limit (600 requests/hour) with appropriate delays
4. Saves prompts to JSON files organized by URL
5. Handles pagination if a single URL has many prompts

#### Output Files
| Dataset | URLs Queried | Prompts Found |
|---------|--------------|---------------|
| Top 100 US URLs | 100 | 31,283 unique prompts |
| Top 100 TV URLs | 100 | 5,951 unique prompts |

#### Plain English
The fetch script goes through each Samsung URL one by one and asks SEMrush "what prompts mention this page?" It saves all the answers to JSON files. Because SEMrush limits us to 600 requests per hour, the script has to pace itself if we are querying many URLs.

---

### Part 4: TV URL Filtering (HE Filter)

#### The HE Filter
To identify TV-related URLs from the 84,856 cited pages, we applied the canonical Home Entertainment (HE) filter from the Samsung Reporting Framework.

#### Filter Location
Source: `C:\Development\Samsung Reporting Framework\src\samsung_reporting\gsc\he_url_filter.py`

#### Include Patterns (URL must contain one of these)
- `/tv`
- `/televisions`
- `/home-audio`
- `/projectors`
- `/micro-led`
- `/micro-rgb`

#### Exclude Patterns (URL must NOT contain any of these)
- `/business`
- `/monitor`
- `/mobile`
- `/displays`
- `/smartphones`
- `/phones/`

#### Results
| Metric | Value |
|--------|-------|
| Total US Cited Pages | 84,856 |
| HE/TV URLs after filter | 2,244 |
| Total prompts for TV URLs | 11,760 |

#### Top TV Topics
| Topic | Prompt Count |
|-------|--------------|
| TVs and Screen Sizes | 739 |
| OLED vs QLED TVs | 254 |
| Smart TV Features | 187 |
| TV Buying Guides | 156 |

#### Plain English
The HE filter is like a smart keyword search that finds all Samsung pages about TVs, audio equipment, and projectors while excluding business monitors, mobile phones, and other non-home-entertainment products. This filter is already used in other Samsung reporting projects, so using it here ensures consistency. Out of 84,856 Samsung pages that AI cites, 2,244 are TV-related.

---

### Part 5: Loading into Supabase

#### Script: load_url_prompts.py
Location: `clients/samsung/load_url_prompts.py`

#### Supabase Table Schema
Table name: `semrush_url_prompts`

| Column | Type | Description |
|--------|------|-------------|
| id | uuid | Auto-generated primary key |
| url | text | The Samsung URL |
| prompt | text | The AI prompt text |
| prompt_hash | text | Unique prompt identifier |
| topic | text | Topic category |
| llm | text | AI model name |
| volume | integer | Search volume |
| mentioned_brands_count | integer | Brands mentioned in response |
| used_sources_count | integer | Sources cited in response |
| serp_id | text | SERP identifier |
| country | text | Market (default: "us") |
| fetched_at | timestamptz | When data was fetched |

#### Unique Constraint
`(url, prompt_hash, country)` - Prevents duplicate prompt entries for the same URL

#### Indexes
- `url` - Fast lookup of prompts by URL
- `prompt_hash` - Fast lookup by prompt
- `topic` - Fast filtering by topic category
- `llm` - Fast filtering by AI model

#### Plain English
The Supabase table stores every prompt associated with every URL. The unique constraint on (url, prompt_hash, country) means if we fetch the same data again, it will update existing records rather than create duplicates. The indexes make common queries fast (like "show me all prompts for this URL" or "show me all prompts about OLED TVs").

---

### Part 6: Data Loaded Summary

| Dataset | Records |
|---------|---------|
| Top 100 US URLs | 31,283 prompts |
| Top 100 TV URLs | 5,951 prompts |

#### Why Different Counts
The top 100 US URLs are the most-cited Samsung pages overall (any category). The top 100 TV URLs are filtered to only TV-related pages. The US URLs have more prompts because they include high-traffic categories like smartphones and appliances in addition to TVs.

---

### Part 7: Documentation Updates

#### semrush-api-endpoints.md
Added URL Prompts endpoint documentation:
- Endpoint URL and Element ID
- MENTIONS_TARGET filter explanation
- Response field descriptions
- Rate limit warning (600/hour)

#### docs/data-definitions.md
Added `semrush_url_prompts` table documentation:
- Full schema with all columns
- Unique constraint explanation
- Index definitions
- Example queries

---

### Files Created

| File | Description |
|------|-------------|
| `clients/samsung/fetch_url_prompts.py` | Script to fetch prompts per URL from SEMrush API |
| `clients/samsung/load_url_prompts.py` | Script to load JSON data into Supabase |

### Files Modified

| File | Change |
|------|--------|
| `clients/samsung/semrush-api-endpoints.md` | Added URL Prompts endpoint documentation |
| `clients/samsung/docs/data-definitions.md` | Added `semrush_url_prompts` table schema |

---

### Technical Details: Rate Limiting

#### The 600/Hour Limit
SEMrush enforces a workspace-level rate limit of 600 requests per hour for the URL Prompts endpoint. This means:
- Maximum 10 requests per minute sustained
- If you need to query 1000 URLs, it takes ~100 minutes
- The fetch script includes delay logic to avoid hitting limits

#### Plain English
SEMrush does not want us to overwhelm their servers, so they limit how many times we can ask questions per hour. The script is smart enough to slow down automatically if we are querying lots of URLs. For 100 URLs, it finishes quickly; for thousands of URLs, plan for it to run for a while.

---

### Lessons Learned

1. **MENTIONS_TARGET vs OWNED_BY_TARGET:** These filters return different data. Use MENTIONS_TARGET when you want to know which prompts mention a specific URL. Use OWNED_BY_TARGET when you want to know which prompts cite Samsung-owned content generally.

2. **Reuse existing filters:** The HE filter from Samsung Reporting Framework saved time and ensured consistency with other projects. Do not reinvent filters that already exist.

3. **Rate limits require planning:** For large URL lists, calculate expected runtime based on the 600/hour limit. Consider running overnight for big batches.

4. **Prompt hash is the unique identifier:** The same prompt text might appear multiple times with different URLs, but the prompt_hash stays consistent. Use it for deduplication.

5. **Topic field enables analysis:** The topic categorization from SEMrush (like "TVs and Screen Sizes") enables quick filtering and analysis without parsing prompt text.

---

## 2026-01-28: Load SEMrush Cited Pages into Supabase

### Session Goals
Create a data pipeline to fetch cited pages from the SEMrush API and load them into a Supabase database table for analysis. The cited pages show which Samsung URLs are being cited by AI platforms when answering user prompts.

---

### Part 1: What Was Done

#### Overview
Created two Python scripts to form a complete data pipeline: `fetch_cited_pages.py` fetches all cited page URLs from the SEMrush Cited Pages API endpoint and saves them to a JSON file, while `load_cited_pages.py` reads that JSON and uploads the data to a Supabase table using the REST API.

#### Plain English
Think of this like collecting a list of all Samsung web pages that AI chatbots (like ChatGPT, Perplexity, etc.) reference when answering questions about TVs. SEMrush tracks this data, and we need to get it into our own database (Supabase) so we can analyze patterns, trends, and gaps. The first script downloads the list from SEMrush, and the second script uploads it to our database.

---

### Part 2: SEMrush Cited Pages API

#### API Details
| Parameter | Value |
|-----------|-------|
| Base URL | `https://api.semrush.com/apis/v4-raw/external-api/v1` |
| Product | `ai` (AI Overview data) |
| Element ID | `9dd09001-1d0e-4d28-b675-53670a2af5b0` |
| Element Name | Cited Pages |

#### Filters Applied
| Filter | Value | Description |
|--------|-------|-------------|
| CBF_country | us | United States market |
| CBF_category | OWNED_BY_TARGET | Pages owned by samsung.com |
| CBF_model | " " (space) | All AI models (ChatGPT, Gemini, etc.) |

#### Response Structure
The API returns data in a nested structure:
- `data.blocks.data` - Array of cited page objects
- `data.blocks.data_statistics[0].rowCount` - Total number of results

Each cited page object contains:
- `url` - The Samsung URL being cited
- `prompts_count` - Number of prompts that cite this URL

#### Plain English
SEMrush has a special API for tracking which URLs AI chatbots cite. We use filters to get only US market data, only Samsung-owned pages (not competitor mentions), and all AI models combined. The API returns both the list of URLs and how many times each URL was cited.

---

### Part 3: Fetching the Data

#### Script: fetch_cited_pages.py
Location: `clients/samsung/fetch_cited_pages.py`

#### How It Works
1. Authenticates with SEMrush API using workspace ID and auth token from `.env`
2. Sends POST request with filters to the Cited Pages element endpoint
3. Receives paginated results (API returns all 84,856 URLs in one response)
4. Saves raw JSON response to `clients/samsung/data/cited_pages.json`

#### Output
- File: `clients/samsung/data/cited_pages.json`
- Records: 84,856 URLs
- Format: Raw JSON array of cited page objects

#### Plain English
The fetch script logs into SEMrush, asks for all cited Samsung pages in the US market, and saves everything to a JSON file. We got back 84,856 different Samsung URLs that AI chatbots have cited at some point.

---

### Part 4: Loading into Supabase

#### Script: load_cited_pages.py
Location: `clients/samsung/load_cited_pages.py`

#### Supabase Table Schema
Table name: `semrush_cited_pages`

| Column | Type | Description |
|--------|------|-------------|
| id | int8 | Auto-generated primary key |
| url | text | The Samsung URL being cited |
| prompts_count | int4 | Number of prompts citing this URL |
| country | text | Market (e.g., "us") |
| category | text | Category (e.g., "OWNED_BY_TARGET") |
| domain | text | Domain (e.g., "samsung.com") |
| fetched_at | timestamptz | When the data was fetched |

#### Unique Constraint
`(url, country, category)` - Prevents duplicate entries for the same URL in the same market/category

#### How It Works
1. Reads the JSON file saved by fetch script
2. Transforms each record into the table schema format
3. Sends batch upsert requests to Supabase REST API
4. Uses `on_conflict` to update existing records instead of failing on duplicates

#### Plain English
The load script reads the JSON file, reformats each URL record to match our database table, and uploads everything to Supabase. If we run it again later (with updated data), it will update existing records rather than creating duplicates.

---

### Part 5: Environment Configuration

#### New Environment Variable
Added to `clients/samsung/.env`:

| Variable | Purpose |
|----------|---------|
| SUPABASE_KEY | API key for Supabase REST API authentication |

#### Existing Variables Used
| Variable | Purpose |
|----------|---------|
| SEMRUSH_WS_ID | SEMrush workspace ID |
| SEMRUSH_EXPORT_TOKEN | SEMrush API authentication token |
| SUPABASE_URL | Supabase project URL |

#### Plain English
The scripts need login credentials for both SEMrush (to download data) and Supabase (to upload data). These are stored in a `.env` file that is not committed to Git (keeps secrets safe).

---

### Part 6: Documentation Updates

#### semrush-api-endpoints.md
Added the Cited Pages endpoint documentation:
- Endpoint URL and Element ID
- Available filters (country, category, model)
- Response structure explanation
- Example usage

#### docs/data-definitions.md
Added Supabase table documentation:
- Table schema with all columns
- Data types and constraints
- API reference for querying the table

#### Plain English
Updated our documentation files so future developers know how the Cited Pages API works and what the Supabase table looks like.

---

### Files Created

| File | Description |
|------|-------------|
| `clients/samsung/fetch_cited_pages.py` | Script to fetch cited pages from SEMrush API |
| `clients/samsung/load_cited_pages.py` | Script to load JSON data into Supabase |
| `clients/samsung/data/cited_pages.json` | Raw data file (84,856 URLs) |

### Files Modified

| File | Change |
|------|--------|
| `clients/samsung/.env` | Added SUPABASE_KEY |
| `clients/samsung/semrush-api-endpoints.md` | Added Cited Pages endpoint documentation |
| `clients/samsung/docs/data-definitions.md` | Added Supabase table schema and API reference |

---

### Technical Details: Supabase REST API

#### Why REST API Instead of Python SDK
We used the Supabase REST API directly (via `httpx`) instead of the official Python SDK (`supabase-py`) because:
1. Fewer dependencies to manage
2. No version compatibility issues
3. Direct control over request/response handling
4. REST API is well-documented and stable

#### Upsert Pattern
```python
response = httpx.post(
    f"{SUPABASE_URL}/rest/v1/semrush_cited_pages",
    headers={
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates"
    },
    json=batch_data
)
```

The `Prefer: resolution=merge-duplicates` header tells Supabase to update existing records instead of failing when the unique constraint is violated.

#### Plain English
Instead of using a special Supabase library, we just send HTTP requests directly. This is simpler and more reliable. When uploading data, we tell Supabase "if this URL already exists, update it instead of creating a duplicate."

---

### Results Summary

| Metric | Value |
|--------|-------|
| URLs fetched from SEMrush | 84,856 |
| Records loaded to Supabase | 84,856 |
| Table name | semrush_cited_pages |
| Market | US |
| Domain | samsung.com |

---

### Lessons Learned

1. **SEMrush API returns all data at once:** Unlike paginated APIs, the Cited Pages endpoint returns all 84,856 records in a single response. No pagination handling needed.

2. **Supabase REST API is simpler than SDK:** For basic CRUD operations, direct REST calls with `httpx` are easier to debug and have fewer dependencies than the Python SDK.

3. **Upsert with unique constraints prevents duplicates:** The combination of `(url, country, category)` unique constraint plus `resolution=merge-duplicates` header ensures we can re-run the load script without creating duplicate records.

4. **Store raw JSON for archival:** Saving the raw API response to `cited_pages.json` allows re-processing without additional API calls if the table schema changes.

---

## 2026-01-26: DataForSEO Related Keywords Script for Changan UK

### Session Goals
Create a Python script to fetch related keywords from the DataForSEO Related Keywords API for Changan UK keyword research. The script should query seed keywords, collect related keyword data, and output structured results for analysis.

---

### Part 1: What Was Done

#### Overview
Created a new script `clients/changan-auto/dataforseo_related_keywords.py` that queries the DataForSEO Related Keywords API using 6 seed keywords relevant to Changan UK market positioning. The script saves raw JSON responses per seed keyword and combines all results into a deduplicated CSV file.

#### Plain English
Think of this like asking a search expert "what other words do people search for when they are looking for Changan cars or Chinese electric vehicles?" The script takes 6 starting keywords (like "changan" and "chinese electric car uk") and asks DataForSEO "what related searches are connected to these?" It then collects all the answers, removes duplicates, and saves everything in a spreadsheet format for analysis.

---

### Part 2: Seed Keywords

The script queries 6 seed keywords divided into two categories:

#### Brand Terms
| Keyword | Purpose |
|---------|---------|
| changan | Core brand name |
| changan uk | Brand + UK market |
| changan cars | Brand + product category |

#### Category Terms
| Keyword | Purpose |
|---------|---------|
| chinese electric car uk | Category search with UK location |
| chinese ev | Shortened category search |
| affordable ev uk | Price-sensitive EV shoppers |

#### Plain English
Brand terms help understand what people search when they already know about Changan. Category terms help understand how people search when they are looking for the type of vehicle Changan sells (affordable Chinese EVs) but may not know the brand yet. Both are important for SEO and content strategy.

---

### Part 3: API Configuration

#### Settings Used
| Parameter | Value | Description |
|-----------|-------|-------------|
| Location Code | 2826 | United Kingdom (targets UK search data) |
| Depth | 4 | How many levels of related keywords to explore |
| Include SERP Info | true | Includes search result page details |
| Include Clickstream Data | true | Includes user click behavior data |

#### Plain English
- **Location Code 2826** tells DataForSEO to find keywords that UK users search for (not US, not global)
- **Depth 4** means the API looks 4 levels deep for related keywords (like exploring 4 levels of "related searches" links)
- **SERP info** shows what types of results appear for each keyword (videos, shopping, featured snippets, etc.)
- **Clickstream data** shows actual user clicking patterns, not just search volume

---

### Part 4: Output Files

#### Raw JSON Files
Location: `clients/changan-auto/data/keywords/`

| File | Description |
|------|-------------|
| `related_kw_changan.json` | Raw API response for "changan" |
| `related_kw_changan_uk.json` | Raw API response for "changan uk" |
| `related_kw_changan_cars.json` | Raw API response for "changan cars" |
| `related_kw_chinese_electric_car_uk.json` | Raw API response for "chinese electric car uk" |
| `related_kw_chinese_ev.json` | Raw API response for "chinese ev" |
| `related_kw_affordable_ev_uk.json` | Raw API response for "affordable ev uk" |

#### Combined CSV
Location: `clients/changan-auto/data/keywords/changan_related_keywords.csv`

| Column | Description |
|--------|-------------|
| keyword | The related keyword found |
| seed_keyword | Which seed keyword it came from |
| depth | How many levels away from the seed (1-4) |
| search_volume | Monthly search volume |
| cpc | Cost-per-click (advertising value) |
| competition | Competition score (0-1) |
| competition_level | LOW, MEDIUM, or HIGH |
| keyword_difficulty | SEO difficulty score (0-100) |
| main_intent | Search intent (informational, transactional, etc.) |
| serp_item_types | What types of results appear (organic, video, shopping, etc.) |

#### Plain English
The raw JSON files are like keeping the original receipts - they have every detail DataForSEO returned. The CSV file is like a summary spreadsheet that combines everything important into one easy-to-analyze table. Each row is one keyword with all its metrics.

---

### Part 5: First Run Results

#### Statistics
| Metric | Value |
|--------|-------|
| Total keywords collected | 329 |
| Unique keywords after deduplication | 215 |
| API cost | $0.15 |

#### Plain English
The script found 329 related keywords across all 6 seed searches. After removing duplicates (the same keyword can be related to multiple seeds), we have 215 unique keywords to analyze. The API call cost 15 cents total.

---

### Part 6: Script Location and Usage

#### File Location
`C:\Development\General Analytics\clients\changan-auto\dataforseo_related_keywords.py`

#### How to Run
```bash
uv run clients/changan-auto/dataforseo_related_keywords.py
```

#### Requirements
- DataForSEO API credentials (login and password)
- Credentials should be stored in environment variables or `.env` file

---

### Files Created

| File | Description |
|------|-------------|
| `clients/changan-auto/dataforseo_related_keywords.py` | Main script |
| `clients/changan-auto/data/keywords/related_kw_*.json` | 6 raw JSON response files |
| `clients/changan-auto/data/keywords/changan_related_keywords.csv` | Combined deduplicated CSV |

---

### Lessons Learned

1. **Deduplication is important:** Related keywords from different seeds often overlap - 329 raw results became 215 unique keywords (35% reduction)

2. **Depth parameter expands coverage:** Using depth=4 finds more distant keyword relationships that depth=1 or 2 would miss

3. **Keep raw responses:** Saving JSON per seed keyword allows re-analysis without additional API costs

4. **UK location targeting:** Using location code 2826 ensures all search volume and competition data reflects UK market, not global averages

---

## 2026-01-23: Component Documentation - 3-Way Alignment

### Session Goals
Complete the documentation of all dashboard components by adding missing sections to both `components.html` (CSS component library) and `style-guide.html` (visual reference). Establish a 3-way alignment pattern between the dashboard, component library, and style guide.

---

### Part 1: What Was Done

#### Overview
Added 7 missing component sections to `templates/base/components.html` (approximately 880 additional lines) and 6 new visual example sections to `dashboards/style-guide.html` (approximately 400 additional lines). This ensures all UI elements used in the Samsung dashboard are properly documented in both the CSS library and the visual reference guide.

#### Plain English
Think of this like creating a complete parts catalog for a car. The dashboard (`scom-overview.html`) is the actual car. The `components.html` file is like an engineering blueprint that defines exactly how each part (button, card, table) should be built. The `style-guide.html` is like a visual catalog with photos showing what each part looks like when assembled. Before this work, some parts existed in the car but were not in the blueprint or catalog. Now all three sources match.

---

### Part 2: Components Added to components.html

The CSS component library was expanded from approximately 1,124 lines to approximately 2,000 lines. The following component sections were added:

#### 1. Header Component
- Dashboard header container with flexbox layout
- Header inner content wrapper with max-width constraint
- Header title styling (font, color, size)
- Header logo image styling (max-height, object-fit)

#### 2. Filter Bar Component
- Sticky positioning with z-index management
- Filter row container with flexbox layout
- Filter group wrapper for horizontal alignment
- Select dropdown styling with focus states
- Date picker trigger button and dropdown panel
- Custom date input fields
- Action buttons (Reset, Advanced Filters)
- Active filter visual feedback (`.has-filter` class)

#### 3. Section Headers Component
- Section header container with top border divider
- Section title styling (font-size, font-weight, color)
- Section subtitle styling (smaller, muted color)
- Prompt section variant (specific padding/margins)
- Source section variant (specific padding/margins)

#### 4. Prompt KPI Grid Component
- 4-column grid layout using CSS Grid
- Responsive breakpoints (2 columns at 1200px, 1 column at 768px)
- Uses existing `.kpi-card-compact` styling for individual cards

#### 5. Source KPI Row Component
- Horizontal row layout for source KPI cards
- Single-row styling variant (not stacked like prompt cards)
- Uses existing color palette for consistency

#### 6. Source Donut Chart Component
- Donut chart container with flexbox layout
- Legend container with vertical list
- Legend items with color indicators
- Type badge styling (Owned, Earned, Social, etc.)
- Color-coded backgrounds for each source type

#### 7. Source Tables Grid Component
- 2-column grid layout for domain/URL tables
- Table container with scroll behavior
- Table header styling
- Table row hover states
- Type badge inline styling
- URL link styling with truncation

#### 8. Competitor Analysis Table Component
- Full-width table layout
- Brand color indicator column
- Numeric column alignment
- Row striping and hover states
- Win/lose/neutral indicator styling

#### Plain English
Each of these components is like a Lego piece with specific shape and color rules. The Header is the top bar with Samsung logo. The Filter Bar is the sticky toolbar with dropdowns. Section Headers are the title bars that say "Prompt Analysis" or "Source Analysis." The KPI grids and rows are the boxes with big numbers. The Donut Chart section defines how the pie chart and its legend look. The Tables Grid defines the two side-by-side tables. The Competitor Table defines the brand comparison table at the bottom.

---

### Part 3: Visual Examples Added to style-guide.html

The style guide was expanded from approximately 2,158 lines to approximately 2,550 lines. The following visual example sections were added:

#### 1. Header Section
- Live example of the dashboard header
- Shows Samsung logo on right, title on left
- Demonstrates sticky positioning behavior

#### 2. Filter Bar Section
- Live example of the filter bar with all controls
- Shows select dropdown states (default, hover, focus, active)
- Demonstrates date picker dropdown behavior
- Shows action button styling

#### 3. Section Headers Section
- Shows Prompt Analysis section header variant
- Shows Source Analysis section header variant
- Demonstrates the visual difference between section types

#### 4. Source KPI Cards Section
- Live example of 4 horizontal KPI cards
- Shows single-value card styling (vs. stacked compact cards)
- Demonstrates the horizontal row layout

#### 5. Source Donut Chart Section
- Live example of the donut chart component
- Shows the chart container and legend layout
- Demonstrates type badges with color coding
- Shows interactive legend items

#### 6. Source Tables Section
- Live example of the 2-column table grid
- Shows domain table with type badges
- Shows URL table with citation counts
- Demonstrates table responsive behavior

#### Plain English
The style guide is like a showroom where you can see what each component looks like. Instead of just describing "a header with a logo on the right," the style guide shows you an actual working example. This helps designers and developers see exactly what they are building toward. Each new section added shows a real, interactive example of that component.

---

### Part 4: Files Modified

| File | Before | After | Lines Added |
|------|--------|-------|-------------|
| `clients/samsung/templates/base/components.html` | ~1,124 lines | ~2,000 lines | ~880 lines |
| `clients/samsung/dashboards/style-guide.html` | ~2,158 lines | ~2,550 lines | ~400 lines |

---

### Part 5: The 3-Way Alignment Pattern

#### The Pattern
A new development pattern was established for component documentation:

1. **Dashboard (source of truth)** - The actual dashboard (`scom-overview.html`) contains the production implementation of each component
2. **components.html (CSS library)** - Extracted CSS rules that can be imported into any dashboard
3. **style-guide.html (visual reference)** - Working examples that show what each component looks like

#### How It Works
When a new component is added to the dashboard:
1. The CSS styles are extracted and added to `components.html`
2. A visual example is added to `style-guide.html`
3. All three files now document the same component

#### Why This Matters
- **Consistency:** New dashboards can import `components.html` and get the same styling
- **Documentation:** Stakeholders can view `style-guide.html` to see all available components
- **Maintenance:** Updating a style in `components.html` updates it everywhere

#### Plain English
Think of it like a recipe system. The dashboard is a finished dish you can taste. The `components.html` is the recipe book with exact ingredients and measurements. The `style-guide.html` is a photo gallery showing what each dish should look like when done. If all three match, you know the recipe is correct. This session ensured all three now match for every component.

---

### Part 6: Decision Made

#### Decision
Established the 3-way component documentation pattern as a standard practice.

#### Why
- Components were being added to the dashboard without being documented
- This created a gap where reusable styles were locked inside one file
- Having all components documented enables building new dashboards faster

#### Alternatives Considered
1. **Document only in code comments** - Rejected because comments are not visual and hard to browse
2. **Use a CSS framework like Bootstrap** - Rejected because it would override Samsung branding
3. **Document only in style-guide.html** - Rejected because CSS extraction to `components.html` enables reuse

#### Plain English
We decided that every time a new component is created, it should be documented in two places: the CSS library (for code reuse) and the style guide (for visual reference). This takes a bit more time upfront but saves significant time later when building additional dashboards or making changes.

---

### Lessons Learned

1. **Extract CSS early, not later.** It is easier to extract component CSS to a library file while building the component than to reverse-engineer it later from a large dashboard file.

2. **Visual examples catch styling issues.** Building a live example in the style guide revealed a few CSS specificity issues that were not obvious in the main dashboard context.

3. **3-way alignment prevents drift.** When all three sources (dashboard, library, guide) are kept in sync, inconsistencies are caught early instead of accumulating over time.

4. **Component documentation is an investment.** The ~1,280 lines added across both files took time, but this documentation will save hours when building the next Samsung dashboard or training a new team member.

---

## 2026-01-23: Sticky Global Filter Bar Implementation

### Session Goals
Add a sticky global filter bar to the Samsung HE AI Visibility Dashboard that allows users to filter data by date range, AI platform, category, and model type. Deploy the updated dashboard to the live server.

---

### Part 1: What Was Built

#### Overview
A sticky filter bar was added at the top of the dashboard (below the header) that stays visible while scrolling. The filter bar contains a date range picker with presets, three dropdown filters (AI Platform, Category, Model Type), a Reset button, and an Advanced Filters button placeholder.

#### Plain English
Think of this like adding a toolbar to a spreadsheet that lets you filter which data you see. Instead of seeing everything at once, you can now say "show me only ChatGPT data from the last 7 days for QLED TVs." The "sticky" part means this toolbar stays at the top of your screen even when you scroll down, so you can always change filters without scrolling back up.

---

### Part 2: Filter Bar Structure

#### Position and Styling
- **Position:** Sticky - stays fixed at the top while scrolling past it
- **Location:** Immediately below the page header, above KPI cards
- **Background:** White card with subtle border (#e0e0e0)
- **Z-index:** 90 (below header at 100, but above content)

#### HTML Structure
```html
<div class="filter-bar">
  <div class="filter-row">
    <div class="filter-group">
      <!-- Date Range Picker -->
      <div class="date-picker-container">
        <button class="date-picker-trigger">Last 30 Days</button>
        <div class="date-picker-dropdown">
          <!-- Presets and custom date inputs -->
        </div>
      </div>

      <!-- Dropdown Filters -->
      <select class="filter-select">...</select>
      <select class="filter-select">...</select>
      <select class="filter-select">...</select>

      <!-- Action Buttons -->
      <button class="filter-reset-btn">Reset</button>
      <button class="filter-advanced-btn">Advanced Filters</button>
    </div>
  </div>
</div>
```

#### Plain English
The filter bar is a horizontal row of controls. From left to right: a date picker button, three dropdown menus, and two buttons. Everything is inside a white box with rounded corners that sits below the Samsung header. When you scroll down the page, this box "sticks" to the top of your screen.

---

### Part 3: Date Range Picker

#### Preset Options
| Option | Description |
|--------|-------------|
| Last 7 Days | Previous 7 calendar days |
| Last 30 Days | Previous 30 calendar days (default) |
| Last 90 Days | Previous 90 calendar days |
| Last 12 Months | Previous 12 calendar months |
| Custom Range | User selects start and end dates |

#### Custom Range Feature
When "Custom Range" is selected:
1. Two date input fields appear (Start Date, End Date)
2. User clicks the calendar icons to pick dates
3. User clicks "Apply" button to confirm
4. The trigger button updates to show the custom range

#### JavaScript Behavior
```javascript
// Toggle dropdown visibility
datePickerTrigger.addEventListener('click', function(e) {
    e.stopPropagation();
    datePickerDropdown.classList.toggle('show');
});

// Handle preset selection
presetButtons.forEach(btn => {
    btn.addEventListener('click', function() {
        // Remove active class from all
        presetButtons.forEach(b => b.classList.remove('active'));
        // Add active class to clicked button
        this.classList.add('active');
        // Update trigger text
        datePickerTrigger.textContent = this.textContent;
        // Hide custom date inputs if not custom
        if (!this.classList.contains('custom-range-btn')) {
            customDateInputs.style.display = 'none';
            datePickerDropdown.classList.remove('show');
        } else {
            customDateInputs.style.display = 'block';
        }
    });
});
```

#### Plain English
The date picker works like a dropdown menu. Click the button and a list appears with quick options like "Last 7 Days" or "Last 30 Days." If none of those fit, choose "Custom Range" to pick exact start and end dates using a calendar. Once you select something, the button text changes to show what you picked, and the dropdown closes.

---

### Part 4: Filter Dropdowns

#### AI Platform Filter
| Value | Label |
|-------|-------|
| (empty) | All Platforms |
| chatgpt | ChatGPT |
| gemini | Gemini |
| perplexity | Perplexity |
| claude | Claude |
| copilot | Copilot |

#### Category Filter
| Value | Label |
|-------|-------|
| (empty) | All Categories |
| tv-features | TV Features |
| tv-models | TV Models |
| reviews-brand | Reviews & Brand |

#### Model Type Filter
| Value | Label |
|-------|-------|
| (empty) | All Models |
| neo-qled | Neo QLED |
| qled | QLED |
| oled | OLED |
| mini-led | Mini-LED |
| micro-led | Micro LED |
| crystal-uhd | Crystal UHD |
| the-frame | The Frame |
| gaming-tvs | Gaming TVs |
| outdoor-tv | Outdoor TV |

#### Plain English
These three dropdown menus let you narrow down the data. "AI Platform" filters by which AI service (like ChatGPT or Gemini) the data came from. "Category" filters by the type of question (about TV features, specific models, or reviews). "Model Type" filters by Samsung TV product line (like QLED or The Frame). Selecting "All" in any dropdown removes that filter.

---

### Part 5: Reset Button and Visual Feedback

#### Reset Functionality
The Reset button clears all filters back to their default state:
- Date Range: "Last 30 Days"
- AI Platform: "All Platforms"
- Category: "All Categories"
- Model Type: "All Models"
- Removes `.has-filter` class from all dropdowns

#### Visual Feedback (`.has-filter` class)
When a filter has a non-default value selected, a blue border is added to indicate it is active:

```css
.filter-select.has-filter {
    border-color: var(--samsung-blue);
    box-shadow: 0 0 0 1px var(--samsung-blue);
}
```

#### JavaScript for Reset
```javascript
resetBtn.addEventListener('click', function() {
    // Reset date picker
    datePickerTrigger.textContent = 'Last 30 Days';
    presetButtons.forEach(btn => btn.classList.remove('active'));
    // Activate the 30-day preset
    document.querySelector('[data-range="30d"]').classList.add('active');

    // Reset all dropdowns
    filterSelects.forEach(select => {
        select.value = '';
        select.classList.remove('has-filter');
    });
});
```

#### Plain English
When you click "Reset," everything goes back to the starting point - 30 days of data with no platform, category, or model filters applied. The blue highlights around any active filters disappear, showing that no filters are currently narrowing the data.

---

### Part 6: Fixes Applied

#### Gap Between Header and Filter Bar
**Problem:** There was a visible gap between the page header and the filter bar.

**Cause:** The header had a `margin-bottom` CSS property adding space below it.

**Solution:** Removed the `margin-bottom` from the header CSS and added `margin-bottom: 16px` to the filter bar instead, so spacing is controlled consistently.

#### Plain English
There was an unwanted gap at the top. This happened because the header was pushing content away from itself. By moving the spacing responsibility to the filter bar, we eliminated the gap and kept proper spacing below the filter bar before the KPI cards.

---

### Part 7: Section Filters Removed

#### What Was Removed
- Filter bars from the Prompt Analysis section (had AI Model dropdown and date selector)
- Filter bars from the Source Analysis section (had Source Type and Platform dropdowns)
- Associated CSS styles for section-level filter rows
- Associated JavaScript for section filter handling

#### Why Removed
With the global sticky filter bar at the top, section-level filters became redundant. Having filters in multiple places:
1. Confused users about which filter applied where
2. Created visual clutter
3. Required keeping multiple filter states in sync

#### Plain English
Before, each section had its own mini filter bar. Now that there is one global filter at the top that applies everywhere, those section filters were removed to avoid confusion. You only need to set filters once at the top, and they apply to the whole dashboard.

---

### Part 8: Files Modified

| File | Changes |
|------|---------|
| `clients/samsung/dashboards/scom-overview.html` | Added filter bar HTML (~3100), added filter bar CSS (~300 lines), added filter bar JavaScript (~150 lines), removed section filter bars, fixed header margin |
| `clients/samsung/dashboards/index.html` | Updated with copy of scom-overview.html for deployment |
| `clients/samsung/dashboards/test-filter-bar.html` | Created standalone test file for filter component development |

---

### Part 9: Deployment

#### Git Commit
- **Commit hash:** `e2f640b`
- **Message:** "Samsung dashboard: sticky filter bar with date picker"
- **Branch:** master
- **Remote:** origin (GitHub)

#### Server Deployment
- **Method:** SCP (secure copy over SSH)
- **Target:** `/var/www/html/samsung/ai-visibility/index.html`
- **URL:** https://robotproof.io/samsung/ai-visibility/
- **Authentication:** Nginx basic auth (password protected)

#### Plain English
The code was saved to Git (version control), uploaded to GitHub, and then copied to the live web server. The dashboard is now live at robotproof.io and requires a username/password to access.

---

### Part 10: Technical Details

#### CSS Statistics
- **Filter bar CSS:** ~300 lines
- **Key styles:** Sticky positioning, flexbox layout, dropdown animations, responsive breakpoints
- **Uses CSS custom properties:** `--samsung-blue`, `--text-primary`, etc.

#### JavaScript Statistics
- **Filter bar JS:** ~150 lines
- **Features:** Date picker toggle, preset selection, custom date apply, reset functionality, filter state tracking, click-outside-to-close

#### Responsive Behavior
- **Desktop (>1024px):** All filters in one row
- **Tablet (768-1024px):** Filters wrap to two rows
- **Mobile (<768px):** Stacked vertical layout

#### Plain English
The filter bar code is about 450 lines total (300 CSS + 150 JavaScript). It uses the same color variables as the rest of the dashboard for consistency. On smaller screens, the filters rearrange themselves to fit - going from a single row on desktop to stacked vertically on phones.

---

### Lessons Learned

1. **Sticky positioning requires z-index management.** The filter bar needs to appear above content but below the header. Getting the z-index values right (header: 100, filter: 90) prevents overlap issues.

2. **Click-outside-to-close improves UX.** Users expect dropdown menus to close when clicking elsewhere on the page. Adding a document-level click listener that closes open dropdowns feels natural.

3. **Global filters simplify the user mental model.** Having one filter bar that applies everywhere is easier to understand than multiple section-specific filters that may or may not interact.

4. **Removing old code prevents confusion.** When adding new functionality that replaces old, deleting the old code (section filters) prevents future developers from being confused about which code is active.

5. **Visual feedback for active filters helps users.** The blue border on active filters gives immediate feedback about what filters are currently applied without needing to open each dropdown.

---

## 2026-01-23: Prompt Analysis Section Redesign

### Session Goals
Redesign the Prompt Analysis section in the Samsung dashboard to improve visual hierarchy and consistency with the established style guide. Replace the old single-row KPI layout with double-stacked compact cards.

---

### Part 1: What Was Changed

#### Overview
The Prompt Analysis section was reorganized to follow the same pattern as the Source Analysis section: a clear section header at the top, followed by KPI cards that use the compact double-stacked layout. The old single-row KPI cards and the dual KPI cards below the sunburst chart were removed in favor of a unified design.

#### Plain English
Think of this like reorganizing a report section. Before, the "Prompt Analysis" area jumped straight into charts and tables without a clear header, and the KPI numbers were scattered in two different places (above and below the sunburst chart). Now, it has a proper title at the top ("Prompt Analysis") with a description, followed by organized number boxes that each show two related metrics stacked on top of each other. This makes it easier to scan and matches how the "Source Analysis" section is laid out.

---

### Part 2: Section Header Added

#### What Was Added (line ~3201)
```html
<div class="section-header" style="border-top: 1px solid #e0e0e0; padding-top: 32px; margin-top: 16px;">
  <h2 class="section-title">Prompt Analysis</h2>
  <p class="section-subtitle">Track prompt performance, citations, mentions, and product visibility</p>
</div>
```

#### Purpose
- Provides a clear visual break between sections
- Matches the pattern used by Source Analysis section
- Uses existing `.section-title` and `.section-subtitle` CSS classes for consistency

#### Plain English
A section header is like a chapter title in a book. It tells you "this is where the Prompt Analysis section starts" and gives a one-line summary of what you will find below. The gray line above it acts as a visual separator from the previous section.

---

### Part 3: Double-Stacked Compact KPI Cards

#### What Was Added (line ~3211)
A new 4-column grid of compact KPI cards, where each card displays two related metrics stacked vertically with a divider between them.

#### The Four Cards

| Card | Top Metric | Top Value | Top Badge | Bottom Metric | Bottom Value | Bottom Badge |
|------|------------|-----------|-----------|---------------|--------------|--------------|
| 1 | Prompts with Citations | 312 | +24 (green) | Without Citations | 70 | -8 (green, decrease is good) |
| 2 | Prompts with Mentions | 847 | -18 (red) | Without Mentions | 153 | +12 (neutral gray) |
| 3 | Prompts with Products | 594 | +37 (green) | Without Products | 406 | -15 (red) |
| 4 | Branded Prompts | 234 | +19 (green) | Non-branded Prompts | 766 | +42 (green) |

#### HTML Structure
```html
<div class="prompt-kpi-grid">
  <div class="kpi-card-compact">
    <div class="kpi-section">
      <div class="kpi-section-left">
        <span class="kpi-label">Prompts with Citations</span>
      </div>
      <div class="kpi-section-right">
        <span class="kpi-value">312</span>
        <span class="change-badge increase">+24</span>
      </div>
    </div>
    <div class="kpi-divider"></div>
    <div class="kpi-section">
      <div class="kpi-section-left">
        <span class="kpi-label">Without Citations</span>
      </div>
      <div class="kpi-section-right">
        <span class="kpi-value">70</span>
        <span class="change-badge decrease-good">-8</span>
      </div>
    </div>
  </div>
  <!-- ... 3 more cards -->
</div>
```

#### Plain English
Each card is like a mini-report showing a pair of related numbers. For example, one card shows "Prompts with Citations" (312) on top and "Without Citations" (70) on the bottom. The colored badges show the change from the previous period - green means the change is good (more citations is good, fewer "without citations" is also good), red means the change is bad, and gray is neutral. The divider line separates the two metrics visually.

---

### Part 4: CSS Changes

#### New CSS Added (line ~2466)
```css
/* Prompt Analysis KPI Grid */
.prompt-kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

@media (max-width: 1200px) {
  .prompt-kpi-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .prompt-kpi-grid {
    grid-template-columns: 1fr;
  }
}
```

#### Old CSS Removed
- `.prompt-kpi-row` - Old single-row flex layout
- `.prompt-kpi-card` - Old single-metric card style

#### Plain English
CSS controls how things look and are arranged on the page. The new `.prompt-kpi-grid` class creates a 4-column layout for the KPI cards. The `@media` rules are like "if/then" statements: if the screen is narrower than 1200 pixels (like a tablet), switch to 2 columns; if narrower than 768 pixels (like a phone), switch to 1 column. The old styles were removed because they are no longer used.

---

### Part 5: What Was Removed

#### Old Dual KPI Cards (below sunburst chart)
The old dual KPI cards that appeared between the sunburst chart and the Prompt Rankings table were removed. These showed similar metrics but in a different layout, creating visual inconsistency.

#### Why Removed
- Duplicate information (same metrics shown twice)
- Different visual style from the rest of the dashboard
- Made the section feel cluttered

#### Plain English
Before, there were two places showing prompt-related numbers - one above the chart and one below it. This was confusing because you would see similar information twice in different formats. Now, all the numbers are consolidated into the four compact cards at the top of the section.

---

### Part 6: Section Order (Prompt Analysis)

The final section order is:

1. **Section Header** - "Prompt Analysis" title and subtitle
2. **Double-stacked KPI Cards** - 4 cards with 8 total metrics
3. **Sunburst Chart** - "Prompt Categories" visualization
4. **Prompt Rankings Table** - Detailed prompt performance data

#### Plain English
When you scroll to the Prompt Analysis section, you first see the title, then the quick summary numbers in the four cards, then the interactive donut/sunburst chart showing categories, and finally the detailed table with all the individual prompts.

---

### Part 7: Files Modified

| File | Changes |
|------|---------|
| `clients/samsung/dashboards/scom-overview.html` | Added section header (~line 3201), added prompt-kpi-grid with 4 compact KPI cards (~line 3211), added `.prompt-kpi-grid` CSS (~line 2466), removed old `.prompt-kpi-row` and `.prompt-kpi-card` CSS, removed old dual KPI cards from below sunburst |

---

### Lessons Learned

1. **Consistent section structure improves scannability.** By giving Prompt Analysis the same header pattern as Source Analysis (title + subtitle + divider), users can quickly identify where each section begins.

2. **Consolidating duplicate information reduces confusion.** Having KPI numbers in two places (above and below the chart) made users see the same thing twice. Putting them all in one place at the top is cleaner.

3. **Double-stacked cards are efficient for paired metrics.** When two metrics are opposites (with/without citations), stacking them in one card shows the relationship clearly while saving horizontal space.

4. **Responsive grid breakpoints should be tested.** The 1200px and 768px breakpoints were chosen to match existing dashboard patterns, but actual behavior should be verified on real devices.

---

## 2026-01-23: Source Analysis Integration into Main Dashboard

### Session Goals
Integrate the approved Source Analysis components from the test file (`test-source-analysis.html`) into the main Samsung dashboard (`scom-overview.html`). This is Stage 3 of the 3-stage workflow: Test File -> Approval -> Integration.

---

### Part 1: What Was Integrated

#### Overview
The Source Analysis section was added to the bottom of the main dashboard, appearing after the Prompt Rankings Table. This section provides visibility into which websites cite Samsung, what types of sources mention the brand, and how Samsung compares to competitors.

#### Plain English
Think of it like adding a new chapter to an existing report. The dashboard already had sections for KPIs, trends, and prompt rankings. Now it also has a "Source Analysis" section that answers: "Who is talking about Samsung, and how do we compare to LG, Sony, and others?"

---

### Part 2: CSS Styles Added (~480 lines)

#### What Was Added

1. **Source Type Color Variables**
   ```css
   :root {
     --source-owned: #1428a0;      /* Samsung's own sites */
     --source-earned: #34a853;     /* News, reviews */
     --source-social: #7c4dff;     /* Social media */
     --source-competitor: #ff4438; /* Competitor comparisons */
     --source-other: #666666;      /* Miscellaneous */
   }
   ```

2. **Competitor Brand Color Variables**
   ```css
   :root {
     --brand-samsung: #1428a0;
     --brand-lg: #a50034;
     --brand-sony: #000000;
     --brand-tcl: #e31937;
     --brand-hisense: #00843d;
   }
   ```

3. **Source KPI Card Styles** - Single-row layout with label, value, and change badge

4. **Donut Chart Styles** - Container sizing, legend layout, hover states

5. **Table Styles** - Type badges with color-coded backgrounds, bar visualizations, brand indicators

6. **Responsive Breakpoints** - At 1024px: 4-column grid becomes 2-column, 2-column tables become stacked

#### Plain English
CSS is like a style guide for websites. We added about 480 lines of styling rules that control colors (blue for Samsung-owned sites, green for news coverage), card layouts (how the KPI boxes look), chart appearance (the donut chart sizing and hover effects), and table formatting (stripes, badges, colored bars). We also added rules for smaller screens so everything still looks good on tablets.

---

### Part 3: HTML Section Structure

#### Where It Was Added
The Source Analysis HTML was inserted after the Prompt Rankings Table section and before the closing `</body>` tag. The dashboard now has this order:
1. Header
2. KPI Cards (4 main metrics)
3. Line Charts (trend visualization)
4. Platform Tables (AI platform breakdown)
5. Sunburst Prompts (category hierarchy)
6. Prompt Rankings Table
7. **Source Analysis (NEW)**

#### Section Contents
```html
<!-- Source Analysis Section -->
<div class="container">
  <div class="source-analysis-section">
    <!-- Section Header -->
    <div class="section-header">
      <h2 class="section-title">Source Analysis</h2>
      <p class="section-subtitle">Citation sources and competitor comparison</p>
    </div>

    <!-- KPI Cards Row (4 cards) -->
    <div class="source-kpi-grid">...</div>

    <!-- Donut Chart + Legend -->
    <div class="source-chart-section">...</div>

    <!-- Domain + URL Tables (2-column) -->
    <div class="source-tables-grid">...</div>

    <!-- Competitor Table -->
    <div class="competitor-section">...</div>
  </div>
</div>
```

#### The Four Sub-Components

| Component | Description |
|-----------|-------------|
| Source KPI Cards | 4 metric cards: Citations (1,247), Citation Gaps (89), Mentions (3,456), Source Visibility (67%) |
| AI Sources Donut Chart | D3.js chart showing breakdown by source type with interactive legend |
| Domain/URL Tables | 2-column grid with Top Source Domains (left) and Most Cited URLs (right) |
| Competitor Analysis | Table comparing Samsung, LG, Sony, TCL, Hisense across citation metrics |

#### Plain English
The HTML is the actual content and structure - the words, numbers, and organization of elements on the page. We added a new section with a title ("Source Analysis"), four number boxes at the top, a donut-shaped chart in the middle, two tables side by side, and a competitor comparison table at the bottom. All of this appears below the existing prompt rankings when you scroll down.

---

### Part 4: D3.js Donut Chart Code

#### What Was Added
Interactive JavaScript code using D3.js v7 library to render the donut chart.

#### Key Features

1. **Arc Expansion on Hover**
   ```javascript
   .on('mouseover', function(event, d) {
     d3.select(this)
       .transition()
       .duration(200)
       .attr('d', arcHover);  // Expands the arc segment
   })
   ```

2. **Legend-Chart Interaction**
   ```javascript
   legendItems.on('mouseover', function(event, d) {
     // Highlight corresponding chart segment
     paths.filter(p => p.data.type === d.type)
       .transition()
       .attr('d', arcHover);
   });
   ```

3. **Center Text Updates**
   ```javascript
   .on('mouseover', function(event, d) {
     centerText.text(d.data.type);
     centerCount.text(d.data.count);
   })
   .on('mouseout', function() {
     centerText.text('Total');
     centerCount.text(totalSources);
   });
   ```

#### Plain English
D3.js is a JavaScript library for creating charts and visualizations. The code we added:
- Draws a donut-shaped pie chart from the data
- Makes chart slices expand slightly when you hover over them (like they are popping out)
- Connects the legend labels to the chart (hover over "Owned" in the legend, and the blue slice highlights)
- Updates the number in the center hole to show details for whatever you are hovering over

---

### Part 5: Files Modified

| File | Changes |
|------|---------|
| `clients/samsung/dashboards/scom-overview.html` | Added ~480 lines CSS, Source Analysis HTML section, D3.js donut chart code |

---

### Part 6: 3-Stage Workflow Complete

This integration completes the full 3-stage development workflow:

| Stage | Status | What Happened |
|-------|--------|---------------|
| 1. Test File | COMPLETE | Created `test-source-analysis.html` with all 4 components |
| 2. Approval | COMPLETE | User reviewed test file and approved for integration |
| 3. Integration | COMPLETE | Components added to main `scom-overview.html` dashboard |

#### Plain English
We follow a 3-step process for adding new dashboard features:
1. First, build it in a separate test file so we can experiment without breaking anything (done earlier)
2. Then, show it to the user for approval (done - you said it looked good)
3. Finally, merge it into the real dashboard (done now)

This is like drafting an article, getting editor approval, then publishing it to the main website.

---

### Lessons Learned

1. **Keep CSS variables in :root for consistency.** By defining `--source-owned: #1428a0` at the top level, both the chart colors and table badges automatically use the same values.

2. **D3.js hover interactions require enter/update/exit pattern awareness.** When adding mouseover effects that also connect to external elements (like legend items), you need to carefully select the corresponding elements using `.filter()`.

3. **Section positioning matters for scroll flow.** The Source Analysis section was placed at the bottom because it provides "drill-down" detail - users first see the high-level KPIs and trends, then scroll down for source-level analysis.

4. **~480 lines of CSS for one section is substantial.** This section has many sub-components (cards, charts, multiple tables, badges), each requiring their own styles. Future sections should consider extracting common patterns to `components.html`.

---

## 2026-01-23: Source Analysis Dashboard Components Test File

### Session Goals
Create a test file containing four components for the Source Analysis section of the Samsung AI Visibility dashboard. This section visualizes citation data, source types, and competitor comparisons.

---

### Part 1: What Is the Source Analysis Section?

#### The Purpose
The Source Analysis section answers questions like: "Which websites cite Samsung?", "What types of sources mention us?", and "How do we compare to competitors in terms of visibility?"

#### The Components
Four distinct components work together to tell this story:

1. **Source KPI Cards** - Quick numbers at a glance (citations, gaps, mentions, visibility)
2. **Source Type Pie Chart** - Visual breakdown of where mentions come from
3. **Source Domain and URL Tables** - Detailed lists of which websites cite Samsung
4. **Competitor Analysis** - How Samsung stacks up against LG, Sony, TCL, Hisense

#### Plain English
Think of it like a report on "who is talking about Samsung." The KPI cards are the headline numbers. The pie chart shows whether mentions come from news sites, Samsung's own website, social media, or competitor comparisons. The tables list the actual websites. The competitor section is like a sports standings table showing how all the TV brands rank.

---

### Part 2: Source KPI Cards

#### What Was Built
A 4-column grid of KPI cards displaying:

| Metric | Description | Sample Value |
|--------|-------------|--------------|
| Citations | Total times Samsung cited as source | 1,247 |
| Citation Gaps | Competitor citations where Samsung absent | 89 |
| Mentions | Total brand mentions across sources | 3,456 |
| Source Visibility | % of sources mentioning Samsung | 67% |

#### Technical Implementation
```html
<div class="kpi-grid">
  <div class="kpi-card">
    <div class="kpi-label">Citations</div>
    <div class="kpi-value">1,247</div>
    <div class="change-badge increase">+12%</div>
  </div>
  <!-- ... more cards -->
</div>
```

```css
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}
```

#### Plain English
Four boxes across the top showing the most important numbers. Each box has a label (what it is), a big number (the value), and a colored badge showing if it went up or down since last time.

---

### Part 3: Source Type Pie Chart

#### What Was Built
A D3.js donut chart showing the breakdown of source types:

| Category | Color | Meaning |
|----------|-------|---------|
| Owned | Blue (#1428a0) | Samsung's own properties (samsung.com) |
| Earned | Green (#34a853) | News articles, reviews, organic coverage |
| Social | Purple (#7c4dff) | Social media platforms |
| Competitor | Red (#ff4438) | Competitor comparison articles |
| Other | Gray (#666) | Miscellaneous sources |

#### Technical Implementation
```javascript
// D3.js v7 donut chart
const pie = d3.pie().value(d => d.count);
const arc = d3.arc().innerRadius(80).outerRadius(120);

const colors = {
  'Owned': 'var(--source-owned)',
  'Earned': 'var(--source-earned)',
  'Social': 'var(--source-social)',
  'Competitor': 'var(--source-competitor)',
  'Other': 'var(--source-other)'
};
```

```css
:root {
  --source-owned: #1428a0;
  --source-earned: #34a853;
  --source-social: #7c4dff;
  --source-competitor: #ff4438;
  --source-other: #666666;
}
```

#### Hover Interactions
- Segments highlight on hover
- Tooltip shows category name and count
- Center label updates to show selected category

#### Plain English
A donut chart (pie chart with a hole in the middle) that shows where Samsung mentions come from. Hover over a slice to see the exact count. The hole in the middle shows the total number of sources. Colors help you quickly identify: blue is Samsung's own sites, green is news/reviews, purple is social media, red is competitor comparisons.

---

### Part 4: Source Domain and URL Tables

#### What Was Built
A 2-column layout with two tables:

**Domain Table (left):**
- Domain name (e.g., "cnet.com")
- Type badge (Earned, Owned, etc.)
- Citation count
- Visual bar showing relative volume

**URL Table (right):**
- Full URL path
- Domain name
- Citation count
- Bar visualization

#### Technical Implementation
```html
<div class="tables-grid">
  <div class="table-card">
    <h3>Top Domains</h3>
    <table>
      <thead>
        <tr>
          <th>Domain</th>
          <th>Type</th>
          <th>Citations</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>cnet.com</td>
          <td><span class="type-badge earned">Earned</span></td>
          <td>
            <div class="bar-cell">
              <div class="bar" style="width: 85%"></div>
              <span>127</span>
            </div>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
  <!-- URL table similar structure -->
</div>
```

```css
.tables-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

@media (max-width: 1024px) {
  .tables-grid {
    grid-template-columns: 1fr;
  }
}
```

#### Plain English
Two tables side by side. The left table groups citations by website (so all CNET articles count together). The right table shows individual URLs. Each row has a little bar that shows how many citations that site has compared to others - longer bar means more citations. On mobile, the tables stack vertically.

---

### Part 5: Competitor Analysis Section

#### What Was Built
A comparison table showing Samsung against competitors:

| Brand | Brand Color | Purpose |
|-------|-------------|---------|
| Samsung | #1428a0 (Samsung Blue) | Primary brand |
| LG | #a50034 (LG Red) | Competitor |
| Sony | #000000 (Black) | Competitor |
| TCL | #e31937 (TCL Red) | Competitor |
| Hisense | #00843d (Hisense Green) | Competitor |

#### Metrics Compared
- Citations - How often each brand is cited
- Mentions - Total brand mentions
- Top Position - Best ranking position achieved
- Visibility Score - Overall visibility percentage

#### Technical Implementation
```css
:root {
  --brand-samsung: #1428a0;
  --brand-lg: #a50034;
  --brand-sony: #000000;
  --brand-tcl: #e31937;
  --brand-hisense: #00843d;
}

.brand-indicator {
  width: 4px;
  height: 24px;
  border-radius: 2px;
  background-color: var(--brand-color);
}
```

```html
<tr>
  <td>
    <div class="brand-indicator" style="background: var(--brand-samsung)"></div>
    Samsung
  </td>
  <td>1,247</td>
  <td>3,456</td>
  <td>1</td>
  <td>67%</td>
</tr>
```

#### Plain English
A table that shows Samsung and its main TV competitors in rows. Each brand has a small colored stripe (Samsung is blue, LG is red, etc.) so you can quickly identify them. The columns show different metrics so you can compare: "Samsung has 1,247 citations while LG has 892."

---

### Part 6: Responsive Design

#### Breakpoints
The layout adapts at 1024px:

| Above 1024px | Below 1024px |
|--------------|--------------|
| 4-column KPI grid | 2-column KPI grid |
| 2-column tables grid | Single column (stacked) |
| Pie chart beside legend | Pie chart above legend |

#### Technical Implementation
```css
@media (max-width: 1024px) {
  .kpi-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .tables-grid {
    grid-template-columns: 1fr;
  }

  .chart-container {
    flex-direction: column;
  }
}
```

#### Plain English
On smaller screens (tablets, small laptops), things rearrange to fit better. Instead of 4 KPI cards in a row, you get 2 rows of 2. Instead of tables side by side, they stack vertically. This keeps everything readable without horizontal scrolling.

---

### Files Created

| File | Purpose |
|------|---------|
| `clients/samsung/dashboards/test-source-analysis.html` | Stage 1 test file with all 4 Source Analysis components |

---

### 3-Stage Workflow Status

This follows the established component development workflow:

| Stage | Status | Description |
|-------|--------|-------------|
| 1. Test File | COMPLETE | Created `test-source-analysis.html` with all components |
| 2. Approval | PENDING | User reviews test file, requests changes if needed |
| 3. Template Extraction | PENDING | After approval, extract components to `templates/` folder |

#### Plain English
We build new dashboard sections in 3 steps. First, we create a test file to experiment with (Stage 1 - done). Then the user reviews it and either approves or asks for changes (Stage 2 - waiting). Finally, once approved, we extract the code into reusable template files (Stage 3). This prevents us from putting untested code into the template library.

---

### Lessons Learned

1. **CSS custom properties for theming.** Defining colors like `--source-owned` and `--brand-samsung` in `:root` makes it easy to maintain consistent colors and change them globally if needed.

2. **D3.js v7 for interactive charts.** The donut chart uses D3's declarative data binding, which makes hover interactions straightforward to implement.

3. **Bar visualizations in tables add context.** A number like "127" means more when you see a bar showing it is 85% of the maximum value in the table.

4. **Responsive grids degrade gracefully.** Using CSS Grid with `repeat(4, 1fr)` that changes to `repeat(2, 1fr)` at breakpoints keeps layouts clean at any screen size.

---

## 2026-01-23: Data Definitions Documentation Page

### Session Goals
Create a comprehensive documentation page that defines all metrics and KPIs used in the Samsung dashboard, providing clear explanations, calculation formulas, and data sources.

---

### Part 1: Why a Data Definitions Page?

#### The Problem
The Samsung dashboard displays many metrics (Share of Voice, AI Visibility Score, Position Change, etc.) but there was no central reference explaining what each metric means or how it is calculated. Team members and stakeholders would need to ask questions or guess at meanings.

#### The Solution
A dedicated documentation page that lives alongside the dashboard, styled consistently with the Samsung brand, that defines every metric in a structured format.

#### Plain English
Imagine getting a report card with grades like "B+" and "87%" but no explanation of what subject they are for or how they were calculated. The Data Definitions page is like a glossary at the back of a textbook - it tells you exactly what each number means and where it comes from.

---

### Part 2: Page Structure and Navigation

#### What Was Built

**Header:**
- Samsung-branded header matching the main dashboard
- Sticky positioning so it stays visible while scrolling
- Title: "Data Definitions"

**Table of Contents:**
- Six anchor links to metric categories
- Allows quick jumping to relevant section
- Categories: Primary KPIs, Dual-Metric KPIs, Prompt Tracking, Platform Metrics, Trend Metrics, Position Metrics

**Section Structure:**
Each section has:
- Section title (e.g., "Primary KPIs")
- Brief description of the category
- Grid of definition cards

#### Technical Implementation
```html
<nav class="toc">
  <a href="#primary-kpis">Primary KPIs</a>
  <a href="#dual-metric-kpis">Dual-Metric KPIs</a>
  <!-- ... more links -->
</nav>

<section id="primary-kpis">
  <h2>Primary KPIs</h2>
  <p class="section-description">...</p>
  <div class="definitions-grid">
    <!-- definition cards here -->
  </div>
</section>
```

#### Plain English
The page works like a well-organized dictionary. At the top, you see a mini-menu showing all the sections. Click on "Platform Metrics" and you jump straight to that section. Each section groups related metrics together, like chapters in a book.

---

### Part 3: Definition Card Design

#### Card Structure
Each metric gets its own card containing:

1. **Name** - The metric title (e.g., "Share of Voice")
2. **Type Badge** - Color-coded label: KPI (blue), Metric (gray), or Derived (purple)
3. **Description** - What the metric measures in plain language
4. **Calculation** - The formula or method used to calculate it
5. **Data Source Tag** - Where the data comes from (Brandwatch, GA4, SEMrush, or Calculated)

#### Technical Implementation
```html
<div class="definition-card">
  <div class="card-header">
    <h3>Share of Voice</h3>
    <span class="badge badge-kpi">KPI</span>
  </div>
  <p class="description">Percentage of AI-generated responses that mention Samsung...</p>
  <div class="calculation">
    <strong>Calculation:</strong>
    <code>(Samsung mentions / Total mentions) x 100</code>
  </div>
  <div class="data-source">
    <span class="source-tag source-brandwatch">Brandwatch</span>
  </div>
</div>
```

#### Badge Colors
| Badge | Color | Meaning |
|-------|-------|---------|
| KPI | Blue (#1428a0) | Key Performance Indicator - primary business metric |
| Metric | Gray (#666) | Standard measurement |
| Derived | Purple (#7c4dff) | Calculated from other metrics |

#### Data Source Colors
| Source | Color | Description |
|--------|-------|-------------|
| Brandwatch | Orange (#ff6d00) | Social listening platform |
| GA4 | Green (#34a853) | Google Analytics 4 |
| SEMrush | Blue (#1a73e8) | SEO/visibility tool |
| Calculated | Gray (#666) | Derived from other data |

#### Plain English
Each card is like a dictionary entry. You see the word (metric name), what it means (description), how to figure it out yourself (calculation formula), and where the information comes from (data source). The colored badges help you quickly tell apart the most important metrics (KPIs in blue) from supporting measurements.

---

### Part 4: Metrics Documented

#### Category 1: Primary KPIs
These are the four main metrics shown at the top of the dashboard:

| Metric | Description | Source |
|--------|-------------|--------|
| Share of Voice | % of AI responses mentioning Samsung | Brandwatch |
| Source Visibility | % of sources where Samsung appears | SEMrush |
| Referral Traffic | Visitors from AI platforms | GA4 |
| AI Visibility Score | Composite score (0-100) | Calculated |

#### Category 2: Dual-Metric KPIs
Cards that show two related metrics together:

| Metric | Description | Source |
|--------|-------------|--------|
| Prompt Mentions | Count of prompts mentioning Samsung | SEMrush |
| Top Product Position | Best position achieved | SEMrush |
| Products Win/Lose | Products gained vs lost visibility | Calculated |
| Position Distribution | Breakdown by position tier | SEMrush |

#### Category 3: Prompt Tracking Metrics
Metrics related to tracking individual prompts:

| Metric | Description | Source |
|--------|-------------|--------|
| Topic Volume | Search volume for topic | SEMrush |
| Visibility Score | Prompt-level visibility | SEMrush |
| Position | Current ranking position | SEMrush |
| Position Change | Movement since last period | Calculated |

#### Category 4: Platform Metrics
Performance across different AI platforms:

| Metric | Description | Source |
|--------|-------------|--------|
| Platform Visibility | Visibility by AI platform | SEMrush |
| Platform Trend | Change over time by platform | Calculated |

#### Category 5: Trend Metrics
Time-based comparisons:

| Metric | Description | Source |
|--------|-------------|--------|
| Daily/Weekly Visibility | Visibility over time | SEMrush |
| Period Comparison | Current vs previous period | Calculated |

#### Category 6: Position Metrics
Ranking-related measurements:

| Metric | Description | Source |
|--------|-------------|--------|
| Average Position | Mean position across prompts | Calculated |
| Top 3 Rate | % of prompts in positions 1-3 | Calculated |

---

### Part 5: Styling Consistency

#### Design Token Usage
The page uses the same Samsung design tokens as the main dashboard:

```css
/* Colors */
--samsung-blue: #1428a0;
--text-primary: #000000;
--text-secondary: #767676;
--surface: #ffffff;
--border: #e5e5e5;

/* Typography */
font-family: 'Samsung Sharp Sans', 'Samsung One', sans-serif;

/* Spacing */
padding: 24px;
gap: 16px;
```

#### Plain English
The definitions page looks like it belongs with the main dashboard - same fonts, same colors, same spacing. This makes it feel like part of the same product rather than a separate document thrown together.

---

### Files Created

| File | Purpose |
|------|---------|
| `clients/samsung/dashboards/data-definitions.html` | Complete Data Definitions documentation page |

---

### Lessons Learned

1. **Documentation is part of the product.** A dashboard without documentation forces users to guess what numbers mean. Including a definitions page makes the dashboard more useful and reduces support questions.

2. **Consistent styling matters for documentation too.** Using the same design tokens as the dashboard makes the documentation feel professional and integrated, not like an afterthought.

3. **Structure definitions consistently.** Every metric card has the same four elements (name, description, calculation, source). This consistency makes it easy to find information.

4. **Color-code to add information.** Using different colors for KPI vs Metric vs Derived badges helps users quickly identify the importance and nature of each metric.

5. **Anchor navigation helps with long pages.** With 15+ metrics across 6 categories, the table of contents with anchor links lets users jump directly to what they need.

---

## 2026-01-22: Path Standardization and Compact KPI Layout

### Session Goals
Fix broken asset paths in templates that caused missing icons on the deployed dashboard. Also improve the compact KPI card layout to be more space-efficient.

---

### Part 1: The Path Mismatch Problem

#### What Was Happening
After deploying the Samsung dashboard to the server, KPI icons were not loading. The browser console showed 404 errors for image files.

#### Technical Explanation
The templates were using inconsistent asset paths that did not match the server directory structure:

| Asset Type | Path in Templates | Actual Server Location |
|------------|-------------------|------------------------|
| Fonts | `../assets/fonts/SamsungSharpSansBd.woff2` | `/var/www/html/samsung/ai-visibility/fonts/SamsungSharpSansBd.woff2` |
| Images | `../assets/logo.jpg` | `/var/www/html/samsung/ai-visibility/images/logo.jpg` |
| KPI Icons | `../assets/sov.jpg` | `/var/www/html/samsung/ai-visibility/images/sov.jpg` |

The `../assets/` path only works if the HTML file is in a subdirectory, but the deployed dashboard (`index.html`) is at the root of `ai-visibility/`. The relative path `../assets/` would look for files in `/var/www/html/samsung/assets/`, which does not exist.

#### Plain English
Imagine your dashboard is a document in a folder, and it references pictures stored nearby. The templates said "go up one folder, then into 'assets' to find the pictures." But on the server, the pictures are actually in subfolders called 'fonts' and 'images' right next to the document. It is like giving someone directions that say "turn left at the bakery" when the bakery moved across the street - they end up in the wrong place.

---

### Part 2: The Solution - Standardized Relative Paths

#### What Was Changed

All asset paths were updated to use relative paths from the dashboard root (`./`):

**`templates/base/fonts.html`:**
```css
/* Before */
src: url('../assets/fonts/SamsungSharpSansBd.woff2') format('woff2');

/* After */
src: url('./fonts/SamsungSharpSansBd.woff2') format('woff2');
```

Complete font URL updates:
- `./fonts/SamsungSharpSansBd.woff2`
- `./fonts/SamsungSharpSans-Bold.ttf`
- `./fonts/SamsungOneLatinWeb-400.woff2`
- `./fonts/SamsungOneLatinCompact-400.ttf`

**`templates/header.html`:**
```html
<!-- Before -->
<img src="../assets/logo.jpg" alt="Samsung Logo">

<!-- After -->
<img src="./images/logo.jpg" alt="Samsung Logo">
```

**`templates/kpi-cards.html`:**
```html
<!-- Before -->
<img src="../assets/sov.jpg" class="kpi-icon">

<!-- After -->
<img src="./images/sov.jpg" class="kpi-icon">
```

Complete KPI icon updates:
- `./images/sov.jpg`
- `./images/source_visi.jpg`
- `./images/referral.jpg`
- `./images/ai-visi.jpg`

#### Why `./` Instead of Just the Filename?
Using `./images/logo.jpg` instead of `images/logo.jpg` makes the path explicitly relative to the current directory. While browsers usually handle both the same way, the `./` prefix makes the intent clear and prevents any ambiguity.

#### Plain English
We changed the directions from "go up and over" to "go into this subfolder right here." The new paths match exactly where the files actually live on the server. Now when the dashboard says "find logo.jpg in the images folder," it looks in the right place.

---

### Part 3: Compact KPI Card Layout Redesign

#### The Old Layout (Stacked)
The original compact KPI card had a stacked layout:
```
+---------------------------+
| Label         [?]         |  <- .kpi-section-header
+---------------------------+
|                           |
|          42%              |  <- .kpi-section-metrics
|        +5.2% ↑            |
|                           |
+---------------------------+
```

#### The New Layout (Side-by-Side)
The redesigned layout puts label and value on the same row:
```
+---------------------------+
| Label [?]       42% +5.2% |  <- .kpi-section with -left and -right
+---------------------------+
```

#### Technical Changes

**CSS Structure:**
```css
/* Old structure */
.kpi-section-header { ... }
.kpi-section-metrics { ... }

/* New structure */
.kpi-section {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px;  /* Reduced from 20px */
}
.kpi-section-left {
    display: flex;
    align-items: center;
    gap: 8px;
}
.kpi-section-right {
    display: flex;
    align-items: center;
    gap: 12px;
}
```

**Value Styling:**
```css
/* Old */
.kpi-section-value { font-size: 42px; }

/* New */
.kpi-section-value { font-size: 28px; }
```

#### Why This Change?
1. **Space efficiency:** Side-by-side layout uses less vertical space
2. **Scanability:** Users can quickly scan left-to-right to see metric name and value
3. **Consistency:** Matches common dashboard patterns (label: value format)
4. **More metrics:** Can fit more rows in the same card height

#### Plain English
The old card was like a business card held vertically - the name at the top, details below. The new card is like a business card held horizontally - name on the left, details on the right. This makes better use of space and is easier to read quickly, like scanning a table.

---

### Part 4: Deployment Workflow Simplified

#### Before
1. Edit templates with `../assets/` paths
2. Run assembly script
3. Manually change paths to `./fonts/` and `./images/` in output
4. Deploy via scp

#### After
1. Edit templates with `./fonts/` and `./images/` paths
2. Run assembly script
3. Deploy via scp (no path changes needed)

#### Plain English
Before, we had to do a "find and replace" step after building the dashboard, fixing all the file paths before uploading. Now the templates already have the correct paths, so we can upload them directly. One less step means fewer chances for mistakes.

---

### Files Modified

| File | Change |
|------|--------|
| `clients/samsung/templates/base/fonts.html` | Updated 4 font URLs from `../assets/fonts/` to `./fonts/` |
| `clients/samsung/templates/header.html` | Updated logo path from `../assets/` to `./images/` |
| `clients/samsung/templates/kpi-cards.html` | Updated 4 KPI icon paths from `../assets/` to `./images/`; redesigned compact layout |

---

### Lessons Learned

1. **Match paths to deployment structure from the start.** It is tempting to organize source files one way and deployed files another way, but this creates a translation step that is easy to forget. Keep them aligned.

2. **Test on the actual server, not just locally.** The path issue only appeared after deployment because local file:// URLs handle relative paths differently than server URLs.

3. **Document the server structure.** Having a clear reference of where files live on the server (`/var/www/html/samsung/ai-visibility/fonts/`) makes it easy to verify paths are correct.

4. **Side-by-side layouts work better for metric displays.** The stacked layout looked nice but wasted space. Users scan dashboards quickly - horizontal layouts support that scanning pattern.

5. **Reduce font sizes when changing layouts.** A 42px number looks fine when it has its own row. When sharing a row with a label, 28px is more balanced.

---

## 2026-01-22: Samsung Dashboard Component Standardization (Part 2)

### Session Goals
Extend the global components system with KPI card type definitions, migrate existing templates to use global change badges, and improve accessibility. Complete the style guide with visual examples and code snippets.

---

### Part 1: KPI Card Type Definitions

#### What Was Added
Two distinct KPI card types were defined in `templates/base/components.html`:

**Header KPI Cards (`.kpi-card-header`):**
```css
.kpi-card-header {
    min-height: 160px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
}
```
- Used for main dashboard metrics (Share of Voice, Source Visibility, etc.)
- Includes an icon at the top
- Centered layout with larger metrics
- 160px minimum height for visual consistency

**Compact KPI Cards (`.kpi-card-compact`):**
```css
.kpi-card-compact {
    display: flex;
    flex-direction: column;
}
.kpi-card-compact .kpi-section {
    padding: 16px;
    border-bottom: 1px solid #e5e5e5;
}
```
- Used for detailed breakdowns (stacked metrics)
- Sections separated by dividers
- No icon, more data-dense
- Flexible height based on content

**Grid Layouts:**
```css
.kpi-row-4 { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; }
.kpi-row-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }
.kpi-row-2 { display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; }
```

#### Plain English
Think of header cards as "billboard" metrics - big numbers that catch your eye at the top of the dashboard. Compact cards are like "spreadsheet" metrics - more detailed information stacked in a smaller space. The grid layouts ensure cards line up properly whether you have 2, 3, or 4 in a row.

---

### Part 2: Green Badge Contrast Fix

#### The Problem
The original green color (#96d551) used for positive change badges had poor contrast against white backgrounds. This made the text difficult to read, especially for users with visual impairments.

#### Technical Fix
Changed the green badge color from #96d551 to #2e7d32:

**Before:**
```css
.change-badge.increase { background: rgba(150, 213, 81, 0.2); color: #96d551; }
```

**After:**
```css
.change-badge.increase { background: rgba(46, 125, 50, 0.15); color: #2e7d32; }
```

The new green (#2e7d32) is a darker shade that meets WCAG contrast guidelines while still being clearly recognizable as "green = good."

#### Plain English
The old green was like neon highlighter yellow-green - bright but hard to read. The new green is more like forest green - still clearly green, but much easier on the eyes and readable for everyone.

---

### Part 3: Template Migration to Global Change Badges

#### What Was Changed

**`templates/kpi-cards.html`:**
- Removed local `.kpi-change` class definitions
- Changed all instances of `class="kpi-change increase"` to `class="change-badge increase"`
- Removed redundant badge CSS from the template

**`templates/kpi-cards-dual.html`:**
- Removed local `.kpi-dual-item-change` class definitions
- Changed all instances of `class="kpi-dual-item-change ..."` to `class="change-badge ..."`
- Removed redundant badge CSS from the template

#### Why This Matters
Before: Each template defined its own badge styles. If we wanted to change the green color, we had to edit multiple files.

After: All templates use the global `.change-badge` class from `components.html`. Change the color once, it updates everywhere.

#### Plain English
Before, each recipe book had its own instructions for making "green sauce." If we wanted to change the recipe, we had to update every book. Now, all books just say "use green sauce from the master recipe" - and we only maintain one recipe.

---

### Part 4: Style Guide Updates

#### What Was Added to the Style Guide

1. **KPI Card Types Section:**
   - Visual examples showing both card types side-by-side
   - Comparison table:

   | Property | Header Card | Compact Card |
   |----------|-------------|--------------|
   | Min Height | 160px | Auto |
   | Icon | Yes | No |
   | Layout | Centered | Stacked sections |
   | Use Case | Main metrics | Detailed breakdowns |

2. **Code Examples:**
   - HTML markup for header cards
   - HTML markup for compact cards
   - Grid layout usage examples

3. **Updated Badge Examples:**
   - Now shows the new #2e7d32 green color
   - Demonstrates all badge variants with proper contrast

#### Plain English
The style guide now shows pictures of both card types so designers can see the difference at a glance. It also includes copy-paste code examples so developers do not have to guess how to use them.

---

### Files Created/Modified

| File | Action | Description |
|------|--------|-------------|
| `clients/samsung/templates/base/components.html` | Modified | Added `.kpi-card-header`, `.kpi-card-compact`, grid layouts; updated green badge color |
| `clients/samsung/templates/kpi-cards.html` | Modified | Migrated to global `.change-badge` classes |
| `clients/samsung/templates/kpi-cards-dual.html` | Modified | Migrated to global `.change-badge` classes |
| `clients/samsung/dashboards/style-guide.html` | Modified | Added KPI card type examples, comparison table, code snippets |

---

### Lessons Learned

1. **Accessibility matters from the start.** The original green color looked fine on a design tool but failed in practice. Always check contrast ratios.

2. **Migration is easier than expected.** Converting templates to use global classes took minutes because the class names were already similar. Well-named classes make refactoring painless.

3. **Visual examples beat documentation.** The style guide comparison table is useful, but seeing both card types side-by-side is what actually communicates the difference.

4. **Two card types cover most needs.** Header cards + compact cards handle the majority of dashboard metric displays. Resist the urge to create more variants until there is a clear need.

---

## 2026-01-22: Samsung Dashboard Component Standardization (Part 1)

### Session Goals
Create a centralized system for reusable UI components (tooltips, change badges) to prevent style duplication across Samsung dashboard templates. Build a comprehensive style guide for visual consistency reference.

---

### Part 1: The Problem - Style Duplication

#### What Was Happening
Each template file (kpi-cards.html, sunburst-prompts.html, etc.) was defining its own tooltip and badge styles. This led to:
- Duplicated CSS across multiple files
- Risk of inconsistent styling when one file is updated but others are not
- Difficulty maintaining a single source of truth for shared UI elements

#### Technical Explanation
The Samsung dashboard uses a template assembly system where multiple HTML component files are combined into a single dashboard. Each component was self-contained, including its own CSS. This worked for component-specific styles, but common elements like tooltips and badges were being redefined in each file.

#### Plain English
Imagine writing the same recipe in 5 different cookbooks. If you want to change an ingredient, you have to update all 5 books - and if you miss one, your dishes will turn out differently. The solution is to write the recipe once in a "master cookbook" that all the other books reference.

---

### Part 2: The Solution - Global Components File

#### What Was Created
A new file `templates/base/components.html` containing globally reusable styles:

**Tooltip Styles:**
```css
.tooltip-icon {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 18px;
    height: 18px;
    background: #8091df;
    color: white;
    border-radius: 50%;
    font-size: 12px;
    cursor: help;
    position: relative;
}

.tooltip-text {
    visibility: hidden;
    opacity: 0;
    /* ... positioning and styling ... */
}

.tooltip-icon:hover .tooltip-text {
    visibility: visible;
    opacity: 1;
}
```

**Change Badge Styles:**
```css
.change-badge {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 2px 8px;
    border-radius: 12px;
    font-size: 12px;
    font-weight: 500;
}

.change-badge.increase { background: rgba(150, 213, 81, 0.2); color: #96d551; }
.change-badge.decrease { background: rgba(255, 68, 56, 0.2); color: #ff4438; }
.change-badge.increase-good { background: rgba(150, 213, 81, 0.2); color: #96d551; }
.change-badge.decrease-bad { background: rgba(255, 68, 56, 0.2); color: #ff4438; }
.change-badge.neutral { background: rgba(254, 180, 71, 0.2); color: #feb447; }
```

#### Why 18x18px for Tooltips?
After reviewing all existing templates, 18x18px was the size already used. Standardizing on this ensures consistency and matches what is already deployed.

#### Plain English
We created a "master stylesheet" for common elements. Any template that needs a tooltip or change badge just uses the global classes (`.tooltip-icon`, `.change-badge.increase`, etc.) instead of defining its own styles. One place to edit, everywhere gets updated.

---

### Part 3: Configuration Update

#### What Was Changed
Updated `configs/scom-overview.json` to include the new components file in the base array:

**Before:**
```json
{
  "base": [
    "base/fonts.html",
    "base/tokens.html"
  ]
}
```

**After:**
```json
{
  "base": [
    "base/fonts.html",
    "base/tokens.html",
    "base/components.html"
  ]
}
```

#### How the Assembly System Works
When the assembly script runs, it:
1. Reads the base files in order (fonts, tokens, components)
2. Extracts their CSS into a combined `<style>` block
3. Combines with component templates to produce the final dashboard

By adding `components.html` to the base array, its styles are automatically included in every assembled dashboard.

#### Plain English
The configuration file is like a recipe card that lists ingredients. By adding "components.html" to the list, the assembly script knows to include those global styles whenever it builds a dashboard. No manual copying needed.

---

### Part 4: Style Guide Creation

#### What Was Built
A comprehensive style guide at `dashboards/style-guide.html` documenting:

1. **Color Palette** - All brand colors with hex values and usage notes
2. **Typography** - Font families (Samsung Sharp Sans, Samsung One), sizes, weights
3. **Tooltip Icons** - Live examples of tooltip hover behavior
4. **Change Badges** - All 5 variants with visual examples
5. **Card Styles** - Standard card appearance with shadows and borders
6. **Metric Values** - Large number formatting (58px, Samsung Sharp Sans Bold)
7. **Labels** - Standard 14px uppercase labels
8. **Inconsistency Audit Table** - Tracking existing style variations that need resolution

#### Why a Style Guide?
- **Reference for development:** Quick visual check of available components
- **Consistency enforcement:** Everyone uses the same styles
- **Client communication:** Shows the design system at a glance
- **Debugging aid:** Compare rendered output against expected appearance

#### Deployment
The style guide was deployed to: https://robotproof.io/samsung/ai-visibility/style-guide.html

#### Plain English
A style guide is like a paint swatch book for a house. Before painting, you check the book to see exactly what "Living Room Blue" looks like. Similarly, before adding a new dashboard element, you check the style guide to see exactly how a tooltip or badge should look. This prevents the "50 shades of blue" problem where every component uses a slightly different color.

---

### Part 5: Prompt Gaps Test Card

#### What Was Created
A test file `dashboards/test-prompt-gaps.html` for a new "Prompt Gaps" KPI card design:

- **Layout:** Stacked card with 2 metrics (horizontal layout)
- **Metric 1:** "Prompt Gaps" - Number of prompts where Samsung is not visible
- **Metric 2:** "Competitors Visible" - Number of competitors appearing in those prompts
- **Styling:** Uses global tooltip and badge components

#### Why a Separate Test File?
Following the Component-First Workflow:
1. **Test file** (edit and experiment) -> This file
2. **Template** (approved, immutable)
3. **Assembly** (generates final dashboard)

The test file allows experimentation without affecting the production dashboard.

#### Plain English
Before building a new room addition to a house, you make a small model first. The test file is that model - a safe place to try out the new card design before committing to it in the main dashboard.

---

### Part 6: Architectural Principles Established

#### The Component Hierarchy
```
templates/base/components.html    <- Global styles (tooltips, badges)
        |
templates/base/tokens.html        <- Design tokens (colors, spacing)
        |
templates/base/fonts.html         <- Font declarations
        |
templates/*.html                  <- Component templates (use global + component-specific styles)
        |
dashboards/*.html                 <- Assembled output
```

#### What Goes Where?

| Element Type | Location | Example |
|--------------|----------|---------|
| Reusable across ALL components | `base/components.html` | Tooltips, badges |
| Design variables | `base/tokens.html` | Colors, spacing, font sizes |
| Font declarations | `base/fonts.html` | @font-face rules |
| Component-specific layout | `templates/*.html` | KPI card grid, chart dimensions |

#### Plain English
Think of it like organizing a kitchen:
- **components.html** = Universal tools drawer (spatulas, spoons) - used everywhere
- **tokens.html** = Measurements and standards (cup sizes, temperatures) - referenced everywhere
- **fonts.html** = Ingredient labels (fonts are the "ingredients" of text)
- **templates/*.html** = Specific recipes (KPI card recipe, chart recipe) - each uses the universal tools

---

### Files Created/Modified

| File | Action | Description |
|------|--------|-------------|
| `clients/samsung/templates/base/components.html` | Created | Global tooltip and badge styles |
| `clients/samsung/configs/scom-overview.json` | Modified | Added components.html to base array |
| `clients/samsung/dashboards/style-guide.html` | Created | Comprehensive component reference |
| `clients/samsung/dashboards/test-prompt-gaps.html` | Created | Test file for new stacked KPI card |

---

### Lessons Learned

1. **Centralize shared styles early.** Retrofitting a global components system is harder than building it from the start. As soon as you see the same CSS in two places, extract it.

2. **Match existing implementations when standardizing.** The 18x18px tooltip size was chosen because it matched what was already deployed. Standardization should minimize changes, not introduce new inconsistencies.

3. **Style guides pay for themselves.** The time spent building the style guide is recovered the first time someone needs to check "what color is our green badge?" instead of hunting through code.

4. **Test files are cheap insurance.** Creating a test file for the Prompt Gaps card took 5 minutes but provides a safe sandbox for experimentation.

5. **Document the hierarchy.** Writing down "global elements go in components.html, component-specific layout goes in templates" prevents future confusion about where new styles belong.

---

## 2026-01-22: MCP Token Expiry Documentation

### Session Goals
Document why MCP authentication fails periodically and provide a quick reference for fixing it. Users were repeatedly encountering auth errors without understanding the root cause.

---

### Part 1: Why Tokens Keep Expiring

#### The Problem
Every week or so, both GA and GTM MCP servers start failing with authentication errors like:
- "Reauthentication is needed"
- "Request had insufficient authentication scopes"
- 503 errors mentioning metadata or plugin

This happens even though authentication worked fine last week.

#### Technical Explanation
The OAuth application (project 335937140210) is currently in "Testing" mode in Google Cloud Console. Google enforces a **7-day token lifetime** for OAuth apps in Testing mode as a security measure. After 7 days, the refresh token becomes invalid and the MCP servers can no longer authenticate.

When an OAuth app is published to "Production" status, the token lifetime extends to **6 months**. This is why commercial applications do not require weekly re-authentication.

#### Plain English
Think of your login as a temporary pass that expires after a week. Google does this on purpose for apps that are not officially published - it is a safety feature. Every 7 days, your pass expires and you need to get a new one by logging in again. If you want a pass that lasts 6 months instead, you need to officially "publish" your app in Google's system.

---

### Part 2: The Quick Fix (Until App is Published)

#### Step-by-Step

When you see auth errors, do these 3 things:

**Step 1: Run the auth command**

Open PowerShell and run (use `gcloud.cmd`, NOT `gcloud`):
```powershell
gcloud.cmd auth application-default login --scopes "https://www.googleapis.com/auth/analytics.readonly,https://www.googleapis.com/auth/tagmanager.readonly,https://www.googleapis.com/auth/tagmanager.edit.containers,https://www.googleapis.com/auth/tagmanager.publish,https://www.googleapis.com/auth/cloud-platform" --client-id-file="C:\Users\rober\Downloads\client_secret_335937140210-0b9u8oki65hjd9bcsnc7uic8ov51bp2u.apps.googleusercontent.com.json"
```

**Step 2: Copy the credentials file**
```powershell
copy "C:\Users\rober\AppData\Roaming\gcloud\application_default_credentials.json" "C:\Users\rober\application_default_credentials.json"
```

**Step 3: Restart Claude Code**

Both commands are saved in `C:\Development\General Analytics\auth-command.txt` for easy copy/paste.

#### Plain English
1. Run a special login command that asks Google for a new pass with all the right permissions
2. Copy your new pass to where the MCP servers expect to find it
3. Restart Claude Code so it picks up the new pass

---

### Part 3: The Permanent Fix

#### How to Extend Token Lifetime to 6 Months

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select project `335937140210`
3. Navigate to: **APIs & Services** > **OAuth consent screen**
4. Click **PUBLISH APP** button
5. Confirm the publishing dialog

After publishing, tokens will last 6 months instead of 7 days.

#### Why the App is Still in Testing Mode
Publishing an OAuth app requires:
- Verifying ownership of any domains used
- Potentially a security review by Google (for sensitive scopes)
- Acceptance of Google's terms

For personal/internal tools, the 7-day re-auth is often acceptable. For production tools used by others, publishing is recommended.

#### Plain English
Right now the app is in "preview" mode, which is why passes expire weekly. To make them last 6 months, you need to flip a switch in Google's settings that says "this is a real app, not just a test." Google may ask some questions first to make sure the app is legitimate.

---

### Part 4: Recognizing Auth Errors

#### Error Messages That Mean "Re-auth Needed"

| Error Message | What It Means |
|---------------|---------------|
| "Reauthentication is needed" | Token expired (most common) |
| "Request had insufficient authentication scopes" | Token is missing some permissions (rare after using full auth command) |
| 503 with "metadata" or "plugin" | MCP server cannot read credentials file |
| "Could not automatically determine credentials" | Credentials file not found or unreadable |

#### Plain English
If you see any error that mentions authentication, re-authentication, scopes, credentials, or 503 errors related to the MCP servers - just run the quick fix. It takes 30 seconds and solves most problems.

---

### Files Reference

| File | Purpose |
|------|---------|
| `C:\Development\General Analytics\auth-command.txt` | Both commands for easy copy/paste |
| `C:\Users\rober\application_default_credentials.json` | Where MCP servers read credentials |
| `C:\Users\rober\AppData\Roaming\gcloud\application_default_credentials.json` | Where gcloud writes credentials (source) |
| `C:\Users\rober\Downloads\client_secret_335937140210-...json` | OAuth client ID file (keep private) |

---

### Lessons Learned

1. **OAuth Testing mode = 7-day token lifetime.** This is intentional by Google, not a bug.

2. **Keep auth-command.txt handy.** You will use it weekly until the OAuth app is published.

3. **Use `gcloud.cmd` not `gcloud`.** The PowerShell wrapper has a bug that causes hangs.

4. **The copy step is required on Windows.** The MCP servers cannot reliably read from the AppData path.

5. **Restart Claude Code after re-auth.** MCP servers cache credentials on startup.

---

## 2026-01-21: MCP Authentication Setup (Critical Reference)

### Session Goals
Document the complete MCP authentication workflow after a painful debugging session. This guide ensures we never waste time debugging scope conflicts again.

---

### Part 1: The Core Problem

#### What Was Happening
After setting up the local GTM MCP server, one MCP would work but the other would fail with authentication errors. Re-authenticating for one server would break the other.

#### Technical Explanation
Google Application Default Credentials (ADC) stores credentials in a single JSON file. This file includes:
- Access token (temporary)
- Refresh token (long-lived)
- Scopes (what the credentials are allowed to do)

The critical issue: **each `gcloud auth application-default login` command OVERWRITES the entire file**. If you authenticate with only GA scopes, the file loses the GTM scopes. If you then authenticate with only GTM scopes, the file loses the GA scopes.

#### Plain English
Think of it like a keycard that can only hold a limited set of permissions at once. When you re-program the keycard for one door (GA), it forgets how to open the other door (GTM). The solution is to program the keycard for ALL doors at the same time.

---

### Part 2: The Solution - Single Auth Command with All Scopes

#### The Command
The complete authentication command is saved in `auth-command.txt` for easy copy/paste:

```
gcloud.cmd auth application-default login --scopes "https://www.googleapis.com/auth/analytics.readonly,https://www.googleapis.com/auth/tagmanager.readonly,https://www.googleapis.com/auth/tagmanager.edit.containers,https://www.googleapis.com/auth/tagmanager.publish,https://www.googleapis.com/auth/cloud-platform" --client-id-file="C:\Users\rober\Downloads\client_secret_335937140210-0b9u8oki65hjd9bcsnc7uic8ov51bp2u.apps.googleusercontent.com.json"
```

#### Scope Breakdown

| Scope | Purpose | Used By |
|-------|---------|---------|
| `analytics.readonly` | Read GA4 data, run reports | GA MCP |
| `tagmanager.readonly` | Read GTM containers, tags, triggers | GTM MCP |
| `tagmanager.edit.containers` | Create/modify GTM tags, triggers, variables | GTM MCP |
| `tagmanager.publish` | Publish GTM container versions | GTM MCP |
| `cloud-platform` | Required by gcloud for project access | Both |

#### Why This Works
By including ALL scopes in a single command, the resulting credentials file has permission to access both GA and GTM APIs. Both MCP servers read the same file, and both find the scopes they need.

#### Plain English
Instead of making two separate keycards (one for GA, one for GTM), we make one super-keycard that opens all the doors. Run the command once, and both servers work.

---

### Part 3: Windows-Specific Issues and Workarounds

#### Issue 1: PowerShell gcloud Wrapper Hangs

**Problem:** Running `gcloud auth application-default login` in PowerShell causes an infinite hang. The terminal just sits there after you complete browser authentication.

**Technical Cause:** The gcloud installation includes a PowerShell wrapper script (`gcloud.ps1`) that has a bug. It throws a "Test-Path: Access is denied" error internally, which causes it to hang instead of completing.

**Solution:** Use `gcloud.cmd` instead of `gcloud`. The `.cmd` batch file wrapper does not have this issue.

```powershell
# This hangs:
gcloud auth application-default login ...

# This works:
gcloud.cmd auth application-default login ...
```

#### Plain English
Google Cloud SDK installs multiple ways to run gcloud commands. The PowerShell version (gcloud.ps1) has a bug that makes it freeze. The old-school Windows batch version (gcloud.cmd) works fine. Same command, different wrapper.

---

#### Issue 2: grpc Cannot Read from AppData Path

**Problem:** Even after successful authentication, the MCP servers fail with authentication errors. The credentials file exists but the servers cannot read it.

**Technical Cause:** The grpc library (used by Google's Python APIs) has issues on Windows reading files from long paths or paths with special directories like `AppData\Roaming`. The default gcloud credentials path is:
```
C:\Users\rober\AppData\Roaming\gcloud\application_default_credentials.json
```

**Solution:** Copy the credentials file to the user's home directory, which has a shorter, simpler path:
```
C:\Users\rober\application_default_credentials.json
```

**Copy Command:**
```powershell
copy "C:\Users\rober\AppData\Roaming\gcloud\application_default_credentials.json" "C:\Users\rober\application_default_credentials.json"
```

The MCP servers are configured to look for credentials in the home directory.

#### Plain English
The software that talks to Google APIs has trouble reading files from deeply nested Windows folders. By copying the credentials file to a simpler location (directly in your user folder), the software can find and read it without issues.

---

### Part 4: Complete Authentication Procedure

#### Step-by-Step Guide

1. **Open PowerShell** in any directory

2. **Run the auth command** (copy from `auth-command.txt`):
   ```powershell
   gcloud.cmd auth application-default login --scopes "https://www.googleapis.com/auth/analytics.readonly,https://www.googleapis.com/auth/tagmanager.readonly,https://www.googleapis.com/auth/tagmanager.edit.containers,https://www.googleapis.com/auth/tagmanager.publish,https://www.googleapis.com/auth/cloud-platform" --client-id-file="C:\Users\rober\Downloads\client_secret_335937140210-0b9u8oki65hjd9bcsnc7uic8ov51bp2u.apps.googleusercontent.com.json"
   ```

3. **Complete browser authentication:**
   - Browser opens to Google login
   - Select the appropriate Google account
   - Grant the requested permissions
   - See "The authentication flow has completed" message

4. **Wait for terminal confirmation:**
   - Terminal should display: "Credentials saved to file: [path]"
   - If it does not respond within 30 seconds, press Ctrl+C
   - Check if the credentials file was updated (file modified time)

5. **Copy credentials to home directory:**
   ```powershell
   copy "C:\Users\rober\AppData\Roaming\gcloud\application_default_credentials.json" "C:\Users\rober\application_default_credentials.json"
   ```

6. **Restart Claude Code** to pick up the new credentials

7. **Test both MCP servers:**
   - Test GA MCP: Try a GA query (e.g., list properties)
   - Test GTM MCP: Try a GTM query (e.g., list containers)

#### Plain English
1. Run the special login command in PowerShell
2. Log in via Google in your browser and approve the permissions
3. Copy the credentials file to the right place
4. Restart Claude Code
5. Test that both GA and GTM tools work

---

### Part 5: Troubleshooting Guide

#### Problem: Auth command hangs indefinitely

**Symptom:** Terminal shows nothing after browser says "authenticated"

**Cause:** Using `gcloud` instead of `gcloud.cmd` in PowerShell

**Fix:** Use `gcloud.cmd auth application-default login ...`

---

#### Problem: One MCP works but the other fails

**Symptom:** GA queries work but GTM fails (or vice versa)

**Cause:** Last authentication only included one set of scopes

**Fix:** Re-run the full auth command with ALL scopes (see auth-command.txt)

---

#### Problem: Browser says authenticated but credentials file unchanged

**Symptom:** File modification date does not update after auth

**Cause:** PowerShell wrapper hung before writing file

**Fix:**
1. Press Ctrl+C to cancel
2. Re-run using `gcloud.cmd` instead of `gcloud`

---

#### Problem: MCP servers fail even with fresh credentials

**Symptom:** "Could not automatically determine credentials" errors

**Cause:** Credentials file in wrong location for grpc to read

**Fix:** Copy credentials to user home directory:
```powershell
copy "C:\Users\rober\AppData\Roaming\gcloud\application_default_credentials.json" "C:\Users\rober\application_default_credentials.json"
```

---

#### Problem: "API not enabled" errors

**Symptom:** Error message mentions "tagmanager.googleapis.com" or "analytics.googleapis.com" not enabled

**Cause:** The API is not enabled in the Google Cloud project

**Fix:**
1. Go to Google Cloud Console
2. Select project (335937140210)
3. Go to "APIs & Services" > "Enable APIs and Services"
4. Search for and enable the required API

---

### Part 6: Files Reference

#### Credentials Files

| File | Purpose |
|------|---------|
| `C:\Users\rober\AppData\Roaming\gcloud\application_default_credentials.json` | Where gcloud saves credentials (source) |
| `C:\Users\rober\application_default_credentials.json` | Where MCP servers read from (target) |

#### Configuration Files

| File | Purpose |
|------|---------|
| `C:\Development\General Analytics\.mcp.json` | MCP server configuration for Claude Code |
| `C:\Development\General Analytics\auth-command.txt` | The complete auth command for copy/paste |
| `C:\Users\rober\Downloads\client_secret_335937140210-....json` | OAuth client ID file (do not share) |

#### MCP Server Locations

| Server | Code Location | Virtual Environment |
|--------|---------------|---------------------|
| GTM MCP | `C:\Users\rober\gtm-mcp\` | `C:\Users\rober\gtm-mcp-py313\` |
| GA MCP | (installed package) | `C:\Users\rober\analytics-mcp-py313\` |

---

### Lessons Learned

1. **Application Default Credentials is a single file with a single scope set.** There is no way to "add" scopes - each auth overwrites the previous. Always authenticate with ALL scopes you need.

2. **Windows gcloud has multiple wrappers with different behaviors.** When one hangs, try a different wrapper (`gcloud.cmd` vs `gcloud` vs `gcloud.ps1`).

3. **grpc on Windows is path-sensitive.** Keep credentials in simple paths (user home directory) rather than deeply nested system folders.

4. **Document auth procedures obsessively.** The time spent writing this guide is less than the time wasted re-debugging the same issues.

5. **Save the working command.** The `auth-command.txt` file exists specifically so you never have to remember or reconstruct the full command with all scopes.

---

## 2026-01-21: Local GTM MCP Server Implementation

### Session Goals
Replace the mcp-remote proxy setup for Google Tag Manager with a locally-built MCP server. The proxy was causing connection issues, and a local server provides better reliability and control.

---

### Part 1: The Problem with mcp-remote

#### What Was Happening
The original GTM MCP configuration used `mcp-remote` as a proxy to connect to a remote GTM MCP server. This setup was experiencing connection issues that made the GTM tools unreliable.

#### Plain English
Think of mcp-remote as a middleman. When Claude wanted to talk to Google Tag Manager, it had to go through this middleman service. Sometimes the middleman would fail to respond or lose connection, making the whole system unreliable. The solution was to cut out the middleman and build a direct connection.

---

### Part 2: Building the Local Server

#### Architecture Decision
The new GTM MCP server follows the exact same architecture as the existing analytics-mcp server:
- **Framework:** FastMCP (a Python library for building MCP servers)
- **Authentication:** Google Application Default Credentials
- **Structure:** Modular tools organized by function

#### What is FastMCP?
FastMCP is a Python framework that simplifies building MCP (Model Context Protocol) servers. It handles all the protocol details, so you only need to write Python functions with decorators like `@mcp.tool()` and FastMCP turns them into MCP-compatible tools.

#### What is Application Default Credentials (ADC)?
ADC is a file on your computer (`application_default_credentials.json`) that proves to Google you are allowed to access certain APIs. It is created when you run `gcloud auth application-default login`. Both the analytics-mcp and gtm-mcp servers use this same file.

#### Plain English
Instead of connecting to someone else's server, we built our own. It runs right on your computer. When Claude needs GTM data, it talks directly to Google using credentials stored on your machine. No middleman, no network dependencies (beyond Google's API), no connection drops.

---

### Part 3: Server Implementation Details

#### Location and Setup
- **Server code:** `C:\Users\rober\gtm-mcp\`
- **Virtual environment:** `C:\Users\rober\gtm-mcp-py313\` (Python 3.13)

#### Tools Implemented (29 total across 7 modules)

| Module | Tools | Purpose |
|--------|-------|---------|
| accounts | 1 | List GTM accounts you have access to |
| containers | 3 | List, get, create GTM containers |
| workspaces | 3 | List, get, create workspaces (draft areas) |
| tags | 5 | List, get, create, update, delete tags |
| triggers | 5 | List, get, create, update, delete triggers |
| variables | 5 | List, get, create, update, delete variables |
| versions | 5 | List, get, create, publish container versions |

#### What are these GTM concepts?
- **Account:** The top-level owner (like "Changan Auto")
- **Container:** A collection of tags for one website (like "Germany" or "UK")
- **Workspace:** A draft area where you make changes before publishing
- **Tags:** Code snippets that run on your website (like Google Analytics tracking)
- **Triggers:** Rules that determine when tags fire (like "when page loads")
- **Variables:** Reusable values (like "the current page URL")
- **Versions:** Published snapshots of your container (like saving a document)

#### Plain English
The server provides 29 different commands Claude can use. These cover everything you would do in the GTM web interface: listing what containers exist, reading tag configurations, creating new triggers, publishing changes, and more. It is like giving Claude a complete remote control for GTM.

---

### Part 4: Google Cloud Configuration

#### API Enablement
Had to enable the Tag Manager API in the Google Cloud project:
- **Project ID:** 335937140210
- **API:** Tag Manager API (tagmanager.googleapis.com)

#### Re-authentication
Re-ran the authentication command to include GTM-specific scopes:

```bash
gcloud auth application-default login \
  --scopes https://www.googleapis.com/auth/analytics.readonly,https://www.googleapis.com/auth/cloud-platform,https://www.googleapis.com/auth/tagmanager.readonly,https://www.googleapis.com/auth/tagmanager.edit.containers,https://www.googleapis.com/auth/tagmanager.publish \
  --client-id-file="client_secret_335937140210-0b9u8oki65hjd9bcsnc7uic8ov51bp2u.apps.googleusercontent.com.json"
```

#### What are OAuth Scopes?
Scopes are permissions. When you authenticate, you specify what the credentials are allowed to do. The scopes used here are:
- `tagmanager.readonly` - Read GTM data
- `tagmanager.edit.containers` - Make changes to containers
- `tagmanager.publish` - Publish container versions

#### Plain English
Google APIs require explicit permission for what you want to do. You need to log in and say "I want to read GTM data, edit containers, and publish changes." Google remembers these permissions in your credentials file. If you later need a new permission, you have to log in again and add it to the list.

---

### Part 5: Configuration Update

#### Updated .mcp.json

**Before (mcp-remote proxy):**
```json
{
  "mcpServers": {
    "gtm-mcp-server": {
      "command": "npx",
      "args": ["mcp-remote", "https://gtm-mcp-server.example.com/sse"]
    }
  }
}
```

**After (local server):**
```json
{
  "mcpServers": {
    "gtm-mcp-server": {
      "command": "C:\\Users\\rober\\gtm-mcp-py313\\Scripts\\uv.exe",
      "args": ["--directory", "C:\\Users\\rober\\gtm-mcp", "run", "gtm-mcp"]
    }
  }
}
```

#### What Changed
Instead of using npx to run mcp-remote (which connected to an external server), we now directly run the local Python server using uv. The `--directory` flag tells uv where the server code lives.

#### Plain English
The configuration file tells Claude Code how to start the GTM server. Before, it said "use this middleman service." Now it says "run the Python server on your computer." Same end result (Claude can manage GTM), but much more reliable.

---

### Part 6: Testing and Verification

#### Successful Test
After updating the configuration, tested by listing containers for the Changan Auto account:
- **Result:** Successfully returned all 11 Changan Auto containers
- **Response time:** Noticeably faster than the mcp-remote setup

#### Containers Verified
All containers from the GTM account table in CLAUDE.md were returned:
- Country Picker (GTM-WNQPXL6N)
- Netherlands (GTM-NXD47XWV)
- United Kingdom (GTM-T8C77SQC)
- Germany (GTM-K9W9M2CP)
- Norway (GTM-PV97D2CT)
- Greece (GTM-NQKF32WT)
- Italy (GTM-KN4C3SKX)
- Spain (GTM-NVHNTJG4)
- Poland (GTM-WQ57LP24)
- Luxembourg (GTM-MZ2GB5XQ)
- Belgium (GTM-TZBH8HLQ)

---

### Files Modified/Created

| File/Location | Change |
|---------------|--------|
| `C:\Users\rober\gtm-mcp\` | New GTM MCP server (Python) |
| `C:\Users\rober\gtm-mcp-py313\` | New virtual environment |
| `C:\Development\General Analytics\.mcp.json` | Updated to use local server |
| `C:\Users\rober\application_default_credentials.json` | Re-authenticated with GTM scopes |

---

### Lessons Learned

1. **Local servers are more reliable than proxies:** Network dependencies add failure points. If you can run something locally, it will be more stable.

2. **Consistent architecture pays off:** Using the same pattern (FastMCP + ADC) for both analytics-mcp and gtm-mcp means less to remember and easier troubleshooting.

3. **Single credential file for multiple servers:** Application Default Credentials can have multiple scopes, so one file works for both GA and GTM servers. Just need to re-authenticate when adding new scopes.

4. **API enablement is easy to forget:** When an API call fails with a "API not enabled" error, the fix is usually just enabling it in Google Cloud Console.

---

## 2026-01-21: DigitalOcean Deployment Workflow

### Session Goals
Establish a deployment workflow for syncing Samsung dashboard files from local development to a DigitalOcean droplet. The dashboard should be publicly accessible at robotproof.io.

---

### Part 1: SSH Configuration

#### What Was Done
The deployment uses an existing SSH configuration with a host alias `digitalocean` pointing to a DigitalOcean droplet.

**SSH Config Location:** `C:\Users\rober\.ssh\config`

**Host Alias:** `digitalocean`

**Droplet IP:** 104.248.11.188

**Key File:** `~/.ssh/digitalocean`

#### Plain English
SSH (Secure Shell) is a way to securely connect to a remote server and run commands or transfer files. Instead of typing the IP address and key file every time, you can create a "host alias" - a nickname that remembers all those details. So instead of typing `ssh -i ~/.ssh/digitalocean root@104.248.11.188`, you just type `ssh digitalocean`.

---

### Part 2: Deployment Command

#### The SCP Approach

**Command:**
```bash
scp clients/samsung/dashboards/scom-overview.html digitalocean:/var/www/html/samsung/ai-visibility/index.html
```

#### What This Does
- `scp` = Secure Copy Protocol (copies files over SSH)
- Takes the local file `scom-overview.html`
- Uploads it to the server at `/var/www/html/samsung/ai-visibility/`
- Renames it to `index.html` so it serves as the default page

#### Plain English
SCP is like drag-and-drop for remote servers. You tell it "take this file from my computer and put it over there on the server." The command above copies the dashboard HTML file and places it where the web server (Nginx) can serve it to visitors.

---

### Part 3: Local Folder Reorganization

#### The Problem
The original dashboard HTML referenced assets using paths like `../assets/fonts/` and `../assets/logo.jpg`. These paths only work when the HTML file is in a specific location relative to the assets folder. On the server, the structure is different.

#### The Solution
Reorganized the local `dashboards/` folder to mirror the server structure:

**Before:**
```
clients/samsung/
├── assets/
│   ├── fonts/
│   ├── logo.jpg
│   ├── sov.jpg
│   └── ai visi.jpg
└── dashboards/
    └── scom-overview.html (references ../assets/)
```

**After:**
```
clients/samsung/dashboards/
├── fonts/           (copied from assets/fonts)
├── images/          (logo.jpg, sov.jpg, source_visi.jpg, referral.jpg, ai-visi.jpg)
├── scom-overview.html (references ./fonts/ and ./images/)
└── ... other test files
```

**Server Structure (matching):**
```
/var/www/html/samsung/ai-visibility/
├── fonts/
├── images/
└── index.html
```

#### Plain English
Think of it like packing a suitcase. The dashboard HTML file needs its fonts and images to be in specific places relative to itself. By organizing the local folder to match exactly how it will look on the server, we can copy everything over without needing to change any paths. Same folder structure = same paths work everywhere.

---

### Part 4: File Path Updates

#### Changes Made in Dashboard HTML

**Font paths:**
- Before: `../assets/fonts/SamsungSharpSans-Bold.woff2`
- After: `./fonts/SamsungSharpSans-Bold.woff2`

**Image paths:**
- Before: `../assets/logo.jpg`
- After: `./images/logo.jpg`

#### Filename Fix

**Problem:** The file `ai visi.jpg` has a space in the name. Spaces in URLs become `%20` which looks ugly and can cause issues.

**Solution:** Renamed to `ai-visi.jpg` (hyphen instead of space).

#### Plain English
Web addresses (URLs) don't handle spaces well. If you try to link to a file called "my file.jpg", the browser converts it to "my%20file.jpg" - that `%20` is the code for a space. It's cleaner and safer to use hyphens instead: "my-file.jpg" works perfectly in URLs.

---

### Part 5: Nginx Configuration

#### What Nginx Is
Nginx (pronounced "engine-x") is the web server software running on the DigitalOcean droplet. It receives requests from browsers and serves the appropriate files.

#### Configuration Changes

**File:** `/etc/nginx/sites-enabled/robotproof.io`

**Added:**
1. A location block for static assets (images, fonts, CSS, JS):
   ```nginx
   location ~ \.(jpg|jpeg|png|gif|ico|css|js|woff|woff2|ttf|svg)$ {
       # serves these file types directly
   }
   ```

2. A location block for the Samsung directory:
   ```nginx
   location /samsung/ {
       index index.html;
   }
   ```

#### Plain English
Nginx needs to know what to do when someone visits different URLs:
- The static assets rule says "if someone requests a file ending in .jpg, .woff2, etc., just serve that file directly"
- The Samsung directory rule says "if someone visits /samsung/ai-visibility/, serve the index.html file in that folder"

Without the `index index.html;` directive, visiting the folder URL would show a "forbidden" error or a directory listing instead of the dashboard.

---

### Part 6: Final Result

#### Live URL
**Dashboard:** https://robotproof.io/samsung/ai-visibility/

#### Deployment Workflow Summary

1. **Edit locally:** Make changes to `clients/samsung/dashboards/scom-overview.html`
2. **Test locally:** Open the HTML file in a browser to verify changes
3. **Deploy:** Run the scp command to upload to server
4. **Verify:** Visit the live URL to confirm deployment

#### Files Modified

| File | Change |
|------|--------|
| `clients/samsung/dashboards/scom-overview.html` | Updated font and image paths |
| `clients/samsung/dashboards/fonts/` | Created, copied fonts from assets |
| `clients/samsung/dashboards/images/` | Created, copied images from assets |
| `/etc/nginx/sites-enabled/robotproof.io` (server) | Added static asset and Samsung location blocks |

---

### Lessons Learned

1. **Mirror structures for easy deployment:** When local and server folder structures match, you can copy files without path translation. This eliminates a whole class of "works locally but not on server" bugs.

2. **Avoid spaces in filenames:** Spaces in filenames cause URL encoding issues. Always use hyphens or underscores for multi-word filenames.

3. **Nginx needs explicit index directive:** Without `index index.html;` in the location block, Nginx won't automatically serve index.html when you visit a directory URL.

4. **SCP is sufficient for simple deployments:** For single-file or small-directory deployments, SCP is simpler than setting up CI/CD pipelines or Git-based deployment hooks.

---

## 2026-01-21: Nginx Basic Authentication for Samsung Dashboard

### Session Goals
Add password protection to the Samsung dashboard at robotproof.io/samsung/ so only authorized users can access it.

---

### Part 1: What is Basic Authentication?

#### Technical Explanation
HTTP Basic Authentication is a simple authentication scheme built into the HTTP protocol. When enabled, the web server challenges visitors with a username/password prompt before allowing access. The credentials are sent with each request (Base64 encoded, not encrypted - hence always use with HTTPS).

#### Plain English
Basic auth is like putting a lock on a door. When someone tries to visit the protected page, a popup appears asking for a username and password. If they enter the correct credentials, they can see the page. If not, they get an "Unauthorized" error. It's the simplest way to add password protection to a website without building a full login system.

---

### Part 2: Creating the Password File

#### What Was Done

**Tool used:** `htpasswd` from the `apache2-utils` package

**Command to create password file:**
```bash
htpasswd -c /etc/nginx/.htpasswd_samsung samsung
```
- `-c` = create new file (omit this flag when adding additional users)
- `/etc/nginx/.htpasswd_samsung` = path to the password file
- `samsung` = the username

**Credentials configured:**
- Username: `samsung`
- Password: `Samsung2026`

#### Plain English
The `htpasswd` utility creates a special file that stores usernames and encrypted passwords. Nginx reads this file to verify credentials. The password is stored as a hash (one-way encryption), so even if someone accesses the file, they can't see the actual password - only a scrambled version of it.

#### Problem Encountered: Special Characters in Passwords

**Issue:** Initial attempts to use passwords with special characters like `!` and `#` caused shell escaping problems.

**Example of failing commands:**
```bash
# These failed due to shell interpretation
htpasswd -b /etc/nginx/.htpasswd_samsung samsung Samsung#2026!
htpasswd -b /etc/nginx/.htpasswd_samsung samsung 'Samsung#2026!'
```

**Solution:** Used an alphanumeric password (`Samsung2026`) to avoid escaping issues.

#### Plain English
Special characters like `!` and `#` have special meanings in the command line (bash shell). The `!` triggers history expansion (recalls previous commands), and `#` starts a comment (everything after it is ignored). While there are ways to escape these characters, the simplest solution was to use a password without special characters. For a client demo dashboard, this provides sufficient security.

---

### Part 3: Nginx Configuration

#### Configuration Changes

**File:** `/etc/nginx/sites-enabled/robotproof.io`

**Updated location block:**
```nginx
location /samsung/ {
    auth_basic "Samsung Dashboard";
    auth_basic_user_file /etc/nginx/.htpasswd_samsung;
    try_files $uri $uri/ $uri/index.html =404;
}
```

#### What Each Directive Does

| Directive | Purpose |
|-----------|---------|
| `auth_basic "Samsung Dashboard"` | Enables basic auth and sets the prompt text shown in the login popup |
| `auth_basic_user_file /etc/nginx/.htpasswd_samsung` | Points to the password file containing valid credentials |
| `try_files $uri $uri/ $uri/index.html =404` | Tells Nginx how to find and serve files in this location |

#### Plain English
These three lines tell Nginx: "Before showing anything in the /samsung/ folder, ask for a username and password. Check the credentials against the .htpasswd_samsung file. If they're correct, serve the requested files. If not, show an error."

---

### Part 4: Session Behavior

#### How Credential Caching Works

**Browser behavior:**
- Once entered, credentials are cached by the browser for the current session
- The user can refresh the page or navigate within the protected area without re-entering credentials
- Credentials are cleared when the browser is closed
- Opening a new browser window/tab to the same URL does NOT require re-entering credentials (session-wide)

**Server-side:**
- No server-side session or timeout configuration
- The browser sends credentials with every request (Basic auth is stateless)
- Nginx validates against the htpasswd file each time (very fast)

#### Plain English
Once you log in, you don't have to keep typing your password for every page or refresh. Your browser remembers the credentials until you close it. This is convenient for the client reviewing the dashboard - they log in once per browser session and can freely navigate and refresh without interruption.

---

### Part 5: Final Result

#### Protected URL
**Dashboard:** https://robotproof.io/samsung/ai-visibility/

**Credentials:**
- Username: `samsung`
- Password: `Samsung2026`

#### How to Test
1. Open the URL in a private/incognito window (to ensure fresh session)
2. Enter username and password when prompted
3. Dashboard loads
4. Refresh the page - no prompt (credentials cached)
5. Close browser completely and reopen - prompt appears again

---

### Files Modified

| Location | File | Change |
|----------|------|--------|
| Server | `/etc/nginx/.htpasswd_samsung` | Created - stores encrypted credentials |
| Server | `/etc/nginx/sites-enabled/robotproof.io` | Added auth_basic directives to /samsung/ location |

---

### Lessons Learned

1. **Avoid special characters in command-line passwords:** Characters like `!` and `#` have special meanings in bash. Either escape them carefully or use alphanumeric passwords for simplicity.

2. **htpasswd requires apache2-utils:** On Ubuntu/Debian, install with `apt install apache2-utils` before using htpasswd.

3. **Basic auth is stateless but browser-cached:** The server doesn't maintain sessions - it validates credentials on every request. The browser caches credentials for convenience, clearing them on browser close.

4. **auth_basic prompt text is customizable:** The string after `auth_basic` appears in the browser's login popup, so use something descriptive like "Samsung Dashboard" instead of generic text.

5. **Always use HTTPS with basic auth:** Basic auth only Base64-encodes credentials (not encryption). Without HTTPS, credentials are transmitted in plain text.

---

## 2026-01-20: Sunburst Prompts Visualization & Prompt Rankings Table

### Session Goals
Create two new interactive dashboard components for the Samsung S.com Overview dashboard: a hierarchical visualization for prompt categories and a data table for prompt performance metrics. The components should work together as an integrated filter system.

---

### Part 1: The Sunburst Chart Requirement

#### What Was Needed
The dashboard needed a way to visualize the hierarchical prompt categories (TV Features, TV Models, TV Reviews & Brand, TV Sizes) and their subcategories. Users should be able to explore the hierarchy by drilling down into specific categories and see sample prompts for their selection.

#### Why a Sunburst Chart?
A sunburst chart displays hierarchical data as concentric rings. The center represents the root (all prompts), and each ring outward represents deeper levels of the hierarchy. It is compact, visually engaging, and supports intuitive click-to-drill-down interaction.

#### Plain English
Imagine a pie chart, but instead of one layer, it has rings like a tree stump. The inner ring shows the main categories (TV Features, TV Models, etc.), and the outer rings show subcategories. You can click any slice to "zoom in" and see just that category's breakdown. It is like zooming into a map - click on a country to see its cities, click on a city to see its neighborhoods.

---

### Part 2: Sunburst Implementation Details

#### Technical Specifications

**File:** `clients/samsung/templates/sunburst-prompts.html`

**Size:** 550x550 pixels, fills half the container width

**D3.js Features Used:**
- `d3.hierarchy()` - Converts nested data into a tree structure
- `d3.partition()` - Calculates the size of each segment based on value
- `d3.arc()` - Draws the curved segments
- `d3.interpolate()` - Smooth transitions when drilling down

**Color Scheme:**
```javascript
const categoryColors = {
    "TV Features": "#6366f1",      // Purple
    "TV Models": "#22c55e",        // Green
    "TV Reviews & Brand": "#f59e0b", // Orange
    "TV Sizes": "#ef4444"          // Red
};
```

#### Navigation Features

1. **Drill-down by clicking** - Click any segment to zoom into that category
2. **Breadcrumb navigation** - Shows current path (e.g., "All > TV Features > Display > OLED") with clickable items to go back
3. **Subcategory chips** - Quick-access buttons showing immediate children of current selection
4. **Sample prompts list** - Displays example prompts matching the current selection

#### Plain English
The sunburst chart has multiple ways to navigate:
- **Click a slice** to zoom in (like double-clicking a folder)
- **Click the breadcrumb trail** at the top to go back up (like clicking the folder path in Windows Explorer)
- **Click a chip button** below the chart to jump to a specific subcategory (like shortcuts)
- **Read the prompts list** on the right to see what prompts match your selection

---

### Part 3: The Prompt Rankings Table Requirement

#### What Was Needed
A data table showing prompt-level performance metrics including:
- Which AI model (ChatGPT, Gemini, Perplexity, AI Overview)
- Topic category and search volume
- Visibility score
- Position rankings at two time points
- Position change indicators
- Samsung product mentions

#### Design Constraints
- Full-width layout (spans entire container)
- Fixed height (600px) with scroll for large datasets
- Sticky header so column names stay visible while scrolling
- Visual indicators (colors, icons, badges) for quick scanning

#### Plain English
This is a spreadsheet-like table showing how Samsung performs for each AI prompt. Each row is a different prompt (like "best 65 inch TV 2026"). The columns show: which AI tool answered it, what category it belongs to, how popular that search is, how visible Samsung is in the answer, where Samsung ranks in positions 1-10, whether that position improved or worsened, and whether a specific Samsung product was mentioned.

---

### Part 4: Prompt Rankings Table Implementation

#### Technical Specifications

**File:** `clients/samsung/templates/prompt-rankings-table.html`

**Table Columns:**
| Column | Description |
|--------|-------------|
| Prompt | The search query text |
| Model | AI platform icon (ChatGPT, Gemini, Perplexity, AI Overview) |
| Topic | Category tag matching sunburst |
| Topic Vol. | Monthly search volume for the topic |
| Visibility | Horizontal bar showing 0-100% visibility score |
| Position (older date) | Ranking position from earlier period |
| Position (newer date) | Ranking position from recent period |
| Change | Up/down arrow, "New", or "Lost" badge |
| Product (older date) | Samsung product mentioned earlier |
| Product (newer date) | Samsung product mentioned recently |

#### Model Icons
```css
.model-chatgpt { background-color: #10a37f; }  /* ChatGPT green */
.model-gemini { background-color: #4285f4; }   /* Gemini blue */
.model-perplexity { background-color: #1a1a2e; } /* Perplexity dark */
.model-aio { background-color: #ea4335; }      /* AI Overview red */
```

#### Position Color Coding
- **Green (#22c55e):** Positions 1-3 (top rankings)
- **Amber (#f59e0b):** Positions 4-6 (mid-page)
- **Gray (#6b7280):** Positions 7+ (below fold)

#### Change Indicators
- **Up arrow (green):** Position improved
- **Down arrow (red):** Position worsened
- **"New" badge (blue):** Samsung newly appeared
- **"Lost" badge (red):** Samsung dropped off

#### Plain English
The table uses visual shortcuts so you can scan quickly:
- **Model icons** tell you which AI tool at a glance (green = ChatGPT, blue = Gemini, etc.)
- **Position colors** flag good vs. bad rankings (green = top 3, amber = middle, gray = low)
- **Visibility bars** show strength visually without reading numbers
- **Change badges** highlight important movements ("New" in blue = good news, "Lost" in red = attention needed)

---

### Part 5: Cross-Component Integration

#### How Sunburst Filters the Table

When a user clicks a category in the sunburst chart, the table below should filter to show only prompts in that category. This required a communication mechanism between the two components.

#### Technical Implementation

**Global Filter Function:**
```javascript
// In prompt-rankings-table.html
window.renderRankingsTable = function(filter) {
    // filter can be: null (show all), or "TV Features", "TV Models", etc.
    const filteredData = filter
        ? promptData.filter(p => p.topic.includes(filter))
        : promptData;
    renderTable(filteredData);
};
```

**Sunburst Calls Filter:**
```javascript
// In sunburst-prompts.html
function onSegmentClick(category) {
    // ... update sunburst visualization ...

    // Filter the rankings table
    if (window.renderRankingsTable) {
        window.renderRankingsTable(category);
    }
}
```

#### Why This Approach?
Using a global function on the `window` object is simple and works well for loosely-coupled components in a single-page dashboard. The sunburst does not need to know how the table works internally - it just calls the function with a category name.

#### Plain English
When you click on "TV Features" in the pie chart, it tells the table below "show me only TV Features prompts." The chart and table talk to each other through a simple message system - the chart says "filter by X" and the table listens and responds. They do not need to know each other's internal workings, just how to send and receive the message.

---

### Part 6: Bug Fixes - Layout and Tooltip Conflicts

#### Problem 1: Layout Spacing

**What Happened:**
When the new components were added to the assembled dashboard, they did not have proper spacing from the edges. The content was touching the container edges.

**Technical Cause:**
Other templates (like `line-charts.html`) included a `.container` wrapper with padding and max-width. The new templates were missing this wrapper.

**Plain English:**
Imagine putting a picture in a frame but forgetting the matting (the border around the picture). The picture touches the frame edges and looks cramped. We needed to add the same padding wrapper that other components use.

**Solution:**
Added `.container` wrapper to both new templates:
```html
<div class="container">
    <div class="sunburst-card">
        <!-- component content -->
    </div>
</div>
```

---

#### Problem 2: Tooltip Style Conflicts

**What Happened:**
When multiple components with tooltips (KPI cards, sunburst, rankings table) were assembled into one dashboard, the tooltip styles conflicted. Hovering over one tooltip affected others.

**Technical Cause:**
All components used the same global CSS class `.tooltip-icon`. When assembled, these styles merged and overrode each other unpredictably.

**Plain English:**
Imagine three different remote controls all using the same "power" button frequency. When you press power on one, all three TVs turn on or off randomly. Each component's tooltip was responding to the same CSS rules.

**Solution:**
Scoped the tooltip CSS selectors to each component's wrapper class:
```css
/* Instead of */
.tooltip-icon { ... }

/* Use scoped selectors */
.sunburst-card .tooltip-icon { ... }
.prompt-rankings-card .tooltip-icon { ... }
```

This ensures each component's tooltip styles only apply within that component's container.

---

### Part 7: Following the 3-Stage Workflow

#### How This Session Applied the Workflow

1. **Stage 1 - Test Files Created:**
   - `dashboards/test-sunburst-prompts.html` - Developed sunburst in isolation
   - `dashboards/test-prompt-rankings-table.html` - Developed table in isolation
   - `dashboards/test-prompt-rankings.html` - Tested both together (prototype)

2. **Stage 2 - Templates Updated:**
   - `templates/sunburst-prompts.html` - Approved sunburst component
   - `templates/prompt-rankings-table.html` - Approved table component

3. **Stage 3 - Config Updated:**
   - Added both components to `configs/scom-overview.json`
   - Ran assembly script to generate updated dashboard

#### Plain English
We followed the "test kitchen" approach:
1. First, we experimented with each component in its own test file (like testing a recipe)
2. Once working, we saved the approved version to the templates folder (like writing down the final recipe)
3. Finally, we updated the config and assembled the dashboard (like serving the finished dish)

---

### Session Summary

| Task | Status |
|------|--------|
| Create sunburst prompts visualization | Complete |
| Create prompt rankings table | Complete |
| Implement cross-component filtering | Complete |
| Fix layout spacing issues | Complete |
| Fix tooltip style conflicts | Complete |
| Update dashboard config | Complete |
| Create test files | Complete |

### Files Created

**Templates:**
- `clients/samsung/templates/sunburst-prompts.html` - D3.js sunburst chart component
- `clients/samsung/templates/prompt-rankings-table.html` - Prompt rankings table component

**Test Files:**
- `clients/samsung/dashboards/test-sunburst-prompts.html` - Standalone sunburst test
- `clients/samsung/dashboards/test-prompt-rankings-table.html` - Standalone table test
- `clients/samsung/dashboards/test-prompt-rankings.html` - Combined prototype

### Files Modified

- `clients/samsung/configs/scom-overview.json` - Added sunburst-prompts and prompt-rankings-table to components array

### Decisions Made

| Decision | Why | Alternative Rejected |
|----------|-----|---------------------|
| D3.js sunburst chart | Enables hierarchical drill-down, compact display, intuitive interaction | Flat dropdown (no hierarchy), tree view (more space), nested accordions (more clicks) |
| Global `window.renderRankingsTable()` function | Simple cross-component communication, loose coupling | Custom events (complex), direct DOM manipulation (brittle), shared state (overkill) |
| Scoped tooltip CSS selectors | Prevents conflicts in assembled dashboard | Global classes (conflicts), inline styles (hard to maintain) |
| 600px max-height with sticky header | Shows substantial data while keeping header visible | Full-height (overwhelms page), pagination (hides data) |

### Lessons Learned

1. **Scope your CSS:** When building components that will be assembled together, use wrapper-scoped selectors (`.component-name .class`) to prevent style conflicts
2. **Test in isolation AND together:** Components that work alone may conflict when combined - always test the assembled result
3. **Simple communication wins:** A global function is simpler and more debuggable than custom events for single-page dashboards
4. **Visual encoding speeds scanning:** Using colors, icons, and badges instead of text labels lets users scan tables faster
5. **Consistent wrappers matter:** All components should use the same container pattern for consistent spacing in the assembled dashboard

---

## 2026-01-20: Samsung Template Assembly System

### Session Goals
Create a template-first assembly system for Samsung dashboards that prevents unintended changes to approved components and enables reproducible dashboard generation.

---

### Part 1: The Problem with LLM-Generated Dashboards

#### What Was Happening
Each time we asked Claude to generate a dashboard, it would produce slightly different results - even when given the same prompts. Once a component was approved by the client, we had no way to guarantee it would stay exactly the same in future dashboard generations.

#### Why This Matters
- Client-approved HTML components should be immutable (unchangeable)
- Regenerating components risks introducing subtle bugs or styling differences
- Manual copy-paste between dashboards is error-prone

#### Plain English
Imagine if every time you asked a printer to print your business card, it used slightly different fonts or colors. Once you have approved a design, you want it printed exactly the same way every time. We needed a system where approved dashboard pieces stay frozen exactly as approved.

---

### Part 2: The Template-First Solution

#### Architecture Overview

The system has three parts:

1. **Templates** (`clients/samsung/templates/`) - Approved HTML components that never change
2. **Configs** (`clients/samsung/configs/`) - JSON files that define which templates to use and in what order
3. **Assembly Script** (`clients/samsung/scripts/assemble_dashboard.py`) - Reads config, combines templates, outputs complete HTML

#### Directory Structure
```
clients/samsung/
├── templates/
│   ├── base/
│   │   ├── fonts.html      # @font-face declarations
│   │   └── tokens.html     # CSS variables (colors, spacing)
│   ├── header.html         # Dashboard header with logo
│   ├── kpi-cards.html      # KPI metric cards
│   └── line-charts.html    # Trend line charts
├── configs/
│   └── scom-overview.json  # S.com Overview dashboard config
└── scripts/
    └── assemble_dashboard.py
```

#### Plain English
Think of it like building with LEGO blocks:
- **Templates** are the individual LEGO pieces (header block, KPI block, chart block)
- **Configs** are the instruction manual that says "put the header on top, then KPI cards, then charts"
- **Assembly script** is you following the instructions to snap the pieces together

Once a LEGO piece is made, you do not redesign it every time you build - you just reuse it.

---

### Part 3: Template Files

#### base/fonts.html
Contains Samsung font declarations:
```html
<style>
@font-face {
    font-family: 'Samsung Sharp Sans';
    src: url('../assets/fonts/SamsungSharpSans-Bold.woff2') format('woff2');
    font-weight: 700;
}
@font-face {
    font-family: 'Samsung One';
    src: url('../assets/fonts/SamsungOne-400.woff2') format('woff2');
    font-weight: 400;
}
/* ... additional font weights ... */
</style>
```

#### base/tokens.html
Contains CSS custom properties (design tokens):
```html
<style>
:root {
    /* Colors */
    --samsung-blue: #1428a0;
    --background-light: #f7f7f7;
    --text-primary: #333333;

    /* Spacing */
    --spacing-sm: 0.5rem;
    --spacing-md: 1rem;
    --spacing-lg: 1.5rem;

    /* Typography */
    --font-heading: 'Samsung Sharp Sans', sans-serif;
    --font-body: 'Samsung One', sans-serif;
}
</style>
```

#### header.html
The dashboard header component with logo and title alignment.

#### kpi-cards.html
The KPI cards row with tooltips and change indicators.

#### line-charts.html
Line chart component with insights annotation boxes.

#### Plain English
Each template file is a self-contained piece of HTML that can work on its own. The fonts file tells the browser how to load Samsung's custom fonts. The tokens file defines all the colors and spacing so everything looks consistent. The other files are the actual visual components you see on the page.

---

### Part 4: Configuration Files

#### What a Config File Contains

**File:** `configs/scom-overview.json`

```json
{
    "name": "S.com Overview Dashboard",
    "output": "../dashboards/scom-overview.html",
    "components": [
        "base/fonts",
        "base/tokens",
        "header",
        "kpi-cards",
        "line-charts"
    ]
}
```

#### How It Works
- `name` - Human-readable dashboard name
- `output` - Where to save the assembled HTML file
- `components` - Ordered list of templates to include (top to bottom)

#### Plain English
The config file is like a recipe that says "to make the S.com Overview Dashboard, combine fonts, tokens, header, KPI cards, and line charts - in that order - and save the result as scom-overview.html."

---

### Part 5: The Assembly Script

#### What It Does

**File:** `scripts/assemble_dashboard.py`

1. Reads the JSON config file
2. For each component in the list, reads the corresponding `.html` file from templates/
3. Concatenates all the HTML into one complete document
4. Wraps everything in proper `<!DOCTYPE html>`, `<head>`, and `<body>` tags
5. Writes the output file

#### Usage
```bash
uv run clients/samsung/scripts/assemble_dashboard.py clients/samsung/configs/scom-overview.json
```

#### Plain English
The script is like an assembly line worker who follows the recipe card:
1. "Okay, the recipe says I need fonts first" - grabs the fonts template
2. "Next is tokens" - adds the tokens template
3. "Then header, KPI cards, line charts" - adds each in order
4. Wraps everything in a complete HTML page
5. Saves the final file

---

### Part 6: Benefits of This Approach

#### Immutability
Once a template is approved, it never changes. The `header.html` that was signed off on January 20th will be the exact same `header.html` used in every dashboard that includes it.

#### Reproducibility
Running the assembly script twice with the same config produces byte-for-byte identical output. No LLM variation.

#### Flexibility
Want a different dashboard? Create a new config file with different components or different order. No need to regenerate the actual components.

#### Maintainability
Bug in the KPI cards? Fix it once in `kpi-cards.html` and all dashboards using that template get the fix automatically next time they are assembled.

#### Plain English
- **Immutability** - "Once approved, do not touch it"
- **Reproducibility** - "Same recipe, same dish, every time"
- **Flexibility** - "Mix and match pieces to create new dashboards"
- **Maintainability** - "Fix a piece once, fix it everywhere"

---

### Part 7: Future Components

The system is designed to accommodate additional components. Planned templates:

| Template | Purpose | Status |
|----------|---------|--------|
| `donut-chart.html` | Sentiment distribution pie chart | Not yet created |
| `stacked-bar.html` | Sentiment over time bars | Not yet created |
| `leaderboard-table.html` | Brand ranking table | Not yet created |
| `data-table.html` | Detailed data grid | Not yet created |

When these are created, they can be added to any dashboard by simply including them in the config's `components` array.

---

### Session Summary

| Task | Status |
|------|--------|
| Create templates/base/ folder with fonts and tokens | Complete |
| Create header.html template | Complete |
| Create kpi-cards.html template | Complete |
| Create line-charts.html template | Complete |
| Create scom-overview.json config | Complete |
| Create assemble_dashboard.py script | Complete |

### Files Created

**Templates:**
- `clients/samsung/templates/base/fonts.html` - Samsung font declarations
- `clients/samsung/templates/base/tokens.html` - CSS design tokens
- `clients/samsung/templates/header.html` - Header component
- `clients/samsung/templates/kpi-cards.html` - KPI cards component
- `clients/samsung/templates/line-charts.html` - Line charts component

**Configs:**
- `clients/samsung/configs/scom-overview.json` - S.com Overview dashboard configuration

**Scripts:**
- `clients/samsung/scripts/assemble_dashboard.py` - Template assembly script

### Decision Made

| Decision | Why | Alternative Rejected |
|----------|-----|---------------------|
| Template-first assembly with immutable templates | Prevents unintended changes to approved components, enables reproducible builds, separates layout (config) from content (templates) | LLM regeneration each time (inconsistent results), monolithic HTML files (hard to maintain) |
| JSON config for component order | Easy to read/edit, standard format, no code changes needed to reorder components | Hardcoded order in script (inflexible), YAML (extra dependency) |
| Separate base/ folder for fonts and tokens | These foundational files are used by all components, separating them emphasizes their shared nature | Mixed with component templates (confusing hierarchy) |

### Lessons Learned

1. **Immutability enables trust:** When clients know approved components cannot accidentally change, they have more confidence in the output
2. **Config-driven assembly is flexible:** Changing dashboard layout requires editing JSON, not code
3. **Template naming matters:** Using descriptive names like `kpi-cards.html` (not `component1.html`) makes configs self-documenting
4. **Base styles should be separate:** Fonts and tokens are dependencies for all other components - keeping them in a `base/` folder makes this relationship clear

---

## Critical Workflow: Component-First Development (3 Stages)

**This is a mandatory workflow for all dashboard development.**

### The Rule

All component changes MUST follow a 3-stage process: Test File -> Template -> Assembled Dashboard. Never skip stages.

### The 3-Stage Workflow

#### Stage 1: Edit Test File (Development Sandbox)

Edit the test file for your component:
- e.g., `dashboards/test-line-chart.html`
- This is your sandbox for experimenting and refining
- Open in browser to verify changes visually
- Iterate until the component looks and works correctly

#### Stage 2: Approve and Update Template (Source of Truth)

Once the test file is correct, copy changes to the template:
- e.g., `templates/line-charts.html`
- Template becomes the locked-in, approved version
- This is the official source of truth for that component

#### Stage 3: Run Assembly Script (Generate Output)

Assemble the final dashboard:
```bash
uv run scripts/assemble_dashboard.py configs/scom-overview.json
```
- Outputs to `dashboards/scom-overview.html`
- Assembly combines all templates into complete dashboard
- Generated output should never be edited directly

### File Hierarchy

```
dashboards/test-*.html     <- Development sandbox (edit first)
        | (approve)
        v
templates/*.html           <- Approved components (source of truth)
        | (assembly)
        v
dashboards/scom-*.html     <- Generated output (never edit directly)
```

### Why This 3-Stage Process Matters

- **Test files are for experimentation** - break things, try ideas, iterate quickly
- **Templates are the source of truth** - only approved, working code goes here
- **Assembly script is pure concatenation** - it reads templates verbatim using marker extraction (`<!-- CSS -->`, `<!-- HTML -->`, `<!-- SCRIPT -->`) and merges them without modification
- **Dashboard edits get overwritten** - if you edit the generated dashboard HTML directly, your changes will be lost on the next assembly run
- **Keeps components modular** - same template can be reused across different dashboards

### Assembly Script Details

- **Location:** `clients/samsung/scripts/assemble_dashboard.py`
- **Behavior:** Reads templates verbatim using marker extraction
- **Config format:** JSON files in `configs/` directory specify component order
- **Output:** Complete HTML dashboards in `dashboards/` directory

### Example - Correct 3-Stage Workflow

```
1. Edit dashboards/test-line-chart.html (experiment with dates, values, styles)
2. Open test-line-chart.html in browser, verify it looks correct
3. Copy approved changes to templates/line-charts.html
4. Run: uv run scripts/assemble_dashboard.py configs/scom-overview.json
5. Dashboard updated with new component
```

### Example - WRONG Workflows

**Skipping Stage 1 (editing template directly):**
```
1. Edit templates/line-charts.html directly  <- WRONG: no sandbox testing
2. Run assembly
3. Discover bugs in generated dashboard
4. Now template has untested code
```

**Skipping Stage 2 (editing generated dashboard):**
```
1. Edit dashboards/scom-overview.html directly  <- WRONG: changes will be lost
2. Changes lost on next assembly run
```

### Plain English

Think of it like developing a recipe:

1. **Test kitchen (test file):** Experiment with ingredients and techniques. Taste as you go. Make mistakes. This is where you figure out what works.

2. **Official recipe card (template):** Once the dish tastes great, write down the final recipe. This becomes the official version that anyone can follow to get the same result.

3. **Serving the dish (assembled dashboard):** When you need to serve guests, follow the recipe card exactly. You do not improvise at serving time - you use the tested, approved recipe.

If you skip the test kitchen and write recipes without testing, you end up with unreliable recipes. If you improvise while serving (editing the generated dashboard), your changes vanish the next time someone follows the recipe card.

### When to Apply This Rule

- Changing chart data, labels, or formatting
- Updating styles (colors, spacing, fonts)
- Adding or removing elements within a component
- Fixing bugs in component behavior
- Trying new features or layouts

**All of these changes start in the test file, get approved into the template, then get assembled.**

### Common Mistake (2026-01-20)

The workflow was violated by editing `templates/line-charts.html` directly without first updating `dashboards/test-line-chart.html`. This skipped the testing stage and put untested code directly into the source of truth.

---

## 2026-01-20: Samsung KPI Cards Element (Client Specification)

### Session Goals
Implement 4 KPI cards for the Samsung S.com Overview dashboard based on client specification document ("Ai reporting Client ask from Jason.pdf"). The cards needed custom icons, tooltips, and change state indicators.

---

### Part 1: Understanding the Client Requirement

#### What The Client Asked For
The PDF specification ("Ai reporting Client ask from Jason.pdf") outlined a dashboard with 4 key performance indicators:
1. **Share of Voice** - What percentage of the market conversation is about Samsung
2. **Source Visibility** - How visible Samsung is across different sources
3. **Referral Traffic** - How many visitors come from referral links
4. **AI Visibility** - A score representing Samsung's presence in AI-generated responses

Each card needed:
- A distinctive icon representing the metric
- The metric label and value
- A percentage change indicator showing period-over-period performance

#### Plain English
The client wanted a row of 4 "scorecard" boxes at the top of their dashboard. Each box shows one important number with a small picture (icon) representing what that number means. Below each number is a smaller indicator showing whether that number went up or down compared to last time.

---

### Part 2: Custom Icon Creation

#### What Happened
The user created custom icons using Nano Baana (an AI image generation tool) to match the dashboard's visual style.

#### Icons Created

| Icon | File | Description |
|------|------|-------------|
| Share of Voice | `clients/samsung/assets/sov.jpg` | Speech bubble with bar chart - represents "voice" in market conversations |
| Source Visibility | `clients/samsung/assets/source_visi.jpg` | Monitor with eye - represents visibility across sources |
| Referral Traffic | `clients/samsung/assets/referral.jpg` | Arrows converging to center - represents traffic flowing in |
| AI Visibility | `clients/samsung/assets/ai visi.jpg` | Brain with gear and sparkles - represents AI/machine learning presence |

#### Plain English
Instead of using generic icons from an icon library, the user created custom pictures that better represent what each metric actually measures. For example, "Share of Voice" uses a speech bubble with a bar chart inside because it is about how much of the conversation (voice) belongs to Samsung (measured as a chart/percentage).

---

### Part 3: Card Styling Implementation

#### Visual Design Decisions

**Icon sizing:**
```css
.kpi-icon {
    width: 64px;
    height: 64px;
    margin-bottom: 0.75rem;
}
```
Icons were enlarged to 64x64 pixels to make them more prominent and recognizable at a glance.

**Content centering:**
```css
.kpi-card {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    min-height: 160px;
}
```
All card content is centered both horizontally and vertically, with a minimum height ensuring consistent card sizes even if content varies.

**Label typography:**
```css
.kpi-label {
    font-family: 'Samsung Sharp Sans', sans-serif;
    font-weight: 700;
    font-size: 0.875rem;
    color: #333;
}
```
Labels use Samsung's brand font in bold to clearly identify each metric.

#### Plain English
We made the pictures bigger (64 pixels square instead of the typical 24-32), centered everything in the card, and used Samsung's official font in bold for the labels. The cards also have a minimum height so they all appear the same size on screen, even if one has a longer label than another.

---

### Part 4: Tooltip Feature

#### What We Built
An info tooltip that appears when hovering over a question mark icon in the top right corner of each card.

#### Technical Implementation
```css
.kpi-tooltip-trigger {
    position: absolute;
    top: 0.5rem;
    right: 0.5rem;
    width: 18px;
    height: 18px;
    background: #8091df;
    color: white;
    border-radius: 50%;
    font-size: 12px;
    cursor: help;
}

.kpi-tooltip-content {
    position: absolute;
    top: 2rem;
    right: 0;
    width: 200px;
    padding: 0.75rem;
    background: white;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    opacity: 0;
    visibility: hidden;
    transition: opacity 0.2s, visibility 0.2s;
}

.kpi-tooltip-trigger:hover + .kpi-tooltip-content {
    opacity: 1;
    visibility: visible;
}
```

#### Why CSS-Only?
We chose a CSS-only approach (using `:hover` and the adjacent sibling selector `+`) rather than JavaScript because:
1. Simpler code with no dependencies
2. Works in static HTML files without a server
3. Smooth fade transition is easy to achieve with CSS
4. No event listeners to manage or clean up

#### Plain English
Each card has a small question mark button in the corner. When you hover your mouse over it, a little explanation box fades in to tell you what that metric means. This is done entirely with CSS - no programming required - using a trick where hovering over one element can affect the visibility of the element right next to it.

---

### Part 5: 4-State Change Indicators

#### The Design Challenge
Change indicators typically show "up" or "down", but real-world data has more states:
- What if there is no comparison data available yet?
- What if the value stayed exactly the same?

#### The 4 States

| State | Color | Display | Use Case |
|-------|-------|---------|----------|
| N/A | Grey (#666666) | "N/A" | No comparison data available (new metric, data not collected) |
| No Change | Yellow (#feb447) | "0%" with dash | Value unchanged from previous period |
| Increase | Green (#96d551) | "+X%" with up arrow | Value went up |
| Decrease | Red (#ff4438) | "-X%" with down arrow | Value went down |

#### CSS Implementation
```css
.kpi-change {
    font-size: 0.875rem;
    font-weight: 600;
    margin-top: 0.25rem;
}

.kpi-change.na {
    color: #666666;
}

.kpi-change.no-change {
    color: #feb447;
}

.kpi-change.increase {
    color: #96d551;
}

.kpi-change.decrease {
    color: #ff4438;
}
```

#### HTML Usage
```html
<!-- No data available -->
<span class="kpi-change na">N/A</span>

<!-- Value unchanged -->
<span class="kpi-change no-change">— 0%</span>

<!-- Value increased -->
<span class="kpi-change increase">&#9650; +12%</span>

<!-- Value decreased -->
<span class="kpi-change decrease">&#9660; -8%</span>
```

#### Plain English
Most dashboards only show green (up) or red (down) arrows. But what if this is a brand new metric and we have nothing to compare it to? We show "N/A" in grey. What if the number is exactly the same as last month? We show "0%" in yellow with a dash instead of an arrow. This covers all the situations that can actually happen in real data.

---

### Part 6: Test Page Creation

#### What We Created
A test page at `clients/samsung/dashboards/test-kpi-cards-client.html` that demonstrates all 4 KPI cards with different change states.

#### Purpose of the Test Page
1. Visual verification that styling matches the specification
2. QA testing of all 4 change states
3. Reference implementation for other developers
4. Client approval before integrating into main dashboard

#### Plain English
Before adding these cards to the real dashboard, we created a separate "test page" that shows all four cards and all the different states they can be in. This lets us (and the client) see exactly how everything looks and catch any problems before they affect the real dashboard.

---

### Session Summary

| Task | Status |
|------|--------|
| Understand client specification | Complete |
| Implement 4 KPI cards | Complete |
| Custom icon integration | Complete |
| Add tooltip feature | Complete |
| Implement 4-state change indicators | Complete |
| Create test page | Complete |
| Update element specification | Complete |

### Files Created

- `clients/samsung/dashboards/test-kpi-cards-client.html` - Test page with all 4 states demonstrated

### Files Modified

- `clients/samsung/prompts/elements/kpi-cards.md` - Updated element specification with tooltip and change state documentation

### Icon Assets (User Created)

- `clients/samsung/assets/sov.jpg` - Share of Voice icon
- `clients/samsung/assets/source_visi.jpg` - Source Visibility icon
- `clients/samsung/assets/referral.jpg` - Referral Traffic icon
- `clients/samsung/assets/ai visi.jpg` - AI Visibility icon

### Decisions Made

| Decision | Why | Alternative Rejected |
|----------|-----|---------------------|
| CSS-only tooltips | No JavaScript required, simpler implementation, works in static HTML | JavaScript tooltips (unnecessary complexity) |
| 4-state change indicators | Covers all real-world scenarios (N/A, no change, up, down) | 2-state (up/down only, cannot represent missing or unchanged data) |
| 64x64px icon size | Makes icons prominent and recognizable at dashboard scale | Smaller sizes (24-32px) felt too subtle |
| min-height on cards | Ensures consistent card sizing regardless of content length | No min-height (cards would vary in size) |

### Lessons Learned

1. **Real data has edge cases:** Always design for "no data" and "unchanged" states, not just up/down
2. **CSS can replace JavaScript:** Hover effects and tooltips work well with pure CSS using `:hover` and sibling selectors
3. **Test pages for components:** Creating isolated test pages speeds up development and makes client approval easier
4. **Custom icons add polish:** Generic icons work, but custom icons that match the metric meaning look more professional

---

## 2026-01-20: Samsung TV Prompts CSV to JSON Parser

### Session Goals
Convert a Semrush export CSV containing 382 TV-related prompts into structured JSON that powers a hierarchical tag filter dropdown in the Samsung AI Visibility dashboard.

---

### Part 1: The Problem

#### What We Needed
The Samsung AI Visibility dashboard needs a tag filter dropdown where users can filter prompts by category. The prompts come from Semrush in a flat CSV format with hierarchical tags encoded using double underscore delimiters.

#### CSV Input Format
The CSV file (`tv_prompts_semrush_import_v2.csv`) contains rows like:
```
prompt,tag1,tag2,tag3,...
"best 55 inch tv 2025",TV Sizes__55 Inch,TV Reviews & Brand__Year Reviews__2025,...
```

The tags use `__` as a hierarchy delimiter:
- `TV Reviews & Brand__Year Reviews__2026` means: TV Reviews & Brand > Year Reviews > 2026
- This represents a three-level nested category

#### Plain English
Imagine a filing system where labels can have sub-labels. Instead of just "Electronics", you might have "Electronics > TVs > Samsung". The double underscore (`__`) is how these nested categories are written in a single text field. We needed to convert this flat text representation into an actual nested folder structure.

---

### Part 2: The JSON Structure (Option C)

#### Why "Option C"?
Three structures were considered:
- **Option A:** Flat list of tags with parent references
- **Option B:** Tag tree separate from prompts, no counts
- **Option C:** Tag tree with counts embedded + prompts array

Option C was chosen because the dashboard filter needs to show how many prompts match each tag level, and having counts pre-calculated means the frontend does not need to count on every filter change.

#### JSON Output Structure

```json
{
  "meta": {
    "totalPrompts": 382,
    "totalTags": 58
  },
  "tagTree": {
    "TV Features": {
      "count": 301,
      "children": {
        "AI": { "count": 35, "children": {} },
        "Audio": { "count": 60, "children": {} },
        "Display": {
          "count": 100,
          "children": {
            "OLED": { "count": 50, "children": {} },
            "QLED": { "count": 30, "children": {} }
          }
        }
      }
    },
    "TV Models": { "count": 347, "children": {...} },
    "TV Reviews & Brand": { "count": 621, "children": {...} },
    "TV Sizes": { "count": 130, "children": {...} }
  },
  "prompts": [
    {
      "text": "best 55 inch tv 2025",
      "tags": ["TV Sizes__55 Inch", "TV Reviews & Brand__Year Reviews__2025"]
    }
  ]
}
```

#### Plain English
The output JSON has three parts:
1. **meta** - A summary: how many prompts total, how many unique tags
2. **tagTree** - A nested folder structure where each folder shows how many items are inside it (counting items in subfolders too)
3. **prompts** - The actual list of prompts, each tagged with its categories

The count at each level includes all prompts in that category AND all subcategories. So if "TV Features" shows 301, that means 301 prompts have tags somewhere under "TV Features" (including AI, Audio, Display, etc.).

---

### Part 3: The Python Script

#### What The Script Does

**File:** `clients/samsung/scripts/parse_prompts_csv.py`

1. **Reads the CSV** - Opens the Semrush export file
2. **Extracts tags** - Looks at columns starting with "tag" (tag1, tag2, tag3...)
3. **Builds the tree** - For each tag like "A__B__C", creates nested nodes A > B > C
4. **Counts prompts** - Each node tracks which prompts belong to it
5. **Writes JSON** - Outputs the structured file

#### Key Technical Details

**Handling the hierarchy:**
```python
def add_tag_to_tree(tree, tag_path, prompt_index):
    parts = tag_path.split("__")
    current = tree
    for part in parts:
        if part not in current:
            current[part] = {"count": 0, "prompts": set(), "children": {}}
        current[part]["prompts"].add(prompt_index)
        current = current[part]["children"]
```

**Plain English:**
The script walks down the tag path like walking down a file path. For "TV Features__Display__OLED", it first goes to (or creates) "TV Features", then inside that goes to "Display", then inside that goes to "OLED". At each level, it remembers that this prompt belongs there.

#### Running the Script

```bash
uv run clients/samsung/scripts/parse_prompts_csv.py
```

This reads from `clients/samsung/assets/tv_prompts_semrush_import_v2.csv` and writes to `clients/samsung/assets/tv_prompts.json`.

---

### Part 4: The Top-Level Categories

The 382 prompts are organized under four main categories:

| Category | Count | Description |
|----------|-------|-------------|
| TV Features | 301 | Technical features (AI, Audio, Display, Smart TV, Gaming) |
| TV Models | 347 | Brand and model names (Samsung, LG, Sony models) |
| TV Reviews & Brand | 621 | Review types, brand comparisons, year-based reviews |
| TV Sizes | 130 | Screen sizes (43", 55", 65", 75", 85") |

Note: Counts can exceed 382 because one prompt can have multiple tags. A prompt about "best 55 inch Samsung OLED TV 2025" might be tagged under TV Sizes, TV Models, TV Features, AND TV Reviews.

#### Plain English
Think of this like a library where one book can be shelved in multiple sections using cross-references. A cookbook about Italian desserts might be listed under both "Cooking > Desserts" AND "Cooking > Italian". The same prompt can appear in multiple categories because it is relevant to multiple topics.

---

### Part 5: Dashboard Integration

#### How The Frontend Uses This

The tag filter dropdown in the AI Visibility dashboard:
1. Loads `tv_prompts.json` on page load
2. Renders `tagTree` as a nested expandable menu
3. Shows counts next to each category (e.g., "TV Features (301)")
4. When user selects a tag, filters the `prompts` array to show only matching prompts

#### Why Pre-Calculated Counts Matter

Without pre-calculated counts, the frontend would need to:
1. Loop through all 382 prompts
2. Check each prompt's tags
3. Count matches for the current filter
4. Repeat this for every filter change

With pre-calculated counts, it just reads the number from the JSON - instant display, no computation.

#### Plain English
It is like a library catalog that already shows "Science: 450 books" vs. having to count all the science books every time someone asks. The counting is done once when we create the JSON, not repeatedly every time someone uses the filter.

---

### Session Summary

| Task | Status |
|------|--------|
| Create CSV parsing script | Complete |
| Build hierarchical tag tree | Complete |
| Calculate prompt counts per tag | Complete |
| Output structured JSON | Complete |
| Document regeneration command | Complete |

### Files Created

- `clients/samsung/scripts/parse_prompts_csv.py` - Python script to parse CSV and build JSON
- `clients/samsung/assets/tv_prompts.json` - Output JSON with nested tag tree + prompts array

### Input/Output Files

| File | Type | Description |
|------|------|-------------|
| `clients/samsung/assets/tv_prompts_semrush_import_v2.csv` | Input | Semrush export with 382 prompts |
| `clients/samsung/assets/tv_prompts.json` | Output | Structured JSON for dashboard |

### Lessons Learned

1. **Delimiter conventions matter:** Using `__` for hierarchy is common in flat-file exports but needs explicit documentation so everyone knows the convention
2. **Pre-calculate for performance:** Counts embedded in the tree avoid expensive client-side loops
3. **One prompt, many tags:** Real-world categorization is not hierarchical - items belong to multiple branches simultaneously

---

## 2026-01-20: Modular Prompt System for Samsung Dashboards

### Session Goals
Refactor the monolithic dashboard prompt file into a modular system with reusable components, design tokens, and individual element files.

---

### Part 1: Why Modularize?

#### The Problem
The original `ai-overview-dashboard.md` was a single large file containing all dashboard specifications. This created issues:
- Generating a single component (like just the header) required providing the entire file
- Changes to design tokens had to be made in multiple places
- No clear separation between "what" (elements) and "how" (styling rules)

#### The Solution
Split the monolithic file into a modular structure:

```
clients/samsung/prompts/
├── _base/
│   ├── design-tokens.md      # Colors, spacing, typography variables
│   ├── fonts.md              # @font-face declarations
│   └── components.md         # Reusable UI patterns
├── elements/
│   ├── header.md             # Dashboard header (approved)
│   ├── kpi-cards.md          # KPI card row
│   ├── line-chart.md         # Historical trend chart
│   ├── donut-chart.md        # Sentiment donut
│   ├── stacked-bar.md        # Sentiment over time
│   ├── leaderboard-table.md  # Brand leaderboard
│   └── data-table.md         # Product performance table
├── _archive/
│   ├── ai-overview-dashboard.md  # Old monolithic file
│   └── dashboard-header.md       # Old header file
└── full-dashboard.md         # Assembly instructions
```

#### Plain English
Imagine having a recipe book where every recipe also includes how to grow the ingredients, how to build the oven, and the complete history of cooking. Finding anything would be a nightmare. We split this into:
- A pantry list (design tokens)
- Individual recipe cards (elements)
- Assembly instructions for the full meal (full-dashboard.md)

Now you can grab just the recipe card for "KPI cards" without carrying the whole book.

---

### Part 2: The Base Layer

#### design-tokens.md
Contains all CSS variables that define the visual language:
- **Colors:** Samsung blue (#1428a0), backgrounds, text colors
- **Spacing:** Consistent padding and gaps (0.5rem, 1rem, 1.5rem, etc.)
- **Typography:** Font sizes, weights, line heights
- **Effects:** Shadows, border-radius values

#### fonts.md
Contains the @font-face declarations for:
- Samsung Sharp Sans (headings)
- Samsung One (body text)

This ensures fonts are loaded consistently across all generated components.

#### components.md
Contains reusable UI patterns like:
- Card containers with shadows
- Section headers
- Responsive grid patterns

#### Plain English
Think of `_base/` as the foundation of a house - it defines all the rules before you start building rooms. Every element file can reference these tokens to stay consistent. If Samsung changes their brand blue color, we update ONE file and everything inherits the change.

---

### Part 3: Element Files

Each element file is self-contained and includes:
1. **Purpose:** What this component does
2. **Structure:** HTML skeleton
3. **Styling:** CSS specific to this element
4. **Data requirements:** What data it expects
5. **Approved implementation:** Working code from v3-ai-overview.html (where available)

#### Elements Created
| File | Purpose |
|------|---------|
| `header.md` | Dashboard title bar with logo |
| `kpi-cards.md` | Row of 4 metric cards |
| `line-chart.md` | Historical trend visualization |
| `donut-chart.md` | Sentiment distribution pie |
| `stacked-bar.md` | Sentiment over time bars |
| `leaderboard-table.md` | Brand ranking table |
| `data-table.md` | Product performance grid |

#### Plain English
Each element file is like a LEGO instruction sheet for one specific piece. You can build just that piece without needing the instructions for the entire set. Want to generate only the KPI cards? Just provide `design-tokens.md` + `kpi-cards.md` - no need for the chart or table specs.

---

### Part 4: The Archive

Moved old files to `_archive/` to preserve history:
- `ai-overview-dashboard.md` - The original monolithic file
- `dashboard-header.md` - An earlier header-only attempt

#### Plain English
We kept the old files in an "archive" folder rather than deleting them. This way, if something in the new system is missing, we can always check what the original said.

---

### Part 5: Full Dashboard Assembly

Created `full-dashboard.md` that explains how to combine all elements:
1. Start with design tokens and fonts
2. Add the header
3. Build the KPI row
4. Add charts in the appropriate layout
5. Include tables at the bottom

This file is the "master recipe" that references all other files.

#### Plain English
This is like the table of contents for the LEGO set - it tells you the order to build things and how they fit together, but the actual building instructions are in the individual element files.

---

### Session Summary

| Task | Status |
|------|--------|
| Create `_base/` folder with foundation files | Complete |
| Create `elements/` folder with 7 component files | Complete |
| Archive old monolithic files | Complete |
| Create full-dashboard.md assembly guide | Complete |

### Files Created

**Base layer:**
- `clients/samsung/prompts/_base/design-tokens.md`
- `clients/samsung/prompts/_base/fonts.md`
- `clients/samsung/prompts/_base/components.md`

**Elements:**
- `clients/samsung/prompts/elements/header.md`
- `clients/samsung/prompts/elements/kpi-cards.md`
- `clients/samsung/prompts/elements/line-chart.md`
- `clients/samsung/prompts/elements/donut-chart.md`
- `clients/samsung/prompts/elements/stacked-bar.md`
- `clients/samsung/prompts/elements/leaderboard-table.md`
- `clients/samsung/prompts/elements/data-table.md`

**Assembly:**
- `clients/samsung/prompts/full-dashboard.md`

**Archive:**
- `clients/samsung/prompts/_archive/ai-overview-dashboard.md`
- `clients/samsung/prompts/_archive/dashboard-header.md`

### Decision Made

| Decision | Why | Alternative Rejected |
|----------|-----|---------------------|
| Modular prompt system with separate element files | Enables generating individual components without full context, easier maintenance, single source of truth for design tokens | Single monolithic prompt file (requires full context for any change, duplicated styling rules) |

### Lessons Learned

1. **Modularity enables flexibility:** When prompts are split into composable pieces, you can request exactly what you need without overwhelming the context
2. **Design tokens prevent drift:** Centralizing colors, spacing, and typography means changes propagate automatically
3. **Archive, don't delete:** Keeping old files provides a safety net and historical reference
4. **Include approved implementations:** Element files that contain working code (not just specs) are more reliable for generation

---

## 2026-01-20: Samsung AI Visibility Dashboard & GitHub Push

### Session Goals
Create a branded dashboard for Samsung's AI Visibility project, fix visual alignment issues, secure API credentials, and push the project to GitHub.

---

### Part 1: Samsung AI Visibility Dashboard

#### What We Did
Built a styled HTML dashboard at `clients/samsung/dashboards/v3-ai-overview.html` with Samsung branding:

**Visual Design:**
- Samsung Sharp Sans font for headings
- Samsung One font for body text
- Samsung blue (#1428a0) for accent colors
- Light gray (#f7f7f7) header background
- Rounded corners and subtle shadows on cards

**Layout Structure:**
- Header: Full width with max-width content container
- Dashboard title "AI Visibility Dashboard" (28px, bold, Samsung blue) on left
- Samsung logo on right
- Main content area with same max-width as header for alignment
- KPI cards in a 4-column CSS grid

#### Technical Details - Header Alignment Fix

**The Problem:**
The header logo and title were not aligned with the main content below. The logo's left edge did not line up with the "Overview" section title.

**Technical Explanation:**
The header had different padding than the main content area. Even though both used max-width, the internal padding created a visual misalignment. The fix required:
1. Adding a `.header-content` wrapper inside the header
2. Giving it the same `max-width` and `padding` as the `.dashboard-container`
3. Using flexbox with `justify-content: space-between` for left/right positioning

**Plain English:**
Imagine two rows of books on a shelf - even if the shelves are the same length, if one row starts further from the edge, they look misaligned. We made sure both the header and main content start at exactly the same spot by giving them identical "margins from the edge."

#### Technical Details - CSS Grid for KPI Cards

**The Problem:**
KPI cards had different widths depending on their content.

**Why Flexbox Failed:**
With `display: flex`, cards naturally size based on their content. A card with "52.3%" takes different space than one with "1,847 keywords."

**The Solution:**
```css
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1.5rem;
}
```

**Plain English:**
Flexbox is like asking four people to stand in a line and each take "as much space as they need" - they end up uneven. CSS Grid is like drawing four equal boxes on the ground and saying "everyone stand in your box" - guaranteed equal spacing.

---

### Part 2: Updated Prompt Documentation

#### What We Did
Updated `clients/samsung/prompts/ai-overview-dashboard.md` to serve as a specification for generating consistent dashboards.

**Changes Made:**
- Renamed from "AI Overview Dashboard" to "AI Visibility Dashboard"
- Added Page Header section with explicit alignment requirements
- Changed font paths from absolute to relative (`../assets/fonts/`)
- Changed KPI card specification from flexbox to CSS grid

#### Plain English
This prompt file is like a recipe card. When we want to create another dashboard like this one (or modify this one), we can give this document to Claude and say "follow these instructions." Having the exact specifications written down means we get consistent results every time.

---

### Part 3: Security Fix - API Key Handling

#### What We Did
Fixed `clients/samsung/groq_kimi.py` to require the API key from environment variables instead of having it hardcoded.

**Before (insecure):**
```python
api_key = "gsk_xxxxx..."  # Hardcoded in source code
```

**After (secure):**
```python
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("GROQ_API_KEY not found in environment. Add it to .env file.")
```

#### Plain English
Imagine writing your house key's location on a sticky note and leaving it on your front door. That is what hardcoding an API key does - anyone who sees the code can use your account. By requiring the key to be in a separate `.env` file (which is never shared), the "house key" stays hidden even if someone sees the code.

#### Why This Matters
- The `.env` file is listed in `.gitignore`, so it never gets uploaded to GitHub
- Even if the code is public, the API credentials remain private
- Each developer can use their own API key without changing the code

---

### Part 4: GitHub Repository Push

#### What We Did
Pushed the initial commit to a new GitHub repository:
- **URL:** https://github.com/Qualmage/ai_visibility
- **Files:** 68 files committed
- **Security:** `.env` file properly gitignored

#### Plain English
We uploaded the project to GitHub, which is like putting it in a shared cloud folder that tracks every change. Importantly, the file containing our secret passwords (`.env`) was NOT uploaded - it stays only on our computer.

---

### Lesson Learned: Describing Visual Issues to AI

#### The Problem
When trying to fix the header alignment, annotated screenshots (with arrows drawn on them) were not effective at communicating the issue to Claude.

#### What Works Better
Explicit text descriptions that state exactly what should align with what:

**Less Effective:**
"See the screenshot - the logo needs to move"

**More Effective:**
"The logo's left edge should align with the Overview section title below. Both should have the same left margin from the edge of the viewport."

#### Plain English
AI understands written descriptions better than visual annotations. Instead of drawing an arrow on a picture, describe in words exactly what you see and what you want. Be specific about which elements should line up with which other elements.

---

### Session Summary

| Task | Status |
|------|--------|
| Apply Samsung branding to dashboard | Complete |
| Fix header/content alignment | Complete |
| Change KPI cards to CSS grid | Complete |
| Update prompt documentation | Complete |
| Remove hardcoded API key | Complete |
| Push to GitHub | Complete |

### Files Created

- `clients/samsung/dashboards/v3-ai-overview.html` - Styled AI Visibility Dashboard

### Files Modified

- `clients/samsung/prompts/ai-overview-dashboard.md` - Updated specifications
- `clients/samsung/groq_kimi.py` - Secured API key handling

### Decisions Made

| Decision | Why | Alternative Rejected |
|----------|-----|---------------------|
| CSS Grid for KPI cards | Guarantees equal-width cards regardless of content | Flexbox (width varies with content) |
| Relative asset paths (`../assets/`) | Enables static file usage without web server | Absolute paths (requires specific deployment) |
| Text descriptions for visual issues | Works better than annotated screenshots with AI | Screenshots with drawn annotations |

### Lessons Learned

1. **CSS Grid vs Flexbox for equal columns:** When you need guaranteed equal widths, use CSS Grid with `repeat(n, 1fr)`. Flexbox widths depend on content.
2. **Alignment requires matching containers:** For header elements to align with body content, they need the same max-width AND the same padding.
3. **Describing visual issues to AI:** Use explicit text ("element A should align with element B") rather than annotated screenshots. AI processes text descriptions more reliably than visual markup.
4. **API key security:** Never hardcode API keys. Use environment variables loaded from `.env` files that are gitignored.

---

## 2026-01-19: Direct Groq API Script for Kimi K2

### Session Goals
Use Groq's hosted Kimi K2 model for AI queries. Originally attempted via claude-code-router, but ultimately bypassed it due to a persistent bug.

---

### Part 1: The claude-code-router Attempt

#### What We Did
Tried to configure claude-code-router to route requests to Groq's Kimi K2 model. Created config at `C:\Users\rober\.claude-code-router\config.json` with multiple provider configurations:
- Groq (primary target)
- OpenRouter (backup)
- Ollama (local fallback)

#### The Problem
Every attempt to use Groq through the router failed with this error:
```
Error code: 400 - {'error': {'message': 'enable_thinking is not supported', ...}}
```

#### Technical Explanation
claude-code-router v2.0.x has a bug (GitHub issue #1046) where it force-injects an `enable_thinking` parameter into API requests. This parameter is for Claude's extended thinking feature, but:
1. Groq's API does not recognize this parameter
2. Groq rejects the entire request as malformed
3. The router has no way to strip this parameter before sending

We tried multiple "transformers" (filters that modify requests):
- `groq` transformer - did not help
- `cleancache` transformer - did not help
- `reasoning` transformer - did not help
- Combined transformers - still failed

#### Plain English
Think of it like a postal service that automatically stamps "FRAGILE" on every package you send, even when the recipient does not accept packages marked "FRAGILE" and returns them. The router was adding a special instruction to every request that Groq did not understand, so Groq refused to process them.

#### Why We Did Not Downgrade
Router v1.x might work (it does not have this bug), but the user preferred a direct solution rather than using an older version of third-party software with unknown other issues.

---

### Part 2: Direct Groq API Script

#### What We Did
Created a Python script that calls the Groq API directly, bypassing claude-code-router entirely.

#### Technical Details

**File:** `clients/samsung/groq_kimi.py`

**Model:** `moonshotai/kimi-k2-instruct-0905` (Kimi K2 hosted on Groq)

**API Endpoint:** `https://api.groq.com/openai/v1/chat/completions`

**Features:**
- Single query mode (ask one question, get answer)
- Report generation mode (structured output with context)
- Interactive chat mode (conversation loop)

**Dependencies:**
- `httpx` - Modern async HTTP client for Python
- `python-dotenv` - Already in project for loading `.env` files

#### Plain English
Instead of using the middleman (router) that was breaking our requests, we created our own direct phone line to Groq. The script formats our questions exactly how Groq expects them, sends them directly, and gives us back the answers.

---

### Part 3: Configuration

#### What We Did
Added the Groq API key to the existing Samsung client `.env` file:

**File:** `clients/samsung/.env`
```
SEMRUSH_API_KEY=...existing key...
GROQ_API_KEY=gsk_...your key here...
```

#### Plain English
We added the Groq "password" (API key) to the same secure file where we keep the Semrush password. This file is not shared in git, so the keys stay private.

---

### Part 4: Usage Examples

#### Command Line Usage

```bash
# Simple query - ask a question, get an answer
uv run python clients/samsung/groq_kimi.py "What are the top 3 SEO trends for 2026?"

# Report generation - create structured analysis
uv run python clients/samsung/groq_kimi.py --report "Samsung TV market analysis"

# Interactive chat - back-and-forth conversation
uv run python clients/samsung/groq_kimi.py --chat
```

#### Python Import Usage

```python
from clients.samsung.groq_kimi import query_kimi, generate_report

# Quick query
response = query_kimi("Analyze this competitor data...")
print(response)

# Generate a report with context
report = generate_report(
    topic="Q4 Performance Summary",
    context="Revenue: $10M, Growth: 15%, Top product: OLED TVs"
)
print(report)
```

#### Plain English
You can use this script three ways:
1. **Quick question:** Type your question after the script name, get an answer
2. **Report mode:** Ask it to write a structured report on a topic
3. **Chat mode:** Have an ongoing conversation where it remembers what you said before

---

### Session Summary

| Task | Status |
|------|--------|
| Configure claude-code-router for Groq | Failed (bug #1046) |
| Try multiple transformer combinations | Failed |
| Create direct Groq API script | Complete |
| Add GROQ_API_KEY to .env | Complete |
| Document usage examples | Complete |

### Files Created

- `clients/samsung/groq_kimi.py` - Direct Groq API script for Kimi K2

### Files Modified

- `clients/samsung/.env` - Added GROQ_API_KEY
- `pyproject.toml` - Added httpx dependency

### Decision Made

| Decision | Why | Alternative Rejected |
|----------|-----|---------------------|
| Use direct Groq API instead of claude-code-router | Router v2.0.x has unfixed bug (#1046) that sends unsupported `enable_thinking` parameter to Groq | Downgrade to router v1.x (user preferred direct API for reliability) |

### Lessons Learned

1. **Third-party routers can have breaking bugs:** When a proxy/router tool adds parameters your target does not support, you may need to bypass it entirely
2. **Direct API calls are more reliable:** Fewer moving parts means fewer things that can break
3. **Check GitHub issues early:** The router bug was documented in issue #1046 - checking issues first could have saved troubleshooting time
4. **Groq API follows OpenAI format:** The endpoint structure (`/openai/v1/chat/completions`) makes it easy to adapt existing OpenAI code

---

## 2026-01-14: Samsung Client Setup & Semrush API Integration

### Session Goals
Add Samsung as a new client, set up Semrush API integration for SEO traffic data, and resolve any environment issues.

---

### Part 1: Samsung Client Folder Setup

#### What We Did
Created the Samsung client folder using the template structure:
```
clients/samsung/
├── README.md
├── .env              # Semrush API key (gitignored)
├── test_semrush_api.py
├── gtm/.gitkeep
├── ga/.gitkeep
├── looker/.gitkeep
└── docs/.gitkeep
```

#### Plain English
We added Samsung as a new client to the project. Just like having a separate filing drawer for each customer, Samsung now has its own organized folder with places for GTM configs, GA reports, Looker dashboards, and documentation.

---

### Part 2: Semrush API Test Script

#### What We Did
Created a test script to query the Semrush API for Samsung HE (Home Entertainment) US organic traffic data.

#### Technical Details
- Used the Semrush `domain_organic` API endpoint
- Queried `samsung.com/us` domain for US database
- Used `python-dotenv` to load API key from `.env` file
- Successfully retrieved daily traffic data (~10,000-11,700 visits)

#### Plain English
Semrush is a tool that estimates how much search traffic a website gets. We created a script that asks Semrush "how many people find Samsung's US website through Google searches?" The script worked - Samsung's home entertainment section gets about 10,000-12,000 daily visitors from organic search.

#### Files Created
- `clients/samsung/test_semrush_api.py` - The API test script
- `clients/samsung/.env` - Contains the Semrush API key (kept secret, not in git)

---

### Part 3: Added Project Dependencies

#### What We Did
Added two new packages to `pyproject.toml`:
- `requests>=2.32.0` - For making HTTP API calls
- `python-dotenv>=1.0.0` - For loading environment variables from `.env` files

#### Plain English
These are like tools we added to our toolbox:
- **requests** - Lets Python talk to websites and APIs (like Semrush)
- **python-dotenv** - Lets us keep secret passwords in a separate file that we do not share

---

### Problem: uv Not Found in PATH

#### What Happened
When trying to run `uv sync` to install the new dependencies, the terminal said "uv: command not found" even though uv was installed.

#### Technical Explanation
The `uv.exe` executable was installed at `C:\Users\rober\.local\bin\uv.exe`, but this directory was not in the system PATH. The PATH is an environment variable that tells Windows where to look for programs when you type their name.

#### Plain English
It is like having a tool in your garage, but when you ask someone to grab it, they only look in the kitchen. The tool exists, but nobody knows where to find it because we did not tell Windows to look in that garage.

#### Solution
Added the directory to the user's PATH permanently using PowerShell:
```powershell
$currentPath = [Environment]::GetEnvironmentVariable("Path", "User")
[Environment]::SetEnvironmentVariable("Path", "$currentPath;$env:USERPROFILE\.local\bin", "User")
```

#### Plain English Solution
We updated the "places to look for tools" list so Windows now knows to check the `.local\bin` garage whenever we ask for a program.

#### Lesson Learned
When installing tools via `pip install --user` or similar methods, they often end up in `~/.local/bin` which may not be in PATH by default on Windows.

---

### Problem: Shell Escaping with PowerShell Variables

#### What Happened
When running PowerShell commands from bash/Claude, the `$env:USERPROFILE` variable was not being expanded correctly - the `$` was getting stripped.

#### Technical Explanation
Different quoting rules apply when invoking PowerShell from another shell:
- **No quotes or double quotes:** The `$` is interpreted by the outer shell (bash) and stripped
- **Single quotes:** The entire command is passed literally to PowerShell, preserving `$env:` variables

#### Plain English
When you tell PowerShell to do something through an intermediary (like bash), the intermediary might misread your instructions. Using single quotes is like putting the instructions in a sealed envelope - they get delivered exactly as written without anyone changing them along the way.

#### Solution
Use single quotes when calling PowerShell from bash:
```bash
# Wrong - $ gets stripped
powershell "echo $env:USERPROFILE"

# Right - $ preserved
powershell 'echo $env:USERPROFILE'
```

#### Lesson Learned
When automating PowerShell commands from Claude or other shells, always use single quotes around commands containing PowerShell variables like `$env:`.

---

### Part 4: Successful API Test

#### What We Did
Ran the Semrush API test script and confirmed it works:
- HTTP Status: 200 (success)
- Data returned: Samsung HE US organic traffic metrics
- Daily traffic range: ~10,000-11,700 visits

#### Plain English
We tested our connection to Semrush and it worked. We can now pull SEO data for Samsung whenever we need it.

---

### Part 5: Semrush Enterprise API Endpoint Capture

#### What We Did
Used Chrome DevTools MCP to intercept API calls made by the Semrush dashboard. Captured 7 endpoints from the enterprise API (v4-raw) that powers their "Insights" feature.

#### Technical Details
The Semrush Enterprise API uses a different structure than their public API:
- **Base URL:** `https://api.semrush.com/apis/v4-raw/external-api/v1`
- **Authentication:** Bearer token + Workspace ID header
- **Products:** Two distinct products - `ai` (AI Overview tracking) and `seo` (traditional SEO)
- **Workspace ID:** `a22caad0-2a96-4174-9e2f-59f1542f156b` (Samsung account)

#### Captured Endpoints

| Endpoint | Purpose |
|----------|---------|
| `POST /elements` | Main data query - returns keywords, trends, rankings |
| `POST /elements/count` | Get count of matching elements |
| `POST /overview` | Dashboard summary statistics |
| `POST /tags` | Tag management for organizing data |
| `POST /export` | Export data in various formats |
| `POST /config` | User configuration and preferences |
| `POST /columns` | Available columns for data queries |

#### Request Structure
All POST requests use JSON body with this pattern:
```json
{
  "product": "ai" or "seo",
  "projectId": "6919587",
  "filters": { ... },
  "pagination": { "offset": 0, "limit": 100 },
  "sorting": { ... }
}
```

#### Plain English
Semrush has two APIs - a public one for basic queries (which we tested earlier) and an enterprise one that powers their fancy dashboard. The enterprise API is like the "staff entrance" at a hotel - it gives access to more features but requires special credentials. We used Chrome DevTools to watch what requests the Semrush website makes when you click around, then wrote down all those requests so we can make them ourselves later.

#### Why This Matters
The public Semrush API has limited features. The enterprise API (v4-raw) provides:
- AI Overview tracking (which keywords trigger AI responses in Google)
- More detailed historical data
- Export capabilities
- Tag/organization features

By documenting these endpoints, we can build scripts that pull the same data the Semrush dashboard shows, but automated.

#### Files Created
- `clients/samsung/semrush-api-endpoints.md` - Complete API documentation with all 7 endpoints

---

### Session Summary

| Task | Status |
|------|--------|
| Create Samsung client folder | Complete |
| Create Semrush API test script | Complete |
| Add requests and python-dotenv dependencies | Complete |
| Fix uv PATH issue | Complete |
| Test Semrush API connection | Complete |
| Capture Semrush Enterprise API endpoints | Complete |
| Document API structure | Complete |

### Files Created

- `clients/samsung/README.md` - Client documentation
- `clients/samsung/.env` - Semrush API key (gitignored)
- `clients/samsung/test_semrush_api.py` - API test script
- `clients/samsung/semrush-api-endpoints.md` - Enterprise API documentation (7 endpoints)
- `clients/samsung/gtm/.gitkeep` - Placeholder for GTM folder
- `clients/samsung/ga/.gitkeep` - Placeholder for GA folder
- `clients/samsung/looker/.gitkeep` - Placeholder for Looker folder
- `clients/samsung/docs/.gitkeep` - Placeholder for docs folder

### Files Modified

- `pyproject.toml` - Added requests and python-dotenv dependencies

### Lessons Learned

1. **PATH awareness:** When tools are installed but not found, check if their directory is in PATH
2. **Shell escaping matters:** Use single quotes when passing PowerShell commands through other shells to preserve `$` variables
3. **Environment files:** Using `.env` files with `python-dotenv` is a clean way to manage API keys without hardcoding them
4. **Browser interception for API discovery:** Chrome DevTools MCP can capture authenticated API calls that would be difficult to discover otherwise - useful for undocumented enterprise APIs

---

## 2026-01-14: Virtual Environment Prompt Fix

### Session Goals
Clean up development environment by fixing incorrectly named virtual environment prompt.

---

### Problem: Wrong Project Name in Terminal Prompt

#### What Happened
When activating the project's virtual environment, the terminal showed `(hisense)` instead of `(general-analytics)`. This was confusing because "hisense" is a completely different project.

#### Technical Explanation
When you create a Python virtual environment, it stores configuration in two places:
1. `pyvenv.cfg` - A config file at the root of the venv with a `prompt` setting
2. `Scripts/Activate.ps1` (Windows) or `bin/activate` (Mac/Linux) - The script that activates the venv, which may have the name hardcoded

This virtual environment was originally created for a "hisense" project and later copied or reused. The prompt name was never updated.

#### Plain English
When you open a terminal and activate a Python project, it shows the project name in parentheses like `(project-name)` so you know which project you're working in. Ours was showing the wrong name - like having someone else's name tag on your desk.

#### Solution
Updated two files to fix the prompt:

1. **`.venv/pyvenv.cfg`**
   ```
   # Before
   prompt = hisense

   # After
   prompt = general-analytics
   ```

2. **`.venv/Scripts/Activate.ps1`** (lines 61-62)
   ```powershell
   # Before
   $_OLD_VIRTUAL_PROMPT = $function:prompt
   $env:VIRTUAL_ENV_PROMPT = "hisense"

   # After
   $_OLD_VIRTUAL_PROMPT = $function:prompt
   $env:VIRTUAL_ENV_PROMPT = "general-analytics"
   ```

#### Files Modified
- `.venv/pyvenv.cfg`
- `.venv/Scripts/Activate.ps1`

---

### Bonus Tip: Clean Up Terminal from Conda Auto-Activate

#### The Issue
If you have Miniconda or Anaconda installed, it often auto-activates the "base" environment every time you open a terminal, showing `(base)` in your prompt. This can be confusing when working with uv-managed projects.

#### Solution
Disable conda auto-activate:
```powershell
conda config --set auto_activate_base false
```

#### Plain English
This tells conda to stop automatically putting you in its "base camp" every time you open a terminal. You can still use conda when you need it, but it won't clutter your prompt when you're working on other projects.

---

### Session Summary

| Task | Status |
|------|--------|
| Fix venv prompt from "hisense" to "general-analytics" | Complete |
| Document conda auto-activate tip | Complete |

### Lessons Learned

1. **Check venv origins:** When reusing or copying virtual environments, always verify the prompt name matches the current project
2. **Two files to check:** On Windows, both `pyvenv.cfg` and `Activate.ps1` may contain the prompt name

---

## 2026-01-13: Initial Setup & GA User Management

### Session Goals
Set up the GA MCP server, create a multi-client folder structure, and add users to Changan Auto GA properties.

---

### Part 1: GA MCP Server Setup

#### What We Did
- Installed `analytics-mcp` package using `uv tool install`
- Created isolated Python 3.13 virtual environment
- Configured `.mcp.json` with the MCP server settings
- Applied Windows-specific workarounds for credentials path

#### Plain English
We set up a background program (MCP server) that lets Claude connect to Google Analytics. This means Claude can now query GA data, run reports, and check real-time analytics directly without you having to copy/paste from the GA interface.

---

### Part 2: The Great MCP Debugging Adventure

#### Problem 1: MCP Tool Calls Hanging Indefinitely

**What happened:**
The MCP server showed "connected" in Claude Code, but any actual tool call would hang forever with no response or error message.

**Technical explanation:**
The analytics-mcp package uses async Python with grpc (Google's remote procedure call library). When installed via pipx, it created a virtual environment based on miniconda Python. Miniconda's asyncio implementation was conflicting with grpc's async code, causing a deadlock.

**Plain English:**
Think of it like having two traffic controllers at an intersection, each waiting for the other to give the go-ahead. Neither one moves, so traffic stops completely. The MCP server was waiting for Google's response system, which was waiting for the MCP server.

**How we diagnosed it:**
1. Tested the GA API directly with synchronous code - worked fine
2. Tested with async code - got error: "Task got Future attached to a different loop"
3. Traced the error to miniconda's Python installation

**Solution:**
Created a completely isolated Python environment using standalone Python 3.13 (not miniconda):
```
C:\Users\rober\analytics-mcp-py313\
```

**Files modified:**
- `.mcp.json` - Updated to use the isolated venv's executable

---

#### Problem 2: Credentials Path Issue (GitHub Issue #73)

**What happened:**
Even with the isolated Python, MCP calls still hung. No error, just silence.

**Technical explanation:**
There's a known bug on Windows where the analytics-mcp package can't read credentials from the default gcloud path (`%APPDATA%\gcloud\application_default_credentials.json`). Something about how Windows handles path resolution in the subprocess.

**Plain English:**
It's like giving someone directions to your house, but they can't find the street because their GPS doesn't recognize the neighborhood name. The program knew where the credentials file was supposed to be, but couldn't actually read it from that location.

**Solution:**
Copied credentials to the user's home directory and explicitly set the path:
```json
{
  "env": {
    "GOOGLE_APPLICATION_CREDENTIALS": "C:\\Users\\rober\\application_default_credentials.json"
  }
}
```

**Lesson learned:**
When something hangs with no error on Windows, check if it's a path/permissions issue. The analytics-mcp GitHub issues page had this exact problem documented.

---

### Part 3: Multi-Client Folder Structure

#### What We Did
Created an organized folder structure for managing multiple clients:
```
clients/
├── _template/           # Copy this for new clients
└── changan-auto/        # First client
    ├── gtm/             # GTM configs, exports
    ├── ga/              # GA reports, queries
    ├── looker/          # Looker Studio assets
    └── docs/            # Client documentation
```

#### Plain English
We organized the project like a filing cabinet with separate drawers for each client. Each drawer has the same folder structure inside, so it's easy to find things and add new clients by copying the template.

---

### Part 4: GA User Management Scripts

#### What We Did
Created scripts to add users to Google Analytics properties without using the GA web interface.

#### Problem: GA MCP is Read-Only

**What happened:**
Tried to use the GA MCP server to add users, but it only has `analytics.readonly` scope.

**Technical explanation:**
OAuth scopes define what an application can do. The MCP server authenticates with read-only permissions to minimize security risk. Adding users requires the `analytics.manage.users` scope.

**Plain English:**
The MCP server has a "visitor pass" that only lets it look at data, not change anything. To add users, we need an "admin badge" with higher permissions.

**Solution:**
Created separate scripts that authenticate with admin permissions:
- `scripts/ga_auth_admin.ps1` - Gets the admin badge (stores separate credentials)
- `scripts/ga_add_user.py` - Uses the admin badge to add/list users

---

#### Problem: ImportError for AccessBinding

**What happened:**
```
ImportError: cannot import name 'AccessBinding' from 'google.analytics.admin_v1beta'
```

**Technical explanation:**
The Google Analytics Admin API has two versions: `v1beta` (stable but limited) and `v1alpha` (newer features, may change). The `AccessBinding` class for user management is only in `v1alpha`.

**Plain English:**
We were looking for a tool in the "stable tools" drawer, but it's actually in the "new tools" drawer. Google hasn't moved it to stable yet.

**Solution:**
Changed the import from `admin_v1beta` to `admin_v1alpha`:
```python
from google.analytics.admin_v1alpha import (
    AnalyticsAdminServiceClient,
    AccessBinding,
    CreateAccessBindingRequest,
)
```

---

### Part 5: Doc-Keeper Agent Setup

#### What We Did
Created a custom Claude Code subagent specifically for maintaining documentation. The agent lives at `.claude/agents/doc-keeper.md` and can be invoked to update both DEVELOPMENT.md and build-log.md.

#### Plain English
We created a "documentation assistant" that Claude can become when needed. Instead of manually updating documentation files, you can ask Claude to switch into "doc-keeper mode" and it will know exactly how to update both the high-level summary (DEVELOPMENT.md) and the detailed journal (build-log.md) in sync.

#### Why This Matters
Good documentation gets outdated fast. By creating a dedicated agent with clear instructions, we ensure:
- Both documentation files stay in sync
- Technical explanations always include plain-English versions
- Nothing gets lost between sessions

---

### Part 6: Adding Users to Changan Auto Properties

#### What We Did
Added two users to all 4 Changan Auto GA properties as VIEWER:
- Kristin.Harder@changanauto.eu - Success on all 4 properties
- Elena.Rosskopf@changaneurope.com - Success on all 4 properties

Attempted to add two more users:
- Chris.Hills@changanuk.com - Failed: "User not allowed"
- Steve.Kelly@changanuk.com - Failed: "User not allowed"

#### Why Some Users Failed

**Technical explanation:**
The "User not allowed" error means the email address doesn't have a Google account. GA can only add users who have Google accounts (either personal Gmail or Google Workspace accounts).

**Plain English:**
Google Analytics can only give access to people who have a Google ID. The changanuk.com domain probably isn't set up with Google Workspace, so those email addresses don't exist in Google's system.

**Solution:**
Those users would need to either:
1. Have their IT department set up Google Workspace for changanuk.com
2. Use personal Gmail addresses instead

---

### Session Summary

| Task | Status |
|------|--------|
| GA MCP server setup | Complete |
| Multi-client folder structure | Complete |
| GA user management scripts | Complete |
| Doc-keeper agent setup | Complete |
| Add Kristin to all properties | Complete |
| Add Elena to all properties | Complete |
| Add Chris/Steve | Failed (no Google accounts) |

### Files Created/Modified

**Created:**
- `clients/` folder structure
- `clients/changan-auto/` with subfolders
- `scripts/ga_add_user.py`
- `scripts/ga_auth_admin.ps1`
- `scripts/README.md`
- `docs/GA-MCP-SETUP.md`
- `docs/build-log.md` (this file)
- `DEVELOPMENT.md`
- `.claude/agents/doc-keeper.md`

**Modified:**
- `.mcp.json` - Added analytics-mcp configuration
- `pyproject.toml` - Updated project name
- `CLAUDE.md` - Added re-authentication instructions

---

## 2026-01-13: Changan Europe Server Error Investigation

### Session Goals
Investigate 500 server errors reported by Googlebot crawling the Changan Europe website. Determine if the issue is with the CDN, origin server, or image processing.

---

### Part 1: Initial Investigation with Chrome DevTools MCP

#### What We Did
- Used Chrome DevTools MCP to launch a browser and navigate to Changan Europe website
- Monitored network requests to identify failing resources
- Tested various pages and image URLs to find patterns

#### Plain English
We used a special tool that lets Claude control a real Chrome browser. This is like having Claude sit at your computer and browse the website while taking notes on everything that happens behind the scenes - which files load, which ones fail, how long things take.

---

### Part 2: Google Search Console Data Analysis

#### What We Did
- Extracted crawl statistics from a GSC export zip file
- Analyzed response code distribution over time
- Identified spike in 500 errors starting around December 5, 2025

#### What The Data Showed
The GSC crawl stats revealed:
- Normal crawling behavior with mostly 200 (success) responses
- Sudden increase in 500 (server error) responses starting Dec 5
- Errors specifically on image URLs

#### Plain English
Google Search Console keeps a diary of every time Googlebot visits your website. We looked at that diary and noticed that starting in early December, Googlebot started running into "Server Error" messages - like showing up at a store and finding a "Closed" sign instead of getting what you came for.

---

### Part 3: Root Cause Identification

#### The Problem
Image URLs with specific resize parameters return 500 errors:
```
/Portals/0/Images/example.jpg?w=1920&h=960  --> 500 Error
/Portals/0/Images/example.jpg?w=1920        --> 200 OK
/Portals/0/Images/example.jpg?w=1230&h=307  --> 200 OK
```

#### Technical Explanation
The Changan Europe website uses DNN (DotNetNuke) with an ImageProcessor module. This module dynamically resizes images based on URL parameters. The 1920x960 dimension combination (2:1 aspect ratio at high resolution) causes the ImageProcessor to fail with an unhandled exception.

The server returns a 500 error because:
1. The ImageProcessor tries to resize the image to 1920x960
2. Something in that specific calculation fails (likely memory allocation or aspect ratio validation)
3. The error is not gracefully handled, so the server returns a generic 500

#### Plain English
The website has a feature that automatically resizes images to whatever size you request. It is like asking a photo printing service to make your photo a certain size. Most sizes work fine, but when you ask for exactly 1920 pixels wide by 960 pixels tall, the resizing tool crashes. It is like a cash register that works fine for most prices but freezes when you try to ring up exactly $19.20.

---

### Part 4: CDN Behavior Analysis

#### What We Found
The Alibaba Cloud CDN is working correctly:
- It caches successful responses and serves them to subsequent visitors
- It does NOT cache 500 errors (correct behavior)
- This is why users rarely see the problem - they get cached images
- Googlebot sees errors because it often requests uncached URLs

#### Plain English
The CDN is like a delivery warehouse that keeps popular items in stock locally so they can be delivered faster. When the warehouse has the image, everyone gets it quickly. But when Googlebot asks for something not in stock, the warehouse has to call the factory (origin server). If the factory has a problem making that specific item, Googlebot sees the error - but regular visitors usually get the already-stocked version.

---

### Part 5: Bug Report Creation

#### What We Did
Created a comprehensive bug report for developers at:
`clients/changan-auto/reports/changan-image-processor-bug-report.md`

The report includes:
- Executive summary for quick understanding
- Reproduction steps to recreate the issue
- Technical details about the failure
- Impact assessment (SEO, user experience)
- Recommended fixes

#### Plain English
We wrote up a detailed "repair request" that explains exactly what is broken, how to see it for yourself, and suggestions for fixing it. This document can be sent to the website developers so they know exactly what to look for and fix.

---

### Session Summary

| Task | Status |
|------|--------|
| Website testing with Chrome DevTools MCP | Complete |
| GSC crawl stats analysis | Complete |
| Root cause identification | Complete |
| CDN behavior verification | Complete |
| Bug report creation | Complete |

### Key Findings

1. **Root Cause:** DNN ImageProcessor fails on 1920x960 resize requests
2. **Scope:** Only affects this specific dimension, other sizes work
3. **Impact:** Googlebot sees errors on cache misses, affecting crawl efficiency
4. **CDN:** Working correctly, not the problem
5. **Timeline:** Issue started around December 5, 2025

### Tools Used

- **Chrome DevTools MCP** - Browser automation for real network analysis
- **File analysis tools** - ZIP extraction and CSV parsing for GSC data

### Files Created

- `clients/changan-auto/reports/changan-image-processor-bug-report.md` - Developer bug report
- `clients/changan-auto/crawl-stats-extracted/Chart.csv` - GSC crawl chart data
- `clients/changan-auto/crawl-stats-extracted/Table.csv` - GSC crawl table data

### Lessons Learned

1. **CDN masking:** CDNs can hide origin server problems from regular users while search bots still see them
2. **Specific parameters matter:** A bug can affect only very specific input combinations
3. **Browser tools for debugging:** Chrome DevTools MCP provides authentic browser behavior that curl/wget cannot replicate
