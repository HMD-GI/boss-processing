<template>
  <div class="resume-sidebar" :style="{ '--theme': color }">
    <div class="rsb-layout">
      <!-- 侧边栏 -->
      <aside class="rsb-aside" :style="{ background: asideBg }">
        <!-- 个人信息 -->
        <div class="rsb-aside-section">
          <div class="rsb-avatar">
            <img v-if="data.personal.avatar" :src="data.personal.avatar" alt="avatar" />
            <span v-else>{{ (data.personal.name || '?')[0] }}</span>
          </div>
          <h1 class="rsb-name">{{ data.personal.name || '姓名' }}</h1>
          <p class="rsb-intention">{{ data.personal.jobIntention || '求职意向' }}</p>
        </div>

        <!-- 联系方式 -->
        <div v-if="data.personal.phone || data.personal.email || data.personal.github || data.personal.blog" class="rsb-aside-section">
          <h3 class="rsb-aside-title">联系方式</h3>
          <div v-if="data.personal.phone" class="rsb-contact-row">
            <span class="rsb-label">手机</span>
            <span class="rsb-value">{{ data.personal.phone }}</span>
          </div>
          <div v-if="data.personal.email" class="rsb-contact-row">
            <span class="rsb-label">邮箱</span>
            <span class="rsb-value">{{ data.personal.email }}</span>
          </div>
          <div v-if="data.personal.github" class="rsb-contact-row">
            <span class="rsb-label">GitHub</span>
            <span class="rsb-value rsb-break">{{ data.personal.github }}</span>
          </div>
          <div v-if="data.personal.blog" class="rsb-contact-row">
            <span class="rsb-label">博客</span>
            <span class="rsb-value rsb-break">{{ data.personal.blog }}</span>
          </div>
        </div>

        <!-- 技能 -->
        <div v-if="data.skills.length" class="rsb-aside-section">
          <h3 class="rsb-aside-title">专业技能</h3>
          <div v-for="skill in data.skills" :key="skill.id" class="rsb-skill">
            <span class="rsb-skill-name">{{ skill.name }}</span>
          </div>
        </div>

        <!-- 奖项荣誉 -->
        <div v-if="data.awards.length" class="rsb-aside-section">
          <h3 class="rsb-aside-title">奖项荣誉</h3>
          <div v-for="award in data.awards" :key="award.id" class="rsb-award">
            <p class="rsb-award-name">{{ award.name }}</p>
            <p class="rsb-award-meta">{{ award.organization }} · {{ award.date }}</p>
          </div>
        </div>
      </aside>

      <!-- 主内容 -->
      <main class="rsb-main">
        <!-- 自我评价 -->
        <section v-if="data.personal.selfEvaluation" class="rsb-main-section">
          <h2 class="rsb-main-title">自我评价</h2>
          <p class="rsb-text">{{ data.personal.selfEvaluation }}</p>
        </section>

        <!-- 教育经历 -->
        <section v-if="data.education.length" class="rsb-main-section">
          <h2 class="rsb-main-title">教育经历</h2>
          <div v-for="edu in data.education" :key="edu.id" class="rsb-item">
            <div class="rsb-item-header">
              <span class="rsb-item-title">{{ edu.school }}</span>
              <span class="rsb-item-date">{{ edu.startDate }} - {{ edu.endDate }}</span>
            </div>
            <p class="rsb-item-sub">
              {{ edu.major }} · {{ edu.degree }}
              <template v-if="edu.gpa"> | GPA: {{ edu.gpa }}</template>
              <template v-if="edu.rank"> | 排名: {{ edu.rank }}</template>
            </p>
            <p v-if="edu.courses" class="rsb-text-sm">主修课程：{{ edu.courses }}</p>
          </div>
        </section>

        <!-- 工作经历 -->
        <section v-if="data.workExperience.length" class="rsb-main-section">
          <h2 class="rsb-main-title">工作经历</h2>
          <div v-for="work in data.workExperience" :key="work.id" class="rsb-item">
            <div class="rsb-item-header">
              <span class="rsb-item-title">{{ work.company }}</span>
              <span class="rsb-item-date">{{ work.startDate }} - {{ work.endDate }}</span>
            </div>
            <p class="rsb-item-sub">{{ work.position }} <template v-if="work.department">| {{ work.department }}</template></p>
            <ul v-if="work.description?.length" class="rsb-list">
              <li v-for="(desc, i) in work.description" :key="i" class="rsb-text-sm">{{ desc }}</li>
            </ul>
          </div>
        </section>

        <!-- 项目经历 -->
        <section v-if="data.projects.length" class="rsb-main-section">
          <h2 class="rsb-main-title">项目经历</h2>
          <div v-for="proj in data.projects" :key="proj.id" class="rsb-item">
            <div class="rsb-item-header">
              <span class="rsb-item-title">{{ proj.name }}</span>
              <span class="rsb-item-role">{{ proj.role }}</span>
            </div>
            <p v-if="proj.techStack" class="rsb-text-sm rsb-tech">技术栈：{{ proj.techStack }}</p>
            <p v-if="proj.description" class="rsb-text-sm">{{ proj.description }}</p>
            <p v-if="proj.achievements" class="rsb-text-sm rsb-highlight">成果：{{ proj.achievements }}</p>
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
  color: { type: String, default: '#4361ee' },
})

const asideBg = computed(() => {
  return `linear-gradient(135deg, ${props.color} 0%, ${props.color}cc 100%)`
})
</script>

<style scoped>
.resume-sidebar {
  font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
  font-size: 14px;
  color: #333;
  line-height: 1.6;
  background: #fff;
  width: 794px;
  min-height: 1123px;
}

.rsb-layout {
  display: flex;
  min-height: 1123px;
}

/* 侧边栏 */
.rsb-aside {
  width: 260px;
  flex-shrink: 0;
  color: #fff;
  padding: 30px 20px;
}

.rsb-aside-section {
  margin-bottom: 24px;
}

.rsb-avatar {
  width: 70px;
  height: 98px;
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.2);
  margin: 0 auto 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  border: 2px solid rgba(255, 255, 255, 0.3);
}

.rsb-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.rsb-avatar span {
  font-size: 32px;
  font-weight: 700;
  color: #fff;
}

.rsb-name {
  font-size: 20px;
  font-weight: 700;
  text-align: center;
  color: #fff;
}

.rsb-intention {
  font-size: 13px;
  text-align: center;
  color: rgba(255, 255, 255, 0.8);
  margin-top: 2px;
}

.rsb-aside-title {
  font-size: 13px;
  font-weight: 600;
  color: #fff;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  padding-bottom: 6px;
  margin-bottom: 10px;
  letter-spacing: 1px;
}

.rsb-contact-row {
  display: flex;
  flex-direction: column;
  margin-bottom: 8px;
}

.rsb-label {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.6);
}

.rsb-value {
  font-size: 12px;
  color: #fff;
  word-break: break-all;
}

.rsb-break {
  font-size: 11px;
}

/* 技能 */
.rsb-skill {
  margin-bottom: 10px;
}

.rsb-skill-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 4px;
}

.rsb-skill-name {
  font-size: 12px;
  color: #fff;
  font-weight: 500;
}

.rsb-skill-level {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.7);
}

.rsb-skill-bar-bg {
  height: 4px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 2px;
}

.rsb-skill-bar {
  height: 100%;
  background: #fff;
  border-radius: 2px;
}

/* 奖项 */
.rsb-award {
  margin-bottom: 8px;
}

.rsb-award-name {
  font-size: 12px;
  color: #fff;
  font-weight: 500;
}

.rsb-award-meta {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.6);
}

/* 主内容 */
.rsb-main {
  flex: 1;
  padding: 30px 28px;
}

.rsb-main-section {
  margin-bottom: 20px;
}

.rsb-main-title {
  font-size: 15px;
  font-weight: 700;
  color: var(--theme);
  margin-bottom: 10px;
  padding-bottom: 6px;
  border-bottom: 2px solid #eef0f4;
}

.rsb-item {
  margin-bottom: 12px;
}

.rsb-item-header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
}

.rsb-item-title {
  font-size: 14px;
  font-weight: 600;
  color: #1a1a2e;
}

.rsb-item-date {
  font-size: 12px;
  color: #999;
}

.rsb-item-sub {
  font-size: 13px;
  color: #555;
  margin: 2px 0;
}

.rsb-item-role {
  font-size: 12px;
  color: var(--theme);
}

/* 文本 */
.rsb-text {
  font-size: 13px;
  color: #555;
  line-height: 1.7;
}

.rsb-text-sm {
  font-size: 12px;
  color: #666;
  margin: 2px 0;
  line-height: 1.6;
}

.rsb-tech {
  color: var(--theme);
}

.rsb-highlight {
  color: var(--theme);
  font-weight: 500;
}

/* 列表 */
.rsb-list {
  list-style: disc;
  padding-left: 18px;
  margin: 4px 0;
}
</style>
