/**
 * API Service
 *
 * Centralized API client with:
 * - Axios instance
 * - Token management
 * - Request/response interceptors
 * - Automatic retry logic
 * - Offline queue integration
 */

import axios, { AxiosInstance, AxiosError, AxiosRequestConfig } from 'axios';
import NetInfo from '@react-native-community/netinfo';
import { store } from '../redux/store';
import { updateToken, logout } from '../redux/slices/authSlice';
import { addToQueue } from '../redux/slices/offlineSlice';
import { API_CONFIG } from '../utils/constants';

/**
 * Create Axios instance
 */
const apiClient: AxiosInstance = axios.create({
  baseURL: API_CONFIG.BASE_URL,
  timeout: API_CONFIG.TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Request Interceptor
 * Adds auth token to all requests
 */
apiClient.interceptors.request.use(
  async (config) => {
    const state = store.getState();
    const token = state.auth.token;

    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
  },
  (error) => Promise.reject(error)
);

/**
 * Response Interceptor
 * Handles token refresh and offline queueing
 */
apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as AxiosRequestConfig & {
      _retry?: boolean;
    };

    // Handle 401 Unauthorized (token expired)
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const state = store.getState();
        const refreshToken = state.auth.refreshToken;

        if (!refreshToken) {
          store.dispatch(logout());
          return Promise.reject(error);
        }

        // Refresh token
        const response = await axios.post(
          `${API_CONFIG.BASE_URL}/auth/refresh`,
          { refresh_token: refreshToken }
        );

        const newToken = response.data.access_token;
        store.dispatch(updateToken(newToken));

        // Retry original request with new token
        if (originalRequest.headers) {
          originalRequest.headers.Authorization = `Bearer ${newToken}`;
        }
        return apiClient(originalRequest);
      } catch (refreshError) {
        // Refresh failed - logout user
        store.dispatch(logout());
        return Promise.reject(refreshError);
      }
    }

    // Handle network errors - queue request for offline sync
    if (!error.response) {
      const netInfo = await NetInfo.fetch();
      if (!netInfo.isConnected) {
        const queuedAction = {
          id: Date.now().toString(),
          type: 'API_REQUEST',
          payload: {
            method: originalRequest.method,
            url: originalRequest.url,
            data: originalRequest.data,
            params: originalRequest.params,
          },
          timestamp: new Date().toISOString(),
          retries: 0,
        };

        store.dispatch(addToQueue(queuedAction));
        console.log('Request queued for offline sync:', queuedAction);
      }
    }

    return Promise.reject(error);
  }
);

/**
 * API Methods
 */

export const api = {
  // Auth
  login: (email: string, password: string) =>
    apiClient.post('/auth/login', { email, password }),

  logout: () => apiClient.post('/auth/logout'),

  refreshToken: (refreshToken: string) =>
    apiClient.post('/auth/refresh', { refresh_token: refreshToken }),

  // Energy Metrics
  getEnergyMetrics: (facilityId: string, startDate: string, endDate: string) =>
    apiClient.get('/energy/metrics', {
      params: { facility_id: facilityId, start_date: startDate, end_date: endDate },
    }),

  getEnergyTrends: (facilityId: string) =>
    apiClient.get(`/energy/trends/${facilityId}`),

  // Emissions
  getEmissions: (facilityId: string, startDate: string, endDate: string) =>
    apiClient.get('/emissions', {
      params: { facility_id: facilityId, start_date: startDate, end_date: endDate },
    }),

  getEmissionsSummary: (facilityId: string) =>
    apiClient.get(`/emissions/summary/${facilityId}`),

  // Dashboard
  getDashboardSummary: (facilityId: string) =>
    apiClient.get(`/dashboard/summary/${facilityId}`),

  // Alarms
  getAlarms: (facilityId: string) =>
    apiClient.get(`/alarms/${facilityId}`),

  acknowledgeAlarm: (alarmId: string) =>
    apiClient.post(`/alarms/${alarmId}/acknowledge`),

  // User Profile
  getUserProfile: () => apiClient.get('/users/me'),

  updateUserProfile: (data: any) => apiClient.put('/users/me', data),

  // Notifications
  registerDevice: (fcmToken: string) =>
    apiClient.post('/notifications/register', { fcm_token: fcmToken }),

  unregisterDevice: (fcmToken: string) =>
    apiClient.post('/notifications/unregister', { fcm_token: fcmToken }),
};

export default apiClient;
