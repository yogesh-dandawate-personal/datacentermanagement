/**
 * Emissions Dashboard - Main page for emissions monitoring and analytics
 *
 * Displays:
 * - Total emissions (Scope 1/2/3 breakdown)
 * - Facility-level dashboard
 * - 30-day trend analysis
 * - Carbon intensity metrics
 * - Forecasted emissions (next 30 days)
 */

import React, { useState, useEffect } from 'react';
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { useEmissionsDashboard, useForecastEmissions, useTrendAnalysis, useCompareFacilities } from '../hooks/useEmissions';
import EmissionsSummaryCard from '../components/EmissionsSummaryCard';
import TrendAnalysisChart from '../components/TrendAnalysisChart';
import FacilityEmissionsTable from '../components/FacilityEmissionsTable';
import ForecastChart from '../components/ForecastChart';

interface EmissionsDashboardProps {
  organizationId: string;
  facilityId?: string;
  period?: 'current_month' | 'current_year' | 'last_30_days' | 'last_90_days';
}

const EmissionsDashboard: React.FC<EmissionsDashboardProps> = ({
  organizationId,
  facilityId,
  period = 'current_month'
}) => {
  const [selectedMetric, setSelectedMetric] = useState<'total' | 'scope1' | 'scope2' | 'scope3'>('total');
  const [trendDays, setTrendDays] = useState(30);

  // Fetch dashboard data
  const { data: dashboardData, loading: dashboardLoading } = useEmissionsDashboard({
    organizationId,
    facilityId,
    period
  });

  // Fetch forecast data
  const { data: forecastData, loading: forecastLoading } = useForecastEmissions({
    organizationId,
    facilityId,
    forecast_days: 30
  });

  // Fetch trend analysis data
  const { data: trendData } = useTrendAnalysis({
    organizationId,
    facilityId,
    days: trendDays,
    scope: selectedMetric === 'total' ? undefined : selectedMetric
  });

  // Fetch facility comparison
  const { data: comparisonData } = useCompareFacilities({
    organizationId,
    period
  });

  if (dashboardLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white mb-2">Emissions Dashboard</h1>
          <p className="text-slate-400">Real-time monitoring and analytics for ESG compliance</p>
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <EmissionsSummaryCard
            label="Total Emissions"
            value={dashboardData?.emissions?.total_tco2e || 0}
            unit="tCO2e"
            unit_period="month"
            trend={dashboardData?.metrics?.mom_change_pct || 0}
            trendDirection={
              (dashboardData?.metrics?.mom_change_pct || 0) > 0 ? 'up' :
              (dashboardData?.metrics?.mom_change_pct || 0) < 0 ? 'down' : 'neutral'
            }
            icon="📊"
            selected={selectedMetric === 'total'}
            onClick={() => setSelectedMetric('total')}
          />
          <EmissionsSummaryCard
            label="Scope 1 (Direct)"
            value={dashboardData?.emissions?.scope_1_tco2e || 0}
            unit="tCO2e"
            percentage={dashboardData?.emissions?.scope_1_pct || 0}
            icon="🔥"
            selected={selectedMetric === 'scope1'}
            onClick={() => setSelectedMetric('scope1')}
          />
          <EmissionsSummaryCard
            label="Scope 2 (Electricity)"
            value={dashboardData?.emissions?.scope_2_tco2e || 0}
            unit="tCO2e"
            percentage={dashboardData?.emissions?.scope_2_pct || 0}
            icon="⚡"
            selected={selectedMetric === 'scope2'}
            onClick={() => setSelectedMetric('scope2')}
          />
          <EmissionsSummaryCard
            label="Scope 3 (Indirect)"
            value={dashboardData?.emissions?.scope_3_tco2e || 0}
            unit="tCO2e"
            percentage={dashboardData?.emissions?.scope_3_pct || 0}
            icon="🌍"
            selected={selectedMetric === 'scope3'}
            onClick={() => setSelectedMetric('scope3')}
          />
        </div>

        {/* Trend and Forecast Row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Trend Analysis */}
          <div className="bg-slate-800 rounded-lg border border-slate-700 p-6 shadow-xl">
            <div className="mb-4">
              <h2 className="text-xl font-bold text-white mb-2">Emissions Trend</h2>
              <div className="flex gap-2">
                <button
                  onClick={() => setTrendDays(7)}
                  className={`px-3 py-1 rounded text-sm ${trendDays === 7 ? 'bg-blue-600 text-white' : 'bg-slate-700 text-slate-300'}`}
                >
                  7 Days
                </button>
                <button
                  onClick={() => setTrendDays(30)}
                  className={`px-3 py-1 rounded text-sm ${trendDays === 30 ? 'bg-blue-600 text-white' : 'bg-slate-700 text-slate-300'}`}
                >
                  30 Days
                </button>
                <button
                  onClick={() => setTrendDays(90)}
                  className={`px-3 py-1 rounded text-sm ${trendDays === 90 ? 'bg-blue-600 text-white' : 'bg-slate-700 text-slate-300'}`}
                >
                  90 Days
                </button>
              </div>
            </div>
            <TrendAnalysisChart
              organizationId={organizationId}
              facilityId={facilityId}
              days={trendDays}
              scope={selectedMetric === 'total' ? undefined : selectedMetric}
            />
            {trendData && (
              <div className="mt-4 pt-4 border-t border-slate-700">
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <p className="text-slate-400">Trend Direction</p>
                    <p className="text-white font-semibold capitalize">{trendData.slope_direction}</p>
                  </div>
                  <div>
                    <p className="text-slate-400">Trend Strength</p>
                    <p className="text-white font-semibold capitalize">{trendData.summary.trend_strength}</p>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Forecast */}
          <div className="bg-slate-800 rounded-lg border border-slate-700 p-6 shadow-xl">
            <div className="mb-4">
              <h2 className="text-xl font-bold text-white mb-1">30-Day Forecast</h2>
              <p className="text-slate-400 text-sm">Predicted emissions with 95% confidence intervals</p>
            </div>
            <ForecastChart
              data={forecastData}
              loading={forecastLoading}
            />
            {forecastData && (
              <div className="mt-4 pt-4 border-t border-slate-700">
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <p className="text-slate-400">Confidence Level</p>
                    <p className="text-white font-semibold capitalize">{forecastData.confidence_level}</p>
                  </div>
                  <div>
                    <p className="text-slate-400">Trend</p>
                    <p className="text-white font-semibold capitalize">{forecastData.trend_direction}</p>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Facilities Breakdown */}
        <div className="bg-slate-800 rounded-lg border border-slate-700 p-6 shadow-xl">
          <h2 className="text-xl font-bold text-white mb-4">Facilities Breakdown</h2>
          <FacilityEmissionsTable
            organizationId={organizationId}
            period={period}
          />
        </div>

        {/* Carbon Intensity Metrics */}
        {dashboardData?.metrics && (
          <div className="mt-8 bg-slate-800 rounded-lg border border-slate-700 p-6 shadow-xl">
            <h2 className="text-xl font-bold text-white mb-4">Carbon Intensity Metrics</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-slate-700 rounded p-4">
                <p className="text-slate-300 text-sm mb-1">Carbon Intensity</p>
                <p className="text-white text-2xl font-bold">{dashboardData.metrics.carbon_intensity_gco2e_kwh.toFixed(3)}</p>
                <p className="text-slate-400 text-xs">gCO2e per kWh</p>
              </div>
              <div className="bg-slate-700 rounded p-4">
                <p className="text-slate-300 text-sm mb-1">Power Usage Effectiveness</p>
                <p className="text-white text-2xl font-bold">{dashboardData.metrics.pue?.toFixed(2) || 'N/A'}</p>
                <p className="text-slate-400 text-xs">PUE ratio</p>
              </div>
              <div className="bg-slate-700 rounded p-4">
                <p className="text-slate-300 text-sm mb-1">Renewable Energy</p>
                <p className="text-white text-2xl font-bold">{dashboardData.metrics.renewable_pct.toFixed(1)}%</p>
                <p className="text-slate-400 text-xs">of total energy</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default EmissionsDashboard;
