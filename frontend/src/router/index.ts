import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'tasks',
    component: () => import('../views/TaskBoardView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/tasks/create',
    name: 'task-create',
    component: () => import('../views/TaskCreateView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/tasks/:id',
    name: 'task-detail',
    component: () => import('../views/TaskDetailView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/tasks/:id/status',
    name: 'task-status-management',
    component: () => import('../views/TaskStatusManagementView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/management/tasks',
    name: 'task-management',
    component: () => import('../views/TaskManagementView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/management/users',
    name: 'user-management',
    component: () => import('../views/UserManagementView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/management/history',
    name: 'task-history',
    component: () => import('../views/TaskHistoryView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/login',
    name: 'login',
    component: () => import('../views/LoginView.vue'),
  },
  {
    path: '/register',
    name: 'register',
    component: () => import('../views/RegisterView.vue'),
  },
  {
    path: '/forgot-password',
    name: 'forgot-password',
    component: () => import('../views/ForgotPasswordView.vue'),
  },
  {
    path: '/profile',
    name: 'profile',
    component: () => import('../views/ProfileView.vue'),
    meta: { requiresAuth: true },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, _from, next) => {
  const auth = useAuthStore()
  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    next({ name: 'login', query: { redirect: to.fullPath } })
    return
  }
  if ((to.name === 'login' || to.name === 'register' || to.name === 'forgot-password') && auth.isAuthenticated) {
    next({ name: 'tasks' })
    return
  }
  next()
})

export default router