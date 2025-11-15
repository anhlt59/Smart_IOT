import { ref, computed } from 'vue'
import { alertsApiService, type AlertFilterParams } from '@/api/modules/alerts.api'
import type { Alert, AlertStats } from '@/core/types/alert'
import type { PaginatedResponse } from '@/core/types/api'

export function useAlerts() {
  const alerts = ref<Alert[]>([])
  const currentAlert = ref<Alert | null>(null)
  const alertStats = ref<AlertStats>({
    total: 0,
    critical: 0,
    warning: 0,
    info: 0,
    triggered: 0,
    acknowledged: 0,
    resolved: 0,
  })
  const pagination = ref<Omit<PaginatedResponse<Alert>, 'items'>>({
    total: 0,
    page: 1,
    pageSize: 25,
    totalPages: 0,
    hasNext: false,
    hasPrevious: false,
  })

  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // Computed - unread (triggered) alerts count
  const unreadCount = computed(() => {
    return alerts.value.filter((alert) => alert.status === 'triggered').length
  })

  // Computed - critical alerts
  const criticalAlerts = computed(() => {
    return alerts.value.filter((alert) => alert.severity === 'critical')
  })

  /**
   * Fetch alerts with filters and pagination
   */
  const fetchAlerts = async (params?: AlertFilterParams) => {
    isLoading.value = true
    error.value = null

    try {
      const response = await alertsApiService.listAlerts(params)

      if (response.success) {
        alerts.value = response.data.items
        pagination.value = {
          total: response.data.total,
          page: response.data.page,
          pageSize: response.data.pageSize,
          totalPages: response.data.totalPages,
          hasNext: response.data.hasNext,
          hasPrevious: response.data.hasPrevious,
        }
      }
    } catch (err: any) {
      error.value = err?.error?.message || 'Failed to fetch alerts'
      console.error('Error fetching alerts:', err)
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Fetch a single alert by ID
   */
  const fetchAlert = async (alertId: string) => {
    isLoading.value = true
    error.value = null

    try {
      const response = await alertsApiService.getAlert(alertId)

      if (response.success) {
        currentAlert.value = response.data
      }
    } catch (err: any) {
      error.value = err?.error?.message || 'Failed to fetch alert'
      console.error('Error fetching alert:', err)
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Fetch alert statistics
   */
  const fetchAlertStats = async (params?: { startDate?: string; endDate?: string }) => {
    isLoading.value = true
    error.value = null

    try {
      const response = await alertsApiService.getAlertStats(params)

      if (response.success) {
        alertStats.value = response.data
      }
    } catch (err: any) {
      error.value = err?.error?.message || 'Failed to fetch alert statistics'
      console.error('Error fetching alert statistics:', err)
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Fetch recent alerts for dashboard
   */
  const fetchRecentAlerts = async (limit: number = 10) => {
    isLoading.value = true
    error.value = null

    try {
      const response = await alertsApiService.getRecentAlerts(limit)

      if (response.success) {
        alerts.value = response.data
      }
    } catch (err: any) {
      error.value = err?.error?.message || 'Failed to fetch recent alerts'
      console.error('Error fetching recent alerts:', err)
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Acknowledge an alert
   */
  const acknowledgeAlert = async (alertId: string, notes?: string) => {
    isLoading.value = true
    error.value = null

    try {
      const response = await alertsApiService.acknowledgeAlert(alertId, { notes })

      if (response.success) {
        // Update alert in the list
        const index = alerts.value.findIndex((a) => a.alertId === alertId)
        if (index !== -1) {
          alerts.value[index] = response.data
        }

        // Update current alert if it's the same
        if (currentAlert.value?.alertId === alertId) {
          currentAlert.value = response.data
        }

        return response.data
      }
    } catch (err: any) {
      error.value = err?.error?.message || 'Failed to acknowledge alert'
      console.error('Error acknowledging alert:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Resolve an alert
   */
  const resolveAlert = async (alertId: string, notes?: string, resolution?: string) => {
    isLoading.value = true
    error.value = null

    try {
      const response = await alertsApiService.resolveAlert(alertId, { notes, resolution })

      if (response.success) {
        // Update alert in the list
        const index = alerts.value.findIndex((a) => a.alertId === alertId)
        if (index !== -1) {
          alerts.value[index] = response.data
        }

        // Update current alert if it's the same
        if (currentAlert.value?.alertId === alertId) {
          currentAlert.value = response.data
        }

        return response.data
      }
    } catch (err: any) {
      error.value = err?.error?.message || 'Failed to resolve alert'
      console.error('Error resolving alert:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  return {
    // State
    alerts,
    currentAlert,
    alertStats,
    pagination,
    isLoading,
    error,

    // Computed
    unreadCount,
    criticalAlerts,

    // Methods
    fetchAlerts,
    fetchAlert,
    fetchAlertStats,
    fetchRecentAlerts,
    acknowledgeAlert,
    resolveAlert,
  }
}
