# iNetZero UX Playbook & Design System

**Version**: 1.0.0
**Status**: 📋 TO BE COMPLETED (Sprint 1 - Week 2)
**Owner**: Design + Frontend Team
**Target Completion**: March 22, 2026

---

## 🎯 Playbook Objective

Establish a comprehensive design system and UX guidelines to ensure **consistent, accessible, and professional** UI across all iNetZero modules. This playbook serves as the single source of truth for all frontend development.

---

## 📋 What's Included in This Playbook

### 1. **Design System & Component Library**
### 2. **Color Palette & Typography**
### 3. **Layout & Spacing Standards**
### 4. **Interactive Component Patterns**
### 5. **Forms & Input Validation**
### 6. **Data Visualization Guidelines**
### 7. **Navigation Patterns**
### 8. **Accessibility Standards (WCAG 2.1 AA)**
### 9. **Dark Mode Support**
### 10. **Mobile Responsiveness**
### 11. **State Patterns (Empty, Loading, Error, Success)**
### 12. **Iconography**
### 13. **Motion & Transitions**
### 14. **User Feedback (Toasts, Modals, Notifications)**

---

## 1️⃣ Design System & Component Library

### Technology Stack
- **Framework**: React 18+ with TypeScript
- **Styling**: Tailwind CSS + Styled Components
- **Component Library**: Radix UI (headless, accessible)
- **Storybook**: For component documentation
- **Icons**: Lucide React (24px, 16px, 32px sizes)

### Core Components to Build

```
Core
├── Button (primary, secondary, danger, ghost)
├── Input (text, email, password, number, date)
├── Textarea
├── Select / Dropdown
├── Checkbox
├── Radio Group
├── Toggle
└── Loading Spinner

Navigation
├── Navbar
├── Sidebar
├── Breadcrumbs
├── Tabs
└── Pagination

Data Display
├── Table (sortable, filterable)
├── Card
├── Badge
├── Avatar
├── Progress Bar
└── Tooltip

Feedback
├── Alert
├── Toast/Notification
├── Modal/Dialog
├── Confirmation Dialog
├── Popover
└── Skeleton Loading

Forms
├── FormField (wrapper with label + error)
├── FormGroup
├── DatePicker
├── TimePicker
├── FileUpload
└── MultiSelect

Data Visualization
├── LineChart
├── BarChart
├── PieChart
├── AreaChart
└── Gauge

Layout
├── Container
├── Grid
├── Flex
├── Stack (Horizontal/Vertical)
└── AspectRatio
```

---

## 2️⃣ Color Palette

### Primary Colors

```
Primary Blue (Brand)
├── 50:  #EBF8FF
├── 100: #BEE3F8
├── 200: #90CDF4
├── 300: #63B3ED
├── 400: #4299E1
├── 500: #3182CE (Primary)
├── 600: #2C5AA0
├── 700: #2C5282
├── 800: #2A4365
└── 900: #1A202C

Complementary Teal
├── 50:  #E0F2F1
├── 500: #26A69A (Secondary)
└── 900: #00695C
```

### Semantic Colors

```
Success
├── Light: #C6F6D5
├── Base:  #48BB78 ✅
└── Dark:  #22543D

Warning
├── Light: #FEEBC8
├── Base:  #ED8936 ⚠️
└── Dark:  #7C2D12

Danger/Error
├── Light: #FED7D7
├── Base:  #F56565 ❌
└── Dark:  #742A2A

Info
├── Light: #BEE3F8
├── Base:  #4299E1 ℹ️
└── Dark:  #2C5282
```

### Neutral Colors

```
White:     #FFFFFF
Gray 50:   #F9FAFB
Gray 100:  #F3F4F6
Gray 200:  #E5E7EB
Gray 300:  #D1D5DB
Gray 400:  #9CA3AF
Gray 500:  #6B7280
Gray 600:  #4B5563
Gray 700:  #374151
Gray 800:  #1F2937
Gray 900:  #111827
Black:     #000000
```

---

## 3️⃣ Typography

### Font Stack
```css
Font Family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', sans-serif
(System fonts for best readability)
```

### Font Sizes & Weights

```
Display (H1)
├── Size: 32px (2rem)
├── Weight: 700 (Bold)
├── Line Height: 40px (1.25)
└── Usage: Page titles, main headings

Heading 2 (H2)
├── Size: 28px (1.75rem)
├── Weight: 600 (Semibold)
├── Line Height: 36px (1.29)
└── Usage: Section headings

Heading 3 (H3)
├── Size: 24px (1.5rem)
├── Weight: 600 (Semibold)
├── Line Height: 32px (1.33)
└── Usage: Subsection headings

Heading 4 (H4)
├── Size: 20px (1.25rem)
├── Weight: 600 (Semibold)
├── Line Height: 28px (1.4)
└── Usage: Card titles, labels

Body Large
├── Size: 18px (1.125rem)
├── Weight: 400 (Regular)
├── Line Height: 28px (1.56)
└── Usage: Large body text

Body Regular
├── Size: 16px (1rem)
├── Weight: 400 (Regular)
├── Line Height: 24px (1.5)
└── Usage: Default body text

Body Small
├── Size: 14px (0.875rem)
├── Weight: 400 (Regular)
├── Line Height: 20px (1.43)
└── Usage: Secondary text, captions

Label
├── Size: 12px (0.75rem)
├── Weight: 500 (Medium)
├── Line Height: 16px (1.33)
└── Usage: Form labels, badges

Code
├── Font: 'Monaco', 'Courier New', monospace
├── Size: 13px
├── Weight: 400
└── Usage: Code blocks, technical content
```

---

## 4️⃣ Layout & Spacing

### Spacing Scale
```
0:    0px
1:    4px
2:    8px
3:    12px
4:    16px
6:    24px
8:    32px
12:   48px
16:   64px
20:   80px
24:   96px
32:   128px
```

### Container Sizes
```
XS: 320px  (mobile)
SM: 640px  (tablet)
MD: 768px  (tablet landscape)
LG: 1024px (desktop)
XL: 1280px (large desktop)
2XL: 1536px (ultra-wide)
```

### Padding Standards

```
Compact Layout:  8px or 12px
Normal Layout:   16px or 24px
Spacious Layout: 32px or 48px

Card Padding:    24px
Modal Padding:   32px
Page Padding:    24px (mobile), 32px (desktop)
```

---

## 5️⃣ Interactive Component Patterns

### Button Variants

```
Primary Button
├── Background: Blue 500
├── Text: White
├── Hover: Blue 600 (darker)
├── Active: Blue 700
├── Disabled: Gray 300 (opacity 50%)
└── Usage: Primary actions, CTAs

Secondary Button
├── Background: Gray 100
├── Text: Gray 900
├── Border: 1px Gray 300
├── Hover: Gray 200
└── Usage: Alternative actions

Danger Button
├── Background: Red 500
├── Text: White
├── Hover: Red 600
└── Usage: Destructive actions (delete, etc)

Ghost Button
├── Background: Transparent
├── Text: Blue 500
├── Border: None
├── Hover: Blue 100 background
└── Usage: Tertiary actions, links
```

### Button Sizes

```
Small:    12px font, 32px height, 12px padding
Regular:  14px font, 40px height, 16px padding
Large:    16px font, 48px height, 20px padding
```

### Loading States

```
Button.loading
├── Show spinner icon
├── Disable click
├── Show text "Loading..." or just spinner
└── Disable pointer events

Spinner Animation
├── Rotate 360° infinite
├── Duration: 1 second
├── Easing: linear
└── Color: Brand primary blue
```

---

## 6️⃣ Forms & Input Validation

### Form Field Structure

```
<FormField
  label="Organization Name"
  required
  error={errors.name}
  helpText="This will appear on reports"
>
  <Input
    name="name"
    placeholder="Enter organization name"
    value={formData.name}
    onChange={handleChange}
    aria-label="Organization Name"
  />
</FormField>
```

### Validation States

```
Valid (Success)
├── Border: Green 500
├── Icon: Check circle
├── Message: Green 600 text
└── Background: Green 50

Invalid (Error)
├── Border: Red 500
├── Icon: Exclamation circle
├── Message: Red 600 text
└── Background: Red 50

Warning
├── Border: Orange 500
├── Icon: Warning triangle
├── Message: Orange 600 text
└── Background: Orange 50

Focused
├── Border: Blue 500
├── Shadow: 0 0 0 3px rgba(66, 153, 225, 0.1)
└── Outline: None (border shadow instead)

Disabled
├── Background: Gray 100
├── Text: Gray 400
├── Cursor: Not-allowed
└── Opacity: 50%
```

### Form Layout Patterns

```
Single Column
├── Label on top
├── Input below
├── Error message below input
└── Gap: 8px between elements

Two Column (Desktop)
├── 50% width each
├── Responsive: 100% width on mobile
└── Gap: 16px between columns

Inline Forms
├── Label and input on same line
├── 30% label, 70% input
└── Error below input block
```

---

## 7️⃣ Data Visualization Guidelines

### Chart Colors (Consistent Palette)

```
Primary Series:    #3182CE (Blue)
Secondary Series:  #26A69A (Teal)
Tertiary Series:   #48BB78 (Green)
Quaternary Series: #ED8936 (Orange)
Quinary Series:    #9F7AEA (Purple)

Attention:         #F56565 (Red)
Neutral:           #A0AEC0 (Gray)
```

### Chart Best Practices

```
Line Charts
├── Use for trends over time
├── Multiple series: Use different colors
├── Marker size: 4px
├── Stroke width: 2px
└── Example: Energy consumption over 7 days

Bar Charts
├── Use for comparisons
├── Group by category
├── Responsive: Stack on mobile
└── Example: Facility-level consumption breakdown

Pie/Donut Charts
├── Use for composition (parts of whole)
├── Max 5-6 segments
├── Show legend and values
└── Example: Scope 1 vs 2 emissions

Gauge Charts
├── Use for KPI status (PUE, CUE, etc)
├── Green: Within target
├── Yellow: Warning zone
├── Red: Exceeded
└── Show min/max/target values

Area Charts
├── Use for volume/cumulative trends
├── Stack areas for parts of whole
└── Example: Carbon breakdown by source
```

---

## 8️⃣ Accessibility (WCAG 2.1 AA)

### Essential Requirements

```
✅ Color Contrast
├── Body text: 4.5:1 ratio (AAA)
├── Large text: 3:1 ratio (AA)
├── UI components: 3:1 ratio
└── Test: Use contrast checker tools

✅ Keyboard Navigation
├── All interactive elements focusable
├── Tab order logical (left→right, top→bottom)
├── Focus indicator visible (blue outline)
├── Escape key closes modals
└── Enter key activates buttons

✅ Screen Reader Support
├── Semantic HTML (button, nav, main, etc)
├── Form labels associated (htmlFor)
├── ARIA labels where needed
├── Images have alt text
└── Lists marked as <ul>, <ol>

✅ Motion
├── No auto-playing animations
├── Reduce motion respected (prefers-reduced-motion)
├── Animations <3 seconds
└── No flashing at >3 Hz

✅ Mobile Accessibility
├── Touch targets: 44px minimum
├── Font size: 16px minimum (avoid zoom)
├── Viewport meta tag set
└── No horizontal scrolling
```

---

## 9️⃣ Dark Mode Support

### Dark Mode Colors

```
Dark Background:   #111827 (Gray 900)
Dark Surface:      #1F2937 (Gray 800)
Dark Surface Alt:  #374151 (Gray 700)
Dark Text:         #F9FAFB (Gray 50)
Dark Text Alt:     #D1D5DB (Gray 300)

Dark Disabled:     #4B5563 (Gray 600)
Dark Border:       #4B5563 (Gray 600)
Dark Input BG:     #374151 (Gray 700)
Dark Input Border: #4B5563 (Gray 600)

Color Adjustments
├── Primary: Lighter shade in dark mode
├── Semantic colors: Slightly adjusted for contrast
└── Shadows: Adjusted for dark backgrounds
```

### Implementation

```css
/* Tailwind dark mode */
<html className="dark">
  /* Using dark: prefix */
  <div className="bg-white dark:bg-gray-900">

/* CSS variable approach */
:root {
  --bg-primary: #FFFFFF;
  --text-primary: #111827;
}

@media (prefers-color-scheme: dark) {
  :root {
    --bg-primary: #111827;
    --text-primary: #F9FAFB;
  }
}
```

---

## 🔟 Mobile Responsiveness

### Breakpoints

```
Mobile:     < 640px   (default, single column)
Tablet:     640px+    (2 columns)
Desktop:    1024px+   (3+ columns)
Wide:       1280px+   (full-width layouts)
```

### Mobile-First Approach

```
1. Design for 320px width first
2. Add features as space allows
3. Optimize touch targets (44px minimum)
4. Stack elements vertically by default
5. Use viewport units wisely
6. Test on real devices
```

### Touch Interactions

```
Button/Link: 44px × 44px minimum
Spacing:     8px minimum between interactive elements
Hover:       Use active state instead (no hover on mobile)
Swipe:       Support horizontal swipe for navigation
Long Press:  Consider for context menus
```

---

## 1️⃣1️⃣ State Patterns

### Empty State

```
<EmptyState
  icon={Database}
  title="No data yet"
  description="Create your first entry to get started"
  action={<Button>Create Entry</Button>}
/>

Design:
├── Icon: 64px, gray 400
├── Title: Body Large, Gray 900
├── Description: Body Small, Gray 600
└── Button: Primary action button
```

### Loading State

```
<Skeleton variant="text" count={3} />
<Skeleton variant="rectangular" height={200} />

Design:
├── Animated shimmer effect (left to right)
├── Duration: 1.5 seconds
├── Color: Gray 200 → Gray 100 → Gray 200
└── Show while fetching data
```

### Error State

```
<ErrorAlert
  title="Failed to load data"
  message="Please try again or contact support"
  retry={() => refetch()}
/>

Design:
├── Background: Red 50
├── Border: Red 500
├── Icon: Exclamation circle (Red 500)
├── Retry button: Secondary
└── Dismissible: Optional X button
```

### Success State

```
<SuccessAlert
  title="Saved successfully"
  message="Your changes have been saved"
/>

Design:
├── Background: Green 50
├── Border: Green 500
├── Icon: Check circle (Green 500)
├── Duration: Auto-dismiss in 5 seconds
└── Dismissible: Optional
```

---

## 1️⃣2️⃣ Iconography

### Icon Library: Lucide React

```
Standard Sizes:
├── 16px  : Inline, labels, small actions
├── 20px  : Default buttons, navigation
├── 24px  : Cards, large buttons
├── 32px  : Headers, emphasis
└── 48px  : Hero sections

Naming Convention:
├── <Icon name="check-circle" />
├── <Icon name="alert-triangle" />
├── <Icon name="settings" />
└── All icons from Lucide library

Color Guidelines:
├── Primary icons:  Brand color (Blue 500)
├── Success icons:  Green 500
├── Warning icons:  Orange 500
├── Error icons:    Red 500
├── Neutral icons:  Gray 400 or 600
└── Disabled:       Gray 300
```

---

## 1️⃣3️⃣ Motion & Transitions

### Animation Easing

```
Ease Curve:
├── ease-in-out: Default (cubic-bezier(0.4, 0, 0.2, 1))
├── ease-in:     Emphasis (cubic-bezier(0.4, 0, 1, 1))
├── ease-out:    Decelerate (cubic-bezier(0, 0, 0.2, 1))
└── linear:      Continuous (spinners, progress)

Duration:
├── 100ms  : Micro-interactions (button hover)
├── 200ms  : Standard transitions
├── 300ms  : Page transitions
├── 500ms  : Emphasis animations
└── 1000ms : Looping animations (spinners)
```

### Transition Examples

```
Button Hover:
transition: all 100ms ease-in-out

Modal Entrance:
animation: slideUp 300ms ease-out

Spinner:
animation: rotate 1s linear infinite

Loading Bar:
transition: width 300ms ease-out

Dropdown Open:
animation: slideDown 200ms ease-out

Alert Toast:
animation: slideIn 200ms ease-out, slideOut 200ms ease-in 4800ms
```

---

## 1️⃣4️⃣ User Feedback System

### Toast Notifications

```
Success Toast
├── Background: Green 50
├── Border-left: 4px Green 500
├── Icon: Check circle
├── Text: Gray 900
├── Duration: 5 seconds auto-dismiss
└── Position: Bottom-right

Error Toast
├── Background: Red 50
├── Border-left: 4px Red 500
├── Icon: Alert circle
├── Text: Gray 900
├── Duration: 10 seconds (longer for errors)
├── Action: Retry button (optional)
└── Position: Bottom-right

Info Toast
├── Background: Blue 50
├── Border-left: 4px Blue 500
├── Icon: Info circle
├── Text: Gray 900
├── Duration: 5 seconds
└── Position: Bottom-right
```

### Modals

```
Modal Structure:
├── Backdrop: Black 50% opacity
├── Container: White, rounded (8px), shadow
├── Header: Title + close button
├── Body: Content area
├── Footer: Action buttons

Sizing:
├── Small:  400px max-width
├── Medium: 600px max-width (default)
├── Large:  800px max-width

Animations:
├── Enter: Scale in + fade in 200ms
├── Exit:  Scale out + fade out 150ms
└── Backdrop: Fade in/out
```

---

## 📁 Directory Structure for Design System

```
frontend/src/
├── components/
│   ├── ui/
│   │   ├── Button.tsx
│   │   ├── Input.tsx
│   │   ├── Select.tsx
│   │   ├── Modal.tsx
│   │   ├── Toast.tsx
│   │   ├── Card.tsx
│   │   ├── Badge.tsx
│   │   ├── Avatar.tsx
│   │   ├── Spinner.tsx
│   │   ├── Skeleton.tsx
│   │   ├── Table.tsx
│   │   └── ... (all base components)
│   │
│   ├── forms/
│   │   ├── FormField.tsx
│   │   ├── FormGroup.tsx
│   │   └── FormActions.tsx
│   │
│   ├── layout/
│   │   ├── Container.tsx
│   │   ├── Stack.tsx
│   │   ├── Grid.tsx
│   │   ├── Navbar.tsx
│   │   ├── Sidebar.tsx
│   │   └── Footer.tsx
│   │
│   ├── data-display/
│   │   ├── Table/
│   │   ├── Card/
│   │   ├── Badge/
│   │   └── Avatar/
│   │
│   └── feedback/
│       ├── Alert.tsx
│       ├── Toast.tsx
│       ├── Modal.tsx
│       ├── Confirmation.tsx
│       └── EmptyState.tsx
│
├── styles/
│   ├── globals.css
│   ├── colors.css
│   ├── typography.css
│   ├── animations.css
│   └── tailwind.config.js
│
├── hooks/
│   ├── useToast.ts
│   ├── useModal.ts
│   └── useMediaQuery.ts
│
└── themes/
    ├── light.ts
    ├── dark.ts
    └── tokens.ts
```

---

## 📚 Storybook Documentation

### Component Story Structure

```typescript
// Button.stories.tsx
import { Button } from './Button'

export default {
  title: 'Components/Button',
  component: Button,
  argTypes: {
    variant: {
      control: { type: 'select' },
      options: ['primary', 'secondary', 'danger', 'ghost'],
    },
    size: {
      control: { type: 'select' },
      options: ['sm', 'md', 'lg'],
    },
    disabled: {
      control: 'boolean',
    },
  },
}

export const Primary = {
  args: {
    variant: 'primary',
    children: 'Click me',
  },
}

export const Secondary = {
  args: {
    variant: 'secondary',
    children: 'Click me',
  },
}

export const Loading = {
  args: {
    variant: 'primary',
    loading: true,
    children: 'Loading...',
  },
}

export const Disabled = {
  args: {
    variant: 'primary',
    disabled: true,
    children: 'Disabled',
  },
}
```

---

## ✅ Implementation Checklist

### Sprint 1 Week 1-2 Deliverables

- [ ] Design tokens finalized (colors, spacing, typography)
- [ ] Component library planned and documented
- [ ] Tailwind CSS configuration
- [ ] Storybook setup and configured
- [ ] Core UI components implemented:
  - [ ] Button (all variants)
  - [ ] Input (all types)
  - [ ] Card
  - [ ] Badge
  - [ ] Spinner/Loading
  - [ ] Toast/Notification
  - [ ] Modal/Dialog
  - [ ] Alert
- [ ] Layout components:
  - [ ] Container
  - [ ] Stack/Flex
  - [ ] Grid
  - [ ] Navbar
  - [ ] Sidebar
- [ ] Accessibility audit (WCAG 2.1 AA)
- [ ] Dark mode theme implemented
- [ ] Mobile responsiveness verified
- [ ] Storybook stories for all components
- [ ] Design system documentation published
- [ ] Team training session on design system

---

## 📝 Guidelines for All Developers

### Before Building Any UI

1. **Check the Design System First**
   - Is the component already built?
   - Use the existing component (don't duplicate)

2. **Follow the Patterns**
   - Use specified colors from palette
   - Use proper spacing scale
   - Match typography hierarchy

3. **Ensure Accessibility**
   - Test keyboard navigation
   - Check color contrast
   - Add ARIA labels where needed
   - Test with screen reader

4. **Mobile First**
   - Design for 320px first
   - Test on real mobile devices
   - Touch targets ≥44px

5. **Document in Storybook**
   - Create story for new component
   - Document all variants
   - Add usage examples

6. **Get Design Review**
   - Consistency check
   - Accessibility review
   - Mobile verification

---

## 📞 UX Design Contact

**Design Lead**: [Name]
**Design Review**: Every Tuesday 10 AM
**Slack Channel**: #design-system

---

**Status**: 📋 To be implemented during Sprint 1
**Owner**: Design + Frontend Team
**Deadline**: March 22, 2026 (End of Sprint 1 Week 2)

All subsequent UI development depends on this playbook being complete and approved.
