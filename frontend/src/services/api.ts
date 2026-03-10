/**
 * API Service Layer
 * Centralized API client for all backend communication
 * Uses mock data in development mode when backend is unavailable
 */

const isLocalhost = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
const API_BASE_URL = import.meta.env.VITE_API_URL || (isLocalhost ? 'http://127.0.0.1:8000/api/v1' : '/api/v1')

// Helper to check if mock data should be used (check at runtime, not module load time)
const shouldUseMockData = () => {
  if (!isLocalhost) return false
  return localStorage.getItem('USE_MOCK_API') === 'true' || localStorage.getItem('BYPASS_AUTH') === 'true'
}

// Types for API responses
export interface ApiResponse<T> {
  data: T
  status: number
  message?: string
}

export interface ApiError {
  status: number
  message: string
  errors?: Record<string, string[]>
}

// Auth
export interface AuthResponse {
  access_token: string
  token_type: string
  user: {
    id: string
    email: string
    name: string
    organization_id: string
  }
}

// Energy
export interface EnergyData {
  timestamp: string
  facility_id: string
  usage_kw: number
  renewable_kw: number
  target_kw: number
}

export interface Facility {
  id: string
  name: string
  location: string
  status: 'Active' | 'Inactive' | 'Maintenance'
  current_usage: number
  renewable_percentage: number
}

export interface EnergyMetrics {
  total_usage: number
  renewable_percentage: number
  daily_cost: number
  facilities: Facility[]
  trend_data: EnergyData[]
}

// Reports
export interface Report {
  id: number
  name: string
  date: string
  status: 'Complete' | 'Pending Review' | 'Draft'
  size: string
  compliance: string
  type: 'ESG' | 'Compliance' | 'Audit' | 'Strategic' | 'Analysis'
}

export interface ComplianceMetrics {
  total_emissions: number
  compliance_rate: number
  reports_generated: number
  trend_data: Array<{
    month: string
    scope1: number
    scope2: number
    scope3: number
  }>
}

// Settings
export interface UserProfile {
  id: string
  full_name: string
  email: string
  company: string
  timezone: string
  avatar_url?: string
}

export interface OrganizationSettings {
  id: string
  name: string
  industry: string
  size: string
  country: string
}

// Analytics Types
export interface AnalyticsTrend {
  month: string
  emissions_co2: number
  energy_usage_kwh: number
  renewable_percentage: number
  cost_usd: number
  forecast?: boolean
}

export interface EnergyPattern {
  timestamp: string
  usage_kw: number
  is_peak: boolean
  anomaly_score?: number
}

export interface ForecastData {
  current_month: string
  projections: Array<{
    month: string
    emissions_co2: number
    confidence_lower: number
    confidence_upper: number
  }>
  accuracy_percentage: number
}

export interface SustainabilityScore {
  overall_score: number // 0-100
  breakdown: {
    energy_efficiency: number
    renewable_usage: number
    emissions_reduction: number
    compliance_adherence: number
  }
  trend: 'improving' | 'stable' | 'declining'
  industry_percentile: number
}

// Reporting Types
export interface ReportTemplate {
  id: string
  name: string
  description: string
  type: 'ESG' | 'Compliance' | 'Energy' | 'Custom'
  sections: string[]
  filters: Record<string, any>
  created_at: string
  updated_at: string
}

export interface CreateReportTemplate {
  name: string
  description: string
  type: string
  sections: string[]
  filters?: Record<string, any>
}

export interface ReportSchedule {
  id: string
  name: string
  template_id: string
  template_name: string
  frequency: 'daily' | 'weekly' | 'monthly' | 'quarterly'
  cron_expression: string
  delivery_channels: Array<{
    type: 'email' | 'slack' | 'webhook'
    config: Record<string, any>
  }>
  enabled: boolean
  last_run?: string
  next_run: string
  created_at: string
}

export interface CreateReportSchedule {
  name: string
  template_id: string
  frequency: string
  cron_expression: string
  delivery_channels: Array<{
    type: string
    config: Record<string, any>
  }>
  enabled?: boolean
}

export interface ReportPreview {
  template_id: string
  template_name: string
  generated_at: string
  sections: Array<{
    title: string
    content: any
  }>
  total_pages: number
  file_size_kb: number
}

export interface DeliveryLog {
  id: string
  schedule_id: string
  schedule_name: string
  report_name: string
  channel: string
  status: 'sent' | 'failed' | 'pending'
  recipient: string
  sent_at: string
  error_message?: string
}

// Benchmarking Types
export interface BenchmarkData {
  industry: string
  your_organization: {
    emissions_intensity: number // tCO2e per $M revenue
    energy_intensity: number // kWh per $M revenue
    renewable_percentage: number
  }
  industry_average: {
    emissions_intensity: number
    energy_intensity: number
    renewable_percentage: number
  }
  industry_best: {
    emissions_intensity: number
    energy_intensity: number
    renewable_percentage: number
  }
}

export interface PeerComparison {
  your_percentile: number // 0-100
  peers_data: Array<{
    peer_id: string
    emissions_intensity: number
    energy_intensity: number
    renewable_percentage: number
  }>
  your_position: number
  total_peers: number
}

export interface GapAnalysisData {
  metric: string
  your_value: number
  target_value: number
  gap_percentage: number
  unit: string
  priority: 'high' | 'medium' | 'low'
}

export interface ImprovementRecommendation {
  id: string
  title: string
  description: string
  category: 'energy' | 'emissions' | 'renewable' | 'efficiency'
  estimated_impact: {
    emissions_reduction_percent: number
    cost_savings_usd: number
    payback_months: number
  }
  difficulty: 'easy' | 'medium' | 'hard'
  priority_score: number
}

// Alerts Types
export interface AlertItem {
  id: string
  type: 'threshold' | 'anomaly' | 'compliance' | 'system'
  severity: 'critical' | 'high' | 'medium' | 'low'
  title: string
  message: string
  metric?: string
  current_value?: number
  threshold_value?: number
  facility_id?: string
  facility_name?: string
  timestamp: string
  status: 'active' | 'dismissed' | 'snoozed'
  snoozed_until?: string
}

export interface AlertSettings {
  email_enabled: boolean
  email_address: string
  slack_enabled: boolean
  slack_webhook_url?: string
  push_enabled: boolean
  quiet_hours: {
    enabled: boolean
    start_time: string // HH:mm format
    end_time: string
    timezone: string
  }
  severity_filter: Array<'critical' | 'high' | 'medium' | 'low'>
}

export interface AlertRule {
  id: string
  name: string
  metric: string
  condition: 'greater_than' | 'less_than' | 'equals' | 'change_percentage'
  threshold: number
  severity: 'critical' | 'high' | 'medium' | 'low'
  enabled: boolean
  facility_ids: string[] // empty array = all facilities
  notification_channels: Array<'email' | 'slack' | 'push'>
  created_at: string
  updated_at: string
}

export interface CreateAlertRule {
  name: string
  metric: string
  condition: string
  threshold: number
  severity: string
  enabled?: boolean
  facility_ids?: string[]
  notification_channels?: string[]
}

// API Client
class APIClient {
  private baseURL: string
  private token: string | null = null

  constructor(baseURL: string) {
    this.baseURL = baseURL
    this.token = this.getStoredToken()
  }

  private getStoredToken(): string | null {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('auth_token')
    }
    return null
  }

  private setToken(token: string): void {
    this.token = token
    if (typeof window !== 'undefined') {
      localStorage.setItem('auth_token', token)
    }
  }

  private async handleResponse<T>(response: Response): Promise<T> {
    const contentType = response.headers.get('content-type')
    const isJson = contentType?.includes('application/json')

    if (!response.ok) {
      const error: ApiError = {
        status: response.status,
        message: response.statusText,
      }

      if (isJson) {
        try {
          const data = await response.json()
          error.message = data.message || data.detail || error.message
          error.errors = data.errors
        } catch (e) {
          // Continue with default error
        }
      }

      throw error
    }

    if (!isJson) {
      return '' as unknown as T
    }

    return response.json()
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    }

    if (typeof options.headers === 'object' && options.headers !== null) {
      Object.assign(headers, options.headers)
    }

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`
    }

    const response = await fetch(`${this.baseURL}${endpoint}`, {
      ...options,
      headers,
    })

    return this.handleResponse<T>(response)
  }

  // Auth endpoints
  async login(email: string, password: string): Promise<AuthResponse> {
    // Use mock data in dev mode
    if (shouldUseMockData()) {
      console.log('✅ Using mock login response (dev mode)')
      const mockResponse: AuthResponse = {
        access_token: 'mock_token_' + Math.random().toString(36).substr(2, 9),
        token_type: 'bearer',
        user: {
          id: 'user-001',
          email: email || 'demo@inetze ro.local',
          name: email?.split('@')[0] || 'Developer',
          organization_id: 'org-001',
        },
      }
      this.setToken(mockResponse.access_token)
      return mockResponse
    }

    const response = await this.request<AuthResponse>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    })
    this.setToken(response.access_token)
    return response
  }

  async signup(data: {
    email: string
    password: string
    full_name: string
    company: string
  }): Promise<AuthResponse> {
    // Use mock data in dev mode
    if (shouldUseMockData()) {
      console.log('✅ Using mock signup response (dev mode)')
      const mockResponse: AuthResponse = {
        access_token: 'mock_token_' + Math.random().toString(36).substr(2, 9),
        token_type: 'bearer',
        user: {
          id: 'user-' + Math.random().toString(36).substr(2, 9),
          email: data.email,
          name: data.full_name,
          organization_id: 'org-' + Math.random().toString(36).substr(2, 9),
        },
      }
      this.setToken(mockResponse.access_token)
      return mockResponse
    }

    const response = await this.request<AuthResponse>('/auth/signup', {
      method: 'POST',
      body: JSON.stringify(data),
    })
    this.setToken(response.access_token)
    return response
  }

  async logout(): Promise<void> {
    this.token = null
    if (typeof window !== 'undefined') {
      localStorage.removeItem('auth_token')
    }
  }

  // Energy endpoints
  async getEnergyMetrics(facilityId?: string, dateRange?: string): Promise<EnergyMetrics> {
    const params = new URLSearchParams()
    if (facilityId && facilityId !== 'all') {
      params.append('facility_id', facilityId)
    }
    if (dateRange) {
      params.append('date_range', dateRange)
    }

    const queryString = params.toString()
    const url = `/energy/metrics${queryString ? `?${queryString}` : ''}`

    return this.request<EnergyMetrics>(url)
  }

  async getFacilities(): Promise<Facility[]> {
    return this.request<Facility[]>('/facilities')
  }

  async getFacility(id: string): Promise<Facility> {
    return this.request<Facility>(`/facilities/${id}`)
  }

  async getEnergyTrend(facilityId?: string, days?: number): Promise<EnergyData[]> {
    const params = new URLSearchParams()
    if (facilityId) {
      params.append('facility_id', facilityId)
    }
    if (days) {
      params.append('days', days.toString())
    }

    const queryString = params.toString()
    const url = `/energy/trend${queryString ? `?${queryString}` : ''}`

    return this.request<EnergyData[]>(url)
  }

  // Reports endpoints
  async getReports(
    search?: string,
    type?: string,
    status?: string,
    page?: number,
    pageSize?: number
  ): Promise<{ reports: Report[]; total: number; pages: number }> {
    const params = new URLSearchParams()
    if (search) params.append('search', search)
    if (type && type !== 'all') params.append('type', type)
    if (status && status !== 'all') params.append('status', status)
    if (page) params.append('page', page.toString())
    if (pageSize) params.append('page_size', pageSize.toString())

    const queryString = params.toString()
    const url = `/reports${queryString ? `?${queryString}` : ''}`

    return this.request<{ reports: Report[]; total: number; pages: number }>(url)
  }

  async getReport(id: number): Promise<Report> {
    return this.request<Report>(`/reports/${id}`)
  }

  async createReport(data: {
    name: string
    type: string
    date: string
  }): Promise<Report> {
    return this.request<Report>('/reports', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  async downloadReport(id: number): Promise<Blob> {
    const response = await fetch(`${this.baseURL}/reports/${id}/download`, {
      headers: {
        'Authorization': `Bearer ${this.token}`,
      },
    })

    if (!response.ok) {
      throw new Error(`Failed to download report: ${response.statusText}`)
    }

    return response.blob()
  }

  async getComplianceMetrics(): Promise<ComplianceMetrics> {
    return this.request<ComplianceMetrics>('/compliance/metrics')
  }

  async getComplianceStatus(): Promise<any> {
    return this.request('/compliance/status')
  }

  async getComplianceScore(): Promise<any> {
    return this.request('/compliance/score')
  }

  async getComplianceMatrix(framework: string): Promise<any> {
    return this.request(`/compliance/matrix/${framework}`)
  }

  async getComplianceGaps(): Promise<any> {
    return this.request('/compliance/gaps')
  }

  async getRemediationTasks(): Promise<any> {
    return this.request('/compliance/tasks')
  }

  async getTargetTracking(): Promise<any> {
    return this.request('/compliance/targets')
  }

  async getKPITargets(): Promise<any> {
    return this.request('/compliance/kpi-targets')
  }

  async getAuditTrail(): Promise<any> {
    return this.request('/compliance/audit-trail')
  }

  // Settings endpoints
  async getUserProfile(): Promise<UserProfile> {
    return this.request<UserProfile>('/users/profile')
  }

  async updateUserProfile(data: Partial<UserProfile>): Promise<UserProfile> {
    return this.request<UserProfile>('/users/profile', {
      method: 'PUT',
      body: JSON.stringify(data),
    })
  }

  async getOrganizationSettings(): Promise<OrganizationSettings> {
    return this.request<OrganizationSettings>('/organizations/settings')
  }

  async updateOrganizationSettings(
    data: Partial<OrganizationSettings>
  ): Promise<OrganizationSettings> {
    return this.request<OrganizationSettings>('/organizations/settings', {
      method: 'PUT',
      body: JSON.stringify(data),
    })
  }

  // Copilot endpoints
  async askCopilot(question: string): Promise<any> {
    return this.request('/copilot/ask', {
      method: 'POST',
      body: JSON.stringify({ question }),
    })
  }

  async getCopilotHistory(): Promise<any[]> {
    return this.request('/copilot/history')
  }

  // Analytics endpoints
  async getAnalyticsTrends(months: number = 12): Promise<AnalyticsTrend[]> {
    return this.request<AnalyticsTrend[]>(`/analytics/trends?months=${months}`)
  }

  async getEnergyPatterns(facilityId?: string, days: number = 30): Promise<EnergyPattern[]> {
    const params = new URLSearchParams()
    if (facilityId) params.append('facility_id', facilityId)
    params.append('days', days.toString())
    return this.request<EnergyPattern[]>(`/analytics/patterns?${params.toString()}`)
  }

  async getForecast(months: number = 6): Promise<ForecastData> {
    return this.request<ForecastData>(`/analytics/forecast?months=${months}`)
  }

  async getSustainabilityScore(): Promise<SustainabilityScore> {
    return this.request<SustainabilityScore>('/analytics/sustainability-score')
  }

  async exportAnalytics(format: 'pdf' | 'csv' = 'pdf'): Promise<Blob> {
    const response = await fetch(`${this.baseURL}/analytics/export?format=${format}`, {
      headers: { 'Authorization': `Bearer ${this.token}` },
    })
    if (!response.ok) throw new Error('Failed to export analytics')
    return response.blob()
  }

  // Reporting endpoints
  async getReportTemplates(): Promise<ReportTemplate[]> {
    return this.request<ReportTemplate[]>('/reporting/templates')
  }

  async createReportTemplate(data: CreateReportTemplate): Promise<ReportTemplate> {
    return this.request<ReportTemplate>('/reporting/templates', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  async updateReportTemplate(id: string, data: Partial<ReportTemplate>): Promise<ReportTemplate> {
    return this.request<ReportTemplate>(`/reporting/templates/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    })
  }

  async deleteReportTemplate(id: string): Promise<void> {
    return this.request(`/reporting/templates/${id}`, { method: 'DELETE' })
  }

  async getReportSchedules(): Promise<ReportSchedule[]> {
    return this.request<ReportSchedule[]>('/reporting/schedules')
  }

  async createReportSchedule(data: CreateReportSchedule): Promise<ReportSchedule> {
    return this.request<ReportSchedule>('/reporting/schedules', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  async updateReportSchedule(id: string, data: Partial<ReportSchedule>): Promise<ReportSchedule> {
    return this.request<ReportSchedule>(`/reporting/schedules/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    })
  }

  async deleteReportSchedule(id: string): Promise<void> {
    return this.request(`/reporting/schedules/${id}`, { method: 'DELETE' })
  }

  async previewReport(templateId: string, filters?: any): Promise<ReportPreview> {
    return this.request<ReportPreview>('/reporting/preview', {
      method: 'POST',
      body: JSON.stringify({ template_id: templateId, filters }),
    })
  }

  async getDeliveryLog(scheduleId?: string): Promise<DeliveryLog[]> {
    const url = scheduleId ? `/reporting/delivery-log?schedule_id=${scheduleId}` : '/reporting/delivery-log'
    return this.request<DeliveryLog[]>(url)
  }

  async resendReport(deliveryId: string): Promise<void> {
    return this.request(`/reporting/delivery-log/${deliveryId}/resend`, { method: 'POST' })
  }

  // Benchmarking endpoints
  async getBenchmarks(industry?: string): Promise<BenchmarkData> {
    const url = industry ? `/benchmarking?industry=${industry}` : '/benchmarking'
    return this.request<BenchmarkData>(url)
  }

  async getPeerComparison(): Promise<PeerComparison> {
    return this.request<PeerComparison>('/benchmarking/peer-comparison')
  }

  async getGapAnalysis(): Promise<GapAnalysisData[]> {
    return this.request<GapAnalysisData[]>('/benchmarking/gap-analysis')
  }

  async getImprovementPlan(): Promise<ImprovementRecommendation[]> {
    return this.request<ImprovementRecommendation[]>('/benchmarking/improvement-plan')
  }

  async exportBenchmarks(format: 'pdf' | 'csv' = 'pdf'): Promise<Blob> {
    const response = await fetch(`${this.baseURL}/benchmarking/export?format=${format}`, {
      headers: { 'Authorization': `Bearer ${this.token}` },
    })
    if (!response.ok) throw new Error('Failed to export benchmarks')
    return response.blob()
  }

  // Alerts endpoints
  async getAlerts(status?: 'active' | 'dismissed' | 'snoozed'): Promise<AlertItem[]> {
    const url = status ? `/alerts?status=${status}` : '/alerts'
    return this.request<AlertItem[]>(url)
  }

  async getAlertHistory(limit: number = 50): Promise<AlertItem[]> {
    return this.request<AlertItem[]>(`/alerts/history?limit=${limit}`)
  }

  async dismissAlert(id: string): Promise<void> {
    return this.request(`/alerts/${id}/dismiss`, { method: 'POST' })
  }

  async snoozeAlert(id: string, minutes: number): Promise<void> {
    return this.request(`/alerts/${id}/snooze`, {
      method: 'POST',
      body: JSON.stringify({ minutes }),
    })
  }

  async getAlertSettings(): Promise<AlertSettings> {
    return this.request<AlertSettings>('/alerts/settings')
  }

  async updateAlertSettings(data: Partial<AlertSettings>): Promise<AlertSettings> {
    return this.request<AlertSettings>('/alerts/settings', {
      method: 'PUT',
      body: JSON.stringify(data),
    })
  }

  async getAlertRules(): Promise<AlertRule[]> {
    return this.request<AlertRule[]>('/alerts/rules')
  }

  async createAlertRule(data: CreateAlertRule): Promise<AlertRule> {
    return this.request<AlertRule>('/alerts/rules', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  async updateAlertRule(id: string, data: Partial<AlertRule>): Promise<AlertRule> {
    return this.request<AlertRule>(`/alerts/rules/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    })
  }

  async deleteAlertRule(id: string): Promise<void> {
    return this.request(`/alerts/rules/${id}`, { method: 'DELETE' })
  }

  // ============================================================================
  // MARKETPLACE, TRADING, & PORTFOLIO ENDPOINTS (Sprint 8)
  // ============================================================================

  // Carbon Credit Management
  async createCreditBatch(orgId: string, data: {
    batch_name: string
    total_quantity: number
    credit_type?: string
    vintage_year: number
    description?: string
    quality_score?: number
  }): Promise<any> {
    const params = new URLSearchParams({
      batch_name: data.batch_name,
      total_quantity: String(data.total_quantity),
      vintage_year: String(data.vintage_year),
      credit_type: data.credit_type || 'verified',
      quality_score: String(data.quality_score || 100),
    })
    if (data.description) params.set('description', data.description)

    return this.request(`/organizations/${orgId}/credits/create-batch?${params.toString()}`, {
      method: 'POST',
    })
  }

  async getOrganizationCredits(orgId: string, status: string = 'active'): Promise<any> {
    return this.request(`/organizations/${orgId}/credits?status=${status}`)
  }

  async retireCredits(orgId: string, creditId: string, quantity: number, reason?: string): Promise<any> {
    const params = new URLSearchParams({
      quantity: String(quantity),
    })
    if (reason) params.set('reason', reason)

    return this.request(`/organizations/${orgId}/credits/${creditId}/retire?${params.toString()}`, {
      method: 'POST',
    })
  }

  // Marketplace Listings
  async createMarketplaceListing(orgId: string, data: {
    batch_id: string
    quantity: number
    price_per_credit: number
    listing_type: string
    expires_in_days?: number
    minimum_bid?: number
  }): Promise<any> {
    const params = new URLSearchParams({
      batch_id: data.batch_id,
      quantity: String(data.quantity),
      price_per_credit: String(data.price_per_credit),
      listing_type: data.listing_type,
      expires_in_days: String(data.expires_in_days || 30),
    })
    if (data.minimum_bid) params.set('minimum_bid', String(data.minimum_bid))

    return this.request(`/organizations/${orgId}/marketplace/listings?${params.toString()}`, {
      method: 'POST',
    })
  }

  async getMarketplaceListings(filters?: {
    min_price?: number
    max_price?: number
    limit?: number
  }): Promise<any> {
    const params = new URLSearchParams()
    if (filters?.min_price) params.set('min_price', String(filters.min_price))
    if (filters?.max_price) params.set('max_price', String(filters.max_price))
    if (filters?.limit) params.set('limit', String(filters.limit))

    return this.request(`/marketplace/listings?${params.toString()}`)
  }

  async getMarketplaceListing(listingId: string): Promise<any> {
    return this.request(`/marketplace/listings/${listingId}`)
  }

  // Trading
  async executeTrade(data: {
    listing_id: string
    quantity: number
    agreed_price?: number
  }): Promise<any> {
    const params = new URLSearchParams({
      listing_id: data.listing_id,
      quantity: String(data.quantity),
    })
    if (data.agreed_price) params.set('agreed_price', String(data.agreed_price))

    return this.request(`/trades/execute?${params.toString()}`, {
      method: 'POST',
    })
  }

  async getTradeHistory(orgId: string, role: string = 'all', limit: number = 100): Promise<any> {
    return this.request(`/organizations/${orgId}/trades?role=${role}&limit=${limit}`)
  }

  async completeTrade(tradeId: string, paymentConfirmed: boolean = true): Promise<any> {
    return this.request(`/trades/${tradeId}/complete?payment_confirmed=${paymentConfirmed}`, {
      method: 'POST',
    })
  }

  // Marketplace Analytics
  async getMarketPriceHistory(days: number = 30): Promise<any> {
    return this.request(`/marketplace/analytics/price-history?days=${days}`)
  }

  async getTradingVolume(days: number = 30): Promise<any> {
    return this.request(`/marketplace/analytics/volume?days=${days}`)
  }

  async getMarketInsights(): Promise<any> {
    return this.request('/marketplace/analytics/market-insights')
  }

  // Utility endpoints
  async healthCheck(): Promise<{ status: string; version: string }> {
    try {
      return await this.request('/health')
    } catch (error) {
      return { status: 'error', version: 'unknown' }
    }
  }

  // Generic get/post methods for flexible endpoint access
  async get<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'GET' })
  }

  async post<T>(endpoint: string, data?: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  async put<T>(endpoint: string, data?: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data),
    })
  }

  async delete<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'DELETE' })
  }
}

// Create singleton instance
export const api = new APIClient(API_BASE_URL)

export default api
