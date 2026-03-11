import React, { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

interface TrendAnalysisChartProps {
  organizationId: string;
  facilityId?: string;
  days: number;
  scope?: string;
}

const TrendAnalysisChart: React.FC<TrendAnalysisChartProps> = ({ organizationId, facilityId, days, scope }) => {
  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Placeholder: would call API in real implementation
    setData([]);
    setLoading(false);
  }, [facilityId, days, scope]);

  if (loading) {
    return <div className="h-64 bg-slate-700 rounded animate-pulse"></div>;
  }

  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={data || []}>
        <CartesianGrid strokeDasharray="3 3" stroke="#475569" />
        <XAxis dataKey="date" stroke="#94a3b8" />
        <YAxis stroke="#94a3b8" />
        <Tooltip contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #475569' }} />
        <Line type="monotone" dataKey="emissions_tco2e" stroke="#3b82f6" dot={false} isAnimationActive={false} />
      </LineChart>
    </ResponsiveContainer>
  );
};

export default TrendAnalysisChart;
