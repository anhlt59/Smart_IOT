import { createRouter, createWebHistory } from 'vue-router'
import { routes } from './routes'
import { authGuard } from './guards'
import { APP_NAME } from '../core/constants'

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// Navigation guard
router.beforeEach(authGuard)

// Update document title
router.afterEach((to) => {
  const title = to.meta.title as string
  document.title = title ? `${title} - ${APP_NAME}` : APP_NAME
})

export default router
