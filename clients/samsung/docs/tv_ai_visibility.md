# TV AI Visibility Slides Documentation

## Purpose of This Document

This document tracks all slides created for the TV AI Visibility presentation. For each slide, include:

1. **Slide Name & File Path** - Where the HTML file is located
2. **Data Source** - Which Supabase table(s) or API(s) the data comes from
3. **Query/Filter Details** - The specific filters, tags, brands, models, and date range used
4. **Key Metrics** - The actual numbers displayed on the slide
5. **Key Insights** - The main takeaways highlighted on the slide
6. **Methodology Notes** - Any important context about how data was aggregated or calculated

---

## Slides

### 1. Share of Voice - AI Concept Mentions

**File Path:** `clients/samsung/slides/tv_ai_visibility/sov_mentions.html`

**Date Created:** 2026-02-04

**Data Source:**
- Supabase table: `semrush_concept_mentions_by_tag`

**Query Details:**
- **Date:** 2026-01-31 (single day snapshot)
- **Brands:** Samsung, LG, Sony, Hisense, TCL
- **AI Models:** All 3 (search-gpt, google-ai-overview, google-ai-mode)
- **Tags (10 categories):**
  - TV Models__QLED
  - TV Models__Sports TVs
  - TV Models__Gaming TVs
  - TV Models__OLED
  - TV Models__Micro RGB
  - TV Models__Mini-LED
  - TV Models__Movies & Cinema
  - TV Features__AI
  - TV Models__Art TV
  - TV Models__Outdoor TV

**SQL Query Used:**
```sql
SELECT
  CASE
    WHEN tag LIKE '%__QLED' THEN 'QLED'
    WHEN tag LIKE '%__Sports TVs' THEN 'Sports TVs'
    -- ... etc
  END as tag_group,
  brand,
  SUM(mentions) as total_mentions
FROM semrush_concept_mentions_by_tag
WHERE tag IN (
  'TV Models__QLED', 'TV Models__Sports TVs', 'TV Models__Gaming TVs',
  'TV Models__OLED', 'TV Models__Micro RGB', 'TV Models__Mini-LED',
  'TV Models__Movies & Cinema', 'TV Features__AI', 'TV Models__Art TV',
  'TV Models__Outdoor TV'
)
GROUP BY 1, 2
ORDER BY tag_group, brand;
```

**Key Metrics:**

| Tag Category | Samsung | LG | Sony | Hisense | TCL | Row Total |
|--------------|---------|-----|------|---------|-----|-----------|
| QLED | 2,131 (53.2%) | 158 (3.9%) | 292 (7.3%) | 391 (9.8%) | 1,037 (25.9%) | 4,009 |
| Sports TVs | 1,970 (34.1%) | 1,072 (18.6%) | 778 (13.5%) | 659 (11.4%) | 1,299 (22.5%) | 5,778 |
| Gaming TVs | 1,746 (29.6%) | 1,847 (31.3%) | 787 (13.3%) | 513 (8.7%) | 1,011 (17.1%) | 5,904 |
| OLED | 1,685 (44.5%) | 1,505 (39.8%) | 357 (9.4%) | 101 (2.7%) | 138 (3.6%) | 3,786 |
| Micro RGB | 916 (62.1%) | 355 (24.1%) | 19 (1.3%) | 157 (10.7%) | 27 (1.8%) | 1,474 |
| Mini-LED | 828 (28.8%) | 195 (6.8%) | 567 (19.7%) | 487 (16.9%) | 798 (27.8%) | 2,875 |
| Movies & Cinema | 542 (32.2%) | 342 (20.3%) | 343 (20.4%) | 155 (9.2%) | 299 (17.8%) | 1,681 |
| AI | 308 (42.5%) | 230 (31.8%) | 153 (21.1%) | 5 (0.7%) | 28 (3.9%) | 724 |
| Art TV | 102 (36.4%) | 32 (11.4%) | 28 (10.0%) | 66 (23.6%) | 52 (18.6%) | 280 |
| Outdoor TV | 97 (82.9%) | 0 (0%) | 0 (0%) | 10 (8.5%) | 10 (8.5%) | 117 |
| **TOTAL** | **10,325** | **5,736** | **3,324** | **2,544** | **4,699** | **26,628** |
| **Overall Share %** | **38.8%** | **21.5%** | **12.5%** | **9.6%** | **17.6%** | 100% |

**Visualizations:**
1. Data table with mentions by tag category and brand (with row percentages)
2. Donut chart showing overall competitor share of voice

**Key Insights (displayed on slide):**

1. **Samsung Leads Overall SOV at 38.8%**
   - Samsung commands the largest share of AI concept mentions across all 10 tag categories
   - 10,325 total mentions - nearly double the second-place competitor LG (5,736)

2. **LG Dominates Gaming TVs**
   - Gaming TVs is the only category where a competitor outperforms Samsung
   - LG: 1,847 mentions (31.3%) vs Samsung: 1,746 mentions (29.6%)
   - This is a high-value segment worth monitoring

3. **QLED is Samsung's Strongest Category**
   - Samsung dominates QLED with 2,131 mentions (53.2% category share)
   - More than 2x the nearest competitor TCL (1,037)
   - Reflects Samsung's brand ownership of the QLED term

**Methodology Notes:**
- Data sourced from SEMrush AI Visibility platform
- Mentions aggregated across 3 AI models (SearchGPT, Google AI Overview, Google AI Mode)
- Single day snapshot: January 31, 2026
- Row percentages show each brand's share within that category
- Overall share percentages show each brand's share of total mentions across all categories

---

### 2. Platform Breakdown - Mentions by AI Model

**File Path:** `clients/samsung/slides/tv_ai_visibility/platform_breakdown.html`

**Date Created:** 2026-02-04

**Data Source:**
- Supabase table: `semrush_concept_mentions_by_tag`

**Query Details:**
- **Date:** 2026-01-31 (single day snapshot)
- **Brands:** Samsung, LG, Sony, Hisense, TCL
- **AI Models:** All 3 (search-gpt, google-ai-overview, google-ai-mode)
- **Tags:** Same 10 categories as Slide 1

**SQL Query Used:**
```sql
SELECT
  model,
  brand,
  SUM(mentions) as total_mentions
FROM semrush_concept_mentions_by_tag
WHERE tag IN (
  'TV Models__QLED', 'TV Models__Sports TVs', 'TV Models__Gaming TVs',
  'TV Models__OLED', 'TV Models__Micro RGB', 'TV Models__Mini-LED',
  'TV Models__Movies & Cinema', 'TV Features__AI', 'TV Models__Art TV',
  'TV Models__Outdoor TV'
)
GROUP BY model, brand
ORDER BY model, total_mentions DESC;
```

**Key Metrics:**

| Model | Samsung | LG | Sony | Hisense | TCL | Total |
|-------|---------|-----|------|---------|-----|-------|
| Google AI Mode | 4,185 (38.7%) | 2,424 (22.4%) | 1,419 (13.1%) | 963 (8.9%) | 1,824 (16.9%) | 10,815 |
| SearchGPT | 3,047 (37.1%) | 1,729 (21.0%) | 1,059 (12.9%) | 861 (10.5%) | 1,521 (18.5%) | 8,217 |
| Google AI Overview | 3,093 (40.7%) | 1,583 (20.8%) | 846 (11.1%) | 720 (9.5%) | 1,354 (17.8%) | 7,596 |
| **TOTAL** | **10,325** | **5,736** | **3,324** | **2,544** | **4,699** | **26,628** |

**Brand Index by Platform (vs Overall Share):**

| Brand | Overall Share | AI Mode Index | SearchGPT Index | AI Overview Index |
|-------|---------------|---------------|-----------------|-------------------|
| Samsung | 38.8% | -0.3% | -4.4% | +4.9% |
| LG | 21.5% | +4.2% | -2.3% | -3.3% |
| Sony | 12.5% | +4.8% | +3.2% | -11.2% |
| Hisense | 9.6% | -7.0% | +1.4% | -5.3% |
| TCL | 17.6% | -4.2% | +3.2% | +2.1% |

**Visualizations:**
1. Three horizontal bar charts (one per AI model) showing mentions by brand
2. Brand Index table showing over/under-indexing by platform
3. Platform volume insights summary

**Key Insights (displayed on slide):**

1. **Google AI Mode Drives Most Volume**
   - Google AI Mode generates 40.6% of all mentions (10,815 of 26,628)
   - Significantly more than SearchGPT (30.9%) or AI Overview (28.5%)
   - The conversational format produces richer brand discussions

2. **Samsung Over-Indexes on AI Overview**
   - Samsung captures 40.7% share on AI Overview vs 38.8% overall (+4.9% index)
   - Google's snippet format favors Samsung's strong SEO presence and product documentation

3. **Sony Struggles on AI Overview**
   - Sony under-indexes by -11.2% on AI Overview (11.1% vs 12.5% overall)
   - But over-indexes on AI Mode (+4.8%) and SearchGPT (+3.2%)
   - Sony performs better in conversational contexts

**Methodology Notes:**
- Index calculated as: (Brand's share on platform) - (Brand's overall share)
- Positive index = brand over-indexes on that platform
- Average mentions per brand: 5,326 (26,628 / 5)
- Platform volume: AI Mode (40.6%), SearchGPT (30.9%), AI Overview (28.5%)

---

### 3. Citations Analysis - Samsung vs Benchmark Competitors

**File Path:** `clients/samsung/slides/tv_ai_visibility/citations_vs_competitors.html`

**Date Created:** 2026-02-04

**Data Source:**
- Supabase table: `semrush_prompt_urls`

**Query Details:**
- **Date:** 2026-01-31 (single day snapshot)
- **Domain Types:** Owned (samsung.com), Benchmark Competitors (LG, Sony, TCL, Hisense, retail)
- **Tags:** Same 10 categories as Slide 1

**SQL Query Used:**
```sql
WITH tag_citations AS (
  SELECT
    CASE
      WHEN tags LIKE '%TV Models__QLED%' THEN 'QLED'
      WHEN tags LIKE '%TV Models__Sports TVs%' THEN 'Sports TVs'
      WHEN tags LIKE '%TV Models__Gaming TVs%' THEN 'Gaming TVs'
      WHEN tags LIKE '%TV Models__OLED%' THEN 'OLED'
      WHEN tags LIKE '%TV Models__Micro RGB%' THEN 'Micro RGB'
      WHEN tags LIKE '%TV Models__Mini-LED%' THEN 'Mini-LED'
      WHEN tags LIKE '%TV Models__Movies & Cinema%' THEN 'Movies & Cinema'
      WHEN tags LIKE '%TV Features__AI%' THEN 'AI'
      WHEN tags LIKE '%TV Models__Art TV%' THEN 'Art TV'
      WHEN tags LIKE '%TV Models__Outdoor TV%' THEN 'Outdoor TV'
    END as tag_category,
    domain_type
  FROM semrush_prompt_urls
  WHERE date = '2026-01-31'
)
SELECT tag_category,
  SUM(CASE WHEN domain_type = 'Owned' THEN 1 ELSE 0 END) as owned,
  SUM(CASE WHEN domain_type = 'Benchmark Competitors' THEN 1 ELSE 0 END) as competitors
FROM tag_citations
WHERE tag_category IS NOT NULL
GROUP BY tag_category;
```

**Key Metrics:**

| Tag Category | Samsung (Owned) | Competitors | Samsung % |
|--------------|-----------------|-------------|-----------|
| QLED | 157 | 46 | 77.3% |
| AI | 107 | 17 | 86.3% |
| Gaming TVs | 80 | 59 | 57.6% |
| Micro RGB | 74 | 30 | 71.2% |
| OLED | 34 | 22 | 60.7% |
| Mini-LED | 16 | 10 | 61.5% |
| Sports TVs | 15 | 23 | 39.5% |
| Outdoor TV | 6 | 0 | 100% |
| Movies & Cinema | 2 | 2 | 50% |
| Art TV | 1 | 0 | 100% |
| **TOTAL** | **492** | **209** | **70.2%** |

**Visualizations:**
1. Stacked horizontal bar chart showing Samsung (Owned) vs Competitors by tag category
2. Summary table with citation counts and Samsung win percentages

**Key Insights (displayed on slide):**

1. **Samsung Dominates AI Category Citations**
   - 86.3% citation share (107 vs 17) reflects Samsung's strong AI-focused content strategy

2. **Sports TVs is Samsung's Weakest Category**
   - Only 39.5% share (15 vs 23) - competitors are cited more frequently for sports-related queries

3. **QLED Validates Brand Ownership**
   - 77.3% citation share for QLED content - competitors are rarely cited as sources

**Methodology Notes:**
- Citations = URLs used as sources in AI responses
- "Owned" = samsung.com and subdomains
- "Benchmark Competitors" = LG, Sony, TCL, Hisense, BestBuy, Walmart domains

---

### 4. Citation Sources - Domain Type Analysis

**File Path:** `clients/samsung/slides/tv_ai_visibility/citation_sources.html`

**Date Created:** 2026-02-04

**Data Source:**
- Supabase table: `semrush_prompt_urls`

**Query Details:**
- **Date:** 2026-01-31 (single day snapshot)
- **All domain types:** Owned, Benchmark Competitors, Earned, Social, Other

**SQL Query Used:**
```sql
SELECT
  REGEXP_REPLACE(source, '^https?://([^/]+).*', '\1') as domain,
  domain_type,
  COUNT(*) as citations
FROM semrush_prompt_urls
WHERE date = '2026-01-31'
GROUP BY 1, 2
ORDER BY citations DESC
LIMIT 15;
```

**Key Metrics:**

**Domain Type Breakdown (13,273 total):**
| Domain Type | Citations | % |
|-------------|-----------|---|
| Other | 7,741 | 58.4% |
| Earned | 2,755 | 20.8% |
| Social | 1,090 | 8.2% |
| Owned | 990 | 7.5% |
| Benchmark Competitors | 697 | 5.3% |

**Top Cited Domains:**
| Rank | Domain | Citations | Type |
|------|--------|-----------|------|
| 1 | rtings.com | 855 | Other |
| 2 | samsung.com | 792 | Owned |
| 3 | youtube.com | 687 | Social |
| 4 | techradar.com | 572 | Earned |
| 5 | tomsguide.com | 443 | Earned |
| 6 | reddit.com | 281 | Social |
| 7 | bestbuy.com | 280 | Competitor |
| 8 | cnet.com | 278 | Earned |
| 9 | businessinsider.com | 253 | Earned |
| 10 | forbes.com | 178 | Earned |
| 11 | news.samsung.com | 169 | Owned |
| 12 | lg.com | 167 | Competitor |

**Visualizations:**
1. Donut chart showing domain type breakdown
2. Top cited domains table with type badges

**Key Insights (displayed on slide):**

1. **Rtings.com is #1 Cited Source**
   - 855 citations - even beating Samsung.com (792)
   - Review aggregators heavily influence AI responses

2. **Samsung.com Ranks #2 Overall**
   - 792 + 169 (news.samsung.com) = 961 total owned citations
   - Strong owned media presence in AI citations

3. **Earned Media is Critical**
   - TechRadar (572) + TomsGuide (443) + CNET (278) = 1,293 citations
   - PR/earned media strategy directly impacts AI visibility

**Methodology Notes:**
- Domains extracted from source URLs using regex
- Domain types assigned by SEMrush based on domain classification

---

### 5. Owned Sources Deep Dive - Regional Citation Analysis

**File Path:** `clients/samsung/slides/tv_ai_visibility/owned_sources.html`

**Date Created:** 2026-02-04

**Data Source:**
- Supabase table: `semrush_prompt_urls`

**Query Details:**
- **Date:** 2026-01-31 (single day snapshot)
- **Filter:** domain_type = 'Owned' only
- **Region extraction:** URL path patterns (e.g., /us/, /uk/)

**SQL Query Used:**
```sql
WITH owned_by_region AS (
  SELECT
    CASE
      WHEN source ~ 'www\.samsung\.com/us[/\?#]' THEN 'US'
      WHEN source ~ 'www\.samsung\.com/uk[/\?#]' THEN 'UK'
      WHEN source ~ 'www\.samsung\.com/au[/\?#]' THEN 'AU'
      WHEN source ~ 'www\.samsung\.com/ca[/\?#]' THEN 'CA'
      WHEN source LIKE '%news.samsung.com/us%' THEN 'US'
      WHEN source LIKE '%news.samsung.com/global%' THEN 'Global'
      ELSE 'Other'
    END as region,
    CASE
      WHEN source LIKE '%www.samsung.com%' THEN 'www.samsung.com'
      WHEN source LIKE '%news.samsung.com%' THEN 'news.samsung.com'
      ELSE 'Other subdomain'
    END as property
  FROM semrush_prompt_urls
  WHERE date = '2026-01-31'
    AND domain_type = 'Owned'
)
SELECT region, property, COUNT(*) as citations
FROM owned_by_region
GROUP BY region, property
ORDER BY citations DESC;
```

**Key Metrics:**

**Owned Citations by Region (990 total):**
| Region | www.samsung.com | news.samsung.com | Other | Total | % |
|--------|-----------------|------------------|-------|-------|---|
| US | 477 | 69 | 0 | 546 | 55.2% |
| Other/Unknown | 144 | 20 | 5 | 169 | 17.1% |
| UK | 65 | 10 | 0 | 75 | 7.6% |
| Global | 1 | 51 | 0 | 52 | 5.3% |
| CA | 33 | 0 | 0 | 33 | 3.3% |
| AU | 17 | 4 | 0 | 21 | 2.1% |
| SG | 20 | 0 | 0 | 20 | 2.0% |
| MY | 17 | 0 | 0 | 17 | 1.7% |
| IN + Others | 18 | 18 | 21 | 57 | 5.8% |
| **TOTAL** | **792** | **172** | **26** | **990** | **100%** |

**Subdomain Breakdown:**
| Subdomain | Citations | % |
|-----------|-----------|---|
| www.samsung.com | 792 | 80.0% |
| news.samsung.com | 169 | 17.1% |
| community.samsung.com | 15 | 1.5% |
| insights.samsung.com | 9 | 0.9% |
| Other | 5 | 0.5% |

**Visualizations:**
1. Donut chart showing regional breakdown (US 55.2% highlighted)
2. Table showing citations by region and property type
3. Subdomain contribution bar chart

**Key Insights (displayed on slide):**

1. **US Drives Only 55% of Owned Citations**
   - samsung.com/us (477) + news.samsung.com/us (69) = 546 citations
   - 45% (444 citations) comes from other regions

2. **Non-US Countries Cannibalize ~300 Citations**
   - UK (75), CA (33), AU (21), SG (20), MY (17), IN (16) etc.
   - May be competing with US content in AI responses for US-based queries

3. **Global Newsroom is Critical**
   - news.samsung.com/global contributes 51 citations (5.3%)
   - The 4th largest source - centralized PR content reaches AI models effectively

**Methodology Notes:**
- Region extracted from URL path (e.g., /us/, /uk/) or subdomain prefix
- "Other/Unknown" includes URLs without clear regional indicators (e.g., /levant/, /ph/)
- Potential cannibalization concern: non-US regional content may be cited for US-market queries

---

### 6. Sentiment Overview - Brand Comparison

**File Path:** `clients/samsung/slides/tv_ai_visibility/sentiment_overview.html`

**Date Created:** 2026-02-04

**Data Source:**
- Supabase table: `semrush_concept_mentions_by_tag`

**Query Details:**
- **Date:** 2026-01-31 (single day snapshot)
- **Brands:** Samsung, LG, Sony, Hisense, TCL
- **AI Models:** All 3 (search-gpt, google-ai-overview, google-ai-mode)
- **Tags:** Same 10 TV categories as Slides 1-5

**SQL Query Used:**
```sql
SELECT
  brand,
  SUM(mentions) as total_mentions,
  SUM(sentiment_positive) as positive,
  SUM(sentiment_negative) as negative,
  SUM(sentiment_neutral) as neutral
FROM semrush_concept_mentions_by_tag
WHERE tag IN (
  'TV Models__QLED', 'TV Models__Sports TVs', 'TV Models__Gaming TVs',
  'TV Models__OLED', 'TV Models__Micro RGB', 'TV Models__Mini-LED',
  'TV Models__Movies & Cinema', 'TV Features__AI', 'TV Models__Art TV',
  'TV Models__Outdoor TV'
)
GROUP BY brand
ORDER BY total_mentions DESC;
```

**Key Metrics:**

**Sentiment by Brand:**
| Brand | Mentions | Positive | Negative | Neutral | Pos % | Neg % |
|-------|----------|----------|----------|---------|-------|-------|
| Samsung | 10,325 | 7,787 | 134 | 2,404 | 75.4% | 1.3% |
| LG | 5,736 | 4,495 | 18 | 1,223 | 78.4% | 0.3% |
| TCL | 4,699 | 3,738 | 17 | 944 | 79.5% | 0.4% |
| Sony | 3,324 | 2,541 | 9 | 774 | 76.4% | 0.3% |
| Hisense | 2,544 | 1,839 | 23 | 682 | 72.3% | 0.9% |

**Samsung Sentiment by AI Model:**
| Model | Mentions | Positive | Negative | Pos % |
|-------|----------|----------|----------|-------|
| Google AI Mode | 4,278 | 3,205 | 78 | 74.9% |
| Google AI Overview | 3,153 | 2,437 | 33 | 77.3% |
| SearchGPT | 3,156 | 2,315 | 26 | 73.4% |

**Visualizations:**
1. Sentiment by Brand table with positive/negative percentages
2. Donut chart showing Samsung's sentiment breakdown (75.4% positive)
3. Samsung Sentiment by AI Model table

**Key Insights (displayed on slide):**

1. **Samsung Leads Volume, Higher Negative Count**
   - 134 negative mentions vs competitors' combined 67
   - More visibility = more scrutiny
   - Focus on addressing specific product feedback

2. **AI Overview Most Favorable to Samsung**
   - 77.3% positive rate - highest among all 3 AI models
   - Google's snippet format favors Samsung's well-structured product content

3. **TCL Has Highest Positive %**
   - 79.5% positive rate despite fewer mentions
   - Budget-friendly positioning and value messaging resonates well with AI models

**Methodology Notes:**
- Data from `semrush_concept_mentions_by_tag` table
- Filtered to 10 TV categories: QLED, OLED, Mini-LED, Micro RGB, Gaming TVs, Sports TVs, Movies & Cinema, Art TV, Outdoor TV, AI Features
- Single day snapshot: January 31, 2026
- Sentiment classification performed by SEMrush AI analysis

---

### 7. Sentiment Drivers - What's Driving Positive & Negative Sentiment

**File Path:** `clients/samsung/slides/tv_ai_visibility/sentiment_drivers.html`

**Date Created:** 2026-02-04

**Data Source:**
- Supabase table: `semrush_concept_prompts`

**Query Details:**
- **Date:** 2026-01-31 (single day snapshot)
- **Brand:** Samsung
- **Sentiment Types:** positive, negative
- **Aggregation:** By concept, with top product association

**SQL Query Used:**
```sql
-- Positive Drivers
SELECT
  concept,
  sentiment,
  COUNT(*) as count,
  MODE() WITHIN GROUP (ORDER BY products[1]) as top_product
FROM semrush_concept_prompts
WHERE brand = 'Samsung'
  AND sentiment = 'positive'
GROUP BY concept, sentiment
ORDER BY count DESC
LIMIT 7;

-- Negative Drivers
SELECT
  concept,
  sentiment,
  COUNT(*) as count,
  MODE() WITHIN GROUP (ORDER BY products[1]) as top_product
FROM semrush_concept_prompts
WHERE brand = 'Samsung'
  AND sentiment = 'negative'
GROUP BY concept, sentiment
ORDER BY count DESC
LIMIT 7;
```

**Key Metrics:**

**Top Positive Sentiment Drivers (Samsung):**
| Concept | Product | Count |
|---------|---------|-------|
| Brightness | S95F | 338 |
| 4K Resolution | OLED 4K S95F TV | 136 |
| Contrast | Neo QLED | 134 |
| Picture Quality | S95F OLED | 121 |
| Gaming Features | S95F | 112 |
| Color Accuracy | S95F | 104 |
| Motion Handling | S95F | 75 |

**Top Negative Sentiment Drivers (Samsung):**
| Concept | Product | Count |
|---------|---------|-------|
| Contrast | DU8000 | 22 |
| Remote Control | Crystal UHD | 13 |
| Brightness | U8000F | 9 |
| Price | QN990F | 9 |
| Input Lag | QN990F | 8 |
| Dolby Vision Support | QN90D | 8 |
| Black Levels | The Frame / Pro | 7 |

**Visualizations:**
1. Side-by-side tables for positive and negative drivers
2. Green/red color-coded bars showing relative magnitude
3. Representative quotes from AI responses

**Key Insights (displayed on slide):**

1. **Brightness is Samsung's #1 Positive Driver**
   - 338 mentions - Samsung's peak brightness and anti-glare technology are key differentiators driving positive sentiment in AI responses

2. **Contrast Appears in Both Positive & Negative**
   - 134 positive vs 22 negative mentions
   - Context matters: Neo QLED praised in general but criticized when compared to OLED's perfect blacks

3. **Remote Control is a Known Pain Point**
   - 13 negative mentions specifically about laggy remote control
   - Actionable UX feedback for product team to address in future models

**Representative Quotes:**

- **Positive:** "Samsung S95F (QD-OLED) - Best overall for sports: superb brightness for an OLED, almost-perfect viewing angles, excellent motion and color, and an anti-glare finish that helps in bright rooms."

- **Negative:** "It lacks local dimming and has poor contrast, so blacks look grayish and the image appears washed out in a dark room." (About Crystal UHD DU7200)

**Methodology Notes:**
- Data from `semrush_concept_prompts` table
- Concepts aggregated by sentiment type for Samsung brand
- Quotes extracted from AI responses
- Single day snapshot: January 31, 2026

---

### 8. Competitor Sentiment Drivers - LG, Sony, TCL & Hisense Analysis

**File Path:** `clients/samsung/slides/tv_ai_visibility/competitor_sentiment.html`

**Date Created:** 2026-02-04

**Data Source:**
- Supabase tables:
  - `semrush_concept_mentions_by_tag` (for sentiment percentages)
  - `semrush_concept_prompts` (for concept drivers)

**Query Details:**
- **Date:** 2026-01-31 (single day snapshot)
- **Brands:** LG, Sony, TCL, Hisense
- **Tags:** Same 10 TV categories as other slides
- **Sentiment Types:** positive, negative

**SQL Queries Used:**
```sql
-- Sentiment percentages (from semrush_concept_mentions_by_tag)
SELECT
  brand,
  SUM(mentions) as total_mentions,
  SUM(sentiment_positive) as positive,
  SUM(sentiment_negative) as negative,
  ROUND(SUM(sentiment_positive)::decimal / SUM(mentions) * 100, 1) as pos_pct
FROM semrush_concept_mentions_by_tag
WHERE tag IN (
  'TV Models__QLED', 'TV Models__Sports TVs', 'TV Models__Gaming TVs',
  'TV Models__OLED', 'TV Models__Micro RGB', 'TV Models__Mini-LED',
  'TV Models__Movies & Cinema', 'TV Features__AI', 'TV Models__Art TV',
  'TV Models__Outdoor TV'
)
AND brand IN ('LG', 'Sony', 'TCL', 'Hisense')
GROUP BY brand;

-- Concept drivers (from semrush_concept_prompts)
SELECT
  brand,
  concept,
  sentiment,
  COUNT(*) as count
FROM semrush_concept_prompts
WHERE brand IN ('LG', 'Sony', 'TCL', 'Hisense')
  AND sentiment = 'positive'
GROUP BY brand, concept, sentiment
ORDER BY brand, count DESC;
```

**Key Metrics:**

**LG (78.4% Positive)**
- Hero Products: C5 OLED / G5 OLED
- Top Positive Drivers: Brightness (88), Picture Quality (84), Gaming Features (84), Contrast (83)
- Differentiator: OLED technology leadership (67 mentions)
- Top Negative: Motion Smoothing (3)

**Sony (76.4% Positive)**
- Hero Products: Bravia 9 / Bravia 8 II
- Top Positive Drivers: Brightness (63), Contrast (44), Color Accuracy (38), Image Processing (30)
- Differentiator: Upscaling & Image Processing (unique strengths)
- Top Negative: Motion Smoothing (2)

**TCL (79.5% Positive)**
- Hero Products: QM8K / QM6K
- Top Positive Drivers: Brightness (142), Value (91), Mini-LED (77), Contrast (75)
- Differentiator: Value messaging dominates positioning
- Top Negative: Off-axis Viewing (1)

**Hisense (72.3% Positive)**
- Hero Products: U8N / U8 Series
- Top Positive Drivers: Brightness (88), Value (65), Mini-LED (50), Contrast (37)
- Differentiator: Budget-friendly positioning with premium features
- Top Negative: Viewing Angles (2)

**Visualizations:**
1. 4-column grid with brand cards for LG, Sony, TCL, Hisense
2. Each card shows: brand color header, sentiment %, hero products, top 4 positive drivers, differentiator, top negative

**Key Insights (displayed on slide):**

1. **Brightness is Universal #1 Driver**
   - All 4 competitors have "brightness" as their top positive driver
   - Samsung leads with 338 mentions - brightness messaging is working

2. **TCL & Hisense Own "Value" Messaging**
   - "Value" appears in top 5 for TCL (91) and Hisense (65) but NOT for LG, Sony, or Samsung
   - Budget positioning is effective in AI responses

3. **Sony Differentiates on Processing**
   - Sony is the only brand with "image processing" and "upscaling" in top 5
   - Samsung can counter with Vision AI messaging

**Methodology Notes:**
- Sentiment % from `semrush_concept_mentions_by_tag` (10 TV categories)
- Concept drivers from `semrush_concept_prompts`
- Competitors have fewer negative mentions (67 combined vs Samsung's 134) due to lower overall visibility
- Single day snapshot: January 31, 2026

---

### 9. Reporting Methodology - Data Sources & KPI Definitions

**File Path:** `clients/samsung/slides/tv_ai_visibility/methodology.html`

**Date Created:** 2026-02-04

**Purpose:**
Executive-friendly overview slide explaining the data sources, KPIs, and definitions used throughout the TV AI Visibility presentation.

**Data Sources Explained:**

#### 1. SEMrush AI Visibility Platform
- **What it measures:** Brand mentions, citations, and sentiment in AI-generated responses
- **AI Models Tracked:** ChatGPT, Google AI Overview, Google AI Mode

**SEMrush KPIs:**
| KPI | Definition |
|-----|------------|
| Mentions | Number of times a brand is named in AI responses |
| Share of Voice (SOV) | Samsung's % of total brand mentions vs competitors |
| Citations | URLs the AI uses as sources in its answers |
| Citation Share | What % of source links point to samsung.com vs competitors |
| Sentiment | Positive, neutral, or negative tone of brand mentions |

#### 2. Adobe Analytics
- **What it measures:** Traffic and revenue from AI platform referrals
- **Platforms Tracked:** ChatGPT, Gemini, Perplexity, Copilot

**Adobe Analytics KPIs:**
| KPI | Definition |
|-----|------------|
| Organic Visits | Baseline traffic from search engines (includes Google AIO & AI Mode) |
| GenAI Visits | Incremental traffic from AI platforms with identifiable referrers |
| CVR (Conversion Rate) | % of visitors who made a purchase |
| AOV (Average Order Value) | Average $ spent per order |
| Revenue | Total $ generated from traffic source |

**Reporting Caveats:**
1. SEMrush data is based on 383 tracked prompts across 3 AI surfaces - a representative sample from a larger prompt universe
2. SEMrush and Adobe track different AI platforms - direct comparison between visibility and traffic requires caution
3. Adobe referrer data has gaps - a significant portion of AI-driven traffic cannot be attributed to specific platforms
4. Google AI Overview & AI Mode traffic appears as Organic in Adobe due to referrer limitations

**Methodology Notes:**
- This is a reference slide, not data-driven
- Designed for executive audiences unfamiliar with AI visibility metrics

---

## Slide Index

| # | Slide Name | File Path | Status |
|---|------------|-----------|--------|
| 1 | Share of Voice - AI Concept Mentions | `slides/tv_ai_visibility/sov_mentions.html` | Complete |
| 2 | Platform Breakdown - Mentions by AI Model | `slides/tv_ai_visibility/platform_breakdown.html` | Complete |
| 3 | Citations Analysis - Samsung vs Competitors | `slides/tv_ai_visibility/citations_vs_competitors.html` | Complete |
| 4 | Citation Sources - Domain Type Analysis | `slides/tv_ai_visibility/citation_sources.html` | Complete |
| 5 | Owned Sources Deep Dive - Regional Analysis | `slides/tv_ai_visibility/owned_sources.html` | Complete |
| 6 | Sentiment Overview - Brand Comparison | `slides/tv_ai_visibility/sentiment_overview.html` | Complete |
| 7 | Sentiment Drivers - Positive & Negative | `slides/tv_ai_visibility/sentiment_drivers.html` | Complete |
| 8 | Competitor Sentiment Drivers | `slides/tv_ai_visibility/competitor_sentiment.html` | Complete |
| 9 | Reporting Methodology | `slides/tv_ai_visibility/methodology.html` | Complete |

---

## Template for New Slides

When documenting a new slide, copy this template:

```markdown
### [#]. [Slide Title]

**File Path:** `clients/samsung/slides/tv_ai_visibility/[filename].html`

**Date Created:** [YYYY-MM-DD]

**Data Source:**
- [Table/API name]

**Query Details:**
- **Date:** [Date range]
- **Brands:** [List of brands]
- **AI Models:** [List of models]
- **Tags/Filters:** [List of tags or other filters]

**SQL Query Used:**
[Code block with actual query]

**Key Metrics:**
[Table or list of key numbers]

**Visualizations:**
[List of charts/tables on the slide]

**Key Insights (displayed on slide):**
[Numbered list of insights with supporting data]

**Methodology Notes:**
[Any important context about data aggregation, calculations, or caveats]
```
