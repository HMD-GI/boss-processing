<template>
  <div class="resume-creative" :style="{ '--theme': color }">
    <!-- 几何装饰头 -->
    <header class="rc-header">
      <div class="rc-shape-1"></div>
      <div class="rc-shape-2"></div>
      <div class="rc-header-content">
        <div class="rc-avatar-area">
          <div class="rc-avatar" v-if="data.personal.avatar">
            <img :src="data.personal.avatar" alt="avatar" />
          </div>
          <div class="rc-avatar rc-avatar-placeholder" v-else>
            {{ (data.personal.name || '?')[0] }}
          </div>
        </div>
        <div class="rc-header-info">
          <h1 class="rc-name">{{ data.personal.name || '姓名' }}</h1>
          <p class="rc-intention">{{ data.personal.jobIntention || '求职意向' }}</p>
          <div class="rc-contact-tags">
            <span v-if="data.personal.phone" class="rc-tag">{{ data.personal.phone }}</span>
            <span v-if="data.personal.email" class="rc-tag">{{ data.personal.email }}</span>
            <span v-if="data.personal.github" class="rc-tag">{{ data.personal.github }}</span>
            <span v-if="data.personal.blog" class="rc-tag">{{ data.personal.blog }}</span>
          </div>
        </div>
      </div>
    </header>

    <div class="rc-body">
      <!-- 自我评价 -->
      <section v-if="data.personal.selfEvaluation" class="rc-section">
        <div class="rc-section-title-wrap">
          <span class="rc-section-icon">01</span>
          <h2 class="rc-section-title">关于我</h2>
        </div>
        <p class="rc-text">{{ data.personal.selfEvaluation }}</p>
      </section>

      <!-- 教育经历 -->
      <section v-if="data.education.length" class="rc-section">
        <div class="rc-section-title-wrap">
          <span class="rc-section-icon">02</span>
          <h2 class="rc-section-title">教育经历</h2>
        </div>
        <div v-for="edu in data.education" :key="edu.id" class="rc-card">
          <div class="rc-card-head">
            <span class="rc-card-title">{{ edu.school }}</span>
            <span class="rc-card-badge">{{ edu.startDate }} - {{ edu.endDate }}</span>
          </div>
          <p class="rc-card-sub">{{ edu.major }} · {{ edu.degree }}</p>
          <div class="rc-card-tags">
            <span v-if="edu.gpa" class="rc-mini-tag">GPA {{ edu.gpa }}</span>
            <span v-if="edu.rank" class="rc-mini-tag">排名 {{ edu.rank }}</span>
          </div>
          <p v-if="edu.courses" class="rc-text-sm">{{ edu.courses }}</p>
        </div>
      </section>

      <!-- 工作经历 -->
      <section v-if="data.workExperience.length" class="rc-section">
        <div class="rc-section-title-wrap">
          <span class="rc-section-icon">03</span>
          <h2 class="rc-section-title">工作经历</h2>
        </div>
        <div v-for="work in data.workExperience" :key="work.id" class="rc-card">
          <div class="rc-card-head">
            <span class="rc-card-title">{{ work.company }}</span>
            <span class="rc-card-badge">{{ work.startDate }} - {{ work.endDate }}</span>
          </div>
          <p class="rc-card-sub">{{ work.position }}<span v-if="work.department"> · {{ work.department }}</span></p>
          <ul v-if="work.description?.length" class="rc-list">
            <li v-for="(desc, i) in work.description" :key="i" class="rc-text-sm">{{ desc }}</li>
          </ul>
        </div>
      </section>

      <!-- 项目经历 -->
      <section v-if="data.projects.length" class="rc-section">
        <div class="rc-section-title-wrap">
          <span class="rc-section-icon">04</span>
          <h2 class="rc-section-title">项目经历</h2>
        </div>
        <div v-for="proj in data.projects" :key="proj.id" class="rc-card">
          <div class="rc-card-head">
            <span class="rc-card-title">{{ proj.name }}</span>
            <span class="rc-card-badge">{{ proj.role }}</span>
          </div>
          <p v-if="proj.techStack" class="rc-tech-line">{{ proj.techStack }}</p>
          <p v-if="proj.description" class="rc-text-sm">{{ proj.description }}</p>
          <p v-if="proj.achievements" class="rc-text-sm rc-highlight">成果：{{ proj.achievements }}</p>
        </div>
      </section>

      <!-- 技能 + 奖项 -->
      <div class="rc-bottom-grid">
        <section v-if="data.skills.length" class="rc-section">
          <div class="rc-section-title-wrap">
            <span class="rc-section-icon">05</span>
            <h2 class="rc-section-title">技能</h2>
          </div>
          <div class="rc-skills">
            <span v-for="skill in data.skills" :key="skill.id" class="rc-skill-chip">
              {{ skill.name }}
            </span>
          </div>
        </section>

        <section v-if="data.awards.length" class="rc-section">
          <div class="rc-section-title-wrap">
            <span class="rc-section-icon">06</span>
            <h2 class="rc-section-title">奖项</h2>
          </div>
          <div v-for="award in data.awards" :key="award.id" class="rc-award-item">
            <p class="rc-award-name">{{ award.name }}</p>
            <p class="rc-award-meta">{{ award.organization }} · {{ award.date }}</p>
          </div>
        </section>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  data: { type: Object, required: true },
  color: { type: String, default: '#e63946' },
})
</script>

<style scoped>
.resume-creative {
  font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
  font-size: 14px;
  color: #333;
  line-height: 1.6;
  background: #fff;
  width: 794px;
  min-height: 1123px;
  position: relative;
  overflow: hidden;
}

/* 头部 */
.rc-header {
  position: relative;
  padding: 36px 40px 28px;
  overflow: hidden;
  background: #f8f9fa;
}

.rc-shape-1 {
  position: absolute;
  top: -60px;
  right: -40px;
  width: 200px;
  height: 200px;
  background: var(--theme);
  border-radius: 50%;
  opacity: 0.1;
}

.rc-shape-2 {
  position: absolute;
  top: -20px;
  right: 80px;
  width: 120px;
  height: 120px;
  border: 3px solid var(--theme);
  border-radius: 50%;
  opacity: 0.15;
}

.rc-header-content {
  display: flex;
  align-items: center;
  gap: 20px;
  position: relative;
  z-index: 1;
}

.rc-avatar {
  width: 60px;
  height: 84px;
  border-radius: 6px;
  overflow: hidden;
  flex-shrink: 0;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.rc-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.rc-avatar-placeholder {
  background: var(--theme);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 32px;
  font-weight: 700;
}

.rc-header-info {
  flex: 1;
}

.rc-name {
  font-size: 26px;
  font-weight: 800;
  color: #1a1a2e;
}

.rc-intention {
  font-size: 14px;
  color: var(--theme);
  font-weight: 600;
  margin: 2px 0 8px;
}

.rc-contact-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.rc-tag {
  font-size: 11px;
  color: #666;
  background: #fff;
  padding: 2px 8px;
  border-radius: 10px;
  border: 1px solid #e8ecf1;
}

/* 主体 */
.rc-body {
  padding: 24px 40px;
}

/* 区块 */
.rc-section {
  margin-bottom: 20px;
}

.rc-section-title-wrap {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
}

.rc-section-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 8px;
  background: var(--theme);
  color: #fff;
  font-size: 12px;
  font-weight: 800;
  flex-shrink: 0;
}

.rc-section-title {
  font-size: 16px;
  font-weight: 700;
  color: #1a1a2e;
}

/* 卡片 */
.rc-card {
  background: #f8f9fa;
  border-radius: 10px;
  padding: 12px 16px;
  margin-bottom: 10px;
  border-left: 3px solid var(--theme);
}

.rc-card-head {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
}

.rc-card-title {
  font-size: 14px;
  font-weight: 700;
  color: #1a1a2e;
}

.rc-card-badge {
  font-size: 11px;
  color: #fff;
  background: var(--theme);
  padding: 2px 8px;
  border-radius: 10px;
}

.rc-card-sub {
  font-size: 13px;
  color: #555;
  margin: 2px 0;
}

.rc-card-tags {
  display: flex;
  gap: 6px;
  margin: 3px 0;
}

.rc-mini-tag {
  font-size: 11px;
  color: var(--theme);
  background: color-mix(in srgb, var(--theme) 10%, transparent);
  padding: 1px 6px;
  border-radius: 4px;
}

.rc-tech-line {
  font-size: 12px;
  color: var(--theme);
  font-weight: 500;
  margin: 2px 0;
}

/* 文本 */
.rc-text {
  font-size: 13px;
  color: #555;
  line-height: 1.7;
}

.rc-text-sm {
  font-size: 12px;
  color: #666;
  margin: 2px 0;
  line-height: 1.6;
}

.rc-highlight {
  color: var(--theme);
  font-weight: 500;
}

/* 列表 */
.rc-list {
  list-style: none;
  padding-left: 0;
  margin: 4px 0;
}

.rc-list li {
  position: relative;
  padding-left: 14px;
  margin: 3px 0;
}

.rc-list li::before {
  content: '●';
  position: absolute;
  left: 0;
  color: var(--theme);
  font-size: 8px;
  top: 5px;
}

/* 底部双栏 */
.rc-bottom-grid {
  display: flex;
  gap: 24px;
}

.rc-bottom-grid .rc-section {
  flex: 1;
}

/* 技能 */
.rc-skills {
  display: block;
}

.rc-skill-chip {
  display: block;
  padding: 3px 0;
  font-size: 13px;
  font-weight: 500;
  color: #333;
  line-height: 1.8;
}

.rc-skill-level {
  font-size: 10px;
  color: var(--theme);
}

/* 奖项 */
.rc-award-item {
  padding: 6px 0;
  border-bottom: 1px dashed #e8ecf1;
}

.rc-award-name {
  font-size: 13px;
  color: #333;
  font-weight: 500;
}

.rc-award-meta {
  font-size: 11px;
  color: #999;
}
</style>
