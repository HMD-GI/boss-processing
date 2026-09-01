<template>
  <div class="resume-elegant" :style="{ '--theme': color }">
    <!-- 顶部 -->
    <header class="re-header">
      <div class="re-avatar" v-if="data.personal.avatar">
        <img :src="data.personal.avatar" alt="photo" />
      </div>
      <h1 class="re-name">{{ data.personal.name || '姓名' }}</h1>
      <div class="re-divider"></div>
      <p class="re-intention">{{ data.personal.jobIntention || '求职意向' }}</p>
      <div class="re-contact">
        <span v-if="data.personal.phone">{{ data.personal.phone }}</span>
        <span v-if="data.personal.phone && data.personal.email" class="re-dot">·</span>
        <span v-if="data.personal.email">{{ data.personal.email }}</span>
        <span v-if="data.personal.wechat" class="re-dot">·</span>
        <span v-if="data.personal.wechat">{{ data.personal.wechat }}</span>
        <span v-if="data.personal.github" class="re-dot">·</span>
        <span v-if="data.personal.github">{{ data.personal.github }}</span>
        <span v-if="data.personal.blog" class="re-dot">·</span>
        <span v-if="data.personal.blog">{{ data.personal.blog }}</span>
      </div>
    </header>

    <div class="re-body">
      <!-- 自我评价 -->
      <section v-if="data.personal.selfEvaluation" class="re-section">
        <h2 class="re-section-title">自<span class="re-title-gap"></span>我<span class="re-title-gap"></span>评<span class="re-title-gap"></span>价</h2>
        <p class="re-text">{{ data.personal.selfEvaluation }}</p>
      </section>

      <!-- 教育经历 -->
      <section v-if="data.education.length" class="re-section">
        <h2 class="re-section-title">教<span class="re-title-gap"></span>育<span class="re-title-gap"></span>经<span class="re-title-gap"></span>历</h2>
        <div v-for="edu in data.education" :key="edu.id" class="re-entry">
          <div class="re-entry-row">
            <span class="re-entry-school">{{ edu.school }}</span>
            <span class="re-entry-date">{{ edu.startDate }} — {{ edu.endDate }}</span>
          </div>
          <p class="re-entry-detail">{{ edu.major }} · {{ edu.degree }}<span v-if="edu.gpa"> · GPA {{ edu.gpa }}</span><span v-if="edu.rank"> · 排名 {{ edu.rank }}</span></p>
          <p v-if="edu.courses" class="re-text-sm">主修课程：{{ edu.courses }}</p>
        </div>
      </section>

      <!-- 工作经历 -->
      <section v-if="data.workExperience.length" class="re-section">
        <h2 class="re-section-title">工<span class="re-title-gap"></span>作<span class="re-title-gap"></span>经<span class="re-title-gap"></span>历</h2>
        <div v-for="work in data.workExperience" :key="work.id" class="re-entry">
          <div class="re-entry-row">
            <span class="re-entry-school">{{ work.company }}</span>
            <span class="re-entry-date">{{ work.startDate }} — {{ work.endDate }}</span>
          </div>
          <p class="re-entry-detail">{{ work.position }}<span v-if="work.department"> · {{ work.department }}</span></p>
          <ul v-if="work.description?.length" class="re-list">
            <li v-for="(desc, i) in work.description" :key="i" class="re-text-sm">{{ desc }}</li>
          </ul>
        </div>
      </section>

      <!-- 项目经历 -->
      <section v-if="data.projects.length" class="re-section">
        <h2 class="re-section-title">项<span class="re-title-gap"></span>目<span class="re-title-gap"></span>经<span class="re-title-gap"></span>历</h2>
        <div v-for="proj in data.projects" :key="proj.id" class="re-entry">
          <div class="re-entry-row">
            <span class="re-entry-school">{{ proj.name }}</span>
            <span class="re-entry-role">{{ proj.role }}</span>
          </div>
          <p v-if="proj.techStack" class="re-tech-line">技术栈：{{ proj.techStack }}</p>
          <p v-if="proj.description" class="re-text-sm">{{ proj.description }}</p>
          <p v-if="proj.achievements" class="re-text-sm re-highlight">成果：{{ proj.achievements }}</p>
        </div>
      </section>

      <!-- 技能 -->
      <section v-if="data.skills.length" class="re-section">
        <h2 class="re-section-title">专<span class="re-title-gap"></span>业<span class="re-title-gap"></span>技<span class="re-title-gap"></span>能</h2>
        <div class="re-skills">
          <span v-for="skill in data.skills" :key="skill.id" class="re-skill-item">
            {{ skill.name }}
          </span>
        </div>
      </section>

      <!-- 奖项 -->
      <section v-if="data.awards.length" class="re-section">
        <h2 class="re-section-title">荣<span class="re-title-gap"></span>誉<span class="re-title-gap"></span>奖<span class="re-title-gap"></span>项</h2>
        <div v-for="award in data.awards" :key="award.id" class="re-entry">
          <div class="re-entry-row">
            <span class="re-entry-school">{{ award.name }}</span>
            <span class="re-entry-date">{{ award.date }}</span>
          </div>
          <p class="re-entry-detail">{{ award.organization }}<span v-if="award.level"> · {{ award.level }}</span></p>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
defineProps({
  data: { type: Object, required: true },
  color: { type: String, default: '#5b8c5a' },
  editMode: { type: Boolean, default: false },
})
</script>

<style scoped>
.resume-elegant {
  font-family: 'Songti SC', 'SimSun', 'PingFang SC', serif;
  font-size: 14px;
  color: #2c2c2c;
  line-height: 1.8;
  background: #fff;
  width: 794px;
  min-height: 1123px;
}

/* 头部 */
.re-header {
  text-align: center;
  padding: 40px 40px 24px;
  position: relative;
}

.re-avatar {
  position: absolute;
  right: 40px;
  top: 40px;
  width: 85px;
  height: 119px;
  border-radius: 6px;
  overflow: hidden;
  border: 2px solid var(--theme);
}

.re-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.re-name {
  font-size: 30px;
  font-weight: 700;
  color: #1a1a1a;
  letter-spacing: 4px;
  font-family: 'Songti SC', 'SimSun', serif;
}

.re-divider {
  width: 60px;
  height: 2px;
  background: var(--theme);
  margin: 12px auto;
}

.re-intention {
  font-size: 15px;
  color: var(--theme);
  letter-spacing: 2px;
  margin-bottom: 8px;
}

.re-contact {
  font-size: 12px;
  color: #888;
  letter-spacing: 0.5px;
}

.re-dot {
  margin: 0 6px;
  color: #ccc;
}

/* 主体 */
.re-body {
  padding: 0 48px 40px;
}

/* 区块 */
.re-section {
  margin-bottom: 22px;
}

.re-section-title {
  font-size: 15px;
  font-weight: 700;
  color: var(--theme);
  text-align: center;
  border-bottom: 1px solid #e8e8e8;
  padding-bottom: 8px;
  margin-bottom: 14px;
  letter-spacing: 2px;
}

.re-title-gap {
  display: inline-block;
  width: 3px;
}

/* 条目 */
.re-entry {
  margin-bottom: 14px;
}

.re-entry-row {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
}

.re-entry-school {
  font-size: 14px;
  font-weight: 700;
  color: #1a1a1a;
}

.re-entry-date {
  font-size: 12px;
  color: #999;
}

.re-entry-detail {
  font-size: 13px;
  color: #555;
  margin: 2px 0;
}

.re-entry-role {
  font-size: 12px;
  color: var(--theme);
}

.re-tech-line {
  font-size: 12px;
  color: #888;
  font-style: italic;
  margin: 2px 0;
}

/* 文本 */
.re-text {
  font-size: 13px;
  color: #444;
  line-height: 1.8;
  text-indent: 2em;
}

.re-text-sm {
  font-size: 12px;
  color: #666;
  margin: 2px 0;
  line-height: 1.7;
}

.re-highlight {
  color: var(--theme);
}

/* 列表 */
.re-list {
  list-style: none;
  padding-left: 0;
  margin: 4px 0;
}

.re-list li {
  position: relative;
  padding-left: 16px;
  margin: 4px 0;
}

.re-list li::before {
  content: '—';
  position: absolute;
  left: 0;
  color: var(--theme);
}

/* 技能 */
.re-skills {
  display: block;
}

.re-skill-item {
  display: block;
  font-size: 13px;
  color: #333;
  line-height: 1.8;
  padding: 1px 0;
}

.re-skill-sep {
  color: #ccc;
  margin: 0 2px;
}

.re-skill-level {
  color: var(--theme);
  font-size: 12px;
}
</style>
