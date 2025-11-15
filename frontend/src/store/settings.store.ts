import { defineStore } from 'pinia'
import { ref, watch } from 'vue'
import { STORAGE_KEYS } from '../core/constants'

export const useSettingsStore = defineStore('settings', () => {
  const theme = ref<'light' | 'dark' | 'auto'>('light')
  const sidebarCollapsed = ref(false)
  const language = ref('en')

  // Initialize from localStorage
  const initialize = () => {
    const storedTheme = localStorage.getItem(STORAGE_KEYS.THEME)
    const storedSidebarCollapsed = localStorage.getItem(STORAGE_KEYS.SIDEBAR_COLLAPSED)
    const storedLanguage = localStorage.getItem(STORAGE_KEYS.LANGUAGE)

    if (storedTheme) {
      theme.value = storedTheme as 'light' | 'dark' | 'auto'
    }

    if (storedSidebarCollapsed) {
      sidebarCollapsed.value = storedSidebarCollapsed === 'true'
    }

    if (storedLanguage) {
      language.value = storedLanguage
    }

    applyTheme()
  }

  const setTheme = (newTheme: 'light' | 'dark' | 'auto') => {
    theme.value = newTheme
    localStorage.setItem(STORAGE_KEYS.THEME, newTheme)
    applyTheme()
  }

  const toggleTheme = () => {
    const newTheme = theme.value === 'light' ? 'dark' : 'light'
    setTheme(newTheme)
  }

  const applyTheme = () => {
    const isDark = theme.value === 'dark' ||
      (theme.value === 'auto' && window.matchMedia('(prefers-color-scheme: dark)').matches)

    if (isDark) {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  }

  const toggleSidebar = () => {
    sidebarCollapsed.value = !sidebarCollapsed.value
    localStorage.setItem(STORAGE_KEYS.SIDEBAR_COLLAPSED, String(sidebarCollapsed.value))
  }

  const setLanguage = (newLanguage: string) => {
    language.value = newLanguage
    localStorage.setItem(STORAGE_KEYS.LANGUAGE, newLanguage)
  }

  // Watch for system theme changes
  if (typeof window !== 'undefined') {
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
      if (theme.value === 'auto') {
        applyTheme()
      }
    })
  }

  return {
    theme,
    sidebarCollapsed,
    language,
    initialize,
    setTheme,
    toggleTheme,
    toggleSidebar,
    setLanguage,
  }
})
