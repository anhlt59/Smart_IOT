import type { RouteRecordRaw } from 'vue-router'

export const usersRoutes: RouteRecordRaw[] = [
  {
    path: '/users',
    name: 'users',
    component: () => import('../../pages/users/UsersPage.vue'),
    meta: {
      requiresAuth: true,
      title: 'Users',
    },
  },
]
