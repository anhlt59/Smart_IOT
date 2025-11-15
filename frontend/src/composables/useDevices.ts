import { ref, computed } from 'vue'
import { devicesApiService, type DeviceFilterParams } from '@/api/modules/devices.api'
import type { Device, SensorReading } from '@/core/types/device'
import type { PaginatedResponse } from '@/core/types/api'

export function useDevices() {
  const devices = ref<Device[]>([])
  const currentDevice = ref<Device | null>(null)
  const deviceHistory = ref<SensorReading[]>([])
  const pagination = ref<Omit<PaginatedResponse<Device>, 'items'>>({
    total: 0,
    page: 1,
    pageSize: 25,
    totalPages: 0,
    hasNext: false,
    hasPrevious: false,
  })

  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // Computed statistics
  const deviceStats = computed(() => {
    const total = devices.value.length
    const online = devices.value.filter((d) => d.status === 'online').length
    const offline = devices.value.filter((d) => d.status === 'offline').length
    const warning = devices.value.filter((d) => d.status === 'warning').length
    const error = devices.value.filter((d) => d.status === 'error').length

    return { total, online, offline, warning, error }
  })

  /**
   * Fetch devices with filters and pagination
   */
  const fetchDevices = async (params?: DeviceFilterParams) => {
    isLoading.value = true
    error.value = null

    try {
      const response = await devicesApiService.listDevices(params)

      if (response.success) {
        devices.value = response.data.items
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
      error.value = err?.error?.message || 'Failed to fetch devices'
      console.error('Error fetching devices:', err)
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Fetch a single device by ID
   */
  const fetchDevice = async (deviceId: string) => {
    isLoading.value = true
    error.value = null

    try {
      const response = await devicesApiService.getDevice(deviceId)

      if (response.success) {
        currentDevice.value = response.data
      }
    } catch (err: any) {
      error.value = err?.error?.message || 'Failed to fetch device'
      console.error('Error fetching device:', err)
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Fetch device history
   */
  const fetchDeviceHistory = async (
    deviceId: string,
    params?: {
      metric?: string
      startDate?: string
      endDate?: string
      interval?: string
      limit?: number
    }
  ) => {
    isLoading.value = true
    error.value = null

    try {
      const response = await devicesApiService.getDeviceHistory(deviceId, params)

      if (response.success) {
        deviceHistory.value = response.data
      }
    } catch (err: any) {
      error.value = err?.error?.message || 'Failed to fetch device history'
      console.error('Error fetching device history:', err)
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Register a new device
   */
  const registerDevice = async (device: Partial<Device>) => {
    isLoading.value = true
    error.value = null

    try {
      const response = await devicesApiService.registerDevice(device)

      if (response.success) {
        // Add new device to the list
        devices.value.unshift(response.data)
        return response.data
      }
    } catch (err: any) {
      error.value = err?.error?.message || 'Failed to register device'
      console.error('Error registering device:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Update device
   */
  const updateDevice = async (deviceId: string, updates: Partial<Device>) => {
    isLoading.value = true
    error.value = null

    try {
      const response = await devicesApiService.updateDevice(deviceId, updates)

      if (response.success) {
        // Update device in the list
        const index = devices.value.findIndex((d) => d.deviceId === deviceId)
        if (index !== -1) {
          devices.value[index] = response.data
        }

        // Update current device if it's the same
        if (currentDevice.value?.deviceId === deviceId) {
          currentDevice.value = response.data
        }

        return response.data
      }
    } catch (err: any) {
      error.value = err?.error?.message || 'Failed to update device'
      console.error('Error updating device:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Delete device
   */
  const deleteDevice = async (deviceId: string) => {
    isLoading.value = true
    error.value = null

    try {
      const response = await devicesApiService.deleteDevice(deviceId)

      if (response.success) {
        // Remove device from the list
        devices.value = devices.value.filter((d) => d.deviceId !== deviceId)

        // Clear current device if it's the same
        if (currentDevice.value?.deviceId === deviceId) {
          currentDevice.value = null
        }
      }
    } catch (err: any) {
      error.value = err?.error?.message || 'Failed to delete device'
      console.error('Error deleting device:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Fetch devices for dashboard
   */
  const fetchDashboardDevices = async () => {
    isLoading.value = true
    error.value = null

    try {
      const response = await devicesApiService.getDashboardDevices()

      if (response.success) {
        devices.value = response.data
      }
    } catch (err: any) {
      error.value = err?.error?.message || 'Failed to fetch dashboard devices'
      console.error('Error fetching dashboard devices:', err)
    } finally {
      isLoading.value = false
    }
  }

  return {
    // State
    devices,
    currentDevice,
    deviceHistory,
    pagination,
    isLoading,
    error,

    // Computed
    deviceStats,

    // Methods
    fetchDevices,
    fetchDevice,
    fetchDeviceHistory,
    registerDevice,
    updateDevice,
    deleteDevice,
    fetchDashboardDevices,
  }
}
