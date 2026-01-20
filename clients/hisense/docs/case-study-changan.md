# Case Study: Changan Auto Europe

**Client:** Changan Automobile
**Industry:** Automotive
**Engagement:** Ongoing
**Scope:** GTM Audit, Tagging Strategy, Data Layer Design, GA4 Analytics, BigQuery Data Pipeline

---

## About Changan Automobile

Changan Automobile is one of China's "Big Four" automakers with a heritage dating back over 160 years. Originally founded in 1862 as a military manufacturing facility, the company entered automobile production in 1959 and has since grown into a global automotive powerhouse.

**Key Facts:**
| Metric | Value |
|--------|-------|
| Founded | 1862 (auto manufacturing from 1959) |
| Global Sales (2024) | 2.68 million vehicles |
| Employees | ~110,000 |
| Manufacturing Bases | 21 worldwide |
| China Market Ranking | Top 5 |

**Recent Milestones:**
- In July 2025, Changan was elevated to become a direct central state-owned enterprise under SASAC—one of only three automotive companies with this status
- Registered assets of over 308 billion yuan ($43 billion)
- Fifth consecutive year of sales growth in 2024
- NEV (New Energy Vehicle) sales up 49% year-on-year

**European Expansion:**
Changan has launched an ambitious global strategy called the "Vast Ocean Plan" with a target to become a top 10 global automaker by 2030. Their European expansion includes:
- German subsidiary registered in Munich (Changan Automobile Deutschland GmbH)
- Dedicated European website serving 11 markets
- Target of 1.5 million overseas sales annually by 2030

---

## Executive Summary

**Alchemy**, part of the **Atoms & Space group**, delivers end-to-end analytics services for Changan Auto's European digital presence across 11 markets. We own and manage the complete analytics lifecycle—from tagging strategy and data layer architecture through to reporting and data transformation—ensuring consistency and quality across all digital channels.

Our scope includes GTM auditing, tagging implementation, multi-platform tracking, GA4 configuration, BigQuery data pipelines, and performance reporting. This single-ownership model eliminates fragmentation and ensures seamless data flow from capture to insight.

---

## The Challenge

Changan Auto launched their European expansion with a multi-country website requiring:

1. **Scalable tag management** across 11 different country sites
2. **A robust data layer** to capture user interactions consistently
3. **Multi-platform tracking** for analytics and advertising platforms
4. **Secure data processing** beyond standard analytics capabilities
5. **Market-specific analytics** to track performance in each region independently

---

## Our Solution

### 1. GTM Audit & Optimisation

We conducted a comprehensive audit of Changan's existing GTM implementation:

**Audit Scope:**
- Tag inventory and redundancy analysis
- Trigger efficiency review
- Naming convention standardisation
- Variable consolidation
- Third-party tag assessment
- Container load performance

**Outcomes:**
- Identified and removed redundant tags
- Standardised naming conventions across all containers
- Consolidated duplicate variables
- Documented tag ownership and purpose
- Improved container efficiency

---

### 2. Data Layer Architecture

We designed and implemented a structured data layer specification:

**Data Layer Components:**
- **Page-level data** - Page type, category, language, market
- **User data** - Authentication state, user preferences, segment
- **Ecommerce events** - Product views, configurator interactions, lead submissions
- **Custom events** - Test drive bookings, dealer locator usage, brochure downloads

**Automotive-Specific Events:**
| Event | Description |
|-------|-------------|
| `vehicle_view` | User views a vehicle model page |
| `configurator_start` | User begins vehicle configuration |
| `configurator_complete` | User completes configuration |
| `test_drive_request` | User submits test drive form |
| `dealer_search` | User searches for dealers |
| `brochure_download` | User downloads vehicle brochure |
| `finance_calculator` | User interacts with finance tool |

**Benefits:**
- Consistent data capture across all 11 markets
- Simplified tag configuration using data layer variables
- Future-proofed for additional tracking requirements
- Clear documentation for development team integration

---

### 3. Multi-Platform Tracking

We implemented and manage tracking across multiple analytics and advertising platforms:

| Platform | Purpose |
|----------|---------|
| Google Analytics 4 | Web analytics & conversion tracking |
| Meta Pixel | Facebook/Instagram advertising |
| TikTok Pixel | TikTok advertising |
| Google Ads | Search & display advertising |

**Centralised Configuration:**
- Master tracking spreadsheet documenting all configurations per market
- Standardised event mapping across platforms
- Consistent conversion definitions
- Simplified onboarding for new markets

---

### 4. BigQuery Data Pipeline

Beyond standard analytics, we capture and process data securely in Google BigQuery:

**Data Sources:**
- GA4 raw event data export
- CRM lead data
- Advertising platform data
- Website interaction data

**Capabilities:**
- **Secure storage** - Data held in client-owned Google Cloud project
- **Data enrichment** - Joining analytics data with business data sources
- **Custom analysis** - SQL-based queries beyond GA4's interface limitations
- **Reporting flexibility** - Feed dashboards, data science workflows, or BI tools

**Benefits:**
- Full data ownership and control
- Granular data access (beyond sampled GA4 reports)
- Cross-platform data joining
- Historical data retention beyond GA4 limits
- GDPR-compliant data processing

---

### 5. GTM Architecture

We designed and manage a multi-container GTM architecture with dedicated containers for each market:

| Coverage | Count |
|----------|-------|
| European Markets | 11 |
| GTM Containers | 11 |
| GA4 Properties | 11 |
| Advertising Platforms | 3+ per market |

**Markets Covered:**
United Kingdom, Germany, Netherlands, Norway, Greece, Italy, Spain, Poland, Luxembourg, Belgium, plus a central country picker.

**Key Benefits:**
- Market-specific tracking rules and triggers
- Localised conversion events
- Centralised management with per-market flexibility
- Easy rollout of new tags across all or specific markets

---

### 6. Platform Migration Support

Changan's European markets have undergone site migrations from **Wix to DotNetNuke (DNN)**. We supported these transitions to ensure tagging continuity and data consistency:

**Migration Scope:**
- Pre-migration audit of existing tracking implementation
- Data layer specification for the new DNN platform
- GTM container updates to accommodate new site structure
- Post-migration validation and QA testing
- Historical data continuity planning

**Key Outcomes:**
- Zero tracking gaps during platform transition
- Consistent event naming across old and new platforms
- Preserved conversion tracking and attribution
- Updated triggers and variables for DNN page structure

---

### 7. GA4 Property Architecture

We implemented a per-country GA4 property structure enabling:

- **Independent market analysis** - Each country team can analyse their own data
- **Cross-market comparison** - Aggregate views for regional leadership
- **Clean data separation** - No cross-contamination between markets

---

## Capabilities Demonstrated

| Area | What We Delivered |
|------|-------------------|
| **GTM Audit** | Full container review, redundancy removal, standardisation |
| **Tagging Strategy** | Multi-market architecture, scalable deployment |
| **Data Layer** | Structured specification, automotive-specific events |
| **Multi-Platform Tracking** | GA4, Meta, TikTok, Google Ads integration |
| **BigQuery Pipeline** | Secure data capture, enrichment, and processing |
| **Platform Migration** | Wix to DNN transition with tagging continuity |
| **GA4 Implementation** | Per-market properties, conversion tracking |

---

## Relevance to Hisense

This engagement demonstrates Alchemy's capability to:

1. **Audit existing implementations** - Identify gaps and optimisation opportunities
2. **Design data layer architecture** - Structured, documented, developer-ready
3. **Implement multi-platform tracking** - GA4, Meta, TikTok, and advertising platforms
4. **Build secure data pipelines** - BigQuery ingestion from multiple sources
5. **Scale across markets** - 11 countries with coordinated tracking
6. **Support platform migrations** - Ensure tagging continuity during CMS transitions
7. **Deliver centralised management** - Master configuration with per-market flexibility

**Why End-to-End Ownership Matters:**

By having Alchemy own the complete analytics stack—tagging, auditing, reporting, and data transformation—Changan benefits from:
- **No handoff gaps** - Single team accountable from data capture to insight
- **Consistent standards** - Unified naming conventions, event definitions, and quality controls
- **Faster resolution** - Issues diagnosed and fixed without cross-team dependencies
- **Strategic alignment** - Reporting tied directly to how data is captured

For Hisense's data transformation initiative, Alchemy brings proven experience in:
- GTM auditing and optimisation
- Data layer design and documentation
- Multi-platform tracking implementation
- BigQuery data pipeline development
- Complex multi-container implementations
- GA4 architecture and configuration
- Platform migration with tagging continuity
- End-to-end delivery across all digital channels

---

*Case study prepared by Alchemy, an Atoms & Space company — January 2026*
