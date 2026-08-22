<template>
  <div class="resume-header-tpl" :style="{ '--theme': color }">
    <div class="rh-top" :style="{ background: color }"><span class="rh-top-text">PERSONAL RESUME</span></div>
    <div class="rh-header">
      <div class="rh-avatar" v-if="data.personal.avatar"><img :src="data.personal.avatar" alt="photo" /></div>
      <div class="rh-info">
        <h1 class="rh-name" :style="{ color: color }">{{ data.personal.name || '姓名' }}</h1>
        <p class="rh-intention">{{ data.personal.jobIntention || '求职意向' }}</p>
        <div class="rh-contact"><span v-if="data.personal.phone">{{ data.personal.phone }}</span><span v-if="data.personal.email">| {{ data.personal.email }}</span><span v-if="data.personal.github">| {{ data.personal.github }}</span></div>
      </div>
    </div>
    <div class="rh-body">
      <section v-if="data.personal.selfEvaluation" class="rh-sec"><div class="rh-sec-title" :style="{ color: color }">自我评价</div><p class="rh-text">{{ data.personal.selfEvaluation }}</p></section>
      <section v-if="data.education.length" class="rh-sec"><div class="rh-sec-title" :style="{ color: color }">教育背景</div><div v-for="e in data.education" :key="e.id" class="rh-entry"><div class="rh-row"><b>{{ e.school }}</b><span class="rh-date">{{ e.startDate }}—{{ e.endDate }}</span></div><p class="rh-sub">{{ e.major }} · {{ e.degree }}</p></div></section>
      <section v-if="data.workExperience.length" class="rh-sec"><div class="rh-sec-title" :style="{ color: color }">工作经历</div><div v-for="w in data.workExperience" :key="w.id" class="rh-entry"><div class="rh-row"><b>{{ w.company }}</b><span class="rh-date">{{ w.startDate }}—{{ w.endDate }}</span></div><p class="rh-sub">{{ w.position }}</p><ul class="rh-list"><li v-for="(d,i) in w.description" :key="i">{{ d }}</li></ul></div></section>
      <section v-if="data.projects.length" class="rh-sec"><div class="rh-sec-title" :style="{ color: color }">项目经历</div><div v-for="p in data.projects" :key="p.id" class="rh-entry"><div class="rh-row"><b>{{ p.name }}</b><span class="rh-role" :style="{color}">{{ p.role }}</span></div><p v-if="p.techStack" class="rh-sub">{{ p.techStack }}</p><p v-if="p.description" class="rh-text-sm">{{ p.description }}</p></div></section>
      <div class="rh-two-col">
        <section v-if="data.skills.length" class="rh-sec"><div class="rh-sec-title" :style="{ color: color }">专业技能</div><div class="rh-skills"><span v-for="s in data.skills" :key="s.id" class="rh-skill">{{ s.name }}</span></div></section>
        <section v-if="data.awards.length" class="rh-sec"><div class="rh-sec-title" :style="{ color: color }">荣誉奖项</div><div v-for="a in data.awards" :key="a.id" class="rh-award"><span>{{ a.name }}</span><span class="rh-date">{{ a.date }}</span></div></section>
      </div>
    </div>
  </div>
</template>
<script setup>defineProps({ data: { type: Object, required: true }, color: { type: String, default: '#5695c3' } })</script>
<style scoped>
.resume-header-tpl{font-family:'PingFang SC','Microsoft YaHei',sans-serif;font-size:14px;color:#333;line-height:1.6;background:#fff;width:794px;min-height:1123px}
.rh-top{text-align:center;padding:6px 0;color:#fff;font-size:12px;letter-spacing:4px;font-weight:600}
.rh-header{display:flex;align-items:center;gap:20px;padding:24px 40px;border-bottom:2px solid var(--theme)}
.rh-avatar{width:85px;height:119px;border-radius:6px;overflow:hidden;border:2px solid var(--theme);flex-shrink:0}
.rh-avatar img{width:100%;height:100%;object-fit:cover}
.rh-name{font-size:26px;font-weight:700;margin-bottom:4px}
.rh-intention{font-size:14px;color:#666;margin-bottom:6px}
.rh-contact{font-size:12px;color:#999}
.rh-body{padding:20px 40px}
.rh-sec{margin-bottom:18px}
.rh-sec-title{font-size:14px;font-weight:700;padding-bottom:6px;border-bottom:1px solid #eee;margin-bottom:10px}
.rh-entry{margin-bottom:12px}
.rh-row{display:flex;justify-content:space-between;align-items:baseline}
.rh-row b{font-size:14px;color:#1a1a2e}
.rh-date{font-size:12px;color:#999}
.rh-sub{font-size:13px;color:#555;margin:2px 0}
.rh-text{font-size:13px;color:#555;line-height:1.7}
.rh-text-sm{font-size:12px;color:#666;margin:2px 0;line-height:1.6}
.rh-list{list-style:disc;padding-left:18px;margin:4px 0}.rh-list li{font-size:12px;color:#666;margin:2px 0}
.rh-two-col{display:flex;gap:30px}.rh-two-col .rh-sec{flex:1}
.rh-skills{display:block}.rh-skill{display:block;font-size:13px;color:#333;padding:2px 0;line-height:1.8}
.rh-award{display:flex;justify-content:space-between;padding:3px 0;border-bottom:1px dashed #eee;font-size:13px}
</style>
