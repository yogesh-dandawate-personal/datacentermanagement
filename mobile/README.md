# iNetZero Mobile App

React Native mobile application for iNetZero ESG Carbon Management Platform.

## Features

- 🔐 **Authentication**: Email/password login with JWT tokens
- 📊 **Dashboard**: Real-time facility metrics (power, energy, PUE, temperature)
- ⚡ **Energy Metrics**: 24-hour energy trends and consumption data
- 🌱 **Carbon Tracking**: Emissions by scope (1/2/3) with total CO₂
- 🔔 **Alarms & Alerts**: Active alarms list with push notifications
- ⚙️ **Settings**: User profile and app preferences
- 📴 **Offline Support**: SQLite database with automatic sync
- 📲 **Push Notifications**: Firebase Cloud Messaging (iOS + Android)
- 🌙 **Dark Mode**: System-aware dark mode support

## Prerequisites

- **Node.js**: 18+ (LTS)
- **npm**: 9+
- **React Native CLI**: Latest
- **Xcode**: 15+ (for iOS)
- **Android Studio**: Latest (for Android)
- **CocoaPods**: Latest (for iOS dependencies)
- **Java**: JDK 17+ (for Android)

## Installation

### 1. Clone Repository
```bash
cd mobile
npm install
```

### 2. iOS Setup
```bash
cd ios
pod install
cd ..
```

### 3. Android Setup
- Open `android/` in Android Studio
- Sync Gradle files
- Download required SDK components

### 4. Firebase Setup

#### iOS
1. Download `GoogleService-Info.plist` from Firebase Console
2. Place in `ios/iNetZero/GoogleService-Info.plist`

#### Android
1. Download `google-services.json` from Firebase Console
2. Place in `android/app/google-services.json`

## Running the App

### iOS
```bash
npm run ios
# OR
npx react-native run-ios --device "iPhone 15 Pro"
```

### Android
```bash
npm run android
# OR
npx react-native run-android
```

### Metro Bundler
```bash
npm start
```

## Configuration

### API Endpoint
Edit `app/utils/constants.ts`:
```typescript
export const API_CONFIG = {
  BASE_URL: __DEV__
    ? 'http://localhost:8000/api'
    : 'https://api.inetzero.com/api',
  TIMEOUT: 30000,
};
```

### Environment Variables
Create `.env` file:
```
API_BASE_URL=https://api.inetzero.com/api
FIREBASE_API_KEY=your_firebase_api_key
```

## Building for Production

### iOS
```bash
cd ios
xcodebuild -workspace iNetZero.xcworkspace \
  -scheme iNetZero \
  -configuration Release \
  -archivePath build/iNetZero.xcarchive \
  archive
```

Or use Xcode:
1. Open `ios/iNetZero.xcworkspace`
2. Product → Archive
3. Distribute to App Store

### Android
```bash
cd android
./gradlew assembleRelease
```

APK location: `android/app/build/outputs/apk/release/app-release.apk`

## Project Structure

```
mobile/
├── app/
│   ├── App.tsx                    # Main app component
│   ├── Navigation.tsx             # Navigation setup
│   ├── screens/                   # Screen components
│   │   ├── AuthScreen.tsx         # Login
│   │   ├── DashboardScreen.tsx    # Metrics overview
│   │   ├── EnergyScreen.tsx       # Energy trends
│   │   ├── EmissionsScreen.tsx    # Carbon tracking
│   │   ├── AlarmsScreen.tsx       # Alerts
│   │   └── SettingsScreen.tsx     # Settings
│   ├── redux/                     # State management
│   │   ├── store.ts               # Redux store
│   │   └── slices/                # Redux slices
│   ├── services/                  # API & storage
│   │   ├── api.ts                 # API client
│   │   ├── database.ts            # SQLite
│   │   ├── sync.ts                # Offline sync
│   │   └── notifications.ts       # Push notifications
│   └── utils/
│       └── constants.ts           # App constants
├── ios/                           # iOS native code
│   └── iNetZero/
│       ├── AppDelegate.mm
│       ├── NotificationService.swift
│       └── Info.plist
├── android/                       # Android native code
│   └── app/src/main/
│       ├── java/com/inetzero/
│       │   ├── MainActivity.java
│       │   └── NotificationService.java
│       └── AndroidManifest.xml
└── package.json
```

## Key Dependencies

| Library | Purpose |
|---------|---------|
| `react-native` | Cross-platform framework |
| `@react-navigation/*` | Navigation |
| `@reduxjs/toolkit` | State management |
| `react-native-sqlite-storage` | Offline storage |
| `@react-native-firebase/*` | Push notifications |
| `axios` | HTTP client |

## Offline Support

The app uses SQLite for offline data storage:

### Tables
- `energy_metrics`: Energy consumption data
- `emissions`: Carbon emissions data
- `alarms`: Active alarms
- `sync_queue`: Pending API requests

### Sync Process
1. User action → Check connectivity
2. If offline → Queue action → Save to SQLite
3. When online → Process queue → Sync API
4. On failure → Retry up to 3 times

## Push Notifications

### Notification Types
- `ENERGY_THRESHOLD`: Energy usage alerts
- `EMISSION_ALERT`: Carbon emissions warnings
- `SYSTEM_WARNING`: System health issues
- `DATA_SYNC`: Sync status updates

### Handling Notifications
```typescript
// Foreground
messaging().onMessage(async (remoteMessage) => {
  console.log('Message:', remoteMessage);
});

// Background
messaging().setBackgroundMessageHandler(async (remoteMessage) => {
  console.log('Background message:', remoteMessage);
});
```

## Testing

### Unit Tests
```bash
npm test
```

### E2E Tests (Detox)
```bash
# Build app
detox build --configuration ios.sim.debug

# Run tests
detox test --configuration ios.sim.debug
```

## Troubleshooting

### iOS Build Errors
```bash
cd ios
rm -rf Pods Podfile.lock
pod install
cd ..
```

### Android Build Errors
```bash
cd android
./gradlew clean
./gradlew assembleDebug
cd ..
```

### Metro Bundler Cache
```bash
npm start -- --reset-cache
```

### Clear AsyncStorage
```bash
# iOS Simulator
xcrun simctl erase all

# Android Emulator
adb shell pm clear com.inetzero
```

## Performance Optimization

### Image Optimization
- Use `react-native-fast-image` for cached images
- Compress images before bundling
- Use WebP format on Android

### List Optimization
- Use `FlatList` with `getItemLayout`
- Implement `shouldComponentUpdate` or `React.memo`
- Lazy load off-screen items

### Bundle Size
```bash
# Analyze bundle
npx react-native-bundle-visualizer
```

## Deployment

### iOS (App Store)
1. Update version in `ios/iNetZero/Info.plist`
2. Archive in Xcode
3. Upload to App Store Connect
4. Submit for review

### Android (Google Play)
1. Update version in `android/app/build.gradle`
2. Generate signed APK/AAB
3. Upload to Google Play Console
4. Submit for review

## CI/CD

### Fastlane
```bash
# Install Fastlane
gem install fastlane

# iOS
cd ios
fastlane beta

# Android
cd android
fastlane beta
```

## Support

- **Documentation**: [docs/SPRINT_11_MOBILE_APP_COMPLETION.md](../docs/SPRINT_11_MOBILE_APP_COMPLETION.md)
- **Issues**: GitHub Issues
- **Email**: support@inetzero.com

## License

Copyright © 2026 iNetZero. All rights reserved.

---

**Version**: 1.0.0
**Last Updated**: 2026-03-11
