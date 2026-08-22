<template>
  <div class="resume-professional" :style="{ '--theme': color }">
    <!-- 顶部深色头 -->
    <header class="rp-header">
      <div class="rp-header-content">
        <div class="rp-avatar" v-if="data.personal.avatar">
          <img :src="data.personal.avatar" alt="photo" />
        </div>
        <div class="rp-header-left">
          <h1 class="rp-name">{{ data.personal.name || '姓名' }}</h1>
          <p class="rp-intention">{{ data.personal.jobIntention || '求职意向' }}</p>
        </div>
        <div class="rp-header-right">
          <div v-if="data.personal.phone" class="rp-contact-line">{{ data.personal.phone }}</div>
          <div v-if="data.personal.email" class="rp-contact-line">{{ data.personal.email }}</div>
          <div v-if="data.personal.github" class="rp-contact-line">{{ data.personal.github }}</div>
          <div v-if="data.personal.blog" class="rp-contact-line">{{ data.personal.blog }}</div>
        </div>
      </div>
      <div class="rp-header-accent"></div>
    </header>

    <div class="rp-body">
      <!-- 自我评价 -->
      <section v-if="data.personal.selfEvaluation" class="rp-section">
        <h2 class="rp-section-title">个人简介</h2>
        <div class="rp-section-content">
          <p class="rp-text">{{ data.personal.selfEvaluation }}</p>
        </div>
      </section>

      <!-- 教育经历 -->
      <section v-if="data.education.length" class="rp-section">
        <h2 class="rp-section-title">教育背景</h2>
        <div class="rp-section-content">
          <div v-for="edu in data.education" :key="edu.id" class="rp-entry">
            <div class="rp-entry-header">
              <span class="rp-entry-title">{{ edu.school }}</span>
              <span class="rp-entry-date">{{ edu.startDate }} — {{ edu.endDate }}</span>
            </div>
            <div class="rp-entry-meta">
              {{ edu.major }} · {{ edu.degree }}
              <span v-if="edu.gpa"> · GPA: {{ edu.gpa }}</span>
              <span v-if="edu.rank"> · 排名: {{ edu.rank }}</span>
            </div>
            <p v-if="edu.courses" class="rp-text-sm rp-courses">{{ edu.courses }}</p>
          </div>
        </div>
      </section>

      <!-- 工作经历 -->
      <section v-if="data.workExperience.length" class="rp-section">
        <h2 class="rp-section-title">工作经历</h2>
        <div class="rp-section-content">
          <div v-for="work in data.workExperience" :key="work.id" class="rp-entry">
            <div class="rp-entry-header">
              <span class="rp-entry-title">{{ work.company }}</span>
              <span class="rp-entry-date">{{ work.startDate }} — {{ work.endDate }}</span>
            </div>
            <div class="rp-entry-meta">{{ work.position }}<span v-if="work.department"> · {{ work.department }}</span></div>
            <ul v-if="work.description?.length" class="rp-list">
              <li v-for="(desc, i) in work.description" :key="i" class="rp-text-sm">{{ desc }}</li>
            </ul>
          </div>
        </div>
      </section>

      <!-- 项目经历 -->
      <section v-if="data.projects.length" class="rp-section">
        <h2 class="rp-section-title">项目经历</h2>
        <div class="rp-section-content">
          <div v-for="proj in data.projects" :key="proj.id" class="rp-entry">
            <div class="rp-entry-header">
              <span class="rp-entry-title">{{ proj.name }}</span>
              <span class="rp-entry-role">{{ proj.role }}</span>
            </div>
            <div v-if="proj.techStack" class="rp-tech">{{ proj.techStack }}</div>
            <p v-if="proj.description" class="rp-text-sm">{{ proj.description }}</p>
            <p v-if="proj.achievements" class="rp-text-sm rp-achievement">成果：{{ proj.achievements }}</p>
          </div>
        </div>
      </section>

      <!-- 技能与奖项 -->
      <div class="rp-two-col">
        <section v-if="data.skills.length" class="rp-section">
          <h2 class="rp-section-title">专业技能</h2>
          <div class="rp-section-content">
            <div class="rp-skill-list">
              <span v-for="skill in data.skills" :key="skill.id" class="rp-skill-item">{{ skill.name }}</span>
            </div>
          </div>
        </section>

        <section v-if="data.awards.length" class="rp-section">
          <h2 class="rp-section-title">荣誉奖项</h2>
          <div class="rp-section-content">
            <div v-for="award in data.awards" :key="award.id" class="rp-award">
              <span class="rp-award-name">{{ award.name }}</span>
              <span class="rp-award-date">{{ award.date }}</span>
            </div>
          </div>
        </section>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  data: { type: Object, required: true },
  color: { type: String, default: '#1a365d' },
})
</script>

<style scoped>
.resume-professional {
  font-family: 'PingFang SC', 'Microsoft YaHei', 'Helvetica Neue', sans-serif;
  font-size: 14px;
  color: #2d2d2d;
  line-height: 1.6;
  background: #fff;
  width: 794px;
  min-height: 1123px;
}

/* 头部 */
.rp-header {
  background: #1a365d;
  color: #fff;
  padding: 28px 40px 0;
  position: relative;
}

.rp-header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 20px;
  gap: 20px;
}

.rp-avatar {
  width: 85px;
  height: 119px;
  border-radius: 6px;
  overflow: hidden;
  border: 2px solid rgba(255, 255, 255, 0.3);
  flex-shrink: 0;
}

.rp-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.rp-name {
  font-size: 28px;
  font-weight: 800;
  color: #fff;
  letter-spacing: 2px;
}

.rp-intention {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.7);
  margin-top: 4px;
  letter-spacing: 1px;
}

.rp-header-right {
  text-align: right;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.8);
}

.rp-contact-line {
  margin: 2px 0;
}

.rp-header-accent {
  height: 4px;
  background: var(--theme);
}

/* 主体 */
.rp-body {
  padding: 24px 40px;
}

/* 区块 */
.rp-section {
  margin-bottom: 20px;
}

.rp-section-title {
  font-size: 14px;
  font-weight: 700;
  color: #1a365d;
  text-transform: uppercase;
  letter-spacing: 2px;
  border-bottom: 2px solid #e2e8f0;
  padding-bottom: 6px;
  margin-bottom: 12px;
}

.rp-section-content {
  padding-left: 2px;
}

/* 条目 */
.rp-entry {
  margin-bottom: 14px;
}

.rp-entry-header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
}

.rp-entry-title {
  font-size: 14px;
  font-weight: 700;
  color: #1a1a2e;
}

.rp-entry-date {
  font-size: 12px;
  color: #718096;
  font-style: italic;
}

.rp-entry-meta {
  font-size: 13px;
  color: #4a5568;
  margin: 1px 0 3px;
}

.rp-entry-role {
  font-size: 12px;
  color: var(--theme);
  font-weight: 600;
}

.rp-tech {
  font-size: 12px;
  color: var(--theme);
  font-style: italic;
  margin: 2px 0;
}

.rp-courses {
  color: #718096;
  font-style: italic;
}

/* 文本 */
.rp-text {
  font-size: 13px;
  color: #4a5568;
  line-height: 1.7;
}

.rp-text-sm {
  font-size: 12px;
  color: #4a5568;
  margin: 2px 0;
  line-height: 1.6;
}

.rp-achievement {
  color: var(--theme);
  font-weight: 500;
}

/* 列表 */
.rp-list {
  list-style: none;
  padding-left: 0;
  margin: 4px 0;
}

.rp-list li {
  position: relative;
  padding-left: 16px;
  margin: 3px 0;
}

.rp-list li::before {
  content: '▸';
  position: absolute;
  left: 0;
  color: var(--theme);
  font-size: 11px;
}

/* 双栏 */
.rp-two-col {
  display: flex;
  gap: 30px;
}

.rp-two-col .rp-section {
  flex: 1;
}

/* 技能列表 */
.rp-skill-list {
  display: block;
}

.rp-skill-item {
  display: block;
  font-size: 13px;
  font-weight: 500;
  color: #2d2d2d;
  padding: 2px 0;
  line-height: 1.8;
}

/* 奖项 */
.rp-award {
  display: flex;
  justify-content: space-between;
  padding: 5px 0;
  border-bottom: 1px dashed #e2e8f0;
}

.rp-award-name {
  font-size: 13px;
  color: #2d2d2d;
  font-weight: 500;
}

.rp-award-date {
  font-size: 12px;
  color: #718096;
}
</style>
