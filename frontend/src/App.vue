<template>
  <div class="app-layout">
    <!-- 侧边栏 -->
    <aside class="sidebar" :class="{ collapsed: isCollapsed }">
      <div class="sidebar-logo">
        <div class="logo-icon">
          <el-icon :size="22"><DataAnalysis /></el-icon>
        </div>
        <transition name="fade">
          <span v-show="!isCollapsed" class="logo-text">BOSS采集系统</span>
        </transition>
      </div>

      <nav class="sidebar-nav">
        <div
          v-for="item in menuItems"
          :key="item.path"
          class="nav-item"
          :class="{ active: activeMenu === item.path }"
          @click="navigateTo(item.path)"
        >
          <el-icon :size="18" class="nav-icon">
            <component :is="item.icon" />
          </el-icon>
          <transition name="fade">
            <span v-show="!isCollapsed" class="nav-label">{{ item.label }}</span>
          </transition>
          <div v-if="activeMenu === item.path" class="active-indicator"></div>
        </div>
      </nav>

      <div class="sidebar-footer">
        <transition name="fade">
          <div v-show="!isCollapsed" class="version-info">
            <span>v1.0.0</span>
          </div>
        </transition>
      </div>
    </aside>

    <!-- 主内容区 -->
    <div class="main-wrapper">
      <!-- 顶栏 -->
      <header class="topbar">
        <div class="topbar-left">
          <el-icon
            :size="20"
            class="collapse-btn"
            @click="isCollapsed = !isCollapsed"
          >
            <Fold v-if="!isCollapsed" />
            <Expand v-else />
          </el-icon>
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item>{{ currentTitle }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="topbar-right">
          <el-tooltip :content="isDark ? '切换到白天模式' : '切换到夜间模式'" placement="bottom">
            <el-icon :size="20" class="topbar-icon theme-toggle-btn" @click="toggleTheme">
              <Sunny v-if="isDark" />
              <Moon v-else />
            </el-icon>
          </el-tooltip>
          <el-tooltip content="刷新数据" placement="bottom">
            <el-icon :size="18" class="topbar-icon" @click="refreshPage">
              <Refresh />
            </el-icon>
          </el-tooltip>
          <el-tooltip content="GitHub" placement="bottom">
            <el-icon :size="18" class="topbar-icon">
              <Link />
            </el-icon>
          </el-tooltip>
          <div class="avatar-wrapper">
            <div class="avatar">A</div>
          </div>
        </div>
      </header>

      <!-- 页面内容 -->
      <main class="content-area">
        <router-view v-slot="{ Component }">
          <keep-alive :exclude="['JobDetail']">
            <component :is="Component" />
          </keep-alive>
        </router-view>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  DataAnalysis, List, PieChart, Download, Document,
  Fold, Expand, Refresh, Link, ChatDotRound, Sunny, Moon,
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const isCollapsed = ref(false)
const isDark = ref(localStorage.getItem('theme') === 'dark')

// 初始化主题
function applyTheme() {
  const root = document.documentElement
  if (isDark.value) {
    root.classList.add('dark')
  } else {
    root.classList.remove('dark')
  }
}

function toggleTheme() {
  isDark.value = !isDark.value
  localStorage.setItem('theme', isDark.value ? 'dark' : 'light')
  applyTheme()
}

// 页面加载时立即应用主题
applyTheme()

const menuItems = [
  { path: '/jobs', label: '职位列表', icon: List },
  { path: '/stats', label: '数据统计', icon: PieChart },
  { path: '/crawl', label: '采集任务', icon: Download },
  { path: '/assistant', label: 'AI助手', icon: ChatDotRound },
  { path: '/resume', label: '简历制作', icon: Document },
]

const activeMenu = computed(() => {
  if (route.path.startsWith('/jobs')) return '/jobs'
  return route.path
})

const currentTitle = computed(() => {
  const item = menuItems.find((m) => activeMenu.value.startsWith(m.path))
  if (item) return item.label
  if (route.path.startsWith('/jobs/')) return '职位详情'
  return ''
})

function navigateTo(path) {
  router.push(path)
}

function refreshPage() {
  window.location.reload()
}
</script>

<style scoped>
.app-layout {
  display: flex;
  min-height: 100vh;
}

/* ========== 侧边栏 ========== */
.sidebar {
  width: 230px;
  background: var(--bg-sidebar);
  display: flex;
  flex-direction: column;
  position: fixed;
  top: 0;
  left: 0;
  bottom: 0;
  z-index: 1000;
  transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
}

.sidebar.collapsed {
  width: 64px;
}

.sidebar-logo {
  height: 60px;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 0 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  flex-shrink: 0;
}

.logo-icon {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: var(--primary-gradient);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  flex-shrink: 0;
  box-shadow: 0 4px 12px rgba(67, 97, 238, 0.4);
}

.logo-text {
  font-size: 15px;
  font-weight: 700;
  color: #fff;
  white-space: nowrap;
  letter-spacing: 0.5px;
}

.sidebar-nav {
  flex: 1;
  padding: 16px 12px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 11px 16px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  color: var(--text-sidebar);
  transition: all 0.25s ease;
  position: relative;
  white-space: nowrap;
}

.nav-item:hover {
  background: var(--bg-sidebar-hover);
  color: #fff;
}

.nav-item.active {
  background: var(--bg-sidebar-active);
  color: var(--text-sidebar-active);
}

.nav-icon {
  flex-shrink: 0;
}

.nav-label {
  font-size: 14px;
  font-weight: 500;
}

.active-indicator {
  position: absolute;
  right: 12px;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--success);
  box-shadow: 0 0 8px var(--success);
}

.sidebar-footer {
  padding: 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

.version-info {
  text-align: center;
  color: rgba(255, 255, 255, 0.2);
  font-size: 12px;
}

/* ========== 主内容区 ========== */
.main-wrapper {
  flex: 1;
  margin-left: 230px;
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  transition: margin-left 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.sidebar.collapsed ~ .main-wrapper {
  margin-left: 64px;
}

/* ========== 顶栏 ========== */
.topbar {
  height: 60px;
  background: var(--bg-topbar);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  box-shadow: var(--shadow-sm);
  position: sticky;
  top: 0;
  z-index: 999;
  transition: background 0.3s ease;
}

.topbar-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.collapse-btn {
  cursor: pointer;
  color: var(--text-secondary);
  transition: color 0.2s;
}

.collapse-btn:hover {
  color: var(--primary);
}

.topbar-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

.topbar-icon {
  cursor: pointer;
  color: var(--text-secondary);
  transition: color 0.2s;
}

.topbar-icon:hover {
  color: var(--primary);
}

.avatar-wrapper {
  display: flex;
  align-items: center;
}

.avatar {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  background: var(--primary-gradient);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(67, 97, 238, 0.3);
  transition: transform 0.2s;
}

.avatar:hover {
  transform: scale(1.05);
}

/* ========== 内容区 ========== */
.content-area {
  flex: 1;
  padding: 24px;
  max-width: 1600px;
  width: 100%;
}

/* ========== 主题切换按钮 ========== */
.theme-toggle-btn {
  transition: transform 0.3s ease, color 0.2s ease;
}

.theme-toggle-btn:hover {
  transform: rotate(180deg);
  color: var(--primary);
}

/* ========== 过渡动画 ========== */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
