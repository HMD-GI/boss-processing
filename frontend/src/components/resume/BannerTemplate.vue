<template>
  <div class="resume-banner" :style="{ '--theme': color }">
    <div class="rb-banner" :style="{ background: color }">
      <div class="rb-banner-left">
        <h1 class="rb-name">{{ data.personal.name || '姓名' }}</h1>
        <p class="rb-intention">{{ data.personal.jobIntention || '求职意向' }}</p>
        <div class="rb-contact">
          <span v-if="data.personal.phone">{{ data.personal.phone }}</span>
          <span v-if="data.personal.email">{{ data.personal.email }}</span>
          <span v-if="data.personal.wechat">微信: {{ data.personal.wechat }}</span>
          <span v-if="data.personal.github">{{ data.personal.github }}</span>
          <span v-if="data.personal.blog">{{ data.personal.blog }}</span>
        </div>
      </div>
      <div class="rb-avatar" v-if="data.personal.avatar">
        <img :src="data.personal.avatar" alt="photo" />
      </div>
    </div>
    <div class="rb-body">
      <section v-if="data.personal.selfEvaluation" class="rb-section"><h2 class="rb-title">自我评价</h2><p class="rb-text">{{ data.personal.selfEvaluation }}</p></section>
      <section v-if="data.education.length" class="rb-section"><h2 class="rb-title">教育背景</h2><div v-for="edu in data.education" :key="edu.id" class="rb-entry"><div class="rb-row"><b>{{ edu.school }}</b><span class="rb-date">{{ edu.startDate }}—{{ edu.endDate }}</span></div><p class="rb-sub">{{ edu.major }} · {{ edu.degree }}<span v-if="edu.gpa"> · GPA: {{ edu.gpa }}</span><span v-if="edu.rank"> · 排名: {{ edu.rank }}</span></p><p v-if="edu.courses" class="rb-text-sm">主修课程：{{ edu.courses }}</p></div></section>
      <section v-if="data.workExperience.length" class="rb-section"><h2 class="rb-title">工作经历</h2><div v-for="w in data.workExperience" :key="w.id" class="rb-entry"><div class="rb-row"><b>{{ w.company }}</b><span class="rb-date">{{ w.startDate }}—{{ w.endDate }}</span></div><p class="rb-sub">{{ w.position }}</p><ul class="rb-list"><li v-for="(d,i) in w.description" :key="i">{{ d }}</li></ul></div></section>
      <section v-if="data.projects.length" class="rb-section"><h2 class="rb-title">项目经历</h2><div v-for="p in data.projects" :key="p.id" class="rb-entry"><div class="rb-row"><b>{{ p.name }}</b><span class="rb-role">{{ p.role }}</span></div><p v-if="p.techStack" class="rb-sub">{{ p.techStack }}</p><p v-if="p.description" class="rb-text-sm">{{ p.description }}</p></div></section>
      <div class="rb-two-col">
        <section v-if="data.skills.length" class="rb-section"><h2 class="rb-title">专业技能</h2><div class="rb-skills"><span v-for="s in data.skills" :key="s.id" class="rb-skill">{{ s.name }}</span></div></section>
        <section v-if="data.awards.length" class="rb-section"><h2 class="rb-title">荣誉奖项</h2><div v-for="a in data.awards" :key="a.id" class="rb-award"><span>{{ a.name }}</span><span class="rb-date">{{ a.date }}</span></div></section>
      </div>
    </div>
  </div>
</template>
<script setup>defineProps({ data: { type: Object, required: true }, color: { type: String, default: '#0e88ad' }, editMode: { type: Boolean, default: false } })</script>
<style scoped>
.resume-banner{font-family:'PingFang SC','Microsoft YaHei',sans-serif;font-size:14px;color:#333;line-height:1.6;background:#fff;width:794px;min-height:1123px}
.rb-banner{display:flex;justify-content:space-between;align-items:center;padding:24px 40px;color:#fff}
.rb-name{font-size:26px;font-weight:700;margin-bottom:4px}
.rb-intention{font-size:14px;opacity:.9;margin-bottom:8px}
.rb-contact{font-size:12px;opacity:.85}
.rb-contact span{margin-right:12px}
.rb-avatar{width:85px;height:119px;border-radius:6px;overflow:hidden;border:2px solid rgba(255,255,255,.4);flex-shrink:0}
.rb-avatar img{width:100%;height:100%;object-fit:cover}
.rb-body{padding:20px 40px}
.rb-section{margin-bottom:18px}
.rb-title{font-size:14px;font-weight:700;color:var(--theme);border-left:3px solid var(--theme);padding-left:8px;margin-bottom:10px}
.rb-entry{margin-bottom:12px}
.rb-row{display:flex;justify-content:space-between;align-items:baseline}
.rb-row b{font-size:14px;color:#1a1a2e}
.rb-date{font-size:12px;color:#999}
.rb-sub{font-size:13px;color:#555;margin:2px 0}
.rb-text{font-size:13px;color:#555;line-height:1.7}
.rb-text-sm{font-size:12px;color:#666;margin:2px 0;line-height:1.6}
.rb-list{list-style:disc;padding-left:18px;margin:4px 0}.rb-list li{font-size:12px;color:#666;margin:2px 0}
.rb-two-col{display:flex;gap:30px}.rb-two-col .rb-section{flex:1}
.rb-skills{display:block}.rb-skill{display:block;font-size:13px;color:#333;padding:2px 0;line-height:1.8}
.rb-award{display:flex;justify-content:space-between;padding:3px 0;border-bottom:1px dashed #eee;font-size:13px}
</style>
