import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: '/jobs',
  },
  {
    path: '/jobs',
    name: 'JobList',
    component: () => import('../views/JobList.vue'),
    meta: { title: '职位列表' },
  },
  {
    path: '/jobs/:jobId',
    name: 'JobDetail',
    component: () => import('../views/JobDetail.vue'),
    meta: { title: '职位详情' },
  },
  {
    path: '/stats',
    name: 'Stats',
    component: () => import('../views/Stats.vue'),
    meta: { title: '数据统计' },
  },
  {
    path: '/crawl',
    name: 'Crawl',
    component: () => import('../views/Crawl.vue'),
    meta: { title: '采集任务' },
  },
  {
    path: '/resume',
    name: 'ResumeEditor',
    component: () => import('../views/ResumeEditor.vue'),
    meta: { title: '简历制作' },
  },
  {
    path: '/assistant',
    name: 'Assistant',
    component: () => import('../views/Assistant.vue'),
    meta: { title: 'AI助手' },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.afterEach((to) => {
  document.title = `${to.meta.title || ''} - BOSS直聘采集系统`
})

export default router
