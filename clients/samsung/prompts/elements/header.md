# Dashboard Header

**Status:** ✅ APPROVED (matches v3-ai-overview.html)

The page header for Samsung AI Visibility Dashboard.

> **Dependencies:** `../_base/design-tokens.md`, `../_base/fonts.md`

---

## Visual Specification

```
┌─────────────────────────────────────────────────────────────────────┐
│  AI Visibility Dashboard                              [SAMSUNG LOGO] │
└─────────────────────────────────────────────────────────────────────┘
```

### Layout
- Full-width background: `--color-bg-header` (#f7f7f7)
- Bottom border: 3px solid `--color-primary` (#1428A0)
- Shadow: `--shadow-sm`
- Content area: max-width `--max-width` (1400px), centered

### Title
- Text: "AI Visibility Dashboard"
- Font: `--font-display` (Samsung Sharp Sans)
- Size: `--font-size-2xl` (28px)
- Weight: `--font-weight-bold` (700)
- Color: `--color-primary` (#1428A0)

### Logo
- Image: `../assets/logo.jpg`
- Height: 36px (width auto)
- Alt text: "Samsung"

---

## Output HTML

```html
<header style="background: var(--color-bg-header); border-bottom: 3px solid var(--color-border-accent); margin-bottom: var(--spacing-2xl); box-shadow: var(--shadow-sm)">
    <div style="max-width: var(--max-width); margin: 0 auto; padding: var(--spacing-lg) var(--spacing-2xl); display: flex; justify-content: space-between; align-items: center">
        <span style="font-family: var(--font-display); font-size: var(--font-size-2xl); font-weight: var(--font-weight-bold); color: var(--color-primary)">AI Visibility Dashboard</span>
        <img src="../assets/logo.jpg" alt="Samsung" height="36">
    </div>
</header>
```

---

## Approved Implementation (Raw Values)

This is the exact implementation from `v3-ai-overview.html`:

```html
<header style="background:#f7f7f7;border-bottom:3px solid #1428A0;margin-bottom:24px;box-shadow:0 2px 4px rgba(0,0,0,0.05)">
    <div style="max-width:1400px;margin:0 auto;padding:16px 24px;display:flex;justify-content:space-between;align-items:center">
        <span style="font-family:'Samsung Sharp Sans',sans-serif;font-size:28px;font-weight:700;color:#1428A0">AI Visibility Dashboard</span>
        <img src="../assets/logo.jpg" alt="Samsung" height="36">
    </div>
</header>
```

---

## Notes

- Header uses inline styles (no external CSS classes needed)
- Content alignment matches the `.container` class used in the main body
- This component is complete and should not be modified without approval
