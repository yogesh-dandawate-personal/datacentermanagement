import React from 'react';
import { useCompareFacilities } from '../hooks/useEmissions';

interface FacilityEmissionsTableProps {
  organizationId: string;
  period?: 'current_month' | 'current_year' | 'last_30_days' | 'last_90_days';
}

const FacilityEmissionsTable: React.FC<FacilityEmissionsTableProps> = ({ organizationId, period = 'current_month' }) => {
  const { data: comparisonData, loading } = useCompareFacilities({
    organizationId,
    period
  });

  if (loading) {
    return <div className="space-y-2"><div className="h-10 bg-slate-700 rounded animate-pulse"></div></div>;
  }

  const facilities = comparisonData?.facilities || [];

  return (
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead className="border-b border-slate-600">
          <tr>
            <th className="text-left py-3 px-4 text-slate-300 font-semibold">Facility</th>
            <th className="text-right py-3 px-4 text-slate-300 font-semibold">Scope 1</th>
            <th className="text-right py-3 px-4 text-slate-300 font-semibold">Scope 2</th>
            <th className="text-right py-3 px-4 text-slate-300 font-semibold">Scope 3</th>
            <th className="text-right py-3 px-4 text-slate-300 font-semibold">Total</th>
          </tr>
        </thead>
        <tbody>
          {facilities && facilities.map((facility) => (
            <tr key={facility.facility_id} className="border-b border-slate-700 hover:bg-slate-700/30">
              <td className="py-3 px-4 text-white font-medium">{facility.facility_name}</td>
              <td className="py-3 px-4 text-right text-slate-300">{facility.scope_1_tco2e?.toLocaleString(undefined, { maximumFractionDigits: 1 })} tCO2e</td>
              <td className="py-3 px-4 text-right text-slate-300">{facility.scope_2_tco2e?.toLocaleString(undefined, { maximumFractionDigits: 1 })} tCO2e</td>
              <td className="py-3 px-4 text-right text-slate-300">{facility.scope_3_tco2e?.toLocaleString(undefined, { maximumFractionDigits: 1 })} tCO2e</td>
              <td className="py-3 px-4 text-right text-white font-semibold">{facility.total_tco2e?.toLocaleString(undefined, { maximumFractionDigits: 1 })} tCO2e</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default FacilityEmissionsTable;
