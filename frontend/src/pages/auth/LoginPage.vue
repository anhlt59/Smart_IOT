<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 to-primary-100 dark:from-gray-900 dark:to-gray-800 px-4">
    <div class="max-w-md w-full">
      <!-- Logo and Title -->
      <div class="text-center mb-8">
        <div class="inline-flex items-center justify-center w-16 h-16 bg-primary-600 rounded-2xl mb-4">
          <span class="text-white font-bold text-2xl">IoT</span>
        </div>
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white">IoT Monitoring</h1>
        <p class="text-gray-600 dark:text-gray-400 mt-2">Monitor. Analyze. Act.</p>
      </div>

      <!-- Login Form -->
      <BaseCard :padding="false">
        <div class="p-6">
          <form @submit.prevent="handleLogin">
            <!-- Email -->
            <div class="mb-4">
              <BaseInput
                v-model="email"
                type="email"
                label="Email"
                placeholder="user@example.com"
                required
                :error="emailError"
              />
            </div>

            <!-- Password -->
            <div class="mb-4">
              <BaseInput
                v-model="password"
                type="password"
                label="Password"
                placeholder="••••••••••"
                required
                :error="passwordError"
              />
            </div>

            <!-- Remember Me & Forgot Password -->
            <div class="flex items-center justify-between mb-6">
              <label class="flex items-center">
                <input type="checkbox" v-model="rememberMe" class="rounded border-gray-300 text-primary-600 focus:ring-primary-500" />
                <span class="ml-2 text-sm text-gray-700 dark:text-gray-300">Remember me</span>
              </label>
              <router-link to="/forgot-password" class="text-sm text-primary-600 hover:text-primary-700 dark:text-primary-400">
                Forgot password?
              </router-link>
            </div>

            <!-- Error Message -->
            <div v-if="error" class="mb-4 p-3 bg-danger-50 dark:bg-danger-900/20 border border-danger-200 dark:border-danger-800 rounded-lg">
              <p class="text-sm text-danger-700 dark:text-danger-400">{{ error }}</p>
            </div>

            <!-- Submit Button -->
            <BaseButton
              type="submit"
              variant="primary"
              size="lg"
              :loading="loading"
              full-width
            >
              Sign In
            </BaseButton>
          </form>

          <!-- Divider -->
          <div class="relative my-6">
            <div class="absolute inset-0 flex items-center">
              <div class="w-full border-t border-gray-300 dark:border-gray-600"></div>
            </div>
            <div class="relative flex justify-center text-sm">
              <span class="px-2 bg-white dark:bg-gray-800 text-gray-500">OR</span>
            </div>
          </div>

          <!-- Social Login -->
          <button
            type="button"
            class="w-full flex items-center justify-center px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
          >
            <svg class="w-5 h-5 mr-2" viewBox="0 0 24 24">
              <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
              <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
              <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
              <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
            </svg>
            Sign in with Google
          </button>

          <!-- Register Link -->
          <p class="mt-6 text-center text-sm text-gray-600 dark:text-gray-400">
            Don't have an account?
            <router-link to="/register" class="text-primary-600 hover:text-primary-700 dark:text-primary-400 font-medium">
              Sign up
            </router-link>
          </p>
        </div>
      </BaseCard>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../../store'
import { BaseInput, BaseButton, BaseCard } from '../../components/base'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const email = ref('')
const password = ref('')
const rememberMe = ref(false)
const emailError = ref('')
const passwordError = ref('')
const error = ref('')
const loading = ref(false)

const handleLogin = async () => {
  // Reset errors
  emailError.value = ''
  passwordError.value = ''
  error.value = ''

  // Basic validation
  if (!email.value) {
    emailError.value = 'Email is required'
    return
  }

  if (!password.value) {
    passwordError.value = 'Password is required'
    return
  }

  loading.value = true

  try {
    const success = await authStore.login(email.value, password.value)

    if (success) {
      const redirect = route.query.redirect as string || '/dashboard'
      router.push(redirect)
    } else {
      error.value = authStore.error || 'Login failed'
    }
  } catch (err: any) {
    error.value = err.message || 'An error occurred during login'
  } finally {
    loading.value = false
  }
}
</script>
