import React, { useEffect, useState } from 'react';

interface FacilityEmissionsTableProps {
  organizationId: string;
  metric: string;
  period: string;
}

const FacilityEmissionsTable: React.FC<FacilityEmissionsTableProps> = ({ organizationId, metric, period }) => {
  const [facilities, setFacilities] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Placeholder: would call API in real implementation
    setFacilities([]);
    setLoading(false);
  }, [organizationId, metric, period]);

  if (loading) {
    return <div className="space-y-2"><div className="h-10 bg-slate-700 rounded animate-pulse"></div></div>;
  }

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
          {facilities.map((facility) => (
            <tr key={facility.id} className="border-b border-slate-700 hover:bg-slate-700/30">
              <td className="py-3 px-4 text-white font-medium">{facility.name}</td>
              <td className="py-3 px-4 text-right text-slate-300">{facility.scope_1?.toLocaleString()} tCO2e</td>
              <td className="py-3 px-4 text-right text-slate-300">{facility.scope_2?.toLocaleString()} tCO2e</td>
              <td className="py-3 px-4 text-right text-slate-300">{facility.scope_3?.toLocaleString()} tCO2e</td>
              <td className="py-3 px-4 text-right text-white font-semibold">{facility.total?.toLocaleString()} tCO2e</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default FacilityEmissionsTable;
