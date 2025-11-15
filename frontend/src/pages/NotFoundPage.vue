<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 px-4">
    <div class="text-center">
      <h1 class="text-9xl font-bold text-gray-200 dark:text-gray-800">404</h1>
      <h2 class="text-3xl font-bold text-gray-900 dark:text-white mt-4">Page Not Found</h2>
      <p class="text-gray-600 dark:text-gray-400 mt-2 mb-8">The page you're looking for doesn't exist.</p>
      <BaseButton @click="$router.push('/dashboard')">
        Go to Dashboard
      </BaseButton>
    </div>
  </div>
</template>

<script setup lang="ts">
import { BaseButton } from '../components/base'
</script>
