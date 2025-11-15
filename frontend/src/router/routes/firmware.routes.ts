import type { RouteRecordRaw } from 'vue-router'

export const firmwareRoutes: RouteRecordRaw[] = [
  {
    path: '/firmware',
    name: 'firmware',
    component: () => import('../../pages/firmware/FirmwarePage.vue'),
    meta: {
      requiresAuth: true,
      title: 'Firmware',
    },
  },
]
