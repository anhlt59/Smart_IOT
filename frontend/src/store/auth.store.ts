import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User, AuthUser } from '../core/types'
import { STORAGE_KEYS } from '../core/constants'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const token = ref<string | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  const isAuthenticated = computed(() => !!token.value && !!user.value)
  const userRole = computed(() => user.value?.role)

  // Initialize from localStorage
  const initialize = () => {
    const storedToken = localStorage.getItem(STORAGE_KEYS.AUTH_TOKEN)
    const storedUser = localStorage.getItem(STORAGE_KEYS.USER_DATA)

    if (storedToken && storedUser) {
      token.value = storedToken
      try {
        user.value = JSON.parse(storedUser)
      } catch (e) {
        console.error('Failed to parse stored user data', e)
        clearAuth()
      }
    }
  }

  const login = async (email: string, password: string) => {
    loading.value = true
    error.value = null

    try {
      // TODO: Replace with actual API call
      // const response = await authApi.login(email, password)

      // Mock data for now
      const mockUser: User = {
        userId: '1',
        email,
        name: 'Test User',
        role: 'admin' as any,
        organizationId: 'org-1',
        preferences: {
          theme: 'light',
          language: 'en',
          timezone: 'UTC',
          dateFormat: 'MMM dd, yyyy',
          notifications: {
            email: { critical: true, warning: true, info: false },
            push: { critical: true, warning: false, info: false },
            sms: { critical: true, warning: false, info: false },
          },
        },
        createdAt: new Date().toISOString(),
      }

      const mockToken = 'mock-jwt-token-' + Date.now()

      setAuth(mockUser, mockToken)
      return true
    } catch (err: any) {
      error.value = err.message || 'Login failed'
      return false
    } finally {
      loading.value = false
    }
  }

  const logout = () => {
    clearAuth()
  }

  const setAuth = (userData: User, authToken: string) => {
    user.value = userData
    token.value = authToken
    localStorage.setItem(STORAGE_KEYS.AUTH_TOKEN, authToken)
    localStorage.setItem(STORAGE_KEYS.USER_DATA, JSON.stringify(userData))
  }

  const clearAuth = () => {
    user.value = null
    token.value = null
    localStorage.removeItem(STORAGE_KEYS.AUTH_TOKEN)
    localStorage.removeItem(STORAGE_KEYS.USER_DATA)
  }

  const updateUser = (userData: Partial<User>) => {
    if (user.value) {
      user.value = { ...user.value, ...userData }
      localStorage.setItem(STORAGE_KEYS.USER_DATA, JSON.stringify(user.value))
    }
  }

  const hasPermission = (permission: string): boolean => {
    // TODO: Implement proper permission check based on user role
    return isAuthenticated.value
  }

  return {
    user,
    token,
    loading,
    error,
    isAuthenticated,
    userRole,
    initialize,
    login,
    logout,
    setAuth,
    updateUser,
    hasPermission,
  }
})
