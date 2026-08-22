<template>
  <div class="job-detail-page" v-loading="loading">
    <!-- 返回按钮 -->
    <div class="back-bar">
      <el-button text @click="goBack">
        <el-icon><ArrowLeft /></el-icon>
        返回列表
      </el-button>
    </div>

    <div v-if="job.job_id" class="detail-content">
      <!-- 职位头部信息（渐变卡片） -->
      <div class="job-hero">
        <div class="hero-left">
          <h1 class="hero-title">{{ job.job_name }}</h1>
          <div class="hero-meta">
            <span v-if="job.city" class="meta-item">
              <el-icon><Location /></el-icon>
              {{ job.city }}
            </span>
            <span v-if="job.area" class="meta-item">
              <el-icon><MapLocation /></el-icon>
              {{ job.area }}
            </span>
            <span v-if="job.experience" class="meta-item">
              <el-icon><Timer /></el-icon>
              {{ job.experience }}
            </span>
            <span v-if="job.education" class="meta-item">
              <el-icon><Reading /></el-icon>
              {{ job.education }}
            </span>
          </div>
        </div>
        <div class="hero-right">
          <div class="salary-box" v-if="job.salary_desc">
            <span class="salary-label">薪资范围</span>
            <span class="salary-value">{{ job.salary_desc }}</span>
          </div>
        </div>
      </div>

      <!-- 双栏布局 -->
      <el-row :gutter="20">
        <!-- 左栏：主要信息 -->
        <el-col :span="16">
          <!-- 职位描述 -->
          <div class="info-section">
            <div class="section-header">
              <div class="section-icon" style="background: var(--primary-gradient);">
                <el-icon><Document /></el-icon>
              </div>
              <h3 class="section-title">职位描述</h3>
            </div>
            <div class="section-body">
              <div v-if="job.job_desc" class="jd-content">{{ job.job_desc }}</div>
              <el-empty v-else description="暂无描述" :image-size="60" />
            </div>
          </div>

          <!-- 技能要求 -->
          <div class="info-section" v-if="uniqueSkills.length">
            <div class="section-header">
              <div class="section-icon" style="background: var(--warning-gradient);">
                <el-icon><Star /></el-icon>
              </div>
              <h3 class="section-title">技能要求</h3>
            </div>
            <div class="section-body">
              <div class="tag-cloud">
                <span
                  v-for="skill in uniqueSkills"
                  :key="skill"
                  class="skill-tag"
                >
                  {{ skill }}
                </span>
              </div>
            </div>
          </div>

          <!-- 经验要求 -->
          <div class="info-section" v-if="job.welfare && job.welfare.length">
            <div class="section-header">
              <div class="section-icon" style="background: var(--success-gradient);">
                <el-icon><Medal /></el-icon>
              </div>
              <h3 class="section-title">经验要求</h3>
            </div>
            <div class="section-body">
              <div class="tag-cloud">
                <span
                  v-for="w in job.welfare"
                  :key="w"
                  class="welfare-tag"
                >
                  {{ w }}
                </span>
              </div>
            </div>
          </div>
        </el-col>

        <!-- 右栏：侧边信息 -->
        <el-col :span="8">
          <!-- 公司信息 -->
          <div class="side-card">
            <div class="side-header">
              <div class="side-icon" style="background: var(--info-gradient);">
                <el-icon><OfficeBuilding /></el-icon>
              </div>
              <span class="side-title">公司信息</span>
            </div>
            <div class="side-body">
              <div class="info-row">
                <span class="info-label">公司名称</span>
                <span class="info-value">{{ job.company_name || '-' }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">所属行业</span>
                <span class="info-value">{{ job.company_industry || '-' }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">公司规模</span>
                <span class="info-value">{{ job.company_scale || '-' }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">融资阶段</span>
                <span class="info-value">{{ job.company_stage || '-' }}</span>
              </div>
            </div>
          </div>

          <!-- 招聘者信息 -->
          <div class="side-card">
            <div class="side-header">
              <div class="side-icon" style="background: var(--danger-gradient);">
                <el-icon><User /></el-icon>
              </div>
              <span class="side-title">招聘者</span>
            </div>
            <div class="side-body">
              <div class="boss-avatar-row">
                <div class="boss-avatar">
                  {{ (job.boss_name || '?').charAt(0) }}
                </div>
                <div class="boss-info">
                  <span class="boss-name">{{ job.boss_name || '未知' }}</span>
                  <span class="boss-title-text">{{ job.boss_title || '-' }}</span>
                </div>
                <el-tag
                  :type="job.boss_active_status === 'online' ? 'success' : 'info'"
                  size="small"
                  effect="light"
                >
                  {{ job.boss_active_status === 'online' ? '在线' : '离线' }}
                </el-tag>
              </div>
            </div>
          </div>

          <!-- 采集信息 -->
          <div class="side-card">
            <div class="side-header">
              <div class="side-icon" style="background: var(--primary-gradient);">
                <el-icon><DataLine /></el-icon>
              </div>
              <span class="side-title">采集信息</span>
            </div>
            <div class="side-body">
              <div class="info-row">
                <span class="info-label">职位ID</span>
                <span class="info-value mono-text">{{ job.job_id }}</span>
              </div>
              <div class="info-row">
                <span class="info-label">采集时间</span>
                <span class="info-value">{{ job.fetch_time || '-' }}</span>
              </div>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>

    <el-empty v-else-if="!loading" description="未找到职位数据" :image-size="100" />
  </div>
</template>

<script>
export default { name: 'JobDetail' }
</script>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  ArrowLeft, Location, MapLocation, Timer, Reading,
  Document, Star, Medal, OfficeBuilding, User, DataLine,
} from '@element-plus/icons-vue'
import api from '../api'

const route = useRoute()
const router = useRouter()

const loading = ref(false)
const job = ref({})

// 技能去重（忽略大小写）
const uniqueSkills = computed(() => {
  const skills = job.value.skills || []
  const seen = new Set()
  const result = []
  for (const s of skills) {
    const key = String(s).trim().toLowerCase()
    if (key && !seen.has(key)) {
      seen.add(key)
      result.push(s)
    }
  }
  return result
})

async function loadJob() {
  loading.value = true
  try {
    job.value = await api.getJobDetail(route.params.jobId)
  } catch (e) {
    job.value = {}
  } finally {
    loading.value = false
  }
}

function goBack() {
  router.push('/jobs')
}

// 监听路由参数变化（keep-alive 缓存组件时 onMounted 不会重新触发）
watch(
  () => route.params.jobId,
  (newId, oldId) => {
    if (newId && newId !== oldId) {
      loadJob()
    }
  }
)

onMounted(loadJob)
</script>

<style scoped>
.back-bar {
  margin-bottom: 12px;
}

/* ========== Hero 卡片 ========== */
.job-hero {
  background: linear-gradient(135deg, #4361ee 0%, #3a0ca3 100%);
  border-radius: var(--radius-lg);
  padding: 28px 32px;
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 8px 32px rgba(67, 97, 238, 0.25);
  color: #fff;
}

.hero-title {
  font-size: 24px;
  font-weight: 700;
  margin-bottom: 14px;
  color: #fff;
}

.hero-meta {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.85);
}

.salary-box {
  text-align: center;
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  border-radius: var(--radius-md);
  padding: 14px 24px;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.salary-label {
  display: block;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.7);
  margin-bottom: 4px;
}

.salary-value {
  display: block;
  font-size: 22px;
  font-weight: 700;
  color: #ffd166;
}

/* ========== 信息区块 ========== */
.info-section {
  background: #fff;
  border-radius: var(--radius-md);
  margin-bottom: 20px;
  box-shadow: var(--shadow-card);
  overflow: hidden;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 24px;
  border-bottom: 1px solid var(--border-light);
}

.section-icon {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  flex-shrink: 0;
}

.section-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
}

.section-body {
  padding: 20px 24px;
}

/* ========== JD 内容 ========== */
.jd-content {
  white-space: pre-wrap;
  word-break: break-all;
  line-height: 1.9;
  font-size: 14px;
  color: var(--text-secondary);
  font-family: 'Inter', 'PingFang SC', 'Microsoft YaHei', sans-serif;
}

/* ========== 标签云 ========== */
.tag-cloud {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.skill-tag {
  display: inline-block;
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 500;
  background: linear-gradient(135deg, #fff8e1 0%, #ffecb3 100%);
  color: #f57c00;
  border: 1px solid #ffd166;
  transition: transform 0.2s;
}

.skill-tag:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(255, 209, 102, 0.3);
}

.welfare-tag {
  display: inline-block;
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 500;
  background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
  color: #2e7d32;
  border: 1px solid #81c784;
  transition: transform 0.2s;
}

.welfare-tag:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(6, 214, 160, 0.2);
}

/* ========== 侧边卡片 ========== */
.side-card {
  background: #fff;
  border-radius: var(--radius-md);
  margin-bottom: 20px;
  box-shadow: var(--shadow-card);
  overflow: hidden;
}

.side-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 20px;
  border-bottom: 1px solid var(--border-light);
}

.side-icon {
  width: 28px;
  height: 28px;
  border-radius: 7px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  flex-shrink: 0;
}

.side-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.side-body {
  padding: 16px 20px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 8px 0;
  border-bottom: 1px solid #f5f5f5;
}

.info-row:last-child {
  border-bottom: none;
}

.info-label {
  color: var(--text-muted);
  font-size: 13px;
  flex-shrink: 0;
}

.info-value {
  color: var(--text-primary);
  font-size: 13px;
  text-align: right;
  word-break: break-all;
  font-weight: 500;
}

.mono-text {
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 12px;
}

/* ========== 招聘者头像 ========== */
.boss-avatar-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.boss-avatar {
  width: 42px;
  height: 42px;
  border-radius: 50%;
  background: var(--danger-gradient);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 16px;
  flex-shrink: 0;
}

.boss-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.boss-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.boss-title-text {
  font-size: 12px;
  color: var(--text-muted);
}
</style>
