/**
 * Live Metric Card Component
 * SPRINT 10 - AGENT 2: Live Dashboard Updates
 *
 * Displays real-time streaming metrics with visual updates
 */
import React, { useState, useEffect } from 'react';
import { Card } from './ui/Card';
import { Badge } from './ui/Badge';

interface LiveMetricCardProps {
  title: string;
  metric_type: string;
  value: number;
  unit: string;
  status?: 'normal' | 'warning' | 'critical';
  trend?: 'up' | 'down' | 'stable';
  lastUpdated?: string;
  icon?: React.ReactNode;
  isLive?: boolean;
}

export const LiveMetricCard: React.FC<LiveMetricCardProps> = ({
  title,
  metric_type,
  value,
  unit,
  status = 'normal',
  trend = 'stable',
  lastUpdated,
  icon,
  isLive = true,
}) => {
  const [pulse, setPulse] = useState(false);
  const [previousValue, setPreviousValue] = useState<number>(value);

  // Trigger pulse animation on value change
  useEffect(() => {
    if (value !== previousValue) {
      setPulse(true);
      setPreviousValue(value);
      const timeout = setTimeout(() => setPulse(false), 1000);
      return () => clearTimeout(timeout);
    }
  }, [value, previousValue]);

  const statusColors = {
    normal: 'text-green-600 bg-green-50',
    warning: 'text-yellow-600 bg-yellow-50',
    critical: 'text-red-600 bg-red-50',
  };

  const trendIcons = {
    up: '↑',
    down: '↓',
    stable: '→',
  };

  const trendColors = {
    up: 'text-green-600',
    down: 'text-red-600',
    stable: 'text-gray-600',
  };

  return (
    <Card className={`relative overflow-hidden transition-all duration-300 ${pulse ? 'ring-2 ring-blue-400' : ''}`}>
      {/* Live indicator */}
      {isLive && (
        <div className="absolute top-3 right-3">
          <div className="flex items-center space-x-1">
            <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
            <span className="text-xs text-gray-500">LIVE</span>
          </div>
        </div>
      )}

      <div className="p-6">
        {/* Header */}
        <div className="flex items-center space-x-3 mb-4">
          {icon && <div className="text-gray-600">{icon}</div>}
          <div>
            <h3 className="text-sm font-medium text-gray-600">{title}</h3>
            <p className="text-xs text-gray-400 mt-0.5">{metric_type}</p>
          </div>
        </div>

        {/* Value */}
        <div className="mb-4">
          <div className="flex items-baseline space-x-2">
            <span className="text-3xl font-bold text-gray-900">
              {value.toLocaleString(undefined, { maximumFractionDigits: 2 })}
            </span>
            <span className="text-sm text-gray-500">{unit}</span>
          </div>
        </div>

        {/* Status and Trend */}
        <div className="flex items-center justify-between">
          <Badge
            variant={status === 'normal' ? 'success' : status === 'warning' ? 'warning' : 'danger'}
            size="sm"
          >
            {status.toUpperCase()}
          </Badge>

          <div className="flex items-center space-x-2">
            <span className={`text-lg font-semibold ${trendColors[trend]}`}>
              {trendIcons[trend]}
            </span>
            {lastUpdated && (
              <span className="text-xs text-gray-400">
                {new Date(lastUpdated).toLocaleTimeString()}
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Pulse overlay */}
      {pulse && (
        <div className="absolute inset-0 bg-blue-100 opacity-20 animate-ping pointer-events-none"></div>
      )}
    </Card>
  );
};
