import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import api, { AuthResponse } from '../services/api'

interface User {
  id: string
  email: string
  name: string
  organization_id: string
}

interface AuthContextType {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (email: string, password: string) => Promise<boolean>
  signup: (email: string, password: string, fullName: string, company: string) => Promise<boolean>
  logout: () => Promise<void>
  token: string | null
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [token, setToken] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isAuthenticated, setIsAuthenticated] = useState(false)

  // Initialize auth state on mount
  useEffect(() => {
    const initializeAuth = async () => {
      const isLocalhost = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'

      // Auto-enable dev mode on localhost
      if (isLocalhost) {
        localStorage.setItem('BYPASS_AUTH', 'true')
        localStorage.setItem('USE_MOCK_API', 'true')
      }

      const devMode = isLocalhost || localStorage.getItem('BYPASS_AUTH') === 'true'
      const storedToken = localStorage.getItem('auth_token')
      const storedUser = localStorage.getItem('auth_user')

      if (devMode || (storedToken && storedUser)) {
        setToken(storedToken)
        setIsAuthenticated(true)
        if (storedUser) {
          setUser(JSON.parse(storedUser))
        } else if (devMode) {
          // Create mock user for dev mode
          const mockUser: User = {
            id: 'dev-user-001',
            email: 'dev@inetze ro.local',
            name: 'Developer',
            organization_id: 'dev-org-001',
          }
          setUser(mockUser)
        }
      }
      setIsLoading(false)
    }

    initializeAuth()
  }, [])

  const login = async (email: string, password: string): Promise<boolean> => {
    try {
      setIsLoading(true)
      const response: AuthResponse = await api.login(email, password)

      const newUser: User = {
        id: response.user.id,
        email: response.user.email,
        name: response.user.name,
        organization_id: response.user.organization_id,
      }

      setToken(response.access_token)
      setUser(newUser)
      setIsAuthenticated(true)

      // Persist to localStorage
      localStorage.setItem('auth_token', response.access_token)
      localStorage.setItem('auth_user', JSON.stringify(newUser))

      return true
    } catch (error) {
      console.error('Login failed:', error)
      setIsAuthenticated(false)
      return false
    } finally {
      setIsLoading(false)
    }
  }

  const signup = async (
    email: string,
    password: string,
    fullName: string,
    company: string
  ): Promise<boolean> => {
    try {
      setIsLoading(true)
      const response: AuthResponse = await api.signup({
        email,
        password,
        full_name: fullName,
        company,
      })

      const newUser: User = {
        id: response.user.id,
        email: response.user.email,
        name: response.user.name,
        organization_id: response.user.organization_id,
      }

      setToken(response.access_token)
      setUser(newUser)
      setIsAuthenticated(true)

      // Persist to localStorage
      localStorage.setItem('auth_token', response.access_token)
      localStorage.setItem('auth_user', JSON.stringify(newUser))

      return true
    } catch (error) {
      console.error('Signup failed:', error)
      setIsAuthenticated(false)
      return false
    } finally {
      setIsLoading(false)
    }
  }

  const logout = async (): Promise<void> => {
    try {
      setIsLoading(true)
      await api.logout()

      setToken(null)
      setUser(null)
      setIsAuthenticated(false)

      // Clear localStorage
      localStorage.removeItem('auth_token')
      localStorage.removeItem('auth_user')
    } catch (error) {
      console.error('Logout failed:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const value: AuthContextType = {
    user,
    isAuthenticated,
    isLoading,
    login,
    signup,
    logout,
    token,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth(): AuthContextType {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
