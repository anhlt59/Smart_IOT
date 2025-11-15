<template>
  <div class="p-6">
    <!-- Page Header -->
    <div class="mb-6">
      <h1 class="text-2xl font-bold text-gray-900 dark:text-white">Dashboard</h1>
      <p class="text-gray-600 dark:text-gray-400">Overview of your IoT devices and alerts</p>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
      <!-- Online Devices -->
      <BaseCard>
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600 dark:text-gray-400">Online Devices</p>
            <p class="text-3xl font-bold text-gray-900 dark:text-white mt-2">1,234</p>
            <p class="text-sm text-success-600 dark:text-success-400 mt-1">↑ 5.2% from last week</p>
          </div>
          <div class="w-12 h-12 bg-success-100 dark:bg-success-900/30 rounded-lg flex items-center justify-center">
            <span class="text-2xl">🟢</span>
          </div>
        </div>
      </BaseCard>

      <!-- Offline Devices -->
      <BaseCard>
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600 dark:text-gray-400">Offline Devices</p>
            <p class="text-3xl font-bold text-gray-900 dark:text-white mt-2">45</p>
            <p class="text-sm text-danger-600 dark:text-danger-400 mt-1">↓ 2.1% from last week</p>
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
            <p class="text-3xl font-bold text-gray-900 dark:text-white mt-2">12</p>
            <p class="text-sm text-warning-600 dark:text-warning-400 mt-1">3 critical</p>
          </div>
          <div class="w-12 h-12 bg-warning-100 dark:bg-warning-900/30 rounded-lg flex items-center justify-center">
            <span class="text-2xl">⚠️</span>
          </div>
        </div>
      </BaseCard>

      <!-- Data Volume -->
      <BaseCard>
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600 dark:text-gray-400">Data Volume</p>
            <p class="text-3xl font-bold text-gray-900 dark:text-white mt-2">12.5 GB</p>
            <p class="text-sm text-primary-600 dark:text-primary-400 mt-1">Last 30 days</p>
          </div>
          <div class="w-12 h-12 bg-primary-100 dark:bg-primary-900/30 rounded-lg flex items-center justify-center">
            <span class="text-2xl">📊</span>
          </div>
        </div>
      </BaseCard>
    </div>

    <!-- Charts and Widgets -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
      <!-- Device Status Overview -->
      <BaseCard title="Device Status Overview">
        <div class="flex items-center justify-center h-64">
          <div class="text-center">
            <div class="text-6xl mb-4">📈</div>
            <p class="text-gray-600 dark:text-gray-400">Chart visualization will be displayed here</p>
          </div>
        </div>
      </BaseCard>

      <!-- Recent Alerts -->
      <BaseCard title="Recent Alerts">
        <div class="space-y-3">
          <div v-for="i in 5" :key="i" class="flex items-start space-x-3 p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
            <span class="text-xl">⚠️</span>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-medium text-gray-900 dark:text-white truncate">High CO2 Level</p>
              <p class="text-xs text-gray-600 dark:text-gray-400">Office 301 • 5 min ago</p>
            </div>
          </div>
        </div>
        <router-link to="/alerts" class="block text-center text-sm text-primary-600 hover:text-primary-700 dark:text-primary-400 mt-4">
          View All Alerts →
        </router-link>
      </BaseCard>

      <!-- Device Health -->
      <BaseCard title="Device Health">
        <div class="space-y-4">
          <div>
            <div class="flex items-center justify-between mb-2">
              <span class="text-sm font-medium text-gray-700 dark:text-gray-300">CPU Usage</span>
              <span class="text-sm font-semibold text-gray-900 dark:text-white">45%</span>
            </div>
            <div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
              <div class="bg-success-500 h-2 rounded-full" style="width: 45%"></div>
            </div>
          </div>

          <div>
            <div class="flex items-center justify-between mb-2">
              <span class="text-sm font-medium text-gray-700 dark:text-gray-300">Memory</span>
              <span class="text-sm font-semibold text-gray-900 dark:text-white">62%</span>
            </div>
            <div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
              <div class="bg-warning-500 h-2 rounded-full" style="width: 62%"></div>
            </div>
          </div>

          <div>
            <div class="flex items-center justify-between mb-2">
              <span class="text-sm font-medium text-gray-700 dark:text-gray-300">Battery</span>
              <span class="text-sm font-semibold text-gray-900 dark:text-white">85%</span>
            </div>
            <div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
              <div class="bg-success-500 h-2 rounded-full" style="width: 85%"></div>
            </div>
          </div>
        </div>
      </BaseCard>
    </div>

    <!-- Device Activity Chart -->
    <BaseCard title="Sensor Data Trends (24h)">
      <div class="h-96 flex items-center justify-center">
        <div class="text-center">
          <div class="text-6xl mb-4">📊</div>
          <p class="text-gray-600 dark:text-gray-400">Real-time sensor data chart will be displayed here</p>
          <p class="text-sm text-gray-500 dark:text-gray-500 mt-2">Temperature, Humidity, CO2 levels over time</p>
        </div>
      </div>
    </BaseCard>
  </div>
</template>

<script setup lang="ts">
import { BaseCard } from '../../components/base'
</script>
