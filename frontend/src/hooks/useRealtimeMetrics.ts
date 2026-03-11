/**
 * Real-Time Metrics WebSocket Hook
 * SPRINT 10 - AGENT 2: Live Dashboard Updates
 *
 * Features:
 * - WebSocket connection management
 * - Auto-reconnect with exponential backoff
 * - Room subscription management
 * - Metric update streaming
 * - Connection status tracking
 * - Heartbeat/ping mechanism
 */
import { useState, useEffect, useRef, useCallback } from 'react';

interface MetricUpdate {
  type: 'metric_update';
  metric_type: string;
  facility_id: string;
  org_id: string;
  tenant_id: string;
  data: {
    value: number;
    unit: string;
    status: string;
    [key: string]: any;
  };
  timestamp: string;
}

interface ThresholdBreach {
  type: 'threshold_breach';
  breach_type: string;
  severity: 'info' | 'warning' | 'critical';
  facility_id: string;
  org_id: string;
  tenant_id: string;
  data: {
    breach_value: number;
    threshold_value: number;
    message: string;
    [key: string]: any;
  };
  timestamp: string;
}

interface ConnectionMessage {
  type: 'connected' | 'subscribed' | 'unsubscribed' | 'pong' | 'error';
  connection_id?: string;
  room_id?: string;
  message?: string;
  timestamp: string;
}

type WebSocketMessage = MetricUpdate | ThresholdBreach | ConnectionMessage;

interface UseRealtimeMetricsOptions {
  autoConnect?: boolean;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
  heartbeatInterval?: number;
}

interface UseRealtimeMetricsReturn {
  // Connection state
  isConnected: boolean;
  connectionStatus: 'disconnected' | 'connecting' | 'connected' | 'error';
  connectionId: string | null;
  error: string | null;

  // Metric updates
  latestMetrics: Map<string, MetricUpdate>;
  latestBreaches: ThresholdBreach[];

  // Actions
  connect: () => void;
  disconnect: () => void;
  subscribe: (roomId: string) => void;
  unsubscribe: (roomId: string) => void;
  clearMetrics: () => void;
}

/**
 * Custom hook for real-time metric streaming via WebSocket
 *
 * @param options Configuration options
 * @returns WebSocket connection state and controls
 *
 * @example
 * ```tsx
 * const {
 *   isConnected,
 *   latestMetrics,
 *   subscribe,
 * } = useRealtimeMetrics({ autoConnect: true });
 *
 * useEffect(() => {
 *   if (isConnected) {
 *     subscribe('facility:abc-123');
 *     subscribe('metric:energy');
 *   }
 * }, [isConnected]);
 * ```
 */
export function useRealtimeMetrics(
  options: UseRealtimeMetricsOptions = {}
): UseRealtimeMetricsReturn {
  const {
    autoConnect = true,
    reconnectInterval = 3000,
    maxReconnectAttempts = 10,
    heartbeatInterval = 30000,
  } = options;

  // State
  const [isConnected, setIsConnected] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState<
    'disconnected' | 'connecting' | 'connected' | 'error'
  >('disconnected');
  const [connectionId, setConnectionId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [latestMetrics, setLatestMetrics] = useState<Map<string, MetricUpdate>>(new Map());
  const [latestBreaches, setLatestBreaches] = useState<ThresholdBreach[]>([]);

  // Refs for WebSocket and intervals
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const heartbeatIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const subscribedRoomsRef = useRef<Set<string>>(new Set());

  /**
   * Send message to WebSocket
   */
  const sendMessage = useCallback((message: any) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    }
  }, []);

  /**
   * Start heartbeat ping
   */
  const startHeartbeat = useCallback(() => {
    if (heartbeatIntervalRef.current) {
      clearInterval(heartbeatIntervalRef.current);
    }

    heartbeatIntervalRef.current = setInterval(() => {
      sendMessage({ action: 'ping' });
    }, heartbeatInterval);
  }, [heartbeatInterval, sendMessage]);

  /**
   * Stop heartbeat ping
   */
  const stopHeartbeat = useCallback(() => {
    if (heartbeatIntervalRef.current) {
      clearInterval(heartbeatIntervalRef.current);
      heartbeatIntervalRef.current = null;
    }
  }, []);

  /**
   * Handle incoming WebSocket message
   */
  const handleMessage = useCallback((event: MessageEvent) => {
    try {
      const message: WebSocketMessage = JSON.parse(event.data);

      switch (message.type) {
        case 'connected':
          setConnectionId(message.connection_id || null);
          setIsConnected(true);
          setConnectionStatus('connected');
          setError(null);
          reconnectAttemptsRef.current = 0;
          console.log('WebSocket connected:', message.connection_id);
          break;

        case 'metric_update':
          // Store metric update with key: metric_type:facility_id
          const metricKey = `${message.metric_type}:${message.facility_id}`;
          setLatestMetrics((prev) => {
            const newMap = new Map(prev);
            newMap.set(metricKey, message);
            return newMap;
          });
          break;

        case 'threshold_breach':
          // Add breach to list (keep last 50)
          setLatestBreaches((prev) => {
            const newBreaches = [message, ...prev].slice(0, 50);
            return newBreaches;
          });
          break;

        case 'subscribed':
          console.log('Subscribed to room:', message.room_id);
          break;

        case 'unsubscribed':
          console.log('Unsubscribed from room:', message.room_id);
          break;

        case 'pong':
          // Heartbeat acknowledged
          break;

        case 'error':
          console.error('WebSocket error message:', message.message);
          setError(message.message || 'Unknown error');
          break;

        default:
          console.warn('Unknown message type:', message);
      }
    } catch (err) {
      console.error('Error parsing WebSocket message:', err);
    }
  }, []);

  /**
   * Connect to WebSocket
   */
  const connect = useCallback(() => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      console.log('WebSocket already connected');
      return;
    }

    setConnectionStatus('connecting');
    setError(null);

    const token = localStorage.getItem('token');
    if (!token) {
      setError('No authentication token found');
      setConnectionStatus('error');
      return;
    }

    const wsUrl = `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${
      window.location.host
    }/api/v1/ws?token=${token}`;

    try {
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log('WebSocket connection established');
        startHeartbeat();

        // Re-subscribe to previously subscribed rooms
        subscribedRoomsRef.current.forEach((roomId) => {
          sendMessage({ action: 'subscribe', room_id: roomId });
        });
      };

      ws.onmessage = handleMessage;

      ws.onerror = (event) => {
        console.error('WebSocket error:', event);
        setError('WebSocket connection error');
        setConnectionStatus('error');
      };

      ws.onclose = (event) => {
        console.log('WebSocket closed:', event.code, event.reason);
        setIsConnected(false);
        setConnectionStatus('disconnected');
        stopHeartbeat();

        // Auto-reconnect with exponential backoff
        if (reconnectAttemptsRef.current < maxReconnectAttempts) {
          reconnectAttemptsRef.current += 1;
          const delay = Math.min(
            reconnectInterval * Math.pow(2, reconnectAttemptsRef.current - 1),
            30000
          );

          console.log(
            `Reconnecting in ${delay}ms (attempt ${reconnectAttemptsRef.current}/${maxReconnectAttempts})`
          );

          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, delay);
        } else {
          setError('Max reconnection attempts reached');
          setConnectionStatus('error');
        }
      };
    } catch (err) {
      console.error('Error creating WebSocket:', err);
      setError('Failed to create WebSocket connection');
      setConnectionStatus('error');
    }
  }, [
    handleMessage,
    maxReconnectAttempts,
    reconnectInterval,
    sendMessage,
    startHeartbeat,
    stopHeartbeat,
  ]);

  /**
   * Disconnect from WebSocket
   */
  const disconnect = useCallback(() => {
    if (wsRef.current) {
      stopHeartbeat();
      wsRef.current.close();
      wsRef.current = null;
    }

    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    setIsConnected(false);
    setConnectionStatus('disconnected');
    setConnectionId(null);
    subscribedRoomsRef.current.clear();
  }, [stopHeartbeat]);

  /**
   * Subscribe to a room
   */
  const subscribe = useCallback(
    (roomId: string) => {
      subscribedRoomsRef.current.add(roomId);
      sendMessage({ action: 'subscribe', room_id: roomId });
    },
    [sendMessage]
  );

  /**
   * Unsubscribe from a room
   */
  const unsubscribe = useCallback(
    (roomId: string) => {
      subscribedRoomsRef.current.delete(roomId);
      sendMessage({ action: 'unsubscribe', room_id: roomId });
    },
    [sendMessage]
  );

  /**
   * Clear all metrics
   */
  const clearMetrics = useCallback(() => {
    setLatestMetrics(new Map());
    setLatestBreaches([]);
  }, []);

  // Auto-connect on mount
  useEffect(() => {
    if (autoConnect) {
      connect();
    }

    return () => {
      disconnect();
    };
  }, [autoConnect]); // Only run on mount

  return {
    isConnected,
    connectionStatus,
    connectionId,
    error,
    latestMetrics,
    latestBreaches,
    connect,
    disconnect,
    subscribe,
    unsubscribe,
    clearMetrics,
  };
}
