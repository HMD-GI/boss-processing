<template>
  <el-dialog
    v-model="visible"
    title="选择简历模板"
    width="900px"
    class="template-gallery-dialog"
    :close-on-click-modal="false"
  >
    <!-- 模板网格 -->
    <div class="tg-grid">
      <!-- 内置模板 -->
      <div
        v-for="tpl in builtinTemplates"
        :key="tpl.id"
        class="tg-card"
        :class="{ active: currentTemplateId === tpl.id }"
        @click="selectTemplate(tpl.id)"
      >
        <!-- 缩略图 -->
        <div class="tg-thumb" :style="tpl.thumbStyle">
          <div class="tg-thumb-inner" v-html="tpl.thumbHtml"></div>
        </div>
        <!-- 信息 -->
        <div class="tg-info">
          <span class="tg-name">{{ tpl.name }}</span>
          <el-tag size="small" type="info" effect="plain">{{ tpl.category }}</el-tag>
        </div>
        <!-- 选中标记 -->
        <div v-if="currentTemplateId === tpl.id" class="tg-active-badge">
          <el-icon><Check /></el-icon>
        </div>
        <!-- 预览按钮 -->
        <div class="tg-preview-btn" @click.stop="previewTemplate(tpl)">
          <el-icon><View /></el-icon>
          预览
        </div>
      </div>

      <!-- 自定义模板 -->
      <div
        v-for="tpl in customTemplates"
        :key="tpl.id"
        class="tg-card tg-custom-card"
        :class="{ active: currentTemplateId === tpl.id }"
        @click="selectTemplate(tpl.id)"
      >
        <div class="tg-thumb tg-thumb-custom">
          <el-icon :size="32" color="#aaa"><DocumentCopy /></el-icon>
          <span class="tg-custom-label">自定义</span>
        </div>
        <div class="tg-info">
          <span class="tg-name">{{ tpl.name }}</span>
          <el-tag size="small" type="warning" effect="plain">自定义</el-tag>
        </div>
        <div class="tg-custom-actions">
          <el-button text size="small" @click.stop="previewTemplate(tpl)">
            <el-icon><View /></el-icon>
          </el-button>
          <el-button text size="small" type="danger" @click.stop="removeCustomTemplate(tpl.id)">
            <el-icon><Delete /></el-icon>
          </el-button>
        </div>
        <div v-if="currentTemplateId === tpl.id" class="tg-active-badge">
          <el-icon><Check /></el-icon>
        </div>
      </div>

      <!-- 上传自定义模板 -->
      <div class="tg-card tg-upload-card" @click="$emit('upload-template')">
        <div class="tg-upload-area">
          <el-icon :size="32"><Plus /></el-icon>
          <span>上传自定义模板</span>
          <span class="tg-upload-hint">支持 .html 格式</span>
        </div>
      </div>
    </div>

    <!-- 大图预览弹窗 -->
    <el-dialog
      v-model="previewVisible"
      :title="previewingTemplate?.name + ' - 预览'"
      width="860px"
      class="template-preview-dialog"
      append-to-body
      destroy-on-close
    >
      <div class="tg-preview-container">
        <div class="tg-preview-loading" v-if="previewLoading">
          <el-icon class="is-loading" :size="32"><Loading /></el-icon>
          <p>渲染中...</p>
        </div>
        <div class="tg-preview-canvas" id="template-preview-canvas" v-show="!previewLoading">
          <component
            v-if="previewingTemplate && !previewingTemplate.isCustom"
            :is="getTemplateComponent(previewingTemplate.id)"
            :data="previewData"
            :color="previewData.themeColor"
          />
          <div
            v-else-if="previewingTemplate && previewingTemplate.isCustom"
            class="tg-custom-preview"
            v-html="previewingTemplate.html"
          ></div>
        </div>
      </div>
      <template #footer>
        <el-button @click="previewVisible = false">关闭</el-button>
        <el-button
          type="primary"
          @click="confirmFromPreview"
          v-if="previewingTemplate"
        >
          使用此模板
        </el-button>
      </template>
    </el-dialog>
  </el-dialog>
</template>

<script setup>
import { ref, computed, nextTick, shallowRef } from 'vue'
import { Check, View, Delete, Plus, DocumentCopy, Loading } from '@element-plus/icons-vue'
import SimpleTemplate from './SimpleTemplate.vue'
import ModernTemplate from './ModernTemplate.vue'
import SidebarTemplate from './SidebarTemplate.vue'
import ProfessionalTemplate from './ProfessionalTemplate.vue'
import CreativeTemplate from './CreativeTemplate.vue'
import ElegantTemplate from './ElegantTemplate.vue'
import ClassicTemplate from './ClassicTemplate.vue'
import DarkSidebarTemplate from './DarkSidebarTemplate.vue'
import MinimalTemplate from './MinimalTemplate.vue'
import BannerTemplate from './BannerTemplate.vue'
import HeaderTemplate from './HeaderTemplate.vue'
import SplitTemplate from './SplitTemplate.vue'
import TimelineTemplate from './TimelineTemplate.vue'
import CardTemplate from './CardTemplate.vue'
import TwoColumnTemplate from './TwoColumnTemplate.vue'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  currentTemplateId: { type: String, default: 'modern' },
  previewData: { type: Object, required: true },
  customTemplates: { type: Array, default: () => [] },
})

const emit = defineEmits(['update:modelValue', 'select', 'upload-template', 'remove-custom'])

const visible = computed({
  get: () => props.modelValue,
  set: (v) => emit('update:modelValue', v),
})

// 内置模板列表（含缩略图样式）
const builtinTemplates = [
  {
    id: 'modern',
    name: '现代简约',
    category: '热门',
    thumbStyle: 'background: linear-gradient(135deg, #4361ee 0%, #3a0ca3 100%);',
    thumbHtml: `
      <div style="padding:8px;">
        <div style="height:30px;background:rgba(255,255,255,0.3);border-radius:4px;margin-bottom:6px;"></div>
        <div style="height:4px;background:rgba(255,255,255,0.2);border-radius:2px;margin-bottom:3px;width:80%;"></div>
        <div style="height:4px;background:rgba(255,255,255,0.15);border-radius:2px;margin-bottom:8px;width:60%;"></div>
        <div style="display:flex;gap:4px;">
          <div style="flex:1;height:40px;background:rgba(255,255,255,0.15);border-radius:4px;"></div>
          <div style="flex:1;height:40px;background:rgba(255,255,255,0.1);border-radius:4px;"></div>
        </div>
      </div>
    `,
  },
  {
    id: 'simple',
    name: '经典简约',
    category: '简约',
    thumbStyle: 'background: #fff; border: 2px solid #e8ecf1;',
    thumbHtml: `
      <div style="padding:8px;text-align:center;">
        <div style="height:12px;width:50%;background:#4361ee;border-radius:2px;margin:0 auto 6px;"></div>
        <div style="height:2px;background:#4361ee;margin-bottom:8px;"></div>
        <div style="height:3px;background:#ddd;border-radius:1px;margin-bottom:3px;"></div>
        <div style="height:3px;background:#ddd;border-radius:1px;margin-bottom:3px;width:80%;margin-left:auto;margin-right:auto;"></div>
        <div style="height:3px;background:#ddd;border-radius:1px;width:60%;margin:0 auto;"></div>
      </div>
    `,
  },
  {
    id: 'sidebar',
    name: '侧边栏风格',
    category: '设计感',
    thumbStyle: 'background: #fff;',
    thumbHtml: `
      <div style="display:flex;height:100%;">
        <div style="width:35%;background:linear-gradient(135deg,#4361ee,#3a0ca3);padding:6px;">
          <div style="width:20px;height:20px;border-radius:50%;background:rgba(255,255,255,0.3);margin:0 auto 4px;"></div>
          <div style="height:3px;background:rgba(255,255,255,0.2);border-radius:1px;margin-bottom:2px;"></div>
          <div style="height:3px;background:rgba(255,255,255,0.15);border-radius:1px;width:80%;"></div>
        </div>
        <div style="flex:1;padding:6px;">
          <div style="height:4px;background:#4361ee;border-radius:1px;margin-bottom:3px;width:70%;"></div>
          <div style="height:2px;background:#eee;margin-bottom:2px;"></div>
          <div style="height:2px;background:#eee;margin-bottom:2px;width:80%;"></div>
          <div style="height:2px;background:#eee;width:60%;"></div>
        </div>
      </div>
    `,
  },
  {
    id: 'professional',
    name: '商务专业',
    category: '商务',
    thumbStyle: 'background: #1a365d;',
    thumbHtml: `
      <div style="padding:8px;">
        <div style="height:24px;background:rgba(255,255,255,0.15);border-radius:3px;margin-bottom:4px;padding:4px 6px;">
          <div style="height:5px;width:40%;background:rgba(255,255,255,0.5);border-radius:1px;"></div>
        </div>
        <div style="height:3px;background:rgba(255,255,255,0.1);margin-bottom:6px;"></div>
        <div style="background:#fff;padding:4px;border-radius:2px;">
          <div style="height:3px;background:#1a365d;border-radius:1px;margin-bottom:2px;width:50%;"></div>
          <div style="height:2px;background:#eee;margin-bottom:2px;"></div>
          <div style="height:2px;background:#eee;width:70%;"></div>
        </div>
      </div>
    `,
  },
  {
    id: 'creative',
    name: '创意风格',
    category: '创意',
    thumbStyle: 'background: #f8f9fa;',
    thumbHtml: `
      <div style="padding:8px;position:relative;overflow:hidden;">
        <div style="position:absolute;top:-15px;right:-10px;width:50px;height:50px;background:#e63946;border-radius:50%;opacity:0.15;"></div>
        <div style="display:flex;gap:4px;margin-bottom:6px;position:relative;">
          <div style="width:16px;height:16px;background:#e63946;border-radius:4px;"></div>
          <div>
            <div style="height:4px;background:#1a1a2e;border-radius:1px;margin-bottom:2px;width:40px;"></div>
            <div style="height:2px;background:#e63946;border-radius:1px;width:30px;"></div>
          </div>
        </div>
        <div style="background:#f0f2f5;border-left:2px solid #e63946;padding:4px;border-radius:0 3px 3px 0;margin-bottom:4px;">
          <div style="height:2px;background:#ddd;border-radius:1px;margin-bottom:2px;"></div>
          <div style="height:2px;background:#ddd;border-radius:1px;width:80%;"></div>
        </div>
        <div style="display:flex;gap:3px;">
          <div style="height:8px;background:#f0f2f5;border-radius:10px;flex:1;"></div>
          <div style="height:8px;background:#f0f2f5;border-radius:10px;flex:1;"></div>
          <div style="height:8px;background:#f0f2f5;border-radius:10px;flex:1;"></div>
        </div>
      </div>
    `,
  },
  {
    id: 'elegant',
    name: '雅致风格',
    category: '学术',
    thumbStyle: 'background: #fff;',
    thumbHtml: `
      <div style="padding:8px;text-align:center;">
        <div style="height:8px;width:40%;background:#5b8c5a;border-radius:1px;margin:0 auto 4px;"></div>
        <div style="width:20px;height:1px;background:#5b8c5a;margin:0 auto 6px;"></div>
        <div style="height:2px;background:#5b8c5a;border-radius:1px;margin:0 auto 6px;width:30%;"></div>
        <div style="border-bottom:1px solid #e8e8e8;margin-bottom:4px;"></div>
        <div style="height:2px;background:#ddd;margin:0 auto 2px;width:70%;"></div>
        <div style="height:2px;background:#ddd;margin:0 auto 2px;width:80%;"></div>
        <div style="height:2px;background:#ddd;margin:0 auto;width:60%;"></div>
      </div>
    `,
  },
  {
    id: 'classic',
    name: '经典横幅',
    category: '热门',
    thumbStyle: 'background: #fff;',
    thumbHtml: `
      <div style="padding:8px;">
        <div style="height:4px;background:#4e7282;border-radius:1px;margin-bottom:6px;"></div>
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
          <div style="height:6px;width:30%;background:#1a1a2e;border-radius:1px;"></div>
          <div style="width:16px;height:20px;background:#4e7282;border-radius:2px;"></div>
        </div>
        <div style="height:3px;background:#4e7282;border-radius:1px;margin-bottom:3px;width:50%;"></div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:2px;margin-bottom:4px;">
          <div style="height:2px;background:#ddd;border-radius:1px;"></div>
          <div style="height:2px;background:#ddd;border-radius:1px;"></div>
        </div>
        <div style="height:3px;background:#4e7282;border-radius:1px;margin-bottom:2px;width:40%;"></div>
        <div style="height:2px;background:#ddd;border-radius:1px;margin-bottom:2px;"></div>
        <div style="height:2px;background:#ddd;border-radius:1px;width:80%;"></div>
      </div>
    `,
  },
  {
    id: 'darksidebar',
    name: '深色侧栏',
    category: '设计感',
    thumbStyle: 'background: #fff;',
    thumbHtml: `
      <div style="display:flex;height:100%;">
        <div style="width:38%;background:#545969;padding:6px;">
          <div style="width:16px;height:20px;background:rgba(255,255,255,0.3);border-radius:2px;margin:0 auto 4px;"></div>
          <div style="height:3px;background:rgba(255,255,255,0.3);border-radius:1px;margin-bottom:2px;"></div>
          <div style="height:3px;background:rgba(255,255,255,0.2);border-radius:1px;width:80%;margin-bottom:4px;"></div>
          <div style="height:2px;background:rgba(255,255,255,0.15);border-radius:1px;margin-bottom:2px;"></div>
          <div style="height:2px;background:rgba(255,255,255,0.1);border-radius:1px;width:70%;"></div>
        </div>
        <div style="flex:1;padding:6px;">
          <div style="width:4px;height:12px;background:#545969;border-radius:1px;display:inline-block;margin-bottom:4px;"></div>
          <div style="height:3px;background:#545969;border-radius:1px;margin-bottom:3px;width:60%;display:inline-block;"></div>
          <div style="height:2px;background:#eee;margin-bottom:2px;"></div>
          <div style="height:2px;background:#eee;margin-bottom:2px;width:80%;"></div>
          <div style="height:2px;background:#eee;width:60%;"></div>
        </div>
      </div>
    `,
  },
  {
    id: 'minimal',
    name: '极简留白',
    category: '简约',
    thumbStyle: 'background: #fff;',
    thumbHtml: `
      <div style="padding:10px;">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
          <div>
            <div style="height:5px;width:50%;background:#2c3e50;border-radius:1px;margin-bottom:3px;"></div>
            <div style="height:2px;background:#2c3e50;border-radius:1px;width:30%;"></div>
          </div>
          <div style="width:14px;height:18px;background:#ddd;border-radius:2px;"></div>
        </div>
        <div style="border-bottom:1px solid #eee;margin-bottom:6px;"></div>
        <div style="height:2px;background:#2c3e50;border-radius:1px;margin-bottom:4px;width:40%;text-transform:uppercase;"></div>
        <div style="height:2px;background:#ddd;margin-bottom:2px;"></div>
        <div style="height:2px;background:#ddd;margin-bottom:2px;width:80%;"></div>
        <div style="height:2px;background:#ddd;width:60%;"></div>
      </div>
    `,
  },
  {
    id: 'banner',
    name: '彩色横幅',
    category: '热门',
    thumbStyle: 'background: #fff;',
    thumbHtml: `<div style="padding:0;"><div style="background:#0e88ad;padding:6px 8px;display:flex;justify-content:space-between;align-items:center;"><div><div style="height:5px;width:30%;background:rgba(255,255,255,.7);border-radius:1px;margin-bottom:2px;"></div><div style="height:3px;width:20%;background:rgba(255,255,255,.5);border-radius:1px;"></div></div><div style="width:12px;height:16px;background:rgba(255,255,255,.3);border-radius:2px;"></div></div><div style="padding:6px;"><div style="height:3px;background:#0e88ad;border-radius:1px;margin-bottom:3px;width:40%;"></div><div style="height:2px;background:#ddd;margin-bottom:2px;"></div><div style="height:2px;background:#ddd;width:80%;"></div></div></div>`,
  },
  {
    id: 'header',
    name: '标题页眉',
    category: '热门',
    thumbStyle: 'background: #fff;',
    thumbHtml: `<div style="padding:0;"><div style="background:#5695c3;text-align:center;padding:3px 0;color:#fff;font-size:8px;">PERSONAL RESUME</div><div style="display:flex;padding:6px 8px;border-bottom:2px solid #5695c3;gap:4px;"><div style="width:12px;height:16px;background:#5695c3;border-radius:2px;"></div><div style="flex:1;"><div style="height:4px;width:40%;background:#5695c3;border-radius:1px;margin-bottom:2px;"></div><div style="height:2px;background:#ddd;width:30%;"></div></div></div><div style="padding:6px 8px;"><div style="height:3px;background:#5695c3;border-radius:1px;margin-bottom:2px;width:50%;"></div><div style="height:2px;background:#ddd;margin-bottom:2px;"></div><div style="height:2px;background:#ddd;width:80%;"></div></div></div>`,
  },
  {
    id: 'split',
    name: '左右分栏',
    category: '设计感',
    thumbStyle: 'background: #fff;',
    thumbHtml: `<div style="display:flex;height:100%;"><div style="width:30%;background:#3978a3;padding:4px;"><div style="width:10px;height:14px;background:rgba(255,255,255,.3);border-radius:1px;margin:0 auto 4px;"></div><div style="height:2px;background:rgba(255,255,255,.2);margin-bottom:2px;"></div><div style="height:2px;background:rgba(255,255,255,.15);width:80%;"></div></div><div style="flex:1;padding:4px;"><div style="height:4px;width:40%;background:#3978a3;border-radius:1px;margin-bottom:2px;"></div><div style="height:2px;background:#ddd;margin-bottom:2px;"></div><div style="height:2px;background:#ddd;width:80%;"></div><div style="border-bottom:2px solid #3978a3;margin:4px 0;"></div><div style="height:2px;background:#ddd;margin-bottom:2px;"></div><div style="height:2px;background:#ddd;width:70%;"></div></div></div>`,
  },
  {
    id: 'timeline',
    name: '时间轴',
    category: '设计感',
    thumbStyle: 'background: #fff;',
    thumbHtml: `<div style="padding:6px 8px;border-bottom:3px solid #1575bf;display:flex;gap:4px;align-items:center;"><div style="width:12px;height:16px;background:#1575bf;border-radius:2px;"></div><div style="height:4px;width:40%;background:#1575bf;border-radius:1px;"></div></div><div style="padding:6px 8px;"><div style="height:3px;background:#1575bf;border-radius:1px;margin-bottom:4px;width:30%;"></div><div style="position:relative;padding-left:8px;"><div style="position:absolute;left:3px;top:0;bottom:0;width:1px;background:#ddd;"></div><div style="display:flex;gap:4px;margin-bottom:4px;"><div style="width:5px;height:5px;border-radius:50%;background:#1575bf;"></div><div style="flex:1;"><div style="height:2px;background:#999;margin-bottom:2px;width:50%;"></div><div style="height:2px;background:#ddd;width:80%;"></div></div></div><div style="display:flex;gap:4px;"><div style="width:5px;height:5px;border-radius:50%;background:#1575bf;"></div><div style="flex:1;"><div style="height:2px;background:#999;margin-bottom:2px;width:40%;"></div><div style="height:2px;background:#ddd;width:70%;"></div></div></div></div></div>`,
  },
  {
    id: 'card',
    name: '卡片风格',
    category: '创意',
    thumbStyle: 'background: #f5f6f8;',
    thumbHtml: `<div style="padding:4px;"><div style="background:#fff;border-radius:4px;padding:4px 6px;margin-bottom:3px;display:flex;gap:4px;align-items:center;"><div style="width:10px;height:14px;background:#a08f75;border-radius:2px;"></div><div style="height:3px;width:30%;background:#a08f75;border-radius:1px;"></div></div><div style="background:#fff;border-radius:3px;padding:4px 6px;margin-bottom:3px;"><div style="height:2px;background:#a08f75;border-radius:1px;margin-bottom:2px;width:40%;"></div><div style="height:2px;background:#ddd;margin-bottom:2px;"></div><div style="height:2px;background:#ddd;width:80%;"></div></div><div style="background:#fff;border-radius:3px;padding:4px 6px;"><div style="height:2px;background:#a08f75;border-radius:1px;margin-bottom:2px;width:30%;"></div><div style="height:2px;background:#ddd;width:70%;"></div></div></div>`,
  },
  {
    id: 'twocol',
    name: '双栏布局',
    category: '简约',
    thumbStyle: 'background: #fff;',
    thumbHtml: `<div style="padding:6px 8px;border-bottom:3px solid #609ef3;display:flex;gap:4px;"><div style="width:10px;height:14px;background:#609ef3;border-radius:2px;"></div><div style="flex:1;"><div style="height:4px;width:30%;background:#609ef3;border-radius:1px;margin-bottom:2px;"></div><div style="height:2px;background:#ddd;width:50%;"></div></div></div><div style="padding:4px 8px;display:flex;gap:8px;"><div style="width:30%;"><div style="height:2px;background:#609ef3;margin-bottom:2px;"></div><div style="height:2px;background:#ddd;margin-bottom:2px;"></div><div style="height:2px;background:#ddd;width:80%;"></div></div><div style="flex:1;"><div style="height:2px;background:#609ef3;margin-bottom:2px;"></div><div style="height:2px;background:#ddd;margin-bottom:2px;"></div><div style="height:2px;background:#ddd;width:80%;"></div></div></div>`,
  },
  // ========== 颜色变体（基于ycresume.com的43个模板配色） ==========
  { id: 'modern-dark', name: '现代简约-墨黑', category: '配色', thumbStyle: 'background: linear-gradient(135deg,#333333 0%,#1a1a2e 100%);', thumbHtml: '<div style="padding:8px;"><div style="height:30px;background:rgba(255,255,255,.15);border-radius:4px;margin-bottom:6px;"></div><div style="height:4px;background:rgba(255,255,255,.15);border-radius:2px;margin-bottom:3px;width:80%;"></div><div style="height:4px;background:rgba(255,255,255,.1);border-radius:2px;width:60%;"></div></div>', baseId: 'modern', defaultColor: '#333333' },
  { id: 'modern-blue', name: '现代简约-天蓝', category: '配色', thumbStyle: 'background: linear-gradient(135deg,#1575bf 0%,#0e88ad 100%);', thumbHtml: '<div style="padding:8px;"><div style="height:30px;background:rgba(255,255,255,.15);border-radius:4px;margin-bottom:6px;"></div><div style="height:4px;background:rgba(255,255,255,.15);border-radius:2px;margin-bottom:3px;width:80%;"></div><div style="height:4px;background:rgba(255,255,255,.1);border-radius:2px;width:60%;"></div></div>', baseId: 'modern', defaultColor: '#1575bf' },
  { id: 'sidebar-deep', name: '侧边栏-深海蓝', category: '配色', thumbStyle: 'background: #fff;', thumbHtml: '<div style="display:flex;height:100%;"><div style="width:35%;background:#284967;padding:6px;"><div style="width:20px;height:20px;border-radius:50%;background:rgba(255,255,255,.3);margin:0 auto 4px;"></div><div style="height:3px;background:rgba(255,255,255,.2);margin-bottom:2px;"></div></div><div style="flex:1;padding:6px;"><div style="height:4px;background:#284967;border-radius:1px;margin-bottom:3px;width:70%;"></div><div style="height:2px;background:#eee;width:60%;"></div></div></div>', baseId: 'sidebar', defaultColor: '#284967' },
  { id: 'sidebar-slate', name: '侧边栏-青灰', category: '配色', thumbStyle: 'background: #fff;', thumbHtml: '<div style="display:flex;height:100%;"><div style="width:35%;background:#4e7282;padding:6px;"><div style="width:20px;height:20px;border-radius:50%;background:rgba(255,255,255,.3);margin:0 auto 4px;"></div><div style="height:3px;background:rgba(255,255,255,.2);margin-bottom:2px;"></div></div><div style="flex:1;padding:6px;"><div style="height:4px;background:#4e7282;border-radius:1px;margin-bottom:3px;width:70%;"></div><div style="height:2px;background:#eee;width:60%;"></div></div></div>', baseId: 'sidebar', defaultColor: '#4e7282' },
  { id: 'banner-teal', name: '彩色横幅-青色', category: '配色', thumbStyle: 'background: #fff;', thumbHtml: '<div style="background:#0e88ad;padding:6px 8px;display:flex;justify-content:space-between;"><div style="height:4px;width:30%;background:rgba(255,255,255,.7);border-radius:1px;"></div><div style="width:12px;height:16px;background:rgba(255,255,255,.3);border-radius:2px;"></div></div>', baseId: 'banner', defaultColor: '#0e88ad' },
  { id: 'banner-blue', name: '彩色横幅-蓝色', category: '配色', thumbStyle: 'background: #fff;', thumbHtml: '<div style="background:#1575bf;padding:6px 8px;display:flex;justify-content:space-between;"><div style="height:4px;width:30%;background:rgba(255,255,255,.7);border-radius:1px;"></div><div style="width:12px;height:16px;background:rgba(255,255,255,.3);border-radius:2px;"></div></div>', baseId: 'banner', defaultColor: '#1575bf' },
  { id: 'header-skyblue', name: '标题页眉-天蓝', category: '配色', thumbStyle: 'background: #fff;', thumbHtml: '<div style="background:#5695c3;text-align:center;padding:3px 0;color:#fff;font-size:8px;">RESUME</div><div style="display:flex;padding:4px 6px;gap:4px;"><div style="width:10px;height:14px;background:#5695c3;border-radius:2px;"></div><div style="height:3px;width:40%;background:#5695c3;border-radius:1px;"></div></div>', baseId: 'header', defaultColor: '#5695c3' },
  { id: 'header-blue', name: '标题页眉-亮蓝', category: '配色', thumbStyle: 'background: #fff;', thumbHtml: '<div style="background:#609ef3;text-align:center;padding:3px 0;color:#fff;font-size:8px;">RESUME</div><div style="display:flex;padding:4px 6px;gap:4px;"><div style="width:10px;height:14px;background:#609ef3;border-radius:2px;"></div><div style="height:3px;width:40%;background:#609ef3;border-radius:1px;"></div></div>', baseId: 'header', defaultColor: '#609ef3' },
  { id: 'darksidebar-dark', name: '深色侧栏-暗灰', category: '配色', thumbStyle: 'background: #fff;', thumbHtml: '<div style="display:flex;height:100%;"><div style="width:38%;background:#545969;padding:6px;"><div style="width:14px;height:18px;background:rgba(255,255,255,.2);border-radius:2px;margin:0 auto 4px;"></div><div style="height:2px;background:rgba(255,255,255,.15);margin-bottom:2px;"></div></div><div style="flex:1;padding:4px;"><div style="height:3px;background:#545969;margin-bottom:2px;width:60%;"></div><div style="height:2px;background:#eee;width:80%;"></div></div></div>', baseId: 'darksidebar', defaultColor: '#545969' },
  { id: 'darksidebar-navy', name: '深色侧栏-海军蓝', category: '配色', thumbStyle: 'background: #fff;', thumbHtml: '<div style="display:flex;height:100%;"><div style="width:38%;background:#1a365d;padding:6px;"><div style="width:14px;height:18px;background:rgba(255,255,255,.2);border-radius:2px;margin:0 auto 4px;"></div><div style="height:2px;background:rgba(255,255,255,.15);margin-bottom:2px;"></div></div><div style="flex:1;padding:4px;"><div style="height:3px;background:#1a365d;margin-bottom:2px;width:60%;"></div><div style="height:2px;background:#eee;width:80%;"></div></div></div>', baseId: 'darksidebar', defaultColor: '#1a365d' },
  { id: 'classic-teal', name: '经典横幅-青色', category: '配色', thumbStyle: 'background: #fff;', thumbHtml: '<div style="padding:6px;"><div style="height:4px;background:#4e7282;border-radius:1px;margin-bottom:4px;"></div><div style="display:flex;justify-content:space-between;"><div style="height:4px;width:30%;background:#1a1a2e;border-radius:1px;"></div><div style="width:12px;height:16px;background:#4e7282;border-radius:2px;"></div></div><div style="height:2px;background:#ddd;margin-top:4px;width:80%;"></div></div>', baseId: 'classic', defaultColor: '#4e7282' },
  { id: 'classic-navy', name: '经典横幅-藏青', category: '配色', thumbStyle: 'background: #fff;', thumbHtml: '<div style="padding:6px;"><div style="height:4px;background:#284967;border-radius:1px;margin-bottom:4px;"></div><div style="display:flex;justify-content:space-between;"><div style="height:4px;width:30%;background:#1a1a2e;border-radius:1px;"></div><div style="width:12px;height:16px;background:#284967;border-radius:2px;"></div></div><div style="height:2px;background:#ddd;margin-top:4px;width:80%;"></div></div>', baseId: 'classic', defaultColor: '#284967' },
  { id: 'split-blue', name: '左右分栏-蓝色', category: '配色', thumbStyle: 'background: #fff;', thumbHtml: '<div style="display:flex;height:100%;"><div style="width:30%;background:#3978a3;padding:4px;"><div style="width:10px;height:14px;background:rgba(255,255,255,.2);border-radius:1px;margin:0 auto 4px;"></div></div><div style="flex:1;padding:4px;"><div style="height:4px;width:40%;background:#3978a3;border-radius:1px;margin-bottom:2px;"></div><div style="height:2px;background:#ddd;width:80%;"></div></div></div>', baseId: 'split', defaultColor: '#3978a3' },
  { id: 'split-navy', name: '左右分栏-藏青', category: '配色', thumbStyle: 'background: #fff;', thumbHtml: '<div style="display:flex;height:100%;"><div style="width:30%;background:#284967;padding:4px;"><div style="width:10px;height:14px;background:rgba(255,255,255,.2);border-radius:1px;margin:0 auto 4px;"></div></div><div style="flex:1;padding:4px;"><div style="height:4px;width:40%;background:#284967;border-radius:1px;margin-bottom:2px;"></div><div style="height:2px;background:#ddd;width:80%;"></div></div></div>', baseId: 'split', defaultColor: '#284967' },
  { id: 'timeline-blue', name: '时间轴-蓝色', category: '配色', thumbStyle: 'background: #fff;', thumbHtml: '<div style="padding:6px 8px;border-bottom:3px solid #1575bf;"><div style="height:4px;width:30%;background:#1575bf;border-radius:1px;"></div></div>', baseId: 'timeline', defaultColor: '#1575bf' },
  { id: 'timeline-teal', name: '时间轴-青色', category: '配色', thumbStyle: 'background: #fff;', thumbHtml: '<div style="padding:6px 8px;border-bottom:3px solid #0e88ad;"><div style="height:4px;width:30%;background:#0e88ad;border-radius:1px;"></div></div>', baseId: 'timeline', defaultColor: '#0e88ad' },
  { id: 'card-warm', name: '卡片-暖灰', category: '配色', thumbStyle: 'background: #f5f6f8;', thumbHtml: '<div style="background:#fff;border-radius:4px;padding:4px 6px;margin-bottom:3px;"><div style="height:2px;background:#a08f75;margin-bottom:2px;width:40%;"></div><div style="height:2px;background:#ddd;width:80%;"></div></div>', baseId: 'card', defaultColor: '#a08f75' },
  { id: 'card-blue', name: '卡片-蓝色', category: '配色', thumbStyle: 'background: #f5f6f8;', thumbHtml: '<div style="background:#fff;border-radius:4px;padding:4px 6px;margin-bottom:3px;"><div style="height:2px;background:#5695c3;margin-bottom:2px;width:40%;"></div><div style="height:2px;background:#ddd;width:80%;"></div></div>', baseId: 'card', defaultColor: '#5695c3' },
  { id: 'twocol-blue', name: '双栏-蓝色', category: '配色', thumbStyle: 'background: #fff;', thumbHtml: '<div style="padding:6px 8px;border-bottom:3px solid #609ef3;"><div style="height:4px;width:30%;background:#609ef3;border-radius:1px;"></div></div>', baseId: 'twocol', defaultColor: '#609ef3' },
  { id: 'twocol-teal', name: '双栏-青色', category: '配色', thumbStyle: 'background: #fff;', thumbHtml: '<div style="padding:6px 8px;border-bottom:3px solid #0e88ad;"><div style="height:4px;width:30%;background:#0e88ad;border-radius:1px;"></div></div>', baseId: 'twocol', defaultColor: '#0e88ad' },
  { id: 'simple-red', name: '经典简约-红色', category: '配色', thumbStyle: 'background: #fff; border: 2px solid #e63946;', thumbHtml: '<div style="padding:8px;text-align:center;"><div style="height:12px;width:50%;background:#e63946;border-radius:2px;margin:0 auto 6px;"></div><div style="height:2px;background:#e63946;margin-bottom:8px;"></div><div style="height:3px;background:#ddd;border-radius:1px;margin-bottom:3px;"></div></div>', baseId: 'simple', defaultColor: '#e63946' },
  { id: 'simple-green', name: '经典简约-绿色', category: '配色', thumbStyle: 'background: #fff; border: 2px solid #5b8c5a;', thumbHtml: '<div style="padding:8px;text-align:center;"><div style="height:12px;width:50%;background:#5b8c5a;border-radius:2px;margin:0 auto 6px;"></div><div style="height:2px;background:#5b8c5a;margin-bottom:8px;"></div><div style="height:3px;background:#ddd;border-radius:1px;margin-bottom:3px;"></div></div>', baseId: 'simple', defaultColor: '#5b8c5a' },
  { id: 'elegant-dark', name: '雅致-墨色', category: '配色', thumbStyle: 'background: #fff;', thumbHtml: '<div style="padding:8px;text-align:center;"><div style="height:8px;width:40%;background:#333;border-radius:1px;margin:0 auto 4px;"></div><div style="height:2px;background:#333;margin:0 auto 6px;width:30%;"></div><div style="height:2px;background:#ddd;margin:0 auto 2px;width:70%;"></div></div>', baseId: 'elegant', defaultColor: '#333333' },
  { id: 'minimal-dark', name: '极简-暗灰', category: '配色', thumbStyle: 'background: #fff;', thumbHtml: '<div style="padding:10px;"><div style="height:5px;width:50%;background:#2c3e50;border-radius:1px;margin-bottom:3px;"></div><div style="border-bottom:1px solid #eee;margin-bottom:6px;"></div><div style="height:2px;background:#2c3e50;border-radius:1px;margin-bottom:2px;width:40%;"></div></div>', baseId: 'minimal', defaultColor: '#2c3e50' },
  { id: 'professional-blue', name: '商务-蓝色', category: '配色', thumbStyle: 'background: #1a365d;', thumbHtml: '<div style="padding:8px;"><div style="height:20px;background:rgba(255,255,255,.1);border-radius:3px;margin-bottom:4px;"></div><div style="background:#fff;padding:4px;border-radius:2px;"><div style="height:3px;background:#1a365d;border-radius:1px;margin-bottom:2px;width:50%;"></div><div style="height:2px;background:#eee;width:70%;"></div></div></div>', baseId: 'professional', defaultColor: '#1a365d' },
  { id: 'creative-red', name: '创意-红色', category: '配色', thumbStyle: 'background: #f8f9fa;', thumbHtml: '<div style="padding:8px;"><div style="display:flex;gap:4px;margin-bottom:4px;"><div style="width:14px;height:14px;background:#e63946;border-radius:3px;"></div><div style="height:4px;background:#1a1a2e;border-radius:1px;width:30px;"></div></div><div style="height:2px;background:#ddd;margin-bottom:2px;"></div><div style="height:2px;background:#ddd;width:80%;"></div></div>', baseId: 'creative', defaultColor: '#e63946' },
]

// 模板组件映射
const componentMap = shallowRef({
  simple: SimpleTemplate,
  modern: ModernTemplate,
  sidebar: SidebarTemplate,
  professional: ProfessionalTemplate,
  creative: CreativeTemplate,
  elegant: ElegantTemplate,
  classic: ClassicTemplate,
  darksidebar: DarkSidebarTemplate,
  minimal: MinimalTemplate,
  banner: BannerTemplate,
  header: HeaderTemplate,
  split: SplitTemplate,
  timeline: TimelineTemplate,
  card: CardTemplate,
  twocol: TwoColumnTemplate,
})

function getTemplateComponent(id) {
  // 颜色变体：查找其 baseId 对应的组件
  const tpl = builtinTemplates.find(t => t.id === id)
  const baseId = tpl?.baseId || id
  return componentMap.value[baseId] || ModernTemplate
}

// 预览
const previewVisible = ref(false)
const previewingTemplate = ref(null)
const previewLoading = ref(false)

function previewTemplate(tpl) {
  previewingTemplate.value = tpl
  previewLoading.value = true
  previewVisible.value = true
  nextTick(() => {
    setTimeout(() => {
      previewLoading.value = false
    }, 300)
  })
}

function confirmFromPreview() {
  if (previewingTemplate.value) {
    emit('select', previewingTemplate.value.id)
    previewVisible.value = false
    visible.value = false
  }
}

function selectTemplate(id) {
  // 颜色变体：同时设置模板ID和默认颜色
  const tpl = builtinTemplates.find(t => t.id === id)
  if (tpl?.defaultColor) {
    emit('select', id, tpl.defaultColor)
  } else {
    emit('select', id)
  }
  visible.value = false
}

function removeCustomTemplate(id) {
  emit('remove-custom', id)
}
</script>

<style scoped>
.tg-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  padding: 4px;
  max-height: 560px;
  overflow-y: auto;
}

.tg-card {
  position: relative;
  border: 2px solid #eef0f4;
  border-radius: 10px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.25s ease;
  background: #fff;
}

.tg-card:hover {
  border-color: var(--primary);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.tg-card.active {
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(67, 97, 238, 0.15);
}

/* 缩略图 */
.tg-thumb {
  height: 140px;
  overflow: hidden;
  position: relative;
}

.tg-thumb-inner {
  width: 100%;
  height: 100%;
  transform-origin: top left;
}

.tg-thumb-custom {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: #f8f9fa;
  gap: 4px;
}

.tg-custom-label {
  font-size: 12px;
  color: #999;
}

/* 信息 */
.tg-info {
  padding: 8px 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.tg-name {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
}

/* 选中标记 */
.tg-active-badge {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: var(--primary);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  box-shadow: 0 2px 8px rgba(67, 97, 238, 0.4);
}

/* 预览按钮 */
.tg-preview-btn {
  position: absolute;
  bottom: 50px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(0, 0, 0, 0.7);
  color: #fff;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 4px;
  opacity: 0;
  transition: opacity 0.2s;
  white-space: nowrap;
}

.tg-card:hover .tg-preview-btn {
  opacity: 1;
}

/* 自定义模板操作 */
.tg-custom-actions {
  position: absolute;
  top: 8px;
  right: 8px;
  display: flex;
  gap: 2px;
}

/* 上传卡片 */
.tg-upload-card {
  border: 2px dashed #c0c4cc;
  display: flex;
  align-items: center;
  justify-content: center;
}

.tg-upload-card:hover {
  border-color: var(--primary);
  background: rgba(67, 97, 238, 0.03);
}

.tg-upload-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 30px 0;
  gap: 6px;
  color: #909399;
  font-size: 13px;
}

.tg-upload-hint {
  font-size: 11px;
  color: #c0c4cc;
}

/* 预览弹窗 */
.tg-preview-container {
  background: #e8eaed;
  padding: 20px;
  border-radius: 8px;
  max-height: 70vh;
  overflow: auto;
  display: flex;
  justify-content: center;
}

.tg-preview-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 80px 0;
  color: #909399;
}

.tg-preview-canvas {
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.12);
}

.tg-custom-preview {
  width: 794px;
  background: #fff;
  min-height: 400px;
}
</style>
