# Build Log

A detailed journal of the General Analytics development process. Each session documents what was done, problems encountered, and how they were solved.

**Purpose:** Capture the full context of development decisions so future-you (or anyone else) can understand not just WHAT was done, but HOW and WHY.

**Format:** Each entry has:
- Technical details for developers
- "Plain English" explanations for non-developers

---

## 2026-01-19: Direct Groq API Script for Kimi K2

### Session Goals
Use Groq's hosted Kimi K2 model for AI queries. Originally attempted via claude-code-router, but ultimately bypassed it due to a persistent bug.

---

### Part 1: The claude-code-router Attempt

#### What We Did
Tried to configure claude-code-router to route requests to Groq's Kimi K2 model. Created config at `C:\Users\rober\.claude-code-router\config.json` with multiple provider configurations:
- Groq (primary target)
- OpenRouter (backup)
- Ollama (local fallback)

#### The Problem
Every attempt to use Groq through the router failed with this error:
```
Error code: 400 - {'error': {'message': 'enable_thinking is not supported', ...}}
```

#### Technical Explanation
claude-code-router v2.0.x has a bug (GitHub issue #1046) where it force-injects an `enable_thinking` parameter into API requests. This parameter is for Claude's extended thinking feature, but:
1. Groq's API does not recognize this parameter
2. Groq rejects the entire request as malformed
3. The router has no way to strip this parameter before sending

We tried multiple "transformers" (filters that modify requests):
- `groq` transformer - did not help
- `cleancache` transformer - did not help
- `reasoning` transformer - did not help
- Combined transformers - still failed

#### Plain English
Think of it like a postal service that automatically stamps "FRAGILE" on every package you send, even when the recipient does not accept packages marked "FRAGILE" and returns them. The router was adding a special instruction to every request that Groq did not understand, so Groq refused to process them.

#### Why We Did Not Downgrade
Router v1.x might work (it does not have this bug), but the user preferred a direct solution rather than using an older version of third-party software with unknown other issues.

---

### Part 2: Direct Groq API Script

#### What We Did
Created a Python script that calls the Groq API directly, bypassing claude-code-router entirely.

#### Technical Details

**File:** `clients/samsung/groq_kimi.py`

**Model:** `moonshotai/kimi-k2-instruct-0905` (Kimi K2 hosted on Groq)

**API Endpoint:** `https://api.groq.com/openai/v1/chat/completions`

**Features:**
- Single query mode (ask one question, get answer)
- Report generation mode (structured output with context)
- Interactive chat mode (conversation loop)

**Dependencies:**
- `httpx` - Modern async HTTP client for Python
- `python-dotenv` - Already in project for loading `.env` files

#### Plain English
Instead of using the middleman (router) that was breaking our requests, we created our own direct phone line to Groq. The script formats our questions exactly how Groq expects them, sends them directly, and gives us back the answers.

---

### Part 3: Configuration

#### What We Did
Added the Groq API key to the existing Samsung client `.env` file:

**File:** `clients/samsung/.env`
```
SEMRUSH_API_KEY=...existing key...
GROQ_API_KEY=gsk_...your key here...
```

#### Plain English
We added the Groq "password" (API key) to the same secure file where we keep the Semrush password. This file is not shared in git, so the keys stay private.

---

### Part 4: Usage Examples

#### Command Line Usage

```bash
# Simple query - ask a question, get an answer
uv run python clients/samsung/groq_kimi.py "What are the top 3 SEO trends for 2026?"

# Report generation - create structured analysis
uv run python clients/samsung/groq_kimi.py --report "Samsung TV market analysis"

# Interactive chat - back-and-forth conversation
uv run python clients/samsung/groq_kimi.py --chat
```

#### Python Import Usage

```python
from clients.samsung.groq_kimi import query_kimi, generate_report

# Quick query
response = query_kimi("Analyze this competitor data...")
print(response)

# Generate a report with context
report = generate_report(
    topic="Q4 Performance Summary",
    context="Revenue: $10M, Growth: 15%, Top product: OLED TVs"
)
print(report)
```

#### Plain English
You can use this script three ways:
1. **Quick question:** Type your question after the script name, get an answer
2. **Report mode:** Ask it to write a structured report on a topic
3. **Chat mode:** Have an ongoing conversation where it remembers what you said before

---

### Session Summary

| Task | Status |
|------|--------|
| Configure claude-code-router for Groq | Failed (bug #1046) |
| Try multiple transformer combinations | Failed |
| Create direct Groq API script | Complete |
| Add GROQ_API_KEY to .env | Complete |
| Document usage examples | Complete |

### Files Created

- `clients/samsung/groq_kimi.py` - Direct Groq API script for Kimi K2

### Files Modified

- `clients/samsung/.env` - Added GROQ_API_KEY
- `pyproject.toml` - Added httpx dependency

### Decision Made

| Decision | Why | Alternative Rejected |
|----------|-----|---------------------|
| Use direct Groq API instead of claude-code-router | Router v2.0.x has unfixed bug (#1046) that sends unsupported `enable_thinking` parameter to Groq | Downgrade to router v1.x (user preferred direct API for reliability) |

### Lessons Learned

1. **Third-party routers can have breaking bugs:** When a proxy/router tool adds parameters your target does not support, you may need to bypass it entirely
2. **Direct API calls are more reliable:** Fewer moving parts means fewer things that can break
3. **Check GitHub issues early:** The router bug was documented in issue #1046 - checking issues first could have saved troubleshooting time
4. **Groq API follows OpenAI format:** The endpoint structure (`/openai/v1/chat/completions`) makes it easy to adapt existing OpenAI code

---

## 2026-01-14: Samsung Client Setup & Semrush API Integration

### Session Goals
Add Samsung as a new client, set up Semrush API integration for SEO traffic data, and resolve any environment issues.

---

### Part 1: Samsung Client Folder Setup

#### What We Did
Created the Samsung client folder using the template structure:
```
clients/samsung/
├── README.md
├── .env              # Semrush API key (gitignored)
├── test_semrush_api.py
├── gtm/.gitkeep
├── ga/.gitkeep
├── looker/.gitkeep
└── docs/.gitkeep
```

#### Plain English
We added Samsung as a new client to the project. Just like having a separate filing drawer for each customer, Samsung now has its own organized folder with places for GTM configs, GA reports, Looker dashboards, and documentation.

---

### Part 2: Semrush API Test Script

#### What We Did
Created a test script to query the Semrush API for Samsung HE (Home Entertainment) US organic traffic data.

#### Technical Details
- Used the Semrush `domain_organic` API endpoint
- Queried `samsung.com/us` domain for US database
- Used `python-dotenv` to load API key from `.env` file
- Successfully retrieved daily traffic data (~10,000-11,700 visits)

#### Plain English
Semrush is a tool that estimates how much search traffic a website gets. We created a script that asks Semrush "how many people find Samsung's US website through Google searches?" The script worked - Samsung's home entertainment section gets about 10,000-12,000 daily visitors from organic search.

#### Files Created
- `clients/samsung/test_semrush_api.py` - The API test script
- `clients/samsung/.env` - Contains the Semrush API key (kept secret, not in git)

---

### Part 3: Added Project Dependencies

#### What We Did
Added two new packages to `pyproject.toml`:
- `requests>=2.32.0` - For making HTTP API calls
- `python-dotenv>=1.0.0` - For loading environment variables from `.env` files

#### Plain English
These are like tools we added to our toolbox:
- **requests** - Lets Python talk to websites and APIs (like Semrush)
- **python-dotenv** - Lets us keep secret passwords in a separate file that we do not share

---

### Problem: uv Not Found in PATH

#### What Happened
When trying to run `uv sync` to install the new dependencies, the terminal said "uv: command not found" even though uv was installed.

#### Technical Explanation
The `uv.exe` executable was installed at `C:\Users\rober\.local\bin\uv.exe`, but this directory was not in the system PATH. The PATH is an environment variable that tells Windows where to look for programs when you type their name.

#### Plain English
It is like having a tool in your garage, but when you ask someone to grab it, they only look in the kitchen. The tool exists, but nobody knows where to find it because we did not tell Windows to look in that garage.

#### Solution
Added the directory to the user's PATH permanently using PowerShell:
```powershell
$currentPath = [Environment]::GetEnvironmentVariable("Path", "User")
[Environment]::SetEnvironmentVariable("Path", "$currentPath;$env:USERPROFILE\.local\bin", "User")
```

#### Plain English Solution
We updated the "places to look for tools" list so Windows now knows to check the `.local\bin` garage whenever we ask for a program.

#### Lesson Learned
When installing tools via `pip install --user` or similar methods, they often end up in `~/.local/bin` which may not be in PATH by default on Windows.

---

### Problem: Shell Escaping with PowerShell Variables

#### What Happened
When running PowerShell commands from bash/Claude, the `$env:USERPROFILE` variable was not being expanded correctly - the `$` was getting stripped.

#### Technical Explanation
Different quoting rules apply when invoking PowerShell from another shell:
- **No quotes or double quotes:** The `$` is interpreted by the outer shell (bash) and stripped
- **Single quotes:** The entire command is passed literally to PowerShell, preserving `$env:` variables

#### Plain English
When you tell PowerShell to do something through an intermediary (like bash), the intermediary might misread your instructions. Using single quotes is like putting the instructions in a sealed envelope - they get delivered exactly as written without anyone changing them along the way.

#### Solution
Use single quotes when calling PowerShell from bash:
```bash
# Wrong - $ gets stripped
powershell "echo $env:USERPROFILE"

# Right - $ preserved
powershell 'echo $env:USERPROFILE'
```

#### Lesson Learned
When automating PowerShell commands from Claude or other shells, always use single quotes around commands containing PowerShell variables like `$env:`.

---

### Part 4: Successful API Test

#### What We Did
Ran the Semrush API test script and confirmed it works:
- HTTP Status: 200 (success)
- Data returned: Samsung HE US organic traffic metrics
- Daily traffic range: ~10,000-11,700 visits

#### Plain English
We tested our connection to Semrush and it worked. We can now pull SEO data for Samsung whenever we need it.

---

### Part 5: Semrush Enterprise API Endpoint Capture

#### What We Did
Used Chrome DevTools MCP to intercept API calls made by the Semrush dashboard. Captured 7 endpoints from the enterprise API (v4-raw) that powers their "Insights" feature.

#### Technical Details
The Semrush Enterprise API uses a different structure than their public API:
- **Base URL:** `https://api.semrush.com/apis/v4-raw/external-api/v1`
- **Authentication:** Bearer token + Workspace ID header
- **Products:** Two distinct products - `ai` (AI Overview tracking) and `seo` (traditional SEO)
- **Workspace ID:** `a22caad0-2a96-4174-9e2f-59f1542f156b` (Samsung account)

#### Captured Endpoints

| Endpoint | Purpose |
|----------|---------|
| `POST /elements` | Main data query - returns keywords, trends, rankings |
| `POST /elements/count` | Get count of matching elements |
| `POST /overview` | Dashboard summary statistics |
| `POST /tags` | Tag management for organizing data |
| `POST /export` | Export data in various formats |
| `POST /config` | User configuration and preferences |
| `POST /columns` | Available columns for data queries |

#### Request Structure
All POST requests use JSON body with this pattern:
```json
{
  "product": "ai" or "seo",
  "projectId": "6919587",
  "filters": { ... },
  "pagination": { "offset": 0, "limit": 100 },
  "sorting": { ... }
}
```

#### Plain English
Semrush has two APIs - a public one for basic queries (which we tested earlier) and an enterprise one that powers their fancy dashboard. The enterprise API is like the "staff entrance" at a hotel - it gives access to more features but requires special credentials. We used Chrome DevTools to watch what requests the Semrush website makes when you click around, then wrote down all those requests so we can make them ourselves later.

#### Why This Matters
The public Semrush API has limited features. The enterprise API (v4-raw) provides:
- AI Overview tracking (which keywords trigger AI responses in Google)
- More detailed historical data
- Export capabilities
- Tag/organization features

By documenting these endpoints, we can build scripts that pull the same data the Semrush dashboard shows, but automated.

#### Files Created
- `clients/samsung/semrush-api-endpoints.md` - Complete API documentation with all 7 endpoints

---

### Session Summary

| Task | Status |
|------|--------|
| Create Samsung client folder | Complete |
| Create Semrush API test script | Complete |
| Add requests and python-dotenv dependencies | Complete |
| Fix uv PATH issue | Complete |
| Test Semrush API connection | Complete |
| Capture Semrush Enterprise API endpoints | Complete |
| Document API structure | Complete |

### Files Created

- `clients/samsung/README.md` - Client documentation
- `clients/samsung/.env` - Semrush API key (gitignored)
- `clients/samsung/test_semrush_api.py` - API test script
- `clients/samsung/semrush-api-endpoints.md` - Enterprise API documentation (7 endpoints)
- `clients/samsung/gtm/.gitkeep` - Placeholder for GTM folder
- `clients/samsung/ga/.gitkeep` - Placeholder for GA folder
- `clients/samsung/looker/.gitkeep` - Placeholder for Looker folder
- `clients/samsung/docs/.gitkeep` - Placeholder for docs folder

### Files Modified

- `pyproject.toml` - Added requests and python-dotenv dependencies

### Lessons Learned

1. **PATH awareness:** When tools are installed but not found, check if their directory is in PATH
2. **Shell escaping matters:** Use single quotes when passing PowerShell commands through other shells to preserve `$` variables
3. **Environment files:** Using `.env` files with `python-dotenv` is a clean way to manage API keys without hardcoding them
4. **Browser interception for API discovery:** Chrome DevTools MCP can capture authenticated API calls that would be difficult to discover otherwise - useful for undocumented enterprise APIs

---

## 2026-01-14: Virtual Environment Prompt Fix

### Session Goals
Clean up development environment by fixing incorrectly named virtual environment prompt.

---

### Problem: Wrong Project Name in Terminal Prompt

#### What Happened
When activating the project's virtual environment, the terminal showed `(hisense)` instead of `(general-analytics)`. This was confusing because "hisense" is a completely different project.

#### Technical Explanation
When you create a Python virtual environment, it stores configuration in two places:
1. `pyvenv.cfg` - A config file at the root of the venv with a `prompt` setting
2. `Scripts/Activate.ps1` (Windows) or `bin/activate` (Mac/Linux) - The script that activates the venv, which may have the name hardcoded

This virtual environment was originally created for a "hisense" project and later copied or reused. The prompt name was never updated.

#### Plain English
When you open a terminal and activate a Python project, it shows the project name in parentheses like `(project-name)` so you know which project you're working in. Ours was showing the wrong name - like having someone else's name tag on your desk.

#### Solution
Updated two files to fix the prompt:

1. **`.venv/pyvenv.cfg`**
   ```
   # Before
   prompt = hisense

   # After
   prompt = general-analytics
   ```

2. **`.venv/Scripts/Activate.ps1`** (lines 61-62)
   ```powershell
   # Before
   $_OLD_VIRTUAL_PROMPT = $function:prompt
   $env:VIRTUAL_ENV_PROMPT = "hisense"

   # After
   $_OLD_VIRTUAL_PROMPT = $function:prompt
   $env:VIRTUAL_ENV_PROMPT = "general-analytics"
   ```

#### Files Modified
- `.venv/pyvenv.cfg`
- `.venv/Scripts/Activate.ps1`

---

### Bonus Tip: Clean Up Terminal from Conda Auto-Activate

#### The Issue
If you have Miniconda or Anaconda installed, it often auto-activates the "base" environment every time you open a terminal, showing `(base)` in your prompt. This can be confusing when working with uv-managed projects.

#### Solution
Disable conda auto-activate:
```powershell
conda config --set auto_activate_base false
```

#### Plain English
This tells conda to stop automatically putting you in its "base camp" every time you open a terminal. You can still use conda when you need it, but it won't clutter your prompt when you're working on other projects.

---

### Session Summary

| Task | Status |
|------|--------|
| Fix venv prompt from "hisense" to "general-analytics" | Complete |
| Document conda auto-activate tip | Complete |

### Lessons Learned

1. **Check venv origins:** When reusing or copying virtual environments, always verify the prompt name matches the current project
2. **Two files to check:** On Windows, both `pyvenv.cfg` and `Activate.ps1` may contain the prompt name

---

## 2026-01-13: Initial Setup & GA User Management

### Session Goals
Set up the GA MCP server, create a multi-client folder structure, and add users to Changan Auto GA properties.

---

### Part 1: GA MCP Server Setup

#### What We Did
- Installed `analytics-mcp` package using `uv tool install`
- Created isolated Python 3.13 virtual environment
- Configured `.mcp.json` with the MCP server settings
- Applied Windows-specific workarounds for credentials path

#### Plain English
We set up a background program (MCP server) that lets Claude connect to Google Analytics. This means Claude can now query GA data, run reports, and check real-time analytics directly without you having to copy/paste from the GA interface.

---

### Part 2: The Great MCP Debugging Adventure

#### Problem 1: MCP Tool Calls Hanging Indefinitely

**What happened:**
The MCP server showed "connected" in Claude Code, but any actual tool call would hang forever with no response or error message.

**Technical explanation:**
The analytics-mcp package uses async Python with grpc (Google's remote procedure call library). When installed via pipx, it created a virtual environment based on miniconda Python. Miniconda's asyncio implementation was conflicting with grpc's async code, causing a deadlock.

**Plain English:**
Think of it like having two traffic controllers at an intersection, each waiting for the other to give the go-ahead. Neither one moves, so traffic stops completely. The MCP server was waiting for Google's response system, which was waiting for the MCP server.

**How we diagnosed it:**
1. Tested the GA API directly with synchronous code - worked fine
2. Tested with async code - got error: "Task got Future attached to a different loop"
3. Traced the error to miniconda's Python installation

**Solution:**
Created a completely isolated Python environment using standalone Python 3.13 (not miniconda):
```
C:\Users\rober\analytics-mcp-py313\
```

**Files modified:**
- `.mcp.json` - Updated to use the isolated venv's executable

---

#### Problem 2: Credentials Path Issue (GitHub Issue #73)

**What happened:**
Even with the isolated Python, MCP calls still hung. No error, just silence.

**Technical explanation:**
There's a known bug on Windows where the analytics-mcp package can't read credentials from the default gcloud path (`%APPDATA%\gcloud\application_default_credentials.json`). Something about how Windows handles path resolution in the subprocess.

**Plain English:**
It's like giving someone directions to your house, but they can't find the street because their GPS doesn't recognize the neighborhood name. The program knew where the credentials file was supposed to be, but couldn't actually read it from that location.

**Solution:**
Copied credentials to the user's home directory and explicitly set the path:
```json
{
  "env": {
    "GOOGLE_APPLICATION_CREDENTIALS": "C:\\Users\\rober\\application_default_credentials.json"
  }
}
```

**Lesson learned:**
When something hangs with no error on Windows, check if it's a path/permissions issue. The analytics-mcp GitHub issues page had this exact problem documented.

---

### Part 3: Multi-Client Folder Structure

#### What We Did
Created an organized folder structure for managing multiple clients:
```
clients/
├── _template/           # Copy this for new clients
└── changan-auto/        # First client
    ├── gtm/             # GTM configs, exports
    ├── ga/              # GA reports, queries
    ├── looker/          # Looker Studio assets
    └── docs/            # Client documentation
```

#### Plain English
We organized the project like a filing cabinet with separate drawers for each client. Each drawer has the same folder structure inside, so it's easy to find things and add new clients by copying the template.

---

### Part 4: GA User Management Scripts

#### What We Did
Created scripts to add users to Google Analytics properties without using the GA web interface.

#### Problem: GA MCP is Read-Only

**What happened:**
Tried to use the GA MCP server to add users, but it only has `analytics.readonly` scope.

**Technical explanation:**
OAuth scopes define what an application can do. The MCP server authenticates with read-only permissions to minimize security risk. Adding users requires the `analytics.manage.users` scope.

**Plain English:**
The MCP server has a "visitor pass" that only lets it look at data, not change anything. To add users, we need an "admin badge" with higher permissions.

**Solution:**
Created separate scripts that authenticate with admin permissions:
- `scripts/ga_auth_admin.ps1` - Gets the admin badge (stores separate credentials)
- `scripts/ga_add_user.py` - Uses the admin badge to add/list users

---

#### Problem: ImportError for AccessBinding

**What happened:**
```
ImportError: cannot import name 'AccessBinding' from 'google.analytics.admin_v1beta'
```

**Technical explanation:**
The Google Analytics Admin API has two versions: `v1beta` (stable but limited) and `v1alpha` (newer features, may change). The `AccessBinding` class for user management is only in `v1alpha`.

**Plain English:**
We were looking for a tool in the "stable tools" drawer, but it's actually in the "new tools" drawer. Google hasn't moved it to stable yet.

**Solution:**
Changed the import from `admin_v1beta` to `admin_v1alpha`:
```python
from google.analytics.admin_v1alpha import (
    AnalyticsAdminServiceClient,
    AccessBinding,
    CreateAccessBindingRequest,
)
```

---

### Part 5: Doc-Keeper Agent Setup

#### What We Did
Created a custom Claude Code subagent specifically for maintaining documentation. The agent lives at `.claude/agents/doc-keeper.md` and can be invoked to update both DEVELOPMENT.md and build-log.md.

#### Plain English
We created a "documentation assistant" that Claude can become when needed. Instead of manually updating documentation files, you can ask Claude to switch into "doc-keeper mode" and it will know exactly how to update both the high-level summary (DEVELOPMENT.md) and the detailed journal (build-log.md) in sync.

#### Why This Matters
Good documentation gets outdated fast. By creating a dedicated agent with clear instructions, we ensure:
- Both documentation files stay in sync
- Technical explanations always include plain-English versions
- Nothing gets lost between sessions

---

### Part 6: Adding Users to Changan Auto Properties

#### What We Did
Added two users to all 4 Changan Auto GA properties as VIEWER:
- Kristin.Harder@changanauto.eu - Success on all 4 properties
- Elena.Rosskopf@changaneurope.com - Success on all 4 properties

Attempted to add two more users:
- Chris.Hills@changanuk.com - Failed: "User not allowed"
- Steve.Kelly@changanuk.com - Failed: "User not allowed"

#### Why Some Users Failed

**Technical explanation:**
The "User not allowed" error means the email address doesn't have a Google account. GA can only add users who have Google accounts (either personal Gmail or Google Workspace accounts).

**Plain English:**
Google Analytics can only give access to people who have a Google ID. The changanuk.com domain probably isn't set up with Google Workspace, so those email addresses don't exist in Google's system.

**Solution:**
Those users would need to either:
1. Have their IT department set up Google Workspace for changanuk.com
2. Use personal Gmail addresses instead

---

### Session Summary

| Task | Status |
|------|--------|
| GA MCP server setup | Complete |
| Multi-client folder structure | Complete |
| GA user management scripts | Complete |
| Doc-keeper agent setup | Complete |
| Add Kristin to all properties | Complete |
| Add Elena to all properties | Complete |
| Add Chris/Steve | Failed (no Google accounts) |

### Files Created/Modified

**Created:**
- `clients/` folder structure
- `clients/changan-auto/` with subfolders
- `scripts/ga_add_user.py`
- `scripts/ga_auth_admin.ps1`
- `scripts/README.md`
- `docs/GA-MCP-SETUP.md`
- `docs/build-log.md` (this file)
- `DEVELOPMENT.md`
- `.claude/agents/doc-keeper.md`

**Modified:**
- `.mcp.json` - Added analytics-mcp configuration
- `pyproject.toml` - Updated project name
- `CLAUDE.md` - Added re-authentication instructions

---

## 2026-01-13: Changan Europe Server Error Investigation

### Session Goals
Investigate 500 server errors reported by Googlebot crawling the Changan Europe website. Determine if the issue is with the CDN, origin server, or image processing.

---

### Part 1: Initial Investigation with Chrome DevTools MCP

#### What We Did
- Used Chrome DevTools MCP to launch a browser and navigate to Changan Europe website
- Monitored network requests to identify failing resources
- Tested various pages and image URLs to find patterns

#### Plain English
We used a special tool that lets Claude control a real Chrome browser. This is like having Claude sit at your computer and browse the website while taking notes on everything that happens behind the scenes - which files load, which ones fail, how long things take.

---

### Part 2: Google Search Console Data Analysis

#### What We Did
- Extracted crawl statistics from a GSC export zip file
- Analyzed response code distribution over time
- Identified spike in 500 errors starting around December 5, 2025

#### What The Data Showed
The GSC crawl stats revealed:
- Normal crawling behavior with mostly 200 (success) responses
- Sudden increase in 500 (server error) responses starting Dec 5
- Errors specifically on image URLs

#### Plain English
Google Search Console keeps a diary of every time Googlebot visits your website. We looked at that diary and noticed that starting in early December, Googlebot started running into "Server Error" messages - like showing up at a store and finding a "Closed" sign instead of getting what you came for.

---

### Part 3: Root Cause Identification

#### The Problem
Image URLs with specific resize parameters return 500 errors:
```
/Portals/0/Images/example.jpg?w=1920&h=960  --> 500 Error
/Portals/0/Images/example.jpg?w=1920        --> 200 OK
/Portals/0/Images/example.jpg?w=1230&h=307  --> 200 OK
```

#### Technical Explanation
The Changan Europe website uses DNN (DotNetNuke) with an ImageProcessor module. This module dynamically resizes images based on URL parameters. The 1920x960 dimension combination (2:1 aspect ratio at high resolution) causes the ImageProcessor to fail with an unhandled exception.

The server returns a 500 error because:
1. The ImageProcessor tries to resize the image to 1920x960
2. Something in that specific calculation fails (likely memory allocation or aspect ratio validation)
3. The error is not gracefully handled, so the server returns a generic 500

#### Plain English
The website has a feature that automatically resizes images to whatever size you request. It is like asking a photo printing service to make your photo a certain size. Most sizes work fine, but when you ask for exactly 1920 pixels wide by 960 pixels tall, the resizing tool crashes. It is like a cash register that works fine for most prices but freezes when you try to ring up exactly $19.20.

---

### Part 4: CDN Behavior Analysis

#### What We Found
The Alibaba Cloud CDN is working correctly:
- It caches successful responses and serves them to subsequent visitors
- It does NOT cache 500 errors (correct behavior)
- This is why users rarely see the problem - they get cached images
- Googlebot sees errors because it often requests uncached URLs

#### Plain English
The CDN is like a delivery warehouse that keeps popular items in stock locally so they can be delivered faster. When the warehouse has the image, everyone gets it quickly. But when Googlebot asks for something not in stock, the warehouse has to call the factory (origin server). If the factory has a problem making that specific item, Googlebot sees the error - but regular visitors usually get the already-stocked version.

---

### Part 5: Bug Report Creation

#### What We Did
Created a comprehensive bug report for developers at:
`clients/changan-auto/reports/changan-image-processor-bug-report.md`

The report includes:
- Executive summary for quick understanding
- Reproduction steps to recreate the issue
- Technical details about the failure
- Impact assessment (SEO, user experience)
- Recommended fixes

#### Plain English
We wrote up a detailed "repair request" that explains exactly what is broken, how to see it for yourself, and suggestions for fixing it. This document can be sent to the website developers so they know exactly what to look for and fix.

---

### Session Summary

| Task | Status |
|------|--------|
| Website testing with Chrome DevTools MCP | Complete |
| GSC crawl stats analysis | Complete |
| Root cause identification | Complete |
| CDN behavior verification | Complete |
| Bug report creation | Complete |

### Key Findings

1. **Root Cause:** DNN ImageProcessor fails on 1920x960 resize requests
2. **Scope:** Only affects this specific dimension, other sizes work
3. **Impact:** Googlebot sees errors on cache misses, affecting crawl efficiency
4. **CDN:** Working correctly, not the problem
5. **Timeline:** Issue started around December 5, 2025

### Tools Used

- **Chrome DevTools MCP** - Browser automation for real network analysis
- **File analysis tools** - ZIP extraction and CSV parsing for GSC data

### Files Created

- `clients/changan-auto/reports/changan-image-processor-bug-report.md` - Developer bug report
- `clients/changan-auto/crawl-stats-extracted/Chart.csv` - GSC crawl chart data
- `clients/changan-auto/crawl-stats-extracted/Table.csv` - GSC crawl table data

### Lessons Learned

1. **CDN masking:** CDNs can hide origin server problems from regular users while search bots still see them
2. **Specific parameters matter:** A bug can affect only very specific input combinations
3. **Browser tools for debugging:** Chrome DevTools MCP provides authentic browser behavior that curl/wget cannot replicate
