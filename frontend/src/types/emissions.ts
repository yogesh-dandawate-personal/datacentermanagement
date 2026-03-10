/**
 * Emissions Module - TypeScript Type Definitions
 */

export interface EmissionsSource {
  id: string
  source_name: string
  source_type: string
  scope: "scope1" | "scope2" | "scope3"
  facility_id?: string
  unit_of_measure: string
  is_active: boolean
  created_at: string
}

export interface ActivityData {
  id: string
  source_id: string
  timestamp: string
  activity_value: number
  activity_unit: string
  validation_status: "valid" | "invalid" | "suspected_anomaly"
}

export interface EmissionsCalculation {
  id: string
  scope: "scope1" | "scope2" | "scope3"
  total_emissions_tco2e: number
  total_emissions_kgco2e?: number
  status: "draft" | "finalized" | "approved"
  period_start: string
  period_end: string
  created_at: string
}

export interface EmissionsReport {
  id: string
  report_type: string
  reporting_year: number
  scope_1_emissions?: number
  scope_2_emissions?: number
  scope_3_emissions?: number
  total_emissions?: number
  status: "draft" | "pending_review" | "approved" | "submitted" | "published"
  created_at: string
}

export interface EmissionsTarget {
  id: string
  target_name: string
  target_year: number
  baseline_value: number
  target_value: number
  progress_percentage: number
  status: "on_track" | "at_risk" | "failed" | "achieved"
}

export interface EmissionsAlert {
  id: string
  alert_type: string
  severity: "info" | "warning" | "critical"
  title: string
  status: "open" | "acknowledged" | "resolved"
  triggered_at: string
  triggered_value?: number
}

export interface DashboardData {
  facility_id: string
  period: string
  date_range: {
    start: string
    end: string
  }
  emissions: {
    total_tco2e: number
    scope_1_tco2e: number
    scope_2_tco2e: number
    scope_3_tco2e: number
    scope_1_pct: number
    scope_2_pct: number
    scope_3_pct: number
  }
  metrics: {
    carbon_intensity_gco2e_kwh: number
    pue?: number
    renewable_pct: number
    mom_change_pct: number
  }
  breakdown: Array<{
    scope: string
    emissions_tco2e: number
    pct: number
  }>
  trend_30d: Array<{
    date: string
    scope_1: number
    scope_2: number
    scope_3: number
    total: number
  }>
  top_sources: Array<{
    source_id: string
    source_name: string
    source_type: string
    emissions_tco2e: number
  }>
}

export interface PortfolioData {
  tenant_id: string
  period: string
  total_emissions_tco2e: number
  scope_breakdown: {
    scope_1_tco2e: number
    scope_2_tco2e: number
    scope_3_tco2e: number
    scope_1_pct: number
    scope_2_pct: number
    scope_3_pct: number
  }
  facility_breakdown: Array<{
    facility_id: string
    facility_name: string
    emissions_tco2e: number
    pct_of_total: number
  }>
  facility_count: number
}

export interface IngestionLog {
  ingestion_log_id: string
  ingestion_method: string
  data_source: string
  records_received: number
  records_processed: number
  records_failed: number
  status: "completed" | "partial_success" | "failed"
  created_at: string
  completed_at?: string
}

export interface AlertRule {
  id: string
  rule_name: string
  metric: string
  operator: ">" | "<" | ">=" | "<=" | "=="
  threshold_value: number
  severity: "info" | "warning" | "critical"
  is_enabled: boolean
}
