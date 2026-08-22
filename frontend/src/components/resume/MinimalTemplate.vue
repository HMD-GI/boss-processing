<template>
  <div class="resume-minimal" :style="{ '--theme': color }">
    <!-- 极简头部 -->
    <header class="mn-header">
      <div class="mn-header-left">
        <h1 class="mn-name">{{ data.personal.name || '姓名' }}</h1>
        <p class="mn-intention">{{ data.personal.jobIntention || '求职意向' }}</p>
        <div class="mn-contact">
          <span v-if="data.personal.phone">{{ data.personal.phone }}</span>
          <span v-if="data.personal.phone && data.personal.email" class="mn-sep">|</span>
          <span v-if="data.personal.email">{{ data.personal.email }}</span>
          <span v-if="data.personal.github" class="mn-sep">|</span>
          <span v-if="data.personal.github">{{ data.personal.github }}</span>
          <span v-if="data.personal.blog" class="mn-sep">|</span>
          <span v-if="data.personal.blog">{{ data.personal.blog }}</span>
        </div>
      </div>
      <div class="mn-avatar" v-if="data.personal.avatar">
        <img :src="data.personal.avatar" alt="photo" />
      </div>
    </header>

    <div class="mn-body">
      <!-- 自我评价 -->
      <section v-if="data.personal.selfEvaluation" class="mn-section">
        <h2 class="mn-section-title">关于我</h2>
        <p class="mn-text">{{ data.personal.selfEvaluation }}</p>
      </section>

      <!-- 教育经历 -->
      <section v-if="data.education.length" class="mn-section">
        <h2 class="mn-section-title">教育经历</h2>
        <div v-for="edu in data.education" :key="edu.id" class="mn-entry">
          <div class="mn-entry-header">
            <span class="mn-entry-school">{{ edu.school }} <span class="mn-entry-degree">{{ edu.degree }}</span></span>
            <span class="mn-entry-date">{{ edu.startDate }} — {{ edu.endDate }}</span>
          </div>
          <p class="mn-entry-detail">{{ edu.major }}<span v-if="edu.gpa"> · GPA {{ edu.gpa }}</span></p>
          <p v-if="edu.courses" class="mn-text-sm">{{ edu.courses }}</p>
        </div>
      </section>

      <!-- 工作经历 -->
      <section v-if="data.workExperience.length" class="mn-section">
        <h2 class="mn-section-title">工作经历</h2>
        <div v-for="work in data.workExperience" :key="work.id" class="mn-entry">
          <div class="mn-entry-header">
            <span class="mn-entry-school">{{ work.company }} <span class="mn-entry-degree">{{ work.position }}</span></span>
            <span class="mn-entry-date">{{ work.startDate }} — {{ work.endDate }}</span>
          </div>
          <p v-if="work.department" class="mn-entry-detail">{{ work.department }}</p>
          <ul v-if="work.description?.length" class="mn-list">
            <li v-for="(desc, i) in work.description" :key="i" class="mn-text-sm">{{ desc }}</li>
          </ul>
        </div>
      </section>

      <!-- 项目经历 -->
      <section v-if="data.projects.length" class="mn-section">
        <h2 class="mn-section-title">项目经历</h2>
        <div v-for="proj in data.projects" :key="proj.id" class="mn-entry">
          <div class="mn-entry-header">
            <span class="mn-entry-school">{{ proj.name }} <span class="mn-entry-degree">{{ proj.role }}</span></span>
          </div>
          <p v-if="proj.techStack" class="mn-tech">{{ proj.techStack }}</p>
          <p v-if="proj.description" class="mn-text-sm">{{ proj.description }}</p>
          <p v-if="proj.achievements" class="mn-text-sm mn-highlight">{{ proj.achievements }}</p>
        </div>
      </section>

      <!-- 技能 -->
      <section v-if="data.skills.length" class="mn-section">
        <h2 class="mn-section-title">专业技能</h2>
        <div class="mn-skills">
          <span v-for="skill in data.skills" :key="skill.id" class="mn-skill-item">{{ skill.name }}</span>
        </div>
      </section>

      <!-- 奖项 -->
      <section v-if="data.awards.length" class="mn-section">
        <h2 class="mn-section-title">荣誉奖项</h2>
        <div v-for="award in data.awards" :key="award.id" class="mn-entry">
          <div class="mn-entry-header">
            <span class="mn-entry-school">{{ award.name }}</span>
            <span class="mn-entry-date">{{ award.date }}</span>
          </div>
          <p class="mn-entry-detail">{{ award.organization }}<span v-if="award.level"> · {{ award.level }}</span></p>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
defineProps({
  data: { type: Object, required: true },
  color: { type: String, default: '#2c3e50' },
})
</script>

<style scoped>
.resume-minimal {
  font-family: 'Helvetica Neue', 'PingFang SC', 'Microsoft YaHei', sans-serif;
  font-size: 14px;
  color: #2c3e50;
  line-height: 1.6;
  background: #fff;
  width: 794px;
  min-height: 1123px;
}

/* 头部 */
.mn-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 50px 50px 30px;
  border-bottom: 1px solid #eee;
}

.mn-header-left {
  flex: 1;
}

.mn-name {
  font-size: 32px;
  font-weight: 300;
  color: #1a1a2e;
  letter-spacing: 2px;
  margin-bottom: 6px;
}

.mn-intention {
  font-size: 15px;
  color: var(--theme);
  margin-bottom: 10px;
  font-weight: 400;
}

.mn-contact {
  font-size: 12px;
  color: #999;
}

.mn-sep {
  margin: 0 6px;
  color: #ddd;
}

.mn-avatar {
  width: 85px;
  height: 119px;
  border-radius: 4px;
  overflow: hidden;
  flex-shrink: 0;
}

.mn-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* 主体 */
.mn-body {
  padding: 30px 50px 40px;
}

/* 区块 */
.mn-section {
  margin-bottom: 28px;
}

.mn-section-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--theme);
  text-transform: uppercase;
  letter-spacing: 3px;
  margin-bottom: 16px;
  padding-bottom: 6px;
  border-bottom: 1px solid #f0f0f0;
}

/* 条目 */
.mn-entry {
  margin-bottom: 16px;
}

.mn-entry-header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
}

.mn-entry-school {
  font-size: 14px;
  font-weight: 600;
  color: #1a1a2e;
}

.mn-entry-degree {
  font-weight: 400;
  color: #666;
  font-size: 13px;
  margin-left: 4px;
}

.mn-entry-date {
  font-size: 12px;
  color: #aaa;
}

.mn-entry-detail {
  font-size: 13px;
  color: #888;
  margin: 2px 0;
}

.mn-tech {
  font-size: 12px;
  color: var(--theme);
  margin: 3px 0;
}

/* 文本 */
.mn-text {
  font-size: 13px;
  color: #555;
  line-height: 1.8;
}

.mn-text-sm {
  font-size: 12px;
  color: #777;
  margin: 2px 0;
  line-height: 1.7;
}

.mn-highlight {
  color: var(--theme);
  font-weight: 500;
}

/* 列表 */
.mn-list {
  list-style: none;
  padding-left: 0;
  margin: 4px 0;
}

.mn-list li {
  position: relative;
  padding-left: 14px;
  margin: 3px 0;
}

.mn-list li::before {
  content: '—';
  position: absolute;
  left: 0;
  color: var(--theme);
}

/* 技能 */
.mn-skills {
  display: block;
}

.mn-skill-item {
  display: block;
  font-size: 13px;
  color: #555;
  padding: 2px 0;
  line-height: 1.8;
}
</style>
