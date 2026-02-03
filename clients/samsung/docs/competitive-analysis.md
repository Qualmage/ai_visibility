# Samsung Competitive AI Visibility Analysis

This document captures the competitive analysis methodology and findings for Samsung's AI visibility compared to LG, Sony, TCL, and Hisense.

## Data Sources

### Tables Used
| Table | Rows | Purpose |
|-------|------|---------|
| `semrush_concept_prompts` | 338,759 | Brand mentions with concepts, sentiment, quotes |
| `semrush_prompt_urls` | 249,307 | URL citations per prompt |
| `semrush_concept_mentions` | 151,787 | Aggregated brand mentions by date/model |

### Brand Data Loaded
| Brand | Rows | Unique Prompts | Date Range |
|-------|------|----------------|------------|
| Samsung | 145,337 | 377 | Jan 1-29, 2026 |
| LG | 78,232 | 314 | Jan 1-29, 2026 |
| TCL | 47,126 | 283 | Jan 1-29, 2026 |
| Sony | 37,131 | 289 | Jan 1-29, 2026 |
| Hisense | 30,933 | 276 | Jan 1-29, 2026 |

---

## Key Findings

### 1. Share of Voice on Generic Prompts

"Generic prompts" = prompts without any brand name (e.g., "best 65 inch TV" not "best Samsung TV")

| Brand | Prompts Appearing In | Coverage % | Total Mentions | Mention Share |
|-------|---------------------|------------|----------------|---------------|
| **Samsung** | 350 / 353 | **99.2%** | 119,166 | 38.9% |
| LG | 309 / 353 | 87.5% | 75,493 | 24.6% |
| Sony | 287 / 353 | 81.3% | 35,539 | 11.6% |
| TCL | 280 / 353 | 79.3% | 46,306 | 15.1% |
| Hisense | 273 / 353 | 77.3% | 30,097 | 9.8% |

**Key Insight:** Samsung appears in 99% of generic TV prompts - AI models recommend Samsung most frequently.

### 2. Sentiment Comparison on Generic Prompts

| Brand | Positive % | Neutral % | Negative % |
|-------|------------|-----------|------------|
| **LG** | **75.7%** | 23.7% | 0.6% |
| TCL | 74.3% | 25.5% | 0.3% |
| Hisense | 72.1% | 27.1% | 0.8% |
| Samsung | 70.4% | 26.6% | **3.0%** |
| Sony | 70.1% | 29.5% | 0.5% |

**Key Insight:** Samsung has highest negative sentiment (3.0%) - 5x higher than competitors. More coverage = more scrutiny.

### 3. Competitive Landscape Overview

| Brand | Total Rows | Unique Prompts | Unique Concepts | Positive % | Negative % |
|-------|------------|----------------|-----------------|------------|------------|
| Samsung | 145,337 | 377 | 12,442 | 70.5% | 3.0% |
| LG | 78,232 | 314 | 6,509 | 75.4% | 0.6% |
| TCL | 47,126 | 283 | 4,139 | 74.2% | 0.3% |
| Sony | 37,131 | 289 | 4,478 | 70.4% | 0.4% |
| Hisense | 30,933 | 276 | 3,468 | 72.2% | 0.8% |

---

## Analysis by Tag/Topic

### Gaming Tag (39 prompts)

| Brand | Unique Concepts | Positive % | Top Products |
|-------|-----------------|------------|--------------|
| **Samsung** | **1,626** | 78.6% | S95F, S90F |
| LG | 1,446 | 77.9% | C5 OLED, G5 OLED |
| Sony | 1,114 | 68.7% | PS5, Bravia 8 II |
| TCL | 839 | **80.3%** | QM7K, QM8K |
| Hisense | 653 | 74.9% | U8N |

**Samsung leads Gaming** with most concepts, but TCL has highest positive %.

### OLED Tag (26 prompts)

| Brand | Unique Concepts | Positive % | Top Products |
|-------|-----------------|------------|--------------|
| **LG** | **1,464** | **81.9%** | G5, C5, G6 |
| Samsung | 1,255 | 75.5% | S95F, S95H, S90F |
| Sony | 687 | 79.5% | Bravia 8 II, A95L |
| TCL | 152 | 73.7% | QM8K |
| Hisense | 115 | 75.7% | U8N |

**LG leads OLED** with most concepts AND highest positive %.

---

## Samsung's Top Negative Concepts

| Concept | Negative Count | Sample Quote |
|---------|----------------|--------------|
| remote control | 188 | "A few users mention the remote isn't ideal" |
| price | 172 | "Much more expensive than 4K" |
| contrast | 157 | "blacks can sometimes look grayish" |
| viewing angles | 139 | "Image quality degrades significantly from the side" |
| local dimming | 137 | "lacks local dimming, causing blacks to appear grayish" |

---

## Head-to-Head: Samsung vs LG OLED

Based on prompt: "compare Samsung vs LG OLED tvs"

### Samsung-Only Concepts (124 unique)

**Strengths:**
- QD-OLED technology, quantum dots
- Bright room performance, anti-glare/matte screen
- Peak brightness 4500 nits
- Color vibrancy, superior color volume
- Tizen OS, Samsung Gaming Hub, SmartThings
- Xbox Cloud Gaming, GeForce Now support
- One Connect Box, solar-powered remote

**Weaknesses:**
- Lack of Dolby Vision
- Higher burn-in risk
- Slight off-axis tint

### LG-Only Concepts (166 unique)

**Strengths:**
- Dolby Vision, Dolby Atmos support
- WOLED panel, OLED Evo, Micro Lens Array (MLA)
- Alpha 11 AI processor
- Natural colors, color accuracy, cinematic quality
- Dark room performance, perfect blacks
- webOS, Magic Remote
- 5-year update commitment, extended panel warranty
- Up to 97-inch size

**Notable:**
- Glossy screen (vs Samsung's matte)
- 1080p gaming at 330Hz
- Filmmaker mode

### Key Differentiators

| Feature | Samsung | LG |
|---------|---------|-----|
| Panel tech | QD-OLED | WOLED + MLA |
| Peak brightness | 4500 nits | 3000 nits |
| Screen finish | Matte/anti-glare | Glossy |
| Best for | Bright rooms | Dark rooms |
| Dolby Vision | No | Yes |
| Max size | 77" | 97" |
| OS | Tizen | webOS |

---

## RPC Functions for Competitive Analysis

### `get_competitive_sov(p_prompt_type)`
Returns Share of Voice by brand on generic/all prompts.

```sql
-- Generic prompts only
SELECT * FROM get_competitive_sov('generic');

-- All prompts
SELECT * FROM get_competitive_sov('all');
```

### `get_brand_sentiment_comparison(p_prompt_type)`
Returns sentiment breakdown by brand.

```sql
SELECT * FROM get_brand_sentiment_comparison('generic');
```

### `get_negative_concepts_by_brand(p_brand, p_limit)`
Returns top negative concepts with sample quotes.

```sql
SELECT * FROM get_negative_concepts_by_brand('Samsung', 10);
SELECT * FROM get_negative_concepts_by_brand('LG', 10);
```

### `get_prompt_brand_comparison(p_prompt, p_tag)`
Compares brands on a specific prompt or tag.

```sql
-- Single prompt
SELECT * FROM get_prompt_brand_comparison('best 65 inch tv for sports');

-- By tag
SELECT * FROM get_prompt_brand_comparison(p_tag => 'Gaming');
SELECT * FROM get_prompt_brand_comparison(p_tag => 'OLED');

-- Both
SELECT * FROM get_prompt_brand_comparison('best gaming tv', 'Gaming');
```

### `get_competitive_landscape()`
Quick overview of all brands.

```sql
SELECT * FROM get_competitive_landscape();
```

---

## Data Collection Scripts

### Fetching Competitor Data

Script: `clients/samsung/fetch_competitor_concept_prompts.py`

```bash
uv run clients/samsung/fetch_competitor_concept_prompts.py
```

- Fetches LG, Sony, TCL, Hisense from SEMrush API
- 116 API calls (~12 minutes)
- Loads into `semrush_concept_prompts` table

---

## Methodology Notes

### Prompt Classification
- **Generic prompts**: No brand name in query (356 prompts)
- **Samsung-branded**: Contains "samsung" (27 prompts)
- **Other-branded**: Contains competitor names

### Concept Granularity
SEMrush extracts concepts at fine granularity:
- "4k 144hz", "4k@144hz", "4k 144 hz support" are separate concepts
- Average ~97 unique concepts per prompt
- Concepts deduplicated across prompts for totals

### Sentiment Context
- **Solo mentions**: Samsung alone = 71.1% positive, 3.1% negative
- **Competitive context**: Samsung + competitors = 61.4% positive, 0.9% negative
- Competitive comparisons are more neutral/balanced

---

## URL Citation Analysis

### Top Cited Domains on Generic Prompts

AI models cite these sources most frequently when answering generic TV queries:

| Domain | Citations | Prompts Cited In | Avg Position |
|--------|-----------|------------------|--------------|
| rtings.com | 14,414 | 342 | 7.1 |
| samsung.com | 12,012 | 319 | 8.8 |
| techradar.com | 10,686 | 330 | 7.4 |
| youtube.com | 10,386 | 352 | 9.2 |
| tomsguide.com | 8,147 | 323 | 7.4 |
| bestbuy.com | 5,543 | 251 | 9.5 |
| reddit.com | 5,340 | 338 | 9.9 |
| cnet.com | 3,915 | 303 | 7.2 |
| businessinsider.com | 3,725 | 233 | 5.9 |
| forbes.com | 3,455 | 224 | 9.2 |

**Key Insight:** rtings.com is the #1 cited source - their TV reviews heavily influence AI recommendations.

### Brand Website Citations

How often AI cites official brand websites on generic (non-branded) prompts:

| Brand | Citations | Prompts Cited In | Avg Position |
|-------|-----------|------------------|--------------|
| **Samsung** | **14,986** | 332 | 8.9 |
| LG | 3,372 | 231 | 10.5 |
| TCL | 2,170 | 173 | 10.1 |
| Sony | 1,480 | 118 | 11.8 |
| Hisense | 76 | 41 | 12.1 |

**Key Insight:** Samsung.com is cited **4.4x more** than lg.com on generic prompts. Samsung's website SEO for AI visibility is significantly stronger.

### Top 3 Position Analysis

Which sources appear in the first 3 citation positions (most influential):

| Domain | Top-3 Citations | Prompts in Top 3 |
|--------|-----------------|------------------|
| rtings.com | 3,987 | 295 |
| techradar.com | 2,209 | 251 |
| tomsguide.com | 1,859 | 258 |
| samsung.com | 1,637 | 201 |
| businessinsider.com | 1,114 | 163 |
| bestbuy.com | 915 | 117 |
| forbes.com | 634 | 114 |
| cnet.com | 602 | 163 |
| lg.com | 410 | 104 |

**Key Insight:** Samsung.com appears in top-3 positions 4x more often than lg.com.

### Citations by AI Model

For "compare Samsung vs LG OLED tvs" prompt:

| Domain | Citations | Avg Position | Models Citing |
|--------|-----------|--------------|---------------|
| techradar.com | 75 | 8.8 | Google AI Mode, AI Overview, SearchGPT |
| rtings.com | 49 | 8.5 | Google AI Mode, AI Overview, SearchGPT |
| youtube.com | 49 | 6.2 | Google AI Mode, AI Overview |
| forbes.com | 26 | 9.7 | Google AI Mode, AI Overview, SearchGPT |
| tomsguide.com | 25 | 9.3 | Google AI Mode, SearchGPT |
| lg.com | 13 | 8.9 | SearchGPT only |
| cnet.com | 13 | 8.6 | Google AI Mode, AI Overview |
| consumerreports.org | 12 | 11.6 | AI Overview, SearchGPT |

**Key Insight:** lg.com is only cited by SearchGPT, not Google's AI models. Samsung.com not cited on direct comparison queries.

### URL Analysis Queries

```sql
-- Top cited domains on generic prompts
WITH generic_prompts AS (
  SELECT DISTINCT prompt FROM semrush_concept_prompts
  WHERE prompt NOT ILIKE '%samsung%' AND prompt NOT ILIKE '%lg%'
    AND prompt NOT ILIKE '%sony%' AND prompt NOT ILIKE '%tcl%'
    AND prompt NOT ILIKE '%hisense%'
)
SELECT
  REGEXP_REPLACE(pu.source, '^https?://([^/]+).*', '\1') as domain,
  COUNT(*) as citation_count,
  COUNT(DISTINCT pu.prompt) as prompts_cited_in,
  ROUND(AVG(pu.position)::numeric, 1) as avg_position
FROM semrush_prompt_urls pu
JOIN generic_prompts gp ON pu.prompt = gp.prompt
GROUP BY 1 ORDER BY 2 DESC LIMIT 20;

-- Brand website citations comparison
SELECT
  CASE
    WHEN source ILIKE '%samsung.com%' THEN 'Samsung'
    WHEN source ILIKE '%lg.com%' THEN 'LG'
    WHEN source ILIKE '%sony.%' THEN 'Sony'
    WHEN source ILIKE '%tcl.com%' THEN 'TCL'
    WHEN source ILIKE '%hisense.%' THEN 'Hisense'
  END as brand,
  COUNT(*) as citations,
  COUNT(DISTINCT prompt) as prompts_cited_in,
  ROUND(AVG(position)::numeric, 1) as avg_position
FROM semrush_prompt_urls
WHERE source ILIKE '%samsung.com%' OR source ILIKE '%lg.com%'
  OR source ILIKE '%sony.%' OR source ILIKE '%tcl.com%'
  OR source ILIKE '%hisense.%'
GROUP BY 1 ORDER BY 2 DESC;
```
