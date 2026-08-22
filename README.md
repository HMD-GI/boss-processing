# BOSS直聘数据采集与分析系统

基于 Chrome CDP 的 BOSS直聘职位数据采集系统，包含前后端分离架构、AI 智能助手、简历制作等功能。

## 功能概览

- **职位采集**：通过 Chrome DevTools Protocol 连接真实浏览器，调用 BOSS直聘内部 API 获取明文薪资数据，绕过字体反爬
- **职位查询**：支持分页查询、多条件筛选（关键词/城市/经验/学历/薪资/公司规模）
- **数据统计**：城市分布、行业分布、薪资分布等可视化图表
- **AI 助手**：自然语言对话，自动解析求职需求 → 检查数据库 → 按需爬取 → LLM 分析推荐岗位
- **简历制作**：PDF 简历上传解析、多种模板选择、实时预览、PDF 导出

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端 | FastAPI + SQLAlchemy + Pydantic |
| 前端 | Vue 3 + Vite + Element Plus + ECharts |
| 爬虫 | Chrome CDP (WebSocket) + 反检测策略 |
| 数据库 | MySQL / SQLite（可选） |
| AI | OpenAI 兼容 API（DeepSeek/OpenAI/通义千问等） |
| 对话存储 | MongoDB |

## 快速开始

### 1. 环境要求

- Python 3.10+
- Node.js 18+
- Google Chrome
- MongoDB（AI 助手功能需要）

### 2. 后端配置

```bash
# 克隆项目
git clone <repository-url>
cd boss_processing

# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
# Windows (PowerShell):
.venv\Scripts\Activate.ps1
# Linux/Mac:
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 填入你的配置（数据库、AI API Key 等）
```

### 3. 前端配置

```bash
cd frontend
npm install
```

### 4. 启动服务

**后端**（终端 1）：
```bash
python run.py serve
```
- API 地址：http://localhost:8000
- Swagger 文档：http://localhost:8000/docs

**前端**（终端 2）：
```bash
cd frontend
npm run dev
```
- 前端地址：http://localhost:5173

### 5. 首次使用

1. 打开浏览器访问 http://localhost:5173
2. 进入「采集任务」页面，点击「环境检查」启动 Chrome 并登录 BOSS直聘
3. 登录成功后即可使用采集、AI 助手等功能

## 项目结构

```
boss_processing/
├── src/                          # 后端源码
│   ├── config/settings.py        # 配置管理
│   ├── crawler/                  # 爬虫引擎
│   │   ├── cdp_connector.py      # Chrome CDP 连接管理
│   │   ├── api_fetcher.py        # 职位列表采集
│   │   ├── detail_fetcher.py     # 详情页抓取
│   │   └── anti_detect.py        # 反检测策略
│   ├── models/                   # 数据模型 (SQLAlchemy ORM)
│   ├── services/                 # 业务服务层
│   ├── api/                      # FastAPI 路由
│   ├── ai_assistant/             # AI 助手模块
│   └── utils/                    # 工具函数
├── frontend/                     # Vue 3 前端
│   ├── src/
│   │   ├── views/                # 页面组件
│   │   ├── components/resume/    # 简历模板组件
│   │   ├── stores/               # Pinia 状态管理
│   │   └── api/                  # API 请求封装
│   └── vite.config.js
├── tests/                        # 测试套件
├── run.py                        # 启动入口
├── requirements.txt              # Python 依赖
└── .env.example                  # 环境变量模板
```

## 测试

```bash
# 激活虚拟环境后
python -m pytest tests/test_utils.py tests/test_anti_detect.py tests/test_cdp.py -v
```

## License

MIT
