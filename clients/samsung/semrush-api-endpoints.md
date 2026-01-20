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

## Notes

- The API key is stored in `.env` as `SEMRUSH_API_KEY`
- Date format: `YYYY-MM-DD`
- All requests use POST method with JSON payload
- Elements are specific to the workspace and may vary between clients
