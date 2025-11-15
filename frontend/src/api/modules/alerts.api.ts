import apiClient from '../client'
import type { ApiResponse, PaginatedResponse, PaginationParams, FilterParams } from '@/core/types/api'
import type { Alert, AlertRule, AlertStats } from '@/core/types/alert'

export interface AlertFilterParams extends FilterParams, PaginationParams {
  severity?: string
  deviceId?: string
  ruleId?: string
}

export interface AcknowledgeAlertRequest {
  notes?: string
}

export interface ResolveAlertRequest {
  notes?: string
  resolution?: string
}

export const alertsApiService = {
  /**
   * List alerts with filters and pagination
   */
  async listAlerts(params?: AlertFilterParams): Promise<ApiResponse<PaginatedResponse<Alert>>> {
    const response = await apiClient.get<ApiResponse<PaginatedResponse<Alert>>>('/alerts', {
      params,
    })
    return response.data
  },

  /**
   * Get alert by ID
   */
  async getAlert(alertId: string): Promise<ApiResponse<Alert>> {
    const response = await apiClient.get<ApiResponse<Alert>>(`/alerts/${alertId}`)
    return response.data
  },

  /**
   * Acknowledge an alert
   */
  async acknowledgeAlert(alertId: string, data?: AcknowledgeAlertRequest): Promise<ApiResponse<Alert>> {
    const response = await apiClient.post<ApiResponse<Alert>>(
      `/alerts/${alertId}/acknowledge`,
      data || {}
    )
    return response.data
  },

  /**
   * Resolve an alert
   */
  async resolveAlert(alertId: string, data?: ResolveAlertRequest): Promise<ApiResponse<Alert>> {
    const response = await apiClient.post<ApiResponse<Alert>>(
      `/alerts/${alertId}/resolve`,
      data || {}
    )
    return response.data
  },

  /**
   * Get alert statistics
   */
  async getAlertStats(params?: { startDate?: string; endDate?: string }): Promise<ApiResponse<AlertStats>> {
    const response = await apiClient.get<ApiResponse<AlertStats>>('/alerts/stats', {
      params,
    })
    return response.data
  },

  /**
   * Get recent alerts for dashboard
   */
  async getRecentAlerts(limit: number = 10): Promise<ApiResponse<Alert[]>> {
    const response = await apiClient.get<ApiResponse<PaginatedResponse<Alert>>>('/alerts', {
      params: {
        page: 1,
        pageSize: limit,
        sortBy: 'triggeredAt',
        sortOrder: 'desc',
      },
    })
    // Extract items from paginated response
    const paginatedData = response.data as ApiResponse<PaginatedResponse<Alert>>
    return {
      ...paginatedData,
      data: paginatedData.data.items,
    }
  },
}
