# Development Guide

This document tracks development progress for the General Analytics project.

**Related docs:**
- [Build Log](docs/build-log.md) - Detailed session journals with problems, solutions, and plain-English explanations

---

## Project Overview

Multi-client GTM & Google Analytics management project. Uses MCP servers to interact with Google Analytics and Google Tag Manager via Claude Code.

### Project Structure

```
General Analytics/
├── clients/              # Per-client folders
│   ├── _template/        # Template for new clients
│   └── changan-auto/     # Changan Auto client
│       ├── gtm/          # GTM configs, exports
│       ├── ga/           # GA reports, queries
│       ├── looker/       # Looker Studio
│       └── docs/         # Client documentation
├── scripts/              # Utility scripts
│   ├── ga_add_user.py    # Add users to GA properties
│   └── ga_auth_admin.ps1 # Auth with admin scope
├── docs/                 # Project documentation
│   ├── GA-MCP-SETUP.md   # GA MCP setup guide (Windows)
│   └── build-log.md      # Detailed development log
├── .claude/              # Claude Code configuration
│   └── agents/           # Custom subagents
│       └── doc-keeper.md # Documentation maintenance agent
├── .mcp.json             # MCP server configuration
├── pyproject.toml        # Python dependencies
├── CLAUDE.md             # AI assistant instructions
└── DEVELOPMENT.md        # This file
```

---

## Session Progress

### 2026-01-20: Samsung TV Prompts CSV to JSON Parser

**Summary:** Created a Python script to convert Semrush TV prompts CSV into structured JSON with hierarchical tags for the Samsung AI Visibility dashboard tag filter dropdown.

#### What Was Done

1. **Created CSV parsing script** (`clients/samsung/scripts/parse_prompts_csv.py`):
   - Parses `clients/samsung/assets/tv_prompts_semrush_import_v2.csv` (382 prompts)
   - Builds hierarchical tag tree from `__` delimiter (e.g., "TV Reviews & Brand__Year Reviews__2026")
   - Counts matching prompts per tag node
   - Outputs structured JSON at `clients/samsung/assets/tv_prompts.json`

2. **JSON structure (Option C):**
   - `meta` - Total prompt count and unique tag count
   - `tagTree` - Nested hierarchy with counts (TV Features, TV Models, TV Reviews & Brand, TV Sizes)
   - `prompts` - Array of prompt objects with text and associated tags

3. **How to regenerate:** `uv run clients/samsung/scripts/parse_prompts_csv.py`

---

### 2026-01-20: Modular Prompt System for Samsung Dashboards

**Summary:** Refactored monolithic dashboard prompt into a modular system with reusable components, design tokens, and individual element files. Enables generating single dashboard components without full context.

#### What Was Done

1. **Created modular prompt structure** at `clients/samsung/prompts/`:
   - `_base/` - Foundation files (design tokens, fonts, components)
   - `elements/` - Individual dashboard components (header, KPI cards, charts, tables)
   - `_archive/` - Old monolithic files for reference
   - `full-dashboard.md` - Assembly instructions

2. **Key files created:**
   - `_base/design-tokens.md` - CSS variables for colors, spacing, typography
   - `_base/fonts.md` - @font-face declarations for Samsung fonts
   - `_base/components.md` - Reusable UI patterns
   - `elements/header.md` - Dashboard header (includes approved v3 implementation)
   - `elements/kpi-cards.md`, `line-chart.md`, `donut-chart.md`, `stacked-bar.md`, `leaderboard-table.md`, `data-table.md`

3. **Benefits achieved:**
   - Generate individual components without full context
   - Single source of truth for design tokens
   - Consistent styling across all elements
   - Easier maintenance and updates

---

### 2026-01-20: Samsung AI Visibility Dashboard & GitHub Push

**Summary:** Built a styled AI Visibility Dashboard for Samsung with proper branding, fixed header alignment issues, secured API key handling, and pushed the initial commit to GitHub.

#### What Was Done

1. **Samsung AI Visibility Dashboard** (`clients/samsung/dashboards/v3-ai-overview.html`):
   - Applied Samsung branding with official fonts (Samsung Sharp Sans, Samsung One)
   - Fixed header alignment - logo and title now align with main content using same max-width and padding
   - Header: #f7f7f7 background, "AI Visibility Dashboard" title (28px bold, Samsung blue) on left, logo on right
   - KPI cards use CSS grid (`grid-template-columns: repeat(4, 1fr)`) for equal-width alignment
   - All asset paths use relative paths (`../assets/`) for static file usage

2. **Updated prompt file** (`clients/samsung/prompts/ai-overview-dashboard.md`):
   - Renamed to "AI Visibility Dashboard"
   - Added Page Header section with alignment requirements
   - Updated font paths to relative
   - Changed KPI cards from flex to CSS grid specification

3. **Security fix** (`clients/samsung/groq_kimi.py`):
   - Removed hardcoded Groq API key
   - Now requires GROQ_API_KEY in .env file (raises error if missing)

4. **GitHub push** to https://github.com/Qualmage/ai_visibility:
   - Initial commit with 68 files
   - .env properly gitignored (API keys protected)

---

### 2026-01-19: Direct Groq API Script for Kimi K2

**Summary:** After extensive troubleshooting with claude-code-router (which has a known bug with extended thinking parameters), we bypassed it entirely and created a direct Groq API script to query the Kimi K2 model.

#### What Was Done

1. **Attempted claude-code-router setup** at `C:\Users\rober\.claude-code-router\config.json`:
   - Configured Groq, OpenRouter, and Ollama providers
   - Tried multiple transformers: `groq`, `openrouter`, `cleancache`, `reasoning`
   - All attempts failed due to router bug #1046 - it force-sends `enable_thinking` parameter that Groq does not support

2. **Created direct Groq API script** at `clients/samsung/groq_kimi.py`:
   - Bypasses broken claude-code-router completely
   - Uses `moonshotai/kimi-k2-instruct-0905` (latest Kimi K2 on Groq)
   - Features: single queries, report generation, interactive chat mode
   - Dependencies added: `httpx` (async HTTP client)

3. **Configuration**:
   - API key stored in `clients/samsung/.env` as `GROQ_API_KEY`
   - Groq API URL: `https://api.groq.com/openai/v1/chat/completions`

---

### 2026-01-14: Samsung Client Setup & Semrush Enterprise API Discovery

**Summary:** Added Samsung as a new client, created Semrush API test script, resolved PATH configuration issues, and captured 7 Semrush Enterprise API endpoints using Chrome DevTools MCP.

#### What Was Done

1. **Added Samsung client** - Created new client folder using template structure at `clients/samsung/`

2. **Semrush API integration** - Created test script to query Semrush API for Samsung SEO traffic data
   - API test successful: Status 200, returned Samsung HE US traffic data (~10k-11.7k daily traffic)

3. **Added dependencies** - Added `requests>=2.32.0` and `python-dotenv>=1.0.0` to pyproject.toml

4. **Fixed uv PATH issue** - Resolved issue where `uv.exe` at `~\.local\bin\` wasn't in system PATH

5. **Shell escaping lesson learned** - Documented PowerShell variable handling when invoked from bash

6. **Semrush Enterprise API endpoint capture** - Used Chrome DevTools MCP to intercept 7 API calls from Semrush dashboard
   - Documented complete API structure at `clients/samsung/semrush-api-endpoints.md`
   - Base URL: `https://api.semrush.com/apis/v4-raw/external-api/v1`
   - Two products discovered: `ai` (AI Overview) and `seo` (SEO)
   - Workspace ID captured for authenticated requests

---

### 2026-01-14: Virtual Environment Prompt Fix

**Summary:** Fixed incorrectly named virtual environment prompt and documented conda deactivation tip.

#### What Was Done

1. **Fixed venv prompt** - Changed hardcoded "hisense" prompt to "general-analytics" in:
   - `.venv/pyvenv.cfg` - Updated `prompt` setting
   - `.venv/Scripts/Activate.ps1` - Updated activation script strings

2. **Setup tip added** - Documented how to disable conda auto-activate for cleaner terminals

---

### 2026-01-13: Changan Europe Server Error Investigation

**Summary:** Investigated 500 errors affecting Googlebot crawling on Changan Europe website using Chrome DevTools MCP and Google Search Console data analysis.

#### What Was Done

1. **Website Testing** - Used Chrome DevTools MCP to navigate Changan Europe site and monitor network requests
2. **GSC Data Analysis** - Extracted and analyzed crawl stats from Google Search Console export
3. **Root Cause Identification** - Identified DNN ImageProcessor failing on specific image dimensions (1920x960)
4. **CDN Verification** - Confirmed Alibaba CDN is working correctly (serving cached content, not caching errors)
5. **Bug Report Creation** - Created comprehensive developer report with reproduction steps

#### Key Findings

- Image resize requests with `?w=1920&h=960` return 500 errors
- Other dimensions work fine (e.g., `?w=1920` or `?w=1230&h=307`)
- CDN masks the issue for cached content but Googlebot sees errors on cache misses
- Issue started around Dec 5, 2025

#### Files Created

- `clients/changan-auto/reports/changan-image-processor-bug-report.md` - Full developer report
- `clients/changan-auto/crawl-stats-extracted/` - Extracted GSC data (Chart.csv, Table.csv)

---

### 2026-01-13: Initial Setup & GA User Management

**Summary:** Set up GA MCP server, created user management scripts, added users to Changan Auto properties.

#### What Was Done

1. **GA MCP Setup** - Configured analytics-mcp server with Windows-specific workarounds
   - Installed analytics-mcp in isolated Python 3.13 venv
   - Applied credentials path workaround for Windows (GitHub Issue #73)
   - Created comprehensive setup documentation

2. **Multi-Client Structure** - Created organized folder structure for managing multiple clients

3. **GA User Management Scripts** - Created scripts to add/list users on GA properties
   - `scripts/ga_add_user.py` - Add or list users with role selection
   - `scripts/ga_auth_admin.ps1` - Authenticate with admin scope

4. **Added Users to Changan Auto Properties**
   - Added Kristin.Harder@changanauto.eu (VIEWER) to all 4 properties
   - Added Elena.Rosskopf@changaneurope.com (VIEWER) to all 4 properties
   - Note: changanuk.com domain users failed (no Google accounts)

---

## Decision Log

| Date | Decision | Why | Alternatives Rejected |
|------|----------|-----|----------------------|
| 2026-01-20 | Modular prompt system with separate element files | Enables generating individual components without full context, easier maintenance | Single monolithic prompt file (requires full context for any change) |
| 2026-01-20 | CSS Grid for KPI cards instead of Flexbox | Guarantees equal-width cards regardless of content | Flexbox (width varies with content) |
| 2026-01-20 | Relative asset paths (`../assets/`) | Enables static file usage without server | Absolute paths (requires specific deployment location) |
| 2026-01-20 | Explicit text descriptions for visual alignment | Works better than annotated screenshots with AI | Screenshots with drawn annotations |
| 2026-01-13 | Isolated Python 3.13 venv for analytics-mcp | Avoids asyncio conflicts with miniconda | Using system Python, pipx with miniconda |
| 2026-01-13 | Credentials in user directory | Windows workaround for GitHub Issue #73 | AppData\Roaming\gcloud path (doesn't work) |
| 2026-01-13 | Separate admin credentials file | Keeps read-only MCP creds separate from admin creds | Single credential file (scope conflicts) |
| 2026-01-13 | admin_v1alpha for user management | AccessBinding class only in alpha, not beta | admin_v1beta (missing classes) |
| 2026-01-13 | Dedicated doc-keeper agent | Ensures DEVELOPMENT.md and build-log.md stay in sync | Manual updates (prone to drift) |
| 2026-01-13 | Chrome DevTools MCP for site testing | Enables real browser testing to see actual network behavior | Manual browser testing (harder to document) |
| 2026-01-14 | .env file for Semrush API key | Keeps secrets out of code, standard practice | Hardcoded key, environment variable without file |
| 2026-01-14 | Single quotes for PowerShell from bash | Preserves `$env:` variables intact | Double quotes (strips `$`), no quotes (fails) |
| 2026-01-14 | Chrome DevTools MCP for API capture | Captures authenticated enterprise API calls with all headers | Manual browser inspection (tedious), Postman (needs manual setup) |
| 2026-01-19 | Direct Groq API instead of claude-code-router | Router v2.0.x has unfixed bug (#1046) that sends unsupported `enable_thinking` parameter | Downgrade router to v1.x (user preferred direct API) |

---

## Changelog

### [Unreleased]

#### Added
- TV prompts CSV to JSON parser (`clients/samsung/scripts/parse_prompts_csv.py`) - Converts Semrush prompts CSV to hierarchical JSON for dashboard tag filtering
- Samsung TV prompts JSON (`clients/samsung/assets/tv_prompts.json`) - 382 prompts with nested tag tree (58 unique tags)
- Modular prompt system for Samsung dashboards (`clients/samsung/prompts/`) - Enables generating individual components
  - `_base/design-tokens.md` - CSS variables for colors, spacing, typography
  - `_base/fonts.md` - @font-face declarations
  - `_base/components.md` - Reusable UI patterns
  - `elements/header.md` - Dashboard header with approved implementation
  - `elements/kpi-cards.md`, `line-chart.md`, `donut-chart.md`, `stacked-bar.md`, `leaderboard-table.md`, `data-table.md`
  - `full-dashboard.md` - Assembly instructions
- Samsung AI Visibility Dashboard (`clients/samsung/dashboards/v3-ai-overview.html`) - Samsung-branded dashboard with proper font, color, and layout styling
- Dashboard prompt documentation (`clients/samsung/prompts/ai-overview-dashboard.md`) - Specification for generating consistent dashboards (now archived)
- Initial GitHub repository at https://github.com/Qualmage/ai_visibility (68 files)

#### Fixed
- Header alignment in dashboard - logo and title now align with main content area
- Security: Removed hardcoded API key from `groq_kimi.py` - now requires .env file
- uv PATH configuration - added `~\.local\bin` to user PATH for `uv.exe` access
- Virtual environment prompt showing "hisense" instead of "general-analytics"

#### Added (previous)
- Direct Groq API script for Kimi K2 (`clients/samsung/groq_kimi.py`) - bypasses broken claude-code-router
- Dependencies: `httpx` for async HTTP requests

#### Investigated
- claude-code-router bug #1046 - router sends unsupported `enable_thinking` parameter to Groq API

#### Added (previous)
- Samsung client folder structure (`clients/samsung/`)
- Semrush API test script (`clients/samsung/test_semrush_api.py`)
- Semrush Enterprise API documentation (`clients/samsung/semrush-api-endpoints.md`) - 7 captured endpoints
- Dependencies: `requests>=2.32.0`, `python-dotenv>=1.0.0`
- Project setup with uv package manager
- MCP configuration for GTM and GA servers
- GA MCP setup documentation (`docs/GA-MCP-SETUP.md`)
- Multi-client folder structure (`clients/`)
- Changan Auto client folder with GTM container reference
- GA user management scripts (`scripts/ga_add_user.py`, `scripts/ga_auth_admin.ps1`)
- Scripts README with usage documentation
- doc-keeper agent for documentation maintenance
- DEVELOPMENT.md and build-log.md for development tracking
- Changan image processor bug report (`clients/changan-auto/reports/`)

#### Investigated
- Changan Europe 500 server errors - identified DNN ImageProcessor as root cause

#### Infrastructure
- analytics-mcp venv at `C:\Users\rober\analytics-mcp-py313`
- Credentials at `C:\Users\rober\application_default_credentials.json`
- Admin credentials at `C:\Users\rober\ga_admin_credentials.json`

---

## Clients

| Client | Folder | GA Account | GTM Account |
|--------|--------|------------|-------------|
| Changan Auto | `clients/changan-auto/` | 336425779 | 6257643491 |
| Samsung | `clients/samsung/` | TBD | TBD |

### Changan Auto GA Properties

| Property | ID |
|----------|-----|
| Country Picker | 468301281 |
| Germany | 467150353 |
| United Kingdom | 468326267 |
| Netherlands | 468349772 |
