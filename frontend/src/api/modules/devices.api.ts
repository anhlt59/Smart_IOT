import apiClient from '../client'
import type { ApiResponse, PaginatedResponse, PaginationParams, FilterParams } from '@/core/types/api'
import type { Device, SensorReading } from '@/core/types/device'

export interface DeviceFilterParams extends FilterParams, PaginationParams {
  organizationId?: string
  deviceType?: string
  location?: string
}

export interface DeviceHistoryParams {
  metric?: string
  startDate?: string
  endDate?: string
  interval?: string
  limit?: number
}

export const devicesApiService = {
  /**
   * Register a new device
   */
  async registerDevice(device: Partial<Device>): Promise<ApiResponse<Device>> {
    const response = await apiClient.post<ApiResponse<Device>>('/devices', device)
    return response.data
  },

  /**
   * Get device by ID
   */
  async getDevice(deviceId: string): Promise<ApiResponse<Device>> {
    const response = await apiClient.get<ApiResponse<Device>>(`/devices/${deviceId}`)
    return response.data
  },

  /**
   * List devices with filters and pagination
   */
  async listDevices(params?: DeviceFilterParams): Promise<ApiResponse<PaginatedResponse<Device>>> {
    const response = await apiClient.get<ApiResponse<PaginatedResponse<Device>>>('/devices', {
      params,
    })
    return response.data
  },

  /**
   * Update device metadata
   */
  async updateDevice(deviceId: string, updates: Partial<Device>): Promise<ApiResponse<Device>> {
    const response = await apiClient.put<ApiResponse<Device>>(`/devices/${deviceId}`, updates)
    return response.data
  },

  /**
   * Delete device
   */
  async deleteDevice(deviceId: string): Promise<ApiResponse<void>> {
    const response = await apiClient.delete<ApiResponse<void>>(`/devices/${deviceId}`)
    return response.data
  },

  /**
   * Get device sensor data history
   */
  async getDeviceHistory(
    deviceId: string,
    params?: DeviceHistoryParams
  ): Promise<ApiResponse<SensorReading[]>> {
    const response = await apiClient.get<ApiResponse<SensorReading[]>>(
      `/devices/${deviceId}/history`,
      {
        params,
      }
    )
    return response.data
  },

  /**
   * Get all devices for dashboard (simplified)
   */
  async getDashboardDevices(): Promise<ApiResponse<Device[]>> {
    const response = await apiClient.get<ApiResponse<Device[]>>('/devices', {
      params: {
        page: 1,
        pageSize: 100,
      },
    })
    // Extract items from paginated response
    const paginatedData = response.data as unknown as ApiResponse<PaginatedResponse<Device>>
    return {
      ...paginatedData,
      data: paginatedData.data.items,
    }
  },
}
