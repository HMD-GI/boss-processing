<template>
  <div class="resume-dark-sidebar" :style="{ '--theme': color }">
    <div class="ds-layout">
      <!-- 左侧深色面板 -->
      <aside class="ds-aside">
        <div class="ds-aside-inner" :style="{ background: asideBg }">
          <div class="ds-avatar" v-if="data.personal.avatar">
            <img :src="data.personal.avatar" alt="photo" />
          </div>
          <h1 class="ds-name">{{ data.personal.name || '姓名' }}</h1>
          <p class="ds-intention">{{ data.personal.jobIntention || '求职意向' }}</p>

          <!-- 联系方式 -->
          <div v-if="data.personal.phone || data.personal.email || data.personal.github || data.personal.blog" class="ds-block">
            <h3 class="ds-block-title">联系方式</h3>
            <ul class="ds-contact-list">
              <li v-if="data.personal.phone">{{ data.personal.phone }}</li>
              <li v-if="data.personal.email">{{ data.personal.email }}</li>
              <li v-if="data.personal.github">{{ data.personal.github }}</li>
              <li v-if="data.personal.blog">{{ data.personal.blog }}</li>
            </ul>
          </div>

          <!-- 自我评价 -->
          <div v-if="data.personal.selfEvaluation" class="ds-block">
            <h3 class="ds-block-title">自我评价</h3>
            <p class="ds-eval-text">{{ data.personal.selfEvaluation }}</p>
          </div>

          <!-- 技能 -->
          <div v-if="data.skills.length" class="ds-block">
            <h3 class="ds-block-title">专业技能</h3>
            <div class="ds-skills">
              <span v-for="skill in data.skills" :key="skill.id" class="ds-skill-item">{{ skill.name }}</span>
            </div>
          </div>

          <!-- 奖项 -->
          <div v-if="data.awards.length" class="ds-block">
            <h3 class="ds-block-title">荣誉奖项</h3>
            <div v-for="award in data.awards" :key="award.id" class="ds-award-item">
              <span class="ds-award-name">{{ award.name }}</span>
              <span class="ds-award-date">{{ award.date }}</span>
            </div>
          </div>
        </div>
      </aside>

      <!-- 右侧主内容 -->
      <main class="ds-main">
        <!-- 教育经历 -->
        <section v-if="data.education.length" class="ds-section">
          <div class="ds-section-header">
            <span class="ds-section-icon" :style="{ background: color }"></span>
            <h2 class="ds-section-title" :style="{ color: color }">教育背景</h2>
          </div>
          <div v-for="edu in data.education" :key="edu.id" class="ds-entry">
            <div class="ds-entry-header">
              <span class="ds-entry-school">{{ edu.school }}</span>
              <span class="ds-entry-date">{{ edu.startDate }} — {{ edu.endDate }}</span>
            </div>
            <p class="ds-entry-detail">{{ edu.major }} · {{ edu.degree }}<span v-if="edu.gpa"> · GPA: {{ edu.gpa }}</span><span v-if="edu.rank"> · 排名: {{ edu.rank }}</span></p>
            <p v-if="edu.courses" class="ds-text-sm">主修课程：{{ edu.courses }}</p>
          </div>
        </section>

        <!-- 工作经历 -->
        <section v-if="data.workExperience.length" class="ds-section">
          <div class="ds-section-header">
            <span class="ds-section-icon" :style="{ background: color }"></span>
            <h2 class="ds-section-title" :style="{ color: color }">工作经历</h2>
          </div>
          <div v-for="work in data.workExperience" :key="work.id" class="ds-entry">
            <div class="ds-entry-header">
              <span class="ds-entry-school">{{ work.company }}</span>
              <span class="ds-entry-date">{{ work.startDate }} — {{ work.endDate }}</span>
            </div>
            <p class="ds-entry-detail">{{ work.position }}<span v-if="work.department"> · {{ work.department }}</span></p>
            <ul v-if="work.description?.length" class="ds-list">
              <li v-for="(desc, i) in work.description" :key="i" class="ds-text-sm">{{ desc }}</li>
            </ul>
          </div>
        </section>

        <!-- 项目经历 -->
        <section v-if="data.projects.length" class="ds-section">
          <div class="ds-section-header">
            <span class="ds-section-icon" :style="{ background: color }"></span>
            <h2 class="ds-section-title" :style="{ color: color }">项目经历</h2>
          </div>
          <div v-for="proj in data.projects" :key="proj.id" class="ds-entry">
            <div class="ds-entry-header">
              <span class="ds-entry-school">{{ proj.name }}</span>
              <span class="ds-entry-role" :style="{ color: color }">{{ proj.role }}</span>
            </div>
            <p v-if="proj.techStack" class="ds-tech">技术栈：{{ proj.techStack }}</p>
            <p v-if="proj.description" class="ds-text-sm">{{ proj.description }}</p>
            <p v-if="proj.achievements" class="ds-text-sm ds-highlight" :style="{ color: color }">成果：{{ proj.achievements }}</p>
          </div>
        </section>
      </main>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  data: { type: Object, required: true },
  color: { type: String, default: '#545969' },
})

const asideBg = computed(() => {
  // 深色侧边栏：主题色加深
  return props.color
})

const textColor = computed(() => '#fff')
</script>

<style scoped>
.resume-dark-sidebar {
  font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
  font-size: 14px;
  color: #333;
  line-height: 1.6;
  background: #fff;
  width: 794px;
  min-height: 1123px;
}

.ds-layout {
  display: flex;
  min-height: 1123px;
}

/* 左侧面板 */
.ds-aside {
  width: 260px;
  flex-shrink: 0;
}

.ds-aside-inner {
  min-height: 100%;
  padding: 30px 20px;
  color: #fff;
}

.ds-avatar {
  width: 85px;
  height: 119px;
  border-radius: 6px;
  overflow: hidden;
  border: 2px solid rgba(255, 255, 255, 0.3);
  margin: 0 auto 16px;
}

.ds-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.ds-name {
  font-size: 22px;
  font-weight: 700;
  text-align: center;
  color: #fff;
  margin-bottom: 4px;
}

.ds-intention {
  font-size: 13px;
  text-align: center;
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 24px;
}

.ds-block {
  margin-bottom: 22px;
}

.ds-block-title {
  font-size: 13px;
  font-weight: 700;
  color: #fff;
  padding-bottom: 6px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  margin-bottom: 10px;
  letter-spacing: 1px;
}

.ds-contact-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.ds-contact-list li {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.85);
  margin: 6px 0;
  word-break: break-all;
}

.ds-eval-text {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.8);
  line-height: 1.8;
}

.ds-skills {
  display: block;
}

.ds-skill-item {
  display: block;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.85);
  padding: 2px 0;
  line-height: 1.8;
}

.ds-award-item {
  display: flex;
  justify-content: space-between;
  padding: 4px 0;
  border-bottom: 1px dashed rgba(255, 255, 255, 0.15);
}

.ds-award-name {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.9);
}

.ds-award-date {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.6);
}

/* 右侧主内容 */
.ds-main {
  flex: 1;
  padding: 30px 30px 30px 24px;
}

.ds-section {
  margin-bottom: 24px;
}

.ds-section-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 14px;
}

.ds-section-icon {
  display: inline-block;
  width: 6px;
  height: 18px;
  border-radius: 2px;
}

.ds-section-title {
  font-size: 16px;
  font-weight: 700;
  letter-spacing: 1px;
}

.ds-entry {
  margin-bottom: 14px;
}

.ds-entry-header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
}

.ds-entry-school {
  font-size: 14px;
  font-weight: 700;
  color: #1a1a2e;
}

.ds-entry-date {
  font-size: 12px;
  color: #999;
}

.ds-entry-detail {
  font-size: 13px;
  color: #555;
  margin: 2px 0;
}

.ds-entry-role {
  font-size: 12px;
  font-weight: 600;
}

.ds-tech {
  font-size: 12px;
  color: #888;
  margin: 2px 0;
}

.ds-text-sm {
  font-size: 12px;
  color: #666;
  margin: 2px 0;
  line-height: 1.7;
}

.ds-highlight {
  font-weight: 500;
}

.ds-list {
  list-style: none;
  padding-left: 0;
  margin: 4px 0;
}

.ds-list li {
  position: relative;
  padding-left: 14px;
  margin: 3px 0;
}

.ds-list li::before {
  content: '·';
  position: absolute;
  left: 0;
  color: var(--theme);
  font-weight: 700;
  font-size: 16px;
  line-height: 1;
}
</style>
