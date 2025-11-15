<template>
  <aside
    :class="sidebarClasses"
    class="bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 fixed left-0 top-0 h-full z-40 transition-transform duration-300"
  >
    <div class="flex flex-col h-full">
      <!-- Logo -->
      <div class="h-16 flex items-center justify-center border-b border-gray-200 dark:border-gray-700">
        <router-link to="/dashboard" class="flex items-center space-x-2">
          <div class="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
            <span class="text-white font-bold text-lg">IoT</span>
          </div>
          <span class="text-xl font-bold text-gray-900 dark:text-white">Monitoring</span>
        </router-link>
      </div>

      <!-- Navigation -->
      <nav class="flex-1 overflow-y-auto py-4 px-3">
        <div v-for="group in navigation" :key="group.title" class="mb-6">
          <h3 v-if="group.title" class="px-3 mb-2 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">
            {{ group.title }}
          </h3>
          <ul class="space-y-1">
            <li v-for="item in group.items" :key="item.name">
              <router-link
                :to="item.path"
                :class="[
                  'flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-colors',
                  isActive(item.path)
                    ? 'bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-400'
                    : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                ]"
              >
                <span class="text-lg mr-3">{{ item.icon }}</span>
                <span>{{ item.label }}</span>
              </router-link>
            </li>
          </ul>
        </div>
      </nav>
    </div>
  </aside>

  <!-- Overlay for mobile -->
  <div
    v-if="!sidebarCollapsed"
    class="lg:hidden fixed inset-0 bg-black/50 z-30"
    @click="toggleSidebar"
  ></div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useSettingsStore } from '../../../store'

const route = useRoute()
const settingsStore = useSettingsStore()

const sidebarCollapsed = computed(() => settingsStore.sidebarCollapsed)

const sidebarClasses = computed(() => {
  return {
    'w-64': true,
    '-translate-x-full lg:translate-x-0': sidebarCollapsed.value,
  }
})

const navigation = [
  {
    title: '',
    items: [
      { name: 'dashboard', label: 'Dashboard', icon: '📊', path: '/dashboard' },
    ],
  },
  {
    title: 'Management',
    items: [
      { name: 'devices', label: 'Devices', icon: '📱', path: '/devices' },
      { name: 'alerts', label: 'Alerts', icon: '🔔', path: '/alerts' },
      { name: 'analytics', label: 'Analytics', icon: '📈', path: '/analytics' },
      { name: 'firmware', label: 'Firmware', icon: '🔧', path: '/firmware' },
    ],
  },
  {
    title: 'Administration',
    items: [
      { name: 'users', label: 'Users', icon: '👥', path: '/users' },
      { name: 'settings', label: 'Settings', icon: '⚙️', path: '/settings' },
    ],
  },
]

const isActive = (path: string) => {
  return route.path.startsWith(path)
}

const toggleSidebar = () => {
  settingsStore.toggleSidebar()
}
</script>
