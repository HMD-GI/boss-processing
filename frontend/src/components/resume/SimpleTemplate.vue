<template>
  <div class="resume-simple" :style="{ '--theme': color }">
    <!-- 头部 -->
    <header class="rs-header">
      <div class="rs-avatar" v-if="data.personal.avatar">
        <img :src="data.personal.avatar" alt="photo" />
      </div>
      <h1 class="rs-name">{{ data.personal.name || '姓名' }}</h1>
      <p class="rs-intention">{{ data.personal.jobIntention || '求职意向' }}</p>
      <div class="rs-contact">
        <span v-if="data.personal.phone">{{ data.personal.phone }}</span>
        <span v-if="data.personal.email">| {{ data.personal.email }}</span>
        <span v-if="data.personal.wechat">| {{ data.personal.wechat }}</span>
        <span v-if="data.personal.github">| {{ data.personal.github }}</span>
        <span v-if="data.personal.blog">| {{ data.personal.blog }}</span>
      </div>
    </header>

    <!-- 自我评价 -->
    <section v-if="data.personal.selfEvaluation" class="rs-section">
      <h2 class="rs-section-title">自我评价</h2>
      <p class="rs-text">{{ data.personal.selfEvaluation }}</p>
    </section>

    <!-- 教育经历 -->
    <section v-if="data.education.length" class="rs-section">
      <h2 class="rs-section-title">教育经历</h2>
      <div v-for="edu in data.education" :key="edu.id" class="rs-item">
        <div class="rs-item-header">
          <span class="rs-item-title">{{ edu.school }}</span>
          <span class="rs-item-date">{{ edu.startDate }} - {{ edu.endDate }}</span>
        </div>
        <p class="rs-item-sub">{{ edu.major }} · {{ edu.degree }} <template v-if="edu.gpa">| GPA: {{ edu.gpa }}</template><template v-if="edu.rank">| 排名: {{ edu.rank }}</template></p>
        <p v-if="edu.courses" class="rs-text-sm">主修课程：{{ edu.courses }}</p>
      </div>
    </section>

    <!-- 工作经历 -->
    <section v-if="data.workExperience.length" class="rs-section">
      <h2 class="rs-section-title">工作经历</h2>
      <div v-for="work in data.workExperience" :key="work.id" class="rs-item">
        <div class="rs-item-header">
          <span class="rs-item-title">{{ work.company }}</span>
          <span class="rs-item-date">{{ work.startDate }} - {{ work.endDate }}</span>
        </div>
        <p class="rs-item-sub">{{ work.position }} <template v-if="work.department">| {{ work.department }}</template></p>
        <ul v-if="work.description?.length" class="rs-list">
          <li v-for="(desc, i) in work.description" :key="i" class="rs-text-sm">{{ desc }}</li>
        </ul>
      </div>
    </section>

    <!-- 项目经历 -->
    <section v-if="data.projects.length" class="rs-section">
      <h2 class="rs-section-title">项目经历</h2>
      <div v-for="proj in data.projects" :key="proj.id" class="rs-item">
        <div class="rs-item-header">
          <span class="rs-item-title">{{ proj.name }}</span>
          <span class="rs-item-role">{{ proj.role }}</span>
        </div>
        <p v-if="proj.techStack" class="rs-text-sm">技术栈：{{ proj.techStack }}</p>
        <p v-if="proj.description" class="rs-text-sm">{{ proj.description }}</p>
        <p v-if="proj.achievements" class="rs-text-sm rs-highlight">成果：{{ proj.achievements }}</p>
      </div>
    </section>

    <!-- 技能 -->
    <section v-if="data.skills.length" class="rs-section">
      <h2 class="rs-section-title">专业技能</h2>
      <div class="rs-skills">
        <span v-for="skill in data.skills" :key="skill.id" class="rs-skill-tag">
          {{ skill.name }}
        </span>
      </div>
    </section>

    <!-- 奖项荣誉 -->
    <section v-if="data.awards.length" class="rs-section">
      <h2 class="rs-section-title">奖项荣誉</h2>
      <div v-for="award in data.awards" :key="award.id" class="rs-item">
        <div class="rs-item-header">
          <span class="rs-item-title">{{ award.name }}</span>
          <span class="rs-item-date">{{ award.date }}</span>
        </div>
        <p class="rs-item-sub">{{ award.organization }} <template v-if="award.level">| {{ award.level }}</template></p>
      </div>
    </section>
  </div>
</template>

<script setup>
defineProps({
  data: { type: Object, required: true },
  color: { type: String, default: '#4361ee' },
  editMode: { type: Boolean, default: false },
})
</script>

<style scoped>
.resume-simple {
  font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
  font-size: 14px;
  color: #333;
  line-height: 1.6;
  padding: 40px;
  background: #fff;
  width: 794px;
  min-height: 1123px;
}

/* 头部 */
.rs-header {
  text-align: center;
  border-bottom: 3px solid var(--theme);
  padding-bottom: 16px;
  margin-bottom: 20px;
  position: relative;
}

.rs-avatar {
  position: absolute;
  right: 0;
  top: 0;
  width: 85px;
  height: 119px;
  border-radius: 6px;
  overflow: hidden;
  border: 2px solid var(--theme);
}

.rs-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.rs-name {
  font-size: 28px;
  font-weight: 700;
  color: #1a1a2e;
  margin-bottom: 4px;
}

.rs-intention {
  font-size: 15px;
  color: var(--theme);
  font-weight: 500;
  margin-bottom: 8px;
}

.rs-contact {
  font-size: 12px;
  color: #666;
}

.rs-contact span {
  margin: 0 2px;
}

/* 区块 */
.rs-section {
  margin-bottom: 18px;
}

.rs-section-title {
  font-size: 15px;
  font-weight: 700;
  color: var(--theme);
  border-left: 4px solid var(--theme);
  padding-left: 8px;
  margin-bottom: 10px;
}

/* 条目 */
.rs-item {
  margin-bottom: 12px;
}

.rs-item-header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
}

.rs-item-title {
  font-size: 14px;
  font-weight: 600;
  color: #1a1a2e;
}

.rs-item-date {
  font-size: 12px;
  color: #999;
}

.rs-item-sub {
  font-size: 13px;
  color: #555;
  margin: 2px 0;
}

.rs-item-role {
  font-size: 12px;
  color: var(--theme);
}

/* 文本 */
.rs-text {
  font-size: 13px;
  color: #555;
  line-height: 1.7;
}

.rs-text-sm {
  font-size: 12px;
  color: #666;
  margin: 2px 0;
  line-height: 1.6;
}

.rs-highlight {
  color: var(--theme);
  font-weight: 500;
}

/* 列表 */
.rs-list {
  list-style: disc;
  padding-left: 18px;
  margin: 4px 0;
}

.rs-list li {
  margin: 2px 0;
}

/* 技能 */
.rs-skills {
  display: block;
}

.rs-skill-tag {
  display: block;
  padding: 3px 0;
  font-size: 13px;
  color: #333;
  line-height: 1.8;
}
</style>
