# Landing Page - Layout Structure Fix

**Status**: ✅ FIXED & VERIFIED
**Date**: March 10, 2026
**Build**: Production build passing

---

## Layout Overview

The Landing page now has a properly structured, responsive layout that correctly positions the header, sidebar navigation, and footer.

### Visual Structure

```
┌─────────────────────────────────────────────────────────────┐
│  Window (full viewport)                                     │
│                                                              │
│  ┌──────────┬─────────────────────────────────────────────┐ │
│  │ Sidebar  │ Header (Nav Bar)                            │ │
│  │ (Fixed)  │ - Fixed Position                            │ │
│  │ z=40     │ - Accounts for sidebar with dynamic left    │ │
│  │          │ - Left margin: 64 units (open) / 20 units  │ │
│  │          │ - Right edge extends to window edge        │ │
│  │ w=64/20  │                                              │ │
│  │          ├─────────────────────────────────────────────┤ │
│  │ 📊 ESG   │ Hero Section                                │ │
│  │ Platform │ - pt-40 (padding-top) to avoid header      │ │
│  │ 🛍️ Carbon│ - Centered content                         │ │
│  │ Marketplace│                                            │ │
│  │ ⚙️ Admin │ ├─────────────────────────────────────────────┤ │
│  │          │ Features Section                            │ │
│  │ [toggle] │ - Grid layout                              │ │
│  │          │ - Responsive columns                       │ │
│  │          │                                              │ │
│  │          ├─────────────────────────────────────────────┤ │
│  │ [Sign In]│ More Sections                              │ │
│  │          │ - Pricing, FAQ, CTA                        │ │
│  │          │                                              │ │
│  │          ├─────────────────────────────────────────────┤ │
│  │          │ Footer                                      │ │
│  │          │ - mt-auto (pushed to bottom)               │ │
│  │          │ - Accounts for sidebar margin             │ │
│  │          │ - Links, company info                      │ │
│  │          │ - Copyright                                │ │
│  │          └─────────────────────────────────────────────┘ │
│  └──────────┴─────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## Technical Structure

### Component Hierarchy

```jsx
<div className="min-h-screen bg-gradient-to-br from-slate-950 via-blue-950 to-slate-950 flex">
  {/* SIDEBAR (Fixed Position) */}
  <aside className={`${sidebarOpen ? 'w-64' : 'w-20'} ... fixed left-0 top-0 h-screen z-40 flex flex-col`}>
    {/* Logo, Navigation, Sign In Button */}
  </aside>

  {/* MAIN CONTENT AREA (Accounts for Sidebar) */}
  <main className={`${sidebarOpen ? 'ml-64' : 'ml-20'} w-full transition-all duration-300 min-h-screen flex flex-col`}>

    {/* HEADER / NAVIGATION (Fixed Position) */}
    <nav className={`fixed top-0 ${sidebarOpen ? 'left-64' : 'left-20'} right-0 z-50 ... transition-all duration-300`}>
      {/* Logo, Navigation Links, Sign In Button */}
    </nav>

    {/* CONTENT SECTIONS */}
    <section className="pt-40 pb-20 px-4">
      {/* Hero Section - First section with extra padding for fixed header */}
    </section>

    <section className="py-20 px-4 border-t border-slate-800">
      {/* Features Section */}
    </section>

    <section className="py-20 px-4 border-t border-slate-800">
      {/* Pricing Section */}
    </section>

    <section className="py-20 px-4 border-t border-slate-800">
      {/* FAQ Section */}
    </section>

    <section className="py-20 px-4 border-t border-slate-800">
      {/* Final CTA Section */}
    </section>

    {/* FOOTER (Inside Main, Pushed to Bottom) */}
    <footer className="border-t border-slate-800 py-12 px-4 bg-slate-900/30 mt-auto">
      {/* Company Info, Links, Copyright */}
    </footer>

  </main>

  {/* LOGIN MODAL (Overlay) */}
  {showLogin && <LoginModal />}
</div>
```

---

## Sidebar States

### Open State (`sidebarOpen = true`)

| Element | Width | Left Position | Margin |
|---------|-------|---------------|--------|
| Sidebar | `w-64` (256px) | `left-0` | - |
| Header (nav) | Full-width | `left-64` | - |
| Main content | Full-width | `ml-64` | 256px |
| Spacing | Full coordinated | All shift together | Smooth |

**Visual:**
```
[Sidebar 256px][Header extends right][Content 256px margin]
```

### Collapsed State (`sidebarOpen = false`)

| Element | Width | Left Position | Margin |
|---------|-------|---------------|--------|
| Sidebar | `w-20` (80px) | `left-0` | - |
| Header (nav) | Full-width | `left-20` | - |
| Main content | Full-width | `ml-20` | 80px |
| Spacing | Full coordinated | All shift together | Smooth |

**Visual:**
```
[Sidebar 80px][Header extends right][Content 80px margin]
```

### Transition

- **Duration**: 300ms smooth transition
- **Easing**: Tailwind default
- **Properties**: width, margin-left, left position
- **Affected Elements**: sidebar, header, main content

---

## Header (Nav Bar) Positioning

### CSS Classes
```css
position: fixed;
top: 0;
left: [64|20]rem;    /* Dynamic based on sidebar state */
right: 0;            /* Extends to window edge */
z-index: 50;         /* Above content, below modals */
transition: all 300ms; /* Smooth animation */
```

### Why This Structure?
- **Fixed Position**: Stays visible while scrolling
- **Dynamic Left**: Changes with sidebar toggle
- **Right: 0**: Always extends to right edge
- **Z-index 50**: Above main content (40), below modals
- **Smooth Transition**: Matches sidebar animation

### Benefits
✅ Header never overlaps main content
✅ Always visible at top of page
✅ Responsive to sidebar toggle
✅ Proper spacing maintained
✅ Professional appearance

---

## Main Content Area

### CSS Classes
```css
margin-left: [16|5]rem;  /* Accounts for sidebar width */
width: 100%;
transition: all 300ms;   /* Smooth animation */
min-height: 100vh;       /* Full viewport height */
display: flex;
flex-direction: column;   /* Stack sections vertically */
```

### Why This Structure?
- **Margin-Left**: Creates space for sidebar
- **Full Width**: Stretches to available space
- **Min-Height**: Ensures footer sticks to bottom
- **Flex Column**: Allows footer to use mt-auto
- **Smooth Transition**: Coordinates with sidebar

### Benefits
✅ Content never overlaps sidebar
✅ Responsive to sidebar state
✅ Proper spacing maintained
✅ Footer stays at bottom
✅ Consistent layout shift

---

## Footer Positioning

### CSS Classes
```css
margin-top: auto;        /* Pushed to bottom */
border-top: 1px solid;
padding: 3rem 1rem;      /* py-12 px-4 */
background: semi-transparent;
```

### Why This Structure?
- **mt-auto**: Uses flex layout to push footer down
- **Inside Main**: Part of main content flow
- **Responsive**: Inherits sidebar margin from main
- **Sticky to Bottom**: Always at viewport bottom when content is short

### Benefits
✅ Footer always at bottom (no hanging)
✅ Part of proper document flow
✅ Accounts for sidebar automatically
✅ Responsive on all screen sizes
✅ Professional appearance

---

## Content Sections Padding

### First Section (Hero)
```css
padding-top: 2.5rem;  /* pt-40 = 10rem */
padding-bottom: 5rem; /* pb-20 */
```

**Why?** First section needs extra padding to avoid fixed header overlap. 40 units = 10rem = ~160px, accounting for header height.

### Other Sections
```css
padding-top: 5rem;    /* py-20 */
padding-bottom: 5rem;
border-top: 1px;      /* Visual separator */
```

**Why?** Consistent spacing between sections with visual dividers.

---

## Responsive Behavior

### Desktop (>1024px)
- Sidebar visible at full width (w-64 or w-20)
- Header stretches to fill available width
- Navigation menu visible
- All sections responsive

### Tablet (768-1024px)
- Sidebar toggles as needed
- Navigation adjusts
- Hero section responsive

### Mobile (<768px)
- Sidebar still functional (may be collapsed)
- Header navigation simplified
- Content stacks appropriately
- Footer adapts to screen width

---

## Z-Index Hierarchy

| Element | Z-Index | Purpose |
|---------|---------|---------|
| Sidebar | 40 | Above content but below header |
| Header (nav) | 50 | Always visible, above content |
| Modals (LoginModal) | 50+ | Top level (defined in component) |
| Content | 0 (default) | Scrolls under header |

---

## Transition Animation

### Sidebar Toggle
```javascript
const [sidebarOpen, setSidebarOpen] = useState(true)

// When user clicks toggle:
setSidebarOpen(!sidebarOpen)

// Causes these class updates:
// sidebar: w-64 → w-20
// header: left-64 → left-20
// main: ml-64 → ml-20
```

### Animation Details
- **Duration**: 300ms (duration-300)
- **Timing**: Tailwind default (ease)
- **Smooth Across**: All elements simultaneously

### User Experience
✅ Smooth, coordinated transition
✅ No layout jump or flicker
✅ Professional appearance
✅ Fast and responsive

---

## Common Issues & Fixes

### Issue: Header Overlaps Content
**Cause**: First section has `pt-32` instead of `pt-40`
**Fix**: Increased to `pt-40` to accommodate fixed header height

### Issue: Footer Not at Bottom
**Cause**: Main element doesn't have flex layout
**Fix**: Added `flex flex-col min-h-screen` to main element

### Issue: Header Doesn't Account for Sidebar
**Cause**: Header uses `w-full` without left margin
**Fix**: Changed to `left-64/left-20` with `right-0`

### Issue: Sidebar Margin Not Applied to Header
**Cause**: Header is fixed, doesn't inherit margin
**Fix**: Applied same margin logic to header position

---

## File Changes Summary

### frontend/src/pages/Landing.tsx

**Before:**
```jsx
<main className={`${sidebarOpen ? 'ml-64' : 'ml-20'} w-full transition-all duration-300`}>
  <nav className="fixed top-0 w-full z-50 ...">
  <section className="pt-32 pb-20 px-4">
  </main>
  <footer className="... py-12 px-4 ...">
```

**After:**
```jsx
<main className={`${sidebarOpen ? 'ml-64' : 'ml-20'} w-full transition-all duration-300 min-h-screen flex flex-col`}>
  <nav className={`fixed top-0 ${sidebarOpen ? 'left-64' : 'left-20'} right-0 z-50 ... transition-all duration-300`}>
  <section className="pt-40 pb-20 px-4">
  <footer className="... py-12 px-4 ... mt-auto">
  </main>
```

**Changes:**
1. ✅ Added `min-h-screen flex flex-col` to main
2. ✅ Changed header from `w-full` to `left-64/left-20 right-0`
3. ✅ Increased first section padding from `pt-32` to `pt-40`
4. ✅ Moved footer inside main element
5. ✅ Added `mt-auto` to footer

---

## Testing Checklist

- [x] Header stays fixed while scrolling
- [x] Header position adjusts with sidebar toggle
- [x] Main content has proper margin from sidebar
- [x] Footer stays at bottom when content is short
- [x] Footer scrolls with content when content is long
- [x] No overlap between header and content
- [x] Sidebar toggle animation is smooth
- [x] Layout works on mobile, tablet, desktop
- [x] Build passes without errors
- [x] No console errors or warnings

---

## Commits

**a692f3b**: "Fix header and footer layout to account for sidebar"
- Dynamic header positioning
- Footer properly placed
- Content padding adjusted
- Smooth transitions maintained

---

## Summary

✅ **Header** is now properly fixed and accounts for sidebar width
✅ **Footer** is now properly positioned at the bottom of main content
✅ **Sidebar margin** is consistently applied across all elements
✅ **Transitions** are smooth and coordinated
✅ **Layout** is responsive and professional
✅ **Build** passes all checks

The Landing page now has a clean, professional layout where the header and footer properly adapt to the sidebar state, creating a cohesive and polished user experience.
