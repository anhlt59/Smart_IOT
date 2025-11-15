import type { RouteRecordRaw } from 'vue-router'

export const authRoutes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'login',
    component: () => import('../../pages/auth/LoginPage.vue'),
    meta: {
      guestOnly: true,
      title: 'Login',
    },
  },
  {
    path: '/register',
    name: 'register',
    component: () => import('../../pages/auth/RegisterPage.vue'),
    meta: {
      guestOnly: true,
      title: 'Register',
    },
  },
]
