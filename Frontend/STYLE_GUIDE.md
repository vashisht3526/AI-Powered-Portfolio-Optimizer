# Visual Style Guide
## AI-Powered Dynamic Portfolio Optimizer

---

## Color Palette

### Neutral Colors (Primary UI)
| Color Name | Hex Code | Usage |
|------------|----------|-------|
| Slate 50 | `#F8FAFC` | Page background |
| Slate 100 | `#F1F5F9` | Secondary background |
| Slate 200 | `#E2E8F0` | Borders, dividers |
| Slate 500 | `#64748B` | Secondary text |
| Slate 600 | `#475569` | Tertiary text |
| Slate 700 | `#334155` | Label text |
| Slate 900 | `#0F172A` | Primary text |
| White | `#FFFFFF` | Cards, surfaces |

### Semantic Colors
| Color Name | Hex Code | Usage |
|------------|----------|-------|
| Blue 600 | `#2563EB` | Primary actions, links, charts |
| Blue 700 | `#1D4ED8` | Hover states |
| Emerald 600 | `#10B981` | Positive metrics, growth |
| Rose 600 | `#F43F5E` | Negative metrics, risk |
| Amber 500 | `#F59E0B` | Warnings |

### Sentiment Badge Colors
| Sentiment | Background | Text | Border |
|-----------|------------|------|--------|
| Positive | `#D1FAE5` (Emerald 100) | `#047857` (Emerald 700) | `#A7F3D0` (Emerald 200) |
| Neutral | `#F1F5F9` (Slate 100) | `#334155` (Slate 700) | `#E2E8F0` (Slate 200) |
| Negative | `#FFE4E6` (Rose 100) | `#BE123C` (Rose 700) | `#FECDD3` (Rose 200) |

---

## Typography

### Font Families
```css
/* System Font Stack */
font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;

/* Monospace (for tickers, code) */
font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, "Liberation Mono", monospace;
```

### Type Scale
| Element | Size | Weight | Line Height | Usage |
|---------|------|--------|-------------|-------|
| Display | 24px | 500 (Medium) | 1.5 | Page titles (h1) |
| Heading | 20px | 500 (Medium) | 1.5 | Section titles (h2) |
| Subheading | 18px | 500 (Medium) | 1.5 | Card titles (h3) |
| Body | 16px | 400 (Normal) | 1.5 | Paragraph text |
| Small | 14px | 400 (Normal) | 1.5 | Helper text |
| Caption | 12px | 400 (Normal) | 1.5 | Labels, timestamps |

### Font Weight Usage
- **400 (Normal)**: Body text, descriptions
- **500 (Medium)**: Headings, labels, buttons
- **600 (Semibold)**: Emphasized values, important metrics

---

## Spacing System

Based on 4px base unit (0.25rem):

| Token | Value | Usage |
|-------|-------|-------|
| `xs` | 0.5rem (2px) | Tight spacing |
| `sm` | 0.75rem (3px) | Icon gaps |
| `base` | 1rem (4px) | Default gap |
| `md` | 1.5rem (6px) | Card padding |
| `lg` | 2rem (8px) | Section spacing |
| `xl` | 3rem (12px) | Major sections |
| `2xl` | 4rem (16px) | Page margins |

### Component-Specific Spacing
- **Card Padding**: 1.5rem (6)
- **Button Padding**: 0.75rem horizontal, 0.5rem vertical
- **Grid Gap**: 1.5rem (6)
- **Section Margin**: 3rem (12)

---

## Border Radius

| Element | Radius | Value |
|---------|--------|-------|
| Cards | `rounded-lg` | 0.625rem (10px) |
| Buttons | `rounded-lg` | 0.5rem (8px) |
| Badges | `rounded-md` | 0.375rem (6px) |
| Inputs | `rounded-md` | 0.375rem (6px) |
| Progress Bars | `rounded-full` | 9999px |

---

## Shadows

### Card Elevation
```css
/* Default Card */
box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);

/* Hover State */
box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);

/* Modal/Dialog */
box-shadow: 0 20px 25px rgba(0, 0, 0, 0.15);
```

---

## Component Specifications

### 1. Metric Card
```
Dimensions:
- Width: Responsive (grid column)
- Height: Auto
- Padding: 1.5rem (6)
- Border: 1px solid #E2E8F0

Layout:
- Header: Icon + Title (flex row)
- Body: Large value + subtitle

Colors:
- Background: White
- Border: Slate 200
- Title: Slate 600
- Value: Semantic (emerald/rose/slate)
- Icon: Matches value color
```

### 2. Data Table
```
Header:
- Background: Transparent
- Text: Slate 700, font-weight: 600
- Border-bottom: 1px solid Slate 200

Rows:
- Background: White
- Hover: Slate 50
- Border-bottom: 1px solid Slate 100
- Padding: 1rem vertical

Cells:
- Text: Slate 900 (data), Slate 700 (labels)
- Alignment: Left (text), Right (numbers)
```

### 3. Button Styles

**Primary Button**
```css
background: #2563EB (Blue 600)
color: white
padding: 0.75rem 1.5rem
border-radius: 0.5rem
font-weight: 500

hover {
  background: #1D4ED8 (Blue 700)
}

disabled {
  opacity: 0.5
  cursor: not-allowed
}
```

**Outline Button**
```css
background: transparent
color: #334155 (Slate 700)
border: 1px solid #E2E8F0 (Slate 200)
padding: 0.75rem 1.5rem
border-radius: 0.5rem

hover {
  background: #F8FAFC (Slate 50)
}
```

### 4. Badge
```
Small Badge:
- padding: 0.25rem 0.5rem
- font-size: 12px
- border-radius: 0.375rem
- font-weight: 500
- border: 1px solid (matching color)

With Icon:
- icon size: 12px (h-3 w-3)
- gap: 0.25rem
```

### 5. Input Fields
```
Dimensions:
- Height: 2.5rem (40px)
- Padding: 0.5rem 0.75rem
- Border: 1px solid #E2E8F0
- Border-radius: 0.375rem

States:
- Default: Slate 200 border
- Focus: Blue 600 ring
- Error: Rose 600 border
- Disabled: Slate 100 background, opacity 0.6
```

### 6. Slider
```
Track:
- Height: 0.5rem (8px)
- Background: #E2E8F0 (Slate 200)
- Border-radius: 9999px

Filled Track:
- Background: #2563EB (Blue 600)

Thumb:
- Size: 1.25rem (20px)
- Background: White
- Border: 2px solid Blue 600
- Box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2)
```

---

## Chart Styling (Recharts)

### Area Chart (Equity Curve)
```javascript
Grid:
- strokeDasharray: "3 3"
- stroke: #E2E8F0 (Slate 200)

Axes:
- stroke: #64748B (Slate 500)
- fontSize: 12px
- tickMargin: 8px

Line/Area:
- stroke: #2563EB (Blue 600)
- strokeWidth: 2px
- fill: linear-gradient (Blue 600 at 20% opacity to 0%)

Tooltip:
- background: white
- border: 1px solid #E2E8F0
- borderRadius: 8px
- fontSize: 13px
- padding: 8px 12px
```

---

## Icons

### Icon System: Lucide React
- **Size**: 16px (h-4 w-4) for inline, 20px (h-5 w-5) for standalone
- **Stroke Width**: 2 (default)
- **Color**: Inherits from parent or semantic color

### Common Icons
| Icon | Usage |
|------|-------|
| `TrendingUp` | Positive metrics, growth |
| `TrendingDown` | Negative metrics, decline |
| `Activity` | Volatility, activity |
| `Target` | Goals, ratios |
| `Bot` | AI assistant |
| `Newspaper` | News section |
| `Settings2` | Controls, configuration |
| `RefreshCw` | Recalculate, update |
| `Calendar` | Date selection |

---

## Layout Grid

### Desktop (>1024px)
```
Container:
- max-width: 1600px
- padding: 1.5rem (6) horizontal
- margin: 0 auto

Grid:
- Columns: 4
- Gap: 1.5rem (6)
- Sidebar: span 1 column
- Main: span 3 columns
```

### Tablet (768px - 1023px)
```
Grid:
- Columns: 1 (stacked)
- Sidebar: full width
- Main: full width
```

### Mobile (<768px)
```
All components:
- Full width
- Vertical stacking
- Increased touch targets (min 44px)
```

---

## Animation & Transitions

### Standard Transitions
```css
/* Default */
transition: all 150ms ease-in-out;

/* Hover Effects */
transition: background-color 200ms ease, border-color 200ms ease;

/* Modal/Dialog Entry */
animation: fadeIn 200ms ease-out;
```

### Loading States
```
Spinner:
- animation: spin 1s linear infinite
- color: Blue 600

Progress Bar:
- transition: width 300ms ease-out
```

---

## Accessibility

### Minimum Contrast Ratios (WCAG AA)
- Normal text (16px): 4.5:1
- Large text (24px): 3:1
- UI components: 3:1

### Focus Indicators
```css
focus-visible {
  outline: 2px solid #2563EB (Blue 600)
  outline-offset: 2px
}
```

### Keyboard Navigation
- Tab order follows visual hierarchy
- All interactive elements are focusable
- Skip links for screen readers

---

## Recommended Usage Patterns

### ✅ DO
- Use semantic colors (green for positive, red for negative)
- Maintain consistent spacing throughout
- Keep cards white on slate background
- Use monospace font for financial tickers
- Include explanatory text below metrics
- Show units for all numerical values
- Add subtle hover effects
- Use icons to reinforce meaning

### ❌ DON'T
- Mix different border radii on same page
- Use colors randomly without meaning
- Overcrowd cards with too much info
- Use aggressive animations
- Hide important information in tooltips
- Use jargon without explanation
- Make buttons look like links
- Reduce contrast for aesthetic reasons

---

## Responsive Behavior

### Breakpoints
| Breakpoint | Width | Layout Change |
|------------|-------|---------------|
| Mobile | < 640px | Single column, stacked |
| Tablet | 640px - 1023px | 2 columns for cards |
| Desktop | 1024px+ | Sidebar + 3-column main |
| Wide | 1600px+ | Max width container |

### Component Adaptations

**Metric Cards:**
- Mobile: 1 column
- Tablet: 2 columns
- Desktop: 4 columns

**Portfolio Table:**
- Mobile: Scrollable horizontally
- Desktop: Full width

**News Section:**
- Mobile: 1 column
- Desktop: 2 columns

---

## Print Styles (Future Enhancement)

```css
@media print {
  /* Hide controls, navigation */
  /* Expand all charts */
  /* Use print-friendly colors */
  /* Add page breaks between sections */
}
```

---

## Performance Considerations

1. **Images**: Use Unsplash for stock photos (when needed)
2. **Charts**: Lazy load if data is large
3. **Fonts**: System fonts (no web font loading)
4. **Icons**: SVG from Lucide (tree-shakeable)
5. **CSS**: Tailwind with PurgeCSS (production)

---

## Component Checklist

When creating new components, ensure:
- [ ] Uses correct color tokens
- [ ] Follows spacing system
- [ ] Has proper TypeScript types
- [ ] Includes accessible labels
- [ ] Handles loading/error states
- [ ] Is keyboard navigable
- [ ] Has responsive behavior
- [ ] Uses semantic HTML
- [ ] Includes explanatory text
- [ ] Matches visual style guide

---

## Design Resources

### Inspiration Sources
- Bloomberg Terminal (professional finance UI)
- Modern SaaS dashboards (clean, minimal)
- Academic journals (clarity, hierarchy)
- Research papers (data visualization)

### Similar Projects
- Portfolio Visualizer
- Morningstar Portfolio Manager
- Yahoo Finance Portfolio

### Tools Used
- Figma (conceptual design)
- Tailwind CSS (styling)
- Recharts (data visualization)
- Radix UI (accessible components)

---

**Last Updated**: February 1, 2026  
**Version**: 1.0  
**Status**: Final Deliverable
