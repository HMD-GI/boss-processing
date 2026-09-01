<template>
  <div class="assistant-container">
    <!-- 左侧：对话历史面板 -->
    <div class="conv-sidebar" :class="{ collapsed: !showConvSidebar }">
      <div class="conv-sidebar-header">
        <el-button
          class="new-chat-btn"
          :icon="Plus"
          @click="startNewChat"
          :disabled="isGenerating"
        >
          新建对话
        </el-button>
      </div>
      <div class="conv-list">
        <div
          v-for="conv in conversations"
          :key="conv.id"
          class="conv-item"
          :class="{ active: conv.id === currentConvId }"
          @click="loadConversation(conv.id)"
        >
          <el-icon :size="16" class="conv-icon"><ChatLineSquare /></el-icon>
          <span class="conv-title">{{ conv.title || '新对话' }}</span>
          <span class="conv-time">{{ formatConvTime(conv.updated_at) }}</span>
          <el-icon
            :size="14"
            class="conv-delete"
            @click.stop="handleDeleteConv(conv.id)"
          >
            <Delete />
          </el-icon>
        </div>
        <div v-if="conversations.length === 0" class="conv-empty">
          暂无对话记录
        </div>
      </div>
    </div>

    <!-- 右侧：聊天区域 -->
    <div class="chat-area">
      <!-- 消息列表 -->
      <div class="messages-container" ref="messagesContainer">
        <!-- 欢迎界面 -->
        <div v-if="messages.length === 0" class="welcome-screen">
          <div class="welcome-logo">
            <el-icon :size="48" color="#4361ee"><ChatDotRound /></el-icon>
          </div>
          <h1 class="welcome-title">AI 求职助手</h1>
          <p class="welcome-subtitle">告诉我你的求职需求，我来帮你找到最合适的岗位</p>
          <div class="welcome-suggestions">
            <div
              v-for="suggestion in suggestions"
              :key="suggestion"
              class="suggestion-card"
              @click="sendMessage(suggestion)"
            >
              <el-icon :size="20" color="#4361ee"><Position /></el-icon>
              <span>{{ suggestion }}</span>
            </div>
          </div>
        </div>

        <!-- 消息列表 -->
        <div
          v-for="(msg, index) in messages"
          :key="index"
          class="message-wrapper"
          :class="msg.role"
        >
          <!-- 用户消息 -->
          <div v-if="msg.role === 'user'" class="user-message">
            <div class="user-avatar">我</div>
            <div class="user-content">{{ msg.content }}</div>
          </div>

          <!-- 系统消息（关键词解析等，不显示） -->
          <div v-else-if="msg.role === 'system'" style="display: none;"></div>

          <!-- AI 消息 -->
          <div v-else-if="msg.role === 'assistant'" class="ai-message">
            <div class="ai-avatar">
              <el-icon :size="20" color="#fff"><ChatDotRound /></el-icon>
            </div>
            <div class="ai-content">
              <!-- 处理步骤 -->
              <div v-if="msg.processSteps && msg.processSteps.length > 0" class="process-steps">
                <div
                  v-for="step in msg.processSteps"
                  :key="step.step"
                  class="process-step"
                  :class="step.status"
                >
                  <div class="step-header" @click="toggleStep(step)">
                    <div class="step-indicator">
                      <el-icon v-if="step.status === 'completed'" :size="16" color="#06d6a0">
                        <CircleCheckFilled />
                      </el-icon>
                      <el-icon v-else-if="step.status === 'error'" :size="16" color="#ef476f">
                        <CircleCloseFilled />
                      </el-icon>
                      <el-icon v-else :size="16" class="step-loading">
                        <Loading />
                      </el-icon>
                    </div>
                    <span class="step-title">步骤{{ step.step }}: {{ step.title }}</span>
                    <el-icon :size="12" class="step-toggle" v-if="step.detail">
                      <ArrowUp v-if="step.expanded" />
                      <ArrowDown v-else />
                    </el-icon>
                  </div>
                  <transition name="step-expand">
                    <div v-if="step.expanded && step.detail" class="step-detail">
                      {{ step.detail }}
                    </div>
                  </transition>
                </div>
              </div>

              <!-- 历史日志输出 -->
              <div v-if="msg.logs && msg.logs.length > 0" class="log-terminal">
                <div class="log-terminal-header">
                  <span class="log-terminal-title">运行日志</span>
                  <span class="log-terminal-count">{{ msg.logs.length }} 行</span>
                </div>
                <div class="log-terminal-body">
                  <div
                    v-for="(log, idx) in msg.logs"
                    :key="idx"
                    class="log-line"
                    :class="log.level"
                  >
                    <span class="log-time">{{ log.time }}</span>
                    <span class="log-message">{{ log.message }}</span>
                  </div>
                </div>
              </div>

              <!-- Markdown 内容 -->
              <div
                v-if="msg.content"
                class="markdown-content"
                v-html="renderMarkdown(msg.content)"
              ></div>

              <!-- 正在生成指示 -->
              <div v-if="msg.generating" class="generating-indicator">
                <span class="dot"></span>
                <span class="dot"></span>
                <span class="dot"></span>
              </div>
            </div>
          </div>
        </div>

        <!-- 当前正在生成的消息 -->
        <div v-if="isGenerating && currentGeneratingMsg" class="message-wrapper assistant">
          <div class="ai-message">
            <div class="ai-avatar">
              <el-icon :size="20" color="#fff"><ChatDotRound /></el-icon>
            </div>
            <div class="ai-content">
              <!-- 处理步骤 -->
              <div v-if="currentSteps.length > 0" class="process-steps">
                <div
                  v-for="step in currentSteps"
                  :key="step.step"
                  class="process-step"
                  :class="step.status"
                >
                  <div class="step-header" @click="toggleStep(step)">
                    <div class="step-indicator">
                      <el-icon v-if="step.status === 'completed'" :size="16" color="#06d6a0">
                        <CircleCheckFilled />
                      </el-icon>
                      <el-icon v-else-if="step.status === 'error'" :size="16" color="#ef476f">
                        <CircleCloseFilled />
                      </el-icon>
                      <el-icon v-else :size="16" class="step-loading">
                        <Loading />
                      </el-icon>
                    </div>
                    <span class="step-title">步骤{{ step.step }}: {{ step.title }}</span>
                    <el-icon :size="12" class="step-toggle" v-if="step.detail">
                      <ArrowUp v-if="step.expanded" />
                      <ArrowDown v-else />
                    </el-icon>
                  </div>
                  <transition name="step-expand">
                    <div v-if="step.expanded && step.detail" class="step-detail">
                      {{ step.detail }}
                    </div>
                  </transition>
                </div>
              </div>

              <!-- 实时日志输出 -->
              <div v-if="currentLogs.length > 0" class="log-terminal">
                <div class="log-terminal-header">
                  <span class="log-terminal-title">
                    <el-icon :size="12" class="log-terminal-icon"><Loading /></el-icon>
                    运行日志
                  </span>
                  <span class="log-terminal-count">{{ currentLogs.length }} 行</span>
                </div>
                <div class="log-terminal-body" ref="logTerminalRef">
                  <div
                    v-for="(log, idx) in currentLogs"
                    :key="idx"
                    class="log-line"
                    :class="log.level"
                  >
                    <span class="log-time">{{ log.time }}</span>
                    <span class="log-message">{{ log.message }}</span>
                  </div>
                </div>
              </div>

              <!-- Markdown 内容（流式） -->
              <div
                v-if="currentGeneratingContent"
                class="markdown-content"
                v-html="renderMarkdown(currentGeneratingContent)"
              ></div>

              <!-- 正在生成指示 -->
              <div class="generating-indicator">
                <span class="dot"></span>
                <span class="dot"></span>
                <span class="dot"></span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 输入区域 -->
      <div class="input-area">
        <div class="input-wrapper">
          <el-input
            v-model="inputText"
            type="textarea"
            :rows="1"
            :autosize="{ minRows: 1, maxRows: 6 }"
            placeholder="输入你的求职需求，例如：我想找上海的Python开发岗位，3-5年经验，薪资20-30K"
            resize="none"
            @keydown.enter.exact.prevent="handleEnter"
            :disabled="isGenerating"
            class="chat-input"
          />
          <el-button
            class="send-btn"
            :icon="Promotion"
            circle
            @click="handleSend"
            :disabled="!inputText.trim() || isGenerating"
            :loading="isGenerating"
          />
        </div>
        <div class="input-hint">
          按 Enter 发送，Shift + Enter 换行
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onActivated, onDeactivated, nextTick, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus, Delete, ChatLineSquare, ChatDotRound, Position,
  CircleCheckFilled, CircleCloseFilled, Loading,
  ArrowUp, ArrowDown, Promotion,
} from '@element-plus/icons-vue'
import { marked } from 'marked'
import api from '../api'

// ========== 状态 ==========
const conversations = ref([])
const currentConvId = ref(null)
const messages = ref([])
const inputText = ref('')
const isGenerating = ref(false)
const showConvSidebar = ref(true)
const messagesContainer = ref(null)
const logTerminalRef = ref(null)

// 当前正在生成的消息
const currentSteps = ref([])
const currentGeneratingContent = ref('')
const currentGeneratingMsg = ref(false)
const currentLogs = ref([])  // 实时日志行列表

// 欢迎页建议
const suggestions = [
  '我想找上海的Python开发岗位，3-5年经验，本科以上，薪资20-30K',
  '帮我看看北京的前端工程师岗位，要求公司规模500人以上',
  '深圳的AI算法岗位，硕士学历，薪资30-50K',
  '杭州的Java后端开发，1-3年经验，10-15K',
]

// ========== Markdown 渲染 ==========
marked.setOptions({
  breaks: true,
  gfm: true,
})

function renderMarkdown(text) {
  if (!text) return ''
  try {
    return marked(text)
  } catch {
    return text
  }
}

// ========== 对话管理 ==========
async function loadConversations() {
  try {
    const data = await api.getConversations()
    conversations.value = data.conversations || []
  } catch {
    // 静默失败
  }
}

async function startNewChat() {
  currentConvId.value = null
  messages.value = []
  currentSteps.value = []
  currentGeneratingContent.value = ''
  currentLogs.value = []
}

async function loadConversation(convId) {
  if (isGenerating.value) return
  try {
    const conv = await api.getConversation(convId)
    currentConvId.value = convId
    // 过滤掉 system 消息，保留 user 和 assistant
    messages.value = (conv.messages || []).filter(m => m.role === 'user' || m.role === 'assistant')
    // 为历史消息中的步骤添加 expanded 属性
    for (const msg of messages.value) {
      if (msg.process_steps) {
        msg.processSteps = msg.process_steps.map(s => ({ ...s, expanded: false }))
      }
      // 恢复日志
      if (msg.logs) {
        msg.logs = msg.logs.map(l => ({ ...l }))
      }
    }
    await nextTick()
    scrollToBottom()
  } catch (e) {
    ElMessage.error('加载对话失败')
  }
}

async function handleDeleteConv(convId) {
  try {
    await ElMessageBox.confirm('确定删除这个对话吗？', '提示', {
      type: 'warning',
    })
    await api.deleteConversation(convId)
    ElMessage.success('对话已删除')
    if (currentConvId.value === convId) {
      startNewChat()
    }
    loadConversations()
  } catch {
    // 取消删除
  }
}

// ========== 发送消息 ==========
function handleEnter() {
  if (!isGenerating.value) {
    handleSend()
  }
}

async function handleSend() {
  const text = inputText.value.trim()
  if (!text || isGenerating.value) return

  // 添加用户消息到列表
  messages.value.push({
    role: 'user',
    content: text,
  })

  inputText.value = ''
  isGenerating.value = true
  currentGeneratingMsg.value = true
  currentSteps.value = []
  currentGeneratingContent.value = ''
  currentLogs.value = []

  await nextTick()
  scrollToBottom()

  // 通过 SSE 调用后端
  try {
    const response = await fetch('/api/assistant/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message: text,
        conversation_id: currentConvId.value,
        user_id: 'default_user',
      }),
    })

    const reader = response.body.getReader()
    const decoder = new TextDecoder('utf-8')
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const dataStr = line.slice(6).trim()
          if (!dataStr) continue
          try {
            const event = JSON.parse(dataStr)
            handleSSEEvent(event)
          } catch {
            // 忽略解析错误
          }
        }
      }
    }

    // 处理剩余 buffer
    if (buffer.startsWith('data: ')) {
      try {
        const event = JSON.parse(buffer.slice(6).trim())
        handleSSEEvent(event)
      } catch {
        // 忽略
      }
    }
  } catch (e) {
    ElMessage.error(`请求失败: ${e.message}`)
  } finally {
    // 将生成的消息添加到消息列表
    if (currentGeneratingContent.value || currentSteps.value.length > 0) {
      messages.value.push({
        role: 'assistant',
        content: currentGeneratingContent.value,
        processSteps: currentSteps.value.map(s => ({ ...s })),
        logs: currentLogs.value.map(l => ({ ...l })),
        generating: false,
      })
    }
    isGenerating.value = false
    currentGeneratingMsg.value = false
    currentGeneratingContent.value = ''
    currentSteps.value = []
    currentLogs.value = []

    await nextTick()
    scrollToBottom()
    loadConversations()
  }
}

function handleSSEEvent(event) {
  switch (event.type) {
    case 'step':
      // 更新处理步骤
      {
        const stepIndex = currentSteps.value.findIndex(s => s.step === event.step)
        const stepData = {
          step: event.step,
          status: event.status,
          title: event.title,
          detail: event.detail || '',
          expanded: false,
        }
        if (stepIndex >= 0) {
          // 保留 expanded 状态
          stepData.expanded = currentSteps.value[stepIndex].expanded
          currentSteps.value[stepIndex] = stepData
        } else {
          currentSteps.value.push(stepData)
        }
        // 自动展开正在运行的步骤
        if (event.status === 'running') {
          stepData.expanded = true
        }
      }
      break

    case 'content':
      currentGeneratingContent.value += event.content
      break

    case 'log':
      // 实时日志输出
      currentLogs.value.push({
        message: event.message,
        level: event.level || 'info',
        time: new Date().toLocaleTimeString(),
      })
      // 自动滚动日志终端到底部
      nextTick(() => {
        if (logTerminalRef.value) {
          logTerminalRef.value.scrollTop = logTerminalRef.value.scrollHeight
        }
      })
      break

    case 'done':
      currentConvId.value = event.conversation_id
      break

    case 'error':
      ElMessage.error(event.message || '处理失败')
      break
  }

  // 自动滚动
  nextTick(() => scrollToBottom())
}

// ========== 辅助方法 ==========
function toggleStep(step) {
  step.expanded = !step.expanded
}

function scrollToBottom() {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

function formatConvTime(timeStr) {
  if (!timeStr) return ''
  const date = new Date(timeStr)
  const now = new Date()
  const diff = now - date
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  return date.toLocaleDateString()
}

// ========== 初始化 ==========
onMounted(() => {
  loadConversations()
})

// keep-alive 激活时：滚动到底部（恢复正在处理的对话视图）
onActivated(() => {
  nextTick(() => {
    scrollToBottom()
  })
})
</script>

<style scoped>
.assistant-container {
  display: flex;
  height: calc(100vh - 60px);
  margin: -24px;
  background: var(--bg-table-header);
}

/* ========== 左侧对话历史 ========== */
.conv-sidebar {
  width: 260px;
  background: var(--bg-card);
  border-right: 1px solid #e8ecf1;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  transition: width 0.3s;
}

.conv-sidebar.collapsed {
  width: 0;
  overflow: hidden;
}

.conv-sidebar-header {
  padding: 16px;
  border-bottom: 1px solid #f0f0f0;
}

.new-chat-btn {
  width: 100%;
  border: 1px solid #e0e0e0 !important;
  background: var(--bg-card) !important;
  color: #333 !important;
  font-weight: 500;
  transition: all 0.2s;
}

.new-chat-btn:hover {
  border-color: #4361ee !important;
  color: #4361ee !important;
  background: var(--bg-table-row-hover) !important;
}

.conv-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.conv-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
  margin-bottom: 2px;
}

.conv-item:hover {
  background: var(--bg-table-header);
}

.conv-item.active {
  background: var(--bg-table-row-hover);
  color: #4361ee;
}

.conv-icon {
  flex-shrink: 0;
  opacity: 0.6;
}

.conv-title {
  flex: 1;
  font-size: 13px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.conv-time {
  font-size: 11px;
  color: #999;
  flex-shrink: 0;
}

.conv-delete {
  opacity: 0;
  color: #999;
  transition: opacity 0.2s, color 0.2s;
  flex-shrink: 0;
}

.conv-item:hover .conv-delete {
  opacity: 1;
}

.conv-delete:hover {
  color: #ef476f !important;
}

.conv-empty {
  text-align: center;
  color: #999;
  font-size: 13px;
  padding: 40px 0;
}

/* ========== 右侧聊天区域 ========== */
.chat-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 24px 0;
}

/* ========== 欢迎界面 ========== */
.welcome-screen {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  padding: 40px;
}

.welcome-logo {
  margin-bottom: 20px;
}

.welcome-title {
  font-size: 28px;
  font-weight: 700;
  color: #1a1a2e;
  margin-bottom: 8px;
}

.welcome-subtitle {
  font-size: 15px;
  color: #5c677d;
  margin-bottom: 36px;
}

.welcome-suggestions {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  max-width: 600px;
  width: 100%;
}

.suggestion-card {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 16px 20px;
  background: var(--bg-card);
  border: 1px solid #e8ecf1;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 14px;
  color: #5c677d;
}

.suggestion-card:hover {
  border-color: #4361ee;
  color: #4361ee;
  box-shadow: 0 2px 12px rgba(67, 97, 238, 0.1);
  transform: translateY(-1px);
}

/* ========== 消息样式 ========== */
.message-wrapper {
  max-width: 800px;
  margin: 0 auto;
  padding: 12px 24px;
}

.message-wrapper.user {
  display: flex;
  justify-content: flex-end;
}

.user-message {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  max-width: 80%;
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #4361ee;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 600;
  flex-shrink: 0;
}

.user-content {
  background: var(--bg-table-row-hover);
  color: #1a1a2e;
  padding: 12px 16px;
  border-radius: 12px 12px 4px 12px;
  font-size: 14px;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-word;
}

.ai-message {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  width: 100%;
}

.ai-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: linear-gradient(135deg, #4361ee 0%, #3a0ca3 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.ai-content {
  flex: 1;
  min-width: 0;
}

/* ========== 处理步骤 ========== */
.process-steps {
  margin-bottom: 16px;
  border: 1px solid #e8ecf1;
  border-radius: 8px;
  overflow: hidden;
  background: var(--bg-table-header);
}

.process-step {
  border-bottom: 1px solid #f0f0f0;
}

.process-step:last-child {
  border-bottom: none;
}

.step-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  cursor: pointer;
  transition: background 0.2s;
}

.step-header:hover {
  background: var(--bg-table-header);
}

.step-indicator {
  display: flex;
  align-items: center;
  flex-shrink: 0;
}

.step-loading {
  animation: spin 1s linear infinite;
  color: #4361ee;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.step-title {
  flex: 1;
  font-size: 13px;
  font-weight: 500;
  color: #333;
}

.step-toggle {
  color: #999;
  flex-shrink: 0;
}

.step-detail {
  padding: 8px 14px 12px 38px;
  font-size: 12px;
  color: #666;
  background: var(--bg-table-header);
  line-height: 1.6;
}

.step-expand-enter-active,
.step-expand-leave-active {
  transition: all 0.2s ease;
  overflow: hidden;
}

.step-expand-enter-from,
.step-expand-leave-to {
  opacity: 0;
  max-height: 0;
}

/* ========== Markdown 内容 ========== */
.markdown-content {
  font-size: 14px;
  line-height: 1.8;
  color: #1a1a2e;
  word-break: break-word;
}

.markdown-content :deep(h2) {
  font-size: 18px;
  font-weight: 700;
  margin: 16px 0 8px;
  color: #1a1a2e;
}

.markdown-content :deep(h3) {
  font-size: 15px;
  font-weight: 600;
  margin: 12px 0 6px;
  color: #333;
}

.markdown-content :deep(p) {
  margin: 6px 0;
}

.markdown-content :deep(ul),
.markdown-content :deep(ol) {
  padding-left: 20px;
  margin: 6px 0;
}

.markdown-content :deep(li) {
  margin: 3px 0;
}

.markdown-content :deep(strong) {
  font-weight: 600;
  color: #1a1a2e;
}

.markdown-content :deep(hr) {
  border: none;
  border-top: 1px dashed #e0e0e0;
  margin: 12px 0;
}

.markdown-content :deep(code) {
  background: var(--bg-table-header);
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 13px;
  font-family: 'Consolas', 'Monaco', monospace;
}

.markdown-content :deep(pre) {
  background: var(--bg-table-header);
  padding: 12px;
  border-radius: 8px;
  overflow-x: auto;
  margin: 8px 0;
}

.markdown-content :deep(pre code) {
  background: none;
  padding: 0;
}

.markdown-content :deep(blockquote) {
  border-left: 3px solid #4361ee;
  padding-left: 12px;
  margin: 8px 0;
  color: #666;
}

/* ========== 生成指示器 ========== */
.generating-indicator {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 0;
}

/* ========== 日志终端 ========== */
.log-terminal {
  margin: 8px 0 12px;
  border: 1px solid #1a1a2e;
  border-radius: 8px;
  overflow: hidden;
  background: #0d1117;
}

.log-terminal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 6px 12px;
  background: #161b22;
  border-bottom: 1px solid #30363d;
}

.log-terminal-title {
  font-size: 12px;
  font-weight: 600;
  color: #8b949e;
  display: flex;
  align-items: center;
  gap: 6px;
}

.log-terminal-icon {
  animation: spin 1s linear infinite;
  color: #58a6ff;
}

.log-terminal-count {
  font-size: 11px;
  color: #6e7681;
}

.log-terminal-body {
  max-height: 240px;
  overflow-y: auto;
  padding: 8px 12px;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 12px;
  line-height: 1.6;
  scroll-behavior: smooth;
}

.log-terminal-body::-webkit-scrollbar {
  width: 6px;
}

.log-terminal-body::-webkit-scrollbar-track {
  background: transparent;
}

.log-terminal-body::-webkit-scrollbar-thumb {
  background: #30363d;
  border-radius: 3px;
}

.log-line {
  display: flex;
  gap: 8px;
  padding: 1px 0;
  word-break: break-all;
  white-space: pre-wrap;
}

.log-time {
  color: #6e7681;
  flex-shrink: 0;
  font-size: 11px;
}

.log-message {
  color: #c9d1d9;
  flex: 1;
  min-width: 0;
}

.log-line.error .log-message {
  color: #f85149;
}

.log-line.warn .log-message {
  color: #d29922;
}

.log-line.info .log-message {
  color: #c9d1d9;
}

.generating-indicator .dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #4361ee;
  animation: dot-bounce 1.4s infinite ease-in-out;
}

.generating-indicator .dot:nth-child(2) {
  animation-delay: 0.2s;
}

.generating-indicator .dot:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes dot-bounce {
  0%, 80%, 100% { transform: scale(0); opacity: 0.5; }
  40% { transform: scale(1); opacity: 1; }
}

/* ========== 输入区域 ========== */
.input-area {
  padding: 16px 24px 20px;
  background: var(--bg-table-header);
  border-top: 1px solid transparent;
}

.input-wrapper {
  max-width: 800px;
  margin: 0 auto;
  display: flex;
  align-items: flex-end;
  gap: 12px;
  background: var(--bg-card);
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  padding: 8px 12px;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.input-wrapper:focus-within {
  border-color: #4361ee;
  box-shadow: 0 0 0 3px rgba(67, 97, 238, 0.1);
}

.chat-input {
  flex: 1;
}

.chat-input :deep(.el-textarea__inner) {
  border: none !important;
  box-shadow: none !important;
  background: transparent !important;
  padding: 4px 0 !important;
  font-size: 14px;
  line-height: 1.6;
  resize: none;
}

.send-btn {
  background: #4361ee !important;
  border: none !important;
  color: #fff !important;
  flex-shrink: 0;
  margin-bottom: 2px;
}

.send-btn:disabled {
  background: #ccc !important;
}

.input-hint {
  max-width: 800px;
  margin: 6px auto 0;
  text-align: center;
  font-size: 12px;
  color: #999;
}
</style>
