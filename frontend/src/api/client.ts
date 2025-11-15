import axios, { AxiosInstance, AxiosError, InternalAxiosRequestConfig } from 'axios'
import { API_BASE_URL, STORAGE_KEYS } from '@/core/constants'
import type { ApiResponse, ApiError } from '@/core/types/api'

// Create axios instance with default config
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor - Add auth token
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem(STORAGE_KEYS.AUTH_TOKEN)
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error: AxiosError) => {
    return Promise.reject(error)
  }
)

// Response interceptor - Handle errors
apiClient.interceptors.response.use(
  (response) => {
    return response
  },
  (error: AxiosError<ApiError>) => {
    if (error.response) {
      // Server responded with error status
      const apiError = error.response.data

      // Handle specific status codes
      switch (error.response.status) {
        case 401:
          // Unauthorized - clear token and redirect to login
          localStorage.removeItem(STORAGE_KEYS.AUTH_TOKEN)
          localStorage.removeItem(STORAGE_KEYS.USER_DATA)
          window.location.href = '/login'
          break
        case 403:
          console.error('Access forbidden:', apiError)
          break
        case 404:
          console.error('Resource not found:', apiError)
          break
        case 500:
          console.error('Server error:', apiError)
          break
        default:
          console.error('API error:', apiError)
      }

      return Promise.reject(apiError)
    } else if (error.request) {
      // Request made but no response received
      console.error('Network error - no response:', error.request)
      return Promise.reject({
        success: false,
        error: {
          code: 'NETWORK_ERROR',
          message: 'Unable to connect to the server. Please check your internet connection.',
        },
        timestamp: new Date().toISOString(),
      } as ApiError)
    } else {
      // Error in setting up the request
      console.error('Request setup error:', error.message)
      return Promise.reject({
        success: false,
        error: {
          code: 'REQUEST_ERROR',
          message: error.message,
        },
        timestamp: new Date().toISOString(),
      } as ApiError)
    }
  }
)

export default apiClient
