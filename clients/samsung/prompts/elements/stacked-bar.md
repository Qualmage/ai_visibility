# Sentiment Over Time Stacked Bar Chart

D3.js stacked bar chart showing daily sentiment breakdown.

> **Dependencies:** `../_base/design-tokens.md`, `../_base/components.md`, D3.js v7

---

## Visual Specification

```
Sentiment Over Time
┌────────────────────────────────────────┐
│  3.5K ██████████████████████████████   │
│       ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓    │
│       ░░░░░░░░░░░░░░░░░░░░░░░░░░░░    │
│     0 ├──┬──┬──┬──┬──┬──┬──┤          │
│       14 15 16 17 18 19 20             │
│                                        │
│  ■ negative  ■ neutral  ■ positive     │
└────────────────────────────────────────┘
```

---

## Container Structure

This chart appears in the right column of a two-column layout.

```html
<div class="chart-container">
    <div class="section-title">Sentiment Over Time</div>
    <svg id="stackedBar" width="350" height="200"></svg>
    <div style="display:flex;gap:12px;justify-content:center;font-size:12px;margin-top:8px">
        <span><span style="display:inline-block;width:10px;height:10px;background:#f44336;border-radius:2px;margin-right:4px"></span>negative</span>
        <span><span style="display:inline-block;width:10px;height:10px;background:#9e9e9e;border-radius:2px;margin-right:4px"></span>neutral</span>
        <span><span style="display:inline-block;width:10px;height:10px;background:#4caf50;border-radius:2px;margin-right:4px"></span>positive</span>
    </div>
</div>
```

---

## D3.js Code

```javascript
// Stacked bar chart
const stackedData = [
    {date:'Jan14', negative:800,  neutral:1200, positive:1400},
    {date:'Jan15', negative:850,  neutral:1250, positive:1450},
    {date:'Jan16', negative:900,  neutral:1300, positive:1500},
    {date:'Jan17', negative:950,  neutral:1350, positive:1550},
    {date:'Jan18', negative:1000, neutral:1400, positive:1600},
    {date:'Jan19', negative:1050, neutral:1450, positive:1650},
    {date:'Jan20', negative:1100, neutral:1500, positive:1700}
];

const dates = ['Jan14','Jan15','Jan16','Jan17','Jan18','Jan19','Jan20'];

const stackedSvg = d3.select("#stackedBar");
const sx = d3.scaleBand()
    .domain(dates)
    .range([0, 300])
    .padding(0.2);

const sy = d3.scaleLinear()
    .domain([0, 3500])
    .range([150, 0]);

const stack = d3.stack().keys(['negative', 'neutral', 'positive']);
const series = stack(stackedData);

const sg = stackedSvg.append("g")
    .attr("transform", "translate(20,10)");

// Bars
sg.selectAll("g")
    .data(series)
    .join("g")
    .attr("fill", d => {
        if (d.key === 'negative') return '#f44336';
        if (d.key === 'neutral') return '#9e9e9e';
        return '#4caf50';
    })
    .selectAll("rect")
    .data(d => d)
    .join("rect")
    .attr("x", d => sx(d.data.date))
    .attr("y", d => sy(d[1]))
    .attr("height", d => sy(d[0]) - sy(d[1]))
    .attr("width", sx.bandwidth());

// X-axis
sg.append("g")
    .attr("transform", "translate(0,150)")
    .call(d3.axisBottom(sx));
```

---

## Chart Specifications

| Property | Value |
|----------|-------|
| SVG Width | 350px |
| SVG Height | 200px |
| Chart Width | 300px |
| Chart Height | 150px |
| Transform | translate(20,10) |
| Y-axis Range | 0 to 3,500 |
| Bar Padding | 0.2 |

---

## Stacking Order (bottom to top)

1. **Negative** - `#f44336` (--color-error)
2. **Neutral** - `#9e9e9e` (--color-neutral)
3. **Positive** - `#4caf50` (--color-success)

---

## Legend HTML

```html
<div style="display:flex;gap:12px;justify-content:center;font-size:12px;margin-top:8px">
    <span>
        <span style="display:inline-block;width:10px;height:10px;background:#f44336;border-radius:2px;margin-right:4px"></span>
        negative
    </span>
    <span>
        <span style="display:inline-block;width:10px;height:10px;background:#9e9e9e;border-radius:2px;margin-right:4px"></span>
        neutral
    </span>
    <span>
        <span style="display:inline-block;width:10px;height:10px;background:#4caf50;border-radius:2px;margin-right:4px"></span>
        positive
    </span>
</div>
```

---

## Mock Data

| Date | Negative | Neutral | Positive | Total |
|------|----------|---------|----------|-------|
| Jan14 | 800 | 1,200 | 1,400 | 3,400 |
| Jan15 | 850 | 1,250 | 1,450 | 3,550 |
| Jan16 | 900 | 1,300 | 1,500 | 3,700 |
| Jan17 | 950 | 1,350 | 1,550 | 3,850 |
| Jan18 | 1,000 | 1,400 | 1,600 | 4,000 |
| Jan19 | 1,050 | 1,450 | 1,650 | 4,150 |
| Jan20 | 1,100 | 1,500 | 1,700 | 4,300 |
