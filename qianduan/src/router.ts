import { createRouter, createWebHistory } from 'vue-router'
import Login from './views/Login.vue'
import Shops from './views/Shops.vue'
import Audit from './views/Audit.vue'
import Messages from './views/Messages.vue'
import KnowledgeBase from './views/KnowledgeBase.vue'
import Statistics from './views/Statistics.vue'
import Users from './views/Users.vue'
import ImportTasks from './views/ImportTasks.vue'
import { useAuthStore } from './store/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/shops' },
    { path: '/login', component: Login },
    { path: '/shops', component: Shops, meta: { requiresAuth: true } },
    { path: '/audit', component: Audit, meta: { requiresAuth: true } },
    { path: '/messages', component: Messages, meta: { requiresAuth: true } },
    { path: '/kb', component: KnowledgeBase, meta: { requiresAuth: true } },
    { path: '/import-tasks', component: ImportTasks, meta: { requiresAuth: true } },
    { path: '/statistics', component: Statistics, meta: { requiresAuth: true } },
    { path: '/users', component: Users, meta: { requiresAuth: true } },
  ]
})

router.beforeEach((to, _from, next) => {
  const auth = useAuthStore()
  if (to.meta?.requiresAuth && !auth.authed) {
    next('/login')
  } else {
    next()
  }
})

export default router

