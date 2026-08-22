import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

/**
 * 简历数据 Store
 *
 * 标准化 JSON 数据结构，驱动所有模板渲染。
 * 数据自动持久化至 localStorage。
 */

// ========== 默认数据 ==========

function createDefaultResume() {
  return {
    templateId: 'modern',
    themeColor: '#4361ee',
    personal: {
      name: '张三',
      avatar: '',
      phone: '138-0000-0000',
      email: 'zhangsan@example.com',
      wechat: '',
      github: '',
      blog: '',
      jobIntention: 'Python 后端开发工程师',
      gpa: '3.8/4.0',
      rank: '前10%',
      selfEvaluation: '5年Python后端开发经验，熟悉Django/Flask框架，具备微服务架构设计能力。擅长高并发系统优化，有丰富的团队协作和项目管理经验。',
    },
    education: [
      {
        id: Date.now(),
        school: '某某大学',
        degree: '硕士',
        major: '计算机科学与技术',
        gpa: '3.8/4.0',
        rank: '前10%',
        courses: '数据结构、算法设计、操作系统、计算机网络、数据库系统',
        startDate: '2019-09',
        endDate: '2022-06',
      },
    ],
    workExperience: [
      {
        id: Date.now() + 1,
        company: '某科技有限公司',
        department: '技术部',
        position: '后端开发工程师',
        startDate: '2022-07',
        endDate: '至今',
        type: '工作',
        description: [
          '负责核心业务系统的架构设计和开发，支撑日均千万级请求',
          '主导微服务化改造，将单体应用拆分为12个微服务，系统可用性提升至99.99%',
          '设计并实现高可用消息队列方案，消息处理延迟降低60%',
        ],
      },
    ],
    projects: [
      {
        id: Date.now() + 2,
        name: '分布式任务调度平台',
        role: '核心开发',
        techStack: 'Python, Django, Celery, Redis, Docker',
        description: '面向企业内部的分布式任务调度平台，支持定时任务、工作流编排和资源监控。',
        achievements: '支撑200+业务线、日均执行50万+任务，任务成功率99.95%',
      },
    ],
    awards: [
      {
        id: Date.now() + 3,
        name: '优秀员工奖',
        organization: '某科技有限公司',
        level: '公司级',
        category: '工作',
        date: '2023-12',
      },
    ],
    skills: [
      { id: 1, name: 'Python' },
      { id: 2, name: 'Django' },
      { id: 3, name: 'MySQL' },
      { id: 4, name: 'Redis' },
      { id: 5, name: 'Docker' },
      { id: 6, name: 'Linux' },
    ],
  }
}

// ========== Store 定义 ==========

export const useResumeStore = defineStore('resume', () => {
  const STORAGE_KEY = 'boss-resume-data'
  const CUSTOM_TPL_KEY = 'boss-resume-custom-templates'

  // 从 localStorage 恢复数据
  function loadFromStorage() {
    try {
      const saved = localStorage.getItem(STORAGE_KEY)
      if (saved) {
        return JSON.parse(saved)
      }
    } catch (e) {
      console.warn('[ResumeStore] Failed to load from localStorage:', e)
    }
    return null
  }

  // 从 localStorage 恢复自定义模板
  function loadCustomTemplates() {
    try {
      const saved = localStorage.getItem(CUSTOM_TPL_KEY)
      if (saved) {
        return JSON.parse(saved)
      }
    } catch (e) {
      console.warn('[ResumeStore] Failed to load custom templates:', e)
    }
    return []
  }

  const data = ref(loadFromStorage() || createDefaultResume())
  const customTemplates = ref(loadCustomTemplates())

  // 自动持久化到 localStorage
  watch(
    data,
    (newVal) => {
      try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(newVal))
      } catch (e) {
        console.warn('[ResumeStore] Failed to save to localStorage:', e)
      }
    },
    { deep: true }
  )

  // 自定义模板持久化
  watch(
    customTemplates,
    (newVal) => {
      try {
        localStorage.setItem(CUSTOM_TPL_KEY, JSON.stringify(newVal))
      } catch (e) {
        console.warn('[ResumeStore] Failed to save custom templates:', e)
      }
    },
    { deep: true }
  )

  // ========== Actions ==========

  function updatePersonal(field, value) {
    data.value.personal[field] = value
  }

  function addEducation() {
    data.value.education.push({
      id: Date.now(),
      school: '',
      degree: '',
      major: '',
      gpa: '',
      rank: '',
      courses: '',
      startDate: '',
      endDate: '',
    })
  }

  function removeEducation(id) {
    data.value.education = data.value.education.filter((e) => e.id !== id)
  }

  function addWork() {
    data.value.workExperience.push({
      id: Date.now(),
      company: '',
      department: '',
      position: '',
      startDate: '',
      endDate: '',
      type: '工作',
      description: [''],
    })
  }

  function removeWork(id) {
    data.value.workExperience = data.value.workExperience.filter((w) => w.id !== id)
  }

  function addProject() {
    data.value.projects.push({
      id: Date.now(),
      name: '',
      role: '',
      techStack: '',
      description: '',
      achievements: '',
    })
  }

  function removeProject(id) {
    data.value.projects = data.value.projects.filter((p) => p.id !== id)
  }

  function addAward() {
    data.value.awards.push({
      id: Date.now(),
      name: '',
      organization: '',
      level: '',
      category: '',
      date: '',
    })
  }

  function removeAward(id) {
    data.value.awards = data.value.awards.filter((a) => a.id !== id)
  }

  function addSkill() {
    data.value.skills.push({
      id: Date.now(),
      name: '',
    })
  }

  function removeSkill(id) {
    data.value.skills = data.value.skills.filter((s) => s.id !== id)
  }

  function setTemplate(templateId) {
    data.value.templateId = templateId
  }

  function setThemeColor(color) {
    data.value.themeColor = color
  }

  function setAvatar(base64) {
    data.value.personal.avatar = base64
  }

  function removeAvatar() {
    data.value.personal.avatar = ''
  }

  // ========== 自定义模板管理 ==========

  function addCustomTemplate(name, html) {
    const id = 'custom_' + Date.now()
    customTemplates.value.push({
      id,
      name: name || '自定义模板',
      html,
      isCustom: true,
      createTime: new Date().toISOString(),
    })
    return id
  }

  function removeCustomTemplate(id) {
    customTemplates.value = customTemplates.value.filter((t) => t.id !== id)
    // 如果当前选中的是被删除的自定义模板，回退到 modern
    if (data.value.templateId === id) {
      data.value.templateId = 'modern'
    }
  }

  function importData(jsonString) {
    const parsed = JSON.parse(jsonString)
    data.value = parsed
  }

  // ========== 从后端解析数据加载 ==========

  function loadFromParsedData(parsed) {
    // 保留当前模板和主题色，用解析数据填充内容
    const currentTemplate = data.value.templateId
    const currentColor = data.value.themeColor
    const currentAvatar = data.value.personal.avatar

    data.value = {
      templateId: parsed.templateId || currentTemplate,
      themeColor: parsed.themeColor || currentColor,
      personal: {
        ...data.value.personal,
        ...parsed.personal,
        // 保留已有头像，解析数据一般没有头像
        avatar: parsed.personal?.avatar || currentAvatar,
      },
      education: parsed.education?.length ? parsed.education : [],
      workExperience: parsed.workExperience?.length ? parsed.workExperience : [],
      projects: parsed.projects?.length ? parsed.projects : [],
      awards: parsed.awards?.length ? parsed.awards : [],
      skills: parsed.skills?.length ? parsed.skills.map(s => ({ id: s.id || Date.now() + Math.random(), name: s.name || '' })) : [],
    }
  }

  function exportData() {
    return JSON.stringify(data.value, null, 2)
  }

  function resetData() {
    data.value = createDefaultResume()
  }

  return {
    data,
    customTemplates,
    updatePersonal,
    addEducation,
    removeEducation,
    addWork,
    removeWork,
    addProject,
    removeProject,
    addAward,
    removeAward,
    addSkill,
    removeSkill,
    setTemplate,
    setThemeColor,
    setAvatar,
    removeAvatar,
    addCustomTemplate,
    removeCustomTemplate,
    importData,
    loadFromParsedData,
    exportData,
    resetData,
  }
})
