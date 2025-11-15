import type { RouteRecordRaw } from 'vue-router'

export const alertsRoutes: RouteRecordRaw[] = [
  {
    path: '/alerts',
    name: 'alerts',
    component: () => import('../../pages/alerts/AlertsPage.vue'),
    meta: {
      requiresAuth: true,
      title: 'Alerts',
    },
  },
]
