# SEMrush Data Architecture

This document maps SEMrush API endpoints to Supabase tables and describes the data flow.

## Endpoint to Table Mapping

| SEMrush Element ID | Element Name | Supabase Table | Data Type | Date Range |
|-------------------|--------------|----------------|-----------|------------|
| `c0cffe83-8104-4cfb-afac-9b1db673d29e` | Prompt to URLs | `semrush_prompt_urls` | Daily | Jan 1, 2026+ |
| `6c914007-60fd-4105-911a-9fb8861be2ec` | Concept to Prompts | `semrush_concept_prompts` | Daily | Jan 1, 2026+ |
| `9dd09001-1d0e-4d28-b675-53670a2af5b0` | Cited Pages | `semrush_cited_pages` | Snapshot | Static |
| `0ed4bc52-b684-41b5-9436-3f5806266631` | Concept Mentions | `semrush_concept_mentions` | Daily | Dec 18, 2025+ |
| `28977430-d565-4529-97eb-2dfe2959b86b` | Source Visibility | *Edge Function* | Live API | Real-time |
| `3c29aa85-4f06-4f14-a376-b02333c6e3fa` | Cited URLs with Prompts | *Edge Function* | Live API | Real-time |
| `3a16b2b2-b227-4a41-9ef2-9c657e64d47e` | Topics with Citations | *Edge Function* | Live API | Real-time |

## Supabase Tables

### 1. `semrush_prompt_urls` (Daily)
**Purpose:** Links prompts to cited URLs with tags and AI model info.

| Column | Type | Description |
|--------|------|-------------|
| `date` | DATE | Data date |
| `prompt` | TEXT | AI prompt text |
| `source` | TEXT | Cited URL |
| `tags` | TEXT | Comma-separated tags |
| `model` | TEXT | AI model (google-ai-mode, search-gpt, etc.) |
| `position` | REAL | Citation position (1 = first) |
| `domain_type` | TEXT | Owned/Earned/Competitor/Other |

**Script:** `fetch_prompt_urls.py`

---

### 2. `semrush_concept_prompts` (Daily)
**Purpose:** Links concepts (features/topics) to prompts with sentiment and quotes.

| Column | Type | Description |
|--------|------|-------------|
| `date` | DATE | Data date |
| `brand_name` | TEXT | Brand (Samsung) |
| `concept` | TEXT | Feature/topic (e.g., "oled technology") |
| `product` | TEXT | Samsung product mentioned |
| `prompt` | TEXT | AI prompt text |
| `quote` | TEXT | Actual AI response quote |
| `sentiment` | TEXT | positive/neutral/negative |

**Script:** `fetch_concept_prompts.py`

---

### 3. `semrush_cited_pages` (Snapshot)
**Purpose:** All URLs cited by AI models with citation counts.

| Column | Type | Description |
|--------|------|-------------|
| `url` | TEXT | Cited URL |
| `prompts_count` | INTEGER | Number of prompts citing this URL |
| `country` | TEXT | Country (us, uk, etc.) |
| `category` | TEXT | OWNED_BY_TARGET, COMPETITOR, OTHER |
| `domain` | TEXT | Domain extracted from URL |

**Script:** `fetch_cited_pages.py` → `load_cited_pages.py`

---

### 4. `semrush_concept_mentions` (Daily)
**Purpose:** Daily concept mentions with sentiment breakdown by AI model and brand.

| Column | Type | Description |
|--------|------|-------------|
| `date` | DATE | Data date |
| `concept` | TEXT | Concept name |
| `concept_category` | TEXT | Category |
| `concept_subcategory` | TEXT | Subcategory |
| `mentions` | INTEGER | Mention count |
| `sentiment_positive` | INTEGER | Positive sentiment count |
| `sentiment_negative` | INTEGER | Negative sentiment count |
| `sentiment_neutral` | INTEGER | Neutral sentiment count |
| `model` | TEXT | AI model |
| `brand` | TEXT | Brand (Samsung) |

**Script:** `fetch_concept_mentions.py` → `load_concept_mentions.py`

---

### 5. `tv_topics` (Reference)
**Purpose:** Static reference table for topic filter dropdown.

| Column | Type | Description |
|--------|------|-------------|
| `category` | TEXT | Category (TV Features, TV Models, etc.) |
| `tag` | TEXT | Tag name |
| `prompt_count` | INTEGER | Number of prompts with this tag |

**Source:** Migrated from `assets/tv_prompts.json`

---

## Live API Endpoints (via Edge Function)

These endpoints are called in real-time via the `semrush-proxy` Supabase Edge Function:

### Source Visibility by Domain
- **Element ID:** `28977430-d565-4529-97eb-2dfe2959b86b`
- **Used by:** GEO Dashboard Citation Sources table
- **Returns:** Domain, domain_type, mentions, citations, visibility

### Cited URLs with Prompts
- **Element ID:** `3c29aa85-4f06-4f14-a376-b02333c6e3fa`
- **Returns:** Individual URLs with prompts that cite them

### Topics with Citations
- **Element ID:** `3a16b2b2-b227-4a41-9ef2-9c657e64d47e`
- **Returns:** Topic-level aggregation with citation counts

---

## Data Relationships

```
semrush_prompt_urls.prompt ──────┐
                                 │
semrush_concept_prompts.prompt ──┼──► JOIN on prompt text
                                 │
semrush_concept_mentions.concept ┘

semrush_prompt_urls.tags ────────► tv_topics.tag (contains)

semrush_prompt_urls.source ──────► semrush_cited_pages.url
```

### Example Queries

**Find all concepts mentioned for a specific prompt:**
```sql
SELECT DISTINCT cp.concept, cp.product, cp.sentiment, cp.quote
FROM semrush_concept_prompts cp
WHERE cp.prompt = 'best OLED TV for gaming'
  AND cp.date = '2026-01-29';
```

**Find all URLs cited for prompts about a concept:**
```sql
SELECT DISTINCT pu.source, pu.position, pu.domain_type
FROM semrush_prompt_urls pu
JOIN semrush_concept_prompts cp ON pu.prompt = cp.prompt AND pu.date = cp.date
WHERE cp.concept LIKE '%gaming%'
  AND pu.date = '2026-01-29';
```

**Get daily sentiment trend for a concept:**
```sql
SELECT date,
       SUM(sentiment_positive) as positive,
       SUM(sentiment_negative) as negative,
       SUM(sentiment_neutral) as neutral
FROM semrush_concept_mentions
WHERE concept_category = 'Gaming'
GROUP BY date
ORDER BY date;
```

---

## Data Freshness

| Table | Update Frequency | Script |
|-------|------------------|--------|
| `semrush_prompt_urls` | Daily | `fetch_prompt_urls.py` |
| `semrush_concept_prompts` | Daily | `fetch_concept_prompts.py` |
| `semrush_cited_pages` | Weekly/Manual | `fetch_cited_pages.py` |
| `semrush_concept_mentions` | Daily | `fetch_concept_mentions.py` |
| `tv_topics` | Static | Manual SQL |

**Note:** Data is available from ~2025-12-18. Scripts default to fetching from Jan 1, 2026 but can be modified to go back further.
