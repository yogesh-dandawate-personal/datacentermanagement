/**
 * API Service Layer
 * Centralized API client for all backend communication
 */

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1'

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
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...options.headers,
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

  // Utility endpoints
  async healthCheck(): Promise<{ status: string; version: string }> {
    try {
      return await this.request('/health')
    } catch (error) {
      return { status: 'error', version: 'unknown' }
    }
  }
}

// Create singleton instance
export const api = new APIClient(API_BASE_URL)

export default api
