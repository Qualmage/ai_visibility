# Samsung AI Visibility Dashboard - Full Assembly

Complete dashboard assembly referencing modular elements.

> **Reference:** `dashboards/v3-ai-overview.html` (approved implementation)

---

## Quick Reference

| Component | File | Status |
|-----------|------|--------|
| Design Tokens | `_base/design-tokens.md` | ✅ Complete |
| Font Declarations | `_base/fonts.md` | ✅ Complete |
| Reusable Components | `_base/components.md` | ✅ Complete |
| Header | `elements/header.md` | ✅ Approved |
| KPI Cards | `elements/kpi-cards.md` | ✅ Complete |
| Line Chart | `elements/line-chart.md` | ✅ Complete |
| Donut Chart | `elements/donut-chart.md` | ✅ Complete |
| Stacked Bar | `elements/stacked-bar.md` | ✅ Complete |
| Leaderboard | `elements/leaderboard-table.md` | ✅ Complete |
| Data Table | `elements/data-table.md` | ✅ Complete |

---

## Page Structure

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ HEADER: AI Visibility Dashboard                              [SAMSUNG LOGO] │
├─────────────────────────────────────────────────────────────────────────────┤
│ Overview                                                                     │
│ [Filters Row]                                                               │
├─────────────────────────────────────────────────────────────────────────────┤
│ KPI CARDS ROW (4 cards)                                                     │
│ [Share of Voice] [Brand Visibility] [Prompts] [Mentions by Sentiment]       │
├─────────────────────────────────────────────────────────────────────────────┤
│ HISTORICAL TREND (Line Chart + Legend)                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│ TWO COLUMN SECTION                                                          │
│ [Brand Leaderboard]              [Sentiment Over Time]                      │
├─────────────────────────────────────────────────────────────────────────────┤
│ DATA TABLE (Brand/Product Performance)                                      │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Assembly Instructions

### 1. Start with HTML Boilerplate

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Samsung AI Overview Dashboard</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        /* Include: _base/fonts.md @font-face declarations */
        /* Include: _base/design-tokens.md CSS variables */
        /* Include: _base/components.md component styles */
    </style>
</head>
<body>
    <!-- Include: elements/header.md -->
    <div class="container">
        <!-- Content sections -->
    </div>
    <script>
        /* Include: D3.js code from chart elements */
    </script>
</body>
</html>
```

### 2. Include Base Styles

From `_base/fonts.md`:
- @font-face declarations for Samsung Sharp Sans and Samsung One

From `_base/design-tokens.md`:
- CSS custom properties (:root block)

From `_base/components.md`:
- .filter-btn, .toggle-btn, .tab-btn
- .badge, .card, .section-title
- .legend, .pagination
- Table base styles

### 3. Include Elements (in order)

1. **Header** (`elements/header.md`)
   - Goes directly after `<body>`
   - Uses inline styles

2. **Container div** with:
   - Overview title + filters row
   - **KPI Cards** (`elements/kpi-cards.md`)
   - **Historical Trend** (`elements/line-chart.md`)
   - **Two-column section**:
     - Left: **Brand Leaderboard** (`elements/leaderboard-table.md`)
     - Right: **Sentiment Over Time** (`elements/stacked-bar.md`)
   - **Data Table** (`elements/data-table.md`)

### 4. Include D3.js Scripts

At the end of `<body>`, include JavaScript from:
- `elements/donut-chart.md` - Donut for KPI card 4
- `elements/line-chart.md` - Historical trend chart
- `elements/stacked-bar.md` - Sentiment over time chart

---

## How to Generate Individual Elements

### Request a Single Element:
> "Generate just the KPI cards row using design tokens from `_base/design-tokens.md` and specs from `elements/kpi-cards.md`"

### Request Multiple Elements:
> "Generate the Historical Trend section (line chart + legend) using specs from `elements/line-chart.md`"

### Request Full Dashboard:
> "Generate the complete dashboard following `full-dashboard.md` assembly"

---

## Filters Row (Context)

Below the "Overview" heading, include filter buttons:

```html
<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:24px">
    <h1>Overview</h1>
</div>
<div class="filters">
    <button class="filter-btn">Last 7 days</button>
    <button class="filter-btn active">Samsung</button>
    <button class="filter-btn">Chat GPT ✕</button>
    <button class="filter-btn">Tags ▾</button>
    <button class="filter-btn">Select Segment ▾</button>
</div>
```

---

## Container Styles

```css
.container {
    max-width: var(--max-width);
    margin: 0 auto;
    padding: var(--spacing-2xl);
}

h1 {
    font-family: var(--font-display);
    font-size: var(--font-size-xl);
    font-weight: var(--font-weight-bold);
    margin-bottom: var(--spacing-lg);
    color: var(--color-primary);
}

.filters {
    display: flex;
    gap: var(--spacing-sm);
    margin-bottom: var(--spacing-2xl);
}
```

---

## Two-Column Layout

```css
.two-col {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: var(--spacing-lg);
}
```

---

## Technical Requirements

- Single HTML file with embedded CSS and JS
- D3.js v7 from CDN: `https://d3js.org/d3.v7.min.js`
- Fonts loaded from: `../assets/fonts/`
- Logo loaded from: `../assets/logo.jpg`
- No other external dependencies

---

## Archive

Previous monolithic prompt files moved to `_archive/`:
- `ai-overview-dashboard.md`
- `dashboard-header.md`
