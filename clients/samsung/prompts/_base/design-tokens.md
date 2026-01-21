# Samsung Design Tokens

Single source of truth for all visual values in the Samsung AI Visibility Dashboard.

## Colors

### Brand Colors
| Token | Value | Usage |
|-------|-------|-------|
| `--color-primary` | `#1428A0` | Samsung Blue - headings, links, active states, primary buttons |
| `--color-primary-light` | `#8091df` | Light blue accent, tooltip icons |

### Accent Colors
| Token | Value | Usage |
|-------|-------|-------|
| `--color-accent-blue` | `#0277c6` | Secondary blue |
| `--color-accent-cyan` | `#02b2e4` | Cyan highlights |
| `--color-accent-teal` | `#01c3b0` | Teal highlights |
| `--color-accent-purple` | `#8091df` | Purple accent (same as primary-light) |
| `--color-accent-green` | `#96d551` | KPI increase state |
| `--color-accent-yellow` | `#feb447` | KPI no-change state |
| `--color-accent-red` | `#ff4438` | KPI decrease state |

### Semantic Colors
| Token | Value | Usage |
|-------|-------|-------|
| `--color-success` | `#4caf50` | Positive changes, "New" badges, positive sentiment |
| `--color-error` | `#f44336` | Negative changes, "Lost" badges, negative sentiment |
| `--color-neutral` | `#9e9e9e` | Neutral sentiment, disabled states |

### Background Colors
| Token | Value | Usage |
|-------|-------|-------|
| `--color-bg-page` | `#f8f9fa` | Page background |
| `--color-bg-header` | `#f7f7f7` | Header background |
| `--color-bg-card` | `#ffffff` | Card backgrounds |
| `--color-bg-success` | `#e8f5e9` | Success badge background |
| `--color-bg-error` | `#ffebee` | Error badge background |

### Text Colors
| Token | Value | Usage |
|-------|-------|-------|
| `--color-text-primary` | `#000000` | Primary text |
| `--color-text-secondary` | `#666666` | Secondary text, labels |
| `--color-text-link` | `#1428A0` | Links |

### Border Colors
| Token | Value | Usage |
|-------|-------|-------|
| `--color-border` | `#e0e0e0` | Default borders |
| `--color-border-accent` | `#1428A0` | Header accent border |

### Competitor Brand Colors
| Token | Value | Brand |
|-------|-------|-------|
| `--color-brand-samsung` | `#1428A0` | Samsung (primary blue) |
| `--color-brand-lg` | `#A50034` | LG (red) |
| `--color-brand-sony` | `#000000` | Sony (black) |
| `--color-brand-tcl` | `#E31937` | TCL (red) |
| `--color-brand-hisense` | `#00A0DF` | Hisense (cyan) |
| `--color-brand-xbox` | `#107C10` | Xbox (green) |
| `--color-brand-roku` | `#6C3C97` | Roku (purple) |

---

## Typography

### Font Families
| Token | Value | Usage |
|-------|-------|-------|
| `--font-display` | `'Samsung Sharp Sans', sans-serif` | Headings, metric values, bold display text |
| `--font-body` | `'Samsung One', -apple-system, sans-serif` | Body text, labels, buttons |

### Font Sizes
| Token | Value | Usage |
|-------|-------|-------|
| `--font-size-xs` | `11px` | Small labels, uppercase hints |
| `--font-size-sm` | `12px` | Badges, toggles, small buttons |
| `--font-size-base` | `14px` | Body text, table cells, filter buttons |
| `--font-size-md` | `16px` | Subtitles |
| `--font-size-lg` | `18px` | Section titles |
| `--font-size-xl` | `24px` | Page section headings (e.g., "Overview") |
| `--font-size-2xl` | `28px` | Header title ("AI Visibility Dashboard") |
| `--font-size-3xl` | `32px` | Large display text |
| `--font-size-metric` | `42px` | KPI card values |

### Font Weights
| Token | Value | Usage |
|-------|-------|-------|
| `--font-weight-normal` | `400` | Body text |
| `--font-weight-medium` | `500` | Labels, emphasized text |
| `--font-weight-bold` | `700` | Headings, metric values |

### Line Heights
| Token | Value | Usage |
|-------|-------|-------|
| `--line-height-tight` | `1.1` | Metric values |
| `--line-height-normal` | `1.5` | Body text |

---

## Spacing

| Token | Value | Usage |
|-------|-------|-------|
| `--spacing-xs` | `4px` | Tight gaps, inline spacing |
| `--spacing-sm` | `8px` | Small gaps between elements |
| `--spacing-md` | `12px` | Medium gaps |
| `--spacing-lg` | `16px` | Card gaps, section spacing |
| `--spacing-xl` | `20px` | Card padding |
| `--spacing-2xl` | `24px` | Container padding, major sections |

---

## Layout

| Token | Value | Usage |
|-------|-------|-------|
| `--max-width` | `1400px` | Container max-width |
| `--header-logo-height` | `36px` | Samsung logo height |

---

## Border Radius

| Token | Value | Usage |
|-------|-------|-------|
| `--radius-sm` | `4px` | Badges, small elements |
| `--radius-md` | `6px` | Toggle buttons |
| `--radius-lg` | `8px` | Filter buttons, inputs |
| `--radius-xl` | `12px` | Cards |

---

## Shadows

| Token | Value | Usage |
|-------|-------|-------|
| `--shadow-sm` | `0 2px 4px rgba(0,0,0,0.05)` | Header shadow |

---

## CSS Variables Declaration

When generating components, include this `:root` block at the start of the `<style>` section:

```css
:root {
    /* Brand */
    --color-primary: #1428A0;
    --color-primary-light: #8091df;

    /* Accent Palette */
    --color-accent-blue: #0277c6;
    --color-accent-cyan: #02b2e4;
    --color-accent-teal: #01c3b0;
    --color-accent-purple: #8091df;
    --color-accent-green: #96d551;
    --color-accent-yellow: #feb447;
    --color-accent-red: #ff4438;

    /* Semantic */
    --color-success: #4caf50;
    --color-error: #f44336;
    --color-neutral: #9e9e9e;

    /* Backgrounds */
    --color-bg-page: #f8f9fa;
    --color-bg-header: #f7f7f7;
    --color-bg-card: #ffffff;
    --color-bg-success: #e8f5e9;
    --color-bg-error: #ffebee;

    /* Text */
    --color-text-primary: #000000;
    --color-text-secondary: #666666;
    --color-text-link: #1428A0;

    /* Borders */
    --color-border: #e0e0e0;
    --color-border-accent: #1428A0;

    /* Competitor brands */
    --color-brand-samsung: #1428A0;
    --color-brand-lg: #A50034;
    --color-brand-sony: #000000;
    --color-brand-tcl: #E31937;
    --color-brand-hisense: #00A0DF;
    --color-brand-xbox: #107C10;
    --color-brand-roku: #6C3C97;

    /* Typography */
    --font-display: 'Samsung Sharp Sans', sans-serif;
    --font-body: 'Samsung One', -apple-system, sans-serif;

    /* Spacing */
    --spacing-xs: 4px;
    --spacing-sm: 8px;
    --spacing-md: 12px;
    --spacing-lg: 16px;
    --spacing-xl: 20px;
    --spacing-2xl: 24px;

    /* Layout */
    --max-width: 1400px;

    /* Radius */
    --radius-sm: 4px;
    --radius-md: 6px;
    --radius-lg: 8px;
    --radius-xl: 12px;

    /* Shadows */
    --shadow-sm: 0 2px 4px rgba(0,0,0,0.05);
}
```
