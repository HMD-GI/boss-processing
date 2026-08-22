import axios from 'axios'
import { ElMessage } from 'element-plus'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
})

api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const msg = error.response?.data?.detail || error.message || '请求失败'
    ElMessage.error(msg)
    return Promise.reject(error)
  }
)

export default {
  // ========== 职位查询 ==========
  getJobs(params) {
    return api.get('/jobs', { params })
  },

  getJobDetail(jobId) {
    return api.get(`/jobs/${jobId}`)
  },

  // ========== 采集任务 ==========
  startCrawl(data) {
    return api.post('/crawl/start', data)
  },

  getCrawlStatus(params) {
    return api.get('/crawl/status', { params })
  },

  // SSE 流式日志 URL（用 EventSource 连接，不走 axios）
  getCrawlStreamUrl(taskId) {
    return `/api/crawl/stream/${taskId}`
  },

  // ========== 数据统计 ==========
  getStats() {
    return api.get('/stats')
  },

  // ========== 城市列表 ==========
  getCitiesWithData() {
    return api.get('/cities')
  },

  getAllCities(keyword = '') {
    return api.get('/cities/all', { params: { keyword } })
  },

  // ========== 环境管理 ==========
  checkEnvironment() {
    return api.post('/env/check')
  },

  // ========== AI 助手 ==========
  // SSE 流式对话 URL（用 fetch + EventSource 连接）
  getAssistantChatUrl() {
    return '/api/assistant/chat'
  },

  // 获取对话列表
  getConversations(userId = 'default_user') {
    return api.get('/assistant/conversations', { params: { user_id: userId } })
  },

  // 获取单个对话详情
  getConversation(conversationId) {
    return api.get(`/assistant/conversation/${conversationId}`)
  },

  // 删除对话
  deleteConversation(conversationId) {
    return api.delete(`/assistant/conversation/${conversationId}`)
  },

  // 创建新对话
  newChat(userId = 'default_user', title = '新对话') {
    return api.post('/assistant/new-chat', { user_id: userId, title })
  },

  // 检查AI助手服务状态
  checkAssistant() {
    return api.get('/assistant/check')
  },
}
