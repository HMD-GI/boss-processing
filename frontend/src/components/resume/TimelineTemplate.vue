<template>
  <div class="resume-timeline-tpl" :style="{ '--theme': color }">
    <header class="tt-header">
      <div class="tt-avatar" v-if="data.personal.avatar"><img :src="data.personal.avatar" alt="photo" /></div>
      <div class="tt-header-info">
        <h1 class="tt-name" :style="{ color: color }">{{ data.personal.name || '姓名' }}</h1>
        <p class="tt-intention">{{ data.personal.jobIntention || '求职意向' }}</p>
        <div class="tt-contact"><span v-if="data.personal.phone">{{ data.personal.phone }}</span><span v-if="data.personal.email">| {{ data.personal.email }}</span><span v-if="data.personal.github">| {{ data.personal.github }}</span><span v-if="data.personal.blog">| {{ data.personal.blog }}</span></div>
      </div>
    </header>
    <div class="tt-body">
      <section v-if="data.personal.selfEvaluation" class="tt-sec"><h2 class="tt-sec-title" :style="{ color: color }">关于我</h2><p class="tt-text">{{ data.personal.selfEvaluation }}</p></section>
      <section v-if="data.education.length" class="tt-sec"><h2 class="tt-sec-title" :style="{ color: color }">教育经历</h2><div class="tt-timeline"><div v-for="e in data.education" :key="e.id" class="tt-item"><div class="tt-dot" :style="{ background: color }"></div><div class="tt-content"><div class="tt-row"><b>{{ e.school }}</b><span class="tt-date">{{ e.startDate }}—{{ e.endDate }}</span></div><p class="tt-sub">{{ e.major }} · {{ e.degree }}</p></div></div></div></section>
      <section v-if="data.workExperience.length" class="tt-sec"><h2 class="tt-sec-title" :style="{ color: color }">工作经历</h2><div class="tt-timeline"><div v-for="w in data.workExperience" :key="w.id" class="tt-item"><div class="tt-dot" :style="{ background: color }"></div><div class="tt-content"><div class="tt-row"><b>{{ w.company }}</b><span class="tt-date">{{ w.startDate }}—{{ w.endDate }}</span></div><p class="tt-sub">{{ w.position }}</p><ul class="tt-list"><li v-for="(d,i) in w.description" :key="i">{{ d }}</li></ul></div></div></div></section>
      <section v-if="data.projects.length" class="tt-sec"><h2 class="tt-sec-title" :style="{ color: color }">项目经历</h2><div class="tt-timeline"><div v-for="p in data.projects" :key="p.id" class="tt-item"><div class="tt-dot" :style="{ background: color }"></div><div class="tt-content"><div class="tt-row"><b>{{ p.name }}</b><span class="tt-role" :style="{color}">{{ p.role }}</span></div><p v-if="p.techStack" class="tt-sub">{{ p.techStack }}</p><p v-if="p.description" class="tt-text-sm">{{ p.description }}</p></div></div></div></section>
      <div class="tt-two-col">
        <section v-if="data.skills.length" class="tt-sec"><h2 class="tt-sec-title" :style="{ color: color }">专业技能</h2><div class="tt-skills"><span v-for="s in data.skills" :key="s.id" class="tt-skill">{{ s.name }}</span></div></section>
        <section v-if="data.awards.length" class="tt-sec"><h2 class="tt-sec-title" :style="{ color: color }">荣誉奖项</h2><div v-for="a in data.awards" :key="a.id" class="tt-award"><span>{{ a.name }}</span><span class="tt-date">{{ a.date }}</span></div></section>
      </div>
    </div>
  </div>
</template>
<script setup>defineProps({ data: { type: Object, required: true }, color: { type: String, default: '#1575bf' } })</script>
<style scoped>
.resume-timeline-tpl{font-family:'PingFang SC','Microsoft YaHei',sans-serif;font-size:14px;color:#333;line-height:1.6;background:#fff;width:794px;min-height:1123px}
.tt-header{display:flex;align-items:center;gap:24px;padding:40px 40px 30px;border-bottom:3px solid var(--theme)}
.tt-avatar{width:85px;height:119px;border-radius:6px;overflow:hidden;border:2px solid var(--theme);flex-shrink:0}
.tt-avatar img{width:100%;height:100%;object-fit:cover}
.tt-name{font-size:28px;font-weight:700;margin-bottom:4px}
.tt-intention{font-size:14px;color:#666;margin-bottom:8px}
.tt-contact{font-size:12px;color:#999}
.tt-body{padding:24px 40px}
.tt-sec{margin-bottom:22px}
.tt-sec-title{font-size:16px;font-weight:700;margin-bottom:14px}
.tt-timeline{position:relative;padding-left:20px}
.tt-timeline::before{content:'';position:absolute;left:5px;top:0;bottom:0;width:2px;background:#e8ecf1}
.tt-item{display:flex;gap:12px;margin-bottom:14px;position:relative}
.tt-dot{width:12px;height:12px;border-radius:50%;border:2px solid #fff;box-shadow:0 0 0 2px var(--theme);flex-shrink:0;margin-top:4px;z-index:1}
.tt-content{flex:1}
.tt-row{display:flex;justify-content:space-between;align-items:baseline}
.tt-row b{font-size:14px;color:#1a1a2e}
.tt-date{font-size:12px;color:#999}
.tt-sub{font-size:13px;color:#555;margin:2px 0}
.tt-text{font-size:13px;color:#555;line-height:1.7}
.tt-text-sm{font-size:12px;color:#666;margin:2px 0;line-height:1.6}
.tt-list{list-style:disc;padding-left:18px;margin:4px 0}.tt-list li{font-size:12px;color:#666;margin:2px 0}
.tt-two-col{display:flex;gap:30px}.tt-two-col .tt-sec{flex:1}
.tt-skills{display:block}.tt-skill{display:block;font-size:13px;color:#333;padding:2px 0;line-height:1.8}
.tt-award{display:flex;justify-content:space-between;padding:4px 0;border-bottom:1px dashed #eee;font-size:13px}
.tt-role{font-size:12px;font-weight:600}
</style>
