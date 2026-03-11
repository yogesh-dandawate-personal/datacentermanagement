/**
 * iNetZero Mobile App
 * Main Application Component
 *
 * Features:
 * - Dark mode support (system/manual)
 * - Redux state management
 * - Navigation setup
 * - Firebase initialization
 * - Offline sync
 */

import React, { useEffect } from 'react';
import {
  StatusBar,
  useColorScheme,
  AppState,
  AppStateStatus,
} from 'react-native';
import { Provider } from 'react-redux';
import { PersistGate } from 'redux-persist/integration/react';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { NavigationContainer } from '@react-navigation/native';
import messaging from '@react-native-firebase/messaging';
import NetInfo from '@react-native-community/netinfo';

import { store, persistor } from './redux/store';
import Navigation from './Navigation';
import { syncOfflineQueue } from './services/sync';
import { initNotifications } from './services/notifications';
import { COLORS } from './utils/constants';

/**
 * Main App Component
 */
function App(): React.JSX.Element {
  const isDarkMode = useColorScheme() === 'dark';
  const backgroundColor = isDarkMode ? COLORS.dark.background : COLORS.light.background;

  useEffect(() => {
    // Initialize Firebase Cloud Messaging
    const initFCM = async () => {
      // Request notification permissions
      const authStatus = await messaging().requestPermission();
      const enabled =
        authStatus === messaging.AuthorizationStatus.AUTHORIZED ||
        authStatus === messaging.AuthorizationStatus.PROVISIONAL;

      if (enabled) {
        console.log('Notification permission granted');

        // Get FCM token
        const token = await messaging().getToken();
        console.log('FCM Token:', token);

        // Initialize notification handlers
        initNotifications();
      } else {
        console.log('Notification permission denied');
      }
    };

    initFCM();

    // Monitor network connectivity
    const unsubscribeNetInfo = NetInfo.addEventListener(state => {
      console.log('Connection type:', state.type);
      console.log('Is connected?', state.isConnected);

      // Sync offline queue when connection restored
      if (state.isConnected) {
        syncOfflineQueue();
      }
    });

    // Handle app state changes (foreground/background)
    const handleAppStateChange = (nextAppState: AppStateStatus) => {
      if (nextAppState === 'active') {
        // App came to foreground - sync data
        syncOfflineQueue();
      } else if (nextAppState === 'background') {
        // App went to background - save state
        console.log('App backgrounded');
      }
    };

    const appStateSubscription = AppState.addEventListener(
      'change',
      handleAppStateChange
    );

    // Cleanup
    return () => {
      unsubscribeNetInfo();
      appStateSubscription.remove();
    };
  }, []);

  return (
    <Provider store={store}>
      <PersistGate loading={null} persistor={persistor}>
        <SafeAreaProvider>
          <NavigationContainer>
            <StatusBar
              barStyle={isDarkMode ? 'light-content' : 'dark-content'}
              backgroundColor={backgroundColor}
            />
            <Navigation />
          </NavigationContainer>
        </SafeAreaProvider>
      </PersistGate>
    </Provider>
  );
}

export default App;
