import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'
import AppLayout from '../layouts/AppLayout.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/login' },
    { path: '/login', component: LoginView },
    {
      path: '/',
      component: AppLayout,
      meta: { requiresAuth: true },
      children: [
        { path: 'dashboard', component: () => import('../views/DashboardView.vue') },
        { path: 'patients', component: () => import('../views/PatientManageView.vue') },
        { path: 'doctors', component: () => import('../views/DoctorManageView.vue') },
        { path: 'blood-sugar', component: () => import('../views/BloodSugarView.vue') },
        { path: 'oxygen', component: () => import('../views/OxygenView.vue') },
        { path: 'messages', component: () => import('../views/MessagesView.vue') },
      ]
    }
  ]
})

router.beforeEach((to) => {
  if (to.meta.requiresAuth && !localStorage.getItem('token')) {
    return '/login'
  }
})

export default router
