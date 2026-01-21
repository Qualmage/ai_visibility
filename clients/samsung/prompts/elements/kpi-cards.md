# Element: KPI Cards (Client Spec)

> 4 KPI cards across the top row for S.com Overview performance metrics.
> Based on: "Ai reporting Client ask from Jason.pdf" - Section 1

## Required Tokens
```
--color-primary, --color-success, --color-bg-card, --color-border,
--color-text-secondary, --font-display, --font-size-xs, --font-size-metric,
--font-weight-bold, --spacing-xs, --spacing-md, --spacing-xl, --radius-xl, --line-height-tight
```

---

## Icon Assets

| Card | File | Description |
|------|------|-------------|
| Share of Voice | `../assets/sov.jpg` | Speech bubble with bar chart |
| Source Visibility | `../assets/source_visi.jpg` | Monitor with eye |
| Referral Traffic | `../assets/referral.jpg` | Arrows converging to center |
| AI Visibility | `../assets/ai visi.jpg` | Brain with gear and sparkles |

---

## Visual Specification

```
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│  [sov.jpg]       │ │  [source_visi]   │ │  [referral]      │ │  [ai visi]       │
│  SHARE OF VOICE  │ │  SOURCE          │ │  REFERRAL        │ │  AI VISIBILITY   │
│  65%             │ │  VISIBILITY      │ │  TRAFFIC         │ │  91              │
│  N/A             │ │  42%             │ │  106,445         │ │                  │
│                  │ │  N/A             │ │  +10,989         │ │                  │
└──────────────────┘ └──────────────────┘ └──────────────────┘ └──────────────────┘
```

---

## Layout

```css
.kpi-row {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: var(--spacing-lg);
    margin-bottom: var(--spacing-2xl);
}
```

---

## Card Structure

```css
.kpi-card {
    background: var(--color-bg-card);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-xl);
    padding: var(--spacing-xl);
    min-height: 140px;
}

.kpi-icon {
    width: 40px;
    height: 40px;
    margin-bottom: var(--spacing-md);
    object-fit: contain;
}

.kpi-label {
    font-size: var(--font-size-xs);
    text-transform: uppercase;
    color: var(--color-text-secondary);
    letter-spacing: 0.5px;
    font-weight: 500;
    margin-bottom: var(--spacing-xs);
}

.kpi-value {
    font-family: var(--font-display);
    font-size: var(--font-size-metric);
    font-weight: var(--font-weight-bold);
    color: var(--color-primary);
    line-height: var(--line-height-tight);
}

.kpi-change {
    font-size: 13px;
    margin-top: var(--spacing-xs);
    color: var(--color-text-secondary);
}

.kpi-change.positive { color: var(--color-success); }
.kpi-change.negative { color: var(--color-error); }
```

---

## Card 1: Share of Voice

**Icon:** `sov.jpg` - Speech bubble with bar chart
**Value:** Percentage (e.g., 65%)
**Change:** May be N/A

```html
<div class="kpi-card">
    <img class="kpi-icon" src="../assets/sov.jpg" alt="Share of Voice">
    <div class="kpi-label">Share of Voice</div>
    <div class="kpi-value">65%</div>
    <div class="kpi-change">N/A</div>
</div>
```

---

## Card 2: Source Visibility

**Icon:** `source_visi.jpg` - Monitor with eye
**Value:** Percentage (e.g., 42%)
**Change:** May be N/A

```html
<div class="kpi-card">
    <img class="kpi-icon" src="../assets/source_visi.jpg" alt="Source Visibility">
    <div class="kpi-label">Source Visibility</div>
    <div class="kpi-value">42%</div>
    <div class="kpi-change">N/A</div>
</div>
```

---

## Card 3: Referral Traffic

**Icon:** `referral.jpg` - Arrows converging to center
**Value:** Number with commas (e.g., 106,445)
**Change:** Absolute number with +/- (e.g., +10,989)

```html
<div class="kpi-card">
    <img class="kpi-icon" src="../assets/referral.jpg" alt="Referral Traffic">
    <div class="kpi-label">Referral Traffic</div>
    <div class="kpi-value">106,445</div>
    <div class="kpi-change positive">+10,989</div>
</div>
```

---

## Card 4: AI Visibility

**Icon:** `ai visi.jpg` - Brain with gear and sparkles
**Value:** Score number (e.g., 91)

```html
<div class="kpi-card">
    <img class="kpi-icon" src="../assets/ai visi.jpg" alt="AI Visibility">
    <div class="kpi-label">AI Visibility</div>
    <div class="kpi-value">91</div>
</div>
```

---

## Complete Row Assembly

```html
<div class="kpi-row">
    <!-- Card 1: Share of Voice -->
    <div class="kpi-card">
        <img class="kpi-icon" src="../assets/sov.jpg" alt="Share of Voice">
        <div class="kpi-label">Share of Voice</div>
        <div class="kpi-value">65%</div>
        <div class="kpi-change">N/A</div>
    </div>

    <!-- Card 2: Source Visibility -->
    <div class="kpi-card">
        <img class="kpi-icon" src="../assets/source_visi.jpg" alt="Source Visibility">
        <div class="kpi-label">Source Visibility</div>
        <div class="kpi-value">42%</div>
        <div class="kpi-change">N/A</div>
    </div>

    <!-- Card 3: Referral Traffic -->
    <div class="kpi-card">
        <img class="kpi-icon" src="../assets/referral.jpg" alt="Referral Traffic">
        <div class="kpi-label">Referral Traffic</div>
        <div class="kpi-value">106,445</div>
        <div class="kpi-change positive">+10,989</div>
    </div>

    <!-- Card 4: AI Visibility -->
    <div class="kpi-card">
        <img class="kpi-icon" src="../assets/ai visi.jpg" alt="AI Visibility">
        <div class="kpi-label">AI Visibility</div>
        <div class="kpi-value">91</div>
    </div>
</div>
```

---

## Data Binding Reference

| Card | Data Field | Format | Example |
|------|------------|--------|---------|
| Share of Voice | `sov` | Percentage with % | 65% |
| Source Visibility | `sourceVisibility` | Percentage with % | 42% |
| Referral Traffic | `referralTraffic` | Number with commas | 106,445 |
| AI Visibility | `aiVisibility` | Integer score (0-100) | 91 |

**Change values:**
- `N/A` when no comparison data available
- `+X%` or `-X%` with `.positive` or `.negative` class for percentage metrics
- Referral Traffic shows both absolute and percentage: `+10,989 (+10.3%)`

**Change state colors:**
| State | Class | Color | Display |
|-------|-------|-------|---------|
| N/A | `.na` | `#666666` (grey) | N/A |
| No Change | `.no-change` | `#feb447` (yellow) | — 0% |
| Increase | `.increase` | `#96d551` (green) | ↑ +X% |
| Decrease | `.decrease` | `#ff4438` (red) | ↓ -X% |
