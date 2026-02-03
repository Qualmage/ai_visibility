# Samsung Dashboard - Data Requirements

This document tracks which data sources are available in Supabase vs. using placeholder data.

## Available Supabase Tables

| Table | Status | Rows | Notes |
|-------|--------|------|-------|
| `semrush_concept_mentions` | ✅ Available | 151,787 | Brand mentions, sentiment, concept categories by date/model |
| `semrush_cited_pages` | ✅ Available | 84,856 | URLs cited in AI responses, domain info |
| `semrush_url_prompts` | ✅ Available | 43,842 | Prompts per URL with volume, topic, LLM |
| `semrush_concept_prompts` | ✅ Available | 145,337 | Brand mentions with prompts, quotes, sentiment |
| `semrush_prompt_urls` | ✅ Available | 249,307 | Date-stamped prompt-to-source mappings with position |
| `tv_topics` | ✅ Available | 41 | TV topic categories for filter dropdown |

## Available RPC Functions

| Function | Status | Notes |
|----------|--------|-------|
| `get_daily_mentions` | ✅ Available | Aggregated mentions by date/model/brand |
| `get_top_categories` | ✅ Available | Top concept categories with sentiment |
| `get_sources_by_topic` | ✅ Available | Sources by topic with sentiment breakdown (joins prompt_urls + concept_prompts) |

### RPC Function Details

#### `get_daily_mentions(date_from, model_filter)`
Returns daily aggregated mentions for KPI cards and trend charts.
- **Returns:** date, model, brand, total_mentions, sentiment_positive, sentiment_negative, sentiment_neutral

#### `get_top_categories(date_from, model_filter, limit_count)`
Returns top concept categories for the Topics bar chart.
- **Returns:** concept_category, total_mentions, sentiment breakdown

#### `get_sources_by_topic(p_date, p_tag)`
Returns sources (domains) for a specific topic with sentiment analysis.
- **Parameters:** `p_date` (date), `p_tag` (topic/tag text)
- **Returns:** domain, domain_type, citations, mentions, positive_pct, negative_pct, neutral_pct
- **Used by:** Sources by Topic with Sentiment table in GEO Dashboard
- **Note:** Joins `semrush_prompt_urls` with `semrush_concept_prompts` to correlate citations with sentiment

## KPI Cards - Data Mapping

| KPI | Data Source | Status | Placeholder Value |
|-----|-------------|--------|-------------------|
| Share of Voice | `semrush_concept_mentions` → Samsung mentions / Total | ✅ Live | -- |
| Source Visibility | `semrush_cited_pages` → Samsung citations / Total | ✅ Live | -- |
| Referral Traffic | **NOT IN SUPABASE** - Needs GA4 integration | ⚠️ Placeholder | 106,445 |
| AI Visibility Score | Composite calculation from mentions | ✅ Live | -- |

## Line Charts - Data Mapping

| Chart | Data Source | Status | Notes |
|-------|-------------|--------|-------|
| Share of Voice Trend | `get_daily_mentions` grouped by brand | ✅ Live | Calculate % per date |
| Source Visibility Trend | `semrush_cited_pages` by date | ⚠️ Needs date field | No date in cited_pages |
| Referral Traffic Trend | **NOT IN SUPABASE** | ⚠️ Placeholder | Needs GA4 data |
| AI Visibility Trend | Composite from daily mentions | ✅ Live | -- |

## New Visualizations - Data Mapping

| Visualization | Data Source | Status | Notes |
|---------------|-------------|--------|-------|
| Brand Heatmap | `semrush_concept_mentions` | ✅ Live | Group by concept × brand |
| Sentiment Treemap | `semrush_concept_mentions` | ✅ Live | sentiment_* fields |
| Model Radar | `get_daily_mentions` | ⚠️ Partial | Missing position data |
| Citation Sankey | `semrush_url_prompts` + `semrush_cited_pages` | ⚠️ Partial | Need topic→prompt→url links |

## Sunburst Chart - Data Mapping

| Field | Data Source | Status |
|-------|-------------|--------|
| concept_category | `semrush_concept_mentions` | ✅ Available |
| concept_subcategory | `semrush_concept_mentions` | ✅ Available |
| concept | `semrush_concept_mentions` | ✅ Available |
| mentions | `semrush_concept_mentions` | ✅ Available |
| Share of Voice | Calculated: brand mentions / total | ✅ Calculated |
| Visibility | **NOT IN SUPABASE** | ⚠️ Placeholder |

## Prompt Rankings Table - Data Mapping

| Column | Data Source | Status |
|--------|-------------|--------|
| Prompt | `semrush_url_prompts.prompt` | ✅ Available |
| Model/LLM | `semrush_url_prompts.llm` | ✅ Available |
| Topic | `semrush_url_prompts.topic` | ✅ Available |
| Volume | `semrush_url_prompts.volume` | ✅ Available |
| Visibility | **NOT IN SUPABASE** | ⚠️ Placeholder |
| Position (prev/curr) | **NOT IN SUPABASE** | ⚠️ Placeholder |
| Product mentioned | `semrush_url_prompts.mentioned_brands_count` | ⚠️ Partial |

## Source Analysis - Data Mapping

| Metric | Data Source | Status |
|--------|-------------|--------|
| Total Citations | `semrush_cited_pages.prompts_count` | ✅ Available |
| Citation Gaps | **NOT IN SUPABASE** | ⚠️ Placeholder |
| Source Type (owned/earned/social) | Derived from `domain` field | ✅ Calculated |
| Domain table | `semrush_cited_pages` grouped by domain | ✅ Available |
| URL table | `semrush_cited_pages` | ✅ Available |
| Avg Position | `semrush_prompt_urls.position` | ✅ Available |

## Cited URLs Table - Data Mapping

| Column | Data Source | Status |
|--------|-------------|--------|
| URL | SEMrush API Element `3c29aa85-4f06-4f14-a376-b02333c6e3fa` | ✅ Live via Proxy |
| Domain | Extracted from URL | ✅ Calculated |
| Prompts Count | SEMrush API response | ✅ Live |
| Triggering Prompts | SEMrush API response | ✅ Live |

**Note:** This table fetches live data from SEMrush via the Supabase Edge Function proxy (`semrush-proxy`).

## Sources by Topic with Sentiment - Data Mapping

| Column | Data Source | Status |
|--------|-------------|--------|
| Domain | `get_sources_by_topic` RPC | ✅ Live |
| Type | `get_sources_by_topic` RPC (domain_type) | ✅ Live |
| Citations | `get_sources_by_topic` RPC | ✅ Live |
| Mentions | `get_sources_by_topic` RPC | ✅ Live |
| Sentiment (positive %) | `get_sources_by_topic` RPC (positive_pct) | ✅ Live |
| Sentiment (negative %) | `get_sources_by_topic` RPC (negative_pct) | ✅ Live |
| Sentiment (neutral %) | `get_sources_by_topic` RPC (neutral_pct) | ✅ Live |

**Note:** This table uses the `get_sources_by_topic` RPC function which joins `semrush_prompt_urls` (249K rows) with `semrush_concept_prompts` (145K rows) server-side for performance.

## Data Needed for Full Implementation

### Priority 1 - Missing Core Data
1. **Referral Traffic** - Needs Google Analytics integration
   - Sessions/visits from AI platforms (ChatGPT, Perplexity, etc.)
   - Traffic by source over time

2. **Position/Ranking Data** - Partially available
   - `semrush_prompt_urls.position` contains URL position in AI responses ✅
   - Brand position in AI response (1st, 2nd, 3rd mention) - needs calculation
   - Position changes over time - available via date field in `semrush_prompt_urls`

### Priority 2 - Enhanced Analytics
3. **Visibility Score** - Need definition
   - How is visibility calculated?
   - What factors contribute to the score?

4. **Citation Gaps** - Need competitor comparison
   - Prompts where competitors cited but Samsung not
   - Requires cross-referencing competitor data

### Priority 3 - Time Series
5. **Historical data with dates** for:
   - Cited pages (add `date` or `fetched_at` column)
   - Position tracking over time

## Placeholder Data Locations

The following files contain placeholder/dummy data that should be replaced:

1. `scom-overview.html` - Line charts use hardcoded date arrays
2. `templates/model-radar.html` - Top Position Rate metric is placeholder
3. `templates/citation-sankey.html` - Link relationships are simulated
4. Source Analysis section - Citation gaps, avg position are hardcoded

## How to Update When Data Available

1. **For new Supabase columns**: Update `js/supabase-data.js` fetch functions
2. **For new RPC functions**: Add to `callRPC()` calls in supabase-data.js
3. **For GA4 integration**: Create new fetch function or MCP server connection
4. **For calculated fields**: Update `calculateKPIs()` or `calculateSourceVisibility()`
