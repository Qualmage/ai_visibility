# Samsung Data Definitions

This document defines all metrics, dimensions, and data sources used in Samsung AI visibility reporting.

---

## SEMrush AI Visibility Definitions

### Concepts

**Official Definition (from SEMrush Support):**
Concepts are the specific qualities and features AI models use when describing products and brands. SEMrush analyzes AI answers to understand the different themes and attributes AI is using to evaluate a product.

**Plain English:**
When AI chatbots describe products, they use specific vocabulary - "picture quality," "smart TV features," "gaming mode," etc. Each of these qualities is a Concept. SEMrush tracks which concepts get associated with which brands.

**Examples by Product Type:**
| Product | Example Concepts |
|---------|------------------|
| TV | "picture quality", "OLED technology", "smart TV features", "gaming mode" |
| Mascara | "clump-free application", "volume", "lengthening" |
| SUV | "safety features", "fuel efficiency", "cargo space" |

**Key Detail - Sentiment:**
Each concept-product relationship carries sentiment (positive, neutral, negative), revealing whether AI frames that attribute favorably or unfavorably.

---

### Topics

**Official Definition (from SEMrush Support):**
Topics are used to estimate Volume for prompts. Unlike keywords, individual prompts are often too specific and unique to measure directly. SEMrush calculates topic-level volume by grouping related prompts that move in the same "semantic direction."

**Plain English:**
When someone asks ChatGPT "What is the best 65-inch OLED TV for gaming in 2026?", that exact phrase is too specific to measure. SEMrush groups it with similar questions into a Topic like "Gaming TVs" and estimates volume based on real AI platform usage data.

**How Topic Volume is Estimated:**
1. Third-party data on real user interactions with AI platforms
2. Machine learning models applied to interaction data
3. Topics generated from SEMrush's database of 250+ million prompts
4. Individual prompts associated with topics for volume estimates

---

### Current Data Status

**Table:** `semrush_concept_mentions`

| Metric | Value |
|--------|-------|
| Brands tracked | Samsung, LG, TCL, Sony, Hisense |
| AI models | ChatGPT (search-gpt), Google AI Overview, Google AI Mode |
| Date range | 2025-12-18 to 2026-01-29 (43 days) |
| Total records | ~152,000 |

**Brand Share of Voice:**
| Brand | Share of Voice | Unique Concepts |
|-------|---------------|-----------------|
| Samsung | 44.8% | 12,884 |
| LG | 19.0% | 6,894 |
| TCL | 14.7% | 5,234 |
| Sony | 11.8% | 4,567 |
| Hisense | 9.8% | 3,778 |

**Why Samsung Has Higher Share of Voice:**
Samsung's 44.8% SoV is legitimate - it reflects that AI models discuss Samsung with more product attributes/features than competitors. More concepts = more mentions = higher Share of Voice. This is a signal of content richness, not data bias.

---

## Dashboard KPI Definitions

Share of Voice displays your brand's competitive strength across all tracked prompts. over the last 30 days compared to the previous 30 days. This weighted metric factors in both how often you appear and where you rank in AI responses, with higher positions earning more points. Click the metric to dive deeper in AI Performance Overview.

Source Visibility tracks how frequently AI systems cite your domain as an authoritative source when responding to your tracked prompts. A rising percentage indicates your content is gaining recognition as a trusted reference, while declines suggest competitors may be capturing more citations. Click the metric to dive deeper in Source Analysis.

Referral Traffic quantifies actual visitors arriving at your site from AI platforms over the last full calendar month. This shows real user behavior, with how many people clicked through from AI responses to visit your domain. This number is based on Semrush traffic analysis and clickstream data. Click the metric to dive deeper in Benchmark Intelligence.

AI Visibility provides a market-wide score measuring your brand's presence across all AI-generated answers in Semrush's database, not just your tracked prompts. The score reflects both the frequency and consistency of appearances compared to other brands. Think of it as your overall AI market share indicator. Click the metric to dive deeper in Visibility Overview.

This information is purely pulled from the brand name and domain added to the project setup, and contains pre-defined filters. 



Source Analysis tracks the origins of information that AI models use to generate answers about your brand and products. The report captures which domains and specific URLs are being referenced, how often they appear, and how their visibility evolves over time. This insight reveals the content ecosystem that influences how AI systems present your brand (and your tracked prompts) to users.

The analysis covers:

Domain-level performance across all citations

URL-specific tracking for detailed content insights

Citation type categorization (owned, earned, social)

Competitive citation comparisons

Reddit-specific visibility tracking

Citations by Domain
The top section displays the primary trend visualization.

Citations by Domain shows how often each domain is referenced across your tracked prompts. The trend line chart visualizes the top 100 cited domains over time, with each line representing a different source. This view helps you spot peaks, declines, and shifts in domain visibility, revealing which sources are gaining or losing influence with AI systems.

AI Sources by Type
The pie chart categorizes citations into:

Owned: Your domain and properties

Earned: Sites mentioning your brand, including media publications. 

Social: User-generated content platforms

Other: Additional source types

This breakdown reveals which citation types dominate your AI visibility and where opportunities exist to improve your citation profile.

Detailed Source Analysis
Source Domain Table
The comprehensive table provides detailed metrics for each cited domain:

Domain Name: The source being cited

Citations: Total citations in the selected period

Change: The change in the number of times this domain was cited

Average Position: Where citations typically appear in responses

Prompt Coverage: Number of tracked prompts citing this source

Toggle between Domain and URL views to analyze performance at different granularities. The Prompts view shows which specific questions trigger citations from each source, while the Topic view groups these prompts thematically.

---

## Supabase Data Tables

### `semrush_cited_pages`

Stores all Samsung URLs cited by AI models, fetched from the SEMrush Cited Pages API.

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key (auto-generated) |
| `url` | TEXT | The cited Samsung URL |
| `prompts_count` | INTEGER | Number of AI prompts citing this URL |
| `country` | TEXT | Country filter (default: `us`) |
| `category` | TEXT | Category filter (default: `OWNED_BY_TARGET`) |
| `domain` | TEXT | Domain filter (default: `samsung.com`) |
| `fetched_at` | TIMESTAMPTZ | When the data was fetched |

**Unique constraint:** `(url, country, category)`

**Current data:** 84,856 URLs (US, samsung.com, OWNED_BY_TARGET)

### `semrush_url_prompts`

Stores the prompts that cite each URL, with topic and AI model metadata.

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key (auto-generated) |
| `url` | TEXT | The cited Samsung URL |
| `prompt` | TEXT | The AI prompt text |
| `prompt_hash` | TEXT | Unique prompt identifier |
| `topic` | TEXT | Topic category |
| `llm` | TEXT | AI model (GOOGLE_AI_OVERVIEW, GOOGLE_AI_MODE, etc.) |
| `volume` | INTEGER | Search volume |
| `mentioned_brands_count` | INTEGER | Brands mentioned in response |
| `used_sources_count` | INTEGER | Sources cited in response |
| `serp_id` | TEXT | SERP identifier |
| `country` | TEXT | Country filter (default: `us`) |
| `fetched_at` | TIMESTAMPTZ | When the data was fetched |

**Unique constraint:** `(url, prompt_hash, country)`

**Indexes:** `url`, `prompt_hash`, `topic`, `llm`

---

## SEMrush API Reference

### Cited Pages Endpoint

Returns all URLs from a domain that are cited by AI models, ranked by citation count.

**Element ID:** `9dd09001-1d0e-4d28-b675-53670a2af5b0`

**Endpoint:**
```
POST https://api.semrush.com/apis/v4-raw/external-api/v1/workspaces/{workspace_id}/products/ai/elements/9dd09001-1d0e-4d28-b675-53670a2af5b0
```

**Request Payload:**
```json
{
  "render_data": {
    "statistics": {
      "rowCount": {"col": "*", "func": "count"}
    },
    "pagination": {
      "limit": 1000,
      "offset": 0,
      "sort_columns": ["prompts_count desc"]
    },
    "filters": {
      "simple": {
        "competitor_domains": ["samsung.com"]
      },
      "advanced": {
        "op": "and",
        "filters": [
          {"op": "eq", "val": "us", "col": "CBF_country"},
          {"op": "eq", "val": "OWNED_BY_TARGET", "col": "CBF_category"},
          {"op": "eq", "val": " ", "col": "CBF_model"}
        ]
      }
    }
  }
}
```

**Response:**
```json
{
  "blocks": {
    "data": [
      {"prompts_count": 1155, "url": "https://www.samsung.com/us/support/..."}
    ],
    "data_statistics": [
      {"executionTimeMs": 15, "rowCount": 84856}
    ]
  }
}
```

**Filter Options:**

| Filter | Column | Values |
|--------|--------|--------|
| Country | `CBF_country` | `us`, `uk`, `de`, etc. |
| Category | `CBF_category` | `OWNED_BY_TARGET`, `COMPETITOR`, `OTHER` |
| AI Model | `CBF_model` | `" "` (all), `search-gpt`, `perplexity`, `gemini`, `copilot` |
| Domain | `competitor_domains` | Array: `["samsung.com"]` |

**Scripts:**
- `fetch_cited_pages.py` - Fetches from SEMrush API → `data/cited_pages.json`
- `load_cited_pages.py` - Loads JSON → Supabase

See `semrush-api-endpoints.md` for full API documentation.

---

### `semrush_concept_mentions`

Stores daily concept mention data with sentiment breakdown, fetched from the SEMrush Concept Mentions API.

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key (auto-generated) |
| `date` | DATE | The date of the snapshot |
| `concept` | TEXT | The concept name (e.g., "picture quality") |
| `concept_category` | TEXT | Category (e.g., "display") |
| `concept_subcategory` | TEXT | Subcategory (e.g., "visual performance") |
| `mentions` | INTEGER | Number of mentions for this date |
| `sentiment_positive` | INTEGER | Positive sentiment count |
| `sentiment_negative` | INTEGER | Negative sentiment count |
| `sentiment_neutral` | INTEGER | Neutral sentiment count |
| `products` | TEXT[] | Array of products associated with this concept |
| `model` | TEXT | AI model (search-gpt, google-ai-overview, google-ai-mode) |
| `brand` | TEXT | Brand filter (default: `Samsung`) |
| `fetched_at` | TIMESTAMPTZ | When the data was fetched |

**Unique constraint:** `(date, concept, model, brand)`

**Indexes:** `date`, `concept`, `model`, `concept_category`

**Data availability:** 2025-12-18 to present (~43 days × 3 models × ~150 concepts = ~19,350 rows)

**Scripts:**
- `fetch_concept_mentions.py` - Fetches daily data → `data/concept_mentions.json`
- `load_concept_mentions.py` - Loads JSON → Supabase

### Concept Parsing

The API returns concepts in format `category__subcategory__concept`. The fetcher script parses this:
- `display__visual performance__picture quality` → category: `display`, subcategory: `visual performance`, concept: `picture quality`
- `battery life` → category: null, subcategory: null, concept: `battery life`

### Example Queries

```sql
-- Row count by model
SELECT model, COUNT(*) FROM semrush_concept_mentions GROUP BY model;

-- Trend for "picture quality" over time
SELECT date, model, mentions, sentiment_positive, sentiment_negative
FROM semrush_concept_mentions
WHERE concept = 'picture quality'
ORDER BY date, model;

-- Top growing concepts (latest vs earliest)
WITH latest AS (
  SELECT concept, model, mentions FROM semrush_concept_mentions WHERE date = '2026-01-29'
),
earliest AS (
  SELECT concept, model, mentions FROM semrush_concept_mentions WHERE date = '2025-12-18'
)
SELECT l.concept, l.model, e.mentions as start_mentions, l.mentions as end_mentions,
       l.mentions - e.mentions as growth
FROM latest l
JOIN earliest e ON l.concept = e.concept AND l.model = e.model
ORDER BY growth DESC
LIMIT 20;
```