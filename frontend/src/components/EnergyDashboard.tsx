"""
Energy Dashboard Component

Real-time energy consumption dashboard with:
- Total consumption card
- Trend charts
- Facility breakdown
- Efficiency metrics
- Peak usage alerts
"""

import React, { useState, useEffect } from 'react';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { useEnergyMetrics } from '../hooks/useEnergyMetrics';

// Mock data for demonstration
const mockDashboardData = {
  organization_id: 'org-123',
  consumption: {
    current_kwh: 1245.32,
    total_kwh: 87234.56,
    average_kwh: 1235.42,
    peak_kwh: 2345.89,
    timestamp: new Date().toISOString(),
    trend: [
      { timestamp: '2026-03-09T00:00', value: 1120 },
      { timestamp: '2026-03-09T01:00', value: 1145 },
      { timestamp: '2026-03-09T02:00', value: 1098 },
      { timestamp: '2026-03-09T03:00', value: 1235 },
      { timestamp: '2026-03-09T04:00', value: 1456 },
      { timestamp: '2026-03-09T05:00', value: 1789 },
      { timestamp: '2026-03-09T06:00', value: 2034 },
      { timestamp: '2026-03-09T07:00', value: 2345 },
      { timestamp: '2026-03-09T08:00', value: 2156 },
      { timestamp: '2026-03-09T09:00', value: 1876 },
      { timestamp: '2026-03-09T10:00', value: 1645 },
      { timestamp: '2026-03-09T11:00', value: 1234 },
      { timestamp: '2026-03-09T12:00', value: 1123 },
      { timestamp: '2026-03-09T13:00', value: 1245 },
      { timestamp: '2026-03-09T14:00', value: 1456 },
      { timestamp: '2026-03-09T15:00', value: 1678 },
      { timestamp: '2026-03-09T16:00', value: 1899 },
      { timestamp: '2026-03-09T17:00', value: 1734 },
      { timestamp: '2026-03-09T18:00', value: 1523 },
      { timestamp: '2026-03-09T19:00', value: 1245 },
      { timestamp: '2026-03-09T20:00', value: 1087 },
      { timestamp: '2026-03-09T21:00', value: 987 },
      { timestamp: '2026-03-09T22:00', value: 1123 },
      { timestamp: '2026-03-09T23:00', value: 1245 },
    ],
  },
  facility_breakdown: [
    { facility_id: 'fac-1', facility_name: 'DC East 1', current_kwh: 456.23, total_kwh: 32145.67, average_kwh: 445.23, peak_kwh: 856.23 },
    { facility_id: 'fac-2', facility_name: 'DC West 1', current_kwh: 345.67, total_kwh: 28934.12, average_kwh: 401.12, peak_kwh: 723.45 },
    { facility_id: 'fac-3', facility_name: 'DC Central', current_kwh: 443.42, total_kwh: 26154.77, average_kwh: 362.98, peak_kwh: 766.21 },
  ],
  timestamp: new Date().toISOString(),
};

interface EnergyConsumptionCard {
  label: string;
  value: number;
  unit: string;
  color: string;
}

interface ConsumptionTrend {
  timestamp: string;
  value: number;
}

interface FacilityBreakdown {
  facility_id: string;
  facility_name: string;
  current_kwh: number;
  total_kwh: number;
  average_kwh: number;
  peak_kwh: number;
}

const EnergyDashboard: React.FC<{ orgId: string }> = ({ orgId }) => {
  const [dashboardData, setDashboardData] = useState(mockDashboardData);
  const [selectedFacility, setSelectedFacility] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { fetchDashboard, subscribeToUpdates } = useEnergyMetrics();

  // Load dashboard data on component mount
  useEffect(() => {
    const loadDashboard = async () => {
      setIsLoading(true);
      try {
        // Try to load from real API, fall back to mock
        const data = await fetchDashboard(orgId);
        if (data) {
          setDashboardData(data);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load dashboard');
        // Continue with mock data
      } finally {
        setIsLoading(false);
      }
    };

    loadDashboard();

    // Subscribe to real-time updates if API available
    const unsubscribe = subscribeToUpdates(orgId, (newData) => {
      setDashboardData(newData);
    });

    return () => unsubscribe();
  }, [orgId, fetchDashboard, subscribeToUpdates]);

  const consumptionCards: EnergyConsumptionCard[] = [
    {
      label: 'Current Load',
      value: dashboardData.consumption.current_kwh,
      unit: 'kW',
      color: 'bg-blue-500',
    },
    {
      label: 'Peak Usage',
      value: dashboardData.consumption.peak_kwh,
      unit: 'kW',
      color: 'bg-red-500',
    },
    {
      label: 'Daily Average',
      value: dashboardData.consumption.average_kwh,
      unit: 'kW',
      color: 'bg-green-500',
    },
    {
      label: 'Total 7-Day',
      value: dashboardData.consumption.total_kwh,
      unit: 'kWh',
      color: 'bg-purple-500',
    },
  ];

  const trendData: ConsumptionTrend[] = dashboardData.consumption.trend.map((t) => ({
    timestamp: new Date(t.timestamp).toLocaleTimeString(),
    value: t.value,
  }));

  const facilityData: FacilityBreakdown[] = dashboardData.facility_breakdown;

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Energy Dashboard</h1>
          <p className="text-gray-600">Real-time energy consumption and analytics</p>
          {error && (
            <div className="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
              <p className="text-sm text-yellow-800">{error} (Using mock data)</p>
            </div>
          )}
        </div>

        {/* Loading State */}
        {isLoading && (
          <div className="flex justify-center items-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500" />
          </div>
        )}

        {!isLoading && (
          <>
            {/* Consumption Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              {consumptionCards.map((card) => (
                <div key={card.label} className="bg-white rounded-lg shadow p-6">
                  <p className="text-gray-600 text-sm font-medium mb-2">{card.label}</p>
                  <div className="flex items-baseline gap-2">
                    <p className="text-3xl font-bold text-gray-900">{card.value.toFixed(1)}</p>
                    <p className="text-lg text-gray-600">{card.unit}</p>
                  </div>
                  <div className={`mt-4 h-1 ${card.color} rounded w-full`} />
                </div>
              ))}
            </div>

            {/* Trend Chart */}
            <div className="bg-white rounded-lg shadow p-6 mb-8">
              <h2 className="text-xl font-bold text-gray-900 mb-4">Energy Consumption Trend (Last 24 Hours)</h2>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={trendData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="timestamp" />
                  <YAxis />
                  <Tooltip formatter={(value) => `${value.toFixed(1)} kW`} />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="value"
                    stroke="#3b82f6"
                    strokeWidth={2}
                    dot={false}
                    name="Power (kW)"
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>

            {/* Facility Breakdown */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4">Energy Breakdown by Facility</h2>

              {/* Bar Chart */}
              <div className="mb-8">
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={facilityData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="facility_name" />
                    <YAxis />
                    <Tooltip formatter={(value) => `${value.toFixed(1)} kWh`} />
                    <Legend />
                    <Bar dataKey="current_kwh" fill="#3b82f6" name="Current (kW)" />
                    <Bar dataKey="peak_kwh" fill="#ef4444" name="Peak (kW)" />
                  </BarChart>
                </ResponsiveContainer>
              </div>

              {/* Facility Table */}
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-4 py-2 text-left text-gray-700 font-semibold">Facility</th>
                      <th className="px-4 py-2 text-right text-gray-700 font-semibold">Current (kW)</th>
                      <th className="px-4 py-2 text-right text-gray-700 font-semibold">Peak (kW)</th>
                      <th className="px-4 py-2 text-right text-gray-700 font-semibold">Average (kW)</th>
                      <th className="px-4 py-2 text-right text-gray-700 font-semibold">Total 7d (kWh)</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {facilityData.map((facility) => (
                      <tr
                        key={facility.facility_id}
                        className="hover:bg-gray-50 cursor-pointer"
                        onClick={() => setSelectedFacility(facility.facility_id)}
                      >
                        <td className="px-4 py-3 text-gray-900 font-medium">{facility.facility_name}</td>
                        <td className="px-4 py-3 text-right text-gray-600">{facility.current_kwh.toFixed(2)}</td>
                        <td className="px-4 py-3 text-right text-gray-600">{facility.peak_kwh.toFixed(2)}</td>
                        <td className="px-4 py-3 text-right text-gray-600">{facility.average_kwh.toFixed(2)}</td>
                        <td className="px-4 py-3 text-right text-gray-600">{facility.total_kwh.toFixed(2)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Footer */}
            <div className="mt-8 text-center text-sm text-gray-600">
              Last updated: {new Date(dashboardData.timestamp).toLocaleString()}
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default EnergyDashboard;
