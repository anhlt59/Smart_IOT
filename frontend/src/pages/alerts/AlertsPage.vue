<template>
  <div class="p-6">
    <!-- Page Header -->
    <div class="mb-6">
      <h1 class="text-2xl font-bold text-gray-900 dark:text-white">Alerts</h1>
      <p class="text-gray-600 dark:text-gray-400">Monitor and manage system alerts</p>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="flex items-center justify-center h-64">
      <div class="text-center">
        <div class="text-6xl mb-4">⏳</div>
        <p class="text-gray-600 dark:text-gray-400">Loading alerts...</p>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="bg-red-50 dark:bg-red-900/20 p-4 rounded-lg mb-6">
      <p class="text-red-600 dark:text-red-400">{{ error }}</p>
    </div>

    <!-- Alerts List -->
    <template v-else>
      <BaseCard>
        <div class="space-y-4">
          <div v-for="alert in alerts" :key="alert.alertId" class="flex items-start space-x-4 p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
            <span class="text-2xl">
              {{ alert.severity === 'critical' ? '🔴' : alert.severity === 'warning' ? '🟡' : 'ℹ️' }}
            </span>
            <div class="flex-1">
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white">{{ alert.title }}</h3>
              <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">{{ alert.message }}</p>
              <div class="flex items-center space-x-4 mt-2 text-xs text-gray-500 dark:text-gray-500">
                <span>{{ alert.deviceName }}</span>
                <span>•</span>
                <span>{{ alert.deviceLocation }}</span>
                <span>•</span>
                <span>{{ new Date(alert.triggeredAt).toLocaleString() }}</span>
              </div>
            </div>
            <div>
              <span class="px-3 py-1 text-xs font-medium rounded-full"
                :class="{
                  'bg-success-100 text-success-700 dark:bg-success-900/30 dark:text-success-400': alert.status === 'resolved',
                  'bg-warning-100 text-warning-700 dark:bg-warning-900/30 dark:text-warning-400': alert.status === 'acknowledged',
                  'bg-danger-100 text-danger-700 dark:bg-danger-900/30 dark:text-danger-400': alert.status === 'triggered'
                }"
              >
                {{ alert.status }}
              </span>
            </div>
          </div>

          <div v-if="alerts.length === 0" class="text-center text-gray-500 dark:text-gray-400 py-8">
            No alerts found
          </div>
        </div>
      </BaseCard>
    </template>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { BaseCard } from '../../components/base'
import { useAlerts } from '../../composables/useAlerts'

const { alerts, isLoading, error, fetchAlerts } = useAlerts()

onMounted(() => {
  fetchAlerts()
})
</script>
