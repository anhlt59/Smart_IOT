<template>
  <div :class="cardClasses">
    <div v-if="$slots.header || title" class="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
      <slot name="header">
        <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100">{{ title }}</h3>
      </slot>
    </div>
    <div :class="bodyClasses">
      <slot />
    </div>
    <div v-if="$slots.footer" class="px-6 py-4 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50">
      <slot name="footer" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  title?: string
  padding?: boolean
  shadow?: boolean
  hover?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  padding: true,
  shadow: true,
  hover: false,
})

const cardClasses = computed(() => {
  const base = 'bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 transition-all'
  const shadowClass = props.shadow ? 'shadow-soft' : ''
  const hoverClass = props.hover ? 'hover:shadow-medium cursor-pointer' : ''

  return `${base} ${shadowClass} ${hoverClass}`
})

const bodyClasses = computed(() => {
  return props.padding ? 'p-6' : ''
})
</script>
