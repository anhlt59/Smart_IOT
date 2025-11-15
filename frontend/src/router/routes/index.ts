import { authRoutes } from './auth.routes'
import { dashboardRoutes } from './dashboard.routes'

export const routes = [
  {
    path: '/',
    redirect: '/dashboard',
  },
  ...authRoutes,
  ...dashboardRoutes,
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: () => import('../../pages/NotFoundPage.vue'),
    meta: {
      title: 'Page Not Found',
    },
  },
]
