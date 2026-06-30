import { createRouter, createWebHistory } from 'vue-router'
import KnowledgeBase from '../views/KnowledgeBase.vue'
import Chat from '../views/Chat.vue'
import Summary from '../views/Summary.vue'

const routes = [
  { path: '/', redirect: '/chat' },
  { path: '/knowledge', name: 'Knowledge', component: KnowledgeBase },
  { path: '/chat', name: 'Chat', component: Chat },
  { path: '/summary', name: 'Summary', component: Summary },
]

export default createRouter({
  history: createWebHistory(),
  routes,
})
