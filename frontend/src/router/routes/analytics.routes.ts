import type { RouteRecordRaw } from 'vue-router'

export const analyticsRoutes: RouteRecordRaw[] = [
  {
    path: '/analytics',
    name: 'analytics',
    component: () => import('../../pages/analytics/AnalyticsPage.vue'),
    meta: {
      requiresAuth: true,
      title: 'Analytics',
    },
  },
]
