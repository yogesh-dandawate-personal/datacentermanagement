/**
 * Application Constants
 */

// API Configuration
export const API_CONFIG = {
  BASE_URL: __DEV__
    ? 'http://localhost:8000/api'
    : 'https://api.inetzero.com/api',
  TIMEOUT: 30000, // 30 seconds
  RETRY_ATTEMPTS: 3,
};

// Color Palette
export const COLORS = {
  // Primary Colors
  primary: '#3B82F6', // Blue 500
  primaryDark: '#2563EB', // Blue 600
  primaryLight: '#60A5FA', // Blue 400

  // Secondary Colors
  secondary: '#10B981', // Green 500
  secondaryDark: '#059669', // Green 600
  secondaryLight: '#34D399', // Green 400

  // Semantic Colors
  success: '#10B981', // Green 500
  warning: '#F59E0B', // Amber 500
  error: '#EF4444', // Red 500
  info: '#3B82F6', // Blue 500

  // Neutral Colors
  black: '#000000',
  white: '#FFFFFF',
  gray: '#6B7280', // Gray 500
  grayLight: '#D1D5DB', // Gray 300
  grayDark: '#374151', // Gray 700

  // Dark Mode Colors
  dark: {
    background: '#111827', // Gray 900
    card: '#1F2937', // Gray 800
    text: '#F9FAFB', // Gray 50
    border: '#374151', // Gray 700
  },

  // Light Mode Colors
  light: {
    background: '#F9FAFB', // Gray 50
    card: '#FFFFFF',
    text: '#111827', // Gray 900
    border: '#E5E7EB', // Gray 200
  },
};

// Typography
export const FONTS = {
  regular: 'System',
  medium: 'System',
  bold: 'System',
  sizes: {
    xs: 12,
    sm: 14,
    base: 16,
    lg: 18,
    xl: 20,
    '2xl': 24,
    '3xl': 30,
  },
};

// Spacing
export const SPACING = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
  '2xl': 48,
};

// Border Radius
export const BORDER_RADIUS = {
  sm: 4,
  md: 8,
  lg: 12,
  xl: 16,
  full: 9999,
};

// Shadows
export const SHADOWS = {
  sm: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.18,
    shadowRadius: 1.0,
    elevation: 1,
  },
  md: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.23,
    shadowRadius: 2.62,
    elevation: 4,
  },
  lg: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.30,
    shadowRadius: 4.65,
    elevation: 8,
  },
};

// Animation Durations
export const ANIMATION = {
  fast: 150,
  normal: 200,
  slow: 300,
};

// Storage Keys
export const STORAGE_KEYS = {
  AUTH_TOKEN: '@auth_token',
  REFRESH_TOKEN: '@refresh_token',
  USER_DATA: '@user_data',
  THEME: '@theme',
  OFFLINE_QUEUE: '@offline_queue',
};

// Notification Types
export const NOTIFICATION_TYPES = {
  ENERGY_THRESHOLD: 'energy_threshold',
  EMISSION_ALERT: 'emission_alert',
  SYSTEM_WARNING: 'system_warning',
  DATA_SYNC: 'data_sync',
};

// Sync Configuration
export const SYNC_CONFIG = {
  INTERVAL: 300000, // 5 minutes
  BATCH_SIZE: 50,
  MAX_RETRIES: 3,
  RETRY_DELAY: 5000, // 5 seconds
};

// Chart Colors
export const CHART_COLORS = {
  energy: '#3B82F6', // Blue
  emissions: '#10B981', // Green
  cost: '#F59E0B', // Amber
  target: '#6B7280', // Gray
};

// Date Formats
export const DATE_FORMATS = {
  DISPLAY: 'MMM dd, yyyy',
  DISPLAY_TIME: 'MMM dd, yyyy HH:mm',
  API: 'yyyy-MM-dd',
  TIME: 'HH:mm',
};
