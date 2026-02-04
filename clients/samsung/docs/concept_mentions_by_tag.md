# Concept Mentions by Tag - Data Pipeline Documentation

## Overview

This document describes the data pipeline for fetching SEMrush concept mentions filtered by tag hierarchy, storing them in Supabase for analysis.

**Date Created:** 2026-02-04
**Data Date:** 2026-01-31 (single day snapshot)

---

## Database Objects

### 1. View: `vw_prompt_tag_hierarchy_lookup`

Maps all 383 unique prompts to their tag hierarchy positions.

**Purpose:** Reference table to see which prompts belong to which tag categories.

**Columns:**
| Column | Description |
|--------|-------------|
| `prompt` | The search query text |
| `parent_1` | First parent tag (full format, e.g., "TV Features") |
| `parent_1_name` | First parent name (clean) |
| `child_1` | First child tag (e.g., "TV Features__Resolution") |
| `child_1_name` | First child name (e.g., "Resolution") |
| `grandchild_1` | First grandchild tag (e.g., "TV Features__Resolution__4K") |
| `grandchild_1_name` | First grandchild name (e.g., "4K") |
| `great_grandchild_1` | First great-grandchild (Samsung sub-hierarchy) |
| `great_grandchild_1_name` | Great-grandchild name |
| `parent_2` through `parent_4` | Additional hierarchy positions (same structure) |

**Example Query:**
```sql
SELECT * FROM vw_prompt_tag_hierarchy_lookup
WHERE child_1_name = 'OLED';
```

---

### 2. Table: `semrush_concept_mentions_by_tag`

Stores concept mentions fetched from SEMrush API, filtered by junior tags.

**Schema:**
```sql
CREATE TABLE semrush_concept_mentions_by_tag (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  date DATE NOT NULL,
  tag TEXT NOT NULL,                    -- Junior tag used as filter
  concept TEXT NOT NULL,
  concept_category TEXT,
  concept_subcategory TEXT,
  mentions INTEGER DEFAULT 0,
  sentiment_positive INTEGER DEFAULT 0,
  sentiment_negative INTEGER DEFAULT 0,
  sentiment_neutral INTEGER DEFAULT 0,
  products TEXT[],
  model TEXT NOT NULL,                  -- search-gpt, google-ai-overview, google-ai-mode
  brand TEXT DEFAULT 'Samsung',
  fetched_at TIMESTAMPTZ DEFAULT now(),
  UNIQUE(date, tag, concept, concept_category, concept_subcategory, model, brand)
);
```

**Indexes:**
- `idx_concept_mentions_by_tag_tag` on `tag`
- `idx_concept_mentions_by_tag_date` on `date`
- `idx_concept_mentions_by_tag_brand` on `brand`
- `idx_concept_mentions_by_tag_model` on `model`

**Record Counts (as of 2026-02-04):**
| Parent Category | Records | Tags |
|-----------------|---------|------|
| TV Features | 7,509 | 17 |
| TV Models | 7,867 | 10 |
| TV Reviews & Brand | 12,194 | 18 |
| TV Sizes | 3,053 | 5 |
| **Total** | **30,623** | **50** |

---

## Important: No Deduplication

**The data is intentionally NOT deduplicated.**

During initial implementation, we discovered that the SEMrush API returns what appeared to be duplicate records - same concept with the same tag/brand/model combination. However, investigation revealed these are **distinct data points**:

### Why Duplicates Exist

1. **Different concept categorizations**: The same concept (e.g., "dolby vision") can appear with different `concept_category` and `concept_subcategory` values:
   - Record 1: `concept_category: "hdr formats"`, `concept_subcategory: null`
   - Record 2: `concept_category: "picture quality"`, `concept_subcategory: "brightness & hdr"`

2. **Different products**: Some duplicates have different products associated:
   - Record 1: `products: ["The Frame"]`, `mentions: 1`
   - Record 2: `products: ["The Frame", "The Frame TV", "The Frame QLED 4K TV"]`, `mentions: 12`

3. **Source prompts**: The concepts may have emerged from different prompts within the same tag category.

### Unique Constraint

The unique constraint includes `concept_category` and `concept_subcategory` to preserve these distinct data points:

```sql
UNIQUE(date, tag, concept, concept_category, concept_subcategory, model, brand)
```

This allows the same concept to appear multiple times if it has different categorizations.

---

## Scripts

### 1. `fetch_concept_mentions_by_tag.py`

Fetches concept mentions from SEMrush API filtered by tag.

**Location:** `clients/samsung/fetch_concept_mentions_by_tag.py`

**Usage:**
```bash
# Fetch specific tag group
uv run fetch_concept_mentions_by_tag.py --group tv-features
uv run fetch_concept_mentions_by_tag.py --group tv-models
uv run fetch_concept_mentions_by_tag.py --group tv-reviews
uv run fetch_concept_mentions_by_tag.py --group tv-sizes

# Fetch all groups
uv run fetch_concept_mentions_by_tag.py --all

# Resume from checkpoint
uv run fetch_concept_mentions_by_tag.py --all --resume
```

**Output:** `data/concept_mentions_by_tag.json`

**API Call Structure:**
```json
{
  "render_data": {
    "project_id": "b7880549-ea08-4d82-81d0-9633f4dcab58",
    "filters": {
      "simple": {
        "start_date": "2026-01-31",
        "end_date": "2026-01-31"
      },
      "advanced": {
        "op": "and",
        "filters": [
          {"op": "eq", "val": "Samsung", "col": "CBF_brand"},
          {"op": "or", "filters": [
            {"col": "CBF_tags", "op": "eq", "val": "TV Models__QLED"}
          ]},
          {"op": "eq", "val": "search-gpt", "col": "CBF_model"}
        ]
      }
    }
  }
}
```

### 2. `load_concept_mentions_by_tag.py`

Loads fetched JSON data into Supabase.

**Location:** `clients/samsung/load_concept_mentions_by_tag.py`

**Usage:**
```bash
uv run load_concept_mentions_by_tag.py
uv run load_concept_mentions_by_tag.py --input data/custom_file.json
```

---

## Tag Groups

### TV Features (17 tags)
- TV Features__AI
- TV Features__Anti-Glare
- TV Features__Art Mode
- TV Features__Brightness
- TV Features__Connectivity
- TV Features__HDR
- TV Features__Input Lag
- TV Features__Motion Handling
- TV Features__Panel Technology
- TV Features__Picture Settings
- TV Features__Refresh Rate
- TV Features__Resolution
- TV Features__Resolution__4K
- TV Features__Resolution__8K
- TV Features__Smart Features
- TV Features__Sound
- TV Features__Viewing Angles

### TV Models (10 tags)
- TV Models__Art TV
- TV Models__Gaming TVs
- TV Models__Micro RGB
- TV Models__Mini-LED
- TV Models__Movies & Cinema
- TV Models__OLED
- TV Models__Outdoor TV
- TV Models__QLED
- TV Models__Smart TV
- TV Models__Sports TVs

### TV Reviews & Brand (18 tags)
- TV Reviews & Brand__Affordable
- TV Reviews & Brand__Best Of
- TV Reviews & Brand__Brand
- TV Reviews & Brand__Brand TV Model Reviews
- TV Reviews & Brand__Brand__TV Features__AI
- TV Reviews & Brand__Brand__TV Features__Smart Features
- TV Reviews & Brand__Brand__TV Features__Streaming
- TV Reviews & Brand__Brand__TV Models__Crystal UHD
- TV Reviews & Brand__Brand__TV Models__Micro RGB
- TV Reviews & Brand__Brand__TV Models__MovingStyle
- TV Reviews & Brand__Brand__TV Models__Neo QLED
- TV Reviews & Brand__Brand__TV Models__Smart TV
- TV Reviews & Brand__Brand__TV Models__The Frame
- TV Reviews & Brand__Buying Guides
- TV Reviews & Brand__Comparison
- TV Reviews & Brand__Deals
- TV Reviews & Brand__Year Reviews__2025
- TV Reviews & Brand__Year Reviews__2026

### TV Sizes (5 tags)
- TV Sizes__Large Size
- TV Sizes__Medium Size
- TV Sizes__Small Size
- TV Sizes__Super Size
- TV Sizes__Viewing Distance

---

## Brands & Models

**Brands:** Samsung, LG, Sony, Hisense, TCL

**AI Models:** search-gpt, google-ai-overview, google-ai-mode

**Total API Calls:** 50 tags x 3 models x 5 brands = 750 calls

---

## Rate Limiting

The SEMrush API has a rate limit of ~600 requests/hour. The fetch script includes:
- 0.3-0.4 second delay between requests
- Checkpoint saves every 20 requests
- Resume capability with `--resume` flag

If rate limited (405 errors), wait 1 hour before retrying.

---

## Example Queries

### Top concepts by tag
```sql
SELECT tag, concept, SUM(mentions) as total_mentions
FROM semrush_concept_mentions_by_tag
WHERE brand = 'Samsung'
GROUP BY tag, concept
ORDER BY total_mentions DESC
LIMIT 20;
```

### Sentiment by brand
```sql
SELECT
  brand,
  SUM(sentiment_positive) as positive,
  SUM(sentiment_neutral) as neutral,
  SUM(sentiment_negative) as negative
FROM semrush_concept_mentions_by_tag
GROUP BY brand
ORDER BY brand;
```

### Tag coverage by model
```sql
SELECT
  model,
  COUNT(DISTINCT tag) as tags_covered,
  COUNT(*) as total_records
FROM semrush_concept_mentions_by_tag
GROUP BY model;
```
