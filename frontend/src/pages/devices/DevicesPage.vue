<template>
  <div class="p-6">
    <!-- Page Header -->
    <div class="mb-6">
      <h1 class="text-2xl font-bold text-gray-900 dark:text-white">Devices</h1>
      <p class="text-gray-600 dark:text-gray-400">Manage and monitor your IoT devices</p>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="flex items-center justify-center h-64">
      <div class="text-center">
        <div class="text-6xl mb-4">⏳</div>
        <p class="text-gray-600 dark:text-gray-400">Loading devices...</p>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="bg-red-50 dark:bg-red-900/20 p-4 rounded-lg mb-6">
      <p class="text-red-600 dark:text-red-400">{{ error }}</p>
    </div>

    <!-- Devices List -->
    <template v-else>
      <BaseCard>
        <div class="space-y-4">
          <div v-for="device in devices" :key="device.deviceId" class="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
            <div class="flex items-center space-x-4">
              <span class="text-2xl">
                {{ device.status === 'online' ? '🟢' : device.status === 'warning' ? '🟡' : '🔴' }}
              </span>
              <div>
                <h3 class="text-lg font-semibold text-gray-900 dark:text-white">{{ device.name }}</h3>
                <p class="text-sm text-gray-600 dark:text-gray-400">
                  {{ device.deviceType }} • Battery: {{ device.batteryLevel }}% • Signal: {{ device.connectivity.quality }}%
                </p>
                <p class="text-xs text-gray-500 dark:text-gray-500">
                  {{ device.location.building }}, {{ device.location.floor }}, {{ device.location.room }}
                </p>
              </div>
            </div>
            <div class="flex items-center space-x-2">
              <span class="px-3 py-1 text-xs font-medium rounded-full"
                :class="{
                  'bg-success-100 text-success-700 dark:bg-success-900/30 dark:text-success-400': device.status === 'online',
                  'bg-warning-100 text-warning-700 dark:bg-warning-900/30 dark:text-warning-400': device.status === 'warning',
                  'bg-danger-100 text-danger-700 dark:bg-danger-900/30 dark:text-danger-400': device.status === 'offline'
                }"
              >
                {{ device.status }}
              </span>
            </div>
          </div>

          <div v-if="devices.length === 0" class="text-center text-gray-500 dark:text-gray-400 py-8">
            No devices found
          </div>
        </div>
      </BaseCard>
    </template>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { BaseCard } from '../../components/base'
import { useDevices } from '../../composables/useDevices'

const { devices, isLoading, error, fetchDevices } = useDevices()

onMounted(() => {
  fetchDevices()
})
</script>
