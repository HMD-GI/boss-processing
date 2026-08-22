<template>
  <div class="resume-editor">
    <!-- 顶部工具栏 -->
    <div class="re-toolbar">
      <div class="re-toolbar-left">
        <el-button type="primary" @click="showGallery = true">
          <el-icon><Grid /></el-icon>
          选择模板
        </el-button>

        <div class="re-current-tpl">
          <span class="re-tpl-label">当前：</span>
          <span class="re-tpl-name">{{ currentTemplateName }}</span>
        </div>

        <div class="re-color-picker">
          <span class="re-color-label">主题色</span>
          <div
            v-for="c in presetColors"
            :key="c"
            class="re-color-dot"
            :class="{ active: store.data.themeColor === c }"
            :style="{ background: c }"
            @click="store.setThemeColor(c)"
          ></div>
          <el-color-picker v-model="store.data.themeColor" size="small" />
        </div>
      </div>

      <div class="re-toolbar-right">
        <el-button type="success" @click="triggerResumeUpload" :loading="parsing">
          <el-icon><Document /></el-icon>
          上传简历
        </el-button>
        <el-button @click="handleImport">
          <el-icon><Upload /></el-icon>
          导入JSON
        </el-button>
        <el-button @click="handleExport">
          <el-icon><Download /></el-icon>
          导出JSON
        </el-button>
        <el-button @click="handleReset" type="danger" plain>
          <el-icon><RefreshLeft /></el-icon>
          重置
        </el-button>
        <el-button type="primary" @click="exportPDF" :loading="exporting">
          <el-icon><Printer /></el-icon>
          导出PDF
        </el-button>
      </div>
    </div>

    <!-- 主体区域 -->
    <div class="re-main">
      <!-- 左侧：表单编辑 -->
      <div class="re-editor-panel">
        <el-tabs v-model="activeTab" class="re-tabs">
          <!-- 个人信息 -->
          <el-tab-pane label="个人信息" name="personal">
            <div class="re-form-section">
              <!-- 头像上传 -->
              <div class="re-avatar-section">
                <div class="re-avatar-label">个人照片</div>
                <div class="re-avatar-upload">
                  <div class="re-avatar-preview" @click="triggerAvatarUpload">
                    <img v-if="store.data.personal.avatar" :src="store.data.personal.avatar" alt="avatar" />
                    <div v-else class="re-avatar-placeholder">
                      <el-icon :size="24"><Plus /></el-icon>
                      <span>上传照片</span>
                    </div>
                  </div>
                  <div class="re-avatar-actions">
                    <el-button size="small" @click="triggerAvatarUpload">
                      <el-icon><Upload /></el-icon>
                      {{ store.data.personal.avatar ? '更换' : '上传' }}
                    </el-button>
                    <el-button v-if="store.data.personal.avatar" size="small" type="danger" plain @click="store.removeAvatar()">
                      移除
                    </el-button>
                  </div>
                  <p class="re-avatar-hint">建议上传一寸或二寸证件照（长方形），将显示在简历模板中</p>
                </div>
                <input ref="avatarInput" type="file" accept="image/*" style="display:none" @change="onAvatarSelected" />
              </div>

              <el-divider />

              <el-form label-width="80px" label-position="left" size="default">
                <el-form-item label="姓名">
                  <el-input v-model="store.data.personal.name" placeholder="请输入姓名" />
                </el-form-item>
                <el-form-item label="求职意向">
                  <el-input v-model="store.data.personal.jobIntention" placeholder="如：Python后端开发工程师" />
                </el-form-item>
                <el-form-item label="手机">
                  <el-input v-model="store.data.personal.phone" placeholder="请输入手机号" />
                </el-form-item>
                <el-form-item label="邮箱">
                  <el-input v-model="store.data.personal.email" placeholder="请输入邮箱" />
                </el-form-item>
                <el-form-item label="微信">
                  <el-input v-model="store.data.personal.wechat" placeholder="请输入微信号" />
                </el-form-item>
                <el-form-item label="GitHub">
                  <el-input v-model="store.data.personal.github" placeholder="如：github.com/username" />
                </el-form-item>
                <el-form-item label="博客">
                  <el-input v-model="store.data.personal.blog" placeholder="如：blog.example.com" />
                </el-form-item>
                <el-form-item label="GPA">
                  <el-input v-model="store.data.personal.gpa" placeholder="如：3.8/4.0" />
                </el-form-item>
                <el-form-item label="排名">
                  <el-input v-model="store.data.personal.rank" placeholder="如：前10%" />
                </el-form-item>
                <el-form-item label="自我评价">
                  <el-input
                    v-model="store.data.personal.selfEvaluation"
                    type="textarea"
                    :rows="4"
                    placeholder="请输入自我评价"
                  />
                </el-form-item>
              </el-form>

              <el-divider />

              <h3 class="re-sub-title">教育经历</h3>
              <div v-for="(edu, idx) in store.data.education" :key="edu.id" class="re-card">
                <div class="re-card-header">
                  <span class="re-card-title">教育经历 {{ idx + 1 }}</span>
                  <el-button type="danger" text size="small" @click="store.removeEducation(edu.id)">
                    删除
                  </el-button>
                </div>
                <el-form label-width="70px" label-position="left" size="default">
                  <el-row :gutter="12">
                    <el-col :span="12">
                      <el-form-item label="学校">
                        <el-input v-model="edu.school" placeholder="学校名称" />
                      </el-form-item>
                    </el-col>
                    <el-col :span="12">
                      <el-form-item label="专业">
                        <el-input v-model="edu.major" placeholder="专业名称" />
                      </el-form-item>
                    </el-col>
                  </el-row>
                  <el-row :gutter="12">
                    <el-col :span="8">
                      <el-form-item label="学位">
                        <el-select v-model="edu.degree" placeholder="学位" style="width: 100%">
                          <el-option label="大专" value="大专" />
                          <el-option label="本科" value="本科" />
                          <el-option label="硕士" value="硕士" />
                          <el-option label="博士" value="博士" />
                        </el-select>
                      </el-form-item>
                    </el-col>
                    <el-col :span="8">
                      <el-form-item label="GPA">
                        <el-input v-model="edu.gpa" placeholder="GPA" />
                      </el-form-item>
                    </el-col>
                    <el-col :span="8">
                      <el-form-item label="排名">
                        <el-input v-model="edu.rank" placeholder="排名" />
                      </el-form-item>
                    </el-col>
                  </el-row>
                  <el-row :gutter="12">
                    <el-col :span="12">
                      <el-form-item label="开始">
                        <el-date-picker v-model="edu.startDate" type="month" format="YYYY-MM" value-format="YYYY-MM" placeholder="开始时间" style="width: 100%" />
                      </el-form-item>
                    </el-col>
                    <el-col :span="12">
                      <el-form-item label="结束">
                        <el-date-picker v-model="edu.endDate" type="month" format="YYYY-MM" value-format="YYYY-MM" placeholder="结束时间" style="width: 100%" />
                      </el-form-item>
                    </el-col>
                  </el-row>
                  <el-form-item label="主修课程">
                    <el-input v-model="edu.courses" placeholder="多个课程用逗号分隔" />
                  </el-form-item>
                </el-form>
              </div>
              <el-button type="primary" plain class="re-add-btn" @click="store.addEducation">
                + 添加教育经历
              </el-button>
            </div>
          </el-tab-pane>

          <!-- 工作经历 -->
          <el-tab-pane label="工作经历" name="work">
            <div class="re-form-section">
              <div v-for="(work, idx) in store.data.workExperience" :key="work.id" class="re-card">
                <div class="re-card-header">
                  <span class="re-card-title">工作经历 {{ idx + 1 }}</span>
                  <el-button type="danger" text size="small" @click="store.removeWork(work.id)">
                    删除
                  </el-button>
                </div>
                <el-form label-width="70px" label-position="left" size="default">
                  <el-row :gutter="12">
                    <el-col :span="12">
                      <el-form-item label="公司">
                        <el-input v-model="work.company" placeholder="公司名称" />
                      </el-form-item>
                    </el-col>
                    <el-col :span="12">
                      <el-form-item label="部门">
                        <el-input v-model="work.department" placeholder="部门名称" />
                      </el-form-item>
                    </el-col>
                  </el-row>
                  <el-row :gutter="12">
                    <el-col :span="8">
                      <el-form-item label="职位">
                        <el-input v-model="work.position" placeholder="职位" />
                      </el-form-item>
                    </el-col>
                    <el-col :span="8">
                      <el-form-item label="开始">
                        <el-date-picker v-model="work.startDate" type="month" format="YYYY-MM" value-format="YYYY-MM" placeholder="开始" style="width: 100%" />
                      </el-form-item>
                    </el-col>
                    <el-col :span="8">
                      <el-form-item label="结束">
                        <el-input v-model="work.endDate" placeholder="如：2024-01 或 至今" />
                      </el-form-item>
                    </el-col>
                  </el-row>
                  <el-form-item label="工作内容">
                    <div class="re-desc-list">
                      <div v-for="(desc, di) in work.description" :key="di" class="re-desc-row">
                        <el-input
                          v-model="work.description[di]"
                          type="textarea"
                          :rows="2"
                          :placeholder="`工作内容 ${di + 1}`"
                        />
                        <el-button
                          v-if="work.description.length > 1"
                          type="danger"
                          text
                          size="small"
                          @click="work.description.splice(di, 1)"
                        >
                          删除
                        </el-button>
                      </div>
                      <el-button text type="primary" size="small" @click="work.description.push('')">
                        + 添加内容
                      </el-button>
                    </div>
                  </el-form-item>
                </el-form>
              </div>
              <el-button type="primary" plain class="re-add-btn" @click="store.addWork">
                + 添加工作经历
              </el-button>
            </div>
          </el-tab-pane>

          <!-- 项目经历 -->
          <el-tab-pane label="项目经历" name="project">
            <div class="re-form-section">
              <div v-for="(proj, idx) in store.data.projects" :key="proj.id" class="re-card">
                <div class="re-card-header">
                  <span class="re-card-title">项目经历 {{ idx + 1 }}</span>
                  <el-button type="danger" text size="small" @click="store.removeProject(proj.id)">
                    删除
                  </el-button>
                </div>
                <el-form label-width="70px" label-position="left" size="default">
                  <el-form-item label="项目名称">
                    <el-input v-model="proj.name" placeholder="项目名称" />
                  </el-form-item>
                  <el-row :gutter="12">
                    <el-col :span="12">
                      <el-form-item label="角色">
                        <el-input v-model="proj.role" placeholder="如：核心开发" />
                      </el-form-item>
                    </el-col>
                    <el-col :span="12">
                      <el-form-item label="技术栈">
                        <el-input v-model="proj.techStack" placeholder="如：Python, Django, Redis" />
                      </el-form-item>
                    </el-col>
                  </el-row>
                  <el-form-item label="项目描述">
                    <el-input v-model="proj.description" type="textarea" :rows="3" placeholder="项目描述" />
                  </el-form-item>
                  <el-form-item label="项目成果">
                    <el-input v-model="proj.achievements" type="textarea" :rows="2" placeholder="项目成果" />
                  </el-form-item>
                </el-form>
              </div>
              <el-button type="primary" plain class="re-add-btn" @click="store.addProject">
                + 添加项目经历
              </el-button>
            </div>
          </el-tab-pane>

          <!-- 技能与奖项 -->
          <el-tab-pane label="技能与奖项" name="skills">
            <div class="re-form-section">
              <h3 class="re-sub-title">专业技能</h3>
              <div v-for="skill in store.data.skills" :key="skill.id" class="re-skill-row">
                <el-input v-model="skill.name" placeholder="请输入技能，如：Python / 熟悉Django框架" style="width: 80%" />
                <el-button type="danger" text @click="store.removeSkill(skill.id)">
                  删除
                </el-button>
              </div>
              <el-button type="primary" plain size="small" class="re-add-btn" @click="store.addSkill">
                + 添加技能
              </el-button>

              <el-divider />

              <h3 class="re-sub-title">奖项荣誉</h3>
              <div v-for="award in store.data.awards" :key="award.id" class="re-card">
                <div class="re-card-header">
                  <el-button type="danger" text size="small" @click="store.removeAward(award.id)">
                    删除
                  </el-button>
                </div>
                <el-form label-width="70px" label-position="left" size="default">
                  <el-row :gutter="12">
                    <el-col :span="12">
                      <el-form-item label="奖项名">
                        <el-input v-model="award.name" placeholder="奖项名称" />
                      </el-form-item>
                    </el-col>
                    <el-col :span="12">
                      <el-form-item label="机构">
                        <el-input v-model="award.organization" placeholder="颁发机构" />
                      </el-form-item>
                    </el-col>
                  </el-row>
                  <el-row :gutter="12">
                    <el-col :span="12">
                      <el-form-item label="等级">
                        <el-input v-model="award.level" placeholder="如：国家级" />
                      </el-form-item>
                    </el-col>
                    <el-col :span="12">
                      <el-form-item label="时间">
                        <el-date-picker v-model="award.date" type="month" format="YYYY-MM" value-format="YYYY-MM" placeholder="获奖时间" style="width: 100%" />
                      </el-form-item>
                    </el-col>
                  </el-row>
                </el-form>
              </div>
              <el-button type="primary" plain class="re-add-btn" @click="store.addAward">
                + 添加奖项
              </el-button>
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>

      <!-- 右侧：实时预览 -->
      <div class="re-preview-panel">
        <div class="re-preview-header">
          <span class="re-preview-title">实时预览</span>
          <div class="re-preview-zoom">
            <el-button-group>
              <el-button size="small" @click="zoomOut">
                <el-icon><ZoomOut /></el-icon>
              </el-button>
              <span class="re-zoom-value">{{ Math.round(zoom * 100) }}%</span>
              <el-button size="small" @click="zoomIn">
                <el-icon><ZoomIn /></el-icon>
              </el-button>
            </el-button-group>
          </div>
        </div>
        <div class="re-preview-scroll">
          <div class="re-preview-canvas" :style="{ transform: `scale(${zoom})` }">
            <div id="resume-preview" class="resume-preview-wrapper">
              <!-- 内置模板（含颜色变体） -->
              <component
                v-if="currentTemplateComponent"
                :is="currentTemplateComponent"
                :data="store.data"
                :color="store.data.themeColor"
              />
              <!-- 自定义模板 -->
              <div
                v-else-if="currentCustomTemplate"
                class="re-custom-render"
                v-html="currentCustomTemplate.html"
              ></div>
              <!-- 回退 -->
              <ModernTemplate
                v-else
                :data="store.data"
                :color="store.data.themeColor"
              />
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 模板选择器 -->
    <TemplateGallery
      v-model="showGallery"
      :current-template-id="store.data.templateId"
      :preview-data="store.data"
      :custom-templates="store.customTemplates"
      @select="onSelectTemplate"
      @upload-template="showUploadDialog = true"
      @remove-custom="store.removeCustomTemplate"
    />

    <!-- 自定义模板上传弹窗 -->
    <el-dialog v-model="showUploadDialog" title="上传自定义模板" width="600px">
      <el-form label-width="100px">
        <el-form-item label="模板名称">
          <el-input v-model="uploadForm.name" placeholder="如：我的自定义模板" />
        </el-form-item>
        <el-form-item label="模板文件">
          <el-upload
            ref="uploadRef"
            :auto-upload="false"
            accept=".html,.htm"
            :limit="1"
            :on-change="onUploadFileChange"
            :on-exceed="onUploadExceed"
          >
            <el-button>
              <el-icon><Upload /></el-icon>
              选择HTML文件
            </el-button>
            <template #tip>
              <div class="el-upload__tip">
                上传一个HTML文件作为自定义简历模板。支持完整HTML简历页面。
                <el-link type="primary" @click="downloadSampleTemplate">下载示例模板</el-link>
              </div>
            </template>
          </el-upload>
        </el-form-item>
        <el-form-item label="模板预览">
          <div class="re-upload-preview" v-if="uploadForm.html">
            <div class="re-upload-preview-inner" v-html="uploadForm.html"></div>
          </div>
          <div v-else class="re-upload-empty">
            <el-icon :size="32" color="#ccc"><DocumentCopy /></el-icon>
            <p>选择文件后预览</p>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showUploadDialog = false">取消</el-button>
        <el-button type="primary" @click="confirmUploadTemplate" :disabled="!uploadForm.html">
          确认上传
        </el-button>
      </template>
    </el-dialog>

    <!-- 隐藏的文件上传 -->
    <input ref="fileInput" type="file" accept=".json" style="display: none" @change="onFileSelected" />
    <input ref="resumeInput" type="file" accept=".pdf" style="display: none" @change="onResumeSelected" />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import {
  Upload, Download, RefreshLeft, Printer,
  ZoomIn, ZoomOut, Grid, Plus, DocumentCopy, Document,
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useResumeStore } from '../stores/resume'
import SimpleTemplate from '../components/resume/SimpleTemplate.vue'
import ModernTemplate from '../components/resume/ModernTemplate.vue'
import SidebarTemplate from '../components/resume/SidebarTemplate.vue'
import ProfessionalTemplate from '../components/resume/ProfessionalTemplate.vue'
import CreativeTemplate from '../components/resume/CreativeTemplate.vue'
import ElegantTemplate from '../components/resume/ElegantTemplate.vue'
import ClassicTemplate from '../components/resume/ClassicTemplate.vue'
import DarkSidebarTemplate from '../components/resume/DarkSidebarTemplate.vue'
import MinimalTemplate from '../components/resume/MinimalTemplate.vue'
import BannerTemplate from '../components/resume/BannerTemplate.vue'
import HeaderTemplate from '../components/resume/HeaderTemplate.vue'
import SplitTemplate from '../components/resume/SplitTemplate.vue'
import TimelineTemplate from '../components/resume/TimelineTemplate.vue'
import CardTemplate from '../components/resume/CardTemplate.vue'
import TwoColumnTemplate from '../components/resume/TwoColumnTemplate.vue'
import TemplateGallery from '../components/resume/TemplateGallery.vue'

const store = useResumeStore()
const activeTab = ref('personal')
const zoom = ref(0.75)
const exporting = ref(false)
const fileInput = ref(null)
const avatarInput = ref(null)
const resumeInput = ref(null)
const showGallery = ref(false)
const showUploadDialog = ref(false)
const uploadRef = ref(null)
const uploadForm = ref({ name: '', html: '' })
const parsing = ref(false)

const presetColors = [
  '#4361ee', '#3a0ca3', '#2d6a4f', '#b5179e',
  '#f77f00', '#d62828', '#0f4c75', '#480ca8',
]

// 当前模板名称
const templateNameMap = {
  simple: '经典简约',
  modern: '现代简约',
  sidebar: '侧边栏风格',
  professional: '商务专业',
  creative: '创意风格',
  elegant: '雅致风格',
}

const currentTemplateName = computed(() => {
  if (templateNameMap[store.data.templateId]) {
    return templateNameMap[store.data.templateId]
  }
  const custom = store.customTemplates.find((t) => t.id === store.data.templateId)
  return custom ? custom.name : '未知模板'
})

// 当前自定义模板
const currentCustomTemplate = computed(() => {
  return store.customTemplates.find((t) => t.id === store.data.templateId)
})

// 当前内置模板组件（支持颜色变体：通过 baseId 查找组件）
const templateComponentMap = {
  simple: SimpleTemplate, modern: ModernTemplate, sidebar: SidebarTemplate,
  professional: ProfessionalTemplate, creative: CreativeTemplate, elegant: ElegantTemplate,
  classic: ClassicTemplate, darksidebar: DarkSidebarTemplate, minimal: MinimalTemplate,
  banner: BannerTemplate, header: HeaderTemplate, split: SplitTemplate,
  timeline: TimelineTemplate, card: CardTemplate, twocol: TwoColumnTemplate,
}
// 颜色变体 ID → 基础布局 ID 映射
const variantToBase = {
  'modern-dark': 'modern', 'modern-blue': 'modern',
  'sidebar-deep': 'sidebar', 'sidebar-slate': 'sidebar',
  'banner-teal': 'banner', 'banner-blue': 'banner',
  'header-skyblue': 'header', 'header-blue': 'header',
  'darksidebar-dark': 'darksidebar', 'darksidebar-navy': 'darksidebar',
  'classic-teal': 'classic', 'classic-navy': 'classic',
  'split-blue': 'split', 'split-navy': 'split',
  'timeline-blue': 'timeline', 'timeline-teal': 'timeline',
  'card-warm': 'card', 'card-blue': 'card',
  'twocol-blue': 'twocol', 'twocol-teal': 'twocol',
  'simple-red': 'simple', 'simple-green': 'simple',
  'elegant-dark': 'elegant', 'minimal-dark': 'minimal',
  'professional-blue': 'professional', 'creative-red': 'creative',
}
const currentTemplateComponent = computed(() => {
  const id = store.data.templateId
  const baseId = variantToBase[id] || id
  return templateComponentMap[baseId] || null
})

function zoomIn() {
  zoom.value = Math.min(zoom.value + 0.1, 1.2)
}

function zoomOut() {
  zoom.value = Math.max(zoom.value - 0.1, 0.4)
}

// ========== 模板选择 ==========

function onSelectTemplate(id, color) {
  store.setTemplate(id)
  if (color) {
    store.setThemeColor(color)
  }
  ElMessage.success('模板已切换')
}

// ========== 头像上传 ==========

function triggerAvatarUpload() {
  avatarInput.value.click()
}

function onAvatarSelected(e) {
  const file = e.target.files[0]
  if (!file) return
  if (file.size > 2 * 1024 * 1024) {
    ElMessage.warning('图片大小不能超过 2MB')
    e.target.value = ''
    return
  }
  const reader = new FileReader()
  reader.onload = (evt) => {
    store.setAvatar(evt.target.result)
    ElMessage.success('照片上传成功')
  }
  reader.readAsDataURL(file)
  e.target.value = ''
}

// ========== 自定义模板上传 ==========

function onUploadFileChange(file) {
  const reader = new FileReader()
  reader.onload = (evt) => {
    uploadForm.value.html = evt.target.result
  }
  reader.readAsText(file.raw)
}

function onUploadExceed() {
  ElMessage.warning('只能上传一个文件，请先移除已有文件')
}

function confirmUploadTemplate() {
  if (!uploadForm.value.html) {
    ElMessage.warning('请先选择HTML文件')
    return
  }
  const name = uploadForm.value.name || '自定义模板 ' + (store.customTemplates.length + 1)
  const id = store.addCustomTemplate(name, uploadForm.value.html)
  store.setTemplate(id)
  ElMessage.success('自定义模板上传成功！')
  // 重置
  uploadForm.value = { name: '', html: '' }
  showUploadDialog.value = false
  showGallery.value = false
  if (uploadRef.value) {
    uploadRef.value.clearFiles()
  }
}

function downloadSampleTemplate() {
  const sampleHtml = `<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="UTF-8">
<style>
  body { font-family: 'PingFang SC', sans-serif; margin: 0; padding: 40px; color: #333; }
  .header { text-align: center; border-bottom: 3px solid #4361ee; padding-bottom: 16px; margin-bottom: 20px; }
  .header h1 { font-size: 28px; color: #1a1a2e; margin: 0 0 4px; }
  .header p { color: #4361ee; font-size: 15px; margin: 0; }
  .section { margin-bottom: 18px; }
  .section h2 { font-size: 15px; color: #4361ee; border-left: 4px solid #4361ee; padding-left: 8px; }
  .item { margin-bottom: 10px; }
  .item-header { display: flex; justify-content: space-between; }
  .item-title { font-weight: 600; }
  .item-date { color: #999; font-size: 12px; }
</style>
</head>
<body>
  <div class="header">
    <h1>{{name}}</h1>
    <p>{{jobIntention}}</p>
    <div style="font-size:12px;color:#666;margin-top:4px;">
      {{phone}} | {{email}}
    </div>
  </div>
  <div class="section">
    <h2>自我评价</h2>
    <p style="font-size:13px;color:#555;">{{selfEvaluation}}</p>
  </div>
  <div class="section">
    <h2>教育经历</h2>
    <!-- education 列表会自动渲染 -->
  </div>
</body>
</html>`
  const blob = new Blob([sampleHtml], { type: 'text/html' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = '简历模板示例.html'
  a.click()
  URL.revokeObjectURL(url)
}

// ========== PDF 导出 ==========

async function exportPDF() {
  exporting.value = true
  try {
    const html2pdf = (await import('html2pdf.js')).default
    const element = document.getElementById('resume-preview')
    const fileName = `${store.data.personal.name || '我的'}简历.pdf`

    const opt = {
      margin: 0,
      filename: fileName,
      image: { type: 'jpeg', quality: 0.98 },
      html2canvas: {
        scale: 2,
        useCORS: true,
        logging: false,
      },
      jsPDF: {
        unit: 'mm',
        format: 'a4',
        orientation: 'portrait',
      },
      pagebreak: { mode: ['css', 'legacy'] },
    }

    await html2pdf().set(opt).from(element).save()
    ElMessage.success('PDF 导出成功！')
  } catch (e) {
    console.error('PDF export error:', e)
    ElMessage.error('PDF 导出失败：' + e.message)
  } finally {
    exporting.value = false
  }
}

// ========== 简历 PDF 上传解析 ==========

function triggerResumeUpload() {
  resumeInput.value.click()
}

async function onResumeSelected(e) {
  const file = e.target.files[0]
  if (!file) return
  if (file.size > 10 * 1024 * 1024) {
    ElMessage.warning('文件大小不能超过 10MB')
    e.target.value = ''
    return
  }

  parsing.value = true
  try {
    const formData = new FormData()
    formData.append('file', file)

    const response = await fetch('/api/resume/parse', {
      method: 'POST',
      body: formData,
    })

    if (!response.ok) {
      const err = await response.json().catch(() => ({}))
      throw new Error(err.detail || `服务器错误 (${response.status})`)
    }

    const result = await response.json()

    if (result.status === 'success' && result.data) {
      // 保留当前模板和主题色，用解析数据填充
      store.loadFromParsedData(result.data)

      // 如果 AI 推荐了模板，提示用户
      if (result.suggestedTemplate && result.suggestedTemplate !== store.data.templateId) {
        const templateNames = {
          simple: '经典简约', modern: '现代简约', sidebar: '侧边栏风格',
          professional: '商务专业', creative: '创意风格', elegant: '雅致风格',
          classic: '经典横幅', darksidebar: '深色侧栏', minimal: '极简留白',
        }
        const tplName = templateNames[result.suggestedTemplate] || result.suggestedTemplate
        ElMessageBox.confirm(
          `AI 根据简历风格推荐使用「${tplName}」模板，是否切换？`,
          '模板推荐',
          { confirmButtonText: '切换模板', cancelButtonText: '保持当前', type: 'info' }
        ).then(() => {
          store.setTemplate(result.suggestedTemplate)
          ElMessage.success('已切换到推荐模板')
        }).catch(() => {})
      } else {
        ElMessage.success(result.message || '简历解析成功！请检查并补充信息')
      }

      // 切换到个人信息标签页
      activeTab.value = 'personal'
    } else {
      throw new Error(result.message || '解析失败')
    }
  } catch (err) {
    console.error('Resume parse error:', err)
    ElMessage.error('简历解析失败：' + err.message)
  } finally {
    parsing.value = false
    e.target.value = ''
  }
}

// ========== JSON 导入导出 ==========

function handleExport() {
  const jsonStr = store.exportData()
  const blob = new Blob([jsonStr], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `${store.data.personal.name || '我的'}简历.json`
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success('JSON 导出成功！')
}

function handleImport() {
  fileInput.value.click()
}

function onFileSelected(e) {
  const file = e.target.files[0]
  if (!file) return
  const reader = new FileReader()
  reader.onload = (evt) => {
    try {
      store.importData(evt.target.result)
      ElMessage.success('JSON 导入成功！')
    } catch (err) {
      ElMessage.error('导入失败：文件格式错误')
    }
  }
  reader.readAsText(file)
  e.target.value = ''
}

function handleReset() {
  ElMessageBox.confirm('确定要重置所有简历数据吗？此操作不可撤销。', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
  }).then(() => {
    store.resetData()
    ElMessage.success('数据已重置')
  }).catch(() => {})
}
</script>

<style scoped>
.resume-editor {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 60px - 48px);
}

/* ========== 顶部工具栏 ========== */
.re-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #fff;
  border-radius: var(--radius-md);
  padding: 12px 20px;
  box-shadow: var(--shadow-sm);
  margin-bottom: 16px;
  flex-shrink: 0;
}

.re-toolbar-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.re-current-tpl {
  display: flex;
  align-items: center;
  gap: 4px;
}

.re-tpl-label {
  font-size: 12px;
  color: var(--text-secondary);
}

.re-tpl-name {
  font-size: 13px;
  font-weight: 600;
  color: var(--primary);
}

.re-color-picker {
  display: flex;
  align-items: center;
  gap: 8px;
  padding-left: 12px;
  border-left: 1px solid #eef0f4;
}

.re-color-label {
  font-size: 13px;
  color: var(--text-secondary);
  font-weight: 500;
}

.re-color-dot {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  cursor: pointer;
  border: 2px solid transparent;
  transition: all 0.2s;
}

.re-color-dot:hover {
  transform: scale(1.15);
}

.re-color-dot.active {
  border-color: #333;
  box-shadow: 0 0 0 2px #fff, 0 0 0 4px #333;
}

.re-toolbar-right {
  display: flex;
  gap: 8px;
}

/* ========== 主体 ========== */
.re-main {
  display: flex;
  gap: 16px;
  flex: 1;
  min-height: 0;
}

/* 左侧编辑面板 */
.re-editor-panel {
  width: 480px;
  flex-shrink: 0;
  background: #fff;
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-sm);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.re-tabs {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.re-tabs :deep(.el-tabs__header) {
  padding: 0 16px;
  margin-bottom: 0;
  flex-shrink: 0;
}

.re-tabs :deep(.el-tabs__content) {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.re-form-section {
  /* padding handled by tabs content */
}

.re-sub-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 12px;
  padding-left: 8px;
  border-left: 3px solid var(--primary);
}

/* 头像上传 */
.re-avatar-section {
  display: flex;
  align-items: flex-start;
  gap: 16px;
}

.re-avatar-label {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  width: 80px;
  flex-shrink: 0;
  text-align: right;
  padding-top: 4px;
}

.re-avatar-upload {
  flex: 1;
}

.re-avatar-preview {
  width: 85px;
  height: 119px;
  border-radius: 6px;
  border: 2px dashed #d0d5dd;
  overflow: hidden;
  cursor: pointer;
  transition: border-color 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #fafbfd;
}

.re-avatar-preview:hover {
  border-color: var(--primary);
}

.re-avatar-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.re-avatar-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  color: #909399;
  font-size: 12px;
}

.re-avatar-actions {
  display: flex;
  gap: 8px;
  margin-top: 8px;
}

.re-avatar-hint {
  font-size: 11px;
  color: #909399;
  margin-top: 4px;
}

/* 表单卡片 */
.re-card {
  border: 1px solid #eef0f4;
  border-radius: 8px;
  padding: 14px;
  margin-bottom: 14px;
  background: #fafbfd;
  transition: border-color 0.2s;
}

.re-card:hover {
  border-color: var(--primary);
}

.re-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.re-card-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
}

.re-add-btn {
  width: 100%;
  margin-top: 4px;
  border-style: dashed;
}

/* 工作描述列表 */
.re-desc-list {
  width: 100%;
}

.re-desc-row {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  margin-bottom: 8px;
}

.re-desc-row .el-input {
  flex: 1;
}

/* 技能行 */
.re-skill-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
}

/* ========== 右侧预览面板 ========== */
.re-preview-panel {
  flex: 1;
  background: #fff;
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-sm);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.re-preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px;
  border-bottom: 1px solid #f0f0f0;
  flex-shrink: 0;
}

.re-preview-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.re-preview-zoom {
  display: flex;
  align-items: center;
  gap: 8px;
}

.re-zoom-value {
  font-size: 12px;
  color: var(--text-secondary);
  min-width: 42px;
  text-align: center;
}

.re-preview-scroll {
  flex: 1;
  overflow: auto;
  background: #e8eaed;
  padding: 24px;
  display: flex;
  justify-content: center;
}

.re-preview-canvas {
  transform-origin: top center;
  transition: transform 0.2s;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.12);
}

.resume-preview-wrapper {
  width: 794px;
  background: #fff;
}

.re-custom-render {
  width: 794px;
  min-height: 400px;
  background: #fff;
}

/* 隐藏滚动条美化 */
.re-preview-scroll::-webkit-scrollbar {
  width: 6px;
}

.re-preview-scroll::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.15);
  border-radius: 3px;
}

.re-editor-panel :deep(.el-tabs__content)::-webkit-scrollbar {
  width: 6px;
}

.re-editor-panel :deep(.el-tabs__content)::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.1);
  border-radius: 3px;
}

/* 上传预览 */
.re-upload-preview {
  border: 1px solid #eef0f4;
  border-radius: 8px;
  overflow: auto;
  max-height: 300px;
  background: #f8f9fa;
}

.re-upload-preview-inner {
  transform-origin: top left;
  transform: scale(0.6);
  width: 794px;
}

.re-upload-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 120px;
  border: 1px dashed #eef0f4;
  border-radius: 8px;
  color: #ccc;
  gap: 8px;
}
</style>
