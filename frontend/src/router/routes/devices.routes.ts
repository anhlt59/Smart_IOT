import type { RouteRecordRaw } from 'vue-router'

export const devicesRoutes: RouteRecordRaw[] = [
  {
    path: '/devices',
    name: 'devices',
    component: () => import('../../pages/devices/DevicesPage.vue'),
    meta: {
      requiresAuth: true,
      title: 'Devices',
    },
  },
]
