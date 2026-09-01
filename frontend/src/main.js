import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import './styles/theme.css'
import App from './App.vue'
import router from './router'

// 在 Vue 挂载前应用主题（避免白色闪烁）
if (localStorage.getItem('theme') === 'dark') {
  document.documentElement.classList.add('dark')
}

const app = createApp(App)
const pinia = createPinia()

for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.use(pinia)
app.use(ElementPlus)
app.use(router)
app.mount('#app')
