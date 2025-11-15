// API Configuration
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:3000/api'
export const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:3000'

// Pagination
export const DEFAULT_PAGE_SIZE = 25
export const PAGE_SIZE_OPTIONS = [10, 25, 50, 100]

// Chart refresh rates (milliseconds)
export const CHART_REFRESH_RATE = 5000
export const DASHBOARD_REFRESH_RATE = 30000

// Date/Time formats
export const DATE_FORMAT = 'MMM dd, yyyy'
export const TIME_FORMAT = 'HH:mm:ss'
export const DATETIME_FORMAT = 'MMM dd, yyyy HH:mm:ss'

// Thresholds
export const BATTERY_LOW_THRESHOLD = 20
export const BATTERY_WARNING_THRESHOLD = 40
export const SIGNAL_WEAK_THRESHOLD = -70
export const SIGNAL_GOOD_THRESHOLD = -50

// Local Storage Keys
export const STORAGE_KEYS = {
  AUTH_TOKEN: 'auth_token',
  USER_DATA: 'user_data',
  THEME: 'theme',
  LANGUAGE: 'language',
  SIDEBAR_COLLAPSED: 'sidebar_collapsed',
} as const

// App Info
export const APP_NAME = 'IoT Monitoring'
export const APP_VERSION = '1.0.0'
