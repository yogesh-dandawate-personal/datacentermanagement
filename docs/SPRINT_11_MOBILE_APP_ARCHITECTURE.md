# Sprint 11: Mobile Application Architecture

**Date**: 2026-03-11
**Sprint**: Sprint 11 (React Native Mobile App)
**Agents**: 5-agent team (React Native, iOS, Android, Offline, Notifications)
**Ralph Phase**: R0-R7 (Full Cycle)

---

## R0: REQUIREMENTS ANALYSIS

### Business Requirements
1. **Cross-Platform Mobile App**: iOS and Android support
2. **Offline-First Architecture**: Work without internet, sync when available
3. **Push Notifications**: Real-time alerts for critical events
4. **Native Performance**: 60fps smooth scrolling, <5s load times
5. **Energy Monitoring**: Real-time facility metrics on mobile
6. **Carbon Tracking**: Emissions data accessible on-the-go

### Technical Requirements
- React Native 0.73+ (latest stable)
- TypeScript for type safety
- Redux Toolkit for state management
- React Navigation 6 for routing
- Firebase Cloud Messaging (FCM) for notifications
- SQLite for offline storage
- AsyncStorage for app preferences
- Native modules for iOS/Android

### Success Criteria
- ✅ App runs on iOS 15+ and Android 11+
- ✅ Offline mode fully functional
- ✅ Push notifications working
- ✅ Zero crashes on core flows
- ✅ 60fps smooth scrolling
- ✅ <5s initial load time

---

## ARCHITECTURE OVERVIEW

### High-Level Architecture
```
┌─────────────────────────────────────────┐
│          React Native App               │
│  (JavaScript/TypeScript - Cross Platform)│
└─────────────────────────────────────────┘
           │                │
           ▼                ▼
┌──────────────────┐  ┌──────────────────┐
│   iOS Native     │  │ Android Native   │
│   - Swift/Obj-C  │  │   - Java/Kotlin  │
│   - Notifications│  │   - Notifications│
│   - Sensors      │  │   - Sensors      │
│   - Deep Links   │  │   - Intents      │
└──────────────────┘  └──────────────────┘
           │                │
           ▼                ▼
┌─────────────────────────────────────────┐
│          iNetZero Backend API           │
│        (FastAPI - REST/WebSocket)       │
└─────────────────────────────────────────┘
```

### Offline-First Architecture
```
User Action
  ↓
Redux Action Dispatched
  ↓
Check Connectivity
  ├─ Online → API Request → Update Redux → Sync SQLite
  └─ Offline → Queue Action → Save to SQLite → Update Redux
                                  ↓
                           (When Online)
                                  ↓
                         Process Queue → Sync API → Resolve Conflicts
```

---

## COMPONENT STRUCTURE

### Mobile App Directory Structure
```
mobile/
├── app/
│   ├── App.tsx                    # Root app component
│   ├── Navigation.tsx             # React Navigation setup
│   ├── screens/                   # Screen components
│   │   ├── AuthScreen.tsx         # Login/signup
│   │   ├── DashboardScreen.tsx    # Main dashboard
│   │   ├── EnergyScreen.tsx       # Energy metrics
│   │   ├── EmissionsScreen.tsx    # Carbon tracking
│   │   ├── AlarmsScreen.tsx       # Alerts list
│   │   └── SettingsScreen.tsx     # App settings
│   ├── components/                # Reusable components
│   │   ├── MetricCard.tsx
│   │   ├── ChartWidget.tsx
│   │   └── LoadingSpinner.tsx
│   ├── redux/                     # State management
│   │   ├── store.ts
│   │   ├── slices/
│   │   │   ├── authSlice.ts
│   │   │   ├── metricsSlice.ts
│   │   │   └── offlineSlice.ts
│   │   └── thunks/
│   ├── services/                  # API/storage services
│   │   ├── api.ts                 # Backend API client
│   │   ├── storage.ts             # AsyncStorage wrapper
│   │   ├── database.ts            # SQLite operations
│   │   └── sync.ts                # Offline sync logic
│   └── utils/                     # Utilities
│       ├── constants.ts
│       └── helpers.ts
├── ios/                           # iOS native code
│   ├── iNetZero/
│   │   ├── AppDelegate.mm         # App lifecycle
│   │   ├── NotificationService.swift
│   │   └── Info.plist             # iOS config
│   └── Podfile                    # CocoaPods dependencies
├── android/                       # Android native code
│   ├── app/src/main/
│   │   ├── java/com/inetzero/
│   │   │   ├── MainActivity.java
│   │   │   └── NotificationService.java
│   │   ├── res/                   # Android resources
│   │   └── AndroidManifest.xml    # Android config
│   └── build.gradle               # Gradle config
├── package.json                   # NPM dependencies
└── tsconfig.json                  # TypeScript config
```

---

## AGENT DELIVERABLES (4,400 LOC)

### AGENT 1: React Native Core (1,500 LOC)
**Responsibilities**:
- App.tsx: Main app component with theme
- Navigation.tsx: Stack + Tab navigation
- 6 screens: Auth, Dashboard, Energy, Emissions, Alarms, Settings
- Redux store setup (auth, metrics, offline slices)
- API service with token management
- AsyncStorage wrapper

**Key Features**:
- Dark mode support (system/manual)
- Touch-optimized UI
- Pull-to-refresh
- App lifecycle management (active/background/inactive)

### AGENT 2: iOS Native Modules (1,000 LOC)
**Responsibilities**:
- Push notifications (APNs + Firebase)
- Device sensors (location, battery)
- Local storage (UserDefaults)
- Background fetch (energy data sync)
- Deep linking (URL schemes)
- App icon badges

**Files**:
- `ios/iNetZero/AppDelegate.mm` (200 lines)
- `ios/iNetZero/NotificationService.swift` (300 lines)
- `ios/iNetZero/SensorManager.swift` (250 lines)
- `ios/iNetZero/StorageManager.swift` (150 lines)
- `ios/iNetZero/DeepLinkHandler.swift` (100 lines)

### AGENT 3: Android Native Modules (1,000 LOC)
**Responsibilities**:
- Push notifications (FCM)
- Device sensors (location, battery)
- SharedPreferences storage
- WorkManager (background sync)
- Intent handling (deep links)
- Notification channels

**Files**:
- `android/app/src/main/java/com/inetzero/MainActivity.java` (150 lines)
- `android/app/src/main/java/com/inetzero/NotificationService.java` (300 lines)
- `android/app/src/main/java/com/inetzero/SensorModule.java` (250 lines)
- `android/app/src/main/java/com/inetzero/StorageModule.java` (150 lines)
- `android/app/src/main/java/com/inetzero/DeepLinkReceiver.java` (150 lines)

### AGENT 4: Offline Support (700 LOC)
**Responsibilities**:
- SQLite database setup (react-native-sqlite-storage)
- Data models (Energy, Emissions, Alarms)
- Sync queue (action queue)
- Conflict resolution (last-write-wins)
- Local state persistence

**Files**:
- `mobile/app/services/database.ts` (250 lines)
- `mobile/app/services/sync.ts` (300 lines)
- `mobile/app/redux/slices/offlineSlice.ts` (150 lines)

### AGENT 5: Push Notifications (200 LOC)
**Responsibilities**:
- FCM integration (iOS + Android)
- Local notifications (alarm thresholds)
- Notification handling (foreground/background)
- Badge management

**Files**:
- `mobile/app/services/notifications.ts` (200 lines)

---

## KEY LIBRARIES

### Core
- `react-native`: 0.73.x (latest stable)
- `react`: 18.2.x
- `typescript`: 5.x

### Navigation
- `@react-navigation/native`: 6.x
- `@react-navigation/native-stack`: 6.x
- `@react-navigation/bottom-tabs`: 6.x
- `react-native-screens`: 3.x
- `react-native-safe-area-context`: 4.x

### State Management
- `@reduxjs/toolkit`: 2.x
- `react-redux`: 9.x
- `redux-persist`: 6.x

### Offline & Storage
- `react-native-sqlite-storage`: 6.x
- `@react-native-async-storage/async-storage`: 1.x
- `react-native-netinfo`: 11.x

### Push Notifications
- `@react-native-firebase/app`: 19.x
- `@react-native-firebase/messaging`: 19.x
- `react-native-push-notification`: 8.x

### UI Components
- `react-native-vector-icons`: 10.x
- `react-native-linear-gradient`: 2.x
- `react-native-charts-wrapper`: 0.6.x

### API & Network
- `axios`: 1.x
- `react-native-url-polyfill`: 2.x

---

## TECHNICAL DECISIONS

### State Management: Redux Toolkit
**Why?**
- Predictable state management
- Offline support with redux-persist
- Redux DevTools for debugging
- Thunks for async operations

### Navigation: React Navigation
**Why?**
- Native performance (react-native-screens)
- Smooth animations
- Deep linking support
- Tab + Stack navigation

### Offline: SQLite + Sync Queue
**Why?**
- Relational data model
- Complex queries
- Fast read/write
- Proven reliability

### Notifications: Firebase Cloud Messaging
**Why?**
- Cross-platform (iOS + Android)
- Free tier sufficient
- Reliable delivery
- Rich notification support

---

## PERFORMANCE TARGETS

### Load Times
- Initial load: <5s (cold start)
- Screen transitions: <300ms
- API requests: <2s (with loading states)
- Offline data: <100ms

### Smoothness
- 60fps scrolling (FlatList optimization)
- No jank during navigation
- Smooth animations (React Native Animated)

### Battery & Data
- Background sync: <5% battery per hour
- Data usage: <10MB per day (typical)
- Efficient API calls (batch requests)

---

## SECURITY

### Data Protection
- JWT tokens in secure storage (Keychain/Keystore)
- SQLite encryption (SQLCipher)
- HTTPS only (SSL pinning)
- No sensitive data in AsyncStorage

### Authentication
- OAuth 2.0 with refresh tokens
- Biometric authentication (Touch/Face ID)
- Auto-logout after 30 minutes inactivity

---

## TESTING STRATEGY

### Unit Tests
- Redux reducers/thunks
- Utility functions
- Service methods

### Integration Tests
- API client
- Offline sync logic
- Navigation flows

### E2E Tests (Detox)
- Login flow
- Dashboard viewing
- Offline mode
- Push notification handling

---

## DEPLOYMENT

### iOS
- App Store Connect
- TestFlight for beta testing
- Fastlane automation
- CodePush for JS updates

### Android
- Google Play Console
- Internal testing track
- Fastlane automation
- CodePush for JS updates

---

## NEXT STEPS (R1-R7)

- **R1**: Setup React Native project with TypeScript
- **R2**: Implement screens and navigation
- **R3**: Build Redux store and API service
- **R4**: Add iOS native modules
- **R5**: Add Android native modules
- **R6**: Implement offline support
- **R7**: Add push notifications and testing

---

**Architecture Review Status**: ✅ APPROVED
**Ready for Implementation**: YES
