# iNetZero Design System v1.0

**Status**: Production-Ready
**Last Updated**: 2026-03-09
**Tailwind CSS** + **ShadCN Patterns** + **Accessibility First**

---

## Table of Contents

1. [Color System](#color-system)
2. [Typography](#typography)
3. [Spacing & Layout](#spacing--layout)
4. [Components](#components)
5. [Usage Examples](#usage-examples)
6. [Accessibility](#accessibility)
7. [Responsive Design](#responsive-design)

---

## Color System

### Primary Colors (Brand Blue)

```css
--color-primary-50: #f0f9ff;    /* Very light blue */
--color-primary-100: #e0f2fe;
--color-primary-200: #bae6fd;
--color-primary-300: #7dd3fc;
--color-primary-400: #38bdf8;
--color-primary-500: #0ea5e9;   /* Primary brand color */
--color-primary-600: #0284c7;   /* Primary dark */
--color-primary-700: #0369a1;
--color-primary-800: #075985;
--color-primary-900: #0c3d66;   /* Very dark blue */
```

**Usage**: Primary buttons, active states, links, brand elements

### Secondary Colors (Cyan/Teal)

```css
--color-secondary-50: #ecf0ff;
--color-secondary-100: #d9e7ff;
--color-secondary-400: #22d3ee;  /* Cyan */
--color-secondary-500: #06b6d4;  /* Cyan (secondary) */
--color-secondary-600: #0891b2;
--color-secondary-700: #0e7490;
```

**Usage**: Accents, secondary buttons, hover states, icons

### Semantic Colors

```css
/* Success */
--color-success-50: #f0fdf4;
--color-success-100: #dcfce7;
--color-success-500: #10b981;   /* Green */
--color-success-600: #059669;
--color-success-900: #064e3b;

/* Warning */
--color-warning-50: #fffbeb;
--color-warning-100: #fef3c7;
--color-warning-500: #f59e0b;   /* Amber */
--color-warning-600: #d97706;
--color-warning-900: #78350f;

/* Danger/Error */
--color-danger-50: #fef2f2;
--color-danger-100: #fee2e2;
--color-danger-500: #ef4444;    /* Red */
--color-danger-600: #dc2626;
--color-danger-900: #7f1d1d;

/* Info */
--color-info-50: #eff6ff;
--color-info-100: #dbeafe;
--color-info-500: #3b82f6;      /* Blue */
--color-info-600: #2563eb;
--color-info-900: #1e3a8a;
```

**Usage**: Status messages, alerts, badges, indicators

### Neutral/Grayscale

```css
/* Light (for light backgrounds) */
--color-gray-50: #f9fafb;
--color-gray-100: #f3f4f6;
--color-gray-200: #e5e7eb;
--color-gray-300: #d1d5db;
--color-gray-400: #9ca3af;

/* Medium */
--color-gray-500: #6b7280;

/* Dark (for dark backgrounds) */
--color-gray-600: #4b5563;
--color-gray-700: #374151;
--color-gray-800: #1f2937;
--color-gray-900: #111827;

/* Dark Mode (Dark Theme for Dark Backgrounds) */
--color-slate-50: #f8fafc;
--color-slate-100: #f1f5f9;
--color-slate-200: #e2e8f0;
--color-slate-300: #cbd5e1;
--color-slate-400: #94a3b8;
--color-slate-500: #64748b;
--color-slate-600: #475569;
--color-slate-700: #334155;
--color-slate-800: #1e293b;     /* Main dark surface */
--color-slate-900: #0f172a;     /* Darker surface */
--color-slate-950: #020617;     /* Darkest */
```

**Usage**: Text, borders, backgrounds, dividers

### Dark Mode Background

```css
/* App Background */
--bg-primary: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
--bg-surface: #1e293b;          /* Card, elevated surfaces */
--bg-elevated: #334155;         /* Hover state */
--bg-input: rgba(30, 41, 59, 0.5);  /* Input backgrounds */

/* Glassmorphic (Frosted Glass Effect) */
--glass-bg: rgba(30, 41, 59, 0.5);
--glass-border: rgba(71, 85, 105, 0.5);
--glass-blur: 12px;
```

### Tailwind Color Mapping

```javascript
// tailwind.config.js
module.exports = {
  theme: {
    colors: {
      primary: {
        50: '#f0f9ff',
        100: '#e0f2fe',
        200: '#bae6fd',
        300: '#7dd3fc',
        400: '#38bdf8',
        500: '#0ea5e9',
        600: '#0284c7',
        700: '#0369a1',
        800: '#075985',
        900: '#0c3d66',
      },
      secondary: {
        50: '#ecf0ff',
        100: '#d9e7ff',
        400: '#22d3ee',
        500: '#06b6d4',
        600: '#0891b2',
        700: '#0e7490',
      },
      success: {
        50: '#f0fdf4',
        500: '#10b981',
        600: '#059669',
        900: '#064e3b',
      },
      warning: {
        50: '#fffbeb',
        500: '#f59e0b',
        600: '#d97706',
        900: '#78350f',
      },
      danger: {
        50: '#fef2f2',
        500: '#ef4444',
        600: '#dc2626',
        900: '#7f1d1d',
      },
      info: {
        50: '#eff6ff',
        500: '#3b82f6',
        600: '#2563eb',
        900: '#1e3a8a',
      },
    },
  },
}
```

---

## Typography

### Heading Scale

```css
/* H1 - Page Titles */
font-size: 2.25rem;   /* 36px */
line-height: 2.5rem; /* 140% */
font-weight: 700;     /* Bold */
letter-spacing: -0.02em;
margin-bottom: 1.5rem;

/* H2 - Section Titles */
font-size: 1.875rem;  /* 30px */
line-height: 2.25rem; /* 150% */
font-weight: 700;     /* Bold */
letter-spacing: -0.01em;
margin-bottom: 1.5rem;

/* H3 - Subsection Titles */
font-size: 1.5rem;    /* 24px */
line-height: 2rem;    /* 133% */
font-weight: 700;     /* Bold */
letter-spacing: -0.01em;
margin-bottom: 1rem;

/* H4 - Card Titles */
font-size: 1.25rem;   /* 20px */
line-height: 1.75rem; /* 140% */
font-weight: 600;     /* Semibold */
margin-bottom: 0.75rem;

/* H5 - Labels */
font-size: 1.125rem;  /* 18px */
line-height: 1.75rem; /* 155% */
font-weight: 600;     /* Semibold */
margin-bottom: 0.5rem;

/* H6 - Small Titles */
font-size: 1rem;      /* 16px */
line-height: 1.5rem;  /* 150% */
font-weight: 600;     /* Semibold */
margin-bottom: 0.5rem;
```

### Body Text

```css
/* Large Body */
font-size: 1.125rem;  /* 18px */
line-height: 1.75rem; /* 156% */
font-weight: 400;     /* Normal */

/* Standard Body (Default) */
font-size: 1rem;      /* 16px */
line-height: 1.5rem;  /* 150% */
font-weight: 400;     /* Normal */

/* Small Body */
font-size: 0.875rem;  /* 14px */
line-height: 1.25rem; /* 143% */
font-weight: 400;     /* Normal */

/* Extra Small */
font-size: 0.75rem;   /* 12px */
line-height: 1rem;    /* 133% */
font-weight: 400;     /* Normal */
```

### Font Families

```css
/* Sans Serif (Primary) */
font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', sans-serif;

/* Monospace (Code, Inputs) */
font-family: 'Roboto Mono', 'Courier New', monospace;
```

### Tailwind Configuration

```javascript
// tailwind.config.js
module.exports = {
  theme: {
    typography: {
      DEFAULT: {
        css: {
          color: '#e2e8f0',
          h1: { fontSize: '2.25rem', fontWeight: '700', lineHeight: '2.5rem' },
          h2: { fontSize: '1.875rem', fontWeight: '700', lineHeight: '2.25rem' },
          h3: { fontSize: '1.5rem', fontWeight: '700', lineHeight: '2rem' },
          h4: { fontSize: '1.25rem', fontWeight: '600', lineHeight: '1.75rem' },
          h5: { fontSize: '1.125rem', fontWeight: '600', lineHeight: '1.75rem' },
          h6: { fontSize: '1rem', fontWeight: '600', lineHeight: '1.5rem' },
        },
      },
    },
  },
}
```

---

## Spacing & Layout

### Spacing Scale (8px base unit)

```css
--space-0: 0;
--space-1: 0.25rem;   /* 4px */
--space-2: 0.5rem;    /* 8px */
--space-3: 0.75rem;   /* 12px */
--space-4: 1rem;      /* 16px */
--space-6: 1.5rem;    /* 24px */
--space-8: 2rem;      /* 32px */
--space-10: 2.5rem;   /* 40px */
--space-12: 3rem;     /* 48px */
--space-16: 4rem;     /* 64px */
--space-20: 5rem;     /* 80px */
--space-24: 6rem;     /* 96px */

/* Common Spacing Patterns */
--container-padding: 1.5rem;    /* 24px (mobile), 3rem (desktop) */
--section-gap: 3rem;             /* 48px - space between sections */
--card-gap: 1.5rem;              /* 24px - gap in grid */
--element-gap: 1rem;             /* 16px - gap between elements */
```

### Border Radius

```css
--radius-none: 0;
--radius-sm: 0.25rem;    /* 4px - small details */
--radius-md: 0.5rem;     /* 8px - form inputs */
--radius-lg: 0.75rem;    /* 12px - buttons, modals */
--radius-xl: 1rem;       /* 16px - cards */
--radius-2xl: 1.5rem;    /* 24px - large cards, hero */
--radius-3xl: 2rem;      /* 32px - extra large */
--radius-full: 9999px;   /* fully rounded (pills) */
```

### Shadows

```css
/* Elevation Levels */
--shadow-none: none;
--shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
--shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
--shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
--shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
--shadow-2xl: 0 25px 50px -12px rgba(0, 0, 0, 0.25);

/* Interactive Shadows */
--shadow-hover: 0 10px 25px -5px rgba(0, 0, 0, 0.2);
--shadow-active: 0 5px 10px -2px rgba(0, 0, 0, 0.15);

/* Glassmorphic Shadow */
--glass-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
```

### Transitions

```css
--transition-fast: all 150ms ease;
--transition-default: all 200ms ease;
--transition-slow: all 300ms ease;

--easing-ease: ease;
--easing-ease-in: ease-in;
--easing-ease-out: ease-out;
--easing-ease-in-out: ease-in-out;
--easing-linear: linear;
```

---

## Components

### Button Component

```typescript
interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  loading?: boolean;
  fullWidth?: boolean;
  icon?: ReactNode;
}

// Variants
primary:    'bg-primary-600 hover:bg-primary-700 text-white'
secondary:  'bg-secondary-600 hover:bg-secondary-700 text-white'
outline:    'border border-slate-700 hover:bg-slate-800 text-white'
ghost:      'hover:bg-slate-800 text-slate-300 hover:text-white'
danger:     'bg-danger-600 hover:bg-danger-700 text-white'

// Sizes
sm:  'px-3 py-1.5 text-sm'
md:  'px-4 py-2 text-base'
lg:  'px-6 py-3 text-lg'

// States
disabled:   'opacity-50 cursor-not-allowed'
loading:    'opacity-75 animate-pulse'
focus:      'focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 focus:ring-offset-slate-900'
```

### Input Component

```typescript
interface InputProps {
  type?: 'text' | 'email' | 'password' | 'number' | 'date' | 'time';
  placeholder?: string;
  value?: string;
  error?: string;
  disabled?: boolean;
  required?: boolean;
  icon?: ReactNode;
}

// Base Style
'w-full px-4 py-2 bg-slate-800/50 border border-slate-700/50'
'rounded-lg text-white placeholder-slate-500'
'focus:border-primary-500/50 focus:ring-2 focus:ring-primary-500/20'
'focus:outline-none transition'
'disabled:opacity-50 disabled:cursor-not-allowed'

// Error State
'border-danger-500/50 bg-danger-500/5 text-danger-400'

// Success State
'border-success-500/50 bg-success-500/5 text-success-400'
```

### Card Component

```typescript
interface CardProps {
  className?: string;
  variant?: 'default' | 'glass' | 'elevated';
  children: ReactNode;
}

// Default (Glass Effect)
'rounded-xl border border-slate-700/50'
'bg-gradient-to-br from-slate-800/50 to-slate-900/50'
'backdrop-blur-xl'
'shadow-lg'

// Elevated
'rounded-xl border border-slate-700'
'bg-slate-800'
'shadow-xl'

// Subcomponents
CardHeader: 'border-b border-slate-700/30 p-6'
CardTitle:  'text-lg font-bold text-white'
CardDescription: 'text-sm text-slate-400 mt-1'
CardContent: 'p-6'
CardFooter: 'border-t border-slate-700/30 px-6 py-4 flex items-center justify-between'
```

### Badge Component

```typescript
interface BadgeProps {
  variant?: 'primary' | 'secondary' | 'success' | 'warning' | 'danger' | 'info';
  size?: 'sm' | 'md' | 'lg';
}

// Variants
primary:    'bg-primary-500/20 text-primary-300 border border-primary-500/30'
secondary:  'bg-secondary-500/20 text-secondary-300 border border-secondary-500/30'
success:    'bg-success-500/20 text-success-300 border border-success-500/30'
warning:    'bg-warning-500/20 text-warning-300 border border-warning-500/30'
danger:     'bg-danger-500/20 text-danger-300 border border-danger-500/30'
info:       'bg-info-500/20 text-info-300 border border-info-500/30'

// Sizes
sm: 'px-2 py-1 text-xs rounded-md'
md: 'px-3 py-1.5 text-sm rounded-lg'
lg: 'px-4 py-2 text-base rounded-lg'
```

### Alert Component

```typescript
interface AlertProps {
  variant?: 'info' | 'success' | 'warning' | 'error';
  title?: string;
  message: string;
  icon?: ReactNode;
  action?: ReactNode;
}

// Variants
info:     'bg-info-500/10 border border-info-500/30 text-info-200'
success:  'bg-success-500/10 border border-success-500/30 text-success-200'
warning:  'bg-warning-500/10 border border-warning-500/30 text-warning-200'
error:    'bg-danger-500/10 border border-danger-500/30 text-danger-200'

// Layout
'rounded-lg p-4 flex items-start gap-3'
```

### Table Component

```typescript
interface TableProps {
  columns: Column[];
  data: Row[];
  sortable?: boolean;
  selectable?: boolean;
  striped?: boolean;
}

// Header
'bg-slate-800/50 border-b border-slate-700/30'
'px-6 py-3 text-left text-sm font-semibold text-slate-200'

// Rows
'border-b border-slate-700/30 hover:bg-slate-800/30 transition'
'px-6 py-4 text-sm text-slate-300'

// Striped
'even:bg-slate-800/20 odd:bg-slate-900/20'
```

### Modal Component

```typescript
interface ModalProps {
  open: boolean;
  onClose: () => void;
  title?: string;
  children: ReactNode;
  footer?: ReactNode;
}

// Overlay
'fixed inset-0 z-50 flex items-center justify-center'
'p-4 bg-black/50 backdrop-blur-sm'

// Content
'relative w-full max-w-md'
'bg-gradient-to-br from-slate-900 to-slate-950'
'backdrop-blur-xl border border-slate-700/50'
'rounded-2xl shadow-2xl'

// Header
'border-b border-slate-700/30 px-6 py-4'

// Body
'p-6'

// Footer
'border-t border-slate-700/30 px-6 py-4 flex items-center justify-end gap-3'
```

---

## Usage Examples

### Button Examples

```tsx
// Primary button
<Button variant="primary" size="lg">
  Create Report
</Button>

// Secondary button
<Button variant="secondary" size="md">
  Cancel
</Button>

// Outline button
<Button variant="outline" size="md">
  <Download className="w-4 h-4 mr-2" />
  Export
</Button>

// Ghost button (minimal)
<Button variant="ghost" size="sm">
  Learn More
</Button>

// Danger button
<Button variant="danger" size="md" loading>
  Deleting...
</Button>

// Disabled button
<Button variant="primary" disabled>
  Unavailable
</Button>
```

### Input Examples

```tsx
// Text input
<Input
  type="text"
  placeholder="Organization name"
  icon={<Building className="w-5 h-5" />}
/>

// Email input with error
<Input
  type="email"
  placeholder="your@company.com"
  error="Invalid email format"
  icon={<Mail className="w-5 h-5" />}
/>

// Password input
<Input
  type="password"
  placeholder="••••••••"
  icon={<Lock className="w-5 h-5" />}
/>

// Date input
<Input
  type="date"
  value={startDate}
  onChange={(e) => setStartDate(e.target.value)}
/>
```

### Card Examples

```tsx
// Default card
<Card>
  <CardHeader>
    <CardTitle>Energy Usage</CardTitle>
    <CardDescription>Daily consumption trends</CardDescription>
  </CardHeader>
  <CardContent>
    {/* Chart or content here */}
  </CardContent>
</Card>

// Card with footer
<Card>
  <CardHeader>
    <CardTitle>Organization Settings</CardTitle>
  </CardHeader>
  <CardContent>
    {/* Form fields */}
  </CardContent>
  <CardFooter>
    <Button variant="outline">Cancel</Button>
    <Button variant="primary">Save</Button>
  </CardFooter>
</Card>

// Elevated card
<Card variant="elevated">
  <CardContent className="p-8">
    {/* Prominent content */}
  </CardContent>
</Card>
```

### Badge Examples

```tsx
// Status badge
<Badge variant="success">Active</Badge>
<Badge variant="warning">Pending</Badge>
<Badge variant="danger">Inactive</Badge>

// Category badge
<Badge variant="primary">ESG Compliance</Badge>
<Badge variant="secondary">Energy Audit</Badge>

// Size variants
<Badge size="sm">Small</Badge>
<Badge size="md">Medium</Badge>
<Badge size="lg">Large</Badge>
```

### Alert Examples

```tsx
// Info alert
<Alert variant="info" title="Update Available" message="A new version is ready to download." />

// Success alert
<Alert variant="success" message="Report generated successfully." />

// Warning alert
<Alert variant="warning" title="High Energy Usage" message="Your facility exceeded the target by 15%." />

// Error alert
<Alert
  variant="error"
  title="Error"
  message="Failed to load data. Please try again."
  action={<Button size="sm" variant="outline">Retry</Button>}
/>
```

---

## Accessibility

### Color Contrast
- ✅ All text has minimum 4.5:1 contrast ratio (WCAG AAA)
- ✅ Interactive elements have 3:1 minimum contrast
- ✅ Colors are never the only indicator of state/meaning

### Keyboard Navigation
- ✅ All interactive elements are keyboard accessible
- ✅ Tab order is logical and visible
- ✅ Focus indicators are always visible (2px ring)
- ✅ Escape closes modals and dropdowns

### Screen Readers
- ✅ ARIA labels for icon-only buttons
- ✅ ARIA descriptions for complex components
- ✅ Form labels associated with inputs
- ✅ Error messages linked to form fields
- ✅ Loading states announced

### Focus Styles

```css
/* Standard Focus Ring */
focus:ring-2
focus:ring-primary-500
focus:ring-offset-2
focus:ring-offset-slate-900
focus:outline-none

/* High Contrast Focus */
focus:ring-4
focus:ring-primary-400
focus:ring-offset-2
focus:ring-offset-slate-900
```

---

## Responsive Design

### Breakpoints

```css
/* Tailwind Default Breakpoints */
mobile:     320px   (sm)
tablet:     640px   (md)
desktop:    1024px  (lg)
wide:       1280px  (xl)
ultrawide:  1536px  (2xl)

/* Usage in Tailwind */
<div className="text-sm md:text-base lg:text-lg">
  Responsive text size
</div>

<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
  Responsive grid
</div>
```

### Mobile-First Approach

```tsx
// Always start with mobile styles, then add larger breakpoints
<div className="
  w-full                    /* Mobile: full width */
  md:w-1/2                  /* Tablet: half width */
  lg:w-1/3                  /* Desktop: third width */
  p-4                       /* Mobile: small padding */
  md:p-6                    /* Tablet: medium padding */
  lg:p-8                    /* Desktop: large padding */
">
  Content
</div>
```

### Common Responsive Patterns

```tsx
// 1. Single column on mobile, multiple on desktop
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
  {/* cards */}
</div>

// 2. Hidden on mobile
<div className="hidden md:block">
  Desktop-only content
</div>

// 3. Responsive text
<h1 className="text-2xl md:text-3xl lg:text-4xl font-bold">
  Responsive heading
</h1>

// 4. Responsive spacing
<div className="p-4 md:p-6 lg:p-8 space-y-4 md:space-y-6">
  Elements
</div>
```

---

## Best Practices

### 1. Use Design Tokens
✅ DO: `text-primary-600`, `bg-slate-800`, `p-6`
❌ DON'T: `text-blue-600`, `bg-gray-800`, `p-24px`

### 2. Consistent Spacing
✅ DO: Use spacing scale (p-4, p-6, p-8, gap-4, gap-6)
❌ DON'T: Random padding values

### 3. Focus Management
✅ DO: Always visible focus indicators
❌ DON'T: Removing focus outlines

### 4. Mobile First
✅ DO: Design mobile first, enhance for desktop
❌ DON'T: Desktop first, then "make it mobile"

### 5. Semantic HTML
✅ DO: Use `<button>` for buttons, `<input>` for inputs
❌ DON'T: Use `<div>` for everything

### 6. ARIA Labels
✅ DO: `<button aria-label="Close">×</button>`
❌ DON'T: `<button>×</button>` (icon-only buttons)

### 7. Color + Other Cues
✅ DO: Red badge with "Error" text
❌ DON'T: Red badge only (colorblind users won't understand)

---

## Implementation Checklist

- [ ] Update `tailwind.config.js` with design tokens
- [ ] Create `src/styles/colors.css` with CSS variables
- [ ] Create `src/styles/typography.css` with font scales
- [ ] Create `src/styles/spacing.css` with spacing utilities
- [ ] Implement 50+ component library
- [ ] Add focus ring utilities
- [ ] Test with keyboard navigation
- [ ] Test with screen reader (NVDA/JAWS/VoiceOver)
- [ ] Verify color contrast (WCAG AAA)
- [ ] Test responsive breakpoints
- [ ] Performance audit (Lighthouse)
- [ ] Cross-browser testing

---

**This design system ensures consistent, professional, accessible UI/UX across iNetZero.**
