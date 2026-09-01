<template>
  <div class="crawl-page">
    <el-row :gutter="24">
      <!-- 左栏 -->
      <el-col :span="10">
        <!-- 采集表单 -->
        <div class="form-card">
          <div class="card-header">
            <div class="header-icon" style="background: var(--primary-gradient);">
              <el-icon><Download /></el-icon>
            </div>
            <div class="header-text">
              <span class="header-title">发起采集任务</span>
              <span class="header-desc">配置参数后一键启动数据采集</span>
            </div>
          </div>
          <div class="form-body">
            <!-- 关键词 -->
            <div class="form-group">
              <label class="form-label">
                <el-icon><Key /></el-icon>
                搜索关键词
              </label>
              <div class="keyword-input-wrapper">
                <el-input
                  v-model="newKeyword"
                  placeholder="输入关键词后按回车或点击添加"
                  size="large"
                  @keyup.enter="addKeyword"
                >
                  <template #append>
                    <el-button :icon="Plus" @click="addKeyword" />
                  </template>
                </el-input>
              </div>
              <div class="keyword-tags" v-if="form.keywords.length">
                <transition-group name="tag">
                  <span
                    v-for="(kw, i) in form.keywords"
                    :key="kw"
                    class="kw-tag"
                  >
                    {{ kw }}
                    <el-icon class="kw-close" @click="removeKeyword(i)"><Close /></el-icon>
                  </span>
                </transition-group>
              </div>
              <div v-else class="hint-text">
                <el-icon><InfoFilled /></el-icon>
                至少添加一个关键词
              </div>
            </div>

            <!-- 城市 -->
            <div class="form-group">
              <label class="form-label">
                <el-icon><Location /></el-icon>
                目标城市
              </label>
              <el-select
                v-model="form.city"
                placeholder="选择城市"
                filterable
                size="large"
                style="width: 100%"
              >
                <el-option
                  v-for="c in allCities"
                  :key="c.code"
                  :label="c.city"
                  :value="c.city"
                />
              </el-select>
            </div>

            <!-- 采集页数 -->
            <div class="form-group">
              <label class="form-label">
                <el-icon><Document /></el-icon>
                采集页数
                <span class="form-value-badge">{{ form.pages }} 页</span>
              </label>
              <el-slider
                v-model="form.pages"
                :min="1"
                :max="10"
                :marks="{ 1: '1', 5: '5', 10: '10' }"
                style="width: 100%; padding: 0 8px"
              />
            </div>

            <!-- 抓取详情 -->
            <div class="form-group toggle-group">
              <div class="toggle-info">
                <label class="form-label no-margin">
                  <el-icon><DocumentChecked /></el-icon>
                  抓取详情页 JD
                </label>
                <span class="toggle-hint">{{ form.fetch_detail ? '较慢，但含完整职位描述' : '快速，仅列表数据' }}</span>
              </div>
              <el-switch
                v-model="form.fetch_detail"
                size="large"
                active-color="#4361ee"
              />
            </div>

            <!-- 提交按钮 -->
            <el-button
              type="primary"
              size="large"
              :loading="submitting"
              :disabled="submitting"
              @click="submitCrawl"
              class="submit-btn"
              :class="{ 'is-crawling': submitting }"
            >
              <el-icon v-if="!submitting"><Promotion /></el-icon>
              <el-icon v-else class="is-loading"><Loading /></el-icon>
              {{ submitting ? '正在爬取中...' : '开始采集' }}
            </el-button>
          </div>
        </div>

        <!-- 环境检查 -->
        <div class="env-card">
          <div class="card-header">
            <div class="header-icon" style="background: var(--info-gradient);">
              <el-icon><Monitor /></el-icon>
            </div>
            <div class="header-text">
              <span class="header-title">环境检查</span>
              <span class="header-desc">检测 Chrome 和登录状态</span>
            </div>
            <el-button
              type="primary"
              size="small"
              :loading="envChecking"
              @click="checkEnv"
              class="check-btn"
            >
              检查
            </el-button>
          </div>
          <div class="env-body">
            <div v-if="envResult" class="env-status-list">
              <div class="env-status-item">
                <div class="status-indicator" :class="envResult.chrome_cdp ? 'ok' : 'fail'"></div>
                <span class="status-label">Chrome CDP</span>
                <span class="status-value" :class="envResult.chrome_cdp ? 'text-ok' : 'text-fail'">
                  {{ envResult.chrome_cdp ? '正常' : '未运行' }}
                </span>
              </div>
              <div class="env-status-item">
                <div class="status-indicator" :class="envResult.websocket ? 'ok' : 'fail'"></div>
                <span class="status-label">WebSocket</span>
                <span class="status-value" :class="envResult.websocket ? 'text-ok' : 'text-fail'">
                  {{ envResult.websocket ? '正常' : '异常' }}
                </span>
              </div>
              <div class="env-status-item">
                <div class="status-indicator" :class="envResult.login_status ? 'ok' : 'fail'"></div>
                <span class="status-label">登录状态</span>
                <span class="status-value" :class="envResult.login_status ? 'text-ok' : 'text-fail'">
                  {{ envResult.login_status ? '已登录' : '未登录' }}
                </span>
              </div>
              <div v-if="envResult.errors?.length" class="env-errors">
                <div v-for="err in envResult.errors" :key="err" class="env-error-item">
                  <el-icon><WarningFilled /></el-icon>
                  {{ err }}
                </div>
              </div>
            </div>
            <div v-else class="env-empty">
              <el-icon :size="32" color="#c0c4cc"><Cpu /></el-icon>
              <span>点击「检查」按钮检测环境</span>
            </div>
          </div>
        </div>
      </el-col>

      <!-- 右栏：实时日志 + 采集日志 -->
      <el-col :span="14">
        <!-- 实时爬取日志 -->
        <div class="live-log-card" v-if="submitting || liveLogs.length">
          <div class="card-header">
            <div class="header-icon" :style="{ background: submitting ? 'var(--primary-gradient)' : 'var(--success-gradient)' }">
              <el-icon v-if="submitting" class="is-loading"><Loading /></el-icon>
              <el-icon v-else><CircleCheckFilled /></el-icon>
            </div>
            <div class="header-text">
              <span class="header-title">{{ submitting ? '爬取进度' : '爬取完成' }}</span>
              <span class="header-desc">{{ submitting ? '实时显示采集流程...' : crawlSummary }}</span>
            </div>
            <el-button
              v-if="!submitting && liveLogs.length"
              type="primary"
              size="small"
              plain
              :icon="Delete"
              @click="clearLiveLogs"
              class="check-btn"
            >
              清除
            </el-button>
          </div>
          <div class="live-log-body" ref="liveLogBody">
            <div
              v-for="(log, i) in liveLogs"
              :key="i"
              class="live-log-line"
              :class="log.level || 'info'"
            >
              <span class="log-time">{{ log.timestamp || '' }}</span>
              <span class="log-icon">
                <el-icon v-if="log.level === 'error'"><WarningFilled /></el-icon>
                <el-icon v-else-if="log.level === 'success'"><CircleCheckFilled /></el-icon>
                <el-icon v-else><InfoFilled /></el-icon>
              </span>
              <span class="log-text">{{ log.message }}</span>
            </div>
          </div>
        </div>

        <!-- 采集日志 -->
        <div class="log-card">
          <div class="card-header">
            <div class="header-icon" style="background: var(--success-gradient);">
              <el-icon><Tickets /></el-icon>
            </div>
            <div class="header-text">
              <span class="header-title">采集日志</span>
              <span class="header-desc">最近 20 条采集记录</span>
            </div>
            <el-button
              type="primary"
              size="small"
              plain
              :icon="Refresh"
              @click="loadLogs"
              class="check-btn"
            >
              刷新
            </el-button>
          </div>

          <div class="log-body" v-loading="logLoading">
            <div v-if="logs.length" class="log-timeline">
              <div
                v-for="(log, i) in logs"
                :key="log.id || i"
                class="log-item"
              >
                <div class="log-dot" :class="log.status === 'success' ? 'success' : 'fail'"></div>
                <div class="log-content">
                  <div class="log-header">
                    <span class="log-keyword">{{ log.keyword || '-' }}</span>
                    <el-tag
                      :type="log.status === 'success' ? 'success' : 'danger'"
                      size="small"
                      effect="light"
                    >
                      {{ log.status }}
                    </el-tag>
                  </div>
                  <div class="log-meta">
                    <span class="meta-tag">
                      <el-icon><Location /></el-icon>
                      {{ log.city || '-' }}
                    </span>
                    <span class="meta-tag">
                      <el-icon><Document /></el-icon>
                      {{ log.fetched_count || 0 }} 条
                    </span>
                    <span class="meta-tag">
                      <el-icon><Clock /></el-icon>
                      {{ log.timestamp ? log.timestamp.replace('T', ' ').substring(0, 19) : '-' }}
                    </span>
                  </div>
                  <div v-if="log.error_msg" class="log-error">
                    <el-icon><WarningFilled /></el-icon>
                    {{ log.error_msg }}
                  </div>
                </div>
              </div>
            </div>
            <div v-else class="log-empty">
              <el-icon :size="40" color="#c0c4cc"><DocumentRemove /></el-icon>
              <p class="empty-title">暂无采集记录</p>
              <p class="empty-desc">发起采集任务后，日志将显示在这里</p>
            </div>
          </div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Download, Plus, Close, Key, Location, Document, DocumentChecked,
  Promotion, Monitor, Cpu, Refresh, Tickets, WarningFilled, Clock,
  InfoFilled, DocumentRemove, Loading, CircleCheckFilled, Delete,
} from '@element-plus/icons-vue'
import api from '../api'

const newKeyword = ref('')
const submitting = ref(false)
const allCities = ref([])
const logs = ref([])
const logLoading = ref(false)
const envChecking = ref(false)
const envResult = ref(null)
const liveLogs = ref([])
const crawlSummary = ref('')
const liveLogBody = ref(null)
let eventSource = null  // SSE 连接

const form = reactive({
  keywords: [],
  city: '上海',
  pages: 3,
  fetch_detail: true,
})

function addKeyword() {
  const kw = newKeyword.value.trim()
  if (!kw) return
  if (form.keywords.includes(kw)) {
    ElMessage.warning('关键词已存在')
    return
  }
  form.keywords.push(kw)
  newKeyword.value = ''
}

function removeKeyword(index) {
  form.keywords.splice(index, 1)
}

async function submitCrawl() {
  if (form.keywords.length === 0) {
    ElMessage.warning('请至少添加一个关键词')
    return
  }
  submitting.value = true
  liveLogs.value = []
  crawlSummary.value = ''
  try {
    const res = await api.startCrawl({
      keywords: form.keywords,
      city: form.city,
      pages: form.pages,
      fetch_detail: form.fetch_detail,
    })
    ElMessage.success('采集任务已启动')
    // 启动 SSE 监听实时日志
    startSSE(res.task_id)
  } catch(e) {
    submitting.value = false
  }
}

function startSSE(taskId) {
  if (eventSource) {
    eventSource.close()
    eventSource = null
  }
  const url = api.getCrawlStreamUrl(taskId)
  eventSource = new EventSource(url)

  eventSource.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data)
      if (data.type === 'end') {
        if (data.status === 'completed') {
          crawlSummary.value = `共采集 ${data.total_jobs} 条职位数据`
          ElMessage.success('采集任务完成！')
        } else if (data.status === 'error') {
          crawlSummary.value = `采集失败: ${data.error}`
          ElMessage.error('采集任务失败')
        }
        submitting.value = false
        eventSource.close()
        eventSource = null
        loadLogs()
      } else if (data.type === 'timeout') {
        ElMessage.warning('实时日志连接超时')
        submitting.value = false
        eventSource.close()
        eventSource = null
      } else if (data.type === 'log') {
        liveLogs.value.push(data)
        // 自动滚动到底部
        nextTick(() => {
          if (liveLogBody.value) {
            liveLogBody.value.scrollTop = liveLogBody.value.scrollHeight
          }
        })
      }
    } catch (e) {
      // 忽略解析错误
    }
  }

  eventSource.onerror = () => {
    // 连接错误时不要立即关闭，可能只是正常关闭
    if (submitting.value) {
      // 仍在爬取中，尝试重连
    }
  }
}

function clearLiveLogs() {
  liveLogs.value = []
  crawlSummary.value = ''
}

async function loadLogs() {
  logLoading.value = true
  try {
    const res = await api.getCrawlStatus({ limit: 20 })
    logs.value = res.recent_logs || []
  } finally {
    logLoading.value = false
  }
}

async function checkEnv() {
  envChecking.value = true
  try {
    envResult.value = await api.checkEnvironment()
    if (envResult.value.chrome_cdp && envResult.value.login_status) {
      ElMessage.success('环境检查通过')
    } else {
      ElMessage.warning('环境检查未通过，请运行 python run.py setup')
    }
  } finally {
    envChecking.value = false
  }
}

async function loadCities() {
  try {
    const res = await api.getAllCities()
    allCities.value = res.cities || []
  } catch (e) {
    // 忽略
  }
}

onMounted(() => {
  loadCities()
  loadLogs()
})

onUnmounted(() => {
  if (eventSource) {
    eventSource.close()
    eventSource = null
  }
})
</script>

<style scoped>
/* ========== 通用卡片 ========== */
.form-card,
.env-card,
.log-card,
.live-log-card {
  background: var(--bg-card);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-card);
  margin-bottom: 20px;
  overflow: hidden;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 18px 24px;
  border-bottom: 1px solid var(--border-light);
}

.header-icon {
  width: 36px;
  height: 36px;
  border-radius: 9px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  flex-shrink: 0;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.header-text {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.header-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
}

.header-desc {
  font-size: 12px;
  color: var(--text-muted);
  margin-top: 2px;
}

.check-btn {
  flex-shrink: 0;
}

/* ========== 表单 ========== */
.form-body {
  padding: 24px;
}

.form-group {
  margin-bottom: 22px;
}

.form-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  font-weight: 600;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.form-label.no-margin {
  margin-bottom: 0;
}

.form-value-badge {
  margin-left: auto;
  background: var(--primary-gradient);
  color: #fff;
  padding: 2px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.keyword-tags {
  margin-top: 10px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.kw-tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 5px 12px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 500;
  background: linear-gradient(135deg, #e8ecf1 0%, #dde4ed 100%);
  color: var(--text-primary);
  transition: all 0.2s;
}

.kw-tag:hover {
  background: var(--primary-gradient);
  color: #fff;
}

.kw-close {
  cursor: pointer;
  font-size: 14px;
  opacity: 0.6;
  transition: opacity 0.2s;
}

.kw-close:hover {
  opacity: 1;
}

.hint-text {
  margin-top: 10px;
  display: flex;
  align-items: center;
  gap: 5px;
  color: var(--text-muted);
  font-size: 13px;
}

.toggle-group {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 16px;
  background: var(--bg-table-header);
  border-radius: var(--radius-sm);
}

.toggle-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.toggle-hint {
  font-size: 12px;
  color: var(--text-muted);
}

.submit-btn {
  width: 100%;
  height: 44px;
  font-size: 15px;
  font-weight: 600;
  margin-top: 8px;
}

/* ========== 环境检查 ========== */
.env-body {
  padding: 20px 24px;
}

.env-status-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.env-status-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  background: var(--bg-table-header);
  border-radius: var(--radius-sm);
}

.status-indicator {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}

.status-indicator.ok {
  background: var(--success);
  box-shadow: 0 0 8px rgba(6, 214, 160, 0.4);
}

.status-indicator.fail {
  background: var(--danger);
  box-shadow: 0 0 8px rgba(239, 71, 111, 0.4);
}

.status-label {
  flex: 1;
  font-size: 13px;
  color: var(--text-secondary);
  font-weight: 500;
}

.status-value {
  font-size: 13px;
  font-weight: 600;
}

.text-ok {
  color: var(--success);
}

.text-fail {
  color: var(--danger);
}

.env-errors {
  margin-top: 8px;
}

.env-error-item {
  display: flex;
  align-items: flex-start;
  gap: 6px;
  padding: 8px 12px;
  background: var(--bg-table-row-hover);
  border-radius: var(--radius-sm);
  font-size: 12px;
  color: var(--danger);
  margin-bottom: 6px;
}

.env-empty {
  text-align: center;
  padding: 30px 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  color: var(--text-muted);
  font-size: 13px;
}

/* ========== 采集日志 ========== */
.log-body {
  padding: 16px 24px;
  min-height: 400px;
}

.log-timeline {
  position: relative;
}

.log-timeline::before {
  content: '';
  position: absolute;
  left: 5px;
  top: 12px;
  bottom: 12px;
  width: 2px;
  background: var(--border-light);
}

.log-item {
  display: flex;
  gap: 16px;
  padding: 14px 0;
  position: relative;
}

.log-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  flex-shrink: 0;
  margin-top: 4px;
  z-index: 1;
  border: 2px solid #fff;
}

.log-dot.success {
  background: var(--success);
  box-shadow: 0 0 6px rgba(6, 214, 160, 0.3);
}

.log-dot.fail {
  background: var(--danger);
  box-shadow: 0 0 6px rgba(239, 71, 111, 0.3);
}

.log-content {
  flex: 1;
  min-width: 0;
}

.log-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 6px;
}

.log-keyword {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.log-meta {
  display: flex;
  gap: 14px;
  flex-wrap: wrap;
}

.meta-tag {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: var(--text-muted);
}

.log-error {
  margin-top: 6px;
  display: flex;
  align-items: flex-start;
  gap: 6px;
  padding: 6px 10px;
  background: var(--bg-table-row-hover);
  border-radius: 6px;
  font-size: 12px;
  color: var(--danger);
}

.log-empty {
  text-align: center;
  padding: 60px 20px;
}

.empty-title {
  margin-top: 14px;
  font-size: 15px;
  font-weight: 600;
  color: var(--text-secondary);
}

.empty-desc {
  margin-top: 6px;
  font-size: 13px;
  color: var(--text-muted);
}

/* ========== 标签动画 ========== */
.tag-enter-active,
.tag-leave-active {
  transition: all 0.3s ease;
}

.tag-enter-from,
.tag-leave-to {
  opacity: 0;
  transform: scale(0.8);
}

/* ========== 实时日志框 ========== */
.submit-btn.is-crawling {
  background: linear-gradient(135deg, #94a3b8 0%, #64748b 100%) !important;
  cursor: not-allowed;
  opacity: 0.8;
}

.live-log-body {
  padding: 12px 20px;
  max-height: 380px;
  min-height: 120px;
  overflow-y: auto;
  background: #1e1e2e;
  font-family: 'Cascadia Code', 'Fira Code', 'Consolas', monospace;
  font-size: 13px;
  line-height: 1.8;
}

.live-log-body::-webkit-scrollbar {
  width: 6px;
}

.live-log-body::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.15);
  border-radius: 3px;
}

.live-log-line {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 2px 0;
  color: #e0e0e0;
  animation: logFadeIn 0.3s ease;
}

@keyframes logFadeIn {
  from {
    opacity: 0;
    transform: translateX(-4px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.live-log-line.error {
  color: #ef5350;
}

.live-log-line.success {
  color: #66bb6a;
}

.log-time {
  color: #6c7086;
  flex-shrink: 0;
  font-size: 12px;
  margin-top: 1px;
}

.log-icon {
  flex-shrink: 0;
  margin-top: 1px;
  display: flex;
  align-items: center;
}

.log-icon .el-icon {
  font-size: 13px;
}

.log-text {
  flex: 1;
  word-break: break-all;
}
</style>
