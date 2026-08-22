<template>
  <div class="resume-split" :style="{ '--theme': color }">
    <div class="sp-top">
      <div class="sp-left" :style="{ background: color }">
        <div class="sp-avatar" v-if="data.personal.avatar"><img :src="data.personal.avatar" alt="photo" /></div>
        <div class="sp-contact">
          <p v-if="data.personal.phone">📱 {{ data.personal.phone }}</p>
          <p v-if="data.personal.email">✉ {{ data.personal.email }}</p>
          <p v-if="data.personal.github">⌨ {{ data.personal.github }}</p>
        </div>
      </div>
      <div class="sp-right">
        <h1 class="sp-name" :style="{ color: color }">{{ data.personal.name || '姓名' }}</h1>
        <p class="sp-intention">{{ data.personal.jobIntention || '求职意向' }}</p>
        <p v-if="data.personal.selfEvaluation" class="sp-eval">{{ data.personal.selfEvaluation }}</p>
      </div>
    </div>
    <div class="sp-body">
      <section v-if="data.education.length" class="sp-sec"><h2 class="sp-sec-title" :style="{borderColor:color}"><span :style="{background:color}">教育背景</span></h2><div v-for="e in data.education" :key="e.id" class="sp-entry"><div class="sp-row"><b>{{ e.school }}</b><span class="sp-date">{{ e.startDate }}—{{ e.endDate }}</span></div><p class="sp-sub">{{ e.major }} · {{ e.degree }}</p></div></section>
      <section v-if="data.workExperience.length" class="sp-sec"><h2 class="sp-sec-title" :style="{borderColor:color}"><span :style="{background:color}">工作经历</span></h2><div v-for="w in data.workExperience" :key="w.id" class="sp-entry"><div class="sp-row"><b>{{ w.company }}</b><span class="sp-date">{{ w.startDate }}—{{ w.endDate }}</span></div><p class="sp-sub">{{ w.position }}</p><ul class="sp-list"><li v-for="(d,i) in w.description" :key="i">{{ d }}</li></ul></div></section>
      <section v-if="data.projects.length" class="sp-sec"><h2 class="sp-sec-title" :style="{borderColor:color}"><span :style="{background:color}">项目经历</span></h2><div v-for="p in data.projects" :key="p.id" class="sp-entry"><div class="sp-row"><b>{{ p.name }}</b><span class="sp-role" :style="{color}">{{ p.role }}</span></div><p v-if="p.techStack" class="sp-sub">{{ p.techStack }}</p><p v-if="p.description" class="sp-text-sm">{{ p.description }}</p></div></section>
      <div class="sp-two-col">
        <section v-if="data.skills.length" class="sp-sec"><h2 class="sp-sec-title" :style="{borderColor:color}"><span :style="{background:color}">专业技能</span></h2><div class="sp-skills"><span v-for="s in data.skills" :key="s.id" class="sp-skill">{{ s.name }}</span></div></section>
        <section v-if="data.awards.length" class="sp-sec"><h2 class="sp-sec-title" :style="{borderColor:color}"><span :style="{background:color}">荣誉奖项</span></h2><div v-for="a in data.awards" :key="a.id" class="sp-award"><span>{{ a.name }}</span><span class="sp-date">{{ a.date }}</span></div></section>
      </div>
    </div>
  </div>
</template>
<script setup>defineProps({ data: { type: Object, required: true }, color: { type: String, default: '#3978a3' } })</script>
<style scoped>
.resume-split{font-family:'PingFang SC','Microsoft YaHei',sans-serif;font-size:14px;color:#333;line-height:1.6;background:#fff;width:794px;min-height:1123px}
.sp-top{display:flex;height:200px}
.sp-left{width:220px;padding:20px;display:flex;flex-direction:column;justify-content:center;gap:12px}
.sp-avatar{width:85px;height:119px;border-radius:6px;overflow:hidden;border:2px solid rgba(255,255,255,.3);margin:0 auto}
.sp-avatar img{width:100%;height:100%;object-fit:cover}
.sp-contact{color:rgba(255,255,255,.85);font-size:12px;text-align:center}
.sp-contact p{margin:4px 0}
.sp-right{flex:1;padding:30px 40px;display:flex;flex-direction:column;justify-content:center}
.sp-name{font-size:28px;font-weight:700;margin-bottom:4px}
.sp-intention{font-size:14px;color:#666;margin-bottom:8px}
.sp-eval{font-size:12px;color:#888;line-height:1.6}
.sp-body{padding:20px 40px}
.sp-sec{margin-bottom:18px}
.sp-sec-title{font-size:0;border-bottom:2px solid var(--theme);margin-bottom:10px;padding:0}
.sp-sec-title span{display:inline-block;color:#fff;font-size:14px;font-weight:600;padding:4px 14px}
.sp-entry{margin-bottom:12px}
.sp-row{display:flex;justify-content:space-between;align-items:baseline}
.sp-row b{font-size:14px;color:#1a1a2e}
.sp-date{font-size:12px;color:#999}
.sp-sub{font-size:13px;color:#555;margin:2px 0}
.sp-text-sm{font-size:12px;color:#666;margin:2px 0;line-height:1.6}
.sp-list{list-style:disc;padding-left:18px;margin:4px 0}.sp-list li{font-size:12px;color:#666;margin:2px 0}
.sp-two-col{display:flex;gap:30px}.sp-two-col .sp-sec{flex:1}
.sp-skills{display:block}.sp-skill{display:block;font-size:13px;color:#333;padding:2px 0;line-height:1.8}
.sp-award{display:flex;justify-content:space-between;padding:3px 0;border-bottom:1px dashed #eee;font-size:13px}
.sp-role{font-size:12px;font-weight:600}
</style>
