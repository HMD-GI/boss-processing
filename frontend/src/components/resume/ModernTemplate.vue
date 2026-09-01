<template>
  <div class="resume-modern" :style="{ '--theme': color }">
    <!-- 头部 -->
    <header class="rm-header" :class="{ 'rm-header-edit': editMode }">
      <div
        class="rm-avatar"
        v-if="data.personal.avatar"
        :class="{ 'rm-drag-el': editMode }"
        @mousedown="editMode ? onDragStart($event, 'field', 'avatar') : null"
      >
        <img :src="data.personal.avatar" alt="photo" :style="avatarStyle" />
      </div>
      <div class="rm-header-left">
        <template v-if="!editMode">
          <h1 class="rm-name" :style="getFieldStyle('name')">{{ data.personal.name || '姓名' }}</h1>
          <p class="rm-intention" :style="getFieldStyle('jobIntention')">{{ data.personal.jobIntention || '求职意向' }}</p>
        </template>
        <template v-else>
          <div
            v-for="field in personalFields.filter(f => ['name','jobIntention'].includes(f.key))"
            :key="field.key"
            class="rm-drag-el rm-drag-field"
            :data-drag-key="field.key"
            data-drag-type="field"
            @mousedown="onDragStart($event, 'field', field.key)"
            :style="getFieldStyle(field.key)"
          >
            <h1 v-if="field.key === 'name'" class="rm-name">{{ data.personal.name || '姓名' }}</h1>
            <p v-if="field.key === 'jobIntention'" class="rm-intention">{{ data.personal.jobIntention || '求职意向' }}</p>
            <div class="rm-resize-handle rm-resize-se" @mousedown.stop="onResizeStart($event, 'field', field.key)"></div>
          </div>
        </template>
      </div>
      <div class="rm-contact">
        <template v-if="!editMode">
          <div v-if="data.personal.phone" class="rm-contact-item" :style="getFieldStyle('phone')">
            <span class="rm-ci-icon">手机</span>{{ data.personal.phone }}
          </div>
          <div v-if="data.personal.email" class="rm-contact-item" :style="getFieldStyle('email')">
            <span class="rm-ci-icon">邮箱</span>{{ data.personal.email }}
          </div>
          <div v-if="data.personal.wechat" class="rm-contact-item" :style="getFieldStyle('wechat')">
            <span class="rm-ci-icon">微信</span>{{ data.personal.wechat }}
          </div>
          <div v-if="data.personal.github" class="rm-contact-item" :style="getFieldStyle('github')">
            <span class="rm-ci-icon">GitHub</span>{{ data.personal.github }}
          </div>
          <div v-if="data.personal.blog" class="rm-contact-item" :style="getFieldStyle('blog')">
            <span class="rm-ci-icon">博客</span>{{ data.personal.blog }}
          </div>
          <div
            v-for="cf in getCustomFields('personal')"
            :key="cf.id"
            v-show="cf.label && cf.value"
            class="rm-contact-item"
            :style="getCustomFieldStyle(getCustomKey('personal', cf.id))"
          >
            <span class="rm-ci-icon">{{ cf.label }}</span>{{ cf.value }}
          </div>
        </template>
        <template v-else>
          <div
            v-for="field in contactFields"
            :key="field.key"
            v-show="data.personal[field.key]"
            class="rm-contact-item rm-drag-el rm-drag-field"
            :data-drag-key="field.key"
            data-drag-type="field"
            @mousedown="onDragStart($event, 'field', field.key)"
            :style="getFieldStyle(field.key)"
          >
            <span class="rm-ci-icon">{{ field.label }}</span>{{ data.personal[field.key] }}
            <div class="rm-resize-handle rm-resize-se" @mousedown.stop="onResizeStart($event, 'field', field.key)"></div>
          </div>
          <div
            v-for="cf in getCustomFields('personal')"
            :key="cf.id"
            class="rm-contact-item rm-drag-el rm-drag-field"
            :data-drag-key="getCustomKey('personal', cf.id)"
            data-drag-type="custom"
            @mousedown="onDragStart($event, 'custom', getCustomKey('personal', cf.id))"
            :style="getCustomFieldStyle(getCustomKey('personal', cf.id))"
          >
            <span class="rm-ci-icon">{{ cf.label || '标签' }}</span>{{ cf.value || '值' }}
            <div class="rm-resize-handle rm-resize-se" @mousedown.stop="onResizeStart($event, 'custom', getCustomKey('personal', cf.id))"></div>
          </div>
        </template>
      </div>
    </header>

    <div class="rm-body">
      <template v-for="sectionKey in orderedSections" :key="sectionKey">
        <!-- 自我评价 -->
        <section
          v-if="sectionKey === 'selfEvaluation' && data.personal.selfEvaluation"
          class="rm-section"
          :class="{ 'rm-drag-section': editMode }"
          :data-drag-key="sectionKey"
          data-drag-type="section"
          @mousedown="editMode ? onDragStart($event, 'section', sectionKey) : null"
          :style="getSectionStyle(sectionKey)"
        >
          <div class="rm-section-header">
            <span class="rm-section-bar"></span>
            <h2 class="rm-section-title">自我评价</h2>
          </div>
          <p class="rm-text">{{ data.personal.selfEvaluation }}</p>
          <template v-if="!editMode">
            <div v-for="cf in getCustomFields('selfEvaluation')" :key="cf.id" v-show="cf.label && cf.value" class="rm-text-sm"><strong>{{ cf.label }}：</strong>{{ cf.value }}</div>
          </template>
          <template v-else>
            <div
              v-for="cf in getCustomFields('selfEvaluation')"
              :key="cf.id"
              class="rm-text-sm rm-drag-el rm-drag-field"
              :data-drag-key="getCustomKey('selfEvaluation', cf.id)"
              data-drag-type="custom"
              @mousedown="onDragStart($event, 'custom', getCustomKey('selfEvaluation', cf.id))"
              :style="getCustomFieldStyle(getCustomKey('selfEvaluation', cf.id))"
            >
              <strong>{{ cf.label || '标签' }}：</strong>{{ cf.value || '值' }}
              <div class="rm-resize-handle rm-resize-se" @mousedown.stop="onResizeStart($event, 'custom', getCustomKey('selfEvaluation', cf.id))"></div>
            </div>
          </template>
          <div v-if="editMode" class="rm-resize-handle rm-resize-se" @mousedown.stop="onResizeStart($event, 'section', sectionKey)"></div>
        </section>

        <!-- 教育经历 -->
        <section
          v-if="sectionKey === 'education' && data.education.length"
          class="rm-section"
          :class="{ 'rm-drag-section': editMode }"
          :data-drag-key="sectionKey"
          data-drag-type="section"
          @mousedown="editMode ? onDragStart($event, 'section', sectionKey) : null"
          :style="getSectionStyle(sectionKey)"
        >
          <div class="rm-section-header">
            <span class="rm-section-bar"></span>
            <h2 class="rm-section-title">教育经历</h2>
          </div>
          <div v-for="edu in data.education" :key="edu.id" class="rm-timeline-item" :class="{ 'rm-sub-container': editMode }" :data-sub-container="`education_${edu.id}`">
            <div class="rm-dot"></div>
            <div class="rm-timeline-content">
              <template v-if="!editMode">
                <div class="rm-item-header">
                  <span class="rm-item-title">{{ edu.school }}</span>
                  <span class="rm-item-date">{{ edu.startDate }} - {{ edu.endDate }}</span>
                </div>
                <p class="rm-item-sub">{{ edu.major }} · {{ edu.degree }}</p>
                <div class="rm-item-meta">
                  <span v-if="edu.gpa" class="rm-meta-tag">GPA: {{ edu.gpa }}</span>
                  <span v-if="edu.rank" class="rm-meta-tag">排名: {{ edu.rank }}</span>
                </div>
                <p v-if="edu.courses" class="rm-text-sm">主修课程：{{ edu.courses }}</p>
                <div v-for="cf in getCustomFields('education', edu.id)" :key="cf.id" v-show="cf.label && cf.value" class="rm-text-sm"><strong>{{ cf.label }}：</strong>{{ cf.value }}</div>
              </template>
              <template v-else>
                <div class="rm-item-header rm-drag-el rm-drag-field"
                  :data-drag-key="`edu_${edu.id}_header`"
                  data-drag-type="sub"
                  @mousedown="onDragStart($event, 'sub', `edu_${edu.id}_header`)"
                  :style="getSubFieldStyle(`edu_${edu.id}_header`)"
                >
                  <span class="rm-item-title">{{ edu.school }}</span>
                  <span class="rm-item-date">{{ edu.startDate }} - {{ edu.endDate }}</span>
                  <div class="rm-resize-handle rm-resize-se" @mousedown.stop="onResizeStart($event, 'sub', `edu_${edu.id}_header`)"></div>
                </div>
                <div class="rm-item-sub rm-drag-el rm-drag-field"
                  :data-drag-key="`edu_${edu.id}_sub`"
                  data-drag-type="sub"
                  @mousedown="onDragStart($event, 'sub', `edu_${edu.id}_sub`)"
                  :style="getSubFieldStyle(`edu_${edu.id}_sub`)"
                >
                  {{ edu.major }} · {{ edu.degree }}
                  <div class="rm-resize-handle rm-resize-se" @mousedown.stop="onResizeStart($event, 'sub', `edu_${edu.id}_sub`)"></div>
                </div>
                <div class="rm-item-meta rm-drag-el rm-drag-field"
                  :data-drag-key="`edu_${edu.id}_meta`"
                  data-drag-type="sub"
                  @mousedown="onDragStart($event, 'sub', `edu_${edu.id}_meta`)"
                  :style="getSubFieldStyle(`edu_${edu.id}_meta`)"
                >
                  <span v-if="edu.gpa" class="rm-meta-tag">GPA: {{ edu.gpa }}</span>
                  <span v-if="edu.rank" class="rm-meta-tag">排名: {{ edu.rank }}</span>
                  <div class="rm-resize-handle rm-resize-se" @mousedown.stop="onResizeStart($event, 'sub', `edu_${edu.id}_meta`)"></div>
                </div>
                <div class="rm-text-sm rm-drag-el rm-drag-field"
                  :data-drag-key="`edu_${edu.id}_courses`"
                  data-drag-type="sub"
                  @mousedown="onDragStart($event, 'sub', `edu_${edu.id}_courses`)"
                  :style="getSubFieldStyle(`edu_${edu.id}_courses`)"
                >
                  主修课程：{{ edu.courses }}
                  <div class="rm-resize-handle rm-resize-se" @mousedown.stop="onResizeStart($event, 'sub', `edu_${edu.id}_courses`)"></div>
                </div>
                <div
                  v-for="cf in getCustomFields('education', edu.id)"
                  :key="cf.id"
                  class="rm-text-sm rm-drag-el rm-drag-field"
                  :data-drag-key="getCustomKey('education', cf.id, edu.id)"
                  data-drag-type="custom"
                  @mousedown="onDragStart($event, 'custom', getCustomKey('education', cf.id, edu.id))"
                  :style="getCustomFieldStyle(getCustomKey('education', cf.id, edu.id))"
                >
                  <strong>{{ cf.label || '标签' }}：</strong>{{ cf.value || '值' }}
                  <div class="rm-resize-handle rm-resize-se" @mousedown.stop="onResizeStart($event, 'custom', getCustomKey('education', cf.id, edu.id))"></div>
                </div>
              </template>
            </div>
          </div>
          <div v-if="editMode" class="rm-resize-handle rm-resize-se" @mousedown.stop="onResizeStart($event, 'section', sectionKey)"></div>
        </section>

        <!-- 工作经历 -->
        <section
          v-if="sectionKey === 'workExperience' && data.workExperience.length"
          class="rm-section"
          :class="{ 'rm-drag-section': editMode }"
          :data-drag-key="sectionKey"
          data-drag-type="section"
          @mousedown="editMode ? onDragStart($event, 'section', sectionKey) : null"
          :style="getSectionStyle(sectionKey)"
        >
          <div class="rm-section-header">
            <span class="rm-section-bar"></span>
            <h2 class="rm-section-title">工作经历</h2>
          </div>
          <div v-for="work in data.workExperience" :key="work.id" class="rm-timeline-item" :class="{ 'rm-sub-container': editMode }" :data-sub-container="`work_${work.id}`">
            <div class="rm-dot"></div>
            <div class="rm-timeline-content">
              <template v-if="!editMode">
                <div class="rm-item-header">
                  <span class="rm-item-title">{{ work.company }}</span>
                  <span class="rm-item-date">{{ work.startDate }} - {{ work.endDate }}</span>
                </div>
                <p class="rm-item-sub">{{ work.position }} <template v-if="work.department">| {{ work.department }}</template></p>
                <ul v-if="work.description?.length" class="rm-list">
                  <li v-for="(desc, i) in work.description" :key="i" class="rm-text-sm">{{ desc }}</li>
                </ul>
                <div v-for="cf in getCustomFields('work', work.id)" :key="cf.id" v-show="cf.label && cf.value" class="rm-text-sm"><strong>{{ cf.label }}：</strong>{{ cf.value }}</div>
              </template>
              <template v-else>
                <div class="rm-item-header rm-drag-el rm-drag-field"
                  :data-drag-key="`work_${work.id}_header`"
                  data-drag-type="sub"
                  @mousedown="onDragStart($event, 'sub', `work_${work.id}_header`)"
                  :style="getSubFieldStyle(`work_${work.id}_header`)"
                >
                  <span class="rm-item-title">{{ work.company }}</span>
                  <span class="rm-item-date">{{ work.startDate }} - {{ work.endDate }}</span>
                  <div class="rm-resize-handle rm-resize-se" @mousedown.stop="onResizeStart($event, 'sub', `work_${work.id}_header`)"></div>
                </div>
                <div class="rm-item-sub rm-drag-el rm-drag-field"
                  :data-drag-key="`work_${work.id}_sub`"
                  data-drag-type="sub"
                  @mousedown="onDragStart($event, 'sub', `work_${work.id}_sub`)"
                  :style="getSubFieldStyle(`work_${work.id}_sub`)"
                >
                  {{ work.position }} <template v-if="work.department">| {{ work.department }}</template>
                  <div class="rm-resize-handle rm-resize-se" @mousedown.stop="onResizeStart($event, 'sub', `work_${work.id}_sub`)"></div>
                </div>
                <div class="rm-list rm-drag-el rm-drag-field"
                  v-if="work.description?.length"
                  :data-drag-key="`work_${work.id}_desc`"
                  data-drag-type="sub"
                  @mousedown="onDragStart($event, 'sub', `work_${work.id}_desc`)"
                  :style="getSubFieldStyle(`work_${work.id}_desc`)"
                >
                  <ul>
                    <li v-for="(desc, i) in work.description" :key="i" class="rm-text-sm">{{ desc }}</li>
                  </ul>
                  <div class="rm-resize-handle rm-resize-se" @mousedown.stop="onResizeStart($event, 'sub', `work_${work.id}_desc`)"></div>
                </div>
                <div
                  v-for="cf in getCustomFields('work', work.id)"
                  :key="cf.id"
                  class="rm-text-sm rm-drag-el rm-drag-field"
                  :data-drag-key="getCustomKey('work', cf.id, work.id)"
                  data-drag-type="custom"
                  @mousedown="onDragStart($event, 'custom', getCustomKey('work', cf.id, work.id))"
                  :style="getCustomFieldStyle(getCustomKey('work', cf.id, work.id))"
                >
                  <strong>{{ cf.label || '标签' }}：</strong>{{ cf.value || '值' }}
                  <div class="rm-resize-handle rm-resize-se" @mousedown.stop="onResizeStart($event, 'custom', getCustomKey('work', cf.id, work.id))"></div>
                </div>
              </template>
            </div>
          </div>
          <div v-if="editMode" class="rm-resize-handle rm-resize-se" @mousedown.stop="onResizeStart($event, 'section', sectionKey)"></div>
        </section>

        <!-- 项目经历 -->
        <section
          v-if="sectionKey === 'projects' && data.projects.length"
          class="rm-section"
          :class="{ 'rm-drag-section': editMode }"
          :data-drag-key="sectionKey"
          data-drag-type="section"
          @mousedown="editMode ? onDragStart($event, 'section', sectionKey) : null"
          :style="getSectionStyle(sectionKey)"
        >
          <div class="rm-section-header">
            <span class="rm-section-bar"></span>
            <h2 class="rm-section-title">项目经历</h2>
          </div>
          <div v-for="proj in data.projects" :key="proj.id" class="rm-timeline-item" :class="{ 'rm-sub-container': editMode }" :data-sub-container="`project_${proj.id}`">
            <div class="rm-dot"></div>
            <div class="rm-timeline-content">
              <template v-if="!editMode">
                <div class="rm-item-header">
                  <span class="rm-item-title">{{ proj.name }}</span>
                  <span class="rm-item-role">{{ proj.role }}</span>
                </div>
                <p v-if="proj.techStack" class="rm-tech-stack">{{ proj.techStack }}</p>
                <p v-if="proj.description" class="rm-text-sm">{{ proj.description }}</p>
                <p v-if="proj.achievements" class="rm-text-sm rm-highlight">成果：{{ proj.achievements }}</p>
                <div v-for="cf in getCustomFields('project', proj.id)" :key="cf.id" v-show="cf.label && cf.value" class="rm-text-sm"><strong>{{ cf.label }}：</strong>{{ cf.value }}</div>
              </template>
              <template v-else>
                <div class="rm-item-header rm-drag-el rm-drag-field"
                  :data-drag-key="`proj_${proj.id}_header`"
                  data-drag-type="sub"
                  @mousedown="onDragStart($event, 'sub', `proj_${proj.id}_header`)"
                  :style="getSubFieldStyle(`proj_${proj.id}_header`)"
                >
                  <span class="rm-item-title">{{ proj.name }}</span>
                  <span class="rm-item-role">{{ proj.role }}</span>
                  <div class="rm-resize-handle rm-resize-se" @mousedown.stop="onResizeStart($event, 'sub', `proj_${proj.id}_header`)"></div>
                </div>
                <div v-if="proj.techStack" class="rm-tech-stack rm-drag-el rm-drag-field"
                  :data-drag-key="`proj_${proj.id}_tech`"
                  data-drag-type="sub"
                  @mousedown="onDragStart($event, 'sub', `proj_${proj.id}_tech`)"
                  :style="getSubFieldStyle(`proj_${proj.id}_tech`)"
                >
                  {{ proj.techStack }}
                  <div class="rm-resize-handle rm-resize-se" @mousedown.stop="onResizeStart($event, 'sub', `proj_${proj.id}_tech`)"></div>
                </div>
                <div v-if="proj.description" class="rm-text-sm rm-drag-el rm-drag-field"
                  :data-drag-key="`proj_${proj.id}_desc`"
                  data-drag-type="sub"
                  @mousedown="onDragStart($event, 'sub', `proj_${proj.id}_desc`)"
                  :style="getSubFieldStyle(`proj_${proj.id}_desc`)"
                >
                  {{ proj.description }}
                  <div class="rm-resize-handle rm-resize-se" @mousedown.stop="onResizeStart($event, 'sub', `proj_${proj.id}_desc`)"></div>
                </div>
                <div v-if="proj.achievements" class="rm-text-sm rm-highlight rm-drag-el rm-drag-field"
                  :data-drag-key="`proj_${proj.id}_ach`"
                  data-drag-type="sub"
                  @mousedown="onDragStart($event, 'sub', `proj_${proj.id}_ach`)"
                  :style="getSubFieldStyle(`proj_${proj.id}_ach`)"
                >
                  成果：{{ proj.achievements }}
                  <div class="rm-resize-handle rm-resize-se" @mousedown.stop="onResizeStart($event, 'sub', `proj_${proj.id}_ach`)"></div>
                </div>
                <div
                  v-for="cf in getCustomFields('project', proj.id)"
                  :key="cf.id"
                  class="rm-text-sm rm-drag-el rm-drag-field"
                  :data-drag-key="getCustomKey('project', cf.id, proj.id)"
                  data-drag-type="custom"
                  @mousedown="onDragStart($event, 'custom', getCustomKey('project', cf.id, proj.id))"
                  :style="getCustomFieldStyle(getCustomKey('project', cf.id, proj.id))"
                >
                  <strong>{{ cf.label || '标签' }}：</strong>{{ cf.value || '值' }}
                  <div class="rm-resize-handle rm-resize-se" @mousedown.stop="onResizeStart($event, 'custom', getCustomKey('project', cf.id, proj.id))"></div>
                </div>
              </template>
            </div>
          </div>
          <div v-if="editMode" class="rm-resize-handle rm-resize-se" @mousedown.stop="onResizeStart($event, 'section', sectionKey)"></div>
        </section>

        <!-- 技能 + 奖项 -->
        <div v-if="sectionKey === 'skills' || sectionKey === 'awards'" class="rm-two-col">
          <section
            v-if="sectionKey === 'skills' && data.skills.length"
            class="rm-section"
            :class="{ 'rm-drag-section': editMode }"
            :data-drag-key="'skills'"
            data-drag-type="section"
            @mousedown="editMode ? onDragStart($event, 'section', 'skills') : null"
            :style="getSectionStyle('skills')"
          >
            <div class="rm-section-header">
              <span class="rm-section-bar"></span>
              <h2 class="rm-section-title">专业技能</h2>
            </div>
            <div class="rm-skills">
              <span v-for="skill in data.skills" :key="skill.id" class="rm-skill-item">
                <span class="rm-skill-name">{{ skill.name }}</span>
              </span>
            </div>
            <template v-if="!editMode">
              <div v-for="cf in getCustomFields('skill')" :key="cf.id" v-show="cf.label && cf.value" class="rm-text-sm"><strong>{{ cf.label }}：</strong>{{ cf.value }}</div>
            </template>
            <template v-else>
              <div
                v-for="cf in getCustomFields('skill')"
                :key="cf.id"
                class="rm-text-sm rm-drag-el rm-drag-field"
                :data-drag-key="getCustomKey('skill', cf.id)"
                data-drag-type="custom"
                @mousedown="onDragStart($event, 'custom', getCustomKey('skill', cf.id))"
                :style="getCustomFieldStyle(getCustomKey('skill', cf.id))"
              >
                <strong>{{ cf.label || '标签' }}：</strong>{{ cf.value || '值' }}
                <div class="rm-resize-handle rm-resize-se" @mousedown.stop="onResizeStart($event, 'custom', getCustomKey('skill', cf.id))"></div>
              </div>
            </template>
            <div v-if="editMode" class="rm-resize-handle rm-resize-se" @mousedown.stop="onResizeStart($event, 'section', 'skills')"></div>
          </section>

          <section
            v-if="sectionKey === 'awards' && data.awards.length"
            class="rm-section"
            :class="{ 'rm-drag-section': editMode }"
            :data-drag-key="'awards'"
            data-drag-type="section"
            @mousedown="editMode ? onDragStart($event, 'section', 'awards') : null"
            :style="getSectionStyle('awards')"
          >
            <div class="rm-section-header">
              <span class="rm-section-bar"></span>
              <h2 class="rm-section-title">奖项荣誉</h2>
            </div>
            <div v-for="award in data.awards" :key="award.id" class="rm-award-item">
              <span class="rm-award-name">{{ award.name }}</span>
              <span class="rm-award-date">{{ award.date }}</span>
            </div>
            <template v-if="!editMode">
              <div v-for="cf in getCustomFields('award')" :key="cf.id" v-show="cf.label && cf.value" class="rm-text-sm"><strong>{{ cf.label }}：</strong>{{ cf.value }}</div>
            </template>
            <template v-else>
              <div
                v-for="cf in getCustomFields('award')"
                :key="cf.id"
                class="rm-text-sm rm-drag-el rm-drag-field"
                :data-drag-key="getCustomKey('award', cf.id)"
                data-drag-type="custom"
                @mousedown="onDragStart($event, 'custom', getCustomKey('award', cf.id))"
                :style="getCustomFieldStyle(getCustomKey('award', cf.id))"
              >
                <strong>{{ cf.label || '标签' }}：</strong>{{ cf.value || '值' }}
                <div class="rm-resize-handle rm-resize-se" @mousedown.stop="onResizeStart($event, 'custom', getCustomKey('award', cf.id))"></div>
              </div>
            </template>
            <div v-if="editMode" class="rm-resize-handle rm-resize-se" @mousedown.stop="onResizeStart($event, 'section', 'awards')"></div>
          </section>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, onUnmounted, nextTick } from 'vue'

const props = defineProps({
  data: { type: Object, required: true },
  color: { type: String, default: '#4361ee' },
  editMode: { type: Boolean, default: false },
})

const orderedSections = computed(() => {
  return props.data.sectionOrder || ['selfEvaluation', 'education', 'workExperience', 'projects', 'skills', 'awards']
})

const fieldLabels = {
  name: '姓名', jobIntention: '求职意向', phone: '手机',
  email: '邮箱', wechat: '微信', github: 'GitHub', blog: '博客',
}

const personalFields = computed(() => {
  const order = props.data.personalFieldOrder || ['name', 'jobIntention', 'phone', 'email', 'wechat', 'github', 'blog']
  return order.map(key => ({ key, label: fieldLabels[key] || key }))
})

const contactFields = computed(() => {
  return personalFields.value.filter(f => !['name', 'jobIntention'].includes(f.key))
})

function getCustomFields(category, parentId) {
  if (!props.data.customFields || !props.data.customFields[category]) return []
  if (parentId !== undefined) {
    const group = props.data.customFields[category].find(g => g.parentId === parentId)
    return group ? group.items : []
  }
  return props.data.customFields[category]
}

function getCustomKey(category, fieldId, parentId) {
  if (parentId !== undefined) return `custom_${category}_${parentId}_${fieldId}`
  return `custom_${category}_${fieldId}`
}

function getSectionStyle(key) {
  const pos = props.data.sectionPositions?.[key]
  const size = props.data.sectionSizes?.[key]
  const style = {}
  if (pos && (pos.x !== 0 || pos.y !== 0)) style.transform = `translate(${pos.x}px, ${pos.y}px)`
  if (size && (size.w || size.h)) {
    if (size.w) style.width = size.w + 'px'
    if (size.h) { style.height = size.h + 'px'; style.overflow = 'hidden' }
  }
  return style
}

function getFieldStyle(key) {
  const pos = props.data.personalFieldPositions?.[key]
  const size = props.data.personalFieldSizes?.[key]
  const style = {}
  if (pos && (pos.x !== 0 || pos.y !== 0)) style.transform = `translate(${pos.x}px, ${pos.y}px)`
  if (size && (size.w || size.h)) {
    if (size.w) style.maxWidth = size.w + 'px'
    if (size.h) { style.maxHeight = size.h + 'px'; style.overflow = 'hidden' }
  }
  return style
}

function getCustomFieldStyle(key) {
  const pos = props.data.customFieldPositions?.[key]
  const size = props.data.customFieldSizes?.[key]
  const style = {}
  if (pos && (pos.x !== 0 || pos.y !== 0)) style.transform = `translate(${pos.x}px, ${pos.y}px)`
  if (size && (size.w || size.h)) {
    if (size.w) style.maxWidth = size.w + 'px'
    if (size.h) { style.maxHeight = size.h + 'px'; style.overflow = 'hidden' }
  }
  return style
}

function getSubFieldStyle(key) {
  const pos = props.data.subFieldPositions?.[key]
  const size = props.data.subFieldSizes?.[key]
  const style = {}
  if (pos && (pos.x !== 0 || pos.y !== 0)) style.transform = `translate(${pos.x}px, ${pos.y}px)`
  if (size && (size.w || size.h)) {
    if (size.w) style.maxWidth = size.w + 'px'
    if (size.h) { style.maxHeight = size.h + 'px'; style.overflow = 'hidden' }
  }
  return style
}

const avatarStyle = computed(() => {
  const pos = props.data.personalFieldPositions?.['avatar']
  if (pos && (pos.x !== 0 || pos.y !== 0)) return { transform: `translate(${pos.x}px, ${pos.y}px)` }
  return {}
})

// ========== 拖拽逻辑 ==========
const dragState = ref({
  dragging: false, type: '', key: '', startX: 0, startY: 0,
  startOffsetX: 0, startOffsetY: 0, el: null, lastDx: 0, lastDy: 0,
  containerEl: null, // 父容器（用于范围约束）
})

// 设置元素位置
function setElementPos(type, key, x, y) {
  if (type === 'section') {
    if (!props.data.sectionPositions) props.data.sectionPositions = {}
    props.data.sectionPositions[key] = { x, y }
  } else if (type === 'field') {
    if (!props.data.personalFieldPositions) props.data.personalFieldPositions = {}
    props.data.personalFieldPositions[key] = { x, y }
  } else if (type === 'custom') {
    if (!props.data.customFieldPositions) props.data.customFieldPositions = {}
    props.data.customFieldPositions[key] = { x, y }
  } else if (type === 'sub') {
    if (!props.data.subFieldPositions) props.data.subFieldPositions = {}
    props.data.subFieldPositions[key] = { x, y }
  }
}

// 获取元素位置
function getElementPos(type, key) {
  if (type === 'section') return props.data.sectionPositions?.[key] || { x: 0, y: 0 }
  if (type === 'field') return props.data.personalFieldPositions?.[key] || { x: 0, y: 0 }
  if (type === 'custom') return props.data.customFieldPositions?.[key] || { x: 0, y: 0 }
  if (type === 'sub') return props.data.subFieldPositions?.[key] || { x: 0, y: 0 }
  return { x: 0, y: 0 }
}

// 获取所有可拖拽元素（可限定在某个容器范围内）
// 当 scope 为 'section' 时，只收集 section 级别的元素（跳过 sub/custom）
function getAllDragRects(excludeKey, excludeType, containerEl, scope) {
  const root = containerEl || document.querySelector('.resume-modern')
  if (!root) return []
  const els = root.querySelectorAll('[data-drag-key]')
  const rects = []
  els.forEach(el => {
    const key = el.getAttribute('data-drag-key')
    const type = el.getAttribute('data-drag-type')
    if (key === excludeKey && type === excludeType) return
    // 当 scope 为 'section' 时，只处理 section 类型，跳过 sub/custom/field
    if (scope === 'section' && type !== 'section') return
    const rect = el.getBoundingClientRect()
    rects.push({ el, key, type, rect })
  })
  return rects
}

function rectsOverlap(a, b) {
  return !(a.right < b.left || a.left > b.right || a.bottom < b.top || a.top > b.bottom)
}

// 查找元素所属的父容器（data-sub-container 或 section）
function getContainerOf(el) {
  if (!el) return null
  return el.closest('[data-sub-container]') || el.closest('section') || null
}

// 约束一个元素的位置使其不超出其父容器边界
// 使用 offsetLeft/offsetTop 获取元素在容器内的基础位置（不受 translate 影响），
// 再结合 translate 值计算最终位置并约束在容器范围内。
// 返回调整后的 translate 值 { x, y }
function clampPosInContainer(el, type, key, newX, newY) {
  const container = getContainerOf(el)
  if (!container) return { x: newX, y: newY }
  // 逐级累加 offsetParent 链，计算元素相对于 container 的基础位置（不受 translate 影响）
  let baseLeft = 0, baseTop = 0
  let node = el
  while (node && node !== container) {
    baseLeft += node.offsetLeft
    baseTop += node.offsetTop
    node = node.offsetParent
  }
  // 如果 offsetParent 链未到 container，用 fallback
  if (node !== container) {
    const elRect = el.getBoundingClientRect()
    const containerRect = container.getBoundingClientRect()
    const oldPos = getElementPos(type, key)
    baseLeft = (elRect.left - containerRect.left) - oldPos.x
    baseTop = (elRect.top - containerRect.top) - oldPos.y
  }
  // 获取元素尺寸
  const elW = el.offsetWidth
  const elH = el.offsetHeight
  const containerW = container.clientWidth
  const containerH = container.clientHeight
  // 新的相对位置 = 基础位置 + translate
  const newRelLeft = baseLeft + newX
  const newRelTop = baseTop + newY
  // 约束在 [0, containerSize - elSize] 范围内
  const clampedRelLeft = Math.max(0, Math.min(newRelLeft, containerW - elW))
  const clampedRelTop = Math.max(0, Math.min(newRelTop, containerH - elH))
  // 反算 translate 值
  const clampedX = newX - (newRelLeft - clampedRelLeft)
  const clampedY = newY - (newRelTop - clampedRelTop)
  return { x: clampedX, y: clampedY }
}

// 将 section 的 translate 值约束在简历模板边界内
// 返回约束后的 { x, y }
// 使用 offsetTop/offsetLeft 获取不受 translate 影响的基础位置
// 通过逐级累加 offsetParent 的 offset 来计算相对于 .resume-modern 的位置
function clampSectionToTemplate(sectionEl, key, newX, newY) {
  const root = document.querySelector('.resume-modern')
  if (!root) return { x: newX, y: newY }
  // 逐级累加 offsetParent 链，计算 section 相对于 root 的基础位置（不受 translate 影响）
  let baseLeft = 0, baseTop = 0
  let node = sectionEl
  while (node && node !== root) {
    baseLeft += node.offsetLeft
    baseTop += node.offsetTop
    node = node.offsetParent
  }
  // 如果 node 不是 root（说明 offsetParent 链未到 root），用 fallback
  if (node !== root) {
    const elRect = sectionEl.getBoundingClientRect()
    const rootRect = root.getBoundingClientRect()
    const oldPos = getElementPos('section', key)
    baseLeft = (elRect.left - rootRect.left) - oldPos.x
    baseTop = (elRect.top - rootRect.top) - oldPos.y
  }
  const elW = sectionEl.offsetWidth
  const elH = sectionEl.offsetHeight
  const containerW = root.clientWidth
  const containerH = root.clientHeight
  const newRelLeft = baseLeft + newX
  const newRelTop = baseTop + newY
  // 约束在 [0, containerSize - elSize] 范围内
  const clampedRelLeft = Math.max(0, Math.min(newRelLeft, containerW - elW))
  const clampedRelTop = Math.max(0, Math.min(newRelTop, containerH - elH))
  const clampedX = newX - (newRelLeft - clampedRelLeft)
  const clampedY = newY - (newRelTop - clampedRelTop)
  return { x: clampedX, y: clampedY }
}

// 尝试移动一个 section 及其所有内部子标签（整体移动），约束在简历模板边界内
// 返回实际移动量 { actualX, actualY }，供调用方判断是否需要尝试备选方向
// 关键：只移动 section 的 transform，子标签的 transform 保持不变
// 因为 CSS 的 transform 会叠加在父元素上，子标签会自动跟随 section 移动
// 如果同时修改子标签的 transform，会导致子标签被"双重移动"
function tryMoveSection(sectionEl, key, pushX, pushY) {
  const existingPos = getElementPos('section', key)
  let newSecX = existingPos.x + pushX
  let newSecY = existingPos.y + pushY
  // 约束 section 在简历模板边界内
  const clamped = clampSectionToTemplate(sectionEl, key, newSecX, newSecY)
  // 计算实际推移动量（可能被 clamp 修正过）
  const actualPushX = clamped.x - existingPos.x
  const actualPushY = clamped.y - existingPos.y
  // 只移动 section 的 transform
  // 子标签和所有内容的 transform 保持不变，通过 CSS transform 叠加自动跟随 section
  setElementPos('section', key, clamped.x, clamped.y)
  return { actualX: actualPushX, actualY: actualPushY }
}

// 移动一个 section 及其所有内部子标签（整体移动）
// section 和子标签保持相对固定的整体，一起移动，并约束在简历模板边界内
function moveSectionWithChildren(sectionEl, key, pushX, pushY) {
  tryMoveSection(sectionEl, key, pushX, pushY)
}

// 碰撞避让：根据拖动方向，将重叠的其他元素向相反方向推移
// 规则：
// - 拖动 section 时：避让对象仅为其他 section，section 整体（含子标签）同步移动，子标签绝不独立移动
// - 拖动 sub/custom 时：避让对象仅为同容器内的其他 sub/custom，不避让其他 section 或其子标签
// section 避让只做上下垂直移动，禁止左右移动
// 避让方向基于 other 相对于 dragRect 的位置：other 在下方则向下推，在上方则向上推
function applyCollisionAvoidance(draggedEl, dragKey, dragType, moveDx, moveDy, containerEl) {
  const dragRect = draggedEl.getBoundingClientRect()
  const GAP = 4

  // 确定避让对象范围
  let others = []
  if (dragType === 'section') {
    // 拖动 section：只避让其他 section
    others = getAllDragRects(dragKey, dragType, containerEl, 'section')
  } else {
    // 拖动 sub/custom：只避让同容器内的其他 sub/custom 元素
    // 不避让 section 或其他 section 内的子标签（子标签锁定在各自模块内）
    const root = containerEl || document.querySelector('.resume-modern')
    if (!root) return
    const draggedContainer = getContainerOf(draggedEl)
    const allEls = root.querySelectorAll('[data-drag-type="sub"], [data-drag-type="custom"]')
    allEls.forEach(el => {
      const key = el.getAttribute('data-drag-key')
      const type = el.getAttribute('data-drag-type')
      if (key === dragKey && type === dragType) return
      // 只处理与拖动元素在同一个容器内的元素
      if (getContainerOf(el) !== draggedContainer) return
      const rect = el.getBoundingClientRect()
      others.push({ el, key, type, rect })
    })
  }

  for (const other of others) {
    if (!rectsOverlap(dragRect, other.rect)) continue

    let pushX = 0, pushY = 0

    if (other.type === 'section') {
      // section 类型：只做垂直避让，禁止左右移动
      // 避让方向基于拖动方向（moveDy），而非相对位置：
      // - 向上拖动(moveDy<0)：被碰撞的模块向下避让（让出上方空间）
      // - 向下拖动(moveDy>0)：被碰撞的模块向上避让（让出下方空间）
      // - 无明显拖动方向(moveDy==0)：基于相对位置决定避让方向
      if (moveDy < 0) {
        // 向上拖动：other 向下避让，使 other.top > dragRect.bottom
        pushY = dragRect.bottom - other.rect.top + GAP
        if (pushY <= 0) pushY = 0
      } else if (moveDy > 0) {
        // 向下拖动：other 向上避让，使 other.bottom < dragRect.top
        pushY = -(other.rect.bottom - dragRect.top + GAP)
        if (pushY >= 0) pushY = 0
      } else {
        // 无明显方向：基于相对位置决定
        const dragCenterY = (dragRect.top + dragRect.bottom) / 2
        const otherCenterY = (other.rect.top + other.rect.bottom) / 2
        if (otherCenterY > dragCenterY) {
          pushY = dragRect.bottom - other.rect.top + GAP
          if (pushY <= 0) pushY = 0
        } else {
          pushY = -(other.rect.bottom - dragRect.top + GAP)
          if (pushY >= 0) pushY = 0
        }
      }
    } else {
      // sub/custom 类型：在父容器内做避让
      const dragCenterY = (dragRect.top + dragRect.bottom) / 2
      const otherCenterY = (other.rect.top + other.rect.bottom) / 2
      const dragCenterX = (dragRect.left + dragRect.right) / 2
      const otherCenterX = (other.rect.left + other.rect.right) / 2

      // 优先垂直避让
      if (otherCenterY !== dragCenterY) {
        if (otherCenterY > dragCenterY) {
          pushY = dragRect.bottom - other.rect.top + GAP
          if (pushY <= 0) pushY = 0
        } else {
          pushY = -(other.rect.bottom - dragRect.top + GAP)
          if (pushY >= 0) pushY = 0
        }
      }
      // 垂直方向无空间时尝试水平
      if (pushY === 0) {
        if (otherCenterX > dragCenterX) {
          pushX = dragRect.right - other.rect.left + GAP
          if (pushX <= 0) pushX = 0
        } else {
          pushX = -(other.rect.right - dragRect.left + GAP)
          if (pushX >= 0) pushX = 0
        }
      }
    }

    if (pushX === 0 && pushY === 0) continue

    if (other.type === 'section') {
      // section 整体移动（含内部子标签），约束在简历模板边界内
      // 只做垂直移动（pushX 始终为 0）
      // 子标签通过 tryMoveSection 内部同步移动，绝不独立避让
      tryMoveSection(other.el, other.key, 0, pushY)
    } else {
      // sub/custom 类型：移动后约束在父容器内
      const existingPos = getElementPos(other.type, other.key)
      let finalX = existingPos.x + pushX
      let finalY = existingPos.y + pushY
      const clamped = clampPosInContainer(other.el, other.type, other.key, finalX, finalY)

      // 检查约束后的位置是否真正有效
      const movedX = clamped.x - existingPos.x
      const movedY = clamped.y - existingPos.y

      if (movedX === 0 && movedY === 0) {
        // 主方向无空间，尝试水平避让
        if (pushY !== 0 && pushX === 0) {
          const dragCenterX = (dragRect.left + dragRect.right) / 2
          const otherCenterX = (other.rect.left + other.rect.right) / 2
          let altPushX = 0
          if (otherCenterX > dragCenterX) {
            altPushX = dragRect.right - other.rect.left + GAP
          } else {
            altPushX = -(other.rect.right - dragRect.left + GAP)
          }
          if (altPushX !== 0) {
            const altX = existingPos.x + altPushX
            const altClamped = clampPosInContainer(other.el, other.type, other.key, altX, existingPos.y)
            if (altClamped.x !== existingPos.x) {
              setElementPos(other.type, other.key, altClamped.x, existingPos.y)
            }
          }
        }
        // 水平也无空间则放弃，不移动
      } else {
        setElementPos(other.type, other.key, clamped.x, clamped.y)
      }
    }
  }
}

// 范围约束：确保拖动中的元素不会移出其父容器边界
// 使用 offsetLeft/offsetTop 逐级累加获取不受 translate 影响的基础位置
function clampToContainer(el, newX, newY) {
  const container = dragState.value.containerEl
  if (!container) return { x: newX, y: newY }
  // 逐级累加 offsetParent 链，计算元素相对于 container 的基础位置（不受 translate 影响）
  let baseLeft = 0, baseTop = 0
  let node = el
  while (node && node !== container) {
    baseLeft += node.offsetLeft
    baseTop += node.offsetTop
    node = node.offsetParent
  }
  // 如果 offsetParent 链未到 container，用 fallback
  if (node !== container) {
    const elRect = el.getBoundingClientRect()
    const containerRect = container.getBoundingClientRect()
    const oldPos = getElementPos(dragState.value.type, dragState.value.key)
    baseLeft = (elRect.left - containerRect.left) - oldPos.x
    baseTop = (elRect.top - containerRect.top) - oldPos.y
  }
  const elW = el.offsetWidth
  const elH = el.offsetHeight
  const containerW = container.clientWidth
  const containerH = container.clientHeight
  const newRelLeft = baseLeft + newX
  const newRelTop = baseTop + newY
  const clampedRelLeft = Math.max(0, Math.min(newRelLeft, containerW - elW))
  const clampedRelTop = Math.max(0, Math.min(newRelTop, containerH - elH))
  const clampedX = newX - (newRelLeft - clampedRelLeft)
  const clampedY = newY - (newRelTop - clampedRelTop)
  return { x: clampedX, y: clampedY }
}

function onDragStart(e, type, key) {
  if (!props.editMode) return
  e.preventDefault()
  e.stopPropagation()

  const existingPos = getElementPos(type, key)
  const root = document.querySelector('.resume-modern')
  const el = root?.querySelector(`[data-drag-key="${key}"][data-drag-type="${type}"]`)

  // 对于 sub 和 custom 类型，查找最近的父容器（data-sub-container 或 section）
  // 对于 section 类型，父容器为简历模板根元素 .resume-modern
  let containerEl = null
  if (type === 'sub' || type === 'custom') {
    // 先查找 data-sub-container
    containerEl = el?.closest('[data-sub-container]')
    // 如果没有找到，查找最近的 section（用于 section 内的 custom 标签）
    if (!containerEl) {
      containerEl = el?.closest('section')
    }
  } else if (type === 'section') {
    // section 的父容器是简历模板根元素
    containerEl = root
  }

  dragState.value = {
    dragging: true, type, key,
    startX: e.clientX, startY: e.clientY,
    startOffsetX: existingPos.x, startOffsetY: existingPos.y,
    el, lastDx: 0, lastDy: 0, containerEl,
  }

  document.addEventListener('mousemove', onMouseMove)
  document.addEventListener('mouseup', onMouseUp)
}

let collisionCheckPending = false

function onMouseMove(e) {
  if (!dragState.value.dragging) return
  e.preventDefault()

  const dx = e.clientX - dragState.value.startX
  const dy = e.clientY - dragState.value.startY
  let newX = dragState.value.startOffsetX + dx
  let newY = dragState.value.startOffsetY + dy

  // 范围约束：section / sub / custom 类型都不能移出各自父容器边界
  if ((dragState.value.type === 'section' || dragState.value.type === 'sub' || dragState.value.type === 'custom') && dragState.value.el) {
    const clamped = clampToContainer(dragState.value.el, newX, newY)
    newX = clamped.x
    newY = clamped.y
  }

  setElementPos(dragState.value.type, dragState.value.key, newX, newY)

  const frameDx = dx - dragState.value.lastDx
  const frameDy = dy - dragState.value.lastDy
  dragState.value.lastDx = dx
  dragState.value.lastDy = dy

  if (!collisionCheckPending) {
    collisionCheckPending = true
    requestAnimationFrame(() => {
      collisionCheckPending = false
      if (dragState.value.dragging && dragState.value.el) {
        nextTick(() => {
          if (dragState.value.dragging && dragState.value.el) {
            // 碰撞检测范围：
            // - section 类型：全局检测，但只作用于其他 section（scope='section'）
            // - sub/custom 类型：只在父容器内检测
            const searchRoot = dragState.value.containerEl || null
            applyCollisionAvoidance(dragState.value.el, dragState.value.key, dragState.value.type, frameDx, frameDy, searchRoot)
          }
        })
      }
    })
  }
}

function onMouseUp() {
  dragState.value.dragging = false
  dragState.value.el = null
  dragState.value.containerEl = null
  document.removeEventListener('mousemove', onMouseMove)
  document.removeEventListener('mouseup', onMouseUp)
}

// ========== Resize 逻辑 ==========
const resizeState = ref({
  resizing: false, type: '', key: '', startX: 0, startY: 0, startW: 0, startH: 0, el: null,
})

function getElementSize(type, key, fallbackW, fallbackH) {
  if (type === 'section') {
    const s = props.data.sectionSizes?.[key]; return { w: s?.w || fallbackW, h: s?.h || fallbackH }
  } else if (type === 'field') {
    const s = props.data.personalFieldSizes?.[key]; return { w: s?.w || fallbackW, h: s?.h || fallbackH }
  } else if (type === 'custom') {
    const s = props.data.customFieldSizes?.[key]; return { w: s?.w || fallbackW, h: s?.h || fallbackH }
  } else if (type === 'sub') {
    const s = props.data.subFieldSizes?.[key]; return { w: s?.w || fallbackW, h: s?.h || fallbackH }
  }
  return { w: fallbackW, h: fallbackH }
}

function setElementSize(type, key, w, h) {
  if (type === 'section') {
    if (!props.data.sectionSizes) props.data.sectionSizes = {}
    props.data.sectionSizes[key] = { w, h }
  } else if (type === 'field') {
    if (!props.data.personalFieldSizes) props.data.personalFieldSizes = {}
    props.data.personalFieldSizes[key] = { w, h }
  } else if (type === 'custom') {
    if (!props.data.customFieldSizes) props.data.customFieldSizes = {}
    props.data.customFieldSizes[key] = { w, h }
  } else if (type === 'sub') {
    if (!props.data.subFieldSizes) props.data.subFieldSizes = {}
    props.data.subFieldSizes[key] = { w, h }
  }
}

function onResizeStart(e, type, key) {
  if (!props.editMode) return
  e.preventDefault()
  e.stopPropagation()
  const root = document.querySelector('.resume-modern')
  const el = root?.querySelector(`[data-drag-key="${key}"][data-drag-type="${type}"]`)
  if (!el) return
  const rect = el.getBoundingClientRect()
  const existing = getElementSize(type, key, rect.width, rect.height)
  resizeState.value = { resizing: true, type, key, startX: e.clientX, startY: e.clientY, startW: existing.w, startH: existing.h, el }
  document.addEventListener('mousemove', onResizeMove)
  document.addEventListener('mouseup', onResizeEnd)
}

function onResizeMove(e) {
  if (!resizeState.value.resizing) return
  e.preventDefault()
  const dx = e.clientX - resizeState.value.startX
  const dy = e.clientY - resizeState.value.startY
  const newW = Math.max(60, resizeState.value.startW + dx)
  const newH = Math.max(20, resizeState.value.startH + dy)
  setElementSize(resizeState.value.type, resizeState.value.key, newW, newH)
}

function onResizeEnd() {
  resizeState.value.resizing = false
  resizeState.value.el = null
  document.removeEventListener('mousemove', onResizeMove)
  document.removeEventListener('mouseup', onResizeEnd)
}

onUnmounted(() => {
  document.removeEventListener('mousemove', onMouseMove)
  document.removeEventListener('mouseup', onMouseUp)
  document.removeEventListener('mousemove', onResizeMove)
  document.removeEventListener('mouseup', onResizeEnd)
})
</script>

<style scoped>
.resume-modern {
  font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
  font-size: 14px;
  color: #333;
  line-height: 1.6;
  background: #fff;
  width: 794px;
  min-height: 1123px;
}

.rm-header {
  background: linear-gradient(135deg, var(--theme) 0%, rgba(0, 0, 0, 0.3) 100%), var(--theme);
  color: #fff;
  padding: 32px 40px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
}

.rm-header-edit { overflow: visible; }

.rm-avatar {
  width: 85px;
  height: 119px;
  border-radius: 6px;
  overflow: hidden;
  border: 2px solid rgba(255, 255, 255, 0.4);
  flex-shrink: 0;
}

.rm-avatar img { width: 100%; height: 100%; object-fit: cover; }

.rm-name { font-size: 30px; font-weight: 800; color: #fff; margin-bottom: 4px; }
.rm-intention { font-size: 15px; color: rgba(255, 255, 255, 0.85); }
.rm-contact { text-align: right; font-size: 12px; color: rgba(255, 255, 255, 0.9); }
.rm-contact-item { margin: 3px 0; }

.rm-ci-icon {
  display: inline-block;
  background: rgba(255, 255, 255, 0.2);
  padding: 1px 6px;
  border-radius: 3px;
  margin-right: 6px;
  font-size: 11px;
}

.rm-body { padding: 24px 40px; }
.rm-section { margin-bottom: 20px; }

.rm-section-header { display: flex; align-items: center; gap: 8px; margin-bottom: 12px; }
.rm-section-bar { width: 4px; height: 16px; background: var(--theme); border-radius: 2px; }
.rm-section-title { font-size: 16px; font-weight: 700; color: #1a1a2e; }

.rm-timeline-item { display: flex; gap: 12px; margin-bottom: 14px; position: relative; }
.rm-timeline-item::before {
  content: '';
  position: absolute;
  left: 5px;
  top: 18px;
  bottom: -14px;
  width: 2px;
  background: #e8ecf1;
}
.rm-timeline-item:last-child::before { display: none; }

.rm-sub-container {
  border: 1px dashed transparent;
  border-radius: 4px;
  transition: border-color 0.2s;
  overflow: hidden;
}
.rm-sub-container:hover { border-color: rgba(0, 0, 0, 0.15); }

.rm-dot {
  width: 12px; height: 12px; border-radius: 50%; background: var(--theme);
  border: 2px solid #fff; box-shadow: 0 0 0 2px var(--theme);
  flex-shrink: 0; margin-top: 4px; z-index: 1;
}

.rm-timeline-content { flex: 1; }
.rm-item-header { display: flex; justify-content: space-between; align-items: baseline; }
.rm-item-title { font-size: 14px; font-weight: 600; color: #1a1a2e; }
.rm-item-date { font-size: 12px; color: #999; }
.rm-item-sub { font-size: 13px; color: #555; margin: 2px 0; }
.rm-item-role { font-size: 12px; color: var(--theme); font-weight: 500; }
.rm-item-meta { display: flex; gap: 10px; margin: 3px 0; }
.rm-meta-tag { font-size: 12px; color: #666; background: #f5f7fa; padding: 1px 8px; border-radius: 10px; }

.rm-tech-stack {
  font-size: 12px; color: var(--theme); background: transparent;
  border: 1px solid var(--theme); display: inline-block;
  padding: 2px 8px; border-radius: 4px; margin: 3px 0;
}

.rm-text { font-size: 13px; color: #555; line-height: 1.7; word-wrap: break-word; overflow-wrap: break-word; }
.rm-text-sm { font-size: 12px; color: #666; margin: 2px 0; line-height: 1.6; word-wrap: break-word; overflow-wrap: break-word; }
.rm-highlight { color: var(--theme); font-weight: 500; }
.rm-list { list-style: disc; padding-left: 18px; margin: 4px 0; }
.rm-list ul { list-style: disc; padding-left: 18px; margin: 0; }

.rm-two-col { display: flex; gap: 30px; }
.rm-two-col .rm-section { flex: 1; }

.rm-skills { display: block; }
.rm-skill-item { display: block; padding: 2px 0; font-size: 13px; line-height: 1.8; }
.rm-skill-name { font-weight: 600; color: #1a1a2e; }

.rm-award-item { display: flex; justify-content: space-between; padding: 4px 0; border-bottom: 1px dashed #e8ecf1; }
.rm-award-name { font-size: 13px; color: #333; font-weight: 500; }
.rm-award-date { font-size: 12px; color: #999; }

.rm-drag-section {
  cursor: move;
  border: 2px dashed transparent;
  border-radius: 4px;
  transition: border-color 0.2s;
  position: relative;
  user-select: none;
}
.rm-drag-section:hover { border-color: var(--theme); }
.rm-drag-section:active { opacity: 0.85; }

.rm-drag-el { cursor: move; user-select: none; }
.rm-drag-field {
  border: 1px dashed transparent;
  border-radius: 4px;
  transition: border-color 0.2s;
  position: relative;
}
.rm-drag-field:hover { border-color: rgba(255, 255, 255, 0.6); }
.rm-drag-el:active { opacity: 0.85; }

.rm-resize-handle { position: absolute; z-index: 10; }
.rm-resize-se {
  bottom: -2px; right: -2px; width: 12px; height: 12px;
  cursor: se-resize;
  border-right: 2px solid var(--theme);
  border-bottom: 2px solid var(--theme);
  border-radius: 0 0 4px 0;
  opacity: 0;
  transition: opacity 0.2s;
}
.rm-drag-section:hover .rm-resize-se,
.rm-drag-field:hover .rm-resize-se { opacity: 1; }
</style>