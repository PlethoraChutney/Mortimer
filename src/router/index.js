import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import SessionView from '@/views/SessionView'
import GridView from '@/views/GridView'

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView
  },
  {
    path: '/sessions/:session',
    name: 'sessionView',
    component: SessionView
  },
  {
    path: '/sessions/:session/grid/:grid',
    name: 'gridView',
    component: GridView
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router
