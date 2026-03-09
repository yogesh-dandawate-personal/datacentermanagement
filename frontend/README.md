# iCarbon Frontend

**Framework**: React 18 / TypeScript
**Styling**: Tailwind CSS + Material-UI
**State Management**: Redux Toolkit / Zustand
**Status**: In Development

---

## 📋 Overview

The iCarbon frontend is a modern, responsive web application for ESG emissions management. Built with React and TypeScript, it provides real-time dashboards, compliance reporting, and goal tracking for datacenters.

## 🗂️ Project Structure

```
frontend/
├── src/
│   ├── components/                  # Reusable Components
│   │   ├── common/                 # Shared components
│   │   │   ├── Header.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   ├── Footer.tsx
│   │   │   └── Loading.tsx
│   │   ├── dashboard/              # Dashboard components
│   │   │   ├── DashboardLayout.tsx
│   │   │   ├── KPICard.tsx
│   │   │   ├── ChartCard.tsx
│   │   │   └── MetricsGrid.tsx
│   │   ├── facilities/             # Facility components
│   │   │   ├── FacilityList.tsx
│   │   │   ├── FacilityCard.tsx
│   │   │   ├── FacilityForm.tsx
│   │   │   └── FacilityDetail.tsx
│   │   ├── emissions/              # Emissions components
│   │   │   ├── EmissionsChart.tsx
│   │   │   ├── ScopeBreakdown.tsx
│   │   │   ├── TrendChart.tsx
│   │   │   └── EmissionsTable.tsx
│   │   ├── reports/                # Report components
│   │   │   ├── ReportList.tsx
│   │   │   ├── ReportGenerator.tsx
│   │   │   ├── ReportViewer.tsx
│   │   │   └── ExportOptions.tsx
│   │   ├── goals/                  # Goals components
│   │   │   ├── GoalList.tsx
│   │   │   ├── GoalForm.tsx
│   │   │   ├── GoalProgress.tsx
│   │   │   └── GoalTracker.tsx
│   │   ├── alerts/                 # Alerts components
│   │   │   ├── AlertList.tsx
│   │   │   ├── AlertDetail.tsx
│   │   │   └── AlertSettings.tsx
│   │   └── settings/               # Settings components
│   │       ├── UserSettings.tsx
│   │       ├── OrgSettings.tsx
│   │       └── IntegrationSettings.tsx
│   │
│   ├── pages/                       # Page Components
│   │   ├── Dashboard.tsx           # Main dashboard
│   │   ├── Facilities.tsx          # Facilities page
│   │   ├── Emissions.tsx           # Emissions analytics
│   │   ├── Reports.tsx             # Reports page
│   │   ├── Goals.tsx               # Goals tracking
│   │   ├── Alerts.tsx              # Alerts management
│   │   ├── Settings.tsx            # Settings page
│   │   ├── Login.tsx               # Authentication
│   │   ├── NotFound.tsx            # 404 page
│   │   └── Error.tsx               # Error page
│   │
│   ├── services/                    # API Services
│   │   ├── api.ts                  # API client setup
│   │   ├── facilitiesApi.ts        # Facilities endpoints
│   │   ├── emissionsApi.ts         # Emissions endpoints
│   │   ├── reportsApi.ts           # Reports endpoints
│   │   ├── goalsApi.ts             # Goals endpoints
│   │   ├── alertsApi.ts            # Alerts endpoints
│   │   ├── usersApi.ts             # User endpoints
│   │   └── authApi.ts              # Authentication
│   │
│   ├── hooks/                       # Custom Hooks
│   │   ├── useAuth.ts              # Authentication hook
│   │   ├── useFacilities.ts        # Facilities hook
│   │   ├── useEmissions.ts         # Emissions hook
│   │   ├── useReports.ts           # Reports hook
│   │   ├── useGoals.ts             # Goals hook
│   │   ├── useAlerts.ts            # Alerts hook
│   │   ├── useFetch.ts             # Generic fetch hook
│   │   └── useLocalStorage.ts      # Local storage hook
│   │
│   ├── store/                       # State Management
│   │   ├── store.ts                # Redux store config
│   │   ├── slices/
│   │   │   ├── authSlice.ts
│   │   │   ├── facilitiesSlice.ts
│   │   │   ├── emissionsSlice.ts
│   │   │   ├── reportsSlice.ts
│   │   │   ├── goalsSlice.ts
│   │   │   ├── alertsSlice.ts
│   │   │   └── uiSlice.ts
│   │   └── selectors/              # Redux selectors
│   │       ├── authSelectors.ts
│   │       └── facilitiesSelectors.ts
│   │
│   ├── utils/                       # Utilities
│   │   ├── constants.ts            # App constants
│   │   ├── validators.ts           # Form validators
│   │   ├── formatters.ts           # Data formatters
│   │   ├── dateUtils.ts            # Date utilities
│   │   ├── chartUtils.ts           # Chart helpers
│   │   └── errorHandler.ts         # Error handling
│   │
│   ├── assets/                      # Static Assets
│   │   ├── styles/
│   │   │   ├── globals.css
│   │   │   ├── tailwind.css
│   │   │   └── theme.ts
│   │   ├── images/
│   │   └── icons/
│   │
│   ├── types/                       # TypeScript Types
│   │   ├── api.ts                  # API response types
│   │   ├── domain.ts               # Domain models
│   │   └── ui.ts                   # UI types
│   │
│   ├── config/                      # Configuration
│   │   ├── constants.ts
│   │   └── routes.ts
│   │
│   ├── App.tsx                     # Root component
│   ├── index.tsx                   # Entry point
│   └── setupTests.ts               # Test setup
│
├── tests/
│   ├── unit/                       # Unit tests
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── utils/
│   │   └── services/
│   ├── integration/                # Integration tests
│   │   ├── workflows/
│   │   └── scenarios/
│   └── e2e/                        # E2E tests (Cypress)
│       ├── support/
│       ├── specs/
│       └── fixtures/
│
├── public/                         # Static files
│   ├── index.html
│   ├── favicon.ico
│   └── manifest.json
│
├── Dockerfile
├── docker-compose.yml
├── package.json
├── tsconfig.json
├── tailwind.config.js
├── jest.config.js
├── .eslintrc.json
└── README.md
```

## 🚀 Getting Started

### Prerequisites
- Node.js 18+
- npm or yarn
- React 18+

### Installation

```bash
# Install dependencies
npm install

# Setup environment
cp .env.example .env

# Start development server
npm start

# Build for production
npm run build

# Run tests
npm test
```

### Development

```bash
# Start with hot reload
npm run dev

# Run linter
npm run lint

# Format code
npm run format

# Type check
npm run type-check
```

## 📊 Key Pages

### 1. Dashboard
Real-time overview of emissions and key metrics
- Current emissions rate
- Historical trends
- Top emitting systems
- Alerts summary

### 2. Facilities
Manage datacenter facilities
- List all facilities
- Add/edit facilities
- View facility details
- Compare facilities

### 3. Emissions
Detailed emissions analytics
- Scope 1, 2, 3 breakdown
- Historical trends
- Comparative analysis
- Forecasting

### 4. Reports
Generate and manage compliance reports
- GRI, TCFD, CDP templates
- Scheduled reporting
- Report history
- Export options

### 5. Goals
Track sustainability targets
- Create and manage goals
- Progress visualization
- Milestone tracking
- Scenario modeling

### 6. Alerts
Manage system alerts
- Alert list and details
- Configure alert rules
- Alert history
- Notification settings

### 7. Settings
User and organization settings
- User profile
- Organization settings
- Integration configuration
- Notification preferences

## 🎨 UI Components

### Available Components
- **Cards**: KPI cards, metric cards
- **Charts**: Line, bar, pie, area charts
- **Tables**: Sortable, filterable tables
- **Forms**: Input fields, dropdowns, date pickers
- **Modals**: Dialog boxes, confirmations
- **Alerts**: Toast notifications, error messages
- **Navigation**: Header, sidebar, breadcrumbs

### Design System
- Color palette: iCarbon brand colors
- Typography: Consistent font hierarchy
- Spacing: 8px grid system
- Shadows: Consistent elevation system
- Icons: Material Design Icons

## 🔄 State Management

### Redux Structure
- Store configuration in `store/store.ts`
- Slices for each domain (facilities, emissions, etc.)
- Selectors for efficient data access
- Thunks for async operations

### Example Usage
```typescript
import { useAppDispatch, useAppSelector } from './store/hooks';
import { facilitiesSelectors } from './store/slices/facilitiesSlice';

function MyComponent() {
  const dispatch = useAppDispatch();
  const facilities = useAppSelector(facilitiesSelectors.selectAll);

  return <div>{facilities.map(f => <div>{f.name}</div>)}</div>;
}
```

## 🔐 Authentication

- OAuth 2.0 / OpenID Connect
- JWT token storage (secure httpOnly cookies)
- Automatic token refresh
- Protected routes with role-based access

## 📡 API Integration

### API Client Setup
```typescript
// Services configured in src/services/api.ts
import { facilitiesApi } from './services/facilitiesApi';

const facilities = await facilitiesApi.list();
```

### Real-Time Updates
- WebSocket connections for live data
- Server-Sent Events for notifications
- Automatic reconnection handling

## 🧪 Testing

```bash
# Unit tests
npm test

# Integration tests
npm run test:integration

# E2E tests
npm run test:e2e

# Coverage report
npm test -- --coverage
```

## 🚀 Deployment

```bash
# Build production bundle
npm run build

# Run production build locally
npm run preview

# Deploy to Vercel
vercel deploy

# Deploy with Docker
docker build -t icarbon-frontend .
docker run -p 3000:3000 icarbon-frontend
```

## 📈 Performance

- Code splitting for faster load
- Image optimization
- Lazy loading of routes
- Memoization of expensive components
- React DevTools Profiler

## ♿ Accessibility

- WCAG 2.1 AA compliance
- Semantic HTML
- ARIA labels
- Keyboard navigation
- Screen reader support

## 🌐 Internationalization

- Multi-language support
- Translation files in `src/locales/`
- Date/time localization
- Currency formatting

## 📝 Code Standards

- ESLint: Code quality
- Prettier: Code formatting
- TypeScript: Type safety
- Husky: Pre-commit hooks

## 🤝 Contributing

1. Create feature branch
2. Follow code standards
3. Write tests
4. Submit PR
5. Pass automated checks

See `../CONTRIBUTING.md` for details.

**Status**: ✅ Active Development
