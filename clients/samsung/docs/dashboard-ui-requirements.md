# Samsung Dashboard UI Requirements

Derived from querying actual data and reverse-engineering what UI components are needed to answer the demo questions.

---

## IMPORTANT: Understanding the Metrics

The data model has a many-to-many relationship that can cause confusion:

### Data Structure
- **Prompts**: ~383 unique questions (e.g., "What are the best gaming TVs?")
- **URLs**: ~70K unique source URLs cited across all prompts
- **Concepts**: ~12K unique concepts with sentiment (e.g., "HDR performance" = positive)

### What Each Metric Means

| Metric | Definition | Example |
|--------|------------|---------|
| **unique_urls** | Distinct source URLs from a domain | RTINGS has 2,344 unique URLs cited |
| **unique_prompts** | Prompts that cite this domain with this sentiment | 358 prompts cite RTINGS with positive sentiment |
| **unique_concepts** | Distinct concepts mentioned in those prompts | 7,949 concepts in RTINGS-citing prompts |
| **total_mentions** | = unique_prompts (the meaningful unit) | Use this for charts/comparisons |

### Why "Prompts" is the Right Unit
- A prompt represents one user question answered by an LLM
- The sentiment comes from how the LLM responded, not from individual URLs
- Counting joined rows would inflate numbers by 100-1000x (cartesian product)

### Sample Corrected Data

| Domain | Type | URLs | Positive Prompts | Negative Prompts |
|--------|------|------|------------------|------------------|
| www.samsung.com | Owned | 3,307 | 340 | 172 |
| www.rtings.com | Other | 2,344 | 358 | 173 |
| www.bestbuy.com | Competitor | 2,168 | 262 | 130 |
| www.techradar.com | Earned | 1,834 | 353 | 170 |
| www.tomsguide.com | Earned | 1,361 | 347 | 167 |

---

## Data Dimensions Available

| Dimension | Values | Source |
|-----------|--------|--------|
| **Domain** | 12 key domains | `summary_domain_sentiment` |
| **Domain Type** | Owned, Earned, Benchmark Competitors, Other | `vw_domain_type_sentiment` |
| **Sentiment** | positive, neutral, negative | All views |
| **Tag Category** | TV Features, TV Models, TV Reviews & Brand, TV Sizes | `vw_prompt_tags_expanded` |
| **Tag Name** | 39 specific tags (Gaming TVs, OLED, etc.) | `vw_tag_sentiment` |
| **Concept** | 1000s of concepts (HDR, input lag, etc.) | `vw_sentiment_quotes` |
| **Product** | S95F, Neo QLED, The Frame, etc. | `vw_prompt_url_sentiment` |
| **Brand** | Samsung (primary), competitors | `vw_prompt_url_sentiment` |

---

## 1. Filter Components Required

### Primary Filters (Always Visible)

| Filter | Type | Options | Data Source |
|--------|------|---------|-------------|
| **Domain** | Multi-select dropdown | 12 domains | `SELECT DISTINCT domain FROM summary_domain_sentiment` |
| **Domain Type** | Checkbox group | Owned, Earned, Competitor, Other | `SELECT DISTINCT domain_type FROM summary_domain_sentiment` |
| **Sentiment** | Toggle/chips | Positive, Neutral, Negative, All | Hardcoded |
| **Date Range** | Date picker | Start/End date | `date` column in base tables |

### Secondary Filters (Collapsible/Advanced)

| Filter | Type | Options | Data Source |
|--------|------|---------|-------------|
| **Tag Category** | Dropdown | TV Features, TV Models, etc. | `SELECT DISTINCT tag_category FROM vw_prompt_tags_expanded` |
| **Tag Name** | Dependent dropdown | Changes based on category | `SELECT DISTINCT tag_name WHERE tag_category = ?` |
| **Concept** | Searchable autocomplete | 1000s of values | `SELECT DISTINCT concept FROM vw_sentiment_quotes LIMIT 100` |
| **Product** | Searchable autocomplete | Product names | `SELECT DISTINCT product FROM vw_prompt_url_sentiment` |

### Filter Dependencies
```
Tag Category → Tag Name (tag dropdown updates when category changes)
Domain Type → Domain (domain dropdown filters when type selected)
```

---

## 2. KPI Cards (Top Summary)

Display high-level metrics that update based on filters.

| KPI | Definition | Query | Example Value |
|-----|------------|-------|---------------|
| **Total Prompts** | Prompts citing selected domains | `SUM(unique_prompts)` | ~1,500 |
| **Positive %** | % prompts with positive sentiment | `positive / total * 100` | ~75% |
| **Negative %** | % prompts with negative sentiment | `negative / total * 100` | ~10% |
| **Unique URLs** | Distinct source URLs | `SUM(unique_urls)` | ~15,000 |
| **Unique Concepts** | Distinct concepts mentioned | `COUNT(DISTINCT concept)` | ~12,000 |
| **Domains Covered** | Number of domains | `COUNT(DISTINCT domain)` | 12 |

**Note:** Use `unique_prompts` as the primary "mentions" metric, not row counts.

---

## 3. Chart Components Required

### 3.1 Sentiment Distribution (Primary)
- **Type:** Donut or stacked bar chart
- **Data:** Positive/Neutral/Negative split (by prompt count)
- **Interaction:** Click segment to filter dashboard
- **Query:**
```sql
SELECT sentiment, SUM(unique_prompts) as prompt_count
FROM vw_domain_sentiment
WHERE domain IN (selected_domains)
GROUP BY sentiment
```
- **Note:** Use `unique_prompts` not `total_mentions` to avoid inflated counts

### 3.2 Domain Comparison Chart
- **Type:** Grouped bar chart or heatmap
- **Data:** Sentiment by domain (prompt counts)
- **Interaction:** Click bar to drill into domain
- **Query:**
```sql
SELECT domain, sentiment, unique_prompts as prompt_count, unique_urls
FROM vw_domain_sentiment
WHERE domain IN (selected_domains)
ORDER BY unique_urls DESC, sentiment
```

### 3.3 Domain Type Breakdown
- **Type:** Stacked bar or treemap
- **Data:** Owned vs Earned vs Competitor
- **Interaction:** Click to filter by type
- **Query:**
```sql
SELECT domain_type, sentiment, total_mentions
FROM vw_domain_type_sentiment
ORDER BY total_mentions DESC
```

### 3.4 Tag/Topic Sentiment
- **Type:** Horizontal bar chart
- **Data:** Sentiment by tag
- **Interaction:** Click tag to see details
- **Query:**
```sql
SELECT tag_name, sentiment, total_mentions
FROM vw_tag_sentiment
WHERE tag_name IS NOT NULL
ORDER BY total_mentions DESC LIMIT 15
```

### 3.5 Concept Cloud or Bar Chart
- **Type:** Word cloud or bar chart
- **Data:** Top concepts by frequency
- **Interaction:** Click concept to see quotes
- **Query:**
```sql
SELECT concept, COUNT(*) as mentions
FROM vw_sentiment_quotes
WHERE sentiment = 'negative'
GROUP BY concept
ORDER BY mentions DESC LIMIT 20
```

### 3.6 Time Series (if date filtering needed)
- **Type:** Line chart
- **Data:** Mentions over time by sentiment
- **Interaction:** Brush to select date range
- **Query:**
```sql
SELECT date, sentiment, COUNT(*) as mentions
FROM vw_prompt_url_sentiment
GROUP BY date, sentiment
ORDER BY date
```

---

## 4. Table Components Required

### 4.1 Quote Browser (PR Action Items)
**Purpose:** Review actual quotes for response/action

| Column | Width | Sortable | Filterable |
|--------|-------|----------|------------|
| Domain | 150px | Yes | Yes (dropdown) |
| Concept | 150px | Yes | Yes (search) |
| Sentiment | 80px | Yes | Yes (chips) |
| Quote | Flexible | No | Yes (search) |
| Date | 100px | Yes | Yes (range) |
| Source URL | 200px | No | No |

**Query:**
```sql
SELECT domain, concept, sentiment, quote, date, source_url
FROM vw_sentiment_quotes
WHERE sentiment = 'negative' AND domain = ?
ORDER BY date DESC
LIMIT 50
```

**Features Needed:**
- Pagination (50 per page)
- Export to CSV
- Copy quote button
- Link to source URL
- Expandable rows for long quotes

### 4.2 Domain Summary Table
**Purpose:** Compare metrics across domains

| Column | Description | Sortable |
|--------|-------------|----------|
| Domain | Source domain name | Yes |
| Domain Type | Owned/Earned/Competitor/Other | Yes |
| Unique URLs | Distinct URLs from this domain | Yes |
| Positive Prompts | Prompts with positive sentiment | Yes |
| Neutral Prompts | Prompts with neutral sentiment | Yes |
| Negative Prompts | Prompts with negative sentiment | Yes |
| Negative % | Negative / Total prompts | Yes |

**Query:**
```sql
SELECT
  domain,
  domain_type,
  MAX(unique_urls) as unique_urls,
  SUM(CASE WHEN sentiment = 'positive' THEN unique_prompts ELSE 0 END) as positive,
  SUM(CASE WHEN sentiment = 'neutral' THEN unique_prompts ELSE 0 END) as neutral,
  SUM(CASE WHEN sentiment = 'negative' THEN unique_prompts ELSE 0 END) as negative
FROM vw_domain_sentiment
GROUP BY domain, domain_type
ORDER BY unique_urls DESC
```

### 4.3 Product Leaderboard
**Purpose:** See which products get most coverage

| Column | Sortable |
|--------|----------|
| Product | Yes |
| Positive | Yes |
| Neutral | Yes |
| Negative | Yes |
| Total | Yes |

---

## 5. Drill-Down Paths

Users need to navigate from high-level to specific:

```
Overview (all data)
    ↓ Click domain
Domain Detail (single domain metrics)
    ↓ Click sentiment
Sentiment Detail (quotes for that sentiment)
    ↓ Click quote
Source URL (external link)
```

```
Tag Overview (all tags)
    ↓ Click tag
Tag Detail (sentiment + domains for tag)
    ↓ Click domain
Tag + Domain quotes
```

```
Concept Cloud
    ↓ Click concept
Concept quotes across all domains
    ↓ Filter by domain
Concept quotes for specific domain
```

---

## 6. Page/View Structure

### View 1: Overview Dashboard
- KPI cards (top)
- Sentiment donut (left)
- Domain comparison chart (right)
- Domain type breakdown (bottom left)
- Top tags chart (bottom right)

### View 2: Domain Deep Dive
- Domain selector (top)
- Domain KPIs
- Sentiment breakdown for selected domain
- Top concepts for domain
- Quote table filtered to domain

### View 3: Topic Analysis
- Tag category/name filters
- Sentiment by tag chart
- Domain coverage for selected tag
- Quotes filtered by tag

### View 4: PR Action Center
- Pre-filtered to negative sentiment
- Quote browser with all filters
- Concept frequency chart (negative only)
- Export functionality

### View 5: Competitive Analysis
- Side-by-side domain comparison
- Domain type filters (Competitor vs Owned vs Earned)
- Concept overlap analysis

---

## 7. Interaction Patterns

### Cross-Filtering
When user clicks on any chart element:
1. Update all other charts to reflect that filter
2. Show active filter as chip/badge
3. Allow clearing individual filters

### Drill-Through
When user clicks on aggregated data:
1. Navigate to detail view with context preserved
2. Show breadcrumb for navigation back
3. Pre-populate filters based on click context

### Export
- Individual charts: PNG/SVG
- Tables: CSV/Excel
- Full dashboard: PDF report

---

## 8. Data Refresh Strategy

| Data Type | Refresh Frequency | Method |
|-----------|-------------------|--------|
| Summary tables | Daily | `SELECT refresh_all_summaries()` |
| Real-time quotes | On-demand | Direct view query |
| Tag aggregations | Daily | Scheduled job |

---

## 9. Performance Considerations

### Use Summary Tables For:
- Domain sentiment breakdown (instant)
- Domain type breakdown (instant)
- Any aggregated metrics

### Use Views With Filters For:
- Quote browsing (WHERE clause required)
- Tag sentiment (filter by tag_name)
- Concept lists (LIMIT required)

### Avoid:
- Full table scans on `vw_sentiment_quotes` without WHERE
- Aggregations across all tags without category filter
- Queries without LIMIT on concept/quote tables

---

## 10. Sample Dashboard Queries

### Overview Page Load
```sql
-- KPIs (from summary) - use unique_prompts as the count
SELECT
  SUM(unique_prompts) as total_prompts,
  SUM(unique_urls) as total_urls,
  SUM(CASE WHEN sentiment = 'positive' THEN unique_prompts ELSE 0 END) as positive_prompts,
  SUM(CASE WHEN sentiment = 'negative' THEN unique_prompts ELSE 0 END) as negative_prompts
FROM summary_domain_sentiment;

-- Domain comparison (sorted by URL count, the measure of domain prominence)
SELECT domain, domain_type, sentiment, unique_urls, unique_prompts, unique_concepts
FROM summary_domain_sentiment
ORDER BY unique_urls DESC, domain, sentiment;

-- Domain type breakdown
SELECT domain_type, sentiment, unique_prompts, unique_concepts
FROM vw_domain_type_sentiment
ORDER BY unique_prompts DESC;
```

### Domain Detail Page
```sql
-- Domain metrics
SELECT * FROM vw_domain_sentiment WHERE domain = ?;

-- Top negative concepts for domain
SELECT concept, COUNT(*) as cnt
FROM vw_sentiment_quotes
WHERE domain = ? AND sentiment = 'negative'
GROUP BY concept
ORDER BY cnt DESC LIMIT 10;

-- Recent negative quotes
SELECT concept, quote, date
FROM vw_sentiment_quotes
WHERE domain = ? AND sentiment = 'negative'
ORDER BY date DESC LIMIT 20;
```

### Tag Analysis Page
```sql
-- Tag sentiment
SELECT * FROM vw_tag_sentiment WHERE tag_name = ?;

-- Tag + domain breakdown
SELECT domain, sentiment, total_mentions
FROM vw_tag_domain_sentiment
WHERE tag_name = ?
ORDER BY total_mentions DESC;
```

---

## 11. Mobile Responsiveness

| Component | Desktop | Tablet | Mobile |
|-----------|---------|--------|--------|
| Filters | Sidebar | Collapsible | Bottom sheet |
| Charts | Side by side | Stacked | Stacked |
| Tables | Full width | Horizontal scroll | Card view |
| KPIs | Row of 6 | 2 rows of 3 | 3 rows of 2 |
