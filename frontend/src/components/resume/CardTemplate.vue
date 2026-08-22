<template>
  <div class="resume-card-tpl" :style="{ '--theme': color }">
    <header class="tc-header">
      <div class="tc-avatar" v-if="data.personal.avatar"><img :src="data.personal.avatar" alt="photo" /></div>
      <div class="tc-header-info">
        <h1 class="tc-name">{{ data.personal.name || '姓名' }}</h1>
        <p class="tc-intention" :style="{ color: color }">{{ data.personal.jobIntention || '求职意向' }}</p>
      </div>
      <div class="tc-header-contact">
        <span v-if="data.personal.phone">{{ data.personal.phone }}</span>
        <span v-if="data.personal.email">{{ data.personal.email }}</span>
        <span v-if="data.personal.github">{{ data.personal.github }}</span>
      </div>
    </header>
    <div class="tc-body">
      <section v-if="data.personal.selfEvaluation" class="tc-card"><h2 class="tc-card-title" :style="{ color: color }">自我评价</h2><p class="tc-text">{{ data.personal.selfEvaluation }}</p></section>
      <section v-if="data.education.length" class="tc-card"><h2 class="tc-card-title" :style="{ color: color }">教育背景</h2><div v-for="e in data.education" :key="e.id" class="tc-entry"><div class="tc-row"><b>{{ e.school }}</b><span class="tc-date">{{ e.startDate }}—{{ e.endDate }}</span></div><p class="tc-sub">{{ e.major }} · {{ e.degree }}</p></div></section>
      <section v-if="data.workExperience.length" class="tc-card"><h2 class="tc-card-title" :style="{ color: color }">工作经历</h2><div v-for="w in data.workExperience" :key="w.id" class="tc-entry"><div class="tc-row"><b>{{ w.company }}</b><span class="tc-date">{{ w.startDate }}—{{ w.endDate }}</span></div><p class="tc-sub">{{ w.position }}</p><ul class="tc-list"><li v-for="(d,i) in w.description" :key="i">{{ d }}</li></ul></div></section>
      <section v-if="data.projects.length" class="tc-card"><h2 class="tc-card-title" :style="{ color: color }">项目经历</h2><div v-for="p in data.projects" :key="p.id" class="tc-entry"><div class="tc-row"><b>{{ p.name }}</b><span class="tc-role" :style="{color}">{{ p.role }}</span></div><p v-if="p.techStack" class="tc-sub">{{ p.techStack }}</p><p v-if="p.description" class="tc-text-sm">{{ p.description }}</p></div></section>
      <div class="tc-two-col">
        <section v-if="data.skills.length" class="tc-card"><h2 class="tc-card-title" :style="{ color: color }">专业技能</h2><div class="tc-skills"><span v-for="s in data.skills" :key="s.id" class="tc-skill">{{ s.name }}</span></div></section>
        <section v-if="data.awards.length" class="tc-card"><h2 class="tc-card-title" :style="{ color: color }">荣誉奖项</h2><div v-for="a in data.awards" :key="a.id" class="tc-award"><span>{{ a.name }}</span><span class="tc-date">{{ a.date }}</span></div></section>
      </div>
    </div>
  </div>
</template>
<script setup>defineProps({ data: { type: Object, required: true }, color: { type: String, default: '#a08f75' } })</script>
<style scoped>
.resume-card-tpl{font-family:'PingFang SC','Microsoft YaHei',sans-serif;font-size:14px;color:#333;line-height:1.6;background:#f5f6f8;width:794px;min-height:1123px;padding:20px}
.tc-header{display:flex;align-items:center;gap:16px;background:#fff;border-radius:10px;padding:20px 24px;margin-bottom:14px;box-shadow:0 2px 8px rgba(0,0,0,.06)}
.tc-avatar{width:85px;height:119px;border-radius:8px;overflow:hidden;flex-shrink:0}
.tc-avatar img{width:100%;height:100%;object-fit:cover}
.tc-header-info{flex:1}
.tc-name{font-size:24px;font-weight:700;color:#1a1a2e}
.tc-intention{font-size:14px;margin-top:2px}
.tc-header-contact{font-size:11px;color:#999;text-align:right}
.tc-header-contact span{display:block;margin:2px 0}
.tc-body{display:flex;flex-direction:column;gap:12px}
.tc-card{background:#fff;border-radius:8px;padding:16px 20px;box-shadow:0 2px 8px rgba(0,0,0,.04)}
.tc-card-title{font-size:14px;font-weight:700;margin-bottom:10px;padding-bottom:6px;border-bottom:2px solid #f0f0f0}
.tc-entry{margin-bottom:10px}
.tc-row{display:flex;justify-content:space-between;align-items:baseline}
.tc-row b{font-size:14px;color:#1a1a2e}
.tc-date{font-size:12px;color:#999}
.tc-sub{font-size:13px;color:#555;margin:2px 0}
.tc-text{font-size:13px;color:#555;line-height:1.7}
.tc-text-sm{font-size:12px;color:#666;margin:2px 0;line-height:1.6}
.tc-list{list-style:disc;padding-left:18px;margin:4px 0}.tc-list li{font-size:12px;color:#666;margin:2px 0}
.tc-two-col{display:flex;gap:12px}
.tc-two-col .tc-card{flex:1}
.tc-skills{display:block}.tc-skill{display:block;font-size:13px;color:#333;padding:2px 0;line-height:1.8}
.tc-award{display:flex;justify-content:space-between;padding:3px 0;border-bottom:1px dashed #eee;font-size:13px}
.tc-role{font-size:12px;font-weight:600}
</style>
