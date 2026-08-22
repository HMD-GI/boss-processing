<template>
  <div class="job-list-page">
    <!-- 搜索栏 -->
    <div class="search-bar">
      <div class="search-fields">
        <div class="field-group">
          <el-icon class="field-icon"><Search /></el-icon>
          <el-input
            v-model="searchForm.keyword"
            placeholder="搜索职位名称"
            clearable
            size="large"
            @keyup.enter="handleSearch"
          />
        </div>
        <div class="field-group">
          <el-icon class="field-icon"><Location /></el-icon>
          <el-select
            v-model="searchForm.city"
            placeholder="选择城市"
            clearable
            filterable
            size="large"
          >
            <el-option
              v-for="c in cities"
              :key="c"
              :label="c"
              :value="c"
            />
          </el-select>
        </div>
        <div class="field-group">
          <el-icon class="field-icon"><OfficeBuilding /></el-icon>
          <el-input
            v-model="searchForm.company"
            placeholder="公司名称"
            clearable
            size="large"
            @keyup.enter="handleSearch"
          />
        </div>
      </div>
      <div class="search-actions">
        <el-button type="primary" size="large" @click="handleSearch">
          <el-icon><Search /></el-icon>
          <span>搜索</span>
        </el-button>
        <el-button size="large" @click="handleReset">
          <el-icon><RefreshLeft /></el-icon>
          <span>重置</span>
        </el-button>
      </div>
    </div>

    <!-- 职位表格 -->
    <div class="table-container">
      <div class="table-toolbar">
        <div class="toolbar-left">
          <span class="table-title">职位列表</span>
          <span class="table-count">{{ total }} 条记录</span>
        </div>
        <div class="toolbar-right">
          <el-select v-model="pageSize" @change="loadJobs" size="default" style="width: 110px">
            <el-option :value="10" label="10 条/页" />
            <el-option :value="20" label="20 条/页" />
            <el-option :value="50" label="50 条/页" />
          </el-select>
        </div>
      </div>

      <el-table
        :data="jobs"
        v-loading="loading"
        style="width: 100%"
        @row-click="handleRowClick"
        :header-cell-style="{ background: '#f8f9fc', color: '#5c677d', fontWeight: 600 }"
      >
        <el-table-column prop="job_name" label="职位名称" min-width="220" show-overflow-tooltip>
          <template #default="{ row }">
            <div class="job-name-cell">
              <span class="job-name-text">{{ row.job_name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="salary_desc" label="薪资" width="130" sortable>
          <template #default="{ row }">
            <span v-if="row.salary_desc" class="salary-badge">{{ row.salary_desc }}</span>
            <span v-else class="text-muted">-</span>
          </template>
        </el-table-column>
        <el-table-column prop="city" label="城市" width="80">
          <template #default="{ row }">
            <span class="city-text">{{ row.city || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="experience" label="经验" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.experience" size="small" effect="plain" type="info">{{ row.experience }}</el-tag>
            <span v-else class="text-muted">-</span>
          </template>
        </el-table-column>
        <el-table-column prop="education" label="学历" width="80">
          <template #default="{ row }">
            <span class="edu-text">{{ row.education || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="company_name" label="公司" min-width="170" show-overflow-tooltip>
          <template #default="{ row }">
            <div class="company-cell">
              <el-icon class="company-icon"><OfficeBuilding /></el-icon>
              <span>{{ row.company_name || '-' }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="fetch_time" label="采集时间" width="170">
          <template #default="{ row }">
            <div class="time-cell">
              <el-icon><Clock /></el-icon>
              <span>{{ row.fetch_time || '-' }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="90" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click.stop="goDetail(row.job_id)">
              查看详情
            </el-button>
          </template>
        </el-table-column>

        <template #empty>
          <div class="empty-state">
            <el-icon :size="48" color="#c0c4cc"><DocumentRemove /></el-icon>
            <p class="empty-title">暂无职位数据</p>
            <p class="empty-desc">请前往「采集任务」页面发起数据采集</p>
          </div>
        </template>
      </el-table>

      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="pageSize"
          :total="total"
          layout="total, prev, pager, next, jumper"
          @current-change="loadJobs"
          background
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  Search, RefreshLeft, Location, OfficeBuilding,
  Clock, DocumentRemove,
} from '@element-plus/icons-vue'
import api from '../api'

const router = useRouter()

const loading = ref(false)
const jobs = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)
const cities = ref([])

const searchForm = reactive({
  keyword: '',
  city: '',
  company: '',
})

async function loadCities() {
  try {
    const res = await api.getCitiesWithData()
    cities.value = res.cities || []
  } catch (e) {
    // 忽略
  }
}

async function loadJobs() {
  loading.value = true
  try {
    const res = await api.getJobs({
      keyword: searchForm.keyword || undefined,
      city: searchForm.city || undefined,
      company: searchForm.company || undefined,
      page: currentPage.value,
      page_size: pageSize.value,
    })
    jobs.value = res.data || []
    total.value = res.total || 0
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  currentPage.value = 1
  loadJobs()
}

function handleReset() {
  searchForm.keyword = ''
  searchForm.city = ''
  searchForm.company = ''
  currentPage.value = 1
  loadJobs()
}

function goDetail(jobId) {
  router.push(`/jobs/${jobId}`)
}

function handleRowClick(row) {
  goDetail(row.job_id)
}

onMounted(() => {
  loadCities()
  loadJobs()
})
</script>

<style scoped>
/* ========== 搜索栏 ========== */
.search-bar {
  background: #fff;
  border-radius: var(--radius-md);
  padding: 20px 24px;
  margin-bottom: 20px;
  box-shadow: var(--shadow-card);
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.search-fields {
  display: flex;
  gap: 12px;
  flex: 1;
  flex-wrap: wrap;
}

.field-group {
  position: relative;
  min-width: 200px;
}

.field-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-muted);
  z-index: 1;
  font-size: 16px;
}

.field-group :deep(.el-input__wrapper),
.field-group :deep(.el-select .el-input__wrapper) {
  padding-left: 34px !important;
  border-radius: var(--radius-sm) !important;
}

.search-actions {
  display: flex;
  gap: 8px;
}

/* ========== 表格容器 ========== */
.table-container {
  background: #fff;
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-card);
  overflow: hidden;
}

.table-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 18px 24px;
  border-bottom: 1px solid var(--border-light);
}

.toolbar-left {
  display: flex;
  align-items: baseline;
  gap: 10px;
}

.table-title {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary);
}

.table-count {
  font-size: 13px;
  color: var(--text-muted);
  background: #f0f2f5;
  padding: 2px 10px;
  border-radius: 20px;
}

/* ========== 表格单元格 ========== */
.job-name-cell .job-name-text {
  font-weight: 500;
  color: var(--text-primary);
}

.salary-badge {
  display: inline-block;
  background: linear-gradient(135deg, #06d6a0 0%, #07b394 100%);
  color: #fff;
  padding: 3px 10px;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 600;
  white-space: nowrap;
}

.city-text {
  color: var(--text-secondary);
  font-weight: 500;
}

.edu-text {
  color: var(--text-secondary);
}

.company-cell {
  display: flex;
  align-items: center;
  gap: 6px;
  color: var(--text-secondary);
}

.company-icon {
  color: var(--primary-light);
  flex-shrink: 0;
}

.time-cell {
  display: flex;
  align-items: center;
  gap: 5px;
  color: var(--text-muted);
  font-size: 13px;
}

.text-muted {
  color: var(--text-muted);
}

/* ========== 分页 ========== */
.pagination-wrapper {
  padding: 16px 24px;
  display: flex;
  justify-content: flex-end;
  border-top: 1px solid var(--border-light);
}

/* ========== 空状态 ========== */
.empty-state {
  padding: 60px 20px;
  text-align: center;
}

.empty-title {
  margin-top: 16px;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-secondary);
}

.empty-desc {
  margin-top: 8px;
  font-size: 13px;
  color: var(--text-muted);
}
</style>
