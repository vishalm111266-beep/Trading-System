# Style Contract

Complete visual specifications for institutional research reports.

## Color System

### Primary Colors

| Name | Hex | Usage |
|------|-----|-------|
| Navy Blue | #003B5C | Cover banner only |
| Medium Blue | #4472C4 | Links, sidebar headings, emphasis, chart primary |
| Light Blue-Gray | #D6DCE4 | Table header backgrounds |
| Dark Charcoal | #333333 | Body text |
| Black | #000000 | Headings |
| White | #FFFFFF | Cover title text, table header text (avoid) |

### Chart Colors

| Order | Hex | Usage |
|-------|-----|-------|
| 1 | #4472C4 | Primary series |
| 2 | #5B9BD5 | Secondary series |
| 3 | #A5A5A5 | Tertiary series |
| 4 | #264478 | Quaternary series |
| 5 | #636363 | Quinary series |

### Background Colors

| Name | Hex | Usage |
|------|-----|-------|
| White | #FFFFFF | Page background, table rows (odd) |
| Light Gray | #F2F2F2 | Table rows (even), sidebar background |
| Light Gray 2 | #D9D9D9 | Chart title bar background |

## Typography

### Font Stack

**Primary (Latin-only):**
```
font-family: "Univers LT Std", "Helvetica Neue", Arial, sans-serif;
```

**Primary (CJK/Latin):**
```
font-family: "Noto Sans CJK SC", "Source Han Sans SC", "PingFang SC", sans-serif;
```

**Chart Labels:**
```
font-family: Arial, sans-serif;
```

### Type Scale

| Element | Size (pt) | Weight | Color | Notes |
|---------|-----------|--------|-------|-------|
| Cover Title | 30-32 | Bold | #FFFFFF | On navy background |
| Cover Subtitle | 18 | Regular | #333333 | Below banner |
| H1 | 16-18 | Bold | #000000 | Underlined |
| H2 | 12-13 | Bold | #000000 | |
| H3 | 11 | Bold | #000000 | |
| Body | 10 | Regular | #333333 | |
| Caption | 8 | Italic | #666666 | Below exhibits |
| Header | 8 | Regular | #666666 | |
| Footer | 8 | Regular | #666666 | |
| Page Number | 8 | Regular | #666666 | |
| Disclosure | 9 | Regular | #333333 | |
| Glossary Term | 10 | Bold | #000000 | |
| Glossary Definition | 10 | Regular | #333333 | |

## Page Specifications

### Dimensions

| Attribute | Value |
|-----------|-------|
| Page Size | US Letter (8.5 × 11 in) |
| Orientation | Portrait |

### Margins

| Side | Value |
|------|-------|
| Top | 1.0 in |
| Bottom | 0.8 in |
| Left | 1.0 in |
| Right | 1.0 in |

### Columns

| Context | Columns |
|---------|---------|
| Cover Page | Two (60% / 40%) |
| Body Pages | Single |

## Cover Page Layout

### Banner
- Full-width navy blue (#003B5C) bar
- Height: approximately 1.5 inches
- Title: White, 30-32pt, bold, left-aligned
- Date: White, 10pt, left side below title
- Firm Name: White, 10pt, right side

### Content Area
- **Left Column (60%):**
  - Summary sections with blue (#4472C4) headings
  - Key metrics table
  - Investment thesis bullet points
  - Target price and rating

- **Right Column (40%):**
  - Light gray (#F2F2F2) sidebar background
  - Analyst information (name, phone, email)
  - "N Things to Know" numbered list
  - Key financials quick view

### Disclaimer
- 8pt text at bottom
- Full regulatory disclaimer text

## Table Specifications

### Header Row
- Background: #D6DCE4 (light blue-gray)
- Text: #000000 (black), bold
- **NOT** dark navy with white text

### Data Rows
- Alternating: #FFFFFF (white) and #F2F2F2 (light gray)
- Thin gray (#CCCCCC) borders
- Cell padding: 4-6pt

### Number Alignment
- Numbers: Right-aligned
- Text: Left-aligned
- Headers: Center-aligned

### Exhibit Label
- Format: "Exhibit N: [Title]"
- Position: Above table, left-aligned
- Style: 10pt, bold, dark charcoal

### Source Line
- Position: Below table, left-aligned
- Style: 8pt, italic, gray
- Format: "Source: [Source Name], [Date]"

## Chart Specifications

### Container
- Border: 1px solid #CCCCCC
- Title bar background: #D9D9D9
- Title bar text: 10pt, bold, #333333

### Axes
- Line color: #666666
- Label text: 8-9pt, Arial, #333333
- Grid lines: #E0E0E0 (light gray)

### Data Series Colors
- Use chart color palette in order
- Bar charts: Navy/Blue palette
- Line charts: Navy + Gray combination

### Exhibit Label
- Format: "Exhibit N: [Title]"
- Position: Above chart, left-aligned
- Style: 10pt, bold, dark charcoal

### Source Line
- Position: Below chart, left-aligned
- Style: 8pt, italic, gray

## Header/Footer Specifications

### Header
- Left: Date (e.g., "July 15, 2026")
- Right: Region/Sector tag (e.g., "Asia Pacific | Technology")
- Style: 8pt, regular, gray
- Separator: Thin gray line below

### Footer
- Left: Firm name + division (e.g., "Global Investment Research")
- Right: Page number
- Style: 8pt, regular, gray
- Separator: Thin gray line above

## Hyperlink Style

- Color: #4472C4 (medium blue)
- Decoration: Underlined
- Hover: #2E5A8C (darker blue)

## Bullet Points

- Style: Filled circles (●)
- Lead-in: Bold text followed by regular text
- Indent: 0.25 inches
- Spacing: 6pt between items

## Mathematical Formulas

- Label: Left-aligned, regular weight
- Equation: Right-aligned or centered
- Style: 10pt, italic for variables
- Spacing: 12pt above and below

## Callout Rules

**DO NOT USE:**
- Colored callout boxes
- "Key Finding" boxes
- "Warning" boxes
- Shaded highlight boxes
- Bordered information boxes

**USE:**
- Bold text for emphasis
- Table formatting for structured data
- Exhibit numbering for references
