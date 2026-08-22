<template>
  <div class="stats-page" v-loading="loading">
    <!-- 概览卡片 -->
    <div class="stat-cards">
      <div
        v-for="(card, i) in statCards"
        :key="i"
        class="stat-card"
        :style="{ '--card-gradient': card.gradient }"
      >
        <div class="card-icon">
          <el-icon :size="24">
            <component :is="card.icon" />
          </el-icon>
        </div>
        <div class="card-body">
          <div class="card-value">{{ card.value }}</div>
          <div class="card-label">{{ card.label }}</div>
        </div>
        <div class="card-decoration"></div>
      </div>
    </div>

    <!-- 图表区 -->
    <el-row :gutter="20" class="chart-row">
      <el-col :span="12">
        <div class="chart-card">
          <div class="chart-header">
            <div class="chart-title">
              <div class="chart-dot" style="background: var(--primary);"></div>
              城市分布
            </div>
          </div>
          <v-chart class="chart" :option="cityChartOption" autoresize />
        </div>
      </el-col>
      <el-col :span="12">
        <div class="chart-card">
          <div class="chart-header">
            <div class="chart-title">
              <div class="chart-dot" style="background: var(--success);"></div>
              经验要求分布
            </div>
          </div>
          <v-chart class="chart" :option="expChartOption" autoresize />
        </div>
      </el-col>
    </el-row>

    <!-- 热门公司排行 -->
    <div class="ranking-card">
      <div class="chart-header">
        <div class="chart-title">
          <div class="chart-dot" style="background: var(--warning);"></div>
          热门招聘公司 Top 10
        </div>
      </div>
      <div class="ranking-list">
        <div
          v-for="(company, i) in stats.top_companies"
          :key="i"
          class="ranking-item"
        >
          <div class="rank-badge" :class="rankClass(i)">{{ i + 1 }}</div>
          <div class="rank-info">
            <span class="rank-name">{{ company.company }}</span>
            <div class="rank-bar-wrapper">
              <div
                class="rank-bar"
                :style="{ width: barWidth(company.count) + '%' }"
              ></div>
            </div>
          </div>
          <div class="rank-count">{{ company.count }} 个职位</div>
        </div>
        <el-empty v-if="!stats.top_companies?.length" description="暂无数据" :image-size="60" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { BarChart, PieChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  GridComponent,
  LegendComponent,
} from 'echarts/components'
import VChart from 'vue-echarts'
import { Briefcase, Location, OfficeBuilding, Medal } from '@element-plus/icons-vue'
import api from '../api'

use([
  CanvasRenderer,
  BarChart,
  PieChart,
  TitleComponent,
  TooltipComponent,
  GridComponent,
  LegendComponent,
])

const loading = ref(false)
const stats = ref({})

const statCards = computed(() => [
  {
    label: '职位总数',
    value: stats.value.total_jobs || 0,
    icon: Briefcase,
    gradient: 'linear-gradient(135deg, #4361ee 0%, #3a0ca3 100%)',
  },
  {
    label: '覆盖城市',
    value: stats.value.city_distribution?.length || 0,
    icon: Location,
    gradient: 'linear-gradient(135deg, #06d6a0 0%, #07b394 100%)',
  },
  {
    label: '招聘公司',
    value: stats.value.top_companies?.length || 0,
    icon: OfficeBuilding,
    gradient: 'linear-gradient(135deg, #7209b7 0%, #560bad 100%)',
  },
  {
    label: '经验要求种类',
    value: stats.value.experience_distribution?.length || 0,
    icon: Medal,
    gradient: 'linear-gradient(135deg, #f72585 0%, #b5179e 100%)',
  },
])

const maxCount = computed(() => {
  const companies = stats.value.top_companies || []
  return companies.length > 0 ? companies[0].count : 1
})

function barWidth(count) {
  return Math.max(5, (count / maxCount.value) * 100)
}

function rankClass(i) {
  if (i === 0) return 'gold'
  if (i === 1) return 'silver'
  if (i === 2) return 'bronze'
  return ''
}

const cityChartOption = computed(() => ({
  tooltip: {
    trigger: 'axis',
    axisPointer: { type: 'shadow' },
    backgroundColor: 'rgba(26, 26, 46, 0.9)',
    borderColor: 'transparent',
    textStyle: { color: '#fff', fontSize: 13 },
  },
  grid: { left: '3%', right: '6%', top: '8%', bottom: '3%', containLabel: true },
  xAxis: {
    type: 'category',
    data: (stats.value.city_distribution || []).map((c) => c.city),
    axisLabel: { rotate: 30, color: '#5c677d', fontSize: 12 },
    axisLine: { lineStyle: { color: '#e8ecf1' } },
  },
  yAxis: {
    type: 'value',
    axisLabel: { color: '#a0a8b8', fontSize: 12 },
    splitLine: { lineStyle: { color: '#f0f2f5', type: 'dashed' } },
  },
  series: [
    {
      type: 'bar',
      data: (stats.value.city_distribution || []).map((c) => c.count),
      itemStyle: {
        borderRadius: [6, 6, 0, 0],
        color: {
          type: 'linear',
          x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [
            { offset: 0, color: '#4361ee' },
            { offset: 1, color: '#4895ef' },
          ],
        },
      },
      barWidth: '40%',
    },
  ],
}))

const expChartOption = computed(() => ({
  tooltip: {
    trigger: 'item',
    formatter: '{b}: {c} ({d}%)',
    backgroundColor: 'rgba(26, 26, 46, 0.9)',
    borderColor: 'transparent',
    textStyle: { color: '#fff', fontSize: 13 },
  },
  legend: {
    bottom: 0,
    left: 'center',
    textStyle: { color: '#5c677d', fontSize: 12 },
  },
  color: ['#4361ee', '#06d6a0', '#ffd166', '#ef476f', '#7209b7', '#4895ef'],
  series: [
    {
      type: 'pie',
      radius: ['42%', '68%'],
      center: ['50%', '42%'],
      avoidLabelOverlap: false,
      label: { show: false },
      emphasis: {
        label: { show: true, fontSize: 14, fontWeight: 'bold', color: '#1a1a2e' },
        itemStyle: { shadowBlur: 10, shadowColor: 'rgba(0,0,0,0.15)' },
      },
      data: (stats.value.experience_distribution || []).map((e) => ({
        name: e.experience || '未知',
        value: e.count,
      })),
    },
  ],
}))

async function loadStats() {
  loading.value = true
  try {
    stats.value = await api.getStats()
  } finally {
    loading.value = false
  }
}

onMounted(loadStats)
</script>

<style scoped>
/* ========== 概览卡片 ========== */
.stat-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 20px;
}

.stat-card {
  background: #fff;
  border-radius: var(--radius-md);
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: var(--shadow-card);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
}

.card-icon {
  width: 52px;
  height: 52px;
  border-radius: var(--radius-sm);
  background: var(--card-gradient);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  flex-shrink: 0;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.card-body {
  flex: 1;
}

.card-value {
  font-size: 28px;
  font-weight: 800;
  color: var(--text-primary);
  line-height: 1.2;
}

.card-label {
  margin-top: 4px;
  font-size: 13px;
  color: var(--text-muted);
}

.card-decoration {
  position: absolute;
  right: -20px;
  top: -20px;
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: var(--card-gradient);
  opacity: 0.06;
}

/* ========== 图表卡片 ========== */
.chart-row {
  margin-bottom: 20px;
}

.chart-card {
  background: #fff;
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-card);
  overflow: hidden;
}

.chart-header {
  padding: 16px 24px;
  border-bottom: 1px solid var(--border-light);
}

.chart-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
}

.chart-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.chart {
  height: 340px;
  padding: 8px;
}

/* ========== 排行榜 ========== */
.ranking-card {
  background: #fff;
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-card);
  overflow: hidden;
}

.ranking-list {
  padding: 8px 24px 16px;
}

.ranking-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 14px 0;
  border-bottom: 1px solid #f5f5f5;
  transition: background 0.2s;
}

.ranking-item:hover {
  background: #f8f9fc;
}

.ranking-item:last-child {
  border-bottom: none;
}

.rank-badge {
  width: 30px;
  height: 30px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 700;
  background: #f0f2f5;
  color: var(--text-secondary);
  flex-shrink: 0;
}

.rank-badge.gold {
  background: linear-gradient(135deg, #ffd700 0%, #ffa500 100%);
  color: #fff;
  box-shadow: 0 2px 8px rgba(255, 165, 0, 0.3);
}

.rank-badge.silver {
  background: linear-gradient(135deg, #c0c0c0 0%, #a8a8a8 100%);
  color: #fff;
  box-shadow: 0 2px 8px rgba(168, 168, 168, 0.3);
}

.rank-badge.bronze {
  background: linear-gradient(135deg, #cd7f32 0%, #b87333 100%);
  color: #fff;
  box-shadow: 0 2px 8px rgba(184, 115, 51, 0.3);
}

.rank-info {
  flex: 1;
  min-width: 0;
}

.rank-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
  display: block;
  margin-bottom: 6px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.rank-bar-wrapper {
  width: 100%;
  height: 6px;
  background: #f0f2f5;
  border-radius: 3px;
  overflow: hidden;
}

.rank-bar {
  height: 100%;
  border-radius: 3px;
  background: linear-gradient(90deg, #4361ee 0%, #4895ef 100%);
  transition: width 0.5s ease;
}

.rank-count {
  font-size: 13px;
  color: var(--text-secondary);
  font-weight: 600;
  white-space: nowrap;
  flex-shrink: 0;
}

/* ========== 响应式 ========== */
@media (max-width: 1200px) {
  .stat-cards {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
