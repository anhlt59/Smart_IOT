import { UserRole } from '../enums'

export interface UserPreferences {
  theme: 'light' | 'dark' | 'auto'
  language: string
  timezone: string
  dateFormat: string
  notifications: {
    email: {
      critical: boolean
      warning: boolean
      info: boolean
    }
    push: {
      critical: boolean
      warning: boolean
      info: boolean
    }
    sms: {
      critical: boolean
      warning: boolean
      info: boolean
    }
  }
  quietHours?: {
    enabled: boolean
    start: string
    end: string
    allowCritical: boolean
  }
}

export interface User {
  userId: string
  email: string
  name: string
  role: UserRole
  organizationId: string
  avatar?: string
  phone?: string
  preferences: UserPreferences
  createdAt: string
  lastLoginAt?: string
}

export interface AuthUser extends User {
  token: string
  refreshToken?: string
  expiresAt?: number
}
