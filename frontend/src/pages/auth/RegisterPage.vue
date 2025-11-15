<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 to-primary-100 dark:from-gray-900 dark:to-gray-800 px-4 py-8">
    <div class="max-w-md w-full">
      <!-- Logo and Title -->
      <div class="text-center mb-8">
        <div class="inline-flex items-center justify-center w-16 h-16 bg-primary-600 rounded-2xl mb-4">
          <span class="text-white font-bold text-2xl">IoT</span>
        </div>
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white">Create Account</h1>
        <p class="text-gray-600 dark:text-gray-400 mt-2">Get started with IoT Monitoring</p>
      </div>

      <!-- Register Form -->
      <BaseCard :padding="false">
        <div class="p-6">
          <form @submit.prevent="handleRegister">
            <!-- Full Name -->
            <div class="mb-4">
              <BaseInput
                v-model="fullName"
                type="text"
                label="Full Name"
                placeholder="John Doe"
                required
              />
            </div>

            <!-- Email -->
            <div class="mb-4">
              <BaseInput
                v-model="email"
                type="email"
                label="Email"
                placeholder="user@example.com"
                required
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
                help-text="Minimum 8 characters"
              />
            </div>

            <!-- Confirm Password -->
            <div class="mb-4">
              <BaseInput
                v-model="confirmPassword"
                type="password"
                label="Confirm Password"
                placeholder="••••••••••"
                required
              />
            </div>

            <!-- Terms and Conditions -->
            <div class="mb-6">
              <label class="flex items-start">
                <input type="checkbox" v-model="acceptTerms" class="mt-1 rounded border-gray-300 text-primary-600 focus:ring-primary-500" />
                <span class="ml-2 text-sm text-gray-700 dark:text-gray-300">
                  I agree to the <a href="#" class="text-primary-600 hover:text-primary-700 dark:text-primary-400">Terms and Conditions</a>
                </span>
              </label>
            </div>

            <!-- Submit Button -->
            <BaseButton
              type="submit"
              variant="primary"
              size="lg"
              :loading="loading"
              full-width
            >
              Create Account
            </BaseButton>
          </form>

          <!-- Login Link -->
          <p class="mt-6 text-center text-sm text-gray-600 dark:text-gray-400">
            Already have an account?
            <router-link to="/login" class="text-primary-600 hover:text-primary-700 dark:text-primary-400 font-medium">
              Sign in
            </router-link>
          </p>
        </div>
      </BaseCard>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { BaseInput, BaseButton, BaseCard } from '../../components/base'

const router = useRouter()

const fullName = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const acceptTerms = ref(false)
const loading = ref(false)

const handleRegister = async () => {
  loading.value = true
  // TODO: Implement registration logic
  setTimeout(() => {
    loading.value = false
    router.push('/login')
  }, 1000)
}
</script>
