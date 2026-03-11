import React from 'react';

interface EmissionsSummaryCardProps {
  label: string;
  value: number;
  unit: string;
  unit_period?: string;
  trend?: number;
  trendDirection?: 'up' | 'down' | 'neutral';
  percentage?: number;
  icon?: string;
  selected?: boolean;
  onClick?: () => void;
}

const EmissionsSummaryCard: React.FC<EmissionsSummaryCardProps> = ({
  label,
  value,
  unit,
  unit_period,
  trend,
  trendDirection,
  percentage,
  icon,
  selected,
  onClick
}) => {
  return (
    <div
      onClick={onClick}
      className={`bg-gradient-to-br rounded-lg border p-6 shadow-lg cursor-pointer transition-all ${
        selected
          ? 'from-blue-600 to-blue-700 border-blue-500 scale-105'
          : 'from-slate-800 to-slate-700 border-slate-600 hover:from-slate-700'
      }`}
    >
      <div className="flex items-start justify-between mb-4">
        <div>
          <p className={`text-sm ${selected ? 'text-blue-100' : 'text-slate-400'} mb-1`}>{label}</p>
          <div className="flex items-baseline gap-2">
            <p className="text-3xl font-bold text-white">{value.toLocaleString(undefined, { maximumFractionDigits: 1 })}</p>
            <p className={`text-lg ${selected ? 'text-blue-100' : 'text-slate-400'}`}>{unit}</p>
          </div>
        </div>
        {icon && <span className="text-3xl">{icon}</span>}
      </div>

      {(trend !== undefined || percentage !== undefined) && (
        <div className="flex items-center gap-4 text-sm">
          {trend !== undefined && (
            <div className="flex items-center gap-1">
              <span className={trendDirection === 'up' ? 'text-red-400' : trendDirection === 'down' ? 'text-green-400' : 'text-slate-400'}>
                {trendDirection === 'up' ? '↑' : trendDirection === 'down' ? '↓' : '→'}
              </span>
              <span className={trendDirection === 'up' ? 'text-red-400' : trendDirection === 'down' ? 'text-green-400' : 'text-slate-400'}>
                {Math.abs(trend).toFixed(1)}%
              </span>
            </div>
          )}
          {percentage !== undefined && (
            <div className="text-slate-300">{percentage.toFixed(1)}% of total</div>
          )}
        </div>
      )}
    </div>
  );
};

export default EmissionsSummaryCard;
