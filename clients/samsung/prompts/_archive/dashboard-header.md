# Samsung SEMrush Dashboard

Create a complete single HTML file for a Samsung SEMrush analytics dashboard. Use D3.js v7 for charts. Include embedded CSS and JS. Output ONLY the HTML code, no explanations.

## Header Layout

### Structure
```
┌─────────────────────────────────────────────────────────────────────┐
│  [SAMSUNG LOGO]                              [Date Range Controls]  │
│   logo.jpg                                   Start: [____] End:[__] │
│                                                                     │
│  SEMrush Performance Dashboard                         [Refresh ↻]  │
│  AI Overview & SEO Analytics                                        │
└─────────────────────────────────────────────────────────────────────┘
```

### Logo Specifications
- Use `/assets/logo.jpg` as an `<img>` element (not text)
- Height: 40px, width auto (maintain aspect ratio)
- Position: Top-left corner
- No letter-spacing effects - use the actual image file

### Title Section
- Main title: "SEMrush Performance Dashboard"
- Font: Samsung Sharp Sans Bold (fallback: system sans-serif)
- Size: 32px
- Color: #1428A0 (Samsung Blue)
- Subtitle: "AI Overview & SEO Analytics"
- Subtitle size: 16px, color: #666

### Date Controls (Top Right)
- Two date input fields: Start Date, End Date
- Labels above inputs, uppercase, 11px, color #666
- Input styling: white background, 1px #e0e0e0 border, 8px border-radius
- Refresh button: Samsung Blue (#1428A0), white text, rounded

### Styling Details
- Background: #f5f5f5 (light gray)
- Header container: white background, subtle shadow
- Padding: 24px
- Border-bottom: 3px solid #1428A0

## Fonts
```css
@font-face {
    font-family: 'Samsung Sharp Sans';
    src: url('/assets/fonts/SamsungSharpSansBd.woff2') format('woff2');
    font-weight: 700;
}
@font-face {
    font-family: 'Samsung One';
    src: url('/assets/fonts/SamsungOneLatinWeb-400.woff2') format('woff2');
    font-weight: 400;
}
```

## Color Palette
- Primary: #1428A0 (Samsung Blue)
- Accents: #0277c6, #02b2e4, #01c3b0, #8091df, #96d551, #feb447, #ff4438
- Background: #f5f5f5
- Cards: #ffffff
- Text primary: #000
- Text secondary: #666
- Borders: #e0e0e0

## Technical Requirements
- Single HTML file with embedded CSS and JS
- Use D3.js v7 from CDN
- Responsive design
- Clean, corporate aesthetic
- No external dependencies except D3.js CDN and local fonts/logo

## Mock Data for Cards
Include 6 metric cards with fake data:
1. Source Visibility - Score: 78.5%
2. AI Visibility Table - 5 rows of keyword data
3. Prompt Rankings - 142 tracked prompts
4. Referral Traffic - 1,847 visits
5. Share of Voice Table - 5 competitors with percentages
6. Share of Voice Chart - D3.js line chart showing 6 months trend
