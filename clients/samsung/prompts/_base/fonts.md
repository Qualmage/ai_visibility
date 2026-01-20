# Samsung Font Declarations

@font-face declarations for Samsung brand fonts. Include this block at the start of any `<style>` section.

## Font Files Location

Fonts are stored in `../assets/fonts/` relative to the dashboard HTML files.

| Font | File | Format |
|------|------|--------|
| Samsung Sharp Sans Bold | `SamsungSharpSansBd.woff2` | WOFF2 |
| Samsung Sharp Sans Bold | `SamsungSharpSans-Bold.ttf` | TrueType |
| Samsung One 400 | `SamsungOneLatinWeb-400.woff2` | WOFF2 |
| Samsung One 400 | `SamsungOneLatinCompact-400.ttf` | TrueType |

## CSS @font-face Block

```css
@font-face {
    font-family: 'Samsung Sharp Sans';
    src: url('../assets/fonts/SamsungSharpSansBd.woff2') format('woff2'),
         url('../assets/fonts/SamsungSharpSans-Bold.ttf') format('truetype');
    font-weight: 700;
}

@font-face {
    font-family: 'Samsung One';
    src: url('../assets/fonts/SamsungOneLatinWeb-400.woff2') format('woff2'),
         url('../assets/fonts/SamsungOneLatinCompact-400.ttf') format('truetype');
    font-weight: 400;
}
```

## Usage Rules

| Element Type | Font Family | Weight |
|--------------|-------------|--------|
| Headings (h1, h2, h3) | Samsung Sharp Sans | 700 |
| Metric values | Samsung Sharp Sans | 700 |
| Section titles | Samsung Sharp Sans | 700 |
| Body text | Samsung One | 400 |
| Buttons | Samsung One | 400 |
| Labels | Samsung One | 400/500 |
| Table cells | Samsung One | 400 |

## Body Default

```css
body {
    font-family: 'Samsung One', -apple-system, sans-serif;
}

h1, h2, h3, .metric-value, .section-title {
    font-family: 'Samsung Sharp Sans', sans-serif;
}
```
