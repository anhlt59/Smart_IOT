import type { RouteRecordRaw } from 'vue-router'

export const settingsRoutes: RouteRecordRaw[] = [
  {
    path: '/settings',
    name: 'settings',
    component: () => import('../../pages/settings/SettingsPage.vue'),
    meta: {
      requiresAuth: true,
      title: 'Settings',
    },
  },
]
