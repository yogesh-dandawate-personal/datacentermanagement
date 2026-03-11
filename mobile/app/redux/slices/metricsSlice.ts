/**
 * Metrics Redux Slice
 */

import { createSlice, PayloadAction } from '@reduxjs/toolkit';

export interface EnergyMetric {
  id: string;
  facility_id: string;
  timestamp: string;
  power_kw: number;
  energy_kwh: number;
  pue: number;
  temperature_c: number;
}

export interface EmissionMetric {
  id: string;
  facility_id: string;
  date: string;
  scope1_kg: number;
  scope2_kg: number;
  scope3_kg: number;
  total_kg: number;
}

interface MetricsState {
  energy: {
    data: EnergyMetric[];
    loading: boolean;
    error: string | null;
    lastSync: string | null;
  };
  emissions: {
    data: EmissionMetric[];
    loading: boolean;
    error: string | null;
    lastSync: string | null;
  };
  cachedData: {
    dashboardSummary: any | null;
    energyTrends: any | null;
  };
}

const initialState: MetricsState = {
  energy: {
    data: [],
    loading: false,
    error: null,
    lastSync: null,
  },
  emissions: {
    data: [],
    loading: false,
    error: null,
    lastSync: null,
  },
  cachedData: {
    dashboardSummary: null,
    energyTrends: null,
  },
};

const metricsSlice = createSlice({
  name: 'metrics',
  initialState,
  reducers: {
    // Energy actions
    fetchEnergyStart: (state) => {
      state.energy.loading = true;
      state.energy.error = null;
    },
    fetchEnergySuccess: (state, action: PayloadAction<EnergyMetric[]>) => {
      state.energy.data = action.payload;
      state.energy.loading = false;
      state.energy.lastSync = new Date().toISOString();
    },
    fetchEnergyFailure: (state, action: PayloadAction<string>) => {
      state.energy.loading = false;
      state.energy.error = action.payload;
    },

    // Emissions actions
    fetchEmissionsStart: (state) => {
      state.emissions.loading = true;
      state.emissions.error = null;
    },
    fetchEmissionsSuccess: (state, action: PayloadAction<EmissionMetric[]>) => {
      state.emissions.data = action.payload;
      state.emissions.loading = false;
      state.emissions.lastSync = new Date().toISOString();
    },
    fetchEmissionsFailure: (state, action: PayloadAction<string>) => {
      state.emissions.loading = false;
      state.emissions.error = action.payload;
    },

    // Cache actions
    updateDashboardCache: (state, action: PayloadAction<any>) => {
      state.cachedData.dashboardSummary = action.payload;
    },
    updateEnergyTrendsCache: (state, action: PayloadAction<any>) => {
      state.cachedData.energyTrends = action.payload;
    },
  },
});

export const {
  fetchEnergyStart,
  fetchEnergySuccess,
  fetchEnergyFailure,
  fetchEmissionsStart,
  fetchEmissionsSuccess,
  fetchEmissionsFailure,
  updateDashboardCache,
  updateEnergyTrendsCache,
} = metricsSlice.actions;

export default metricsSlice.reducer;
