<template>
  <div class="resume-two-col-tpl" :style="{ '--theme': color }">
    <header class="tw-header">
      <div class="tw-avatar" v-if="data.personal.avatar"><img :src="data.personal.avatar" alt="photo" /></div>
      <div class="tw-name-block">
        <h1 class="tw-name" :style="{ color: color }">{{ data.personal.name || '姓名' }}</h1>
        <p class="tw-intention">{{ data.personal.jobIntention || '求职意向' }}</p>
      </div>
      <div class="tw-contact-block">
        <div v-if="data.personal.phone" class="tw-c-item">{{ data.personal.phone }}</div>
        <div v-if="data.personal.email" class="tw-c-item">{{ data.personal.email }}</div>
        <div v-if="data.personal.github" class="tw-c-item">{{ data.personal.github }}</div>
        <div v-if="data.personal.blog" class="tw-c-item">{{ data.personal.blog }}</div>
      </div>
    </header>
    <div class="tw-body">
      <!-- 左栏 -->
      <div class="tw-left">
        <section v-if="data.personal.selfEvaluation" class="tw-sec"><h2 class="tw-sec-title" :style="{ borderColor: color }">自我评价</h2><p class="tw-text">{{ data.personal.selfEvaluation }}</p></section>
        <section v-if="data.skills.length" class="tw-sec"><h2 class="tw-sec-title" :style="{ borderColor: color }">专业技能</h2><div class="tw-skills"><span v-for="s in data.skills" :key="s.id" class="tw-skill">{{ s.name }}</span></div></section>
        <section v-if="data.awards.length" class="tw-sec"><h2 class="tw-sec-title" :style="{ borderColor: color }">荣誉奖项</h2><div v-for="a in data.awards" :key="a.id" class="tw-award"><span>{{ a.name }}</span><span class="tw-date">{{ a.date }}</span></div></section>
      </div>
      <!-- 右栏 -->
      <div class="tw-right">
        <section v-if="data.education.length" class="tw-sec"><h2 class="tw-sec-title" :style="{ borderColor: color }">教育经历</h2><div v-for="e in data.education" :key="e.id" class="tw-entry"><div class="tw-row"><b>{{ e.school }}</b><span class="tw-date">{{ e.startDate }}—{{ e.endDate }}</span></div><p class="tw-sub">{{ e.major }} · {{ e.degree }}</p></div></section>
        <section v-if="data.workExperience.length" class="tw-sec"><h2 class="tw-sec-title" :style="{ borderColor: color }">工作经历</h2><div v-for="w in data.workExperience" :key="w.id" class="tw-entry"><div class="tw-row"><b>{{ w.company }}</b><span class="tw-date">{{ w.startDate }}—{{ w.endDate }}</span></div><p class="tw-sub">{{ w.position }}</p><ul class="tw-list"><li v-for="(d,i) in w.description" :key="i">{{ d }}</li></ul></div></section>
        <section v-if="data.projects.length" class="tw-sec"><h2 class="tw-sec-title" :style="{ borderColor: color }">项目经历</h2><div v-for="p in data.projects" :key="p.id" class="tw-entry"><div class="tw-row"><b>{{ p.name }}</b><span class="tw-role" :style="{color}">{{ p.role }}</span></div><p v-if="p.techStack" class="tw-sub">{{ p.techStack }}</p><p v-if="p.description" class="tw-text-sm">{{ p.description }}</p></div></section>
      </div>
    </div>
  </div>
</template>
<script setup>defineProps({ data: { type: Object, required: true }, color: { type: String, default: '#609ef3' } })</script>
<style scoped>
.resume-two-col-tpl{font-family:'PingFang SC','Microsoft YaHei',sans-serif;font-size:14px;color:#333;line-height:1.6;background:#fff;width:794px;min-height:1123px}
.tw-header{display:flex;align-items:center;gap:20px;padding:28px 40px;border-bottom:3px solid var(--theme)}
.tw-avatar{width:85px;height:119px;border-radius:6px;overflow:hidden;border:2px solid var(--theme);flex-shrink:0}
.tw-avatar img{width:100%;height:100%;object-fit:cover}
.tw-name-block{flex:1}
.tw-name{font-size:26px;font-weight:700;margin-bottom:4px}
.tw-intention{font-size:14px;color:#666}
.tw-contact-block{text-align:right;font-size:12px;color:#999}
.tw-c-item{margin:3px 0}
.tw-body{display:flex;gap:24px;padding:20px 40px}
.tw-left{width:200px;flex-shrink:0}
.tw-right{flex:1}
.tw-sec{margin-bottom:18px}
.tw-sec-title{font-size:14px;font-weight:700;color:#1a1a2e;border-left:3px solid var(--theme);padding-left:8px;margin-bottom:10px}
.tw-entry{margin-bottom:12px}
.tw-row{display:flex;justify-content:space-between;align-items:baseline}
.tw-row b{font-size:14px;color:#1a1a2e}
.tw-date{font-size:12px;color:#999}
.tw-sub{font-size:13px;color:#555;margin:2px 0}
.tw-text{font-size:13px;color:#555;line-height:1.7}
.tw-text-sm{font-size:12px;color:#666;margin:2px 0;line-height:1.6}
.tw-list{list-style:disc;padding-left:18px;margin:4px 0}.tw-list li{font-size:12px;color:#666;margin:2px 0}
.tw-skills{display:block}.tw-skill{display:block;font-size:13px;color:#333;padding:2px 0;line-height:1.8}
.tw-award{display:flex;justify-content:space-between;padding:3px 0;border-bottom:1px dashed #eee;font-size:13px}
.tw-role{font-size:12px;font-weight:600}
</style>
