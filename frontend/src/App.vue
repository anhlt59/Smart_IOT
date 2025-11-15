<template>
  <div id="app" class="min-h-screen bg-gray-50 dark:bg-gray-900">
    <!-- Layout for authenticated users -->
    <template v-if="isAuthenticated && !isAuthRoute">
      <AppSidebar />
      <div class="lg:pl-64">
        <AppHeader />
        <main class="pt-16">
          <RouterView />
        </main>
      </div>
    </template>

    <!-- Layout for auth pages -->
    <template v-else>
      <RouterView />
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { AppHeader, AppSidebar } from './components/modules/layout'
import { useAuthStore, useSettingsStore } from './store'

const route = useRoute()
const authStore = useAuthStore()
const settingsStore = useSettingsStore()

const isAuthenticated = computed(() => authStore.isAuthenticated)
const isAuthRoute = computed(() => route.path.startsWith('/login') || route.path.startsWith('/register'))

onMounted(() => {
  // Initialize stores from localStorage
  authStore.initialize()
  settingsStore.initialize()
})
</script>

<style>
/* Import Google Fonts */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
</style>
