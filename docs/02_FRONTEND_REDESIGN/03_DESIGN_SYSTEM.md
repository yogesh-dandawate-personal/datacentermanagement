# Design System: iNetZero UI Standards
**Agent**: Design System Agent
**Date**: March 9, 2026
**Status**: ✅ COMPLETE
**Purpose**: Standardize all UI elements, colors, spacing, typography

---

## COLOR TOKENS

### Add to `tailwind.config.ts`

```typescript
extend: {
  colors: {
    // Primary (Blue - Main brand color)
    primary: {
      100: '#dbeafe',
      200: '#bfdbfe',
      300: '#93c5fd',
      400: '#60a5fa',
      500: '#3b82f6',
      600: '#2563eb',
      700: '#1d4ed8',
      800: '#1e40af',
      900: '#1e3a8a',
    },
    // Secondary (Cyan - Accent)
    secondary: {
      100: '#cffafe',
      200: '#a5f3fc',
      300: '#67e8f9',
      400: '#22d3ee',
      500: '#06b6d4',
      600: '#0891b2',
      700: '#0e7490',
      800: '#155e75',
      900: '#164e63',
    },
    // Success (Green)
    success: {
      100: '#dcfce7',
      200: '#bbf7d0',
      300: '#86efac',
      400: '#4ade80',
      500: '#22c55e',
      600: '#16a34a',
      700: '#15803d',
      800: '#166534',
      900: '#145231',
    },
    // Warning (Amber/Yellow)
    warning: {
      100: '#fef3c7',
      200: '#fde68a',
      300: '#fcd34d',
      400: '#facc15',
      500: '#eab308',
      600: '#ca8a04',
      700: '#a16207',
      800: '#854d0e',
      900: '#713f12',
    },
    // Danger (Red)
    danger: {
      100: '#fee2e2',
      200: '#fecaca',
      300: '#fca5a5',
      400: '#f87171',
      500: '#ef4444',
      600: '#dc2626',
      700: '#b91c1c',
      800: '#991b1b',
      900: '#7f1d1d',
    },
    // Neutral (Slate - grays)
    slate: {
      // (Use Tailwind defaults)
    },
  },
}
```

### Color Usage

| Element | Color | Shade |
|---------|-------|-------|
| Primary buttons | primary | 600 |
| Primary text | primary | 400 |
| Sidebar active state | primary | 500/20 with 50% opacity |
| Secondary buttons | secondary | 600 |
| Success alerts | success | 600 |
| Warning alerts | warning | 600 |
| Error alerts | danger | 600 |
| Text on dark | slate | 300 (for body) |
| Borders | slate | 700/30 (with opacity) |
| Backgrounds (dark) | slate | 900/950 |

---

## TYPOGRAPHY SCALE

### Font Families
```
Font Stack: Inter, system-ui, sans-serif
```

### Heading Hierarchy

| Level | Size | Weight | Line-Height | Usage |
|-------|------|--------|-------------|-------|
| h1 | 2.5rem (40px) | 700 | 1.2 | Page titles |
| h2 | 2rem (32px) | 700 | 1.3 | Section titles |
| h3 | 1.5rem (24px) | 600 | 1.4 | Subsections |
| h4 | 1.25rem (20px) | 600 | 1.4 | Card titles |
| h5 | 1rem (16px) | 600 | 1.5 | Labels |
| h6 | 0.875rem (14px) | 600 | 1.5 | Small labels |

### Body Text

| Level | Size | Weight | Line-Height | Usage |
|-------|------|--------|-------------|-------|
| body-lg | 1rem (16px) | 400 | 1.6 | Main body text |
| body | 0.9375rem (15px) | 400 | 1.6 | Standard body |
| body-sm | 0.875rem (14px) | 400 | 1.5 | Secondary text |
| body-xs | 0.75rem (12px) | 400 | 1.4 | Captions |

### Tailwind Configuration

```typescript
extend: {
  fontSize: {
    'h1': ['2.5rem', { lineHeight: '1.2', fontWeight: '700' }],
    'h2': ['2rem', { lineHeight: '1.3', fontWeight: '700' }],
    'h3': ['1.5rem', { lineHeight: '1.4', fontWeight: '600' }],
    'h4': ['1.25rem', { lineHeight: '1.4', fontWeight: '600' }],
    'h5': ['1rem', { lineHeight: '1.5', fontWeight: '600' }],
    'h6': ['0.875rem', { lineHeight: '1.5', fontWeight: '600' }],
    'body-lg': ['1rem', { lineHeight: '1.6', fontWeight: '400' }],
    'body': ['0.9375rem', { lineHeight: '1.6', fontWeight: '400' }],
    'body-sm': ['0.875rem', { lineHeight: '1.5', fontWeight: '400' }],
    'body-xs': ['0.75rem', { lineHeight: '1.4', fontWeight: '400' }],
  },
}
```

---

## SPACING SCALE

**Base Unit**: 4px (Tailwind default)

| Scale | Pixels | Tailwind | Usage |
|-------|--------|----------|-------|
| xs | 4px | gap-1 | Tight spacing |
| sm | 8px | gap-2 | Small spacing |
| md | 12px | gap-3 | Medium spacing |
| lg | 16px | gap-4 | Standard spacing |
| xl | 24px | gap-6 | Loose spacing |
| 2xl | 32px | gap-8 | Very loose spacing |
| 3xl | 48px | gap-12 | Huge spacing |

### Layout Margins/Padding

- Page containers: `px-4 sm:px-6 lg:px-8`
- Section padding: `py-12 md:py-16 lg:py-20`
- Component padding: `p-4` (small), `p-6` (medium), `p-8` (large)
- Gaps between sections: `space-y-6` or `space-y-8`

---

## SHADOWS

```typescript
extend: {
  boxShadow: {
    'xs': '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
    'sm': '0 1px 3px 0 rgba(0, 0, 0, 0.1)',
    'base': '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
    'md': '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
    'lg': '0 20px 25px -5px rgba(0, 0, 0, 0.1)',
    'xl': '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
  }
}
```

**Usage**:
- Cards: `shadow-sm`
- Modals/Dropdowns: `shadow-lg`
- Elevated sections: `shadow-md`

---

## BORDER RADIUS

| Name | Size | Usage |
|------|------|-------|
| rounded-sm | 2px | Subtle corners |
| rounded | 4px | Default (inputs) |
| rounded-md | 6px | Cards, buttons |
| rounded-lg | 8px | Larger cards, modals |
| rounded-xl | 12px | Hero sections |
| rounded-full | 9999px | Pills, avatars |

---

## TRANSITIONS

```typescript
transitionDuration: {
  'fast': '150ms',
  'default': '200ms',
  'slow': '300ms',
}
```

**Usage**:
- Hover states: `transition duration-fast`
- Sidebar toggle: `transition duration-300`
- Modal/Dropdown: `transition duration-200`

---

## COMPONENT SPECS

### Button

**Variants**: primary, secondary, outline, ghost, danger
**Sizes**: sm (px-3 py-1.5), md (px-4 py-2), lg (px-6 py-3)
**States**: default, hover, focus, active, disabled, loading
**Min height**: 44px (accessibility)

### Card

**Variants**: default, elevated, glass
**Padding**: p-4, p-6, p-8
**Borders**: `border border-slate-700/30`
**Shadows**: `shadow-sm`

### Input / Textarea / Select

**States**: default, focus, disabled, error
**Styling**: `border border-slate-700 rounded bg-slate-900/50`
**Focus**: `focus:border-primary-500 focus:outline-none`
**Disabled**: `disabled:opacity-50 disabled:cursor-not-allowed`

### Badge

**Variants**: primary, secondary, success, warning, danger
**Sizes**: sm, md, lg

### Table

**Row hover**: `hover:bg-slate-800/30`
**Striped**: Alternate row background
**Header**: `bg-slate-900` bold text
**Borders**: Subtle row dividers

### Modal / Dialog

**Overlay**: `bg-black/50 backdrop-blur-sm`
**Content**: `bg-slate-900 rounded-lg shadow-xl`
**Close button**: Top-right corner

### Loading States

**Skeleton**: Gray shimmer effect
**Spinner**: Rotating icon
**Progress**: Bar or circular
**Toast**: Bottom-right position

### Empty States

**Icon**: Large icon (Lucide)
**Title**: "No data available"
**Description**: Contextual message
**Action**: Button to create/import

---

## RESPONSIVE BREAKPOINTS

| Breakpoint | Width | Use Case |
|-----------|-------|----------|
| sm | 640px | Tablets in portrait |
| md | 768px | Tablets in landscape |
| lg | 1024px | Small desktops |
| xl | 1280px | Standard desktops |
| 2xl | 1536px | Large desktops |

### Layout Patterns

```
Mobile-first:
- Single column
- Full-width cards
- Stacked nav

Tablet (md):
- 2-column grids
- Sidebar collapses
- Half-width modals

Desktop (lg+):
- 3-4 column grids
- Sidebar visible
- Full-width modals
```

---

## COMPONENT COMPOSITION

### AppShell
- Sidebar
- Header
- Main content area
- Footer

### SidebarNav
- Logo
- Nav items (with active state)
- User menu (bottom)
- Collapsible toggle

### Header/TopBar
- Search input
- Notifications icon
- User menu dropdown

### PageHeader
- Title + description
- Breadcrumbs
- Action buttons

### KPI Card
- Icon (top-right)
- Title
- Value + unit
- Change indicator
- Optional chart spark

### Chart Panel
- Title + description
- Chart area
- Legend
- Export button

---

## DARK MODE DEFAULTS

All colors are dark-theme optimized:
- Background: Slate 950 (almost black)
- Surfaces: Slate 900 (dark gray)
- Text: Slate 100 (off-white)
- Secondary text: Slate 400 (light gray)
- Borders: Slate 700 with 30% opacity

No light mode currently needed.

---

## ACCESSIBILITY STANDARDS

### WCAG 2.1 AA Compliance Targets

1. **Color Contrast**: 4.5:1 for body text, 3:1 for large text
2. **Focus Indicators**: Visible 3px ring on all interactive elements
3. **Semantic HTML**: Proper heading hierarchy, nav, main, etc.
4. **ARIA Labels**: Icon buttons must have aria-label
5. **Form Labels**: All inputs must have `<label>` or aria-label
6. **Keyboard Navigation**: All interactive elements reachable via Tab

### Focus Ring Utility

```typescript
extend: {
  outline: {
    'primary-ring': '2px solid #60a5fa',
  }
}
```

Usage: `focus:outline-primary-ring focus:outline-offset-2`

---

## IMPLEMENTATION PRIORITY

1. **Phase 1 (Critical)**: Add color tokens to tailwind.config.ts
2. **Phase 2 (Critical)**: Fix Button, Card, Input variants
3. **Phase 3 (High)**: Add spacing/typography to config
4. **Phase 4 (High)**: Create component patterns (SidebarNav, Header, KPI, Chart)
5. **Phase 5 (Medium)**: Add accessibility utilities
6. **Phase 6 (Medium)**: Document in Storybook

---

**Next Phase**: Maker Agent will now implement these standards in code.

Prepared by: Design System Agent
Timestamp: March 9, 2026, 11:15 AM

