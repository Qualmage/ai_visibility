# Samsung Reusable Components

Shared component patterns used across dashboard elements. Reference design tokens from `design-tokens.md`.

---

## Filter Button

Pill-shaped buttons used for filters and toggles.

### CSS
```css
.filter-btn {
    font-family: var(--font-body);
    background: var(--color-bg-card);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-lg);
    padding: var(--spacing-sm) var(--spacing-lg);
    font-size: var(--font-size-base);
    cursor: pointer;
    transition: all 0.2s;
}

.filter-btn:hover {
    border-color: var(--color-primary);
}

.filter-btn.active {
    background: var(--color-primary);
    color: #fff;
    border-color: var(--color-primary);
}
```

### HTML
```html
<button class="filter-btn">Label</button>
<button class="filter-btn active">Active Label</button>
```

---

## Toggle Button Group

Smaller buttons for Day/Week/Month type toggles.

### CSS
```css
.toggle-group {
    display: flex;
    gap: var(--spacing-xs);
}

.toggle-btn {
    font-family: var(--font-body);
    background: var(--color-bg-card);
    border: 1px solid var(--color-border);
    padding: 6px 12px;
    font-size: var(--font-size-sm);
    border-radius: var(--radius-md);
    cursor: pointer;
    transition: all 0.2s;
}

.toggle-btn:hover {
    border-color: var(--color-primary);
}

.toggle-btn.active {
    background: var(--color-primary);
    color: #fff;
    border-color: var(--color-primary);
}
```

### HTML
```html
<div class="toggle-group">
    <button class="toggle-btn">Day</button>
    <button class="toggle-btn active">Week</button>
    <button class="toggle-btn">Month</button>
</div>
```

---

## Tab Buttons

Horizontal tab navigation.

### CSS
```css
.tabs {
    display: flex;
    gap: var(--spacing-sm);
    margin-bottom: var(--spacing-lg);
}

.tab-btn {
    font-family: var(--font-body);
    background: var(--color-bg-card);
    border: 1px solid var(--color-border);
    padding: var(--spacing-sm) var(--spacing-lg);
    border-radius: var(--radius-lg);
    cursor: pointer;
    font-size: var(--font-size-base);
    transition: all 0.2s;
}

.tab-btn:hover {
    border-color: var(--color-primary);
}

.tab-btn.active {
    background: var(--color-primary);
    color: #fff;
    border-color: var(--color-primary);
}
```

### HTML
```html
<div class="tabs">
    <button class="tab-btn active">Tab 1</button>
    <button class="tab-btn">Tab 2</button>
    <button class="tab-btn">Tab 3</button>
</div>
```

---

## Badge

Small labels for status indicators.

### CSS
```css
.badge {
    font-family: var(--font-body);
    padding: var(--spacing-xs) var(--spacing-sm);
    border-radius: var(--radius-sm);
    font-size: var(--font-size-sm);
    font-weight: 500;
}

.badge.new {
    background: var(--color-bg-success);
    color: var(--color-success);
}

.badge.lost {
    background: var(--color-bg-error);
    color: var(--color-error);
}
```

### HTML
```html
<span class="badge new">New</span>
<span class="badge lost">Lost</span>
```

---

## Card Container

White card with border used for dashboard sections.

### CSS
```css
.card {
    background: var(--color-bg-card);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-xl);
    padding: var(--spacing-xl);
}
```

### HTML
```html
<div class="card">
    <!-- Card content -->
</div>
```

---

## Section Title

Title row with optional right-side controls.

### CSS
```css
.section-title {
    font-family: var(--font-display);
    font-size: var(--font-size-lg);
    font-weight: var(--font-weight-bold);
    margin-bottom: var(--spacing-md);
    display: flex;
    justify-content: space-between;
    align-items: center;
    color: var(--color-primary);
}
```

### HTML
```html
<div class="section-title">
    <span>Section Name</span>
    <div class="toggle-group">
        <!-- Optional controls -->
    </div>
</div>
```

---

## Change Indicator

For showing positive/negative changes in metrics.

### CSS
```css
.change {
    font-size: 13px;
    margin-top: var(--spacing-xs);
}

.change.positive {
    color: var(--color-success);
}

.change.negative {
    color: var(--color-error);
}
```

### HTML
```html
<div class="change positive">↑ +5%</div>
<div class="change negative">↓ -3%</div>
```

---

## Legend Item

For chart legends with checkboxes.

### CSS
```css
.legend {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-sm);
    font-size: var(--font-size-base);
}

.legend-item {
    display: flex;
    align-items: center;
    gap: 6px;
}

.legend-color {
    width: 12px;
    height: 12px;
    border-radius: 2px;
}

input[type="checkbox"] {
    accent-color: var(--color-primary);
}
```

### HTML
```html
<div class="legend">
    <label class="legend-item">
        <input type="checkbox" checked>
        <span class="legend-color" style="background: var(--color-brand-samsung)"></span>
        Samsung
    </label>
</div>
```

---

## Pagination

For data table pagination.

### CSS
```css
.pagination {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: var(--spacing-md);
    font-size: var(--font-size-base);
}
```

### HTML
```html
<div class="pagination">
    <span>1-10 of 529</span>
    <div style="display: flex; gap: var(--spacing-sm)">
        <button class="filter-btn">&lt;</button>
        <button class="filter-btn">&gt;</button>
    </div>
</div>
```

---

## Base Table Styles

### CSS
```css
table {
    width: 100%;
    border-collapse: collapse;
    font-size: var(--font-size-base);
}

th, td {
    padding: var(--spacing-md);
    text-align: left;
    border-bottom: 1px solid var(--color-border);
}

th {
    font-family: var(--font-display);
    font-weight: var(--font-weight-bold);
    color: var(--color-primary);
}
```
