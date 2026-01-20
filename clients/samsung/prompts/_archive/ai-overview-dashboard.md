# Samsung AI Visibility Dashboard

Create a complete single HTML file replicating a SEMrush AI Overview dashboard. Use D3.js v7 for all charts. Include embedded CSS and JS. Output ONLY the HTML code, no explanations.

## Page Header
- Background: #f7f7f7
- Border-bottom: 3px solid #1428A0
- Left side: "AI Visibility Dashboard" text - 28px, font-weight 700, color #1428A0, Samsung Sharp Sans font
- Right side: Samsung logo `<img src="../assets/logo.jpg" height="36">`
- Header content must align with main content below (same max-width: 1400px and padding: 24px)

## Page Layout

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ AI Visibility Dashboard                                      [SAMSUNG LOGO] │
├─────────────────────────────────────────────────────────────────────────────┤
│ Overview                                                                     │
│ [Last 7 days] [Samsung] [Chat GPT ✕] [Tags ▾] [Select Segment ▾]           │
├─────────────────────────────────────────────────────────────────────────────┤
│ ┌──────────┐ ┌──────────┐ ┌─────────────────┐ ┌─────────────────┐          │
│ │Share of  │ │Brand     │ │Prompts          │ │Mentions by      │          │
│ │Voice     │ │Visibility│ │240 +182         │ │sentiment        │          │
│ │57% ↓-1%  │ │63% ↓-12% │ │143 -123         │ │[DONUT: 3K]      │          │
│ └──────────┘ └──────────┘ └─────────────────┘ └─────────────────┘          │
├─────────────────────────────────────────────────────────────────────────────┤
│ Historical Trend                                    [Day] [Week] [Month]    │
│ [Share of Voice] [Brand Visibility] [Mentions] [Avg. Position]              │
│ ┌─────────────────────────────────────────────────────────┬───────────────┐ │
│ │                    LINE CHART                           │ Brand         │ │
│ │  60% ─────────────────────────────────────────────      │ ☑ Samsung     │ │
│ │  50% ═══════════════════════════════════════════════    │ ☑ LG          │ │
│ │  40%                                                    │ ☑ Sony        │ │
│ │  30%                                                    │ ☑ TCL         │ │
│ │  20% ───────────────────────────────────────────────    │ ☑ Hisense     │ │
│ │  10%                                                    │ ☑ Xbox        │ │
│ │   0%                                                    │ ☑ Roku        │ │
│ │      Jan14  Jan15  Jan16  Jan17  Jan18  Jan19  Jan20    │ + Add Brand   │ │
│ └─────────────────────────────────────────────────────────┴───────────────┘ │
├─────────────────────────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────┐  ┌────────────────────────────────────────┐ │
│ │ Brand Leaderboard      3/9  │  │ Sentiment Over Time                    │ │
│ │ SoV Rank │ Brand │ Share   │  │ ┌────────────────────────────────────┐ │ │
│ │    1     │Samsung│ 57% ████│  │ │     STACKED BAR CHART              │ │ │
│ │    2     │ LG    │ 26% ██  │  │ │  3.5K ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓        │ │ │
│ │    3     │ Sony  │ 21% ██  │  │ │     ░░░░░░░░░░░░░░░░░░░░░░░░       │ │ │
│ │    4     │ TCL   │ 19% █   │  │ │     ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒       │ │ │
│ │    5     │Hisense│ 17% █   │  │ │   0 ├──┬──┬──┬──┬──┬──┬──┤        │ │ │
│ │    6     │ Xbox  │  3%     │  │ │     14 15 16 17 18 19 20           │ │ │
│ │    7     │ Roku  │  3%     │  │ │  ■ negative ■ neutral ■ positive   │ │ │
│ └─────────────────────────────┘  └────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────────────────┤
│ Brand / Product Performance (All Products)                    [Advanced ▾]  │
│ ┌───────────────────────────────────────────────────────────────────────┐   │
│ │ Prompt                        │Model│Product    │Jan 14│Jan 20│Change│   │
│ │ best tv for casual gaming     │ ⚙  │ S95F      │  —   │  1   │ New  │   │
│ │ 85 inch tv reviews            │ ⚙  │ QN90D     │  —   │  3   │ New  │   │
│ │ Samsung The Frame Pro reviews │ ⚙  │ Frame/Pro │  —   │  1   │ New  │   │
│ │ what tv should I buy?         │ ⚙  │ S95H QD   │  —   │  3   │ New  │   │
│ │ Is AI upscaling TV worth it?  │ ⚙  │ Q8F Vision│  6   │  —   │ Lost │   │
│ └───────────────────────────────────────────────────────────────────────┘   │
│                                                          1-10 of 529  < >   │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Header
- Title: "Overview" - 24px, font-weight 600, color #000
- Filter row with pill-shaped buttons (white bg, 1px #e0e0e0 border, 8px radius, 8px 16px padding)
- Active filters have brand-colored left border or background tint
- "✕" close button on removable filters

## KPI Cards Row (4 cards in CSS grid)
- Use CSS grid: `grid-template-columns: repeat(4, 1fr)` for equal-width columns
Each card:
- White background, 1px #e0e0e0 border, 12px border-radius
- Padding: 20px
- Label: 12px uppercase, color #666
- Value: 48px font-weight 700
- Change indicator: small text with arrow, green (#4caf50) for positive, red (#f44336) for negative

### Card 1: Share of Voice
- Value: 57%
- Change: ↓ -1% (red)

### Card 2: Brand Visibility
- Value: 63%
- Change: ↓ -12% (red)

### Card 3: Prompts
- Two rows:
  - "Responses with brand mention" → 240 with +182 (green badge)
  - "Responses without brand mention" → 143 with -123 (red badge)

### Card 4: Mentions by Sentiment
- D3.js donut chart, 80px diameter
- Center text: "3K"
- Three segments: Positive (green #4caf50), Neutral (gray #9e9e9e), Negative (red #f44336)
- Small legend on right

## Historical Trend Section
- Section title: "Historical Trend" with sort icon
- Right side: Day/Week/Month toggle buttons
- Tab row: "Share of Voice" (active), "Brand Visibility", "Mentions", "Avg. Position"

### Line Chart (D3.js)
- X-axis: Jan 14 - Jan 20
- Y-axis: 0% to 60%
- 7 lines for brands with distinct colors:
  - Samsung: #1428A0 (primary blue) - top line ~57%
  - LG: #A50034 (red)
  - Sony: #000000 (black)
  - TCL: #E31937 (red)
  - Hisense: #00A0DF (cyan)
  - Xbox: #107C10 (green)
  - Roku: #6C3C97 (purple)
- Smooth curves (d3.curveMonotoneX)
- Grid lines: light gray dashed

### Brand Legend (right panel)
- Checkboxes with brand colors
- "+ Add Brand" dropdown at bottom

## Two Column Section

### Left: Brand Leaderboard
- Header: "Brand Leaderboard" with "Manage columns 3/9" button and export icon
- Table columns: SoV Rank, Brand (with logo icon), Share of Voice
- Share of Voice column has horizontal bar chart
- Bar colors match brand colors
- Data:
  1. Samsung - 57%
  2. LG - 26%
  3. Sony - 21%
  4. TCL - 19%
  5. Hisense - 17%
  6. Xbox - 3%
  7. Roku - 3%

### Right: Sentiment Over Time
- Header: "Sentiment Over Time" with export icon
- D3.js stacked bar chart
- X-axis: dates Jan 14-20
- Y-axis: 0 to 3.5K mentions
- Three stacked segments per bar:
  - negative (bottom): #f44336 red
  - neutral (middle): #9e9e9e gray
  - positive (top): #4caf50 green
- Legend at bottom: ■ negative ■ neutral ■ positive

## Brand/Product Performance Table
- Header: "Brand / Product Performance (All Products)" with sort icon
- "Advanced Filter" dropdown
- Columns:
  - Checkbox
  - Prompt (blue link text)
  - Model (gear icon ⚙)
  - Product
  - Position January 14, 2026
  - Position January 20, 2026
  - Position Change

- Position Change badges:
  - "New" = green background (#e8f5e9), green text (#4caf50)
  - "Lost" = red background (#ffebee), red text (#f44336)
  - "—" for no data

- Mock data (10 rows):
  1. "best tv for casual gaming" | S95F | — | 1 | New
  2. "85 inch tv reviews" | QN90D | — | 3 | New
  3. "Samsung The Frame Pro reviews" | The Frame / Pro | — | 1 | New
  4. "what tv should I buy?" | S95H QD-OLED | — | 3 | New
  5. "Is AI upscaling TV worth it?" | Q8F Vision AI TV | 6 | — | Lost
  6. "What are the main features of art TVs vs regular?" | Frame Pro Neo QLED | — | 2 | New
  7. "Which 4K TVs are best for gaming?" | S95F | — | 2 | New
  8. "tv with 120Hz refresh rate and HDMI 2.1" | S95F OLED TV | — | 1 | New
  9. "S84F reviews" | S84F OLED TV | — | 1 | New
  10. "tv for sports with great color accuracy" | S95C | — | 1 | New

- Pagination: "1-10 of 529" with < > arrows

## Styling

### Fonts
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
body { font-family: 'Samsung One', -apple-system, sans-serif; }
h1, h2, h3, .metric-value { font-family: 'Samsung Sharp Sans', sans-serif; }
```

### Colors
- Background: #f8f9fa
- Cards: #ffffff
- Primary: #1428A0
- Text primary: #000
- Text secondary: #666
- Borders: #e0e0e0
- Success: #4caf50
- Error: #f44336
- Accent colors for brands as listed above

### Layout
- Max-width: 1400px, centered
- Padding: 24px
- Card gaps: 16px
- Border-radius: 12px for cards, 8px for buttons
