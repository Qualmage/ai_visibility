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
│   ├── changan-auto/     # Changan Auto client
│   │   ├── gtm/          # GTM configs, exports
│   │   ├── ga/           # GA reports, queries
│   │   ├── looker/       # Looker Studio
│   │   └── docs/         # Client documentation
│   └── samsung/          # Samsung client
│       ├── templates/    # Immutable HTML components
│       │   ├── base/     # fonts.html, tokens.html
│       │   ├── header.html
│       │   ├── kpi-cards.html
│       │   └── line-charts.html
│       ├── configs/      # Dashboard JSON configs
│       ├── scripts/      # Assembly and utility scripts
│       ├── dashboards/   # Generated dashboard HTML
│       ├── assets/       # Images, fonts
│       └── prompts/      # LLM prompt specifications
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

## MCP Authentication Quick Reference

**When to use this:** MCP servers failing with "Reauthentication is needed" or "insufficient authentication scopes" errors.

### Why This Happens

The OAuth app (project 335937140210) is in "Testing" mode, which means tokens expire after ~7 days. Every time you start a new session after token expiry, both GA and GTM MCPs will fail.

### Quick Fix (3 Steps)

1. **Run the auth command** (use `gcloud.cmd`, NOT `gcloud` in PowerShell):
   ```powershell
   gcloud.cmd auth application-default login --scopes "https://www.googleapis.com/auth/analytics.readonly,https://www.googleapis.com/auth/tagmanager.readonly,https://www.googleapis.com/auth/tagmanager.edit.containers,https://www.googleapis.com/auth/tagmanager.publish,https://www.googleapis.com/auth/cloud-platform" --client-id-file="C:\Users\rober\Downloads\client_secret_335937140210-0b9u8oki65hjd9bcsnc7uic8ov51bp2u.apps.googleusercontent.com.json"
   ```

2. **Copy credentials to home directory:**
   ```powershell
   copy "C:\Users\rober\AppData\Roaming\gcloud\application_default_credentials.json" "C:\Users\rober\application_default_credentials.json"
   ```

3. **Restart Claude Code**

Both commands are also in `C:\Development\General Analytics\auth-command.txt` for easy copy/paste.

### Signs You Need to Re-auth

- Error: "Reauthentication is needed"
- Error: "Request had insufficient authentication scopes"
- 503 errors mentioning metadata or plugin
- MCP tools worked last week but fail today

### Permanent Fix (Extends Token Life to 6 Months)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select project `335937140210`
3. Navigate to: APIs & Services > OAuth consent screen
4. Change Publishing status from "Testing" to "In Production"

### Key Files

| File | Purpose |
|------|---------|
| `C:\Development\General Analytics\auth-command.txt` | Both commands for easy copy/paste |
| `C:\Users\rober\application_default_credentials.json` | Where MCP servers read credentials from |
| `C:\Users\rober\Downloads\client_secret_335937140210-...json` | OAuth client ID file (do not share) |

See `docs/build-log.md` for detailed troubleshooting and plain-English explanations.

---

## Session Progress

### 2026-02-04 (Session 16): TV AI Visibility Presentation - Methodology Slide

**Summary:** Created a new methodology slide (slide #6) for the TV AI Visibility presentation that explains data sources, KPI definitions, and tracked AI platforms. This slide provides the foundational context needed for stakeholders to understand how the metrics in the presentation are calculated.

#### What Was Done

1. **Created Methodology Slide (`clients/samsung/slides/tv_ai_visibility/methodology.html`):**
   - **Data Sources Section:** Explains the two primary sources:
     - SEMrush AI Visibility (brand mentions in AI responses)
     - Adobe Analytics (traffic and revenue from AI referrals)
   - **KPI Definitions Section:** Defines all metrics used in the presentation:
     - Mentions, Share of Voice (SOV), Citations, Visibility Score
     - Conversion Rate (CVR), Average Order Value (AOV), Revenue
   - **AI Platforms Tracked Section:** Shows which platforms each data source covers:
     - SEMrush: ChatGPT, Google AI Overview, Google AI Mode, Perplexity, Claude
     - Adobe Analytics: Referral traffic from AI platforms
   - **Data Limitations Section:** Placeholder for user to fill in known caveats

2. **Updated Presentation Documentation (`clients/samsung/docs/tv_ai_visibility.md`):**
   - Added slide #6 documentation to the slide inventory
   - Documents slide purpose and content sections

#### Files Created
- `clients/samsung/slides/tv_ai_visibility/methodology.html`

#### Files Modified
- `clients/samsung/docs/tv_ai_visibility.md`

#### Business Value
- Provides transparency about data sources for stakeholder trust
- Defines KPIs consistently to avoid interpretation confusion
- Documents which AI platforms are monitored vs not
- Creates space to acknowledge data limitations upfront

---

### 2026-02-02 (Session 15): Samsung TV Panel Type Slides - 5-Slide Restructure (QLED Prototype)

**Summary:** Created a new 5-slide presentation structure for Samsung TV panel types, using QLED as the prototype. Each slide focuses on a specific analytical angle: platform distribution, concepts & sentiment, citations, trends over time, and competitive branded vs generic prompt analysis. All data pulled from Supabase (not fabricated).

#### What Was Done

1. **Created 5 QLED Prototype Slides (`clients/samsung/slides/qled/`):**
   - **1-platform.html** - Dual donut charts: Brand Mentions vs URL Citations by AI platform
     - Left donut: Mentions (ChatGPT leads with 46%)
     - Right donut: Citations (Google AI Overview dominates with 72%)
   - **2-concepts.html** - Horizontal stacked sentiment bars + mixed quote examples
     - Top 10 QLED concepts with positive/neutral/negative breakdown
     - 5 real AI quotes (2 positive, 1 neutral, 2 negative)
   - **3-citations.html** - Table of top cited Samsung URLs with triggering prompts
     - Clean table format with readable fonts
   - **4-trends.html** - Multi-line time series showing concept mentions over time
     - Real data from Dec 18, 2025 to Jan 29, 2026
     - Shows the Jan 15 spike when prompts were added
   - **5-competitive.html** - Branded vs Generic prompt comparison
     - Dual bar charts: Samsung vs competitors
     - Branded = prompts containing brand/model names
     - Generic = prompts without brand references

2. **New Chart Functions Added to `slide-charts.js`:**
   - `renderConceptBars()` - Horizontal stacked sentiment bars
   - `renderCitationList()` - URL cards with prompts (replaced with table in final)
   - `renderTrendLines()` - D3 multi-line time series
   - `renderDualCompetitorBars()` - Side-by-side branded/generic comparison
   - `renderSimpleBars()` - Helper for horizontal bars
   - Updated `renderDonut()` to accept custom center label

3. **Created Shared CSS:** `clients/samsung/slides/css/slides.css` - Shared component styles for all slides

4. **Key Data Insights Discovered:**
   - 380 total unique prompts in `concept_prompts` table
   - 266 prompts relate to QLED specifically
   - Citations: Google AI Overview dominates (72%)
   - Mentions: ChatGPT leads (46%)
   - Branded vs Generic query uses regex filtering on `semrush_concept_prompts`

5. **Terminology Clarified:**
   - **Citations** = Samsung URLs cited by AI platforms
   - **Mentions** = Samsung brand mentioned in AI responses

#### Files Created
- `clients/samsung/slides/qled/1-platform.html`
- `clients/samsung/slides/qled/2-concepts.html`
- `clients/samsung/slides/qled/3-citations.html`
- `clients/samsung/slides/qled/4-trends.html`
- `clients/samsung/slides/qled/5-competitive.html`
- `clients/samsung/slides/css/slides.css`

#### Files Modified
- `clients/samsung/slides/js/slide-charts.js` - Added 5 new chart functions

#### Pending Work
- Task #7: Replicate 5-slide structure to remaining 5 categories (OLED, Mini-LED, Micro RGB, Gaming TVs, Sports TVs)

#### Business Value
- Clearer distinction between Mentions (brand visibility) and Citations (URL authority)
- Trend analysis shows data growth patterns over time
- Branded vs Generic analysis reveals Samsung's competitive positioning on different prompt types
- Real quotes provide actionable PR insights

---

### 2026-02-02 (Session 14): Samsung TV Panel Type Slides (Initial 3-Section Version)

**Summary:** Created 6 HTML presentation slides for Samsung TV panel type analysis. Each slide focuses on a specific TV category (Gaming TVs, QLED, Sports TVs, OLED, Mini-LED, Micro RGB) and displays three D3.js visualizations: Platform Breakdown (donut chart), Concepts & Sentiment (treemap), and Competitive Analysis (radar chart). Data is queried from Supabase tables.

#### What Was Done

1. **Created 6 HTML Presentation Slides:**
   - `gaming-tvs.html` - Gaming TVs panel type analysis
   - `qled.html` - QLED TV panel type analysis
   - `sports-tvs.html` - Sports TVs panel type analysis
   - `oled.html` - OLED TV panel type analysis
   - `mini-led.html` - Mini-LED TV panel type analysis
   - `micro-rgb.html` - Micro RGB TV panel type analysis

2. **Each Slide Contains 3 Sections:**
   - **Platform Breakdown (Donut Chart)** - Shows AI model distribution (SearchGPT, Google AI Overview, Google AI Mode) for prompts tagged with that panel type
   - **Concepts & Sentiment (Treemap)** - Samsung concepts colored by sentiment (green=positive, gray=neutral, red=negative), sized by mention count
   - **Competitive Analysis (Radar Chart)** - Multi-metric brand comparison showing Samsung vs competitors across visibility, sentiment, and citation metrics

3. **Created Shared Chart Library:**
   - `clients/samsung/slides/js/slide-charts.js` - Reusable D3.js chart functions
   - `renderDonut(containerId, data)` - Donut chart with legend
   - `renderTreemap(containerId, data)` - Treemap with sentiment coloring
   - `renderRadar(containerId, data)` - Radar chart for brand comparison

4. **Data Sources:**
   - Supabase table: `semrush_prompt_urls` - For platform distribution and citation data
   - Supabase table: `semrush_concept_prompts` - For concept mentions and sentiment

5. **Styling:**
   - Samsung brand fonts (Samsung Sharp Sans, Samsung One)
   - Samsung brand colors (blue #1428A0, accent purple #8091df)
   - Consistent with existing dashboard design system

#### Files Created
- `clients/samsung/slides/gaming-tvs.html`
- `clients/samsung/slides/qled.html`
- `clients/samsung/slides/sports-tvs.html`
- `clients/samsung/slides/oled.html`
- `clients/samsung/slides/mini-led.html`
- `clients/samsung/slides/micro-rgb.html`
- `clients/samsung/slides/js/slide-charts.js`

#### Business Value
- Provides focused analysis per TV panel type for stakeholder presentations
- Enables quick comparison of Samsung's AI visibility across different product categories
- Shows which panel types have strongest/weakest competitive positioning
- Identifies sentiment patterns by product category for PR focus

---

### 2026-02-02 (Session 13): Samsung Competitive AI Visibility Analysis

**Summary:** Loaded competitor brand data from SEMrush API and created Supabase RPC functions to enable competitive Share of Voice analysis. Samsung can now be compared against LG, Sony, TCL, and Hisense across generic prompts, sentiment breakdown, and topic tags.

#### What Was Done

1. **Loaded Competitor Data from SEMrush API:**
   - Created `clients/samsung/fetch_competitor_concept_prompts.py` script
   - Fetched 29 days of data (Jan 1-29, 2026) for LG, Sony, TCL, and Hisense
   - 174,029 new rows loaded in 12.8 minutes (116 API calls)
   - Total `semrush_concept_prompts` now has 338,759 rows across 5 brands

2. **Created Competitive Analysis RPC Functions:**
   - `get_competitive_sov(p_prompt_type)` - Share of Voice by brand on generic/all prompts
   - `get_brand_sentiment_comparison(p_prompt_type)` - Sentiment breakdown by brand
   - `get_negative_concepts_by_brand(p_brand, p_limit)` - Top negative concepts with quotes
   - `get_prompt_brand_comparison(p_prompt, p_tag)` - Head-to-head comparison by prompt or tag
   - `get_competitive_landscape()` - Quick overview of all brands

3. **Key Competitive Findings:**
   - Samsung appears in 99.2% of generic prompts (vs LG 87.5%)
   - Samsung has highest negative sentiment (3.0%) vs competitors (<1%)
   - Samsung leads Gaming tag, LG leads OLED tag
   - Samsung strengths: QD-OLED, brightness (4500 nits), anti-glare, bright room performance
   - Samsung weaknesses: No Dolby Vision, higher burn-in risk, price

4. **Created Analysis Documentation:**
   - `clients/samsung/docs/competitive-analysis.md` - Full methodology and findings

5. **URL Citation Analysis (Continuation):**
   - Analyzed URL-level citations from `semrush_prompt_urls` table
   - **Top Cited Domains:** rtings.com leads (14,414 citations), samsung.com second (12,012)
   - **Brand Website Comparison:** samsung.com has 4.4x more citations than lg.com on generic prompts
   - **Top-3 Position Dominance:** samsung.com appears in top-3 positions 4x more than lg.com
   - **Model Differences:** lg.com only cited by SearchGPT, not Google AI models; samsung.com not cited on comparison queries

#### Files Created/Updated
- `clients/samsung/fetch_competitor_concept_prompts.py`
- `clients/samsung/docs/competitive-analysis.md` (extended with URL citation analysis)

#### Supabase Changes
- Added 174,029 rows to `semrush_concept_prompts` (LG, Sony, TCL, Hisense)
- Created 5 new RPC functions for competitive analysis

#### Business Value
- True competitive Share of Voice now measurable on generic prompts
- Can identify Samsung's strengths/weaknesses vs each competitor
- Tag-level analysis shows where Samsung leads vs trails
- Negative concept analysis provides PR action items
- URL citation analysis shows Samsung's 4.4x advantage in brand website visibility
- Identified competitor weakness: LG invisible to Google AI models

---

### 2026-01-30 (Session 12): Samsung Dashboard System Architecture Documentation

**Summary:** Created a comprehensive system architecture documentation page (`architecture.html`) for the Samsung AI Visibility Dashboard. This provides technical reference for developers and stakeholders to understand how the entire system works - from data sources to database schema to frontend components.

#### What Was Done

1. **Created Architecture Documentation Page (`clients/samsung/dashboards/architecture.html`):**
   - Self-contained HTML file with Samsung branding (fonts, colors, design tokens)
   - Linked from dashboard header navigation alongside GEO Dashboard and Data Definitions
   - Responsive layout matching other dashboard pages

2. **System Overview Section:**
   - ASCII diagram showing data flow: SEMrush API -> Python Scripts -> Supabase -> Dashboard
   - Three-column summary of Data Sources, Data Pipeline, and Frontend architecture
   - Visual representation of the complete data journey

3. **Database Schema Documentation:**
   - Table inventory with row counts (semrush_prompt_urls: 249,307 rows, semrush_concept_mentions: 151,787 rows, etc.)
   - Detailed column schemas for primary tables (semrush_concept_mentions, semrush_cited_pages, semrush_prompt_urls)
   - Purpose and key columns documented for each table

4. **RPC Function Reference:**
   - 8 Supabase RPC functions documented with parameters and return types
   - Functions include: get_daily_mentions, get_top_categories, get_samsung_country_citations, get_sources_by_topic, get_cited_urls, get_cited_urls_count, get_negative_quotes, get_concept_sentiment_summary
   - Example JavaScript and REST API code snippets

5. **Dashboard Component Inventory:**
   - 11 charts listed with chart types (Doughnut, Bar, Line, Pie, etc.)
   - 5 tables listed with features (Sortable, Hierarchical, Paginated)
   - 4 KPI cards with live/placeholder status

6. **Data Flow Documentation:**
   - Visual flow diagram showing loadDashboard() orchestration (5 steps)
   - Parallel API fetch code pattern documented
   - Shows how filters cascade through the system

7. **Filter System Documentation:**
   - Main filters listed: Date Range, Model, Topic, Domain Type, Sentiment
   - Secondary section-specific filters documented
   - Filter Impact Matrix showing which filters affect which components

8. **Data Pipeline Scripts Reference:**
   - 8 Python scripts documented (fetch_*.py and load_*.py)
   - Purpose and output for each script
   - Typical data refresh workflow with example commands

9. **Technology Stack Summary:**
   - Frontend: HTML5/CSS3, Chart.js, D3.js, Vanilla JavaScript
   - Backend: Supabase (PostgreSQL), Edge Functions, REST API + RPC
   - Data Pipeline: Python 3.12+, httpx, supabase-py, SEMrush API

#### Files Created
- `clients/samsung/dashboards/architecture.html`

#### Business Value
- Reduces onboarding time for new developers
- Provides stakeholders with technical reference
- Documents system dependencies and data flow
- Serves as living documentation that can be updated as system evolves

---

### 2026-01-30 (Session 11): Samsung Country Sites Citation Analysis Chart

**Summary:** Added a new horizontal bar chart to the Samsung GEO Dashboard showing how different Samsung country sites contribute to AI response citations. This helps identify which Samsung regional sites (e.g., /us/, /uk/, /de/) and subdomains (e.g., design.samsung.com, developer.samsung.com) are being cited by AI models.

#### What Was Done

1. **Database Changes:**
   - Created new Supabase RPC function `get_samsung_country_citations()`
   - Extracts country codes from URLs (e.g., samsung.com/us/ -> /us/)
   - Identifies subdomains (e.g., design.samsung.com, developer.samsung.com)
   - Returns citation counts and unique URL counts per site
   - Filters for domain_type = 'Owned' and samsung.com URLs only

2. **Dashboard UI Changes (geo-dashboard.html):**
   - Added new chart section after Citation Sources table
   - Title: "Samsung Site Citations by Country"
   - Subtitle: "(Which Samsung country sites appear in AI responses?)"
   - Chart.js horizontal bar chart showing top 15 sites

3. **JavaScript Changes:**
   - Added `samsungCountryChart` instance variable
   - Added `fetchSamsungCountryCitations()` function calling the RPC
   - Added `renderSamsungCountryChart()` with Chart.js horizontal bar chart
   - Wired up in `loadDashboard()` Promise.all

4. **Visual Design:**
   - /us/ highlighted in Samsung blue (#1428A0) - dominant at 10,180 citations
   - Other country codes in lighter purple (#8091df)
   - Subdomains (design.samsung.com, etc.) in gray (#9e9e9e)
   - Tooltips show citation count and unique URL count

#### Business Value
- Helps identify if US site (target market) is being cited appropriately
- Shows which country sites are appearing in US search AI responses
- Reveals subdomain citation patterns (developer, design, community sites)

#### Files Modified
- `clients/samsung/dashboards/geo-dashboard.html`

#### Supabase Changes
- Created: `get_samsung_country_citations()` RPC function

---

### 2026-01-30 (Session 10): Topics Tree Table UI Improvement

**Summary:** Replaced the "Top Topics by Mentions" bar chart with an expandable tree table that displays topic hierarchy (categories and tags) with full metrics. Removed the redundant "Sources by Topic with Sentiment" section. Created a new `summary_topics_tree` table and RPC function to power the tree table.

#### What Was Done

1. **Database Changes:**
   - Created new Supabase table `summary_topics_tree` to store pre-computed topic metrics
   - Table columns: category, tag, prompt_count, citations, unique_sources, positive_pct, neutral_pct, negative_pct
   - Created `get_topics_tree_data()` RPC function that queries this summary table

2. **Dashboard UI Changes (geo-dashboard.html):**
   - Replaced "Top Topics by Mentions" Chart.js bar chart with an expandable tree table
   - Removed "Sources by Topic with Sentiment" section (redundant with new tree table)
   - Tree table shows 4 categories: TV Features, TV Models, TV Reviews & Brand, TV Sizes
   - Categories are collapsed by default, click to expand and see child tags
   - Added Expand All / Collapse All buttons for quick navigation

3. **JavaScript Changes:**
   - Removed: `fetchSourcesByTopic()`, `renderSourcesByTopicTable()`, `setupSourcesByTopicSorting()`, `renderTopicsChartFromData()`
   - Added: `fetchTopicsTreeData()`, `renderTopicsTree()`, `toggleTopicCategory()`, `expandAllTopics()`, `collapseAllTopics()`

4. **CSS Changes:**
   - Added styles for `.topic-category-row`, `.topic-tag-row`, `.expand-icon`

#### Files Modified
- `clients/samsung/dashboards/geo-dashboard.html`

#### Supabase Changes
- Created: `summary_topics_tree` table
- Created: `get_topics_tree_data()` RPC function

---

### 2026-01-30 (Session 9): PR Action Center Fixes and Cited URLs Supabase Migration

**Summary:** Fixed PR Action Center filter bugs by correcting Supabase function return types and removing duplicate function overloads. Migrated the Cited URLs table from SEMrush API proxy to direct Supabase queries, adding filters and pagination.

#### What Was Done

1. **Fixed PR Action Center Filters:**
   - Fixed `get_negative_quotes` function - was missing `date` field in return type
   - Dropped old 3-param `get_negative_quotes(integer, text, text)` overload (ambiguous)
   - Dropped old 1-param `get_concept_sentiment_summary(integer)` overload (ambiguous)
   - Functions now work correctly with topic filtering and return dates for the quotes table

2. **Migrated Cited URLs Table to Supabase:**
   - Previously fetched from SEMrush API via proxy (`/functions/v1/semrush-proxy`)
   - Now queries `semrush_prompt_urls` table directly from Supabase
   - Created new Supabase RPC functions:
     - `get_cited_urls(p_limit, p_offset, p_date_from, p_date_to, p_tag, p_domain_type, p_domain)` - aggregated URL data
     - `get_cited_urls_count(...)` - total count for pagination
     - `get_top_cited_domains(p_limit)` - top domains for filter dropdown

3. **Added Cited URLs Filters and Pagination:**
   - Responds to top-level filters: Date Range, Topic, Domain Type
   - Section-level Domain filter dropdown (top 30 domains grouped by type)
   - Pagination (15 items per page)

#### New JavaScript Functions
- `fetchCitedUrls()` - fetch paginated URL data from Supabase
- `fetchCitedUrlsCount()` - fetch total count for pagination
- `loadCitedUrlsDomainFilter()` - populate domain dropdown
- `reloadCitedUrls()` - reload table when filters change
- `changeCitedUrlsPage()` - handle pagination

#### Files Modified
- `clients/samsung/dashboards/geo-dashboard.html`

#### Supabase Changes
- Fixed: `get_negative_quotes` return type now includes `date` field
- Dropped: `get_negative_quotes(integer, text, text)` (old overload)
- Dropped: `get_concept_sentiment_summary(integer)` (old overload)
- Created: `get_cited_urls`, `get_cited_urls_count`, `get_top_cited_domains`

---

### 2026-01-30 (Session 8): Data Definitions Page Restructured for GEO Dashboard

**Summary:** Completely restructured the `clients/samsung/dashboards/data-definitions.html` documentation page to align with the actual GEO Dashboard metrics. Replaced outdated placeholder sections with new sections matching the live dashboard, updated all formulas to match the JavaScript calculations in `supabase-data.js`, and replaced all placeholder text with actual content.

#### What Was Done

1. **Replaced Outdated Sections** - Removed placeholder sections that no longer matched the dashboard:
   - Removed: Dual-Metric KPIs, Prompt Tracking, Position Metrics
   - These were from an earlier dashboard design and contained `[TBD]` placeholders

2. **Added New Metric Sections** - Created 7 new sections matching the live dashboard:

   | Section | Metrics Documented |
   |---------|-------------------|
   | Primary KPIs | Share of Voice, Visibility Score, Sentiment Score, Total Mentions |
   | Domain Sentiment Analysis | Sentiment by Domain, Domain Type Breakdown, Domain Performance Summary |
   | Citation Metrics | Citations, Mentions, Visibility %, URLs Cited |
   | Concept Analysis | Concept Mentions, Top Positive/Negative Concepts, Concept Sentiment Mix |
   | Platform Metrics | Platform Mentions, Platform Trend (with AI model pills for ChatGPT, Google AI Overview, Google AI Mode) |
   | Trend Metrics | Mentions Over Time, Period Comparison |
   | PR Action Center | Negative Quotes, Negative Concept Frequency, Prompts with Negative Quotes |

3. **Added "Understanding the Data" Section** - New explanatory section with info boxes:
   - Mentions vs Citations (what each means)
   - Sentiment Classification (how positive/neutral/negative is determined)
   - Data Freshness (when data updates)
   - Position/Ranking (how ranking is calculated)
   - AI Model Coverage (which AI platforms are tracked)

4. **Updated All Formulas** - Ensured formulas match the actual JavaScript calculations in `supabase-data.js`:
   - Share of Voice: `(Samsung Mentions / Total Brand Mentions) x 100`
   - Visibility Score: `(Cited URLs / Total Tracked URLs) x 100`
   - Sentiment Score: `((Positive - Negative) / Total Mentions) x 100`

5. **Replaced All Placeholder Text** - Removed all `[TBD]` and `[Description to be provided]` placeholders with actual content

6. **Updated Data Source Badges** - Changed to show "Semrush" consistently across all metrics (previously had mixed/incomplete sources)

7. **Updated Table of Contents** - Rewrote to match new section structure

8. **Fixed Navigation** - Updated back link to point to `geo-dashboard.html` instead of `scom-overview.html`

#### Files Modified
- `clients/samsung/dashboards/data-definitions.html`

---

### 2026-01-30 (Session 7): Data Context, KPI Changes, Topic Filter, and Deployment

**Summary:** Enhanced geo-dashboard.html with data context and measurement caveats, added period-over-period change indicators to KPIs, implemented topic filtering for multiple dashboard sections, fixed Hisense brand color, and deployed to production.

#### What Was Done

1. **Data Coverage Section** - Added a new section after KPI cards explaining data context:
   - 36,765 Samsung prompts tracked (from Semrush's 250M+ database)
   - 383 tracked prompts focused on TV queries
   - 3 AI surfaces monitored (ChatGPT, Google AI Overview, Google AI Mode)

2. **Measurement Caveats Box** (amber styling) - Documented data limitations:
   - Sample-based tracking limitations
   - Surface coverage gaps (missing Perplexity, Claude, Copilot)
   - Response variability (same prompt returns different answers)
   - Prompt diversity (users phrase questions infinitely different ways)

3. **Improving Measurement Box** (green styling) - Listed future enhancement paths:
   - Model probing
   - Model mechanistic interpretability analysis
   - Adobe Analytics referral analysis
   - Adobe Analytics user journey tracking

4. **KPI Change Indicators** - Updated `calculateKPIs()` to compute period-over-period changes:
   - Splits data into first half vs second half of date range
   - KPI cards now show percentage change badges
   - Updated `updateKPICard()` to hide badges when no change data available

5. **Topic Filter Support** - Added filtering capability to multiple sections:
   - New `fetchPromptsByTag()` function to get prompts matching a tag
   - Updated `get_negative_quotes` RPC to accept `p_tag` parameter
   - Updated `get_concept_sentiment_summary` RPC to accept `p_tag` parameter
   - Created `get_prompts_by_tag` RPC function
   - Created `get_domain_sentiment_by_tag` RPC function
   - Topic filter now filters: Negative Quotes, Concept Sentiment, Citation Sources, Cited URLs
   - Note: KPIs and Domain Sentiment don't filter by topic yet (would need pre-computed summary tables)

6. **Brand Color Fix** - Changed Hisense brand color from #00A0DF to #00a4a0

7. **Production Deployment** - Deployed to DigitalOcean at https://robotproof.io/samsung/ai-visibility/geo-dashboard.html

#### New/Updated Supabase Functions

- `get_negative_quotes(p_limit, p_domain, p_concept, p_tag)` - Added `p_tag` parameter
- `get_concept_sentiment_summary(p_limit, p_tag)` - Added `p_tag` parameter
- `get_prompts_by_tag(p_tag)` - Returns prompts matching a tag
- `get_domain_sentiment_by_tag(p_tag)` - Returns domain sentiment filtered by tag (slow for filtered queries)

#### Files Modified

- `clients/samsung/dashboards/geo-dashboard.html` - All changes above

#### Deployment URL

- https://robotproof.io/samsung/ai-visibility/geo-dashboard.html

---

### 2026-01-30 (Session 6): PR Action Center Fixes, Domain Filter, and Concept Filter

**Summary:** Fixed a critical bug in the PR Action Center where a cartesian join caused only 1 concept to display with duplicate quotes. Added domain and concept filtering capabilities to the PR Action Center, and updated the Quote Browser to show prompts instead of domains.

#### Problem Diagnosed

The PR Action Center was showing only 1 concept ("interface") with the same quote repeated for all domains. Root cause: the `get_negative_quotes` RPC function had a cartesian join problem - joining `concept_prompts` to `prompt_urls` to `domains` caused 1 quote x 20 domains = 20 duplicate rows.

#### Data Reality (verified via MCP)

- 4,308 unique negative quotes exist in the database
- 919 unique negative concepts exist
- Top concepts by negative mentions: remote control (188), price (172), contrast (157), viewing angles (139)

#### Fixes Applied

1. **Fixed `get_negative_quotes` RPC function** - Removed broken JOINs that caused cartesian product; now queries `semrush_concept_prompts` directly with DISTINCT; added optional `p_domain` parameter for filtering by domain; uses EXISTS subquery to filter by domain without duplicates

2. **Added Domain Filter to PR Action Center** - New dropdown grouped by domain type (Earned, Owned, Competitors, Other); shows negative mention count next to each domain; `loadPRDomainFilter()` function populates dropdown from `summary_domain_sentiment`; `reloadPRActionCenter()` function reloads only PR section when filter changes

3. **Added Concept Filter to PR Action Center** - New dropdown next to domain filter; populated from `get_concept_sentiment_summary` RPC filtered to concepts with negative > 0; shows count: "remote control (188 negative)"; works in combination with domain filter

4. **Updated Quote Browser** - Changed "Domain" column to "Prompt" (quotes aren't directly from domains); shows which search query triggered the negative sentiment; updated table header, renderQuoteBrowser(), and exportQuotesToCSV()

5. **Updated "Negative Coverage by Source" chart** - Renamed to "Prompts with Most Negative Quotes"; now shows which prompts generate the most negative sentiment

#### New/Updated Supabase Functions

- `get_negative_quotes(p_limit, p_domain, p_concept)` - Returns unique negative quotes, optionally filtered by domain and/or concept
- `get_concept_sentiment_summary(p_limit)` - Aggregates concepts by sentiment counts

#### New JavaScript Functions

- `loadPRConceptFilter()` - Populates the concept dropdown from RPC, filtering to concepts with negative mentions
- Updated `reloadPRActionCenter()` - Reads both domain and concept filters, passes both to fetchNegativeQuotes()
- Updated `exportQuotesToCSV()` - Includes concept in filename when filtered (e.g., `samsung_negative_quotes_rtings_com_remote_control_2026-01-30.csv`)

#### Use Cases

- "What does RTINGS say about remote control?" - Filter Domain: rtings.com, Concept: remote control
- "All negative quotes about price" - Concept: price
- "What are TechRadar's criticisms?" - Domain: techradar.com

#### Lessons Learned

- JOINs can cause cartesian products when relationships are many-to-many
- Use EXISTS subqueries instead of JOINs when filtering to avoid duplicates
- Always test RPC functions via MCP before assuming they work in the dashboard
- Combinable filters give users powerful ad-hoc analysis without new code

#### Files Modified

- `clients/samsung/dashboards/geo-dashboard.html` - Added concept filter HTML, loadPRConceptFilter(), updated reloadPRActionCenter() and exportQuotesToCSV()
- Supabase migrations for RPC functions (added `p_concept` parameter to `get_negative_quotes`)

---

### 2026-01-30 (Session 5): GEO Dashboard Sentiment Analysis Enhancement

**Summary:** Applied the UI requirements plan to transform `clients/samsung/dashboards/geo-dashboard.html` with comprehensive sentiment analysis sections. Added ~1100 lines of new code including 4 new dashboard sections, enhanced filtering, and interactive data visualizations for PR action and domain analysis.

#### What Was Done

1. **Enhanced Filter Bar** - Added Domain Type filter (Owned/Earned/Competitors/Other) and Sentiment filter (Positive/Neutral/Negative) to the existing filter bar

2. **Domain Sentiment Analysis Section** (new, after KPI cards):
   - Sentiment by Domain horizontal stacked bar chart showing positive/neutral/negative breakdown per domain
   - Owned vs Earned vs Competitor comparison chart for aggregate domain type analysis
   - Domain Performance Summary sortable table with domain metrics
   - "Questions this section answers" visible to users for context

3. **PR Action Center Section** (new):
   - Top Negative Concepts chart identifying pain points
   - Negative Coverage by Source chart showing which sources have negative sentiment
   - Quote Browser table with pagination for reviewing actual negative quotes
   - Export CSV functionality for PR team workflows
   - "Questions this section answers" for user guidance

4. **Concept Analysis Section** (new):
   - Top Positive Concepts chart highlighting strengths
   - Concept Sentiment Mix stacked bar chart showing sentiment distribution per concept
   - "Questions this section answers" for context

5. **Topic Deep Dive Section** (enhanced existing Top Topics):
   - Added section header with questions list
   - Sentiment breakdown per tag showing how each topic is perceived

#### Technical Implementation
- Added ~15 new CSS classes for section headers, question displays, tooltips, pagination, and export buttons
- Added 8 new JavaScript functions for data fetching (fetchDomainSentiment, fetchNegativeQuotes, fetchConceptSentiment)
- Added 9 new chart rendering functions (renderDomainSentimentChart, renderDomainTypeChart, etc.)
- Integrated new filters into loadDashboard() function
- File grew from ~1940 lines to ~3022 lines

#### Data Sources Used
- `summary_domain_sentiment` table (pre-computed aggregations)
- `vw_sentiment_quotes` view (for quote browser)
- Existing RPC functions for domain/concept queries

#### Files Modified
- `clients/samsung/dashboards/geo-dashboard.html`

---

### 2026-01-30 (Session 4): Critical Cartesian Product Fix in Domain Sentiment Views

**Summary:** Fixed a critical bug in the Supabase views and summary tables where joining `semrush_prompt_urls` (249K rows) with `semrush_concept_prompts` (145K rows) on the `prompt` column created a cartesian product explosion. Each prompt has ~651 URLs and ~386 concepts, so the join multiplied rows up to 251K per prompt, inflating "mentions" counts from thousands to millions (e.g., RTINGS showed 4.9M positive "mentions" when the correct count is 358 prompts).

#### The Problem

The original `refresh_single_domain_sentiment()` function joined the two tables directly on `prompt`, which created:
- 383 unique prompts in `semrush_prompt_urls`
- 377 unique prompts in `semrush_concept_prompts`
- Each prompt appears ~651 times in URLs table (once per source URL)
- Each prompt appears ~386 times in concepts table (once per concept)
- Join result: up to 651 x 386 = 251,286 rows per matching prompt

This caused wildly inflated counts like 69M positive "mentions" for Samsung when the meaningful unit is ~30K prompts.

#### The Fix

Rewrote `refresh_single_domain_sentiment_v2()` to:
1. First get distinct prompts that cite a domain (from `semrush_prompt_urls`)
2. Then join with concepts to get sentiment breakdown (from `semrush_concept_prompts`)
3. Count DISTINCT prompts and concepts, not joined rows
4. Use prompts as the meaningful "mentions" count (renamed to `total_mentions`)

#### Corrected Numbers (example: RTINGS)

| Metric | Before (Inflated) | After (Correct) |
|--------|-------------------|-----------------|
| Positive "mentions" | 4,958,931 | 358 prompts |
| Unique URLs | N/A | 2,344 |
| Unique concepts | 7,949 | 7,949 (unchanged) |

#### Key Insight

- `unique_urls` = how many distinct URLs from that domain are cited
- `unique_prompts` = how many prompts (questions) cite that domain with that sentiment
- `unique_concepts` = how many distinct concepts appear in those prompts
- `total_mentions` should equal `unique_prompts` (the meaningful unit of measurement)

#### Updated Functions

- `refresh_single_domain_sentiment_v2(domain)` - Correct counts using distinct prompts
- `refresh_all_summaries()` - Now uses v2 function
- Refreshed all 12 key domains with corrected data

---

### 2026-01-30 (Session 3): Dashboard Demo Questions and UI Requirements Documentation

**Summary:** Created comprehensive documentation to ensure the Samsung AI Visibility dashboard can answer all questions clients will ask. This includes 60+ demo questions across 10 categories, sample queries against Supabase views to understand data patterns, and detailed UI requirements for filters, charts, tables, and page structure.

#### What Was Done

1. **Created `clients/samsung/docs/dashboard-demo-questions.md`** - 60+ questions across 10 categories:
   - Domain questions (RTINGS vs TechRadar vs Tom's Guide vs CNET)
   - Domain Type questions (Owned vs Earned vs Competitor breakdown)
   - Sentiment questions (top negative concepts, negative quotes from review sites)
   - Tag/Topic questions (Gaming TVs, OLED sentiment across domains)
   - Concept questions (remote control, price, contrast, viewing angles)
   - Brand questions (Samsung: 69M positive, 26M neutral, 2.6M negative mentions)
   - Product questions (S95F, Neo QLED, The Frame top products)
   - PR Action questions (negative quotes requiring response)
   - Time-based questions (trends over periods)
   - Cross-dimensional questions (combining filters)

2. **Ran Sample Queries Against Supabase Views** to understand data patterns:
   - Domain comparison queries showing sentiment percentages
   - Domain type breakdown (Owned vs Earned vs Competitor)
   - Top negative concepts identified: remote control, price, contrast, viewing angles
   - Negative quotes from review sites extracted for PR action
   - Tag/topic sentiment analysis
   - Brand mention volumes with sentiment breakdown
   - Product mentions and rankings
   - Available tags (39 tags in 4 categories)
   - Available domains (12 key domains in 4 types)

3. **Created `clients/samsung/docs/dashboard-ui-requirements.md`** - Complete UI specification:
   - Filter components needed (Domain, Domain Type, Sentiment, Date, Tag, Concept)
   - KPI cards specification
   - 6 chart types required (sentiment donut, domain comparison, domain type, tag sentiment, concept cloud, time series)
   - Table specifications (quote browser, domain summary, product leaderboard)
   - Drill-down paths for interactive exploration
   - Page/view structure (5 views: Overview, Domain Detail, Topic Analysis, PR Action Center, Competitive Analysis)
   - Performance considerations (when to use summary tables vs views)
   - Sample queries for each page

#### Files Created
- `clients/samsung/docs/dashboard-demo-questions.md`
- `clients/samsung/docs/dashboard-ui-requirements.md`

---

### 2026-01-30 (Session 2): Supabase View Optimizations - Summary Tables for Performance

**Summary:** The views created earlier today were timing out on aggregated queries (249K rows being computed on every request). Implemented a summary table architecture with pre-computed aggregations and refresh functions. Domain sentiment and domain type sentiment queries are now instant.

#### Problem Solved
Views like `vw_domain_sentiment` and `vw_domain_type_sentiment` were timing out because they computed aggregations across 249K+ rows on every query. This is fine for filtered queries but unacceptable for dashboard-level summaries.

#### Optimizations Applied

1. **Domain Lookup Table** (`semrush_domains`)
   - Extracts unique source URLs with pre-computed domain names
   - Eliminates repeated `SPLIT_PART()` operations on every query
   - Indexed on `domain` and `domain_type`

2. **Summary Tables** (pre-computed aggregations):
   | Table | Purpose |
   |-------|---------|
   | `summary_domain_sentiment` | 12 key domains pre-aggregated |
   | `summary_domain_type_sentiment` | Owned/Earned/Competitor/Other breakdown |
   | `summary_tag_sentiment` | Tag-level sentiment (structure ready) |
   | `summary_tag_domain_sentiment` | Tag + domain combinations (structure ready) |

3. **Updated Views** to read from summary tables:
   - `vw_domain_sentiment` -> reads from `summary_domain_sentiment`
   - `vw_domain_type_sentiment` -> reads from `summary_domain_type_sentiment`

4. **Refresh Functions**:
   - `refresh_single_domain_sentiment(domain)` - Refresh one domain
   - `refresh_all_summaries()` - Refresh all 12 key domains + domain type summary

5. **New Indexes**:
   - `idx_prompt_urls_domain_type` on `semrush_prompt_urls(domain_type)`
   - `idx_prompt_urls_source` on `semrush_prompt_urls(source)`

#### Key Domains Pre-populated
- Review sites: rtings.com, techradar.com, tomsguide.com, cnet.com, whathifi.com
- Business: forbes.com, businessinsider.com, bestbuy.com
- Owned: samsung.com, news.samsung.com
- Competitors: lg.com, sony.com

#### Performance Results
- Domain sentiment queries: **instant** (was timing out)
- Domain type queries: **instant** (was timing out)
- Tag sentiment with WHERE clause: fast
- Tag + domain with WHERE clause: fast

#### Dashboard Usage
- Use `vw_domain_sentiment` and `vw_domain_type_sentiment` directly for aggregated data
- Use `vw_sentiment_quotes` with WHERE filters for PR action items
- Call `refresh_all_summaries()` periodically to update pre-computed data

---

### 2026-01-30: Samsung Supabase Views - Flexible Query Layer

**Summary:** Created 7 PostgreSQL views in Supabase to enable flexible querying across the full Samsung AI visibility data chain: Tag -> Prompt -> URL/Domain -> Concept -> Sentiment. These views join data from `semrush_prompt_urls` (249K rows), `semrush_concept_prompts` (145K rows), and `tv_topics` (41 rows) to answer complex questions about brand perception.

#### Views Created

| View | Purpose |
|------|---------|
| `vw_prompt_url_sentiment` | Core linked view joining prompts to URLs to sentiment |
| `vw_domain_sentiment` | All domains aggregated with sentiment percentages |
| `vw_domain_type_sentiment` | Sentiment breakdown by domain type (Owned/Earned/Competitor) |
| `vw_sentiment_quotes` | All sentiment quotes filterable by domain |
| `vw_prompt_tags_expanded` | Normalized tag rows with category/tag parsed from prompt data |
| `vw_tag_sentiment` | Sentiment aggregated by tag |
| `vw_tag_domain_sentiment` | Combined view: tags + domains + sentiment |

#### Example Queries Now Possible
- "What negative things do review sites say about Samsung?"
- "Which concepts get positive sentiment on owned domains?"
- "What's the sentiment breakdown for 'Gaming TVs' tag?"

#### Why Views Instead of More RPC Functions
Views are simpler to maintain and can be combined in ad-hoc queries. RPC functions are better for complex aggregations that need parameters. These views complement the existing `get_sources_by_topic` RPC function.

---

### 2026-01-29 (Session 3): Documentation Sync - Supabase Tables, RPC Functions, and GEO Dashboard Features

**Summary:** Comprehensive documentation update to capture undocumented Supabase infrastructure and GEO Dashboard features. Added documentation for 6 Supabase tables (including 3 previously undocumented), 3 RPC functions (including 1 previously undocumented), and new dashboard features like the Cited URLs table and Sources by Topic with Sentiment table.

#### What Was Documented

1. **Supabase Tables - Updated Row Counts and Added Missing Tables:**

   | Table | Rows | Purpose |
   |-------|------|---------|
   | `semrush_concept_mentions` | 151,787 | Brand mentions, sentiment, concepts by date/model |
   | `semrush_cited_pages` | 84,856 | URLs cited in AI responses |
   | `semrush_url_prompts` | 43,842 | Prompts per URL with volume, topic, LLM |
   | `semrush_concept_prompts` | 145,337 | Brand mentions with prompts, quotes, sentiment |
   | `semrush_prompt_urls` | 249,307 | Date-stamped prompt-to-source mappings with position |
   | `tv_topics` | 41 | TV topic categories for filter dropdown |

2. **NEW RPC Function Documented: `get_sources_by_topic`**
   - Parameters: `p_date` (date), `p_tag` (text)
   - Returns: domain, domain_type, citations, mentions, positive/negative/neutral percentages
   - Joins `semrush_prompt_urls` with `semrush_concept_prompts` to correlate sources with sentiment
   - Used by: "Sources by Topic with Sentiment" table in GEO Dashboard

3. **GEO Dashboard Features Documented:**
   - Cited URLs Table (SEMrush Element ID: `3c29aa85-4f06-4f14-a376-b02333c6e3fa`)
   - Sources by Topic with Sentiment Table (uses `get_sources_by_topic` RPC)
   - supabase-data.js centralized data service module

#### Files Updated
- `DEVELOPMENT.md` (this file)
- `docs/build-log.md`
- `clients/samsung/dashboards/DATA-REQUIREMENTS.md`

---

### 2026-01-29 (Session 2): GEO Dashboard - Supabase Edge Function and Live Data

**Summary:** Major infrastructure update to the GEO Dashboard. Created a Supabase Edge Function (`semrush-proxy`) to proxy SEMrush API calls from the browser (avoiding CORS issues). Migrated Topic filter data from static JSON file to Supabase `tv_topics` table. Updated Citation Sources table to fetch live data from SEMrush via the proxy.

#### What Was Done

1. **Created Supabase Edge Function: `semrush-proxy`**
   - Endpoint: `https://zozzhptqoclvbfysmopg.supabase.co/functions/v1/semrush-proxy`
   - Purpose: Proxy SEMrush API calls to avoid browser CORS restrictions
   - Accepts POST body with `element_id`, `project_id`, and `filters`
   - Returns SEMrush API response with CORS headers
   - JWT verification disabled for public dashboard access

2. **Created Supabase Table: `tv_topics`**
   - Purpose: Store TV topic/tag data for the Topic filter dropdown
   - Columns: `id`, `category`, `tag`, `prompt_count`, `created_at`
   - Data: 41 topics across 4 categories (TV Features, TV Models, TV Reviews & Brand, TV Sizes)
   - Migrated from static `clients/samsung/assets/tv_prompts.json`

3. **Updated Citation Sources to Use SEMrush Proxy**
   - Changed from direct SEMrush API calls to Supabase Edge Function
   - SEMrush Element ID: `28977430-d565-4529-97eb-2dfe2959b86b` (Source Visibility)
   - Data includes: domain, domain_type, mentions, citations, visibility
   - Model filter: omits CBF_model filter when "All Models" selected
   - Now loads 1,833 domains from SEMrush

4. **Updated Topic Filter to Use Supabase**
   - Changed from fetching `tv_prompts.json` file to querying `tv_topics` table
   - Topics load from: `${SUPABASE_URL}/rest/v1/tv_topics`
   - 41 topics organized by category in dropdown

#### New SEMrush API Endpoints Discovered
| Element ID | Purpose |
|-----------|---------|
| `28977430-d565-4529-97eb-2dfe2959b86b` | Source Visibility by Domain (used for Citation Sources) |
| `3c29aa85-4f06-4f14-a376-b02333c6e3fa` | Cited URLs with prompts |
| `3a16b2b2-b227-4a41-9ef2-9c657e64d47e` | Topics with citation counts |

#### Technical Details
- Edge Function handles CORS preflight (OPTIONS) and adds `Access-Control-Allow-Origin: *`
- Dashboard fetches 1,833 domains from SEMrush for Citation Sources table
- Topic filter loads 41 topics from Supabase tv_topics table

#### Files Modified
- `clients/samsung/dashboards/geo-dashboard.html`

#### New Supabase Resources
- Edge Function: `semrush-proxy`
- Table: `tv_topics`

---

### 2026-01-29: GEO Dashboard - Topic Filter and Citation Sources Table

**Summary:** Enhanced the GEO Performance Dashboard with a new Topic filter dropdown and a Citation Sources table. The Topic filter dynamically loads categories from tv_prompts.json, while the Citation Sources table shows which domains are citing Samsung, classified by type (Owned/Earned/Social/Competitor) with sentiment data.

#### What Was Done

1. **Added Topic Filter to Filter Bar:**
   - New dropdown filter positioned after the Model filter
   - Dynamically populated from `clients/samsung/assets/tv_prompts.json` tagTree
   - Categories: TV Features, TV Models, TV Reviews & Brand, Use Cases
   - Each category has child tags (e.g., OLED, QLED, Gaming TVs, Anti-Glare, etc.)
   - 58 total tags organized in hierarchical structure

2. **Added Citation Sources Table:**
   - New sortable table below the "Top Topics by Mentions" chart
   - Columns: Domain, Type, Citations, Mentions, Sentiment
   - Domain classification logic:
     - Owned: samsung.com
     - Earned: Major media sites (techradar, cnet, rtings, tomsguide, etc.)
     - Social: reddit.com, youtube.com
     - Competitor: lg.com, sony.com, tcl.com, hisense.com
   - Sentiment badge color-coded: green (positive), red (negative), gray (neutral)
   - Click column headers to sort ascending/descending
   - Shows top 10 domains by citation count

3. **New CSS Styles:**
   - `.citation-table` - Table styling with sortable headers and hover states
   - `.source-type-badge` - Colored badges for Owned/Earned/Social/Competitor types
   - `.sentiment-badge` - Colored badges for sentiment percentages

4. **New JavaScript Functions:**
   - `loadTopicFilter()` - Fetches tv_prompts.json and populates topic dropdown with optgroup hierarchy
   - `fetchCitationSources()` - Queries semrush_cited_pages and semrush_concept_mentions tables, aggregates by domain
   - `classifyDomain()` - Categorizes domains as owned/earned/social/competitor based on domain matching
   - `renderCitationTable()` - Renders the citation table with sorting controls
   - `setupTableSorting()` - Enables click-to-sort on table headers with ascending/descending toggle

#### Data Sources
- Topics: `clients/samsung/assets/tv_prompts.json` (tagTree with 58 tags across 4 categories)
- Citations: `semrush_cited_pages` Supabase table
- Sentiment: `semrush_concept_mentions` Supabase table aggregated by domain

#### Client Requirements Addressed
This implements the client's request to show:
- WHO is citing Samsung (domain names with type classification)
- WHAT topics are covered (topic filter connected to prompts data)
- Sentiment of coverage (positive/neutral/negative percentages)

#### Files Modified
- `clients/samsung/dashboards/geo-dashboard.html`

---

### 2026-01-29: Samsung AI Visibility Dashboard - Supabase Integration and D3.js Visualizations

**Summary:** Major update to the Samsung AI Visibility Dashboard connecting KPI cards to live Supabase data and creating 4 new D3.js visualization templates. Also updated existing components with live data fetching and documented what data is available vs. placeholder.

#### What Was Done

1. **Created Supabase Data Service Module** (`clients/samsung/dashboards/js/supabase-data.js`):
   - Centralized data fetching logic for dashboard components
   - Connects to Supabase REST API with anon key
   - Provides functions for KPIs, trends, and concept data

2. **Connected Main Dashboard KPI Cards to Live Data:**
   - KPI cards now fetch real metrics from Supabase
   - Fallback to placeholder data when Supabase unavailable
   - Maintains visual consistency during loading states

3. **Created 4 New D3.js Visualization Templates:**
   - `templates/brand-heatmap.html` - Brand Comparison Heatmap showing concept visibility across brands
   - `templates/sentiment-treemap.html` - Sentiment Treemap visualizing positive/neutral/negative distribution
   - `templates/model-radar.html` - Model Performance Radar Chart comparing AI models
   - `templates/citation-sankey.html` - Citation Flow Sankey Diagram showing content-to-citation paths

4. **Updated Line Charts with Live Data:**
   - Modified `templates/line-charts.html` to fetch data from Supabase
   - Added placeholder fallback when live data unavailable
   - Shows mentions trends over time by AI model

5. **Added Placeholder Data Notes:**
   - Sunburst chart section notes placeholder data status
   - Prompt rankings section indicates data requirements
   - Source analysis section documents pending GA4 integration

6. **Added D3.js to GEO Dashboard:**
   - Included D3.js v7 script tag in `dashboards/geo-dashboard.html`
   - Prepares for future Chart.js to D3.js migration
   - Currently uses Chart.js for all visualizations

7. **Updated Component Library:**
   - Extended `templates/base/components.html` with CSS for new visualization types
   - Added styles for heatmap, treemap, radar, and sankey components

8. **Updated Style Guide:**
   - Added documentation for new visualization components in `dashboards/style-guide.html`
   - Includes usage examples and configuration options

9. **Created Data Requirements Documentation:**
   - New file `DATA-REQUIREMENTS.md` documenting:
     - What Supabase data is available (concept mentions, cited pages, URL prompts)
     - What data is placeholder (referral traffic needs GA4, position data not in Supabase)
     - Integration status for each dashboard component

#### Data Status

| Data Type | Status | Source |
|-----------|--------|--------|
| Concept Mentions | Live | Supabase `semrush_concept_mentions` |
| Cited Pages | Live | Supabase `semrush_cited_pages` |
| URL Prompts | Live | Supabase `semrush_url_prompts` |
| Referral Traffic | Placeholder | Requires GA4 integration |
| Position Data | Placeholder | Not in current Supabase tables |
| Sentiment Data | Placeholder | SEMrush API available but not loaded |

#### Files Created
- `clients/samsung/dashboards/js/supabase-data.js`
- `clients/samsung/templates/brand-heatmap.html`
- `clients/samsung/templates/sentiment-treemap.html`
- `clients/samsung/templates/model-radar.html`
- `clients/samsung/templates/citation-sankey.html`
- `clients/samsung/DATA-REQUIREMENTS.md`

#### Files Modified
- `clients/samsung/templates/line-charts.html`
- `clients/samsung/templates/sunburst-prompts.html`
- `clients/samsung/templates/base/components.html`
- `clients/samsung/dashboards/style-guide.html`
- `clients/samsung/dashboards/geo-dashboard.html`
- `clients/samsung/dashboards/scom-overview.html`

---

### 2026-01-29: SEMrush Data Definitions Documented

**Summary:** Documented official SEMrush definitions for Concepts and Topics based on direct communication with SEMrush support. These definitions clarify how SEMrush measures AI visibility and why Samsung's higher Share of Voice is legitimate.

#### Key Definitions

**Concepts:**
- Specific qualities and features AI models use when describing products and brands
- Extracted from AI answers to tracked prompts (e.g., "clump-free application" for mascara, "safety features" for SUVs)
- Each concept-product relationship carries sentiment (positive, neutral, negative)

**Topics:**
- Used to estimate Volume for prompts (individual prompts are too specific to measure directly)
- Group related prompts that move in the same "semantic direction"
- Volume estimated from third-party data on real AI platform interactions + ML models
- Generated from SEMrush's database of 250+ million prompts

#### Current Data Status

The `semrush_concept_mentions` table now contains data for 5 brands:
| Brand | Share of Voice | Unique Concepts |
|-------|---------------|-----------------|
| Samsung | 44.8% | 12,884 |
| LG | 19.0% | 6,894 |
| TCL | 14.7% | 5,234 |
| Sony | 11.8% | 4,567 |
| Hisense | 9.8% | 3,778 |

Samsung's higher SoV is legitimate - it reflects that AI models discuss Samsung with more product attributes/features than competitors.

#### Files Modified
- `docs/build-log.md` (added detailed session entry)
- `clients/samsung/docs/data-definitions.md` (added official SEMrush definitions)

---

### 2026-01-29: GEO Performance Dashboard Created

**Summary:** Built a complete GEO (Generative Engine Optimization) Performance Dashboard for Samsung at `clients/samsung/dashboards/geo-dashboard.html`. This dashboard visualizes AI visibility metrics using live data from Supabase.

#### What Was Done

1. **Created self-contained dashboard** (`clients/samsung/dashboards/geo-dashboard.html`):
   - Single HTML file with embedded CSS and JavaScript
   - Samsung branding (fonts, colors, design tokens)
   - Responsive layout adapting to mobile/tablet/desktop

2. **Implemented 4 KPI Cards:**
   - Share of Voice (percentage of Samsung mentions vs competitors)
   - Visibility Score (composite metric of AI presence)
   - Sentiment Score (positive/neutral/negative breakdown)
   - Total Mentions (raw mention count)

3. **Built 5 Chart.js Visualizations:**
   - **Share of Voice donut chart** - Shows model breakdown for single brand, brand comparison when multiple brands present
   - **Sentiment Distribution donut chart** - Positive/neutral/negative split
   - **Visibility by AI Model bar chart** - SearchGPT, Google AI Overview, Google AI Mode
   - **Mentions Trend line chart** - Daily Samsung mentions over time
   - **Top Topics horizontal bar chart** - Top 10 concept categories by mention count

4. **Added Filter Bar:**
   - Date range selector: 7 days, 14 days, 30 days, All time
   - Model filter: All models, SearchGPT, Google AI Overview, Google AI Mode

5. **Integrated live Supabase data:**
   - Connects to `semrush_concept_mentions` table via REST API
   - Uses anon key for public read access
   - Queries ~58k rows spanning 2025-12-18 to 2026-01-29

#### Technical Decisions

| Decision | Rationale |
|----------|-----------|
| Chart.js over D3.js | Simpler API, faster implementation, sufficient for these chart types |
| Single HTML file | No build step required, easy to deploy, self-contained |
| Graceful single-brand handling | Currently only Samsung in database; ready for competitor data when added |

#### Files Created
- `clients/samsung/dashboards/geo-dashboard.html`

---

### 2026-01-29: Concept Mentions Data Pipeline Complete

**Summary:** Built and executed the complete data pipeline for SEMrush Concept Mentions, loading 57,831 rows into Supabase. This tracks how frequently specific concepts (topics) appear across AI model responses over time.

#### What Was Done

1. **Created Supabase table `semrush_concept_mentions`** via migration with schema:
   - Columns: id, concept, llm, mentions, date, fetched_at
   - Unique constraint on (concept, llm, date) for deduplication
   - Indexes on concept, llm, date for query performance

2. **Created fetch script** (`clients/samsung/fetch_concept_mentions.py`):
   - Fetches daily concept data from SEMrush API
   - Element ID: `e0f20fc8-83e6-4c66-a55b-23bf64a2ac6f` (Concept Mentions endpoint)
   - Iterates through date range and models

3. **Created load script** (`clients/samsung/load_concept_mentions.py`):
   - Loads JSON data to Supabase via REST API
   - Upserts on conflict to avoid duplicates

4. **Updated documentation:**
   - Added Concept Mentions endpoint to `semrush-api-endpoints.md`
   - Added table schema to `docs/data-definitions.md`

#### Results

| Metric | Value |
|--------|-------|
| Total rows loaded | 57,831 |
| Date range | 2025-12-18 to 2026-01-29 (43 days) |
| Models tracked | search-gpt (19,837), google-ai-mode (21,652), google-ai-overview (16,342) |

#### Major Finding
Concept count jumped approximately 5x around January 15 (from ~150 concepts/day to ~1000 concepts/day per model). This indicates either expanded SEMrush tracking or a significant change in AI model behavior.

#### Files Created
- `clients/samsung/fetch_concept_mentions.py`
- `clients/samsung/load_concept_mentions.py`
- `clients/samsung/data/concept_mentions.json`

---

### 2026-01-29: SEMrush Citations by Model API Testing

**Summary:** Tested and documented the SEMrush Citations by Model API endpoint. Discovered that the date filter has no effect on the response - it always returns the same 4 historical time points regardless of the date passed. Documented the endpoint structure, sample data, and trend observations.

#### Key Findings

1. **Endpoint**: Citations by Model (`c57c36a4-cb53-49c3-bbe6-6467881206e3`)

2. **Response Structure**:
   - Returns 20 rows (4 time points x 5 AI models)
   - Fields: `bar` (model name), `value` (citation count)
   - Models: UNSPECIFIED, GEMINI, GOOGLE_AI_OVERVIEW, GOOGLE_AI_MODE, CHAT_GPT

3. **Date Filter Behavior**:
   - The `date` filter has NO effect on the response
   - Tested with 2025-11-30, 2025-12-15, 2025-12-31 - all return identical data
   - Always returns same 4 historical time points regardless of date passed

4. **Sample Data (Latest Time Point)**:
   - UNSPECIFIED: 398,339 (50.1%)
   - GOOGLE_AI_OVERVIEW: 167,121 (21.0%)
   - GEMINI: 86,641 (10.9%)
   - CHAT_GPT: 73,616 (9.3%)
   - GOOGLE_AI_MODE: 70,961 (8.9%)

5. **Time Series Trends**:
   - GEMINI data only appears at time point 3+ (was 0 before)
   - CHAT_GPT citations are decreasing over time
   - UNSPECIFIED and Google models are increasing

#### Files Modified
- `clients/samsung/semrush-api-endpoints.md` (added endpoint documentation)
- `docs/build-log.md` (added session entry)

---

### 2026-01-28: Fetch Prompts Per URL from SEMrush

**Summary:** Created scripts to fetch prompts associated with each Samsung URL from the SEMrush URL Prompts API endpoint. This complements the Cited Pages data by showing which prompts each URL appears in. Loaded 31,283 unique prompts for top 100 US URLs and 5,951 prompts for top 100 TV URLs.

#### What Was Done

1. **Created `fetch_url_prompts.py`** - Script to fetch prompts per URL from SEMrush API
   - Uses Element ID `777346b4-6777-40fe-9356-4a5d63a70ef8` (URL Prompts endpoint)
   - Filter: `CBF_category=MENTIONS_TARGET` (different from Cited Pages which uses OWNED_BY_TARGET)
   - Rate limit: 600 requests/hour per workspace
   - Iterates through URLs and fetches prompts for each

2. **Created `load_url_prompts.py`** - Script to load JSON data into Supabase
   - Uses Supabase REST API with upsert on conflict (url, prompt_hash, country)
   - Transforms SEMrush data into normalized table format
   - Batch inserts for efficiency

3. **Created Supabase table `semrush_url_prompts`** with schema:
   - Columns: id, url, prompt, prompt_hash, topic, llm, volume, mentioned_brands_count, used_sources_count, serp_id, country, fetched_at
   - Unique constraint on (url, prompt_hash, country) for deduplication
   - Indexes on: url, prompt_hash, topic, llm

4. **Data Loaded:**
   - **Top 100 US URLs:** 31,283 unique prompts
   - **Top 100 TV URLs:** 5,951 unique prompts (filtered using HE filter)

5. **TV URL Filtering:** Applied canonical HE filter from Samsung Reporting Framework
   - Includes: tv, televisions, home-audio, projectors, micro-led, micro-rgb
   - Excludes: business, monitor, mobile, displays, smartphones, /phones/

#### Key Stats
- Total HE/TV URLs in US cited pages: 2,244 URLs with 11,760 prompts
- Top TV topics: "TVs and Screen Sizes" (739 prompts), "OLED vs QLED TVs" (254 prompts)

#### Files Created/Modified
- `clients/samsung/fetch_url_prompts.py` (created)
- `clients/samsung/load_url_prompts.py` (created)
- `clients/samsung/semrush-api-endpoints.md` (modified - added URL Prompts endpoint)
- `clients/samsung/docs/data-definitions.md` (modified - added table schema)

---

### 2026-01-28: Load SEMrush Cited Pages into Supabase

**Summary:** Created scripts to fetch and load SEMrush Cited Pages data into Supabase. Fetched 84,856 URLs from the SEMrush Cited Pages API endpoint (US market, samsung.com, OWNED_BY_TARGET filter) and loaded all data into the `semrush_cited_pages` Supabase table via REST API.

#### What Was Done

1. **Created `fetch_cited_pages.py`** - Script to fetch all cited pages from SEMrush API
   - Uses Element ID `9dd09001-1d0e-4d28-b675-53670a2af5b0` (Cited Pages endpoint)
   - Filters: CBF_country=us, CBF_category=OWNED_BY_TARGET, CBF_model=" " (all models)
   - Response structure: data in `blocks.data`, total count in `blocks.data_statistics[0].rowCount`
   - Saves results to `clients/samsung/data/cited_pages.json`

2. **Created `load_cited_pages.py`** - Script to load JSON data into Supabase
   - Uses Supabase REST API (not Python SDK)
   - Batch inserts with upsert on conflict (url, country, category)
   - Transforms SEMrush data into normalized table format

3. **Fetched 84,856 URLs** from SEMrush API and saved to JSON

4. **Loaded all data into Supabase** `semrush_cited_pages` table

5. **Updated documentation:**
   - Added Cited Pages endpoint to `semrush-api-endpoints.md`
   - Added Supabase table schema to `docs/data-definitions.md`

#### Files Created/Modified
- `clients/samsung/fetch_cited_pages.py` (created)
- `clients/samsung/load_cited_pages.py` (created)
- `clients/samsung/data/cited_pages.json` (created, 84,856 rows)
- `clients/samsung/.env` (modified - added SUPABASE_KEY)
- `clients/samsung/semrush-api-endpoints.md` (modified)
- `clients/samsung/docs/data-definitions.md` (modified)

---

### 2026-01-26: DataForSEO Related Keywords Script for Changan UK

**Summary:** Created a new Python script to fetch related keywords from the DataForSEO Related Keywords API for Changan UK keyword research. The script queries 6 seed keywords (brand terms: changan, changan uk, changan cars; category terms: chinese electric car uk, chinese ev, affordable ev uk), collects related keywords with SEO metrics, and outputs deduplicated results.

#### What Was Done

1. **Created `clients/changan-auto/dataforseo_related_keywords.py`** - Main script that:
   - Queries DataForSEO Related Keywords API with 6 seed keywords
   - Uses UK location code (2826), depth=4, includes SERP info and clickstream data
   - Saves raw JSON responses per seed keyword for archival
   - Combines and deduplicates all keywords into a single CSV

2. **Output files created:**
   - `clients/changan-auto/data/keywords/related_kw_{seed}.json` - 6 raw JSON files
   - `clients/changan-auto/data/keywords/changan_related_keywords.csv` - Combined deduplicated CSV

3. **CSV columns:** keyword, seed_keyword, depth, search_volume, cpc, competition, competition_level, keyword_difficulty, main_intent, serp_item_types

#### First Run Results
- 329 total keywords collected across 6 seeds
- 215 unique keywords after deduplication
- API cost: $0.15

---

### 2026-01-23: Component Documentation - 3-Way Alignment

**Summary:** Added 7 missing component sections to `templates/base/components.html` (~880 lines) and 6 new sections to `dashboards/style-guide.html` (~400 lines). Established a 3-way alignment pattern between dashboard, CSS library, and visual reference.

#### What Was Done

1. **Extended components.html** (1,124 to ~2,000 lines) with:
   - Header component (dashboard header with logo)
   - Filter Bar component (sticky filter with dropdowns, date picker, reset button)
   - Section Headers component (Prompt/Source section headers with title/subtitle)
   - Prompt KPI Grid component (4-column grid for prompt analysis cards)
   - Source KPI Row component (horizontal KPI cards for source analysis)
   - Source Donut Chart component (chart with legend and type badges)
   - Source Tables Grid component (2-column grid for domain/URL tables)
   - Competitor Analysis Table component (brand comparison table)

2. **Extended style-guide.html** (2,158 to ~2,550 lines) with:
   - Header section visual example
   - Filter Bar section with select states and action buttons
   - Section Headers with prompt/source variants
   - Source KPI Cards row
   - Source Donut Chart with type badges
   - Source Tables grid with domain/URL tables

3. **Established 3-Way Alignment Pattern:**
   - Dashboard (`scom-overview.html`) = production source of truth
   - `components.html` = extracted CSS for reuse
   - `style-guide.html` = visual reference with live examples

#### Files Modified
- `clients/samsung/templates/base/components.html`
- `clients/samsung/dashboards/style-guide.html`

---

### 2026-01-23: Sticky Global Filter Bar Implementation

**Summary:** Added a sticky global filter bar to the Samsung HE AI Visibility Dashboard with date range picker, platform/category/model filters, and reset functionality. Deployed to live server.

#### What Was Done

1. **Added sticky filter bar** at top of dashboard (below header):
   - Position: sticky with z-index 90, stays visible while scrolling
   - Background: white card with border (#e0e0e0)
   - Contains: Date Range picker, AI Platform dropdown, Category dropdown, Model Type dropdown, Reset button, Advanced Filters button

2. **Date Range Picker with presets:**
   - Last 7 Days, Last 30 Days (default), Last 90 Days, Last 12 Months
   - Custom Range option with calendar date inputs and Apply button

3. **Filter Dropdowns:**
   - AI Platform: All Platforms, ChatGPT, Gemini, Perplexity, Claude, Copilot
   - Category: All Categories, TV Features, TV Models, Reviews & Brand
   - Model Type: All Models, Neo QLED, QLED, OLED, Mini-LED, Micro LED, Crystal UHD, The Frame, Gaming TVs, Outdoor TV

4. **Reset button** clears all filters to defaults

5. **Visual feedback** with `.has-filter` class adding blue border when filter is active

6. **Removed section-level filter bars** from Prompt Analysis and Source Analysis sections (replaced by global sticky bar)

7. **Fixed gap** between header and filter bar (removed header margin-bottom)

#### Files Modified
- `clients/samsung/dashboards/scom-overview.html` - Main dashboard with filter bar
- `clients/samsung/dashboards/index.html` - Deployed version
- `clients/samsung/dashboards/test-filter-bar.html` - Standalone test file

#### Deployment
- Commit: `e2f640b` - "Samsung dashboard: sticky filter bar with date picker"
- Live URL: https://robotproof.io/samsung/ai-visibility/ (password protected)

---

### 2026-01-23: Prompt Analysis Section Redesign

**Summary:** Redesigned the Prompt Analysis section in the Samsung dashboard (scom-overview.html) to improve visual hierarchy and consistency with the style guide. Added a dedicated section header and replaced single-row KPI cards with double-stacked compact cards.

#### What Was Done

1. **Added Prompt Analysis section header** (line ~3201):
   - Title: "Prompt Analysis"
   - Subtitle: "Track prompt performance, citations, mentions, and product visibility"
   - Styled with top border divider, matching the Source Analysis section pattern

2. **Replaced KPI cards with double-stacked compact layout** (line ~3211):
   - Changed from single-row style to double-stacked `.kpi-card-compact` style per style guide
   - 4 cards in a single row using `.prompt-kpi-grid` (4-column grid)
   - Each card displays two stacked metrics with a divider between them

3. **KPI Card Content**:
   | Card | Top Metric | Bottom Metric |
   |------|------------|---------------|
   | 1 | Prompts with Citations (312, +24) | Without Citations (70, -8) |
   | 2 | Prompts with Mentions (847, -18) | Without Mentions (153, +12) |
   | 3 | Prompts with Products (594, +37) | Without Products (406, -15) |
   | 4 | Branded Prompts (234, +19) | Non-branded Prompts (766, +42) |

4. **CSS changes** (line ~2466):
   - Added `.prompt-kpi-grid` with `grid-template-columns: repeat(4, 1fr)`
   - Responsive breakpoints: 2 columns at 1200px, 1 column at 768px
   - Removed old `.prompt-kpi-row` and `.prompt-kpi-card` styles

5. **Removed old dual KPI cards** that were positioned below the sunburst chart

#### Section Order (Prompt Analysis)
1. Section header with title/subtitle
2. Double-stacked KPI cards (4 in a row)
3. Sunburst chart (Prompt Categories)
4. Prompt Rankings table

---

### 2026-01-23: Source Analysis Integration into Main Dashboard

**Summary:** Integrated the Source Analysis components from the test file into the main Samsung dashboard (scom-overview.html). This completes Stage 3 of the workflow - the components are now live in the production dashboard.

#### What Was Done

1. **Added CSS styles (~480 lines)** including:
   - Source type colors as CSS custom properties (--source-owned, --source-earned, etc.)
   - Source KPI cards with single-row styling
   - Donut chart container and legend styles
   - Source domain and URL tables with type badges
   - Competitor analysis table with brand color indicators
   - Responsive breakpoints at 1024px

2. **Added HTML section** after the Prompt Rankings Table:
   - Section header with "Source Analysis" title and subtitle
   - 4 KPI cards: Citations (1,247), Citation Gaps (89), Mentions (3,456), Source Visibility (67%)
   - AI Sources by Type donut chart with color-coded legend
   - 2-column grid: Source Domains table + Cited URLs table
   - Competitor Citation Analysis table (Samsung, LG, Sony, TCL, Hisense)

3. **Added D3.js interactive donut chart** with:
   - Hover animations (arc segment expansion on mouseover)
   - Legend-chart interaction (hover legend item highlights chart segment)
   - Center text updates dynamically on hover

#### 3-Stage Workflow Complete
- **Stage 1 (Test File):** COMPLETE - `test-source-analysis.html` created earlier
- **Stage 2 (Approval):** COMPLETE - Components reviewed and approved
- **Stage 3 (Integration):** COMPLETE - Components added to `scom-overview.html`

---

### 2026-01-23: Source Analysis Dashboard Components Test File

**Summary:** Created a test file for the Source Analysis section of the Samsung dashboard. This file contains 4 components that visualize how Samsung is cited and mentioned across different source types, domains, and competitor comparisons.

#### What Was Done

1. **Created `clients/samsung/dashboards/test-source-analysis.html`** with 4 components:

2. **Component 1: Source KPI Cards (4-column grid)**
   - Citations - Total number of times Samsung is cited
   - Citation Gaps - Competitor citations where Samsung is absent
   - Mentions - Total brand mentions across sources
   - Source Visibility - Percentage of sources mentioning Samsung

3. **Component 2: Source Type Pie Chart**
   - D3.js v7 donut chart with hover interactions
   - 5 source type categories: Owned, Earned, Social, Competitor, Other
   - Custom colors defined as CSS properties
   - Center label shows total sources

4. **Component 3: Source Domain and URL Tables**
   - 2-column grid layout
   - Domain table with type badges and citation counts
   - URL table with full paths and bar visualizations
   - Sortable by citation count

5. **Component 4: Competitor Analysis Section**
   - Comparison table with Samsung, LG, Sony, TCL, Hisense
   - Brand colors for visual indicators
   - Metrics: Citations, Mentions, Top Position, Visibility Score

#### Technical Details
- Uses existing style patterns from style-guide.html
- D3.js v7 for the donut chart with hover interactions
- Responsive design with breakpoints at 1024px
- Source type colors defined as CSS custom properties
- Competitor brand colors defined for visual indicators

#### 3-Stage Workflow Status
This follows the established 3-stage workflow:
- **Stage 1 (Test File):** COMPLETE - `test-source-analysis.html` created
- **Stage 2 (Approval):** PENDING - User review needed
- **Stage 3 (Template Extraction):** PENDING - After approval, extract to templates

---

### 2026-01-23: Data Definitions Documentation Page

**Summary:** Created a comprehensive Data Definitions documentation page for the Samsung dashboard that defines all metrics and KPIs used across the dashboard. This serves as a reference guide for understanding what each metric means, how it is calculated, and where the data comes from.

#### What Was Done

1. **Created `clients/samsung/dashboards/data-definitions.html`** - A standalone documentation page with:
   - Samsung-branded header with sticky positioning
   - Table of contents with anchor links for quick navigation
   - Six metric category sections

2. **Documented six metric categories:**
   - **Primary KPIs** - Share of Voice, Source Visibility, Referral Traffic, AI Visibility Score
   - **Dual-Metric KPIs** - Prompt Mentions, Top Product Position, Products Win/Lose, Position Distribution
   - **Prompt Tracking Metrics** - Topic Volume, Visibility Score, Position, Position Change
   - **Platform Metrics** - Platform Visibility, Platform Trend
   - **Trend Metrics** - Daily/Weekly Visibility, Period Comparison
   - **Position Metrics** - Average Position, Top 3 Rate

3. **Definition card structure includes:**
   - Metric name
   - Description (what it measures)
   - Calculation formula
   - Data source tag (Brandwatch, GA4, SEMrush, or Calculated)

4. **Styling:**
   - Uses Samsung design tokens (fonts, colors, spacing)
   - Matches dashboard visual style for consistency
   - Definition cards with color-coded badge types (KPI, Metric, Derived)
   - Data source tags color-coded by provider

#### Key Benefit
Team members and stakeholders can now look up any dashboard metric to understand exactly what it represents and how it is calculated.

---

### 2026-01-22: Path Standardization and Compact KPI Layout

**Summary:** Fixed template asset paths to match server directory structure, eliminating broken icons on deployed dashboard. Also redesigned compact KPI cards with a side-by-side layout for better space efficiency.

#### What Was Done

1. **Fixed asset path inconsistencies:**
   - Templates used `../assets/fonts/` and `../assets/` paths
   - Server has `./fonts/` and `./images/` directories at `/var/www/html/samsung/ai-visibility/`
   - Standardized all paths to relative (`./fonts/`, `./images/`)

2. **Files updated with correct paths:**
   - `templates/base/fonts.html` - Font URLs now use `./fonts/`
   - `templates/header.html` - Logo now uses `./images/logo.jpg`
   - `templates/kpi-cards.html` - KPI icons now use `./images/`

3. **Compact KPI card layout redesign:**
   - Changed from stacked layout to side-by-side (label+tooltip left, value+badge right)
   - Reduced padding from 20px to 16px
   - Reduced value font size from 42px to 28px
   - New structure: `.kpi-section-left` and `.kpi-section-right` instead of `.kpi-section-header` and `.kpi-section-metrics`

#### Key Benefit
Templates can now be assembled and deployed directly via scp without any path transformation.

---

### 2026-01-22: Samsung Dashboard Component Standardization (Continued)

**Summary:** Extended the global components system with KPI card type definitions, migrated templates to use global change badges, and improved accessibility. The style guide now serves as a complete component reference with visual examples and code snippets.

#### What Was Done (Latest)

1. **Added KPI card type definitions to `templates/base/components.html`**:
   - `.kpi-card-header` - Header KPI cards (160px min-height, with icon, centered layout)
   - `.kpi-card-compact` - Compact KPI cards (stacked sections with dividers, no icon)
   - `.kpi-row-4`, `.kpi-row-3`, `.kpi-row-2` - Grid layouts for different card counts

2. **Updated `dashboards/style-guide.html`** with:
   - Visual examples of both KPI card types (header and compact)
   - Comparison table showing properties of each type
   - Code examples for using the card types

3. **Standardized global components**:
   - Tooltip icon size: 18x18px with "?" icon
   - Change badges: `.change-badge` with variants (.increase, .decrease, .increase-good, .decrease-bad)
   - Green badge contrast improved: changed from #96d551 to #2e7d32 (better accessibility)

4. **Migrated templates to use global change badges**:
   - `templates/kpi-cards.html` - migrated from `.kpi-change` to `.change-badge`
   - `templates/kpi-cards-dual.html` - migrated from `.kpi-dual-item-change` to `.change-badge`

5. **Style guide deployed** to: https://robotproof.io/samsung/ai-visibility/style-guide.html

#### Key Decision
Two KPI card types serve different purposes: header cards (4 main metrics with icons) and compact cards (detailed breakdowns with stacked metrics). Templates now use global `.change-badge` classes instead of component-specific change indicators.

---

### 2026-01-22: Samsung Dashboard Component Standardization (Initial)

**Summary:** Created a global components system for reusable UI elements (tooltips, change badges) and a comprehensive style guide. This architectural change prevents style duplication across templates and ensures visual consistency.

#### What Was Done

1. **Created `templates/base/components.html`** - Global reusable styles:
   - `.tooltip-icon` + `.tooltip-text` - Standardized 18x18px tooltip icons
   - `.change-badge` - Change indicator badges with variants: `.increase`, `.decrease`, `.increase-good`, `.decrease-bad`, `.neutral`

2. **Updated `configs/scom-overview.json`** - Added `base/components.html` to base array for automatic inclusion

3. **Created `dashboards/style-guide.html`** - Comprehensive component reference showing color palette, typography, tooltips, badges, cards, and an inconsistency audit table

4. **Created `dashboards/test-prompt-gaps.html`** - Test file for new Prompt Gaps KPI card (stacked card with 2 metrics)

5. **Deployed style guide** to https://robotproof.io/samsung/ai-visibility/style-guide.html

#### Key Decision
Global reusable elements (tooltips, badges) go in `components.html`. Templates use global classes and only define component-specific layout. This prevents duplication and ensures consistency.

---

### 2026-01-21: MCP Authentication Setup (Critical Reference)

**Summary:** Documented the complete MCP authentication workflow after a painful debugging session. The key insight: Application Default Credentials can only hold ONE set of scopes at a time, so you must authenticate with ALL scopes (GA + GTM) in a single command.

#### The Core Problem
- `gcloud auth application-default login` overwrites the credentials file each time
- Both GA MCP and GTM MCP share the same credentials file
- If you auth with only GA scopes, GTM breaks. If you auth with only GTM scopes, GA breaks.

#### The Solution
1. **Always authenticate with ALL scopes in a single command** (see `auth-command.txt`)
2. **Use `gcloud.cmd` instead of `gcloud`** in PowerShell (avoids "Test-Path: Access is denied" error)
3. **Copy credentials file** from `AppData\Roaming\gcloud\` to `C:\Users\rober\` (Windows grpc workaround)

#### Quick Reference
- **Auth command:** See `C:\Development\General Analytics\auth-command.txt`
- **Source credentials:** `C:\Users\rober\AppData\Roaming\gcloud\application_default_credentials.json`
- **Target credentials:** `C:\Users\rober\application_default_credentials.json`
- **After auth:** Run `copy` command, then restart Claude Code

See `docs/build-log.md` for the complete troubleshooting guide with all scopes and error scenarios.

---

### 2026-01-21: Local GTM MCP Server Implementation

**Summary:** Replaced the problematic mcp-remote proxy for GTM with a locally-built Python MCP server. The new server uses the same architecture as analytics-mcp (FastMCP + Application Default Credentials) and provides 29 tools across 7 modules for comprehensive GTM management.

#### What Was Done

1. **Created local GTM MCP server:**
   - Location: `C:\Users\rober\gtm-mcp\`
   - Virtual environment: `C:\Users\rober\gtm-mcp-py313\`
   - Framework: FastMCP (same as analytics-mcp)
   - Authentication: Google Application Default Credentials

2. **Implemented 29 tools across 7 modules:**
   - `accounts` - List GTM accounts
   - `containers` - List, get, create containers
   - `workspaces` - List, get, create workspaces
   - `tags` - List, get, create, update, delete tags
   - `triggers` - List, get, create, update, delete triggers
   - `variables` - List, get, create, update, delete variables
   - `versions` - List, get, create, publish versions

3. **Google Cloud configuration:**
   - Enabled Tag Manager API in project 335937140210
   - Re-authenticated with GTM scopes: `tagmanager.readonly`, `tagmanager.edit.containers`, `tagmanager.publish`

4. **Updated `.mcp.json`:**
   - Replaced mcp-remote proxy configuration with direct local server
   - Uses uv to run the server from `C:\Users\rober\gtm-mcp\`

5. **Successful testing:**
   - Verified connection returns all 11 Changan Auto containers

#### Why This Change

The previous setup used mcp-remote as a proxy to connect to a remote GTM MCP server. This was causing connection issues. Building a local server eliminates the network dependency and provides a more reliable, faster connection.

---

### 2026-01-21: Nginx Basic Authentication for Samsung Dashboard

**Summary:** Added password protection to the Samsung dashboard at robotproof.io/samsung/ using Nginx basic authentication. Created htpasswd credentials file and updated Nginx configuration to require login before accessing the dashboard.

#### What Was Done

1. **Created htpasswd file:**
   - Location: `/etc/nginx/.htpasswd_samsung`
   - Username: `samsung`
   - Password: `Samsung2026`
   - Tool: `htpasswd` from `apache2-utils` package

2. **Updated Nginx configuration:**
   - File: `/etc/nginx/sites-enabled/robotproof.io`
   - Added `auth_basic "Samsung Dashboard";` directive
   - Added `auth_basic_user_file /etc/nginx/.htpasswd_samsung;` directive

3. **Session behavior:**
   - Credentials cached by browser until browser is closed
   - Client can refresh/navigate without re-entering password
   - No server-side session timeout (browser-managed)

#### Problem Solved
Special characters (`!`, `#`) in passwords caused shell escaping issues. Solution: used alphanumeric password.

---

### 2026-01-21: DigitalOcean Deployment Workflow

**Summary:** Established a deployment workflow for syncing Samsung dashboard files from local development to a DigitalOcean droplet at robotproof.io. Reorganized local folder structure to mirror server paths, updated asset references, and configured Nginx for static file serving.

#### What Was Done

1. **SSH Configuration:**
   - Using existing SSH config at `C:\Users\rober\.ssh\config` with host alias `digitalocean`
   - Key file: `~/.ssh/digitalocean`
   - Droplet IP: 104.248.11.188

2. **Deployment Command:**
   ```bash
   scp clients/samsung/dashboards/scom-overview.html digitalocean:/var/www/html/samsung/ai-visibility/index.html
   ```

3. **Local Folder Reorganization:**
   - Added `fonts/` and `images/` subdirectories to `clients/samsung/dashboards/`
   - Copied fonts from `assets/fonts/` to `dashboards/fonts/`
   - Copied images (logo.jpg, sov.jpg, source_visi.jpg, referral.jpg, ai-visi.jpg) to `dashboards/images/`
   - Renamed `ai visi.jpg` to `ai-visi.jpg` (removed space for URL compatibility)

4. **File Path Updates in Dashboard HTML:**
   - Font paths: `../assets/fonts/` to `./fonts/`
   - Image paths: `../assets/` to `./images/`

5. **Nginx Configuration:**
   - Updated `/etc/nginx/sites-enabled/robotproof.io`
   - Added static asset location block for images, fonts, CSS, JS
   - Added `/samsung/` location with `index index.html;` directive

#### Live URL
Dashboard accessible at: https://robotproof.io/samsung/ai-visibility/

---

### 2026-01-20: Sunburst Prompts Visualization & Prompt Rankings Table

**Summary:** Created two new interactive dashboard components for the Samsung S.com Overview dashboard: a D3.js sunburst chart for visualizing prompt categories with drill-down navigation, and a full-width data table showing prompt performance metrics. Both components work together as a filter system.

#### What Was Done

1. **Sunburst Prompts Visualization** (`templates/sunburst-prompts.html`):
   - Interactive D3.js sunburst chart (550x550px, fills half container width)
   - Drill-down navigation by clicking on segments
   - Breadcrumb navigation to go back up hierarchy
   - Subcategory chips for quick navigation
   - Sample prompts list that filters based on selection
   - Color-coded legend for 4 main categories: TV Features, TV Models, TV Reviews & Brand, TV Sizes
   - Acts as a filter for the prompt rankings table below

2. **Prompt Rankings Table** (`templates/prompt-rankings-table.html`):
   - Full-width data table showing prompt performance metrics
   - Columns: Prompt, Model, Topic, Topic Vol., Visibility (bar), Position (2 dates), Change, Product (2 dates)
   - Model icons: ChatGPT (green), Gemini (blue), Perplexity (dark), AI Overview (red)
   - Position color coding: green (1-3), amber (4-6), gray (7+)
   - Change indicators: up/down arrows, "New", "Lost" badges
   - Samsung products highlighted in blue
   - 600px max-height with scroll and sticky header
   - 20 sample prompts with category tags
   - Global `window.renderRankingsTable(filter)` function for filtering

3. **Dashboard Config Updated** - Added both components to `configs/scom-overview.json`

4. **Bug Fixes:**
   - Added `.container` wrapper to both templates for proper layout spacing
   - Added scoped tooltip CSS (`.sunburst-card .tooltip-icon`, `.prompt-rankings-card .tooltip-icon`) to fix tooltip conflicts in assembled dashboard

#### Test Files Created
- `dashboards/test-sunburst-prompts.html` - Standalone sunburst test
- `dashboards/test-prompt-rankings-table.html` - Standalone table test
- `dashboards/test-prompt-rankings.html` - Combined view (prototype)

#### Dashboard Component Count
The S.com Overview dashboard now has 6 components: header, kpi-cards, line-charts, platform-tables, sunburst-prompts, prompt-rankings-table

---

### 2026-01-20: Component-First Workflow Clarification (3 Stages)

**Summary:** Corrected the Component-First Development Workflow documentation to accurately reflect the 3-stage process: Test File -> Template -> Assembly. The previous 2-stage documentation was incomplete.

#### The Corrected 3-Stage Workflow

1. **Edit test file** (e.g., `dashboards/test-line-chart.html`) - Development sandbox for experimenting
2. **Approve and update template** (e.g., `templates/line-charts.html`) - Locked-in source of truth
3. **Run assembly script** - Generates final dashboard from templates

#### File Hierarchy
```
dashboards/test-*.html     <- Development sandbox (edit first)
        | (approve)
templates/*.html           <- Approved components (source of truth)
        | (assembly)
dashboards/scom-*.html     <- Generated output (never edit directly)
```

#### Key Lesson
The mistake made was editing `templates/line-charts.html` directly without first updating `dashboards/test-line-chart.html`. This skipped the testing stage. Always start changes in the test file.

---

### 2026-01-20: Samsung Template Assembly System

**Summary:** Created a template-first assembly system for Samsung dashboards. Templates are immutable HTML components stored in `clients/samsung/templates/`, with dashboard layouts defined by JSON configs. An assembly script combines templates into complete dashboards.

#### What Was Done

1. **Created template structure** at `clients/samsung/templates/`:
   - `base/fonts.html` - Samsung font declarations (@font-face rules)
   - `base/tokens.html` - CSS variables and base styles (colors, spacing, typography)
   - `header.html` - Header component with logo and title
   - `kpi-cards.html` - KPI cards component with tooltips
   - `line-charts.html` - Line charts component with insights boxes

2. **Created dashboard config** at `clients/samsung/configs/`:
   - `scom-overview.json` - Defines component order and assembly settings

3. **Created assembly script** at `clients/samsung/scripts/`:
   - `assemble_dashboard.py` - Reads config, combines templates, outputs complete HTML

4. **Key design principles:**
   - Templates are immutable once approved (no LLM regeneration)
   - Component order controlled via JSON config array
   - Easy to add future components (donut, stacked-bar, leaderboard, data-table)

#### How to Use

```bash
uv run clients/samsung/scripts/assemble_dashboard.py clients/samsung/configs/scom-overview.json
```

---

### 2026-01-20: Samsung KPI Cards Element (Client Specification)

**Summary:** Implemented 4 KPI cards for the Samsung S.com Overview dashboard based on client specification ("Ai reporting Client ask from Jason.pdf"). Added custom icons, tooltips, and 4-state change indicators.

#### What Was Done

1. **Created 4 KPI card designs:**
   - Share of Voice (65%) - Speech bubble with bar chart icon
   - Source Visibility (42%) - Monitor with eye icon
   - Referral Traffic (106,445) - Arrows converging to center icon
   - AI Visibility (91) - Brain with gear and sparkles icon

2. **Custom icon assets** (created by user with Nano Baana):
   - `clients/samsung/assets/sov.jpg` - Share of Voice icon
   - `clients/samsung/assets/source_visi.jpg` - Source Visibility icon
   - `clients/samsung/assets/referral.jpg` - Referral Traffic icon
   - `clients/samsung/assets/ai visi.jpg` - AI Visibility icon

3. **Styling implementation:**
   - Icons enlarged to 64x64px
   - Card content centered with flexbox
   - Labels bold using Samsung Sharp Sans font
   - Min-height 160px for consistent card sizing

4. **Tooltip feature:** CSS-only info tooltip (question mark icon, #8091df accent, hover reveals description modal with smooth fade)

5. **4-state change indicators** for period-over-period comparison:
   - N/A (grey #666666) - No comparison data
   - No Change (yellow #feb447) - Value unchanged
   - Increase (green #96d551) - Value went up
   - Decrease (red #ff4438) - Value went down

---

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
| 2026-02-02 | 5-slide structure per panel type (platform, concepts, citations, trends, competitive) | Each slide has single analytical focus for clearer storytelling; allows deeper drill-down per topic; better for stakeholder presentations with Q&A | 3-section single page (too dense), 10+ slides (too many), single overview page (not enough detail) |
| 2026-02-02 | Dual donut charts for Platform slide (Mentions vs Citations) | Clearly separates two distinct metrics that stakeholders often conflate; visual side-by-side comparison highlights platform differences | Single donut with toggle (loses comparison), stacked bar (harder to read percentages), table only (not visual enough) |
| 2026-02-02 | Horizontal stacked sentiment bars for Concepts slide | Shows sentiment breakdown per concept at a glance; horizontal layout fits more concept names; stacked bars show proportion not just counts | Vertical bars (truncates long concept names), treemap (loses granular % breakdown), pie charts per concept (too many charts) |
| 2026-02-02 | Include real AI quotes on Concepts slide | Provides concrete evidence for sentiment classifications; actionable for PR teams; shows what AI models actually say | Quotes on separate slide (loses context), no quotes (abstract data only), all quotes (overwhelming) |
| 2026-02-02 | Table format for Citations slide instead of cards | Tables are easier to scan for URLs; allows sorting by different columns; familiar format for stakeholders | Card layout (takes more space), list only (loses metrics), expandable rows (adds complexity) |
| 2026-02-02 | Multi-line time series for Trends slide | Shows multiple concepts on same chart for comparison; reveals data collection patterns (Jan 15 spike); standard format for time-based data | Separate charts per concept (hard to compare), area chart (overlapping obscures data), single aggregate line (loses concept-level detail) |
| 2026-02-02 | Branded vs Generic split for Competitive slide | Most actionable competitive insight - shows if Samsung wins on brand searches vs category searches; identifies defensive vs offensive opportunities | Overall SOV only (misses nuance), by AI model (less actionable), by sentiment (covered elsewhere) |
| 2026-02-02 | Separate HTML slides per panel type instead of single parameterized page | Each slide is self-contained for easy sharing and presentation; no URL parameters needed; slides can be opened offline; simpler implementation | Single page with URL parameters (harder to share, requires server), tabs in one page (less focused for presentations), PDF export (loses interactivity) |
| 2026-02-02 | Shared D3.js chart library (`slide-charts.js`) for all slides | Ensures visual consistency across slides; reduces code duplication; easier to update chart styling globally; follows DRY principle | Inline chart code per slide (duplication, inconsistency), Chart.js (less control for radar/treemap), separate libraries per chart type (larger bundle) |
| 2026-02-02 | Three visualizations per slide (Donut, Treemap, Radar) | Covers the three key analysis angles: platform distribution, concept sentiment, competitive comparison; fits on single screen; answers most stakeholder questions | More charts (overwhelming), fewer charts (incomplete picture), different chart types (less appropriate for data types) |
| 2026-01-30 | Create system architecture documentation page | Provides comprehensive technical reference for developers and stakeholders; documents database schema, RPC functions, component inventory, and data flow; reduces onboarding time; serves as living documentation | README file only (not visual enough), Confluence/Notion (external dependency), code comments only (scattered, hard to navigate), no documentation (tribal knowledge risk) |
| 2026-01-30 | Add Samsung Country Sites Citation Chart | Shows which Samsung regional sites (/us/, /uk/, etc.) and subdomains are being cited by AI models; helps identify if US site (target market) is appropriately represented; reveals unexpected citation patterns from international sites | Global domain filter only (hides country-level detail), separate dashboard page (loses context), text list instead of chart (harder to compare visually) |
| 2026-01-30 | Highlight US site in distinct color (Samsung blue) | US is the target market for this analysis; visual emphasis draws attention to key data point; other sites use consistent secondary colors for easy comparison | Same color for all bars (harder to spot US), gradient colors (implies ranking not category), no highlighting (key insight buried) |
| 2026-01-30 | Replace Topics bar chart with expandable tree table | Bar chart only showed aggregated mentions per category, hiding tag-level detail; tree table shows full hierarchy with all metrics (prompt count, citations, unique sources, sentiment); collapsed-by-default keeps UI clean while allowing drill-down | Keep bar chart with separate tag table (redundant), modal drill-down (extra clicks), nested accordions (harder to compare tags across categories) |
| 2026-01-30 | Remove "Sources by Topic with Sentiment" section | Redundant with new tree table which includes sentiment percentages per tag; reduces dashboard clutter; one combined view is easier to understand than two separate visualizations | Keep both sections (confusing, redundant data), merge into tree table tooltip (loses visibility), move to separate page (loses context) |
| 2026-01-30 | Pre-compute topic metrics in `summary_topics_tree` table | Aggregating across 249K rows on every request is slow; pre-computed summary enables instant tree table rendering; table structure matches UI hierarchy (category -> tags) | Compute on-the-fly (slow), cache in browser (stale data), use existing views (not optimized for this hierarchy) |
| 2026-01-30 | Migrate Cited URLs from SEMrush API proxy to direct Supabase queries | Eliminates dependency on SEMrush proxy Edge Function; enables filtering by date, topic, domain type, and domain; allows pagination without re-fetching all data; data already exists in `semrush_prompt_urls` table | Keep SEMrush proxy (adds latency, limited filtering), client-side filtering (slow for 249K rows), pre-aggregated views only (less flexible) |
| 2026-01-30 | Drop duplicate/ambiguous Supabase function overloads | PostgreSQL function overloading caused "ambiguous function call" errors when parameter counts matched but types differed; removing old overloads ensures the correct function is always called | Keep all overloads (continues to cause errors), rename functions (breaks existing code), use different parameter names (PostgreSQL matches by position not name) |
| 2026-01-30 | Add section-level domain filter for Cited URLs (separate from global filters) | Domain filtering for Cited URLs is a deep-dive action, not a global filter; keeps global filter bar focused on primary dimensions; shows top 30 domains grouped by type for quick selection | Global domain filter (affects all sections), free-text search (harder to use), no domain filter (limits analysis) |
| 2026-01-30 | Restructure data-definitions.html to match live GEO Dashboard | Original page had placeholder metrics from earlier design that no longer exist; documentation must reflect what users actually see; prevents confusion when stakeholders look up metric definitions | Keep old sections with [TBD] placeholders (confusing), create new documentation page (orphans the old one), document only in code comments (not accessible to non-developers) |
| 2026-01-30 | Add "Understanding the Data" explanatory section to data definitions | Non-technical stakeholders need context about what mentions vs citations mean, how sentiment is classified, and which AI platforms are tracked; reduces support questions; improves data literacy | Tooltips only (not enough space for explanation), separate glossary page (extra navigation), assume users understand (leads to misinterpretation) |
| 2026-01-30 | Use EXISTS subquery instead of JOINs for domain filtering in `get_negative_quotes` | JOINs on many-to-many relationships create cartesian products (1 quote x 20 domains = 20 duplicate rows); EXISTS subquery filters without multiplying rows; maintains DISTINCT quote results | Multi-table JOIN with GROUP BY (still slow, complex), DISTINCT on all columns (may miss legitimate duplicates), denormalize domain into quotes table (storage waste) |
| 2026-01-30 | Show "Prompt" instead of "Domain" in Quote Browser | Quotes come from AI responses to prompts, not from domains directly; showing the prompt that triggered the quote provides actionable context; domain can be derived from cited URLs if needed | Keep domain column (misleading, quotes don't come from domains), show both (too wide), show URL instead (too granular) |
| 2026-01-30 | Add domain filter as dropdown in PR Action Center rather than global filter bar | PR workflow is domain-specific (e.g., "what is RTINGS saying?"); keeps filter close to the data it affects; doesn't clutter global filter bar with PR-specific controls | Global domain filter (affects all sections, confusing), modal filter dialog (extra clicks), URL parameter (not discoverable) |
| 2026-01-30 | Group PR domain filter by domain type (Earned/Owned/Competitors/Other) | Makes it easy to find specific domain categories; shows negative count per domain to highlight problematic sources; mirrors the domain type filter logic used elsewhere | Flat alphabetical list (hard to find domains), separate filters per type (too many dropdowns), search box (overkill for ~20 domains) |
| 2026-01-30 | Show "Questions this section answers" directly on dashboard sections | Helps users understand what insights each section provides without documentation lookup; improves self-service analytics; reduces support questions about dashboard interpretation | Hide in tooltip only (users don't discover it), separate help page (extra clicks), no questions shown (users confused about purpose) |
| 2026-01-30 | Separate PR Action Center as dedicated section instead of inline with domain analysis | PR teams need focused workflow for managing negative mentions; export and pagination features are specific to this use case; keeps domain analysis cleaner for general visibility questions | Inline in domain section (cluttered), separate page (loses context), expandable panel (too hidden) |
| 2026-01-30 | Add Domain Type and Sentiment filters to global filter bar | These are the most common filtering dimensions for AI visibility analysis; enables quick switching between owned/earned/competitor views; sentiment filter lets users focus on positive or negative coverage | Section-level filters only (inconsistent UX), query parameters only (not discoverable), preset buttons (not flexible enough) |
| 2026-01-30 | Use distinct prompts as the "mentions" metric instead of joined row counts | Prompts are the meaningful unit of measurement (a prompt is a question asked to an AI); URL counts inflate when the same prompt cites multiple URLs; concept counts inflate when the same prompt discusses multiple concepts; prevents misleading metrics in the dashboard | Keep row counts (wildly inaccurate), use distinct URLs (measures citations not questions), use distinct concepts (measures topics not questions) |
| 2026-01-30 | Rewrite `refresh_single_domain_sentiment_v2()` with two-step aggregation | First get distinct prompts per domain, then join with concepts for sentiment breakdown; prevents cartesian product explosion; counts DISTINCT values instead of rows | Fix the original join with GROUP BY (still slow), create materialized view (adds maintenance complexity), denormalize data into single table (storage inefficient) |
| 2026-01-30 | Document demo questions before building UI | Ensures dashboard answers real client questions; reveals required data queries before implementation; validates that views and tables have sufficient data; prevents building features nobody asked for | Build UI first and hope it answers questions (risky), informal requirements (leads to scope creep), wait for client feedback (delays delivery) |
| 2026-01-30 | Structure UI requirements by page/view with sample queries | Clear mapping between UI components and data sources; developers know exactly which query powers each chart; makes performance optimization targets explicit | Unstructured requirements doc (hard to implement), mockups only (don't show data requirements), code comments only (scattered, incomplete) |
| 2026-01-29 | Supabase Edge Function proxy for SEMrush API calls | Browser cannot call SEMrush API directly due to CORS; Edge Function adds CORS headers and proxies requests; keeps API key secure on server side | Direct browser calls (CORS blocked), backend proxy server (extra infrastructure), client-side CORS workarounds (unreliable) |
| 2026-01-29 | Migrate Topic filter data from static JSON to Supabase table | Enables dynamic updates without redeploying dashboard; consistent data source pattern with other dashboard components; easier to manage via Supabase dashboard | Keep static JSON (requires file deployment for updates), hardcode in JavaScript (hard to maintain) |
| 2026-01-29 | Disable JWT verification on semrush-proxy Edge Function | Dashboard is public-facing; no authentication required for read-only data; simplifies frontend code | Require JWT (adds login flow complexity), IP whitelisting (doesn't work for public dashboard) |
| 2026-01-29 | D3.js for advanced visualizations (heatmap, treemap, radar, sankey) | These chart types require low-level control D3 provides; Chart.js lacks built-in support for sankey/treemap; D3 already used in sunburst component | Chart.js (no sankey/treemap support), commercial libraries (cost, dependencies), custom Canvas (too much work) |
| 2026-01-29 | Centralized Supabase data service module instead of inline fetch calls | Single source of truth for API calls; easier to update credentials; enables consistent error handling and caching across components | Inline fetch in each component (code duplication), server-side proxy (adds complexity), GraphQL (overkill) |
| 2026-01-29 | Placeholder fallback pattern for live data components | Graceful degradation when Supabase unavailable; allows dashboard to render during development; clear visual indicator of data status | Hard failure on API error (poor UX), loading spinners only (confusing), no fallback (blank charts) |
| 2026-01-29 | Keep Chart.js in GEO dashboard but add D3.js script | GEO dashboard works well with Chart.js; adding D3 script prepares for future migration without breaking current functionality | Full D3 rewrite now (risky, time-consuming), remove D3 entirely (limits future options) |
| 2026-01-29 | Chart.js for GEO dashboard instead of D3.js | Simpler API, faster implementation, sufficient for donut/bar/line charts; D3.js overkill for these standard chart types | D3.js (more complex, slower development), commercial charting library (unnecessary cost/dependencies) |
| 2026-01-29 | Single self-contained HTML file for GEO dashboard | No build step, easy deployment, works as static file, all dependencies via CDN | Modular templates (adds complexity for simple dashboard), build system (overkill for single page) |
| 2026-01-29 | Supabase anon key for dashboard data access | Public read-only access sufficient for concept mentions data, no sensitive data exposed, simplifies frontend code | Server-side proxy (adds complexity), authenticated access (requires login flow) |
| 2026-01-28 | Use MENTIONS_TARGET filter for URL Prompts (vs OWNED_BY_TARGET for Cited Pages) | MENTIONS_TARGET returns prompts where the URL is mentioned; OWNED_BY_TARGET returns prompts where Samsung owns the cited source; different filters serve different analytical purposes | Using same filter for both (would miss mention data), querying all categories (too much noise) |
| 2026-01-28 | Apply HE filter from Samsung Reporting Framework for TV URL subset | Canonical filter already validated for Samsung HE reporting; ensures consistency across projects | Custom TV filter (risk of missing URLs or including non-TV), manual URL selection (not scalable) |
| 2026-01-28 | Supabase REST API for data loading instead of Python SDK | REST API is simpler, no additional SDK dependencies, direct HTTP calls work reliably | Python SDK (adds dependencies, version compatibility issues), direct SQL (requires database connection, less portable) |
| 2026-01-23 | 3-way component documentation pattern: dashboard -> components.html -> style-guide.html | Ensures all UI elements are documented for reuse; CSS extraction enables importing styles into new dashboards; visual reference helps designers and stakeholders understand available components | Document only in code comments (not visual), use CSS framework like Bootstrap (overrides Samsung branding), document only in style-guide.html (no CSS reuse) |
| 2026-01-23 | Global sticky filter bar instead of section-level filters | Single point of control is easier for users to understand; eliminates confusion about filter scope; reduces code duplication; simplifies state management | Section-level filters (confusing scope, duplicated code), floating filter panel (takes up too much space), sidebar filters (requires layout change) |
| 2026-01-23 | Date picker with presets + custom range | Presets cover 80% of use cases quickly; custom range provides flexibility without cluttering the UI; Apply button prevents accidental submissions | Calendar-only (slower for common ranges), presets-only (inflexible), always-visible calendar (takes too much space) |
| 2026-01-22 | Standardize template paths to `./fonts/` and `./images/` (relative from dashboard root) | Matches server directory structure exactly; eliminates need for path transformation during deployment; templates work identically locally and on server | Keep `../assets/` paths and transform during assembly (adds complexity), use absolute server paths (breaks local testing) |
| 2026-01-22 | Compact KPI card side-by-side layout (label left, value right) | Better space efficiency; cleaner visual hierarchy; allows more metrics per card without vertical scrolling | Keep stacked layout (wastes vertical space), grid layout (too complex for 2-item rows) |
| 2026-01-22 | Two KPI card types: `.kpi-card-header` (with icon) and `.kpi-card-compact` (stacked sections) | Different use cases: header cards for main dashboard metrics, compact cards for detailed breakdowns; clear visual hierarchy | Single card type (too rigid), many card variants (overcomplicated), inline overrides (inconsistent) |
| 2026-01-22 | Change green badge color from #96d551 to #2e7d32 | Improved contrast ratio for accessibility; #96d551 was too light on white backgrounds | Keep original green (poor accessibility), use different badge design (inconsistent with palette) |
| 2026-01-22 | Migrate templates to use global `.change-badge` classes | Single source of truth for badge styles; easier maintenance; guarantees consistency across all templates | Keep component-specific classes (duplication), inline styles (unmaintainable) |
| 2026-01-22 | Global components.html for reusable UI elements (tooltips, badges) | Prevents style duplication across templates; single source of truth for shared styles; ensures visual consistency | Inline styles in each template (duplication), CSS framework import (overkill), copy-paste styles (drift over time) |
| 2026-01-22 | Standardize tooltip size to 18x18px globally | Matches all existing template implementations; consistent visual appearance; easier to maintain | Different sizes per component (inconsistent), larger tooltips (too prominent), smaller tooltips (hard to click) |
| 2026-01-21 | Single auth command with ALL scopes (GA + GTM) | ADC file gets overwritten on each auth; separate auth breaks the other MCP server | Separate auth per server (breaks other server), service accounts per server (overkill), multiple credential files (MCP servers don't support custom paths easily) |
| 2026-01-21 | Use `gcloud.cmd` instead of `gcloud` in PowerShell | The .ps1 wrapper script throws "Test-Path: Access is denied" error causing auth to hang indefinitely | Using `gcloud` directly (hangs), running in CMD instead (less convenient), WSL (adds complexity) |
| 2026-01-21 | Copy credentials file to user home directory | grpc library on Windows has issues reading from AppData\Roaming path; copying to C:\Users\rober\ works | Fix grpc configuration (unclear how), use environment variable (didn't work reliably) |
| 2026-01-21 | Local GTM MCP server instead of mcp-remote proxy | Eliminates network dependency and connection issues; faster response; full control over implementation; same architecture as analytics-mcp for consistency | mcp-remote proxy (unstable connections), official remote server (network dependent), REST API directly (no MCP integration) |
| 2026-01-21 | FastMCP framework for GTM server | Same framework as analytics-mcp for consistency; simple decorator-based tool definition; handles MCP protocol automatically | Raw MCP protocol (more boilerplate), other frameworks (inconsistent with existing setup) |
| 2026-01-21 | Application Default Credentials for GTM auth | Consistent with analytics-mcp; single credential file works for both servers; no per-server OAuth tokens to manage | OAuth per-server (more files to manage), service account (overkill for personal use) |
| 2026-01-21 | Nginx basic auth for Samsung dashboard protection | Simple to implement, no code changes needed, browser handles credential caching, sufficient for client demo | Full login system (overkill), IP whitelisting (client IP may change), VPN (adds friction for client) |
| 2026-01-21 | Alphanumeric password to avoid shell escaping issues | Special characters (!#) cause bash interpretation problems; alphanumeric is simpler and sufficient for demo security | Complex escaping sequences (error-prone), interactive htpasswd prompt (harder to document) |
| 2026-01-21 | SCP-based deployment to DigitalOcean droplet | Simple, direct file transfer; uses existing SSH config; no CI/CD overhead for single-file dashboards | rsync (overkill for single files), Git-based deployment (unnecessary complexity), FTP (less secure) |
| 2026-01-21 | Mirror local folder structure to server structure | Enables scp of entire directories without path translation; same relative paths work locally and on server | Keep assets separate (requires path changes per environment), symlinks (platform-dependent) |
| 2026-01-21 | Remove spaces from filenames (ai visi.jpg to ai-visi.jpg) | Spaces in URLs cause encoding issues (%20); hyphens are URL-safe and more readable | URL encoding (ugly URLs), underscores (less common convention) |
| 2026-01-20 | D3.js sunburst chart for prompt category visualization | Enables hierarchical drill-down navigation, compact display of nested categories, intuitive click-to-explore interaction | Flat dropdown (cannot show hierarchy), tree view (takes more space), nested accordions (requires more clicks) |
| 2026-01-20 | Global `window.renderRankingsTable(filter)` function for cross-component filtering | Allows sunburst to filter table without tight coupling, simple function call interface | Custom events (more complex), direct DOM manipulation (brittle), shared state object (overkill) |
| 2026-01-20 | Scoped tooltip CSS selectors (`.sunburst-card .tooltip-icon`) | Prevents tooltip style conflicts when multiple components assembled into single dashboard | Global tooltip classes (cause conflicts), inline styles (hard to maintain), unique class prefixes (verbose) |
| 2026-01-20 | Component-First Development Workflow (3 stages): Test File -> Template -> Assembly | Test files are sandboxes for experimentation; templates are locked-in source of truth; assembly generates output; skipping stages leads to untested code or lost changes | Editing templates directly (skips testing), editing generated dashboards (changes lost on reassembly) |
| 2026-01-20 | Template-first assembly system with immutable templates | Prevents unintended changes to approved components, enables reproducible builds, separates layout (config) from content (templates) | LLM regeneration each time (inconsistent results), monolithic HTML files (hard to maintain) |
| 2026-01-20 | CSS-only tooltips for KPI cards | No JavaScript required, simpler implementation, works in static HTML | JavaScript-based tooltips (unnecessary complexity for hover effect) |
| 2026-01-20 | 4-state change indicators (N/A, No Change, Increase, Decrease) | Covers all real-world comparison scenarios clearly | 2-state (up/down only, cannot represent missing data or unchanged) |
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
- **Samsung QLED 5-Slide Prototype** - New 5-slide presentation structure in `clients/samsung/slides/qled/`:
  - `1-platform.html` - Dual donut charts (Mentions vs Citations by AI platform)
  - `2-concepts.html` - Horizontal stacked sentiment bars + real AI quotes
  - `3-citations.html` - Table of top cited Samsung URLs with prompts
  - `4-trends.html` - Multi-line time series of concept mentions over time
  - `5-competitive.html` - Branded vs Generic prompt comparison (Samsung vs competitors)
- **New Chart Functions in `slide-charts.js`:** `renderConceptBars()`, `renderCitationList()`, `renderTrendLines()`, `renderDualCompetitorBars()`, `renderSimpleBars()`; updated `renderDonut()` to accept custom center label
- **Shared Slide CSS** - `clients/samsung/slides/css/slides.css` for consistent styling across all slides
- **Samsung TV Panel Type Slides (Initial)** - 6 HTML presentation slides (`clients/samsung/slides/`) for panel-type-specific analysis: Gaming TVs, QLED, Sports TVs, OLED, Mini-LED, Micro RGB; each slide shows Platform Breakdown donut chart, Concepts & Sentiment treemap, and Competitive Analysis radar chart
- **Shared D3.js Chart Library** - `clients/samsung/slides/js/slide-charts.js` with reusable functions: `renderDonut()`, `renderTreemap()`, `renderRadar()` for consistent chart rendering across slides
- **Samsung Country Sites Citation Analysis Chart** - New horizontal bar chart in GEO Dashboard showing citation counts per Samsung country site (/us/, /uk/, /de/, etc.) and subdomain (design.samsung.com, developer.samsung.com); US site highlighted in Samsung blue; top 15 sites displayed; tooltips show citation and unique URL counts
- **New Supabase RPC Function `get_samsung_country_citations()`** - Extracts country codes from samsung.com URLs and identifies subdomains; returns citation counts and unique URL counts per site; filters for Owned domain type

#### Changed
- **Topics Section UI Overhaul** - Replaced "Top Topics by Mentions" Chart.js bar chart with expandable tree table showing full topic hierarchy (4 categories with child tags) and all metrics (prompt count, citations, unique sources, sentiment percentages); categories collapsed by default with click-to-expand; added Expand All / Collapse All buttons

#### Removed
- **Sources by Topic with Sentiment Section** - Redundant with new Topics tree table which includes sentiment data per tag; removed `fetchSourcesByTopic()`, `renderSourcesByTopicTable()`, `setupSourcesByTopicSorting()`, `renderTopicsChartFromData()` functions

#### Added
- **New Supabase Table `summary_topics_tree`** - Pre-computed topic metrics table with columns: category, tag, prompt_count, citations, unique_sources, positive_pct, neutral_pct, negative_pct
- **New Supabase RPC Function `get_topics_tree_data()`** - Queries summary_topics_tree table for tree table rendering
- **New JavaScript Functions** in geo-dashboard.html: `fetchTopicsTreeData()`, `renderTopicsTree()`, `toggleTopicCategory()`, `expandAllTopics()`, `collapseAllTopics()`
- **New CSS Classes** for tree table: `.topic-category-row`, `.topic-tag-row`, `.expand-icon`

#### Fixed
- **PR Action Center Filters** - Fixed `get_negative_quotes` Supabase function missing `date` field in return type; removed duplicate/ambiguous function overloads (`get_negative_quotes(integer, text, text)` and `get_concept_sentiment_summary(integer)`); filters and quotes table now work correctly with topic filtering

#### Changed
- **Cited URLs Table Migrated to Supabase** - Previously fetched from SEMrush API via proxy, now queries `semrush_prompt_urls` table directly; responds to global filters (Date Range, Topic, Domain Type); added section-level Domain filter dropdown with top 30 domains grouped by type; added pagination (15 items per page)

#### Added
- **New Supabase RPC Functions for Cited URLs:**
  - `get_cited_urls(p_limit, p_offset, p_date_from, p_date_to, p_tag, p_domain_type, p_domain)` - returns aggregated URL data with pagination
  - `get_cited_urls_count(...)` - returns total count for pagination
  - `get_top_cited_domains(p_limit)` - returns top domains grouped by type for filter dropdown
- **New JavaScript Functions** in geo-dashboard.html: `fetchCitedUrls()`, `fetchCitedUrlsCount()`, `loadCitedUrlsDomainFilter()`, `reloadCitedUrls()`, `changeCitedUrlsPage()`

#### Changed
- **Data Definitions Page Restructured** (`clients/samsung/dashboards/data-definitions.html`):
  - Replaced outdated sections (Dual-Metric KPIs, Prompt Tracking, Position Metrics) with new sections matching live GEO Dashboard
  - Added 7 new metric sections: Primary KPIs, Domain Sentiment Analysis, Citation Metrics, Concept Analysis, Platform Metrics, Trend Metrics, PR Action Center
  - Added "Understanding the Data" explanatory section with info boxes for Mentions vs Citations, Sentiment Classification, Data Freshness, Position/Ranking, AI Model Coverage
  - Updated all formulas to match actual JavaScript calculations in `supabase-data.js`
  - Replaced all `[TBD]` and `[Description to be provided]` placeholders with actual content
  - Updated data source badges to show "Semrush" consistently
  - Updated Table of Contents to match new structure
  - Fixed back navigation link to point to `geo-dashboard.html`

#### Fixed
- **Critical:** PR Action Center cartesian join bug in `get_negative_quotes` RPC - joining concept_prompts to prompt_urls to domains caused 1 quote x 20 domains = 20 duplicate rows, showing only 1 concept ("interface") with repeated quotes
- Rewrote `get_negative_quotes` to query `semrush_concept_prompts` directly with DISTINCT, added optional `p_domain` parameter using EXISTS subquery for filtering without duplicates
- Quote Browser "Domain" column renamed to "Prompt" (quotes don't come from domains, they come from AI responses to prompts)
- "Negative Coverage by Source" chart renamed to "Prompts with Most Negative Quotes" (more accurate description)

#### Added
- **PR Action Center Domain Filter** - New dropdown to filter negative quotes by domain:
  - Domains grouped by type (Earned, Owned, Competitors, Other)
  - Shows negative mention count next to each domain
  - `loadPRDomainFilter()` function populates dropdown from `summary_domain_sentiment`
  - `reloadPRActionCenter()` function reloads only PR section when filter changes
- **New Supabase RPC functions:**
  - `get_negative_quotes(p_limit, p_domain)` - Returns unique negative quotes with optional domain filter
  - `get_concept_sentiment_summary(p_limit)` - Aggregates concepts by sentiment counts

#### Added (previous)
- **GEO Dashboard Sentiment Analysis Enhancement** - Major update to `clients/samsung/dashboards/geo-dashboard.html`:
  - Domain Sentiment Analysis section with stacked bar chart and domain type comparison
  - PR Action Center section with negative concepts chart, negative sources chart, quote browser with pagination, and CSV export
  - Concept Analysis section with positive concepts chart and sentiment mix visualization
  - Enhanced Topic Deep Dive section with sentiment breakdown per tag
  - Domain Type filter (Owned/Earned/Competitors/Other) in global filter bar
  - Sentiment filter (Positive/Neutral/Negative) in global filter bar
  - "Questions this section answers" displays on each new section
  - 8 new data fetching functions (fetchDomainSentiment, fetchNegativeQuotes, fetchConceptSentiment, etc.)
  - 9 new chart rendering functions (renderDomainSentimentChart, renderDomainTypeChart, etc.)
  - ~15 new CSS classes for section headers, question displays, tooltips, pagination, export buttons
  - File expanded from ~1940 lines to ~3022 lines

#### Fixed
- **Critical:** Cartesian product bug in `refresh_single_domain_sentiment()` - joining `semrush_prompt_urls` with `semrush_concept_prompts` on `prompt` column created up to 251K rows per prompt (651 URLs x 386 concepts), inflating "mentions" counts from thousands to millions
- Created `refresh_single_domain_sentiment_v2()` with correct two-step aggregation: first get distinct prompts citing a domain, then join with concepts for sentiment breakdown
- Refreshed all 12 key domains in `summary_domain_sentiment` table with corrected counts
- RTINGS example: positive "mentions" corrected from 4,958,931 to 358 (actual prompt count)

#### Added (previous)
- Dashboard Demo Questions documentation (`clients/samsung/docs/dashboard-demo-questions.md`) - 60+ questions across 10 categories for validating dashboard capabilities
- Dashboard UI Requirements documentation (`clients/samsung/docs/dashboard-ui-requirements.md`) - Complete UI specification including filters, charts, tables, page structure, and sample queries
- Supabase Edge Function `semrush-proxy` - Proxies SEMrush API calls to avoid browser CORS issues
- Supabase table `tv_topics` - Stores 41 TV topics across 4 categories for Topic filter dropdown
- Three new SEMrush API endpoints discovered: Source Visibility by Domain, Cited URLs, Topics with citation counts
- Topic filter in GEO Dashboard filter bar - now loads from Supabase `tv_topics` table (migrated from static JSON)
- Citation Sources table in GEO Dashboard - now fetches live data from SEMrush via proxy (1,833 domains)
- Domain classification logic: Owned (samsung.com), Earned (media sites), Social (reddit, youtube), Competitor (lg, sony, etc.)
- Table sorting functionality with ascending/descending toggle on column headers
- Supabase data service module (`clients/samsung/dashboards/js/supabase-data.js`) - Centralized live data fetching for dashboard components
- 4 new D3.js visualization templates for Samsung dashboard:
  - `templates/brand-heatmap.html` - Brand Comparison Heatmap for concept visibility across brands
  - `templates/sentiment-treemap.html` - Sentiment Treemap for positive/neutral/negative distribution
  - `templates/model-radar.html` - Model Performance Radar Chart comparing AI models
  - `templates/citation-sankey.html` - Citation Flow Sankey Diagram for content-to-citation paths
- D3.js v7 script tag added to `geo-dashboard.html` for future Chart.js migration
- CSS for new visualization types in `templates/base/components.html`
- Documentation for new visualization components in `style-guide.html`
- `DATA-REQUIREMENTS.md` documenting available vs. placeholder data across dashboard

#### Changed
- Main dashboard KPI cards now fetch live data from Supabase (with placeholder fallback)
- Line charts updated to fetch live mention trends from Supabase
- Sunburst, prompt rankings, and source analysis sections now display placeholder data notes
- GEO dashboard already connects to live Supabase data (uses Chart.js)

#### Notes
- Some data remains placeholder: referral traffic (needs GA4), position data (not in Supabase)
- All new visualizations have sample data fallback when Supabase unavailable
- GEO dashboard uses Chart.js but D3 migration prepared

#### Added (previous)
- SEMrush data definitions documentation (from SEMrush support):
  - Official definitions for Concepts (product attributes/features AI uses to describe products)
  - Official definitions for Topics (semantic groupings used to estimate prompt volume)
  - Topic volume methodology: third-party AI platform interaction data + ML models from 250M+ prompt database
  - Current data stats: 5 brands, 3 AI models, 43 days, ~152k records
  - Samsung SoV explanation: higher SoV reflects more product attributes discussed by AI, not data bias
- GEO Performance Dashboard for Samsung (`clients/samsung/dashboards/geo-dashboard.html`):
  - 4 KPI Cards: Share of Voice, Visibility Score, Sentiment Score, Total Mentions
  - 5 Chart.js visualizations: Share of Voice donut, Sentiment Distribution donut, Visibility by Model bar chart, Mentions Trend line chart, Top Topics horizontal bar chart
  - Filter bar with date range selector (7/14/30 days, all time) and model filter
  - Live Supabase integration querying `semrush_concept_mentions` table (~58k rows)
  - Samsung branding: fonts, colors, design tokens
  - Responsive layout for mobile/tablet/desktop
  - Graceful single-brand handling (ready for competitor data when added)
- SEMrush Concept Mentions data pipeline for Samsung:
  - Created `clients/samsung/fetch_concept_mentions.py` - fetches daily concept data from SEMrush API (Element ID: e0f20fc8-83e6-4c66-a55b-23bf64a2ac6f)
  - Created `clients/samsung/load_concept_mentions.py` - loads JSON to Supabase with upsert
  - Supabase table `semrush_concept_mentions` with columns: id, concept, llm, mentions, date, fetched_at
  - Unique constraint on (concept, llm, date) for deduplication
  - Indexes on concept, llm, date for query performance
  - **57,831 rows loaded** covering 43 days (2025-12-18 to 2026-01-29)
  - 3 models tracked: search-gpt, google-ai-mode, google-ai-overview
  - Major finding: concept count jumped ~5x around Jan 15 (from ~150/day to ~1000/day per model)
- Concept Mentions endpoint added to `clients/samsung/semrush-api-endpoints.md`
- `semrush_concept_mentions` table schema added to `clients/samsung/docs/data-definitions.md`
- SEMrush Citations by Model endpoint documentation (`clients/samsung/semrush-api-endpoints.md`):
  - Element ID: `c57c36a4-cb53-49c3-bbe6-6467881206e3`
  - Returns 20 rows (4 time points x 5 AI models): UNSPECIFIED, GOOGLE_AI_OVERVIEW, GEMINI, CHAT_GPT, GOOGLE_AI_MODE
  - Date filter has no effect (returns fixed time series)
  - Sample data: UNSPECIFIED leads with 398,339 citations (50.1%), Google products combined 40.8%, ChatGPT 9.3%
  - Trend analysis: Google AI citations growing, ChatGPT declining, Gemini is recent addition
- SEMrush URL Prompts data pipeline for Samsung (`clients/samsung/fetch_url_prompts.py`, `clients/samsung/load_url_prompts.py`):
  - Fetches prompts per URL from SEMrush API (Element ID: 777346b4-6777-40fe-9356-4a5d63a70ef8)
  - Filter: MENTIONS_TARGET category (prompts where URL is mentioned)
  - Rate limit: 600 requests/hour per workspace
  - Loaded 31,283 prompts for top 100 US URLs, 5,951 prompts for top 100 TV URLs
- Supabase table `semrush_url_prompts` with columns: id, url, prompt, prompt_hash, topic, llm, volume, mentioned_brands_count, used_sources_count, serp_id, country, fetched_at
  - Unique constraint on (url, prompt_hash, country) for deduplication
  - Indexes on url, prompt_hash, topic, llm
- TV URL filtering using canonical HE filter from Samsung Reporting Framework
  - Includes: tv, televisions, home-audio, projectors, micro-led, micro-rgb
  - Excludes: business, monitor, mobile, displays, smartphones, /phones/
- Documentation updates:
  - URL Prompts endpoint added to `clients/samsung/semrush-api-endpoints.md`
  - `semrush_url_prompts` table schema added to `clients/samsung/docs/data-definitions.md`
- SEMrush Cited Pages data pipeline for Samsung (`clients/samsung/fetch_cited_pages.py`, `clients/samsung/load_cited_pages.py`):
  - Fetches all cited pages from SEMrush API (Element ID: 9dd09001-1d0e-4d28-b675-53670a2af5b0)
  - Filters: US market, samsung.com domain, OWNED_BY_TARGET category
  - Loads 84,856 URLs into Supabase `semrush_cited_pages` table
  - Uses Supabase REST API with upsert for deduplication
- Supabase table `semrush_cited_pages` with columns: id, url, prompts_count, country, category, domain, fetched_at
  - Unique constraint on (url, country, category) for deduplication
- Documentation updates:
  - Cited Pages endpoint added to `clients/samsung/semrush-api-endpoints.md`
  - Supabase table schema and API reference added to `clients/samsung/docs/data-definitions.md`
- DataForSEO Related Keywords script for Changan UK (`clients/changan-auto/dataforseo_related_keywords.py`):
  - Queries 6 seed keywords (3 brand terms, 3 category terms) via DataForSEO Related Keywords API
  - UK location targeting (code 2826), depth=4, includes SERP info and clickstream data
  - Saves raw JSON per seed keyword to `clients/changan-auto/data/keywords/related_kw_{seed}.json`
  - Combines and deduplicates results to `clients/changan-auto/data/keywords/changan_related_keywords.csv`
  - CSV columns: keyword, seed_keyword, depth, search_volume, cpc, competition, competition_level, keyword_difficulty, main_intent, serp_item_types
  - First run: 329 total keywords, 215 unique after deduplication, $0.15 API cost
- Component documentation - 3-way alignment between dashboard, CSS library, and style guide:
  - Extended `clients/samsung/templates/base/components.html` from ~1,124 to ~2,000 lines with 8 component sections: Header, Filter Bar, Section Headers, Prompt KPI Grid, Source KPI Row, Source Donut Chart, Source Tables Grid, Competitor Analysis Table
  - Extended `clients/samsung/dashboards/style-guide.html` from ~2,158 to ~2,550 lines with 6 visual example sections: Header, Filter Bar, Section Headers, Source KPI Cards, Source Donut Chart, Source Tables
- Sticky global filter bar for Samsung dashboard (`clients/samsung/dashboards/scom-overview.html`):
  - Position: sticky below header, stays visible while scrolling
  - Date Range picker with presets (7d, 30d, 90d, 12mo) and custom range with calendar inputs
  - AI Platform filter: ChatGPT, Gemini, Perplexity, Claude, Copilot
  - Category filter: TV Features, TV Models, Reviews & Brand
  - Model Type filter: Neo QLED, QLED, OLED, Mini-LED, Micro LED, Crystal UHD, The Frame, Gaming TVs, Outdoor TV
  - Reset button to clear all filters
  - Visual feedback with `.has-filter` class (blue border on active filters)
  - ~300 lines CSS, ~150 lines JavaScript
- Test file for filter bar development (`clients/samsung/dashboards/test-filter-bar.html`)

#### Changed
- Removed section-level filter bars from Prompt Analysis and Source Analysis sections (replaced by global sticky filter bar)
- Fixed gap between header and filter bar by removing header `margin-bottom` and adding `margin-bottom: 16px` to filter bar

#### Deployed
- Samsung dashboard with filter bar to https://robotproof.io/samsung/ai-visibility/
- Commit: `e2f640b` - "Samsung dashboard: sticky filter bar with date picker"

#### Changed
- Prompt Analysis section in `scom-overview.html` redesigned with:
  - New section header with title "Prompt Analysis" and descriptive subtitle
  - Double-stacked compact KPI cards (4 cards, each with 2 metrics) replacing single-row cards
  - New `.prompt-kpi-grid` CSS class with 4-column responsive grid
  - Removed old `.prompt-kpi-row` and `.prompt-kpi-card` styles
  - Removed old dual KPI cards from below the sunburst chart

#### Added
- Source Analysis section integrated into main dashboard (`clients/samsung/dashboards/scom-overview.html`):
  - ~480 lines of CSS for source type colors, KPI cards, donut chart, tables, and responsive breakpoints
  - Section header with title "Source Analysis" and descriptive subtitle
  - 4 Source KPI cards: Citations, Citation Gaps, Mentions, Source Visibility
  - D3.js v7 interactive donut chart with hover animations and legend interaction
  - 2-column tables grid: Source Domains table + Cited URLs table
  - Competitor Citation Analysis table with brand color indicators
  - Responsive layout (1024px breakpoint)
- Source Analysis dashboard components test file (`clients/samsung/dashboards/test-source-analysis.html`) - Stage 1 test file with:
  - Source KPI Cards (4-column grid): Citations, Citation Gaps, Mentions, Source Visibility
  - Source Type Pie Chart: D3.js v7 donut chart with Owned/Earned/Social/Competitor/Other categories
  - Source Domain and URL Tables: 2-column grid with type badges and bar visualizations
  - Competitor Analysis Section: Comparison table for Samsung, LG, Sony, TCL, Hisense
  - Responsive design with breakpoints at 1024px
  - CSS custom properties for source type and competitor brand colors
- Samsung Data Definitions documentation page (`clients/samsung/dashboards/data-definitions.html`) - Comprehensive metric reference with:
  - Six category sections: Primary KPIs, Dual-Metric KPIs, Prompt Tracking, Platform Metrics, Trend Metrics, Position Metrics
  - Definition cards with name, description, calculation formula, and data source
  - Table of contents with anchor navigation
  - Color-coded badges for metric type (KPI, Metric, Derived) and data source (Brandwatch, GA4, SEMrush, Calculated)
  - Samsung-branded styling with sticky header

#### Fixed
- Template asset paths standardized to match server directory structure:
  - `templates/base/fonts.html` - Changed `../assets/fonts/` to `./fonts/`
  - `templates/header.html` - Changed `../assets/` to `./images/`
  - `templates/kpi-cards.html` - Changed `../assets/` to `./images/`
- Broken KPI icons on deployed dashboard now load correctly

#### Changed
- Compact KPI card layout redesigned from stacked to side-by-side:
  - Label + tooltip on left, value + change badge on right
  - Reduced padding from 20px to 16px
  - Reduced value font size from 42px to 28px
  - New CSS classes: `.kpi-section-left`, `.kpi-section-right` (replacing `.kpi-section-header`, `.kpi-section-metrics`)

#### Added
- KPI card type definitions in `clients/samsung/templates/base/components.html`:
  - `.kpi-card-header` - Header KPI cards (160px min-height, with icon, centered layout)
  - `.kpi-card-compact` - Compact KPI cards (stacked sections with dividers, no icon)
  - `.kpi-row-4`, `.kpi-row-3`, `.kpi-row-2` - Grid layouts for different card counts
- Samsung global components system (`clients/samsung/templates/base/components.html`)
  - `.tooltip-icon` + `.tooltip-text` - Standardized 18x18px tooltip icons with hover reveal
  - `.change-badge` - Change indicator badges with variants: `.increase`, `.decrease`, `.increase-good`, `.decrease-bad`, `.neutral`
- Samsung style guide (`clients/samsung/dashboards/style-guide.html`) - Comprehensive component reference with color palette, typography, tooltips, badges, cards, metric values, labels, and inconsistency audit table
- Visual examples of both KPI card types in style guide with comparison table and code examples
- Test file for Prompt Gaps KPI card (`clients/samsung/dashboards/test-prompt-gaps.html`) - Stacked card layout with 2 metrics
- Style guide deployed to https://robotproof.io/samsung/ai-visibility/style-guide.html

#### Changed
- Green badge color improved from #96d551 to #2e7d32 for better contrast/accessibility
- Updated `clients/samsung/configs/scom-overview.json` to include `base/components.html` in base array for automatic inclusion in assembled dashboards
- Migrated `clients/samsung/templates/kpi-cards.html` from `.kpi-change` to global `.change-badge` classes
- Migrated `clients/samsung/templates/kpi-cards-dual.html` from `.kpi-dual-item-change` to global `.change-badge` classes

#### Added (previous)
- MCP Authentication Quick Reference section in DEVELOPMENT.md (prominent placement for easy access)
- Token expiry documentation: OAuth apps in "Testing" mode have 7-day token lifetime
- Permanent fix instructions: Publish OAuth app to extend token lifetime to 6 months
- MCP authentication reference documentation (critical setup guide)
  - `auth-command.txt` - Single auth command with all required scopes
  - Complete troubleshooting guide in `docs/build-log.md`
- Local GTM MCP server at `C:\Users\rober\gtm-mcp\` replacing mcp-remote proxy
  - 29 tools across 7 modules: accounts, containers, workspaces, tags, triggers, variables, versions
  - Uses FastMCP framework and Application Default Credentials
  - Virtual environment at `C:\Users\rober\gtm-mcp-py313\`
- Nginx basic authentication for Samsung dashboard at robotproof.io/samsung/
  - htpasswd file at `/etc/nginx/.htpasswd_samsung`
  - Credentials: username `samsung`, password `Samsung2026`
  - Browser caches credentials until browser close (no re-login on refresh)
- DigitalOcean deployment workflow for Samsung dashboards
  - SSH config using `digitalocean` host alias
  - Deployment via `scp` to `/var/www/html/samsung/ai-visibility/`
  - Local folder structure mirrors server structure (`dashboards/fonts/`, `dashboards/images/`)
- Live dashboard URL: https://robotproof.io/samsung/ai-visibility/

#### Infrastructure
- Nginx configuration updated with `auth_basic` directives for `/samsung/` location block

#### Changed
- Reorganized `clients/samsung/dashboards/` to include `fonts/` and `images/` subdirectories
- Updated asset paths in `scom-overview.html` from `../assets/` to `./fonts/` and `./images/`
- Renamed `ai visi.jpg` to `ai-visi.jpg` (removed space for URL compatibility)

#### Infrastructure
- Nginx configuration updated on robotproof.io to serve `/samsung/` directory with static assets

#### Added (previous session)
- Sunburst Prompts Visualization (`clients/samsung/templates/sunburst-prompts.html`) - Interactive D3.js sunburst chart for prompt category hierarchy with drill-down navigation, breadcrumbs, subcategory chips, and sample prompts list
- Prompt Rankings Table (`clients/samsung/templates/prompt-rankings-table.html`) - Full-width performance table with model icons, position color coding, change indicators, visibility bars, and sticky header
- Cross-component filtering: sunburst chart filters prompt rankings table via `window.renderRankingsTable(filter)` function
- Test files: `test-sunburst-prompts.html`, `test-prompt-rankings-table.html`, `test-prompt-rankings.html`

#### Changed
- Updated `configs/scom-overview.json` to include sunburst-prompts and prompt-rankings-table components
- Clarified Component-First Development Workflow to 3 stages: Test File -> Template -> Assembly (see build-log.md for full documentation)

#### Fixed
- Added `.container` wrapper to sunburst and prompt-rankings templates for proper layout spacing
- Scoped tooltip CSS selectors (`.sunburst-card .tooltip-icon`, `.prompt-rankings-card .tooltip-icon`) to fix style conflicts in assembled dashboard

#### Added (previous session)
- Samsung template assembly system (`clients/samsung/templates/`, `configs/`, `scripts/assemble_dashboard.py`) - Template-first dashboard generation with immutable components
  - `templates/base/fonts.html` - Samsung font declarations
  - `templates/base/tokens.html` - CSS variables and base styles
  - `templates/header.html` - Header component
  - `templates/kpi-cards.html` - KPI cards with tooltips
  - `templates/line-charts.html` - Line charts with insights boxes
  - `configs/scom-overview.json` - S.com Overview dashboard configuration
- Samsung KPI Cards element specification (`clients/samsung/prompts/elements/kpi-cards.md`) - 4 KPI cards for S.com Overview dashboard
- KPI card test page (`clients/samsung/dashboards/test-kpi-cards-client.html`) - Test page demonstrating all 4 change states
- Custom KPI icons at `clients/samsung/assets/` - sov.jpg, source_visi.jpg, referral.jpg, ai visi.jpg
- CSS-only tooltip feature for KPI cards with hover reveal and smooth fade transition
- 4-state change indicators: N/A (grey), No Change (yellow), Increase (green), Decrease (red)
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
- Local GTM MCP server at `C:\Users\rober\gtm-mcp\` (replaces mcp-remote proxy)
- gtm-mcp venv at `C:\Users\rober\gtm-mcp-py313`
- analytics-mcp venv at `C:\Users\rober\analytics-mcp-py313`
- Credentials at `C:\Users\rober\application_default_credentials.json` (used by both MCP servers)
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
