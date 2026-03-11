/**
 * Live Monitoring Dashboard Page
 * SPRINT 10 - AGENT 2: Complete Live Dashboard
 *
 * Features:
 * - Real-time metric streaming
 * - Live charts
 * - Threshold breach alerts
 * - Connection status indicator
 */
import React, { useState, useEffect } from 'react';
import { useRealtimeMetrics } from '../hooks/useRealtimeMetrics';
import { LiveMetricCard } from '../components/LiveMetricCard';
import { LiveChart } from '../components/LiveChart';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Alert } from '../components/ui/Alert';
import { Button } from '../components/ui/Button';

interface ChartDataPoint {
  timestamp: string;
  value: number;
}

export const LiveMonitoring: React.FC = () => {
  const {
    isConnected,
    connectionStatus,
    error,
    latestMetrics,
    latestBreaches,
    subscribe,
    unsubscribe,
    clearMetrics,
  } = useRealtimeMetrics({ autoConnect: true });

  const [chartData, setChartData] = useState<Map<string, ChartDataPoint[]>>(new Map());
  const [selectedFacility, setSelectedFacility] = useState<string>('facility-1');

  // Subscribe to rooms on connection
  useEffect(() => {
    if (isConnected) {
      subscribe(`facility:${selectedFacility}`);
      subscribe('metric:energy');
      subscribe('metric:carbon');
      subscribe('metric:water');
      subscribe(`alerts:${selectedFacility}`);
    }

    return () => {
      if (isConnected) {
        unsubscribe(`facility:${selectedFacility}`);
        unsubscribe('metric:energy');
        unsubscribe('metric:carbon');
        unsubscribe('metric:water');
        unsubscribe(`alerts:${selectedFacility}`);
      }
    };
  }, [isConnected, selectedFacility, subscribe, unsubscribe]);

  // Update chart data when metrics arrive
  useEffect(() => {
    latestMetrics.forEach((metric, key) => {
      const dataPoint: ChartDataPoint = {
        timestamp: metric.timestamp,
        value: metric.data.value,
      };

      setChartData((prev) => {
        const newData = new Map(prev);
        const existing = newData.get(key) || [];
        newData.set(key, [...existing, dataPoint].slice(-50)); // Keep last 50 points
        return newData;
      });
    });
  }, [latestMetrics]);

  const getConnectionStatusBadge = () => {
    switch (connectionStatus) {
      case 'connected':
        return <Badge variant="success">Connected</Badge>;
      case 'connecting':
        return <Badge variant="warning">Connecting...</Badge>;
      case 'disconnected':
        return <Badge variant="secondary">Disconnected</Badge>;
      case 'error':
        return <Badge variant="danger">Error</Badge>;
      default:
        return <Badge variant="secondary">Unknown</Badge>;
    }
  };

  // Extract metrics by type
  const energyMetric = Array.from(latestMetrics.values()).find(
    (m) => m.metric_type === 'energy'
  );
  const carbonMetric = Array.from(latestMetrics.values()).find(
    (m) => m.metric_type === 'carbon'
  );
  const waterMetric = Array.from(latestMetrics.values()).find(
    (m) => m.metric_type === 'water'
  );

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Live Monitoring</h1>
            <p className="text-gray-600 mt-1">Real-time facility metrics and alerts</p>
          </div>
          <div className="flex items-center space-x-4">
            {getConnectionStatusBadge()}
            <Button onClick={clearMetrics} variant="outline" size="sm">
              Clear Data
            </Button>
          </div>
        </div>
      </div>

      {/* Error Alert */}
      {error && (
        <Alert variant="danger" className="mb-6">
          <p className="font-semibold">Connection Error</p>
          <p className="text-sm mt-1">{error}</p>
        </Alert>
      )}

      {/* Facility Selector */}
      <Card className="mb-6">
        <div className="p-4">
          <label className="text-sm font-medium text-gray-700 mb-2 block">
            Select Facility
          </label>
          <select
            value={selectedFacility}
            onChange={(e) => setSelectedFacility(e.target.value)}
            className="w-full md:w-64 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="facility-1">Data Center 1 - NYC</option>
            <option value="facility-2">Data Center 2 - SF</option>
            <option value="facility-3">Data Center 3 - London</option>
          </select>
        </div>
      </Card>

      {/* Live Metric Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
        <LiveMetricCard
          title="Energy Consumption"
          metric_type="energy"
          value={energyMetric?.data.value || 0}
          unit="kWh"
          status={energyMetric?.data.status || 'normal'}
          lastUpdated={energyMetric?.timestamp}
          icon={
            <svg
              className="w-6 h-6"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M13 10V3L4 14h7v7l9-11h-7z"
              />
            </svg>
          }
          isLive={isConnected}
        />

        <LiveMetricCard
          title="Carbon Emissions"
          metric_type="carbon"
          value={carbonMetric?.data.value || 0}
          unit="kg CO2e"
          status={carbonMetric?.data.status || 'normal'}
          lastUpdated={carbonMetric?.timestamp}
          icon={
            <svg
              className="w-6 h-6"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
          }
          isLive={isConnected}
        />

        <LiveMetricCard
          title="Water Usage"
          metric_type="water"
          value={waterMetric?.data.value || 0}
          unit="L"
          status={waterMetric?.data.status || 'normal'}
          lastUpdated={waterMetric?.timestamp}
          icon={
            <svg
              className="w-6 h-6"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M3 6l3 1m0 0l-3 9a5.002 5.002 0 006.001 0M6 7l3 9M6 7l6-2m6 2l3-1m-3 1l-3 9a5.002 5.002 0 006.001 0M18 7l3 9m-3-9l-6-2m0-2v2m0 16V5m0 16H9m3 0h3"
              />
            </svg>
          }
          isLive={isConnected}
        />
      </div>

      {/* Live Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <Card>
          <div className="p-6 h-96">
            <LiveChart
              data={
                chartData.get(`energy:${selectedFacility}`)?.map((d) => ({
                  timestamp: d.timestamp,
                  value: d.value,
                })) || []
              }
              title="Energy Consumption Trend"
              yAxisLabel="kWh"
              color="#3b82f6"
            />
          </div>
        </Card>

        <Card>
          <div className="p-6 h-96">
            <LiveChart
              data={
                chartData.get(`carbon:${selectedFacility}`)?.map((d) => ({
                  timestamp: d.timestamp,
                  value: d.value,
                })) || []
              }
              title="Carbon Emissions Trend"
              yAxisLabel="kg CO2e"
              color="#10b981"
            />
          </div>
        </Card>
      </div>

      {/* Threshold Breaches */}
      {latestBreaches.length > 0 && (
        <Card>
          <div className="p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              Recent Alerts
              <span className="ml-2 text-sm font-normal text-gray-500">
                ({latestBreaches.length})
              </span>
            </h2>

            <div className="space-y-3">
              {latestBreaches.slice(0, 10).map((breach, index) => (
                <Alert
                  key={index}
                  variant={
                    breach.severity === 'critical'
                      ? 'danger'
                      : breach.severity === 'warning'
                      ? 'warning'
                      : 'info'
                  }
                >
                  <div className="flex items-start justify-between">
                    <div>
                      <p className="font-semibold">
                        {breach.breach_type.toUpperCase()} - {breach.severity.toUpperCase()}
                      </p>
                      <p className="text-sm mt-1">
                        {breach.data.message || 'Threshold breach detected'}
                      </p>
                      <p className="text-xs text-gray-500 mt-1">
                        {new Date(breach.timestamp).toLocaleString()}
                      </p>
                    </div>
                    <Badge
                      variant={
                        breach.severity === 'critical'
                          ? 'danger'
                          : breach.severity === 'warning'
                          ? 'warning'
                          : 'info'
                      }
                    >
                      {breach.severity}
                    </Badge>
                  </div>
                </Alert>
              ))}
            </div>
          </div>
        </Card>
      )}

      {/* Connection Info */}
      {!isConnected && (
        <Card className="mt-6">
          <div className="p-6 text-center text-gray-500">
            <svg
              className="w-12 h-12 mx-auto mb-4 text-gray-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M8.111 16.404a5.5 5.5 0 017.778 0M12 20h.01m-7.08-7.071c3.904-3.905 10.236-3.905 14.141 0M1.394 9.393c5.857-5.857 15.355-5.857 21.213 0"
              />
            </svg>
            <p className="text-lg font-medium">Connecting to real-time stream...</p>
            <p className="text-sm mt-2">
              Please wait while we establish a connection to the monitoring server.
            </p>
          </div>
        </Card>
      )}
    </div>
  );
};
