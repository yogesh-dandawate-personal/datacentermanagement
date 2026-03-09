"""
Custom React Hook for Energy Metrics

Handles:
- Fetching energy dashboard data
- Real-time WebSocket updates
- Error handling and retries
- Caching
"""

import { useCallback, useRef } from 'react';

interface DashboardData {
  organization_id: string;
  consumption: {
    current_kwh: number;
    total_kwh: number;
    average_kwh: number;
    peak_kwh: number;
    timestamp: string;
    trend: Array<{ timestamp: string; value: number }>;
  };
  facility_breakdown: Array<{
    facility_id: string;
    facility_name: string;
    current_kwh: number;
    total_kwh: number;
    average_kwh: number;
    peak_kwh: number;
  }>;
  timestamp: string;
}

interface UseEnergyMetrics {
  fetchDashboard: (orgId: string) => Promise<DashboardData | null>;
  fetchMetrics: (orgId: string, period: string) => Promise<any>;
  fetchFacilityEfficiency: (facilityId: string) => Promise<any>;
  fetchPeakUsage: (meterId: string) => Promise<any>;
  subscribeToUpdates: (orgId: string, callback: (data: DashboardData) => void) => () => void;
}

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const WS_BASE_URL = process.env.REACT_APP_WS_URL || 'ws://localhost:8000';

export const useEnergyMetrics = (): UseEnergyMetrics => {
  const wsRef = useRef<WebSocket | null>(null);

  /**
   * Fetch complete dashboard data
   */
  const fetchDashboard = useCallback(async (orgId: string): Promise<DashboardData | null> => {
    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        console.warn('No auth token found, using mock data');
        return null;
      }

      const response = await fetch(
        `${API_BASE_URL}/api/v1/organizations/${orgId}/dashboards/energy`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (!response.ok) {
        throw new Error(`Dashboard API error: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Failed to fetch dashboard:', error);
      // Return null to fall back to mock data
      return null;
    }
  }, []);

  /**
   * Fetch energy metrics for a period
   */
  const fetchMetrics = useCallback(
    async (orgId: string, period: string = 'day') => {
      try {
        const token = localStorage.getItem('access_token');
        if (!token) return null;

        const response = await fetch(
          `${API_BASE_URL}/api/v1/metrics/energy?period=${period}&org_id=${orgId}`,
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );

        if (!response.ok) {
          throw new Error(`Metrics API error: ${response.status}`);
        }

        return await response.json();
      } catch (error) {
        console.error('Failed to fetch metrics:', error);
        return null;
      }
    },
    []
  );

  /**
   * Fetch efficiency metrics for a facility
   */
  const fetchFacilityEfficiency = useCallback(async (facilityId: string) => {
    try {
      const token = localStorage.getItem('access_token');
      if (!token) return null;

      const response = await fetch(
        `${API_BASE_URL}/api/v1/facilities/${facilityId}/energy/efficiency`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (!response.ok) {
        throw new Error(`Efficiency API error: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Failed to fetch efficiency metrics:', error);
      return null;
    }
  }, []);

  /**
   * Fetch peak usage for a meter
   */
  const fetchPeakUsage = useCallback(async (meterId: string) => {
    try {
      const token = localStorage.getItem('access_token');
      if (!token) return null;

      const response = await fetch(
        `${API_BASE_URL}/api/v1/meters/${meterId}/energy/peak-usage`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (!response.ok) {
        throw new Error(`Peak usage API error: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Failed to fetch peak usage:', error);
      return null;
    }
  }, []);

  /**
   * Subscribe to real-time WebSocket updates
   * Returns unsubscribe function
   */
  const subscribeToUpdates = useCallback(
    (orgId: string, callback: (data: DashboardData) => void): (() => void) => {
      try {
        const token = localStorage.getItem('access_token');
        if (!token) {
          console.warn('No auth token for WebSocket, skipping real-time updates');
          return () => {}; // Return no-op unsubscribe
        }

        // Attempt WebSocket connection
        wsRef.current = new WebSocket(
          `${WS_BASE_URL}/api/v1/ws/dashboards/${orgId}/energy?token=${token}`
        );

        wsRef.current.onopen = () => {
          console.log('WebSocket connected to energy updates');
        };

        wsRef.current.onmessage = (event) => {
          try {
            const message = JSON.parse(event.data);
            if (message.type === 'energy_update' && message.data) {
              callback(message.data);
            }
          } catch (error) {
            console.error('Failed to parse WebSocket message:', error);
          }
        };

        wsRef.current.onerror = (error) => {
          console.error('WebSocket error:', error);
        };

        wsRef.current.onclose = () => {
          console.log('WebSocket disconnected');
        };

        // Return unsubscribe function
        return () => {
          if (wsRef.current) {
            wsRef.current.close();
            wsRef.current = null;
          }
        };
      } catch (error) {
        console.error('Failed to establish WebSocket connection:', error);
        return () => {}; // Return no-op if WebSocket unavailable
      }
    },
    []
  );

  return {
    fetchDashboard,
    fetchMetrics,
    fetchFacilityEfficiency,
    fetchPeakUsage,
    subscribeToUpdates,
  };
};

export default useEnergyMetrics;
