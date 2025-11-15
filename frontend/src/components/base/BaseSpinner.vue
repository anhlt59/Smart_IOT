<template>
  <div :class="spinnerClasses">
    <div class="animate-spin rounded-full border-2 border-current border-t-transparent" :class="sizeClasses"></div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  size?: 'xs' | 'sm' | 'md' | 'lg'
  color?: string
}

const props = withDefaults(defineProps<Props>(), {
  size: 'md',
  color: 'text-primary-600',
})

const sizeClasses = computed(() => {
  const sizes = {
    xs: 'h-3 w-3',
    sm: 'h-4 w-4',
    md: 'h-8 w-8',
    lg: 'h-12 w-12',
  }
  return sizes[props.size]
})

const spinnerClasses = computed(() => {
  return `inline-flex ${props.color}`
})
</script>
