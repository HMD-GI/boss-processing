<template>
  <div class="resume-classic" :style="{ '--theme': color }">
    <!-- 顶部标题横幅 -->
    <header class="cl-header">
      <div class="cl-header-bar" style="background: var(--theme);"></div>
      <div class="cl-header-content">
        <div class="cl-title-block">
          <h1 class="cl-title">个人简历</h1>
          <p class="cl-subtitle">{{ data.personal.name || '姓名' }} · {{ data.personal.jobIntention || '求职意向' }}</p>
        </div>
        <div class="cl-avatar" v-if="data.personal.avatar">
          <img :src="data.personal.avatar" alt="photo" />
        </div>
      </div>
    </header>

    <div class="cl-body">
      <!-- 基本信息 -->
      <section class="cl-section">
        <div class="cl-section-title">
          <span class="cl-section-tag" style="background: var(--theme);">基本信息</span>
          <div class="cl-section-line" style="border-color: var(--theme);"></div>
        </div>
        <div class="cl-info-grid">
          <div v-if="data.personal.phone" class="cl-info-item"><span class="cl-info-label">电话</span><span>{{ data.personal.phone }}</span></div>
          <div v-if="data.personal.email" class="cl-info-item"><span class="cl-info-label">邮箱</span><span>{{ data.personal.email }}</span></div>
          <div v-if="data.personal.github" class="cl-info-item"><span class="cl-info-label">GitHub</span><span>{{ data.personal.github }}</span></div>
          <div v-if="data.personal.blog" class="cl-info-item"><span class="cl-info-label">博客</span><span>{{ data.personal.blog }}</span></div>
        </div>
      </section>

      <!-- 自我评价 -->
      <section v-if="data.personal.selfEvaluation" class="cl-section">
        <div class="cl-section-title">
          <span class="cl-section-tag" style="background: var(--theme);">自我评价</span>
          <div class="cl-section-line" style="border-color: var(--theme);"></div>
        </div>
        <p class="cl-text">{{ data.personal.selfEvaluation }}</p>
      </section>

      <!-- 教育经历 -->
      <section v-if="data.education.length" class="cl-section">
        <div class="cl-section-title">
          <span class="cl-section-tag" style="background: var(--theme);">教育背景</span>
          <div class="cl-section-line" style="border-color: var(--theme);"></div>
        </div>
        <div v-for="edu in data.education" :key="edu.id" class="cl-entry">
          <div class="cl-entry-header">
            <span class="cl-entry-title">{{ edu.school }}</span>
            <span class="cl-entry-date">{{ edu.startDate }} — {{ edu.endDate }}</span>
          </div>
          <p class="cl-entry-sub">{{ edu.major }} · {{ edu.degree }}<span v-if="edu.gpa"> · GPA: {{ edu.gpa }}</span><span v-if="edu.rank"> · 排名: {{ edu.rank }}</span></p>
          <p v-if="edu.courses" class="cl-text-sm">主修课程：{{ edu.courses }}</p>
        </div>
      </section>

      <!-- 工作经历 -->
      <section v-if="data.workExperience.length" class="cl-section">
        <div class="cl-section-title">
          <span class="cl-section-tag" style="background: var(--theme);">工作经历</span>
          <div class="cl-section-line" style="border-color: var(--theme);"></div>
        </div>
        <div v-for="work in data.workExperience" :key="work.id" class="cl-entry">
          <div class="cl-entry-header">
            <span class="cl-entry-title">{{ work.company }}</span>
            <span class="cl-entry-date">{{ work.startDate }} — {{ work.endDate }}</span>
          </div>
          <p class="cl-entry-sub">{{ work.position }}<span v-if="work.department"> · {{ work.department }}</span></p>
          <ul v-if="work.description?.length" class="cl-list">
            <li v-for="(desc, i) in work.description" :key="i" class="cl-text-sm">{{ desc }}</li>
          </ul>
        </div>
      </section>

      <!-- 项目经历 -->
      <section v-if="data.projects.length" class="cl-section">
        <div class="cl-section-title">
          <span class="cl-section-tag" style="background: var(--theme);">项目经历</span>
          <div class="cl-section-line" style="border-color: var(--theme);"></div>
        </div>
        <div v-for="proj in data.projects" :key="proj.id" class="cl-entry">
          <div class="cl-entry-header">
            <span class="cl-entry-title">{{ proj.name }}</span>
            <span class="cl-entry-role" style="color: var(--theme);">{{ proj.role }}</span>
          </div>
          <p v-if="proj.techStack" class="cl-text-sm" style="color: var(--theme);">技术栈：{{ proj.techStack }}</p>
          <p v-if="proj.description" class="cl-text-sm">{{ proj.description }}</p>
          <p v-if="proj.achievements" class="cl-text-sm cl-highlight">成果：{{ proj.achievements }}</p>
        </div>
      </section>

      <!-- 技能 + 奖项 -->
      <div class="cl-two-col">
        <section v-if="data.skills.length" class="cl-section">
          <div class="cl-section-title">
            <span class="cl-section-tag" style="background: var(--theme);">专业技能</span>
            <div class="cl-section-line" style="border-color: var(--theme);"></div>
          </div>
          <div class="cl-skills">
            <span v-for="skill in data.skills" :key="skill.id" class="cl-skill-item">{{ skill.name }}</span>
          </div>
        </section>

        <section v-if="data.awards.length" class="cl-section">
          <div class="cl-section-title">
            <span class="cl-section-tag" style="background: var(--theme);">荣誉奖项</span>
            <div class="cl-section-line" style="border-color: var(--theme);"></div>
          </div>
          <div v-for="award in data.awards" :key="award.id" class="cl-award">
            <span class="cl-award-name">{{ award.name }}</span>
            <span class="cl-award-date">{{ award.date }}</span>
          </div>
        </section>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  data: { type: Object, required: true },
  color: { type: String, default: '#4e7282' },
})
</script>

<style scoped>
.resume-classic {
  font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
  font-size: 14px;
  color: #333;
  line-height: 1.6;
  background: #fff;
  width: 794px;
  min-height: 1123px;
}

/* 头部横幅 */
.cl-header {
  position: relative;
  margin-bottom: 0;
}

.cl-header-bar {
  height: 6px;
}

.cl-header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px 40px 20px;
}

.cl-title {
  font-size: 26px;
  font-weight: 800;
  color: #1a1a2e;
  letter-spacing: 3px;
}

.cl-subtitle {
  font-size: 14px;
  color: var(--theme);
  margin-top: 4px;
}

.cl-avatar {
  width: 85px;
  height: 119px;
  border-radius: 6px;
  overflow: hidden;
  border: 2px solid var(--theme);
  flex-shrink: 0;
}

.cl-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* 主体 */
.cl-body {
  padding: 0 40px 30px;
}

/* 区块 */
.cl-section {
  margin-bottom: 20px;
}

.cl-section-title {
  display: flex;
  align-items: center;
  gap: 0;
  margin-bottom: 14px;
}

.cl-section-tag {
  display: inline-block;
  color: #fff;
  font-size: 13px;
  font-weight: 600;
  padding: 3px 14px;
  border-radius: 0 3px 3px 0;
  letter-spacing: 1px;
}

.cl-section-line {
  flex: 1;
  border-top: 2px dashed #ddd;
  margin-left: 4px;
}

/* 基本信息网格 */
.cl-info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 6px 30px;
  padding: 4px 0;
}

.cl-info-item {
  font-size: 13px;
  color: #555;
}

.cl-info-label {
  display: inline-block;
  width: 50px;
  color: #888;
  font-weight: 500;
}

/* 条目 */
.cl-entry {
  margin-bottom: 14px;
}

.cl-entry-header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
}

.cl-entry-title {
  font-size: 14px;
  font-weight: 700;
  color: #1a1a2e;
}

.cl-entry-date {
  font-size: 12px;
  color: #999;
}

.cl-entry-sub {
  font-size: 13px;
  color: #555;
  margin: 2px 0;
}

.cl-entry-role {
  font-size: 12px;
  font-weight: 600;
}

/* 文本 */
.cl-text {
  font-size: 13px;
  color: #555;
  line-height: 1.8;
}

.cl-text-sm {
  font-size: 12px;
  color: #666;
  margin: 2px 0;
  line-height: 1.7;
}

.cl-highlight {
  color: var(--theme);
  font-weight: 500;
}

/* 列表 */
.cl-list {
  list-style: none;
  padding-left: 0;
  margin: 4px 0;
}

.cl-list li {
  position: relative;
  padding-left: 16px;
  margin: 3px 0;
}

.cl-list li::before {
  content: '▸';
  position: absolute;
  left: 0;
  color: var(--theme);
  font-size: 11px;
}

/* 双栏 */
.cl-two-col {
  display: flex;
  gap: 30px;
}

.cl-two-col .cl-section {
  flex: 1;
}

/* 技能 */
.cl-skills {
  display: block;
}

.cl-skill-item {
  display: block;
  font-size: 13px;
  color: #333;
  padding: 2px 0;
  line-height: 1.8;
}

/* 奖项 */
.cl-award {
  display: flex;
  justify-content: space-between;
  padding: 4px 0;
  border-bottom: 1px dashed #eee;
}

.cl-award-name {
  font-size: 13px;
  color: #333;
  font-weight: 500;
}

.cl-award-date {
  font-size: 12px;
  color: #999;
}
</style>
