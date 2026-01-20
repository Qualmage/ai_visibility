# Brand Leaderboard Table

Table showing brand rankings by Share of Voice with inline bar charts.

> **Dependencies:** `../_base/design-tokens.md`, `../_base/components.md`

---

## Visual Specification

```
Brand Leaderboard                                    3/9
┌──────────┬────────────┬─────────────────────────────────┐
│ SoV Rank │ Brand      │ Share                           │
├──────────┼────────────┼─────────────────────────────────┤
│    1     │ ⬤ Samsung  │ 57% ████████████████████████    │
│    2     │ ⬤ LG       │ 26% ███████████                  │
│    3     │ ⬤ Sony     │ 21% █████████                    │
│    4     │ ⬤ TCL      │ 19% ████████                     │
│    5     │ ⬤ Hisense  │ 17% ███████                      │
│    6     │ ⬤ Xbox     │  3% █                            │
│    7     │ ⬤ Roku     │  3% █                            │
└──────────┴────────────┴─────────────────────────────────┘
```

---

## Container Structure

This table appears in the left column of a two-column layout.

```html
<div class="chart-container">
    <div class="section-title">
        Brand Leaderboard
        <span style="font-size:12px;color:#666">3/9</span>
    </div>
    <table>
        <!-- Table content -->
    </table>
</div>
```

---

## Complete HTML

```html
<div class="chart-container">
    <div class="section-title">Brand Leaderboard <span style="font-size:12px;color:#666">3/9</span></div>
    <table>
        <thead>
            <tr>
                <th>SoV Rank</th>
                <th>Brand</th>
                <th>Share</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>1</td>
                <td>⬤ Samsung</td>
                <td>57% <svg width="100" height="8"><rect x="0" y="0" width="57" height="8" fill="#1428A0" rx="4"/></svg></td>
            </tr>
            <tr>
                <td>2</td>
                <td>⬤ LG</td>
                <td>26% <svg width="100" height="8"><rect x="0" y="0" width="26" height="8" fill="#A50034" rx="4"/></svg></td>
            </tr>
            <tr>
                <td>3</td>
                <td>⬤ Sony</td>
                <td>21% <svg width="100" height="8"><rect x="0" y="0" width="21" height="8" fill="#000" rx="4"/></svg></td>
            </tr>
            <tr>
                <td>4</td>
                <td>⬤ TCL</td>
                <td>19% <svg width="100" height="8"><rect x="0" y="0" width="19" height="8" fill="#E31937" rx="4"/></svg></td>
            </tr>
            <tr>
                <td>5</td>
                <td>⬤ Hisense</td>
                <td>17% <svg width="100" height="8"><rect x="0" y="0" width="17" height="8" fill="#00A0DF" rx="4"/></svg></td>
            </tr>
            <tr>
                <td>6</td>
                <td>⬤ Xbox</td>
                <td>3% <svg width="100" height="8"><rect x="0" y="0" width="3" height="8" fill="#107C10" rx="4"/></svg></td>
            </tr>
            <tr>
                <td>7</td>
                <td>⬤ Roku</td>
                <td>3% <svg width="100" height="8"><rect x="0" y="0" width="3" height="8" fill="#6C3C97" rx="4"/></svg></td>
            </tr>
        </tbody>
    </table>
</div>
```

---

## Inline Bar Chart

Each row has an inline SVG bar chart in the Share column:

```html
<svg width="100" height="8">
    <rect x="0" y="0" width="[PERCENTAGE]" height="8" fill="[BRAND_COLOR]" rx="4"/>
</svg>
```

- Width: percentage value (e.g., 57 for 57%)
- Height: 8px
- Border radius: 4px
- Color: brand color from design tokens

---

## Two-Column Layout

The leaderboard appears alongside the Sentiment Over Time chart:

```html
<div class="two-col">
    <div class="chart-container">
        <!-- Brand Leaderboard -->
    </div>
    <div class="chart-container">
        <!-- Sentiment Over Time -->
    </div>
</div>
```

```css
.two-col {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: var(--spacing-lg);
}
```

---

## Mock Data

| Rank | Brand | Share | Color |
|------|-------|-------|-------|
| 1 | Samsung | 57% | #1428A0 |
| 2 | LG | 26% | #A50034 |
| 3 | Sony | 21% | #000000 |
| 4 | TCL | 19% | #E31937 |
| 5 | Hisense | 17% | #00A0DF |
| 6 | Xbox | 3% | #107C10 |
| 7 | Roku | 3% | #6C3C97 |

---

## Header Badge

"3/9" indicates 3 columns visible out of 9 available (column selector functionality).
