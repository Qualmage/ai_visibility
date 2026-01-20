# **Hisense USA Data Project**

Proposal  
Prepared by: Alchemy EMEA LTD (part of the Atoms & Space Collective) | Date: January 2026

# **Executive Summary**

Alchemy proposes a 12-month engagement to support Hisense USA's digital transformation, focusing on data layer implementation, analytics strategy, and customer data platform preparation. This proposal addresses the current foundational stage of data maturity, supporting the migration from Wix to AEM, HubSpot to Salesforce, and establishing unified tracking across both retailer (Where to Buy) and DTC sales models.

## **Investment Summary**

| Phase | Period | Monthly Investment |
| ----- | ----- | ----- |
| Phase 1: Foundation | Mid-Jan \- Mar 2026 | $37,000/month |
| Phase 2: Acquisition & Structuring | Apr \- Sep 2026 | $27,500/month |
| Phase 3: Activation & CDP Prep | Oct \- Dec 2026 | $39,000/month |
| **Year 1 Total** | **11.5 months** | **$374,500** |

# **Context**

**Client:** Hisense USA

**Key Contact:** Myles Jordan (Head of Digital)

**Alchemy Group Contact:** Rob Francis (Head of Data & Tools)

**Social Agency:** Agent42 (part of the Atoms and Space Collective)

**Opportunity:** Digital transformation with significant data/analytics workstream

# **Current State**

## **Platform Migrations In Flight**

| System | Current | Future | Timeline |
| ----- | ----- | ----- | ----- |
| Website | Wix | Adobe Experience Manager (headless) | Homepage Dec 31 2025, Full site March 2026 |
| CRM | HubSpot | Salesforce Marketing Cloud | March 2026, parallel with HubSpot until Oct 2026 |
| Attribution | Price Spider | ChannelSight | TBC |
| DTC Platform | Shopify | SAP Commerce Cloud | TBC |

**Key dependency:** Accenture is handling the AEM build; HQ owns the Accenture retainer.

## **Data Maturity**

The current state represents a foundational stage of data maturity, with significant opportunities for development:

* **No data layer** on current site  
* **No custom tagging** implemented  
* **No customer segmentation** \- emails are distributed to 400k recipients with identical content  
* **No Customer Data Platform (CDP)** \- on the roadmap but budget not allocated until H2 2026  
* **HubSpot underutilized** \- approximately 1M contacts, but currently limited to form submission capture  
* **Tableau lacking governance** \- multiple dashboards exist without centralized oversight or standardization  
* **Manual processes** \- lead scoring will be handled manually in Salesforce in the initial phase  
* **Awareness-focused media** \- prior to 2026, media spend has been exclusively allocated to awareness campaigns with broad reach

## **Data Sources Identified**

| Source | What It Contains | Storage/Access |
| ----- | ----- | ----- |
| HubSpot | Form submissions, \~1M contacts, 470k subscribed | Moving to Salesforce |
| PowerBI | Store sales data down to zip code level | HQ-owned, retailers send in various formats |
| Price Spider / ChannelSight | "Where to Buy" click attribution, conversion data, deflection data | Looker dashboard \+ possible API |
| GA4 | Web analytics (free version, no 360\) | Standard |
| Salesforce (future) | CRM, single source of customer data, personalization engine | March 2026 onwards |

# **Alchemy Role**

## **Division of Responsibilities**

| Alchemy | Accenture |
| ----- | ----- |
| Solution design documents | Implementation into AEM |
| Data layer schema design | Integration of data layer logic |
| JavaScript snippets (ready to deploy) | Script deployment |
| GTM configuration | Testing |
| Tag strategy and implementation | Maintenance |

**Key point:** Alchemy provides both specifications and production-ready JavaScript, rather than documentation alone. This ensures implementation quality and removes ambiguity.

# **Agent42 Collaboration & Multichannel Tracking**

Agent42, part of the Atoms & Space Collective, is handling the social media side for Hisense USA. Tight collaboration between Alchemy and Agent42 is critical to ensure unified tracking and attribution across all channels.

## **FIFA Social Campaign**

This has been identified as a key campaign moment. While audience testing will take place during FIFA, targeting will remain relatively broad. This presents an opportunity to:

* Establish consistent UTM parameter conventions between Alchemy and Agent42  
* Ensure social campaign tracking flows into the unified data layer  
* Capture learnings from FIFA to inform future campaign segmentation  
* Test audience hypotheses that can be refined post-campaign

## **Multichannel Awareness & Attribution**

Hisense's media spend has historically been entirely awareness-focused (above the line, mass reach). The 2026 transformation aims to connect upper-funnel awareness to lower-funnel conversion. This requires:

### **Cross-Agency Coordination**

| Channel | Owner | Tracking Requirement |
| ----- | ----- | ----- |
| Social (Organic & Paid) | Agent42 | UTM standards, platform pixels, social listening |
| Website & Data Layer | Alchemy | GTM, GA4, Salesforce integration |
| TV / Above the Line | Media Agency (TBC) | Brand lift studies, site traffic correlation |
| Retailer / Where to Buy | Alchemy \+ ChannelSight | Click attribution, conversion data where available |

### **Unified Tracking Framework**

To ensure multichannel attribution works, Alchemy and Agent42 must align on:

* **UTM naming conventions** \- consistent source, medium, campaign, content parameters across all channels  
* **Campaign taxonomy** \- shared naming structure for campaigns (e.g., FIFA\_2026\_Social\_Awareness)  
* **Pixel and tag coordination** \- ensure social pixels fire correctly alongside GTM tags  
* **Reporting cadence** \- regular sync between agencies and client to review cross-channel performance  
* **Audience sharing** \- ability to create retargeting audiences from website behavior for social activation

# **Data Layer Strategy**

## **Purpose**

The data layer standardizes how website data is captured, making it:

* **Consistent** \- common schema across all events  
* **Portable** \- capable of routing to multiple destinations (GA4, Salesforce, data warehouse)  
* **Joinable** \- structured with identifiers that map to external data sources

## **Technical Considerations**

1. **AEM is headless (SPA)** \- event-driven, stateful architecture rather than traditional page views  
2. **Salesforce has flat data structure** \- data layer may be nested and will require transformation  
3. **GTM as the routing layer** \- sits above platforms and abstracts destination changes

## **Phased Rollout Complexity**

Three environments running in parallel during transition:

| Phase | Timeframe | Platforms Active |
| ----- | ----- | ----- |
| Phase 1 | Jan-Feb 2026 | Wix (most pages) \+ AEM (homepage only) \+ HubSpot |
| Phase 2 | March 2026 | Full AEM \+ Salesforce (HubSpot status TBC) |
| Phase 3 | Post-March 2026 | AEM \+ Salesforce (unified) |

### **Approach**

1. Deploy a simple data layer as a proof of concept on Wix (low risk, as this platform is scheduled for retirement)  
2. Use the AEM homepage (December 31, 2025\) as the first production implementation  
3. Validate that schema and GTM routing function correctly  
4. Extend progressively as the full AEM rollout proceeds in March 2026

**Critical principle:** Schema-first approach \- design once, implement twice (Wix, then AEM). The schema remains constant; implementation varies by platform.

# **Two Sales Models Requiring Different Approaches**

## **A: Where to Buy (Retailer-driven)**

* Hisense-usa.com is marketing/discovery  
* Purchase happens on Amazon, Best Buy, Costco, etc.  
* Attribution relies on ChannelSight click tracking  
* Conversion data depends on retailer data partnerships  
* No direct transaction data owned by Hisense

**Data layer captures:** Product views, "Where to Buy" clicks, UTM parameters, session data

## **B: DTC (Direct-to-Consumer)**

* Currently limited to Laser TV category  
* Moving from Shopify to SAP Commerce Cloud  
* Full checkout flow owned by Hisense  
* Complete transaction visibility  
* Requires ecommerce data layer (cart, checkout, purchase events)

**Data layer captures:** Product views, add to cart, checkout steps, purchase complete, order details

***Both models need to coexist in the same data layer spec.***

# **Customer Profiling**

## **Current State**

* No meaningful profiling currently in place  
* No segmentation \- emails are sent to 400,000 recipients monthly, all receiving identical content  
* Product registrations are not grouped by purchase type  
* Anonymous data is limited \- no event-level data beyond page views and button clicks

## **Vision**

* Account-based, personalised one-to-one marketing  
* Propensity modelling \- predicting not only likelihood to purchase, but anticipated product selection  
* Lookalike modelling to support paid media teams  
* Audience insights that inform channel selection

## **Realistic Timeline**

* Approximately 8–12 months required to acquire sufficient data before structuring can begin  
* A further six months to develop audiences suitable for always-on automation  
* Expectation management will be required: by Q2 2026, HQ may question why full personalisation has not yet been achieved

## **Early Profiling vs. Later Profiling**

### **Phase 1: Anonymous Behavioral Profiling (Immediate \- via Data Layer)**

| Data Point | Source | Profile Use |
| ----- | ----- | ----- |
| Pages viewed | Data layer | Product interest signals |
| Product categories browsed | Data layer | Category affinity |
| Traffic source / UTM | Data layer | Acquisition channel |
| "Where to Buy" clicks | Data layer \+ ChannelSight | Purchase intent |
| Which retailer selected | Data layer \+ ChannelSight | Retailer preference |

### 

### 

### 

### **Phase 2: Known User Profiling (Once forms are submitted)**

| Data Point | Source | Profile Use |
| ----- | ----- | ----- |
| Email / Name | Form submission | Identity |
| Product owned | Product registration | Customer value, cross-sell |
| Support requests | Support forms | Satisfaction signals |
| Email engagement | Salesforce | Engagement scoring |

### **Phase 3: Enriched Profiling (6-12 months)**

| Data Point | Source | Profile Use |
| ----- | ----- | ----- |
| Purchase history (DTC) | Ecommerce transactions | RFM scoring, LTV |
| Multi-product ownership | Product registrations | Cross-sell opportunities |
| Campaign response patterns | Salesforce \+ GA4 | Content preferences |
| Behavioral scoring | Aggregated events | Propensity modeling |

## **Lead Scoring Approach**

Myles acknowledged scoring will be manual and rules-based initially:

| Event | Score Impact | Rationale |
| ----- | ----- | ----- |
| Product registration | \+4 | Confirmed customer, known product |
| Email opened, not clicked | \-1 | Low engagement signal |
| Form submission | \+2 | Active interest |
| "Where to Buy" click | \+3 | High purchase intent |
| Support request | \+1 | Customer, but potentially at-risk |

This manual scoring in Salesforce is the bridge until budget for algorithmic scoring / CDP in H2 2026\.

# **Data Maturity Roadmap**

## **Stage 1: Foundation (Q1 2026 \- Jan-Mar)**

**Focus:** Data capture infrastructure

* Data layer design & implementation  
* GTM configuration  
* Salesforce setup  
* Data audit  
* Governance framework

**Profiling capability:** Anonymous behavioral signals only

## **Stage 2: Acquisition (Q2 2026 \- Apr-Jun)**

**Focus:** Growing known user base

* Form optimization  
* Zero-party data collection  
* Manual lead scoring  
* Initial segmentation  
* Test & learn agenda (including FIFA campaign learnings)

**Profiling capability:** Basic known user profiles, manual segments

## **Stage 3: Structuring (Q3 2026 \- Jul-Sep)**

**Focus:** Organizing and enriching data

* Data volume assessment  
* Segment refinement  
* Attribution analysis  
* Cross-source joining  
* Reporting dashboards

**Profiling capability:** Multi-dimensional segments, basic scoring

## **Stage 4: Activation (Q4 2026 \- Oct-Dec)**

**Focus:** Using data for personalization

* Always-on automations  
* Audience syndication  
* Dynamic content  
* Performance optimization

**Profiling capability:** Actionable audiences, automated journeys

## **Stage 5: Intelligence (2027+)**

**Focus:** Predictive and scaled personalization

* CDP implementation (H2 2026 budget)  
* Algorithmic scoring  
* On-site personalization  
* 1:1 marketing

**Profiling capability:** Predictive, real-time, one-to-one

# **Data Governance Framework**

## **Current State \- Myles' Concerns**

* Data access is currently unguarded  
* Significant data privacy risk \- bulk data exports (e.g., email lists) can be shared via unsecured channels without restriction; encryption is required  
* No formal process for data access or handling  
* Tableau dashboards have proliferated without centralised governance  
* No naming conventions in place for campaigns or links

**Note:** Alchemy has experience with SHA-256 encryption of PII and data compliance, as well as extensive experience with Power BI, Tableau, Looker Studio, and custom dashboarding.

## **Governance Workstream**

| Area | What's Needed |
| ----- | ----- |
| Data Access | Who can access what data? Role-based permissions in Salesforce, GA4, PowerBI |
| Data Handling | PII handling policies, encryption requirements, no raw data over Teams/email |
| Naming Conventions | UTM parameters, campaign naming, data layer event naming (aligned with Agent42) |
| Data Catalog | Inventory of all data sources, what they contain, who owns them |
| Consent Management | How is consent captured? Cookie consent, email opt-in, data retention |
| Documentation | Data dictionary, schema documentation, process documentation |
| Quality Assurance | QA process for tracking implementation, data validation |

## **Governance Deliverables**

1. **Data Governance Framework Document** \- Policies, roles, responsibilities  
2. **Data Catalog** \- Inventory of all sources and fields  
3. **Naming Convention Guide** \- UTM, events, campaigns (shared with Agent42)  
4. **Data Layer Specification** \- Schema documentation  
5. **QA Checklist** \- Validation process for implementations

# **Proposed Team & Day Rates**

| Role | Responsibility | Day Rate |
| ----- | ----- | ----- |
| Client Director | Client relationship, strategic counsel, commercial ownership, HQ engagement | $1,500/day |
| Account Director | Project coordination, day-to-day management, status reporting, team oversight | $1,200/day |
| Lead Analytics Consultant | Strategy, architecture, QA oversight, governance, CDP requirements | $1,400/day |
| Tagging Specialist | GTM configuration, data layer JS, event tracking, Accenture specs, BAU | $1,000/day |
| Data Engineer | Data warehouse, PowerBI integration, cross-source joining, CDP architecture | $1,100/day |

## **Team Allocation by Phase**

| Role | Phase 1 | Phase 2 | Phase 3 |
| ----- | ----- | ----- | ----- |
| Client Director | 2.5 days/month | 1.5 days/month | 3 days/month |
| Account Director | 5 days/month | 3 days/month | 4.5 days/month |
| Lead Analytics Consultant | 9 days/month | 5.5 days/month | 10 days/month |
| Tagging Specialist | 14 days/month | 9 days/month | 5.5 days/month |
| Data Engineer | \- | 4.5 days/month | 6.5 days/month |
| **Total Days/Month** | **30.5 days** | **23.5 days** | **29.5 days** |

## **Year 1 Investment by Role**

| Role | Total Days | Day Rate | Total | % |
| ----- | ----- | ----- | ----- | ----- |
| Client Director | 24.25 | $1,500 | $36,375 | 10% |
| Account Director | 44 | $1,200 | $52,800 | 14% |
| Lead Analytics Consultant | 85.5 | $1,400 | $119,700 | 32% |
| Tagging Specialist | 105.5 | $1,000 | $105,500 | 28% |
| Data Engineer | 46.5 | $1,100 | $51,150 | 14% |
| **Total** | **305.75** |  | **$374,500** | **100%** |

# **Phased Approach**

## **Phase 1: Foundation (Mid-Jan \- Mar 2026\)**

**Duration:** 2.5 months | **Phase Total:** $92,500

**Focus:** Data capture infrastructure \- accelerated delivery for compressed timeline before Salesforce launch

* Full audit of current state (GTM, GA4, forms, data sources)  
* Data layer schema design (covering both WTB and DTC models)  
* JavaScript snippets for Accenture to implement into AEM  
* GTM container configuration  
* Event specification mapping  
* Governance framework document  
* Naming convention guide (coordinated with Agent42)  
* QA test plan

**Profiling capability:** Anonymous behavioral signals only

## **Phase 2: Acquisition & Structuring (Apr \- Sep 2026\)**

**Duration:** 6 months | **Phase Total:** $165,000

**Focus:** Implementation support, test & learn, data warehouse build

* Ongoing tagging support (new templates, event additions, Accenture liaison)  
* ChannelSight integration and click tracking implementation  
* SAP Commerce Cloud ecommerce tracking (cart, checkout, purchase events)  
* Data warehouse setup and PowerBI API integration  
* Cross-channel reporting and campaign performance dashboards  
* Test & learn agenda (including FIFA campaign tracking and learnings)  
* Agent42 coordination on UTM taxonomy and social tracking

**Profiling capability:** Basic known user profiles, manual segments

## **Phase 3: Activation & CDP Prep (Oct \- Dec 2026\)**

**Duration:** 3 months | **Phase Total:** $117,000

**Focus:** CDP deep-dive, advanced segmentation, 2027 roadmap planning

* BAU tagging and analytics support  
* Data warehouse optimisation and advanced reporting  
* CDP vendor evaluation (Salesforce Data Cloud, Segment, Tealium, etc.)  
* Requirements definition and integration architecture design  
* Identity resolution strategy  
* Business case development for HQ budget approval  
* 2027 roadmap and maturity assessment

**Profiling capability:** Multi-dimensional segments, CDP-ready

**Invoice Schedule**

It is the expectation of the SOW that Client will provide the PO\# and/or all billing information by January 16, 2026\. Invoices will be submitted according to the schedule below.

| Billing Month | Invoice Amount | Payment Terms |
| ----- | ----- | ----- |
| January 30, 2026 | $18,500 | NET 60 |
| February 27, 2026 | $37,000 | NET 60 |
| March 31, 2026 | $37,000 | NET 60 |
| April 30, 2026 | $27,500 | NET 60 |
| May 29, 2026 | $27,500 | NET 60 |
| June 30, 2026 | $27,500 | NET 60 |
| July 31, 2026 | $27,500 | NET 60 |
| August 31, 2026 | $27,500 | NET 60 |
| September 30, 2026 | $27,500 | NET 60 |
| October 30, 2026 | $39,000 | NET 60 |
| November 30, 2026 | $39,000 | NET 60 |
| December 31, 2026 | $39,000 | NET 60 |
| **Total:** | **$374,500** |  |

# **Workstreams**

## **Workstream A: Data Layer & Tagging**

* Data layer schema design (covering both WTB and DTC models)  
* JavaScript snippets for Accenture to implement  
* GTM container configuration  
* Event specification mapping  
* QA test plan  
* Phased rollout support (Wix POC → AEM homepage → Full AEM)

## **Workstream B: Where to Buy Attribution**

* ChannelSight integration assessment  
* Click tracking implementation  
* Retailer data unification (where available)  
* Deflection data analysis (competitor product purchases)

## **Workstream C: DTC Ecommerce Tracking**

* Full ecommerce data layer (GA4 ecommerce schema)  
* SAP Commerce Cloud integration  
* Cart/checkout/purchase event tracking  
* Transaction capture into Salesforce

## **Workstream D: Data Governance**

* Governance framework document  
* Data catalog  
* Naming convention guide (coordinated with Agent42)  
* QA checklist

## **Workstream E: Multichannel & Agent42 Coordination**

* Unified UTM and campaign taxonomy  
* Social pixel and tag coordination  
* Cross-channel reporting framework  
* FIFA campaign tracking setup

## **Workstream F: Sell-Through Data Unification**

* Data warehouse setup and configuration  
* PowerBI API integration  
* Cross-source data joining  
* Unified reporting dashboards

## **Workstream G: Customer Data Platform**

* CDP scoping and vendor evaluation (Salesforce Data Cloud, Segment, Tealium, or alternative)  
* Requirements definition based on profiling and segmentation needs  
* Integration architecture design (connecting data layer, Salesforce, GA4, ChannelSight)  
* Identity resolution strategy (stitching anonymous to known users)  
* Audience activation roadmap (syndication to paid media, email, on-site personalization)  
* Business case development to support H2 2026 budget request

# **Key Dates & Review Points**

| Date | Milestone |
| ----- | ----- |
| Dec 31, 2025 | AEM homepage launches |
| Mid-January 2026 | Engagement start \- planning/audit phase begins |
| March 2026 | Salesforce deployed, full AEM deployed \- REVIEW POINT |
| Q2 2026 | FIFA campaign \- audience testing opportunity |
| September 2026 | CDP business case presentation \- REVIEW POINT |
| October 2026 | HubSpot contract ends |
| December 2026 | 2027 roadmap sign-off \- REVIEW POINT |
| H2 2026 | Potential CDP budget approval |

# **Scope Clarification**

## **What's Included**

* Dedicated Client Director for relationship & commercial ownership  
* Dedicated Account Director for project & team management  
* All 7 workstreams (A through G)  
* Data layer design AND JavaScript deliverables  
* GTM configuration and QA  
* Governance framework and documentation  
* Agent42 coordination on tracking  
* Accenture liaison and handoff management  
* Data warehouse setup (Phase 2+)  
* CDP vendor evaluation and business case (Phase 3\)  
* Weekly status calls, monthly reviews, quarterly business reviews  
* 2027 roadmap planning

## **What's Not Included**

* CDP licensing costs (vendor fees for Salesforce Data Cloud, Segment, etc.)  
* Data warehouse infrastructure/hosting (AWS, GCP \- HQ may provide)  
* Agent42 social execution (separate engagement)  
* Accenture implementation hours (HQ retainer)  
* Salesforce configuration (internal/Salesforce team)

# **Terms**

1. **Retainer model:** Monthly invoicing in advance  
2. **Payment terms:** Net 60 days  
3. **Review points:** March 2026, September 2026, December 2026  
4. **Scope changes:** Any material changes to scope will be documented and agreed in writing  
5. **Notice period:** 30 days written notice to adjust or terminate engagement

# **Next Steps**

1. Review and approve proposal  
2. Finalize contract and SOW  
3. Schedule kick-off call for mid-January 2026  
4. Arrange access to GTM, GA4, and relevant systems  
5. Introduce Alchemy team to Accenture counterparts