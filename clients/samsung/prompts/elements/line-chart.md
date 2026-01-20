# Historical Trend Line Chart

Multi-line D3.js chart showing brand share of voice over time.

> **Dependencies:** `../_base/design-tokens.md`, `../_base/components.md`, D3.js v7

---

## Visual Specification

```
Historical Trend                                    [Day] [Week] [Month]
[Share of Voice] [Brand Visibility] [Mentions] [Avg. Position]

┌───────────────────────────────────────────────────────┬───────────────┐
│  60% ─────────────────────────────────────────────    │ ☑ Samsung     │
│  50%                                                  │ ☑ LG          │
│  40%     ════════════════════════════════════         │ ☑ Sony        │
│  30%                                                  │ ☑ TCL         │
│  20% ──────────────────────────────────────────────   │ ☑ Hisense     │
│  10%                                                  │ ☑ Xbox        │
│   0%                                                  │ ☑ Roku        │
│      Jan14  Jan15  Jan16  Jan17  Jan18  Jan19  Jan20  │ + Add Brand   │
└───────────────────────────────────────────────────────┴───────────────┘
```

---

## Container Structure

```css
.chart-container {
    background: var(--color-bg-card);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-xl);
    padding: var(--spacing-xl);
    margin-bottom: var(--spacing-2xl);
}
```

---

## HTML Structure

```html
<div class="chart-container">
    <div class="section-title">
        <span>Historical Trend</span>
        <div class="toggle-group">
            <button class="toggle-btn">Day</button>
            <button class="toggle-btn active">Week</button>
            <button class="toggle-btn">Month</button>
        </div>
    </div>
    <div class="tabs">
        <button class="tab-btn active">Share of Voice</button>
        <button class="tab-btn">Brand Visibility</button>
        <button class="tab-btn">Mentions</button>
        <button class="tab-btn">Avg. Position</button>
    </div>
    <div style="display:flex;gap:24px">
        <svg id="lineChart" width="800" height="300"></svg>
        <div class="legend">
            <label class="legend-item"><input type="checkbox" checked> <span class="legend-color" style="background:#1428A0"></span>Samsung</label>
            <label class="legend-item"><input type="checkbox" checked> <span class="legend-color" style="background:#A50034"></span>LG</label>
            <label class="legend-item"><input type="checkbox" checked> <span class="legend-color" style="background:#000"></span>Sony</label>
            <label class="legend-item"><input type="checkbox" checked> <span class="legend-color" style="background:#E31937"></span>TCL</label>
            <label class="legend-item"><input type="checkbox" checked> <span class="legend-color" style="background:#00A0DF"></span>Hisense</label>
            <label class="legend-item"><input type="checkbox" checked> <span class="legend-color" style="background:#107C10"></span>Xbox</label>
            <label class="legend-item"><input type="checkbox" checked> <span class="legend-color" style="background:#6C3C97"></span>Roku</label>
            <button class="filter-btn" style="margin-top:8px">+ Add Brand</button>
        </div>
    </div>
</div>
```

---

## D3.js Code

```javascript
// Line chart
const dates = ['Jan14','Jan15','Jan16','Jan17','Jan18','Jan19','Jan20'];
const brands = [
    {name:'Samsung',color:'#1428A0',values:[54,55,56,57,56,56,57]},
    {name:'LG',color:'#A50034',values:[24,25,25,26,26,26,26]},
    {name:'Sony',color:'#000',values:[20,20,21,21,21,21,21]},
    {name:'TCL',color:'#E31937',values:[18,18,19,19,19,19,19]},
    {name:'Hisense',color:'#00A0DF',values:[16,16,17,17,17,17,17]},
    {name:'Xbox',color:'#107C10',values:[3,3,3,3,3,3,3]},
    {name:'Roku',color:'#6C3C97',values:[3,3,3,3,3,3,3]}
];

const lineSvg = d3.select("#lineChart");
const margin = {top:20,right:20,bottom:30,left:50};
const width = 800 - margin.left - margin.right;
const height = 300 - margin.top - margin.bottom;

const x = d3.scalePoint().domain(dates).range([0,width]);
const y = d3.scaleLinear().domain([0,60]).range([height,0]);

const line = d3.line()
    .x((d,i)=>x(dates[i]))
    .y(d=>y(d))
    .curve(d3.curveMonotoneX);

const g = lineSvg.append("g")
    .attr("transform",`translate(${margin.left},${margin.top})`);

// Grid lines
g.selectAll(".grid")
    .data(y.ticks(6))
    .join("line")
    .attr("class","grid")
    .attr("x1",0)
    .attr("x2",width)
    .attr("y1",d=>y(d))
    .attr("y2",d=>y(d))
    .attr("stroke","#e0e0e0")
    .attr("stroke-dasharray","2,2");

// Lines
brands.forEach(b=>{
    g.append("path")
        .datum(b.values)
        .attr("fill","none")
        .attr("stroke",b.color)
        .attr("stroke-width",2)
        .attr("d",line);
});

// Axes
g.append("g")
    .attr("transform",`translate(0,${height})`)
    .call(d3.axisBottom(x));

g.append("g")
    .call(d3.axisLeft(y).tickFormat(d=>d+"%"));
```

---

## Chart Specifications

| Property | Value |
|----------|-------|
| SVG Width | 800px |
| SVG Height | 300px |
| Margins | top: 20, right: 20, bottom: 30, left: 50 |
| Y-axis Range | 0% to 60% |
| Curve Type | `d3.curveMonotoneX` (smooth) |
| Grid Lines | Light gray (#e0e0e0), dashed |
| Line Width | 2px |

---

## Mock Data

| Brand | Color | Jan14 | Jan15 | Jan16 | Jan17 | Jan18 | Jan19 | Jan20 |
|-------|-------|-------|-------|-------|-------|-------|-------|-------|
| Samsung | #1428A0 | 54% | 55% | 56% | 57% | 56% | 56% | 57% |
| LG | #A50034 | 24% | 25% | 25% | 26% | 26% | 26% | 26% |
| Sony | #000000 | 20% | 20% | 21% | 21% | 21% | 21% | 21% |
| TCL | #E31937 | 18% | 18% | 19% | 19% | 19% | 19% | 19% |
| Hisense | #00A0DF | 16% | 16% | 17% | 17% | 17% | 17% | 17% |
| Xbox | #107C10 | 3% | 3% | 3% | 3% | 3% | 3% | 3% |
| Roku | #6C3C97 | 3% | 3% | 3% | 3% | 3% | 3% | 3% |
