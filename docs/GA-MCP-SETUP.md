# Google Analytics MCP Setup Guide (Windows)

This guide documents the setup process for the Google Analytics MCP server on Windows, including known issues and workarounds.

## Prerequisites

- Python 3.13+ (standalone, NOT miniconda/conda)
- Google Cloud CLI (`gcloud`)
- A Google Cloud project with Analytics APIs enabled

## Known Windows Issues

### Issue: MCP tool calls hang/timeout (Error -32001)

**Cause:** Two known problems on Windows:
1. **Conda/miniconda Python conflicts** - If analytics-mcp is installed using conda's Python, asyncio/grpc conflicts cause the MCP server to hang
2. **Credentials file path** - The default gcloud credentials path (`AppData\Roaming\gcloud\`) causes timeouts

**Reference:** [GitHub Issue #73](https://github.com/googleanalytics/google-analytics-mcp/issues/73)

## Installation Steps

### 1. Create isolated Python environment (NOT using conda)

Use a standalone Python installation (from python.org or via `winget`):

```powershell
# Find standalone Python (not miniconda)
where python

# Create venv with standalone Python
& "C:\Users\<username>\AppData\Local\Programs\Python\Python313\python.exe" -m venv "C:\Users\<username>\analytics-mcp-py313"

# Install analytics-mcp
& "C:\Users\<username>\analytics-mcp-py313\Scripts\pip.exe" install analytics-mcp
```

### 2. Authenticate with Google Cloud

```powershell
gcloud auth application-default login --scopes="https://www.googleapis.com/auth/analytics.readonly,https://www.googleapis.com/auth/cloud-platform" --client-id-file="<path-to-client-secret>.json"
```

### 3. Move credentials file (CRITICAL for Windows)

Copy the credentials from the default location to your user directory:

```powershell
copy "$env:APPDATA\gcloud\application_default_credentials.json" "$env:USERPROFILE\application_default_credentials.json"
```

### 4. Configure `.mcp.json`

```json
{
  "mcpServers": {
    "analytics-mcp": {
      "command": "C:\\Users\\<username>\\analytics-mcp-py313\\Scripts\\analytics-mcp.exe",
      "args": [],
      "env": {
        "GOOGLE_PROJECT_ID": "<your-project-id>",
        "GOOGLE_APPLICATION_CREDENTIALS": "C:\\Users\\<username>\\application_default_credentials.json"
      }
    }
  }
}
```

### 5. Restart Claude Code

After updating the config, restart Claude Code to load the new MCP server.

## Troubleshooting

### Verify credentials work directly

```python
# test_ga_direct.py
import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"C:\Users\<username>\application_default_credentials.json"

from google.analytics.admin import AnalyticsAdminServiceClient

client = AnalyticsAdminServiceClient()
for summary in client.list_account_summaries():
    print(f"Account: {summary.display_name}")
```

### Verify async client works

If the sync client works but MCP hangs, test the async client:

```python
# test_ga_async.py
import os
import asyncio
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"C:\Users\<username>\application_default_credentials.json"

from google.analytics.admin_v1beta import AnalyticsAdminServiceAsyncClient
import google.auth

async def main():
    credentials, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/analytics.readonly"])
    client = AnalyticsAdminServiceAsyncClient(credentials=credentials)
    pager = await client.list_account_summaries()
    async for summary in pager:
        print(f"Account: {summary.display_name}")

asyncio.run(main())
```

If this fails with `RuntimeError: Task got Future attached to a different loop`, you have a Python environment conflict (likely conda).

### Check MCP server status

In Claude Code, type `/mcp` to see connected servers and their status.

## Current Configuration (This Project)

| Setting | Value |
|---------|-------|
| Python venv | `C:\Users\rober\analytics-mcp-py313` |
| Credentials | `C:\Users\rober\application_default_credentials.json` |
| Project ID | `changan-gsc` |

## Available MCP Tools

- `get_account_summaries` - List all GA4 accounts and properties
- `get_property_details` - Get details for a specific property
- `list_google_ads_links` - List Google Ads links for a property
- `run_report` - Run a GA4 report
- `run_realtime_report` - Run a realtime report
- `get_custom_dimensions_and_metrics` - Get custom dimensions/metrics for a property
