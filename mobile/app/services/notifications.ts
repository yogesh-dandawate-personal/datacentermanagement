/**
 * Push Notifications Service
 *
 * Handles:
 * - Firebase Cloud Messaging (FCM)
 * - Local notifications
 * - Notification handling (foreground/background)
 * - Badge management
 */

import messaging from '@react-native-firebase/messaging';
import PushNotification, { Importance } from 'react-native-push-notification';
import { Platform } from 'react-native';
import { api } from './api';
import { NOTIFICATION_TYPES } from '../utils/constants';

/**
 * Initialize notifications
 */
export const initNotifications = async (): Promise<void> => {
  // Configure push notification library
  PushNotification.configure({
    // Called when notification is received (foreground)
    onNotification: function (notification) {
      console.log('Notification received:', notification);

      // Display local notification
      if (notification.foreground) {
        showLocalNotification(
          notification.title || 'iNetZero Alert',
          notification.message || ''
        );
      }

      notification.finish(PushNotification.FetchResult.NoData);
    },

    // Called when user taps notification
    onAction: function (notification) {
      console.log('Notification action:', notification.action);
    },

    // Android-specific
    popInitialNotification: true,
    requestPermissions: Platform.OS === 'ios',
  });

  // Create notification channels (Android)
  if (Platform.OS === 'android') {
    PushNotification.createChannel(
      {
        channelId: 'default',
        channelName: 'Default Notifications',
        channelDescription: 'Default notification channel',
        playSound: true,
        soundName: 'default',
        importance: Importance.HIGH,
        vibrate: true,
      },
      (created) => console.log(`Channel created: ${created}`)
    );

    PushNotification.createChannel(
      {
        channelId: 'alarms',
        channelName: 'Alarms & Alerts',
        channelDescription: 'Critical alarms and alerts',
        playSound: true,
        soundName: 'alarm',
        importance: Importance.HIGH,
        vibrate: true,
      },
      (created) => console.log(`Alarms channel created: ${created}`)
    );
  }

  // Register for remote notifications
  await registerForRemoteNotifications();

  // Handle foreground messages
  messaging().onMessage(async (remoteMessage) => {
    console.log('FCM message received (foreground):', remoteMessage);

    if (remoteMessage.notification) {
      showLocalNotification(
        remoteMessage.notification.title || 'iNetZero Alert',
        remoteMessage.notification.body || ''
      );
    }
  });

  // Handle background messages
  messaging().setBackgroundMessageHandler(async (remoteMessage) => {
    console.log('FCM message received (background):', remoteMessage);
  });
};

/**
 * Register for remote notifications
 */
export const registerForRemoteNotifications = async (): Promise<void> => {
  try {
    // Get FCM token
    const token = await messaging().getToken();
    console.log('FCM Token:', token);

    // Register device with backend
    await api.registerDevice(token);

    // Listen for token refresh
    messaging().onTokenRefresh(async (newToken) => {
      console.log('FCM Token refreshed:', newToken);
      await api.registerDevice(newToken);
    });
  } catch (error) {
    console.error('Failed to register for remote notifications:', error);
  }
};

/**
 * Show local notification
 */
export const showLocalNotification = (
  title: string,
  message: string,
  channelId: string = 'default'
): void => {
  PushNotification.localNotification({
    channelId,
    title,
    message,
    playSound: true,
    soundName: 'default',
    importance: 'high',
    vibrate: true,
    vibration: 300,
  });
};

/**
 * Show alarm notification
 */
export const showAlarmNotification = (
  alarmType: string,
  message: string,
  severity: 'critical' | 'warning' | 'info'
): void => {
  const channelId = severity === 'critical' ? 'alarms' : 'default';

  PushNotification.localNotification({
    channelId,
    title: `${severity.toUpperCase()}: ${alarmType}`,
    message,
    playSound: true,
    soundName: severity === 'critical' ? 'alarm' : 'default',
    importance: 'high',
    vibrate: true,
    vibration: severity === 'critical' ? 500 : 300,
    priority: 'high',
  });
};

/**
 * Update badge count
 */
export const updateBadgeCount = (count: number): void => {
  if (Platform.OS === 'ios') {
    PushNotification.setApplicationIconBadgeNumber(count);
  } else {
    // Android badge updates handled by notification library
    console.log('Badge count updated:', count);
  }
};

/**
 * Clear all notifications
 */
export const clearAllNotifications = (): void => {
  PushNotification.cancelAllLocalNotifications();
  updateBadgeCount(0);
};

/**
 * Unregister device
 */
export const unregisterDevice = async (): Promise<void> => {
  try {
    const token = await messaging().getToken();
    await api.unregisterDevice(token);
    console.log('Device unregistered successfully');
  } catch (error) {
    console.error('Failed to unregister device:', error);
  }
};

/**
 * Check notification permissions
 */
export const checkNotificationPermissions = async (): Promise<boolean> => {
  const authStatus = await messaging().requestPermission();
  return (
    authStatus === messaging.AuthorizationStatus.AUTHORIZED ||
    authStatus === messaging.AuthorizationStatus.PROVISIONAL
  );
};
