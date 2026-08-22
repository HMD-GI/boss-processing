<template>
  <div class="resume-modern" :style="{ '--theme': color }">
    <!-- 头部 -->
    <header class="rm-header">
      <div class="rm-avatar" v-if="data.personal.avatar">
        <img :src="data.personal.avatar" alt="photo" />
      </div>
      <div class="rm-header-left">
        <h1 class="rm-name">{{ data.personal.name || '姓名' }}</h1>
        <p class="rm-intention">{{ data.personal.jobIntention || '求职意向' }}</p>
      </div>
      <div class="rm-contact">
        <div v-if="data.personal.phone" class="rm-contact-item">
          <span class="rm-ci-icon">手机</span>{{ data.personal.phone }}
        </div>
        <div v-if="data.personal.email" class="rm-contact-item">
          <span class="rm-ci-icon">邮箱</span>{{ data.personal.email }}
        </div>
        <div v-if="data.personal.github" class="rm-contact-item">
          <span class="rm-ci-icon">GitHub</span>{{ data.personal.github }}
        </div>
        <div v-if="data.personal.blog" class="rm-contact-item">
          <span class="rm-ci-icon">博客</span>{{ data.personal.blog }}
        </div>
      </div>
    </header>

    <div class="rm-body">
      <!-- 自我评价 -->
      <section v-if="data.personal.selfEvaluation" class="rm-section">
        <div class="rm-section-header">
          <span class="rm-section-bar"></span>
          <h2 class="rm-section-title">自我评价</h2>
        </div>
        <p class="rm-text">{{ data.personal.selfEvaluation }}</p>
      </section>

      <!-- 教育经历 -->
      <section v-if="data.education.length" class="rm-section">
        <div class="rm-section-header">
          <span class="rm-section-bar"></span>
          <h2 class="rm-section-title">教育经历</h2>
        </div>
        <div v-for="edu in data.education" :key="edu.id" class="rm-timeline-item">
          <div class="rm-dot"></div>
          <div class="rm-timeline-content">
            <div class="rm-item-header">
              <span class="rm-item-title">{{ edu.school }}</span>
              <span class="rm-item-date">{{ edu.startDate }} - {{ edu.endDate }}</span>
            </div>
            <p class="rm-item-sub">{{ edu.major }} · {{ edu.degree }}</p>
            <div class="rm-item-meta">
              <span v-if="edu.gpa" class="rm-meta-tag">GPA: {{ edu.gpa }}</span>
              <span v-if="edu.rank" class="rm-meta-tag">排名: {{ edu.rank }}</span>
            </div>
            <p v-if="edu.courses" class="rm-text-sm">主修课程：{{ edu.courses }}</p>
          </div>
        </div>
      </section>

      <!-- 工作经历 -->
      <section v-if="data.workExperience.length" class="rm-section">
        <div class="rm-section-header">
          <span class="rm-section-bar"></span>
          <h2 class="rm-section-title">工作经历</h2>
        </div>
        <div v-for="work in data.workExperience" :key="work.id" class="rm-timeline-item">
          <div class="rm-dot"></div>
          <div class="rm-timeline-content">
            <div class="rm-item-header">
              <span class="rm-item-title">{{ work.company }}</span>
              <span class="rm-item-date">{{ work.startDate }} - {{ work.endDate }}</span>
            </div>
            <p class="rm-item-sub">{{ work.position }} <template v-if="work.department">| {{ work.department }}</template></p>
            <ul v-if="work.description?.length" class="rm-list">
              <li v-for="(desc, i) in work.description" :key="i" class="rm-text-sm">{{ desc }}</li>
            </ul>
          </div>
        </div>
      </section>

      <!-- 项目经历 -->
      <section v-if="data.projects.length" class="rm-section">
        <div class="rm-section-header">
          <span class="rm-section-bar"></span>
          <h2 class="rm-section-title">项目经历</h2>
        </div>
        <div v-for="proj in data.projects" :key="proj.id" class="rm-timeline-item">
          <div class="rm-dot"></div>
          <div class="rm-timeline-content">
            <div class="rm-item-header">
              <span class="rm-item-title">{{ proj.name }}</span>
              <span class="rm-item-role">{{ proj.role }}</span>
            </div>
            <p v-if="proj.techStack" class="rm-tech-stack">{{ proj.techStack }}</p>
            <p v-if="proj.description" class="rm-text-sm">{{ proj.description }}</p>
            <p v-if="proj.achievements" class="rm-text-sm rm-highlight">成果：{{ proj.achievements }}</p>
          </div>
        </div>
      </section>

      <!-- 技能 + 奖项 -->
      <div class="rm-two-col">
        <section v-if="data.skills.length" class="rm-section">
          <div class="rm-section-header">
            <span class="rm-section-bar"></span>
            <h2 class="rm-section-title">专业技能</h2>
          </div>
          <div class="rm-skills">
            <span v-for="skill in data.skills" :key="skill.id" class="rm-skill-item">
              <span class="rm-skill-name">{{ skill.name }}</span>
            </span>
          </div>
        </section>

        <section v-if="data.awards.length" class="rm-section">
          <div class="rm-section-header">
            <span class="rm-section-bar"></span>
            <h2 class="rm-section-title">奖项荣誉</h2>
          </div>
          <div v-for="award in data.awards" :key="award.id" class="rm-award-item">
            <span class="rm-award-name">{{ award.name }}</span>
            <span class="rm-award-date">{{ award.date }}</span>
          </div>
        </section>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  data: { type: Object, required: true },
  color: { type: String, default: '#4361ee' },
})
</script>

<style scoped>
.resume-modern {
  font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
  font-size: 14px;
  color: #333;
  line-height: 1.6;
  background: #fff;
  width: 794px;
  min-height: 1123px;
}

/* 头部 */
.rm-header {
  background: linear-gradient(135deg, var(--theme) 0%, color-mix(in srgb, var(--theme) 70%, #000) 100%);
  color: #fff;
  padding: 32px 40px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
}

.rm-avatar {
  width: 85px;
  height: 119px;
  border-radius: 6px;
  overflow: hidden;
  border: 2px solid rgba(255, 255, 255, 0.4);
  flex-shrink: 0;
}

.rm-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.rm-name {
  font-size: 30px;
  font-weight: 800;
  color: #fff;
  margin-bottom: 4px;
}

.rm-intention {
  font-size: 15px;
  color: rgba(255, 255, 255, 0.85);
}

.rm-contact {
  text-align: right;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.9);
}

.rm-contact-item {
  margin: 3px 0;
}

.rm-ci-icon {
  display: inline-block;
  background: rgba(255, 255, 255, 0.2);
  padding: 1px 6px;
  border-radius: 3px;
  margin-right: 6px;
  font-size: 11px;
}

/* 主体 */
.rm-body {
  padding: 24px 40px;
}

/* 区块 */
.rm-section {
  margin-bottom: 20px;
}

.rm-section-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.rm-section-bar {
  width: 4px;
  height: 16px;
  background: var(--theme);
  border-radius: 2px;
}

.rm-section-title {
  font-size: 16px;
  font-weight: 700;
  color: #1a1a2e;
}

/* 时间线 */
.rm-timeline-item {
  display: flex;
  gap: 12px;
  margin-bottom: 14px;
  position: relative;
}

.rm-timeline-item::before {
  content: '';
  position: absolute;
  left: 5px;
  top: 18px;
  bottom: -14px;
  width: 2px;
  background: #e8ecf1;
}

.rm-timeline-item:last-child::before {
  display: none;
}

.rm-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: var(--theme);
  border: 2px solid #fff;
  box-shadow: 0 0 0 2px var(--theme);
  flex-shrink: 0;
  margin-top: 4px;
  z-index: 1;
}

.rm-timeline-content {
  flex: 1;
}

.rm-item-header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
}

.rm-item-title {
  font-size: 14px;
  font-weight: 600;
  color: #1a1a2e;
}

.rm-item-date {
  font-size: 12px;
  color: #999;
}

.rm-item-sub {
  font-size: 13px;
  color: #555;
  margin: 2px 0;
}

.rm-item-role {
  font-size: 12px;
  color: var(--theme);
  font-weight: 500;
}

.rm-item-meta {
  display: flex;
  gap: 10px;
  margin: 3px 0;
}

.rm-meta-tag {
  font-size: 12px;
  color: #666;
  background: #f5f7fa;
  padding: 1px 8px;
  border-radius: 10px;
}

.rm-tech-stack {
  font-size: 12px;
  color: var(--theme);
  background: color-mix(in srgb, var(--theme) 8%, transparent);
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  margin: 3px 0;
}

/* 文本 */
.rm-text {
  font-size: 13px;
  color: #555;
  line-height: 1.7;
}

.rm-text-sm {
  font-size: 12px;
  color: #666;
  margin: 2px 0;
  line-height: 1.6;
}

.rm-highlight {
  color: var(--theme);
  font-weight: 500;
}

/* 列表 */
.rm-list {
  list-style: disc;
  padding-left: 18px;
  margin: 4px 0;
}

/* 双栏 */
.rm-two-col {
  display: flex;
  gap: 30px;
}

.rm-two-col .rm-section {
  flex: 1;
}

/* 技能 */
.rm-skills {
  display: block;
}

.rm-skill-item {
  display: block;
  padding: 2px 0;
  font-size: 13px;
  line-height: 1.8;
}

.rm-skill-name {
  font-weight: 600;
  color: #1a1a2e;
}

.rm-skill-level {
  color: var(--theme);
}

/* 奖项 */
.rm-award-item {
  display: flex;
  justify-content: space-between;
  padding: 4px 0;
  border-bottom: 1px dashed #e8ecf1;
}

.rm-award-name {
  font-size: 13px;
  color: #333;
  font-weight: 500;
}

.rm-award-date {
  font-size: 12px;
  color: #999;
}
</style>
