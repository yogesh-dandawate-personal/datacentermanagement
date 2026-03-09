# Glasmorphic Design System for iNetZero

**Design Style**: Glasmorphism (Modern, Premium, Frosted Glass Effect)
**Status**: 📋 To be implemented during Sprint 1
**Last Updated**: March 9, 2026

---

## 🎨 What is Glasmorphism?

Glasmorphism is a modern UI design trend featuring:
- **Frosted glass effect** (semi-transparent, blurred background)
- **Soft shadows** and layered depth
- **Neon accent colors** for contrast and vibrancy
- **Subtle gradients** and inner glows
- **Floating, floating components** with depth perception

**Perfect for**: Modern SaaS dashboards, data visualization, premium brands

---

## 🌈 Glasmorphic Color Palette

### Glass Backgrounds (Semi-transparent)

```
Light Mode Glass:
├── Primary Glass:    rgba(255, 255, 255, 0.10) → blur(12px)
├── Secondary Glass:  rgba(255, 255, 255, 0.08) → blur(10px)
├── Tertiary Glass:   rgba(255, 255, 255, 0.06) → blur(8px)
└── Text Over Glass:  #1F2937 (Gray 800)

Dark Mode Glass:
├── Primary Glass:    rgba(30, 30, 60, 0.30) → blur(12px)
├── Secondary Glass:  rgba(30, 30, 60, 0.25) → blur(10px)
├── Tertiary Glass:   rgba(30, 30, 60, 0.20) → blur(8px)
└── Text Over Glass:  #F9FAFB (Gray 50)
```

### Neon Accent Colors

```
Neon Cyan (Primary Accent)
├── Hex:           #00D9FF
├── RGB:           0, 217, 255
├── Usage:         Primary buttons, active states, focus rings
├── Glow Color:    rgba(0, 217, 255, 0.3)
└── Text Shadow:   0 0 10px rgba(0, 217, 255, 0.6)

Neon Purple (Secondary Accent)
├── Hex:           #B93FFF
├── RGB:           185, 63, 255
├── Usage:         Highlights, special features
├── Glow Color:    rgba(185, 63, 255, 0.3)
└── Text Shadow:   0 0 10px rgba(185, 63, 255, 0.6)

Neon Green (Success)
├── Hex:           #39FF14
├── RGB:           57, 255, 20
├── Usage:         Success states, positive feedback
├── Glow Color:    rgba(57, 255, 20, 0.3)
└── Text Shadow:   0 0 10px rgba(57, 255, 20, 0.6)

Neon Orange (Warning)
├── Hex:           #FF6B35
├── RGB:           255, 107, 53
├── Usage:         Warnings, attention-needed
├── Glow Color:    rgba(255, 107, 53, 0.3)
└── Text Shadow:   0 0 10px rgba(255, 107, 53, 0.6)

Neon Pink (Error)
├── Hex:           #FF006E
├── RGB:           255, 0, 110
├── Usage:         Errors, critical alerts
├── Glow Color:    rgba(255, 0, 110, 0.3)
└── Text Shadow:   0 0 10px rgba(255, 0, 110, 0.6)
```

---

## 💎 Glasmorphic CSS Foundation

### Base Glass Classes

```css
/* Primary Glass Element */
.glass {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-radius: 12px;
  box-shadow:
    0 8px 32px 0 rgba(31, 38, 135, 0.37),
    inset 1px 1px 0 rgba(255, 255, 255, 0.3);
}

/* Dark Mode Adjustment */
.dark .glass {
  background: rgba(15, 20, 50, 0.4);
  border: 1px solid rgba(0, 217, 255, 0.15);
  box-shadow:
    0 8px 32px 0 rgba(0, 0, 0, 0.3),
    inset 1px 1px 0 rgba(255, 255, 255, 0.1);
}

/* Glass Card with Neon Cyan Border */
.glass-card {
  background: rgba(255, 255, 255, 0.08);
  border: 2px solid rgba(0, 217, 255, 0.3);
  backdrop-filter: blur(15px);
  -webkit-backdrop-filter: blur(15px);
  border-radius: 16px;
  padding: 24px;
  box-shadow:
    0 8px 32px rgba(31, 38, 135, 0.37),
    0 0 20px rgba(0, 217, 255, 0.2),
    inset 1px 1px 0 rgba(255, 255, 255, 0.2);
}

/* Glass Card Hover State */
.glass-card:hover {
  border-color: rgba(0, 217, 255, 0.5);
  box-shadow:
    0 12px 40px rgba(31, 38, 135, 0.45),
    0 0 30px rgba(0, 217, 255, 0.3),
    inset 1px 1px 0 rgba(255, 255, 255, 0.3);
  transform: translateY(-2px);
}

/* Neon Text Glow */
.neon-cyan {
  color: #00D9FF;
  text-shadow: 0 0 10px rgba(0, 217, 255, 0.8);
  font-weight: 600;
}

.neon-purple {
  color: #B93FFF;
  text-shadow: 0 0 10px rgba(185, 63, 255, 0.8);
  font-weight: 600;
}

/* Gradient Border Glass */
.gradient-border-glass {
  background: linear-gradient(135deg, rgba(0, 217, 255, 0.4), rgba(185, 63, 255, 0.4));
  padding: 2px;
  border-radius: 16px;

  & > div {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 14px;
    padding: 24px;
    backdrop-filter: blur(12px);
  }
}

/* Glasmorphic Input */
.glass-input {
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  border-radius: 8px;
  padding: 12px 16px;
  color: #1F2937;
  transition: all 200ms ease-in-out;

  &:focus {
    border-color: rgba(0, 217, 255, 0.5);
    box-shadow:
      0 0 20px rgba(0, 217, 255, 0.2),
      inset 0 0 0 1px rgba(0, 217, 255, 0.2);
    outline: none;
  }

  &::placeholder {
    color: rgba(31, 38, 135, 0.5);
  }
}

.dark .glass-input {
  background: rgba(15, 20, 50, 0.3);
  color: #F9FAFB;

  &::placeholder {
    color: rgba(255, 255, 255, 0.3);
  }
}
```

---

## 🎯 Glasmorphic Component Styling

### Glasmorphic Buttons

```css
/* Primary Glass Button */
.btn-glass-primary {
  background: rgba(0, 217, 255, 0.15);
  color: #00D9FF;
  border: 2px solid rgba(0, 217, 255, 0.4);
  backdrop-filter: blur(10px);
  border-radius: 10px;
  padding: 12px 24px;
  font-weight: 600;
  cursor: pointer;
  transition: all 200ms ease-in-out;
  box-shadow: 0 0 15px rgba(0, 217, 255, 0.1);

  &:hover {
    background: rgba(0, 217, 255, 0.25);
    border-color: rgba(0, 217, 255, 0.6);
    box-shadow: 0 0 25px rgba(0, 217, 255, 0.3);
    transform: translateY(-2px);
  }

  &:active {
    transform: translateY(0);
    box-shadow: 0 4px 15px rgba(0, 217, 255, 0.2);
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
}

/* Secondary Glass Button (Purple) */
.btn-glass-secondary {
  background: rgba(185, 63, 255, 0.15);
  color: #B93FFF;
  border: 2px solid rgba(185, 63, 255, 0.4);
  backdrop-filter: blur(10px);
  border-radius: 10px;
  padding: 12px 24px;
  font-weight: 600;
  transition: all 200ms ease-in-out;
  box-shadow: 0 0 15px rgba(185, 63, 255, 0.1);

  &:hover {
    background: rgba(185, 63, 255, 0.25);
    border-color: rgba(185, 63, 255, 0.6);
    box-shadow: 0 0 25px rgba(185, 63, 255, 0.3);
  }
}

/* Danger Glass Button (Neon Pink) */
.btn-glass-danger {
  background: rgba(255, 0, 110, 0.15);
  color: #FF006E;
  border: 2px solid rgba(255, 0, 110, 0.4);
  backdrop-filter: blur(10px);
  border-radius: 10px;
  padding: 12px 24px;
  font-weight: 600;
  transition: all 200ms ease-in-out;

  &:hover {
    background: rgba(255, 0, 110, 0.25);
    border-color: rgba(255, 0, 110, 0.6);
    box-shadow: 0 0 25px rgba(255, 0, 110, 0.3);
  }
}

/* Ghost Glass Button */
.btn-glass-ghost {
  background: transparent;
  color: #00D9FF;
  border: 2px solid rgba(0, 217, 255, 0.3);
  border-radius: 10px;
  padding: 12px 24px;
  cursor: pointer;
  transition: all 200ms ease-in-out;

  &:hover {
    background: rgba(0, 217, 255, 0.1);
    border-color: rgba(0, 217, 255, 0.6);
  }
}
```

### Glasmorphic Cards

```css
/* Dashboard Card */
.dashboard-card {
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(0, 217, 255, 0.2);
  border-radius: 16px;
  padding: 24px;
  backdrop-filter: blur(15px);
  -webkit-backdrop-filter: blur(15px);
  box-shadow:
    0 8px 32px rgba(31, 38, 135, 0.37),
    inset 1px 1px 0 rgba(255, 255, 255, 0.2);
  transition: all 300ms ease-in-out;

  &:hover {
    border-color: rgba(0, 217, 255, 0.4);
    box-shadow:
      0 12px 40px rgba(31, 38, 135, 0.45),
      0 0 20px rgba(0, 217, 255, 0.2),
      inset 1px 1px 0 rgba(255, 255, 255, 0.3);
    transform: translateY(-4px);
  }
}

/* Metric Card with Neon Title */
.metric-card {
  @extend .dashboard-card;

  .metric-title {
    color: #00D9FF;
    font-size: 14px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 12px;
  }

  .metric-value {
    font-size: 32px;
    font-weight: 700;
    color: #1F2937;
    margin-bottom: 8px;
  }

  .metric-unit {
    font-size: 12px;
    color: rgba(31, 38, 135, 0.6);
  }

  .metric-trend {
    font-size: 12px;
    font-weight: 600;
    margin-top: 12px;

    &.positive {
      color: #39FF14;
    }

    &.negative {
      color: #FF006E;
    }
  }
}
```

### Glasmorphic Navigation

```css
/* Navbar Glass */
.navbar-glass {
  background: rgba(255, 255, 255, 0.1);
  border-bottom: 1px solid rgba(0, 217, 255, 0.2);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  padding: 16px 24px;
  box-shadow:
    0 8px 32px rgba(31, 38, 135, 0.3),
    inset 0 1px 0 rgba(255, 255, 255, 0.2);
}

/* Sidebar Glass */
.sidebar-glass {
  background: rgba(255, 255, 255, 0.08);
  border-right: 1px solid rgba(0, 217, 255, 0.15);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
}

/* Nav Link */
.nav-link-glass {
  color: #4B5563;
  padding: 12px 16px;
  border-radius: 8px;
  transition: all 200ms ease-in-out;
  position: relative;

  &:hover {
    background: rgba(0, 217, 255, 0.1);
    color: #00D9FF;
  }

  &.active {
    background: rgba(0, 217, 255, 0.15);
    color: #00D9FF;
    border-left: 3px solid #00D9FF;
    text-shadow: 0 0 8px rgba(0, 217, 255, 0.4);
  }
}
```

### Glasmorphic Modal

```css
.modal-backdrop-glass {
  background: rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
}

.modal-glass {
  background: rgba(255, 255, 255, 0.12);
  border: 1px solid rgba(0, 217, 255, 0.3);
  border-radius: 20px;
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  box-shadow:
    0 8px 32px 0 rgba(31, 38, 135, 0.37),
    0 0 30px rgba(0, 217, 255, 0.2);
  padding: 32px;
  max-width: 600px;
  animation: glassSlideUp 300ms ease-out;

  .modal-header {
    margin-bottom: 24px;
    border-bottom: 1px solid rgba(0, 217, 255, 0.2);
    padding-bottom: 16px;

    h2 {
      color: #1F2937;
      font-size: 24px;
      font-weight: 700;
    }
  }

  .modal-footer {
    margin-top: 24px;
    border-top: 1px solid rgba(0, 217, 255, 0.2);
    padding-top: 16px;
    display: flex;
    gap: 12px;
    justify-content: flex-end;
  }
}

@keyframes glassSlideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
```

---

## ✨ Glasmorphic Animations

### Entrance Animation

```css
@keyframes glassEnter {
  0% {
    opacity: 0;
    transform: scale(0.95) translateY(10px);
    backdrop-filter: blur(0px);
  }
  100% {
    opacity: 1;
    transform: scale(1) translateY(0);
    backdrop-filter: blur(12px);
  }
}

.glass {
  animation: glassEnter 400ms cubic-bezier(0.34, 1.56, 0.64, 1);
}
```

### Hover & Focus Glow

```css
@keyframes glassGlowPulse {
  0%, 100% {
    box-shadow:
      0 8px 32px rgba(31, 38, 135, 0.37),
      0 0 15px rgba(0, 217, 255, 0.1);
  }
  50% {
    box-shadow:
      0 8px 32px rgba(31, 38, 135, 0.37),
      0 0 25px rgba(0, 217, 255, 0.2);
  }
}

.glass:hover {
  animation: glassGlowPulse 2s ease-in-out infinite;
}
```

### Loading Animation

```css
@keyframes glassShimmer {
  0% {
    background-position: -1000px 0;
  }
  100% {
    background-position: 1000px 0;
  }
}

.glass-loading {
  background: linear-gradient(
    90deg,
    rgba(0, 217, 255, 0.1) 0%,
    rgba(0, 217, 255, 0.2) 25%,
    rgba(0, 217, 255, 0.1) 50%
  );
  background-size: 1000px 100%;
  animation: glassShimmer 2s infinite;
}
```

---

## 🎨 Glasmorphic Dark Mode

```css
.dark {
  /* Darker glass backgrounds */
  .glass {
    background: rgba(15, 20, 50, 0.35);
    border-color: rgba(0, 217, 255, 0.15);
  }

  .glass-card {
    background: rgba(15, 20, 50, 0.3);
    border-color: rgba(0, 217, 255, 0.25);
    box-shadow:
      0 8px 32px rgba(0, 0, 0, 0.4),
      0 0 20px rgba(0, 217, 255, 0.15);
  }

  .glass-input {
    background: rgba(15, 20, 50, 0.25);
    border-color: rgba(0, 217, 255, 0.15);
    color: #F9FAFB;
  }

  /* Stronger neon colors in dark mode */
  .neon-cyan {
    text-shadow: 0 0 12px rgba(0, 217, 255, 0.9);
  }

  .neon-purple {
    text-shadow: 0 0 12px rgba(185, 63, 255, 0.9);
  }

  /* Stronger borders and glows */
  .dashboard-card:hover {
    box-shadow:
      0 12px 40px rgba(0, 0, 0, 0.5),
      0 0 30px rgba(0, 217, 255, 0.25);
  }
}
```

---

## 📦 Glasmorphic Component Implementation Checklist

**Sprint 1 Deliverables:**

- [ ] Glasmorphic CSS framework set up
- [ ] Glass button component (all variants)
- [ ] Glass card component
- [ ] Glass input/form fields
- [ ] Glasmorphic navigation (navbar + sidebar)
- [ ] Glasmorphic modal with backdrop
- [ ] Neon text glow styles
- [ ] Backdrop-filter polyfills (for Safari compatibility)
- [ ] Dark mode glasmorphic variants
- [ ] Accessibility maintained (contrast ratios checked)
- [ ] Storybook stories for all glass components
- [ ] Animation library (Framer Motion integration)
- [ ] Responsive glass layouts
- [ ] Glasmorphic icon styling

---

## 🛠️ Tailwind Configuration for Glasmorphism

```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        neon: {
          cyan: '#00D9FF',
          purple: '#B93FFF',
          green: '#39FF14',
          orange: '#FF6B35',
          pink: '#FF006E',
        },
      },
      backdropBlur: {
        xs: '2px',
        sm: '4px',
        DEFAULT: '12px',
        md: '15px',
        lg: '20px',
      },
      boxShadow: {
        'glass-sm': '0 4px 16px rgba(31, 38, 135, 0.15)',
        'glass-md': '0 8px 32px rgba(31, 38, 135, 0.37)',
        'glass-lg': '0 20px 48px rgba(31, 38, 135, 0.45)',
        'glass-cyan': '0 0 20px rgba(0, 217, 255, 0.2)',
        'glass-purple': '0 0 20px rgba(185, 63, 255, 0.2)',
      },
      textShadow: {
        'neon-cyan': '0 0 10px rgba(0, 217, 255, 0.8)',
        'neon-purple': '0 0 10px rgba(185, 63, 255, 0.8)',
        'neon-green': '0 0 10px rgba(57, 255, 20, 0.8)',
      },
    },
  },
  plugins: [
    require('@tailwindcss/backdrop-blur'),
  ],
}
```

---

## 🎯 Usage Example

```jsx
// Example: Glasmorphic Dashboard Component
import React from 'react'

export function GlassmorphicDashboard() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Glass Navbar */}
      <nav className="glass navbar-glass sticky top-0 z-50">
        <h1 className="text-2xl font-bold neon-cyan">iNetZero</h1>
      </nav>

      {/* Main Content */}
      <main className="p-6 space-y-6">
        {/* Metric Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="glass-card metric-card">
            <h3 className="metric-title">Total Consumption</h3>
            <p className="metric-value">45,200</p>
            <p className="metric-unit">kWh</p>
            <p className="metric-trend positive">↑ 2.5% this month</p>
          </div>

          <div className="glass-card metric-card">
            <h3 className="metric-title">Scope 2 Emissions</h3>
            <p className="metric-value">18,080</p>
            <p className="metric-unit">kg CO₂e</p>
            <p className="metric-trend negative">↑ 1.2% this month</p>
          </div>

          <div className="glass-card metric-card">
            <h3 className="metric-title">PUE Ratio</h3>
            <p className="metric-value">1.18</p>
            <p className="metric-unit">efficiency</p>
            <p className="metric-trend positive">Target: &lt;1.2</p>
          </div>
        </div>

        {/* Glass Modal Example */}
        <div className="modal-backdrop-glass fixed inset-0 flex items-center justify-center">
          <div className="modal-glass">
            <div className="modal-header">
              <h2>Submit Report for Review</h2>
            </div>
            <p>Are you ready to submit this ESG report for manager review?</p>
            <div className="modal-footer">
              <button className="btn-glass-ghost">Cancel</button>
              <button className="btn-glass-primary">Submit</button>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
```

---

## ⚠️ Browser Support & Fallbacks

```css
/* Fallback for browsers without backdrop-filter */
.glass {
  background: rgba(255, 255, 255, 0.1);
  /* Fallback: solid semi-transparent background */

  @supports (backdrop-filter: blur(10px)) {
    background: rgba(255, 255, 255, 0.08);
    backdrop-filter: blur(12px);
  }
}
```

**Browser Compatibility:**
- Chrome/Edge: 76+
- Firefox: 103+
- Safari: 9+ (with -webkit prefix)
- Mobile: iOS 13+, Android 12+

---

## 📝 Final Notes

**Glasmorphism elevates iNetZero to a modern, premium platform look while maintaining:**
- ✅ Professional data visualization
- ✅ Accessibility (WCAG 2.1 AA)
- ✅ Dark mode support
- ✅ Mobile responsiveness
- ✅ Performance (hardware acceleration via backdrop-filter)

**The combination of glasmorphic design with neon accents creates a sophisticated, modern SaaS application that stands out in the market.**

---

**Status**: 📋 To be implemented during Sprint 1
**Owner**: Design + Frontend Team
**Deadline**: March 22, 2026
