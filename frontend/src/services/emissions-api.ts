/**
 * Emissions API Client
 * Handles all API communication for emissions features
 */

const API_BASE = process.env.REACT_APP_API_BASE || 'http://localhost:8000'

interface ApiResponse<T> {
  data?: T
  error?: string
  count?: number
  total?: number
}

class EmissionsApiClient {
  /**
   * EMISSIONS SOURCES
   */

  async getSources(orgId: string, facilityId?: string) {
    const params = new URLSearchParams()
    if (facilityId) params.append('facility_id', facilityId)

    const response = await fetch(
      `${API_BASE}/api/v1/emissions/organizations/${orgId}/sources?${params}`,
      { credentials: 'include' }
    )

    if (!response.ok) {
      throw new Error(`Failed to fetch sources: ${response.statusText}`)
    }

    return response.json()
  }

  async createSource(orgId: string, sourceData: any) {
    const response = await fetch(
      `${API_BASE}/api/v1/emissions/organizations/${orgId}/sources`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(sourceData),
        credentials: 'include',
      }
    )

    if (!response.ok) {
      throw new Error(`Failed to create source: ${response.statusText}`)
    }

    return response.json()
  }

  /**
   * ACTIVITY DATA
   */

  async submitActivityData(
    orgId: string,
    sourceId: string,
    timestamp: string,
    activityValue: number,
    activityUnit: string
  ) {
    const response = await fetch(
      `${API_BASE}/api/v1/emissions/organizations/${orgId}/activity-data`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          source_id: sourceId,
          timestamp,
          activity_value: activityValue,
          activity_unit: activityUnit,
        }),
        credentials: 'include',
      }
    )

    if (!response.ok) {
      throw new Error(`Failed to submit activity data: ${response.statusText}`)
    }

    return response.json()
  }

  async uploadBatchFile(orgId: string, file: File, sourceId?: string) {
    const formData = new FormData()
    formData.append('file', file)
    if (sourceId) formData.append('source_id', sourceId)

    const response = await fetch(
      `${API_BASE}/api/v1/emissions/organizations/${orgId}/activity-data/batch`,
      {
        method: 'POST',
        body: formData,
        credentials: 'include',
      }
    )

    if (!response.ok) {
      throw new Error(`Failed to upload batch file: ${response.statusText}`)
    }

    return response.json()
  }

  async getActivityData(orgId: string, sourceId?: string, startDate?: string, endDate?: string) {
    const params = new URLSearchParams()
    if (sourceId) params.append('source_id', sourceId)
    if (startDate) params.append('start_date', startDate)
    if (endDate) params.append('end_date', endDate)

    const response = await fetch(
      `${API_BASE}/api/v1/emissions/organizations/${orgId}/activity-data?${params}`,
      { credentials: 'include' }
    )

    if (!response.ok) {
      throw new Error(`Failed to fetch activity data: ${response.statusText}`)
    }

    return response.json()
  }

  /**
   * CALCULATIONS
   */

  async calculateScope1(orgId: string, sourceId: string, periodStart: string, periodEnd: string) {
    const response = await fetch(
      `${API_BASE}/api/v1/emissions/organizations/${orgId}/calculate/scope1`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          source_id: sourceId,
          period_start: periodStart,
          period_end: periodEnd,
        }),
        credentials: 'include',
      }
    )

    if (!response.ok) {
      throw new Error(`Failed to calculate Scope 1: ${response.statusText}`)
    }

    return response.json()
  }

  async calculateScope2(orgId: string, sourceId: string, periodStart: string, periodEnd: string) {
    const response = await fetch(
      `${API_BASE}/api/v1/emissions/organizations/${orgId}/calculate/scope2`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          source_id: sourceId,
          period_start: periodStart,
          period_end: periodEnd,
        }),
        credentials: 'include',
      }
    )

    if (!response.ok) {
      throw new Error(`Failed to calculate Scope 2: ${response.statusText}`)
    }

    return response.json()
  }

  async calculateScope3(orgId: string, sourceId: string, periodStart: string, periodEnd: string) {
    const response = await fetch(
      `${API_BASE}/api/v1/emissions/organizations/${orgId}/calculate/scope3`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          source_id: sourceId,
          period_start: periodStart,
          period_end: periodEnd,
        }),
        credentials: 'include',
      }
    )

    if (!response.ok) {
      throw new Error(`Failed to calculate Scope 3: ${response.statusText}`)
    }

    return response.json()
  }

  async getCalculations(orgId: string, scope?: string, status?: string) {
    const params = new URLSearchParams()
    if (scope) params.append('scope', scope)
    if (status) params.append('status', status)

    const response = await fetch(
      `${API_BASE}/api/v1/emissions/organizations/${orgId}/calculations?${params}`,
      { credentials: 'include' }
    )

    if (!response.ok) {
      throw new Error(`Failed to fetch calculations: ${response.statusText}`)
    }

    return response.json()
  }

  /**
   * ANALYTICS
   */

  async getFacilityDashboard(facilityId: string, period: string = 'current_month') {
    const params = new URLSearchParams({ period })

    const response = await fetch(
      `${API_BASE}/api/v1/emissions/facilities/${facilityId}/dashboard?${params}`,
      { credentials: 'include' }
    )

    if (!response.ok) {
      throw new Error(`Failed to fetch facility dashboard: ${response.statusText}`)
    }

    return response.json()
  }

  async getPortfolioOverview(orgId: string, period: string = 'current_year') {
    const params = new URLSearchParams({ period })

    const response = await fetch(
      `${API_BASE}/api/v1/emissions/organizations/${orgId}/portfolio?${params}`,
      { credentials: 'include' }
    )

    if (!response.ok) {
      throw new Error(`Failed to fetch portfolio overview: ${response.statusText}`)
    }

    return response.json()
  }

  async getTrendAnalysis(orgId: string, facilityId?: string, days: number = 30, scope?: string) {
    const params = new URLSearchParams()
    params.append('days', days.toString())
    if (facilityId) params.append('facility_id', facilityId)
    if (scope) params.append('scope', scope)

    const response = await fetch(
      `${API_BASE}/api/v1/emissions/organizations/${orgId}/analytics/trend?${params}`,
      { credentials: 'include' }
    )

    if (!response.ok) {
      throw new Error(`Failed to fetch trend analysis: ${response.statusText}`)
    }

    return response.json()
  }

  async getForecastEmissions(orgId: string, facilityId?: string, forecastDays: number = 30) {
    const params = new URLSearchParams()
    params.append('forecast_days', forecastDays.toString())
    if (facilityId) params.append('facility_id', facilityId)

    const response = await fetch(
      `${API_BASE}/api/v1/emissions/organizations/${orgId}/analytics/forecast?${params}`,
      { credentials: 'include' }
    )

    if (!response.ok) {
      throw new Error(`Failed to fetch emissions forecast: ${response.statusText}`)
    }

    return response.json()
  }

  async getOrganizationDashboard(orgId: string, facilityId?: string, period: string = 'current_month') {
    const params = new URLSearchParams({ period })
    if (facilityId) params.append('facility_id', facilityId)

    const response = await fetch(
      `${API_BASE}/api/v1/emissions/organizations/${orgId}/dashboard?${params}`,
      { credentials: 'include' }
    )

    if (!response.ok) {
      throw new Error(`Failed to fetch organization dashboard: ${response.statusText}`)
    }

    return response.json()
  }

  async compareFacilities(orgId: string, period: string = 'current_month') {
    const params = new URLSearchParams({ period })

    const response = await fetch(
      `${API_BASE}/api/v1/emissions/organizations/${orgId}/analytics/compare-facilities?${params}`,
      { credentials: 'include' }
    )

    if (!response.ok) {
      throw new Error(`Failed to fetch facility comparison: ${response.statusText}`)
    }

    return response.json()
  }

  /**
   * TARGETS
   */

  async getTargets(orgId: string) {
    const response = await fetch(
      `${API_BASE}/api/v1/emissions/organizations/${orgId}/targets`,
      { credentials: 'include' }
    )

    if (!response.ok) {
      throw new Error(`Failed to fetch targets: ${response.statusText}`)
    }

    return response.json()
  }

  async createTarget(orgId: string, targetData: any) {
    const response = await fetch(
      `${API_BASE}/api/v1/emissions/organizations/${orgId}/targets`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(targetData),
        credentials: 'include',
      }
    )

    if (!response.ok) {
      throw new Error(`Failed to create target: ${response.statusText}`)
    }

    return response.json()
  }

  /**
   * ALERTS
   */

  async getAlerts(orgId: string, severity?: string, status?: string) {
    const params = new URLSearchParams()
    if (severity) params.append('severity', severity)
    if (status) params.append('status', status)

    const response = await fetch(
      `${API_BASE}/api/v1/emissions/organizations/${orgId}/alerts?${params}`,
      { credentials: 'include' }
    )

    if (!response.ok) {
      throw new Error(`Failed to fetch alerts: ${response.statusText}`)
    }

    return response.json()
  }

  async acknowledgeAlert(orgId: string, alertId: string) {
    const response = await fetch(
      `${API_BASE}/api/v1/emissions/organizations/${orgId}/alerts/${alertId}/acknowledge`,
      {
        method: 'POST',
        credentials: 'include',
      }
    )

    if (!response.ok) {
      throw new Error(`Failed to acknowledge alert: ${response.statusText}`)
    }

    return response.json()
  }

  async resolveAlert(orgId: string, alertId: string) {
    const response = await fetch(
      `${API_BASE}/api/v1/emissions/organizations/${orgId}/alerts/${alertId}/resolve`,
      {
        method: 'POST',
        credentials: 'include',
      }
    )

    if (!response.ok) {
      throw new Error(`Failed to resolve alert: ${response.statusText}`)
    }

    return response.json()
  }

  async getAlertRules(orgId: string) {
    const response = await fetch(
      `${API_BASE}/api/v1/emissions/organizations/${orgId}/alert-rules`,
      { credentials: 'include' }
    )

    if (!response.ok) {
      throw new Error(`Failed to fetch alert rules: ${response.statusText}`)
    }

    return response.json()
  }

  async createAlertRule(orgId: string, ruleData: any) {
    const response = await fetch(
      `${API_BASE}/api/v1/emissions/organizations/${orgId}/alert-rules`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(ruleData),
        credentials: 'include',
      }
    )

    if (!response.ok) {
      throw new Error(`Failed to create alert rule: ${response.statusText}`)
    }

    return response.json()
  }

  /**
   * INGESTION HISTORY
   */

  async getIngestionHistory(orgId: string, sourceId?: string) {
    const params = new URLSearchParams()
    if (sourceId) params.append('source_id', sourceId)

    const response = await fetch(
      `${API_BASE}/api/v1/emissions/organizations/${orgId}/ingestion-history?${params}`,
      { credentials: 'include' }
    )

    if (!response.ok) {
      throw new Error(`Failed to fetch ingestion history: ${response.statusText}`)
    }

    return response.json()
  }
}

export const emissionsApi = new EmissionsApiClient()
