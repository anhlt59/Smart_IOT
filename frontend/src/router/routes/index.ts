import { authRoutes } from './auth.routes'
import { dashboardRoutes } from './dashboard.routes'
import { devicesRoutes } from './devices.routes'
import { alertsRoutes } from './alerts.routes'
import { analyticsRoutes } from './analytics.routes'
import { firmwareRoutes } from './firmware.routes'
import { usersRoutes } from './users.routes'
import { settingsRoutes } from './settings.routes'

export const routes = [
  {
    path: '/',
    redirect: '/dashboard',
  },
  ...authRoutes,
  ...dashboardRoutes,
  ...devicesRoutes,
  ...alertsRoutes,
  ...analyticsRoutes,
  ...firmwareRoutes,
  ...usersRoutes,
  ...settingsRoutes,
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: () => import('../../pages/NotFoundPage.vue'),
    meta: {
      title: 'Page Not Found',
    },
  },
]
