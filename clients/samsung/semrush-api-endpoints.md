# Semrush Enterprise API Endpoints

This document contains all captured API endpoints for Samsung from the Semrush Enterprise dashboard.

## API Configuration

| Setting | Value |
|---------|-------|
| Base URL | `https://api.semrush.com/apis/v4-raw/external-api/v1` |
| Workspace ID | `a22caad0-2a96-4174-9e2f-59f1542f156b` |
| Authorization | `Apikey {SEMRUSH_API_KEY}` |
| Content-Type | `application/json` |

## Project IDs

| Product | Project ID |
|---------|------------|
| AI Overview (AIO) | `b7880549-ea08-4d82-81d0-9633f4dcab58` |
| SEO | `f793bec8-7306-459d-aefc-0575e63d929b` |

## API Endpoint Pattern

```
POST {BASE_URL}/workspaces/{workspaceId}/products/{product}/elements/{elementId}
```

## AI Overview Page Endpoints

| Element Name | Element ID | Product |
|-------------|------------|---------|
| Source Visibility | `81d48bce-e04e-43ad-996d-ab4e4a52ce45` | ai |
| AI Visibility Table | `1b75cb07-b293-4509-9c71-89619b117260` | ai |
| Prompt Tracking Rankings | `b4afea7a-46fd-465f-bb58-4e193b57c569` | ai |
| Referral Traffic Table | `e8f701c8-942c-4f26-8c06-cfbbaf985409` | ai |
| Prompt Tracking Citations | `72fa48ad-56f7-42e8-85b4-0b5f0e99c16f` | ai |
| **Cited Pages (URLs)** | `9dd09001-1d0e-4d28-b675-53670a2af5b0` | ai |
| **URL Prompts** | `777346b4-6777-40fe-9356-4a5d63a70ef8` | ai |
| **Citations by Model** | `c57c36a4-cb53-49c3-bbe6-6467881206e3` | ai |
| **Source Visibility by Domain** | `28977430-d565-4529-97eb-2dfe2959b86b` | ai |
| **Cited URLs with Prompts** | `3c29aa85-4f06-4f14-a376-b02333c6e3fa` | ai |
| **Topics with Citations** | `3a16b2b2-b227-4a41-9ef2-9c657e64d47e` | ai |
| **Concept to Prompts Mapping** | `6c914007-60fd-4105-911a-9fb8861be2ec` | ai |
| **Prompt to URLs (Daily)** | `c0cffe83-8104-4cfb-afac-9b1db673d29e` | ai |

## SEO Page Endpoints

| Element Name | Element ID | Product |
|-------------|------------|---------|
| Share of Voice Table | `5d6024b9-fadb-4c36-9e3f-e01b49a4f89b` | seo |
| Share of Voice Chart | `184a8d65-2248-4030-86e2-288340667f87` | seo |

## Request Payload Example

```json
{
  "render_data": {
    "filters": {
      "simple": {
        "start_date": "2025-12-16",
        "end_date": "2026-01-14"
      }
    }
  }
}
```

## Example API Call

```python
import requests

BASE_URL = "https://api.semrush.com/apis/v4-raw/external-api/v1"
WORKSPACE_ID = "a22caad0-2a96-4174-9e2f-59f1542f156b"
API_KEY = "your_api_key_here"

def get_element_data(product: str, element_id: str, start_date: str, end_date: str):
    """Fetch data from a Semrush Enterprise element."""
    url = f"{BASE_URL}/workspaces/{WORKSPACE_ID}/products/{product}/elements/{element_id}"

    headers = {
        "accept": "application/json",
        "Authorization": f"Apikey {API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "render_data": {
            "filters": {
                "simple": {
                    "start_date": start_date,
                    "end_date": end_date
                }
            }
        }
    }

    response = requests.post(url, headers=headers, json=payload)
    return response.json()

# Example: Get AI Visibility data
ai_visibility = get_element_data(
    product="ai",
    element_id="1b75cb07-b293-4509-9c71-89619b117260",
    start_date="2025-12-16",
    end_date="2026-01-14"
)
```

## Cited Pages Endpoint Details

The Cited Pages endpoint returns all URLs from a domain that are cited by AI models.

### Request Payload

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

### Response Structure

```json
{
  "blocks": {
    "data": [
      {"prompts_count": 1155, "url": "https://www.samsung.com/us/support/answer/ANS10001896/"},
      {"prompts_count": 934, "url": "https://www.samsung.com/us/support/answer/ANS10002500/"}
    ],
    "data_statistics": [
      {"executionTimeMs": 15, "rowCount": 84856}
    ]
  }
}
```

### Filter Options

| Filter Column | Values | Description |
|---------------|--------|-------------|
| `CBF_country` | `us`, `uk`, etc. | Country filter |
| `CBF_category` | `OWNED_BY_TARGET`, `COMPETITOR`, `OTHER` | Domain ownership category |
| `CBF_model` | `" "` (space), `search-gpt`, `perplexity`, etc. | AI model filter (space = all) |
| `competitor_domains` | Array of domains | Domain to query |

### Data Fields

| Field | Type | Description |
|-------|------|-------------|
| `url` | string | The cited URL |
| `prompts_count` | integer | Number of AI prompts citing this URL |

### Scripts

- `fetch_cited_pages.py` - Fetches all data from API → `data/cited_pages.json`
- `load_cited_pages.py` - Loads JSON into Supabase `semrush_cited_pages` table

---

## URL Prompts Endpoint Details

Returns all prompts that cite a specific URL.

### Request Payload

```json
{
  "render_data": {
    "pagination": {"limit": 1000, "offset": 0},
    "filters": {
      "simple": {
        "competitor_domains": ["samsung.com"],
        "url": "https://www.samsung.com/us/support/answer/ANS10001896/"
      },
      "advanced": {
        "op": "and",
        "filters": [
          {"op": "eq", "val": "us", "col": "CBF_country"},
          {"op": "eq", "val": " ", "col": "CBF_model"},
          {"op": "eq", "val": "MENTIONS_TARGET", "col": "CBF_category"}
        ]
      }
    }
  }
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `prompt` | string | The AI prompt text |
| `prompt_hash` | string | Unique prompt identifier |
| `topic` | string | Topic category |
| `llm` | string | AI model (GOOGLE_AI_OVERVIEW, GOOGLE_AI_MODE, etc.) |
| `volume` | integer | Search volume |
| `mentioned_brands_count` | integer | Number of brands mentioned in response |
| `used_sources_count` | integer | Number of sources cited in response |
| `serp_id` | string | SERP identifier |

### Scripts

- `fetch_url_prompts.py` - Fetches prompts for each URL → `data/url_prompts/*.json`
- `load_url_prompts.py` - Loads JSON into Supabase `semrush_url_prompts` table

---

## Citations by Model Endpoint Details

Returns citation counts broken down by AI model over time.

### Endpoint Information

| Parameter | Value |
|-----------|-------|
| Element ID | `c57c36a4-cb53-49c3-bbe6-6467881206e3` |
| Product | `ai` |
| Element Name | Citations by Model |

### Request Payload

```json
{
  "render_data": {
    "filters": {
      "simple": {
        "competitor_domains": ["samsung.com"]
      },
      "advanced": {
        "op": "and",
        "filters": [
          {"op": "eq", "val": "us", "col": "CBF_country"},
          {"op": "eq", "val": "2025-12-31", "col": "date"}
        ]
      }
    }
  }
}
```

### Response Structure

Returns 20 rows (4 time points x 5 AI models):

```json
{
  "blocks": {
    "data": [
      {"bar": "UNSPECIFIED", "value": 398339},
      {"bar": "GOOGLE_AI_OVERVIEW", "value": 167121},
      {"bar": "GEMINI", "value": 86641},
      {"bar": "CHAT_GPT", "value": 73616},
      {"bar": "GOOGLE_AI_MODE", "value": 70961}
    ]
  }
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `bar` | string | AI model name (see Model Values below) |
| `value` | integer | Citation count for that model at that time point |

### Model Values

| Model Name | Description |
|------------|-------------|
| `UNSPECIFIED` | Citations from unidentified AI sources |
| `GOOGLE_AI_OVERVIEW` | Google AI Overview (search results) |
| `GEMINI` | Google Gemini |
| `CHAT_GPT` | OpenAI ChatGPT |
| `GOOGLE_AI_MODE` | Google AI Mode |

### Important: Date Filter Behavior

**The `date` filter has NO effect on the response.** Testing confirmed:
- Tested with dates: 2025-11-30, 2025-12-15, 2025-12-31
- All dates return identical data
- API always returns the same 4 historical time points regardless of date passed

This means the endpoint returns a fixed time series snapshot, not date-filtered data.

### Sample Data (Latest Time Point)

| Model | Citation Count |
|-------|----------------|
| UNSPECIFIED | 398,339 |
| GOOGLE_AI_OVERVIEW | 167,121 |
| GEMINI | 86,641 |
| CHAT_GPT | 73,616 |
| GOOGLE_AI_MODE | 70,961 |

### Time Series Observations

The 4 time points show trends over time:
- **GEMINI:** Only appears at time point 3+ (was 0 before) - indicates recent addition
- **CHAT_GPT:** Citations are decreasing over time
- **UNSPECIFIED & Google models:** Citations are increasing over time

### Plain English

This endpoint shows how many times Samsung content is cited by different AI chatbots. The "UNSPECIFIED" category is largest because many AI citations cannot be attributed to a specific model. Google's products (AI Overview, Gemini, AI Mode) combined account for more citations than ChatGPT alone. The trend data shows Google AI presence is growing while ChatGPT citations are declining.

---

## Concept Mentions Endpoint Details

Returns daily concept mentions with sentiment breakdown, filtered by AI model and brand.

### Endpoint Information

| Parameter | Value |
|-----------|-------|
| Element ID | `0ed4bc52-b684-41b5-9436-3f5806266631` |
| Product | `ai` |
| Project ID | `b7880549-ea08-4d82-81d0-9633f4dcab58` |
| Element Name | Concept Mentions |

### Request Payload

```json
{
  "render_data": {
    "project_id": "b7880549-ea08-4d82-81d0-9633f4dcab58",
    "filters": {
      "simple": {
        "start_date": "2025-12-31",
        "end_date": "2025-12-31"
      },
      "advanced": {
        "op": "and",
        "filters": [
          {"op": "eq", "val": "Samsung", "col": "CBF_brand"},
          {"op": "eq", "val": "search-gpt", "col": "CBF_model"}
        ]
      }
    }
  }
}
```

### Response Structure

```json
{
  "blocks": {
    "data": [
      {
        "concept": "display__visual performance__picture quality",
        "mentions_end": 145,
        "sentiment_positive": 89,
        "sentiment_negative": 12,
        "sentiment_neutral": 44,
        "products": ["Galaxy S24", "QLED TV"]
      }
    ]
  }
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `concept` | string | Concept with category/subcategory prefix (parsed on `__`) |
| `mentions_end` | integer | Number of mentions for the date |
| `sentiment_positive` | integer | Positive sentiment count |
| `sentiment_negative` | integer | Negative sentiment count |
| `sentiment_neutral` | integer | Neutral sentiment count |
| `products` | array | Products associated with this concept |

### Filter Options

| Filter | Column | Values |
|--------|--------|--------|
| Brand | `CBF_brand` | `Samsung` |
| AI Model | `CBF_model` | `search-gpt`, `google-ai-overview`, `google-ai-mode` |
| Date | `start_date`, `end_date` | `YYYY-MM-DD` format (use same date for daily snapshot) |

### Data Availability

- **Start date:** 2025-12-18 (first day with data)
- **Concepts per day:** ~120-180 per model
- **Total models:** 3 (search-gpt, google-ai-overview, google-ai-mode)

### Scripts

- `fetch_concept_mentions.py` - Fetches daily data → `data/concept_mentions.json`
- `load_concept_mentions.py` - Loads JSON → Supabase `semrush_concept_mentions`

---

## Source Visibility by Domain Endpoint Details

Returns domain-level citation and visibility metrics. **Used by GEO Dashboard Citation Sources table.**

### Endpoint Information

| Parameter | Value |
|-----------|-------|
| Element ID | `28977430-d565-4529-97eb-2dfe2959b86b` |
| Product | `ai` |
| Element Name | Source Visibility by Domain |

### Request Payload

```json
{
  "render_data": {
    "project_id": "b7880549-ea08-4d82-81d0-9633f4dcab58",
    "filters": {
      "simple": {
        "start_date": "2026-01-29",
        "end_date": "2026-01-29"
      },
      "advanced": {
        "op": "and",
        "filters": [
          {"op": "eq", "val": "search-gpt", "col": "CBF_model"}
        ]
      }
    }
  }
}
```

**Note:** Omit the `advanced.filters` array to get data for all models combined.

### Response Structure

```json
{
  "blocks": {
    "data": [
      {
        "domain": "samsung.com",
        "domain_type": "Owned",
        "mentions_end": 1123,
        "mentions_start": 1123,
        "prompts_with_citations": 446,
        "total_prompts": 1055,
        "urls_count": 671,
        "visibility": 0.4227
      }
    ]
  }
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `domain` | string | The domain name |
| `domain_type` | string | Classification: Owned, Earned, Benchmark Competitors, Other |
| `mentions_end` | integer | Number of mentions |
| `prompts_with_citations` | integer | Number of prompts citing this domain |
| `total_prompts` | integer | Total prompts tracked |
| `urls_count` | integer | Number of unique URLs cited from this domain |
| `visibility` | float | Visibility score (0-1, multiply by 100 for percentage) |

### Domain Type Values

| Type | Description |
|------|-------------|
| `Owned` | Target brand's own domain (samsung.com) |
| `Earned` | Media/review sites (techradar.com, cnet.com) |
| `Benchmark Competitors` | Competitor domains (bestbuy.com, lg.com) |
| `Other` | All other domains |

### Supabase Edge Function Proxy

This endpoint is accessed via the `semrush-proxy` Edge Function to avoid CORS issues:

```javascript
const response = await fetch('https://zozzhptqoclvbfysmopg.supabase.co/functions/v1/semrush-proxy', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        element_id: '28977430-d565-4529-97eb-2dfe2959b86b',
        filters: {
            simple: { start_date: '2026-01-29', end_date: '2026-01-29' }
        }
    })
});
```

---

## Cited URLs with Prompts Endpoint Details

Returns individual URLs with the prompts that cite them.

### Endpoint Information

| Parameter | Value |
|-----------|-------|
| Element ID | `3c29aa85-4f06-4f14-a376-b02333c6e3fa` |
| Product | `ai` |
| Element Name | Cited URLs with Prompts |

### Response Structure

```json
{
  "blocks": {
    "data": [
      {
        "domain_type": "Earned",
        "mentions_end": 2,
        "position_end": 9,
        "prompts": ["What is the best 75-inch TV?", "75 inch tv reviews"],
        "prompts_with_citation": 2,
        "source": "https://9meters.com/technology/tv/best-75-inch-tvs-2025",
        "total_responses": 34
      }
    ]
  }
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `source` | string | The cited URL |
| `domain_type` | string | Domain classification |
| `mentions_end` | integer | Number of mentions |
| `position_end` | float | Average citation position |
| `prompts` | array | List of prompts that cite this URL |
| `prompts_with_citation` | integer | Number of prompts citing this URL |
| `total_responses` | integer | Total AI responses tracked |

---

## Topics with Citations Endpoint Details

Returns topic-level aggregation with citation counts and associated prompts.

### Endpoint Information

| Parameter | Value |
|-----------|-------|
| Element ID | `3a16b2b2-b227-4a41-9ef2-9c657e64d47e` |
| Product | `ai` |
| Element Name | Topics with Citations |

### Response Structure

```json
{
  "blocks": {
    "data": [
      {
        "topic_name": "75 Inch TV Comparisons and Reviews",
        "topic_volume": 1750,
        "prompt_count": 4,
        "prompts": "What is the best 75-inch TV?,75 inch TV vs 85 inch TV,...",
        "citations_total": 122,
        "domain_count": 41,
        "url_count": 56
      }
    ]
  }
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `topic_name` | string | The topic/category name |
| `topic_volume` | integer | Search volume for this topic |
| `prompt_count` | integer | Number of prompts in this topic |
| `prompts` | string | Comma-separated list of prompts |
| `citations_total` | integer | Total citations across all prompts |
| `domain_count` | integer | Number of unique domains cited |
| `url_count` | integer | Number of unique URLs cited |

---

## Concept to Prompts Mapping Endpoint Details

Returns the relationship between concepts (features/topics) and the AI prompts that mention them, including the actual quote from the AI response. **Data loaded into Supabase `semrush_concept_prompts` table.**

### Endpoint Information

| Parameter | Value |
|-----------|-------|
| Element ID | `6c914007-60fd-4105-911a-9fb8861be2ec` |
| Product | `ai` |
| Element Name | Concept to Prompts Mapping |

### Request Payload

```json
{
  "render_data": {
    "project_id": "b7880549-ea08-4d82-81d0-9633f4dcab58",
    "filters": {
      "simple": {
        "start_date": "2025-12-31",
        "end_date": "2026-01-29"
      },
      "advanced": {
        "op": "and",
        "filters": [
          {"op": "eq", "val": "Samsung", "col": "CBF_brand"}
        ]
      }
    }
  }
}
```

### Response Structure

```json
{
  "blocks": {
    "data": [
      {
        "brand_name": "Samsung",
        "concept": "oled technology",
        "product": "S95F",
        "prompt": "is Mini-LED better than OLED",
        "quote": "The choice between them depends on whether you prioritize...",
        "sentiment": "neutral"
      }
    ]
  }
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `brand_name` | string | The brand (Samsung) |
| `concept` | string | The concept/feature mentioned (e.g., "oled technology", "anti-reflection screen") |
| `product` | string | Samsung product mentioned (e.g., "S95F", "QN90F") |
| `prompt` | string | The AI prompt that triggered this response |
| `quote` | string | The actual quote from the AI response |
| `sentiment` | string | Sentiment classification: positive, neutral, negative |

### Supabase Table

Data is stored in `semrush_concept_prompts` table:

```sql
SELECT concept, prompt, product, sentiment, quote
FROM semrush_concept_prompts
WHERE concept LIKE '%oled%'
ORDER BY concept;
```

### Data Statistics

- **Total rows:** 8,376
- **Unique concepts:** 2,090
- **Unique prompts:** 324
- **Unique products:** 376

### Scripts

- `load_concept_prompts.py` - Loads JSON data → Supabase `semrush_concept_prompts`

---

## Prompt to URLs (Daily) Endpoint Details

Returns daily data linking prompts to cited URLs with tags and AI model info. **Data loaded into Supabase `semrush_prompt_urls` table.**

### Endpoint Information

| Parameter | Value |
|-----------|-------|
| Element ID | `c0cffe83-8104-4cfb-afac-9b1db673d29e` |
| Product | `ai` |
| Element Name | Prompt to URLs (Daily) |

### Request Payload

```json
{
  "render_data": {
    "project_id": "b7880549-ea08-4d82-81d0-9633f4dcab58",
    "filters": {
      "simple": {
        "start_date": "2026-01-01",
        "end_date": "2026-01-01"
      }
    }
  }
}
```

### Response Structure

```json
{
  "blocks": {
    "data": [
      {
        "date": "2026-01-01T00:00:00Z",
        "prompt": "55 inch tv reviews",
        "source": "https://www.rtings.com/tv/reviews/best/by-size/55-inch",
        "tags": "TV Reviews & Brand,TV Reviews & Brand__Buying Guides,TV Sizes,TV Sizes__Medium Size",
        "model": "google-ai-mode",
        "position": 1,
        "domain_type": "Other"
      }
    ]
  }
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `date` | string | Date of the data (ISO format) |
| `prompt` | string | The AI prompt |
| `source` | string | The cited URL |
| `tags` | string | Comma-separated tags (category, category__subcategory) |
| `model` | string | AI model: `google-ai-mode`, `search-gpt`, `google-ai-overview` |
| `position` | float | Citation position (1 = first citation) |
| `domain_type` | string | Classification: Owned, Earned, Benchmark Competitors, Other |

### Supabase Table

Data is stored in `semrush_prompt_urls` table:

```sql
-- Find URLs cited for a specific prompt
SELECT source, model, position, tags
FROM semrush_prompt_urls
WHERE prompt = 'best 55 inch tv'
ORDER BY date DESC, position;

-- Find prompts that cite a specific domain
SELECT DISTINCT prompt, date, position
FROM semrush_prompt_urls
WHERE source LIKE '%rtings.com%'
ORDER BY date DESC;
```

### Data Statistics

- **Total rows:** 249,307
- **Days loaded:** 29 (2026-01-01 to 2026-01-29)
- **Unique prompts:** 383
- **Unique URLs:** 69,974
- **Data available from:** ~2025-12-18 (can go back further)

### Scripts

- `fetch_prompt_urls.py` - Fetches daily data from SEMrush → Supabase `semrush_prompt_urls`

---

## Prompt Responses Endpoint Details

Returns the full AI-generated response text for a specific prompt on a specific date. **Data loaded into Supabase `semrush_prompt_responses` table.**

### Endpoint Information

| Parameter | Value |
|-----------|-------|
| Element ID | `f1d71cca-00af-454e-80a6-4af6c5d5117a` |
| Product | `ai` |
| Element Name | Prompt Responses |

### Request Payload

```json
{
  "render_data": {
    "project_id": "b7880549-ea08-4d82-81d0-9633f4dcab58",
    "filters": {
      "simple": {
        "keyword": "best 55 inch tv",
        "end_date": "2026-01-31"
      }
    }
  }
}
```

### Filter Options

| Filter | Description |
|--------|-------------|
| `keyword` | The prompt text to fetch response for |
| `end_date` | The date to fetch (single day) |

### Response Structure

```json
{
  "blocks": {
    "data": [
      {
        "text": "## Best 55-Inch TVs for 2026\n\nHere are the top recommendations...",
        "value": 1
      }
    ]
  }
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `text` | string | Full AI response in markdown format |
| `value` | integer | Response index (usually 1) |

### Supabase Table

Data is stored in `semrush_prompt_responses` table:

```sql
-- Get all responses for a prompt
SELECT date, response_text, response_index
FROM semrush_prompt_responses
WHERE prompt = 'best 55 inch tv'
ORDER BY date DESC;

-- Find prompts mentioning a brand
SELECT DISTINCT prompt, date
FROM semrush_prompt_responses
WHERE response_text ILIKE '%samsung%'
ORDER BY date DESC;
```

### Rate Limiting

This endpoint requires one API call per prompt per day. With 383 tracked prompts:
- **Daily fetch:** 383 calls (~40 minutes at rate limit)
- **Historical backfill:** 383 × days (~6,500 calls for 17 days = ~11 hours)

### Scripts

- `fetch_prompt_responses.py` - Fetches daily responses → Supabase `semrush_prompt_responses`

---

## Notes

- The API key is stored in `.env` as `SEMRUSH_API_KEY`
- Date format: `YYYY-MM-DD`
- All requests use POST method with JSON payload
- Elements are specific to the workspace and may vary between clients
- **Rate limit:** 600 requests/hour per workspace (beta period, free)
- **CORS:** Browser requests blocked - use Supabase Edge Function `semrush-proxy` as proxy
