# KPI Cards Row

Row of 4 KPI metric cards displayed below the filters.

> **Dependencies:** `../_base/design-tokens.md`, `../_base/fonts.md`, `../_base/components.md`

---

## Visual Specification

```
┌──────────────┐ ┌──────────────┐ ┌─────────────────────────┐ ┌─────────────────────────┐
│ SHARE OF     │ │ BRAND        │ │ PROMPTS                 │ │ MENTIONS BY SENTIMENT   │
│ VOICE        │ │ VISIBILITY   │ │ With mention: 240 +182  │ │ [DONUT]  3K             │
│ 57%          │ │ 63%          │ │ Without: 143 -123       │ │                         │
│ ↓ -1%        │ │ ↓ -12%       │ │                         │ │                         │
└──────────────┘ └──────────────┘ └─────────────────────────┘ └─────────────────────────┘
```

---

## Layout

- CSS Grid: `grid-template-columns: repeat(4, 1fr)`
- Gap: `--spacing-lg` (16px)
- Cards have equal widths, uniform height (`align-items: stretch`)

---

## Card Structure

### Base Card Styles
```css
.kpi-row {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: var(--spacing-lg);
    margin-bottom: var(--spacing-2xl);
    align-items: stretch;
}

.kpi-card {
    background: var(--color-bg-card);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-xl);
    padding: var(--spacing-xl);
    display: grid;
    grid-template-rows: auto 1fr;
    min-height: 120px;
}

.kpi-label {
    font-size: var(--font-size-xs);
    text-transform: uppercase;
    color: var(--color-text-secondary);
    letter-spacing: 0.5px;
    font-weight: 500;
}

.kpi-value {
    font-family: var(--font-display);
    font-size: var(--font-size-metric);
    font-weight: var(--font-weight-bold);
    color: var(--color-primary);
    line-height: var(--line-height-tight);
}

.kpi-content {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: flex-start;
}

.kpi-change {
    font-size: 13px;
    margin-top: var(--spacing-xs);
}

.kpi-change.positive { color: var(--color-success); }
.kpi-change.negative { color: var(--color-error); }
```

---

## Card Types

### Card 1: Share of Voice
Simple metric with change indicator.

```html
<div class="kpi-card">
    <div class="kpi-label">Share of Voice</div>
    <div class="kpi-content">
        <div class="kpi-value">57%</div>
        <div class="kpi-change negative">↓ -1%</div>
    </div>
</div>
```

### Card 2: Brand Visibility
Simple metric with change indicator.

```html
<div class="kpi-card">
    <div class="kpi-label">Brand Visibility</div>
    <div class="kpi-content">
        <div class="kpi-value">63%</div>
        <div class="kpi-change negative">↓ -12%</div>
    </div>
</div>
```

### Card 3: Prompts
Two-row display with inline badges.

```html
<div class="kpi-card">
    <div class="kpi-label">Prompts</div>
    <div class="kpi-content" style="justify-content:flex-start;gap:12px;padding-top:8px">
        <div style="display:flex;justify-content:space-between;align-items:center;width:100%">
            <span style="font-size:14px">Responses with brand mention</span>
            <span class="badge new">240 <span style="color:var(--color-success)">+182</span></span>
        </div>
        <div style="display:flex;justify-content:space-between;align-items:center;width:100%">
            <span style="font-size:14px">Responses without brand mention</span>
            <span class="badge lost">143 <span style="color:var(--color-error)">-123</span></span>
        </div>
    </div>
</div>
```

### Card 4: Mentions by Sentiment
Donut chart with total count.

```html
<div class="kpi-card">
    <div class="kpi-label">Mentions by Sentiment</div>
    <div class="kpi-content" style="flex-direction:row;align-items:center;gap:16px">
        <svg id="donutChart" width="80" height="80"></svg>
        <div style="font-family:var(--font-display);font-size:32px;font-weight:700;color:var(--color-primary)">3K</div>
    </div>
</div>
```

> See `donut-chart.md` for the D3.js code to populate `#donutChart`

---

## Complete Row HTML

```html
<div class="kpi-row">
    <div class="kpi-card">
        <div class="kpi-label">Share of Voice</div>
        <div class="kpi-content">
            <div class="kpi-value">57%</div>
            <div class="kpi-change negative">↓ -1%</div>
        </div>
    </div>
    <div class="kpi-card">
        <div class="kpi-label">Brand Visibility</div>
        <div class="kpi-content">
            <div class="kpi-value">63%</div>
            <div class="kpi-change negative">↓ -12%</div>
        </div>
    </div>
    <div class="kpi-card">
        <div class="kpi-label">Prompts</div>
        <div class="kpi-content" style="justify-content:flex-start;gap:12px;padding-top:8px">
            <div style="display:flex;justify-content:space-between;align-items:center;width:100%">
                <span style="font-size:14px">Responses with brand mention</span>
                <span class="badge new">240 <span style="color:#4caf50">+182</span></span>
            </div>
            <div style="display:flex;justify-content:space-between;align-items:center;width:100%">
                <span style="font-size:14px">Responses without brand mention</span>
                <span class="badge lost">143 <span style="color:#f44336">-123</span></span>
            </div>
        </div>
    </div>
    <div class="kpi-card">
        <div class="kpi-label">Mentions by Sentiment</div>
        <div class="kpi-content" style="flex-direction:row;align-items:center;gap:16px">
            <svg id="donutChart" width="80" height="80"></svg>
            <div style="font-family:'Samsung Sharp Sans',sans-serif;font-size:32px;font-weight:700;color:#1428A0">3K</div>
        </div>
    </div>
</div>
```

---

## Mock Data

| Metric | Value | Change | Direction |
|--------|-------|--------|-----------|
| Share of Voice | 57% | -1% | negative |
| Brand Visibility | 63% | -12% | negative |
| Prompts with mention | 240 | +182 | positive |
| Prompts without mention | 143 | -123 | negative |
| Total Mentions | 3,000 | - | - |
