<template>
  <div class="p-6">
    <!-- Page Header -->
    <div class="mb-6">
      <h1 class="text-2xl font-bold text-gray-900 dark:text-white">Dashboard</h1>
      <p class="text-gray-600 dark:text-gray-400">Overview of your IoT devices and alerts</p>
    </div>

    <!-- Loading State -->
    <div v-if="devicesLoading || alertsLoading" class="flex items-center justify-center h-64">
      <div class="text-center">
        <div class="text-6xl mb-4">⏳</div>
        <p class="text-gray-600 dark:text-gray-400">Loading dashboard data...</p>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="devicesError || alertsError" class="bg-red-50 dark:bg-red-900/20 p-4 rounded-lg mb-6">
      <p class="text-red-600 dark:text-red-400">{{ devicesError || alertsError }}</p>
    </div>

    <!-- Dashboard Content -->
    <template v-else>
      <!-- Stats Cards -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
        <!-- Online Devices -->
        <BaseCard>
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-gray-600 dark:text-gray-400">Online Devices</p>
              <p class="text-3xl font-bold text-gray-900 dark:text-white mt-2">{{ deviceStats.online }}</p>
              <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">{{ deviceStats.total }} total</p>
            </div>
            <div class="w-12 h-12 bg-success-100 dark:bg-success-900/30 rounded-lg flex items-center justify-center">
              <span class="text-2xl">🟢</span>
            </div>
          </div>
        </BaseCard>

        <!-- Offline/Warning Devices -->
        <BaseCard>
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-gray-600 dark:text-gray-400">Issues</p>
              <p class="text-3xl font-bold text-gray-900 dark:text-white mt-2">{{ deviceStats.offline + deviceStats.warning }}</p>
              <p class="text-sm text-danger-600 dark:text-danger-400 mt-1">
                {{ deviceStats.offline }} offline, {{ deviceStats.warning }} warning
              </p>
            </div>
            <div class="w-12 h-12 bg-danger-100 dark:bg-danger-900/30 rounded-lg flex items-center justify-center">
              <span class="text-2xl">🔴</span>
            </div>
          </div>
        </BaseCard>

        <!-- Active Alerts -->
        <BaseCard>
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-gray-600 dark:text-gray-400">Active Alerts</p>
              <p class="text-3xl font-bold text-gray-900 dark:text-white mt-2">{{ unreadAlertsCount }}</p>
              <p class="text-sm text-warning-600 dark:text-warning-400 mt-1">{{ criticalAlertsCount }} critical</p>
            </div>
            <div class="w-12 h-12 bg-warning-100 dark:bg-warning-900/30 rounded-lg flex items-center justify-center">
              <span class="text-2xl">⚠️</span>
            </div>
          </div>
        </BaseCard>

        <!-- Total Devices -->
        <BaseCard>
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-gray-600 dark:text-gray-400">Total Devices</p>
              <p class="text-3xl font-bold text-gray-900 dark:text-white mt-2">{{ deviceStats.total }}</p>
              <p class="text-sm text-primary-600 dark:text-primary-400 mt-1">Monitored</p>
            </div>
            <div class="w-12 h-12 bg-primary-100 dark:bg-primary-900/30 rounded-lg flex items-center justify-center">
              <span class="text-2xl">📊</span>
            </div>
          </div>
        </BaseCard>
      </div>

      <!-- Charts and Widgets -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
        <!-- Device List -->
        <BaseCard title="Devices">
          <div class="space-y-3">
            <div v-for="device in devices.slice(0, 5)" :key="device.deviceId" class="flex items-start space-x-3 p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
              <span class="text-xl">
                {{ device.status === 'online' ? '🟢' : device.status === 'warning' ? '🟡' : '🔴' }}
              </span>
              <div class="flex-1 min-w-0">
                <p class="text-sm font-medium text-gray-900 dark:text-white truncate">{{ device.name }}</p>
                <p class="text-xs text-gray-600 dark:text-gray-400">
                  {{ device.deviceType }} • Battery: {{ device.batteryLevel }}%
                </p>
              </div>
            </div>
            <div v-if="devices.length === 0" class="text-center text-gray-500 dark:text-gray-400 py-4">
              No devices found
            </div>
          </div>
        </BaseCard>

        <!-- Recent Alerts -->
        <BaseCard title="Recent Alerts">
          <div class="space-y-3">
            <div v-for="alert in alerts.slice(0, 5)" :key="alert.alertId" class="flex items-start space-x-3 p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
              <span class="text-xl">
                {{ alert.severity === 'critical' ? '🔴' : alert.severity === 'warning' ? '🟡' : 'ℹ️' }}
              </span>
              <div class="flex-1 min-w-0">
                <p class="text-sm font-medium text-gray-900 dark:text-white truncate">{{ alert.title }}</p>
                <p class="text-xs text-gray-600 dark:text-gray-400">{{ alert.deviceName }} • {{ alert.status }}</p>
              </div>
            </div>
            <div v-if="alerts.length === 0" class="text-center text-gray-500 dark:text-gray-400 py-4">
              No alerts found
            </div>
          </div>
        </BaseCard>

        <!-- Device Health -->
        <BaseCard title="Device Health">
          <div class="space-y-4">
            <div v-if="averageBattery > 0">
              <div class="flex items-center justify-between mb-2">
                <span class="text-sm font-medium text-gray-700 dark:text-gray-300">Average Battery</span>
                <span class="text-sm font-semibold text-gray-900 dark:text-white">{{ averageBattery }}%</span>
              </div>
              <div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                <div
                  class="h-2 rounded-full"
                  :class="averageBattery > 60 ? 'bg-success-500' : averageBattery > 30 ? 'bg-warning-500' : 'bg-danger-500'"
                  :style="`width: ${averageBattery}%`"
                ></div>
              </div>
            </div>

            <div v-if="averageSignal > 0">
              <div class="flex items-center justify-between mb-2">
                <span class="text-sm font-medium text-gray-700 dark:text-gray-300">Signal Quality</span>
                <span class="text-sm font-semibold text-gray-900 dark:text-white">{{ averageSignal }}%</span>
              </div>
              <div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                <div
                  class="h-2 rounded-full"
                  :class="averageSignal > 70 ? 'bg-success-500' : averageSignal > 40 ? 'bg-warning-500' : 'bg-danger-500'"
                  :style="`width: ${averageSignal}%`"
                ></div>
              </div>
            </div>

            <div>
              <div class="flex items-center justify-between mb-2">
                <span class="text-sm font-medium text-gray-700 dark:text-gray-300">Online Rate</span>
                <span class="text-sm font-semibold text-gray-900 dark:text-white">{{ onlineRate }}%</span>
              </div>
              <div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                <div
                  class="bg-success-500 h-2 rounded-full"
                  :style="`width: ${onlineRate}%`"
                ></div>
              </div>
            </div>
          </div>
        </BaseCard>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { BaseCard } from '../../components/base'
import { useDevices } from '../../composables/useDevices'
import { useAlerts } from '../../composables/useAlerts'

// Composables
const {
  devices,
  deviceStats,
  isLoading: devicesLoading,
  error: devicesError,
  fetchDashboardDevices
} = useDevices()

const {
  alerts,
  unreadCount: unreadAlertsCount,
  criticalAlerts,
  isLoading: alertsLoading,
  error: alertsError,
  fetchRecentAlerts
} = useAlerts()

// Computed properties
const criticalAlertsCount = computed(() => criticalAlerts.value.length)

const averageBattery = computed(() => {
  if (devices.value.length === 0) return 0
  const total = devices.value.reduce((sum, device) => sum + (device.batteryLevel || 0), 0)
  return Math.round(total / devices.value.length)
})

const averageSignal = computed(() => {
  if (devices.value.length === 0) return 0
  const devicesWithSignal = devices.value.filter(d => d.connectivity.quality)
  if (devicesWithSignal.length === 0) return 0
  const total = devicesWithSignal.reduce((sum, device) => sum + (device.connectivity.quality || 0), 0)
  return Math.round(total / devicesWithSignal.length)
})

const onlineRate = computed(() => {
  if (deviceStats.value.total === 0) return 0
  return Math.round((deviceStats.value.online / deviceStats.value.total) * 100)
})

// Lifecycle
onMounted(async () => {
  await Promise.all([
    fetchDashboardDevices(),
    fetchRecentAlerts(10)
  ])
})
</script>
