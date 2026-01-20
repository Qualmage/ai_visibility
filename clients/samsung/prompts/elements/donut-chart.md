# Sentiment Donut Chart

Small D3.js donut chart showing mentions by sentiment, used in KPI card 4.

> **Dependencies:** `../_base/design-tokens.md`, D3.js v7

---

## Visual Specification

```
    ╭─────╮
   ╱ ● ● ● ╲
  │  ●   ●  │   3K
  │  ●   ●  │
   ╲ ● ● ● ╱
    ╰─────╯
```

Small donut (80x80px) with three segments:
- Positive (green) - top
- Neutral (gray) - middle
- Negative (red) - bottom

---

## Placement

This donut is embedded in KPI Card 4 "Mentions by Sentiment":

```html
<div class="kpi-card">
    <div class="kpi-label">Mentions by Sentiment</div>
    <div class="kpi-content" style="flex-direction:row;align-items:center;gap:16px">
        <svg id="donutChart" width="80" height="80"></svg>
        <div style="font-family:'Samsung Sharp Sans',sans-serif;font-size:32px;font-weight:700;color:#1428A0">3K</div>
    </div>
</div>
```

---

## D3.js Code

```javascript
// Donut chart
const donutData = [
    {label:'Positive', value:1500, color:'#4caf50'},  // --color-success
    {label:'Neutral',  value:900,  color:'#9e9e9e'},  // --color-neutral
    {label:'Negative', value:600,  color:'#f44336'}   // --color-error
];

const donut = d3.select("#donutChart");
const radius = 40;
const innerRadius = 25;

const pie = d3.pie().value(d => d.value);
const arc = d3.arc().innerRadius(innerRadius).outerRadius(radius);

donut.selectAll("path")
    .data(pie(donutData))
    .join("path")
    .attr("d", arc)
    .attr("fill", d => d.data.color)
    .attr("transform", "translate(40,40)");
```

---

## Chart Specifications

| Property | Value |
|----------|-------|
| SVG Width | 80px |
| SVG Height | 80px |
| Outer Radius | 40px |
| Inner Radius | 25px |
| Center Offset | translate(40,40) |

---

## Segment Colors

| Segment | Token | Value |
|---------|-------|-------|
| Positive | `--color-success` | #4caf50 |
| Neutral | `--color-neutral` | #9e9e9e |
| Negative | `--color-error` | #f44336 |

---

## Mock Data

| Sentiment | Count | Percentage |
|-----------|-------|------------|
| Positive | 1,500 | 50% |
| Neutral | 900 | 30% |
| Negative | 600 | 20% |
| **Total** | **3,000** | 100% |

The total (3K) is displayed next to the donut, not as a center label.
