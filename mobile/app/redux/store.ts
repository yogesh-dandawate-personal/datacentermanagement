/**
 * Redux Store Configuration
 *
 * Features:
 * - Redux Toolkit
 * - Redux Persist (AsyncStorage)
 * - TypeScript types
 */

import { configureStore } from '@reduxjs/toolkit';
import {
  persistStore,
  persistReducer,
  FLUSH,
  REHYDRATE,
  PAUSE,
  PERSIST,
  PURGE,
  REGISTER,
} from 'redux-persist';
import AsyncStorage from '@react-native-async-storage/async-storage';

import authReducer from './slices/authSlice';
import metricsReducer from './slices/metricsSlice';
import offlineReducer from './slices/offlineSlice';

// Persist configurations
const authPersistConfig = {
  key: 'auth',
  storage: AsyncStorage,
  whitelist: ['token', 'refreshToken', 'user', 'isAuthenticated'],
};

const metricsPersistConfig = {
  key: 'metrics',
  storage: AsyncStorage,
  whitelist: ['cachedData'],
};

const offlinePersistConfig = {
  key: 'offline',
  storage: AsyncStorage,
  whitelist: ['queue'],
};

// Create persisted reducers
const persistedAuthReducer = persistReducer(authPersistConfig, authReducer);
const persistedMetricsReducer = persistReducer(metricsPersistConfig, metricsReducer);
const persistedOfflineReducer = persistReducer(offlinePersistConfig, offlineReducer);

// Configure store
export const store = configureStore({
  reducer: {
    auth: persistedAuthReducer,
    metrics: persistedMetricsReducer,
    offline: persistedOfflineReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: [FLUSH, REHYDRATE, PAUSE, PERSIST, PURGE, REGISTER],
      },
    }),
});

// Create persistor
export const persistor = persistStore(store);

// Export types
export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
