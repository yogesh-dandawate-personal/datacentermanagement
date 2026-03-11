/**
 * Live Chart Component
 * SPRINT 10 - AGENT 2: Real-Time Charting
 *
 * Auto-updating chart for streaming metric data
 */
import React, { useMemo } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface LiveChartProps {
  data: Array<{
    timestamp: string;
    value: number;
    [key: string]: any;
  }>;
  title: string;
  yAxisLabel?: string;
  maxDataPoints?: number;
  color?: string;
}

export const LiveChart: React.FC<LiveChartProps> = ({
  data,
  title,
  yAxisLabel = 'Value',
  maxDataPoints = 50,
  color = '#3b82f6',
}) => {
  // Limit data points and format for chart
  const chartData = useMemo(() => {
    return data
      .slice(-maxDataPoints)
      .map((point) => ({
        ...point,
        time: new Date(point.timestamp).toLocaleTimeString(),
      }));
  }, [data, maxDataPoints]);

  return (
    <div className="w-full h-full">
      <h3 className="text-lg font-semibold text-gray-800 mb-4">{title}</h3>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart
          data={chartData}
          margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis
            dataKey="time"
            stroke="#6b7280"
            style={{ fontSize: '12px' }}
          />
          <YAxis
            label={{ value: yAxisLabel, angle: -90, position: 'insideLeft' }}
            stroke="#6b7280"
            style={{ fontSize: '12px' }}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: 'rgba(255, 255, 255, 0.95)',
              border: '1px solid #e5e7eb',
              borderRadius: '8px',
            }}
          />
          <Legend />
          <Line
            type="monotone"
            dataKey="value"
            stroke={color}
            strokeWidth={2}
            dot={false}
            isAnimationActive={true}
            animationDuration={300}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};
