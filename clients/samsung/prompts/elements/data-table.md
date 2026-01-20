# Brand/Product Performance Table

Data table showing prompt rankings and position changes.

> **Dependencies:** `../_base/design-tokens.md`, `../_base/components.md`

---

## Visual Specification

```
Brand / Product Performance (All Products)                    [Advanced ▾]
┌───┬───────────────────────────────────┬───────┬────────────┬───────┬───────┬────────┐
│ ☐ │ Prompt                            │ Model │ Product    │Jan 14 │Jan 20 │ Change │
├───┼───────────────────────────────────┼───────┼────────────┼───────┼───────┼────────┤
│ ☐ │ best tv for casual gaming         │  ⚙   │ S95F       │   —   │   1   │  New   │
│ ☐ │ 85 inch tv reviews                │  ⚙   │ QN90D      │   —   │   3   │  New   │
│ ☐ │ Samsung The Frame Pro reviews     │  ⚙   │ Frame/Pro  │   —   │   1   │  New   │
│ ☐ │ what tv should I buy?             │  ⚙   │ S95H QD    │   —   │   3   │  New   │
│ ☐ │ Is AI upscaling TV worth it?      │  ⚙   │ Q8F Vision │   6   │   —   │  Lost  │
└───┴───────────────────────────────────┴───────┴────────────┴───────┴───────┴────────┘
                                                               1-10 of 529    < >
```

---

## Container Structure

```html
<div class="chart-container">
    <div class="section-title">
        Brand / Product Performance (All Products)
        <button class="filter-btn">Advanced ▾</button>
    </div>
    <table>
        <!-- Table content -->
    </table>
    <div class="pagination">
        <span>1-10 of 529</span>
        <div style="display:flex;gap:8px">
            <button class="filter-btn">&lt;</button>
            <button class="filter-btn">&gt;</button>
        </div>
    </div>
</div>
```

---

## Complete HTML

```html
<div class="chart-container">
    <div class="section-title">
        Brand / Product Performance (All Products)
        <button class="filter-btn">Advanced ▾</button>
    </div>
    <table>
        <thead>
            <tr>
                <th><input type="checkbox"></th>
                <th>Prompt</th>
                <th>Model</th>
                <th>Product</th>
                <th>Jan 14</th>
                <th>Jan 20</th>
                <th>Change</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><input type="checkbox"></td>
                <td style="color:#1428A0;cursor:pointer">best tv for casual gaming</td>
                <td>⚙</td>
                <td>S95F</td>
                <td>—</td>
                <td>1</td>
                <td><span class="badge new">New</span></td>
            </tr>
            <tr>
                <td><input type="checkbox"></td>
                <td style="color:#1428A0;cursor:pointer">85 inch tv reviews</td>
                <td>⚙</td>
                <td>QN90D</td>
                <td>—</td>
                <td>3</td>
                <td><span class="badge new">New</span></td>
            </tr>
            <tr>
                <td><input type="checkbox"></td>
                <td style="color:#1428A0;cursor:pointer">Samsung The Frame Pro reviews</td>
                <td>⚙</td>
                <td>Frame/Pro</td>
                <td>—</td>
                <td>1</td>
                <td><span class="badge new">New</span></td>
            </tr>
            <tr>
                <td><input type="checkbox"></td>
                <td style="color:#1428A0;cursor:pointer">what tv should I buy?</td>
                <td>⚙</td>
                <td>S95H QD</td>
                <td>—</td>
                <td>3</td>
                <td><span class="badge new">New</span></td>
            </tr>
            <tr>
                <td><input type="checkbox"></td>
                <td style="color:#1428A0;cursor:pointer">Is AI upscaling TV worth it?</td>
                <td>⚙</td>
                <td>Q8F Vision</td>
                <td>6</td>
                <td>—</td>
                <td><span class="badge lost">Lost</span></td>
            </tr>
        </tbody>
    </table>
    <div class="pagination">
        <span>1-10 of 529</span>
        <div style="display:flex;gap:8px">
            <button class="filter-btn">&lt;</button>
            <button class="filter-btn">&gt;</button>
        </div>
    </div>
</div>
```

---

## Column Specifications

| Column | Width | Content |
|--------|-------|---------|
| Checkbox | auto | `<input type="checkbox">` |
| Prompt | flex | Blue link text (`color: #1428A0; cursor: pointer`) |
| Model | auto | Gear icon ⚙ |
| Product | auto | Product name |
| Jan 14 | auto | Position number or "—" |
| Jan 20 | auto | Position number or "—" |
| Change | auto | Badge (New/Lost) |

---

## Badge Styles

### New (Gained position)
```html
<span class="badge new">New</span>
```
- Background: `--color-bg-success` (#e8f5e9)
- Text: `--color-success` (#4caf50)

### Lost (Lost position)
```html
<span class="badge lost">Lost</span>
```
- Background: `--color-bg-error` (#ffebee)
- Text: `--color-error` (#f44336)

### No Data
```html
<td>—</td>
```
- Use em-dash (—) for empty/no data cells

---

## Mock Data

| Prompt | Product | Jan 14 | Jan 20 | Change |
|--------|---------|--------|--------|--------|
| best tv for casual gaming | S95F | — | 1 | New |
| 85 inch tv reviews | QN90D | — | 3 | New |
| Samsung The Frame Pro reviews | Frame/Pro | — | 1 | New |
| what tv should I buy? | S95H QD | — | 3 | New |
| Is AI upscaling TV worth it? | Q8F Vision | 6 | — | Lost |
| What are the main features of art TVs vs regular? | Frame Pro Neo QLED | — | 2 | New |
| Which 4K TVs are best for gaming? | S95F | — | 2 | New |
| tv with 120Hz refresh rate and HDMI 2.1 | S95F OLED TV | — | 1 | New |
| S84F reviews | S84F OLED TV | — | 1 | New |
| tv for sports with great color accuracy | S95C | — | 1 | New |

---

## Pagination

```html
<div class="pagination">
    <span>1-10 of 529</span>
    <div style="display:flex;gap:8px">
        <button class="filter-btn">&lt;</button>
        <button class="filter-btn">&gt;</button>
    </div>
</div>
```

Total records: 529
