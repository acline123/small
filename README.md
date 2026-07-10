# StudyAgent — 基于 RAG 的智能学习助手 Agent

《智能 Agent 应用开发项目》课程实践项目。

## 功能

- 文档上传（PDF / DOCX / TXT）并自动构建 ChromaDB 知识库
- RAG 检索增强问答（LangChain + ChromaDB）
- Agent 工作流：LLM 意图识别 → MCP Tool 调用 → DeepSeek 生成
- MCP Tool：`search_document`、`summary_document`、`generate_exercise`
- **学习分析**：每次提问自动分析用户水平（Beginner/Intermediate/Advanced），生成个性化学习路线
- **智能习题**：基于聊天记录和文档生成习题（选择/判断/填空），自动批改+解析
- 多轮对话 + SQLite 聊天记录
- Vue3 + Element Plus 前端四页面

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue3、Element Plus、Axios、Vite |
| 后端 | Python、Flask、LangChain |
| 向量库 | ChromaDB |
| 数据库 | SQLite、SQLAlchemy |
| 大模型 | DeepSeek API（token-cloud 代理） |
| Embedding | BAAI/bge-m3（SiliconFlow） |

## 前置依赖

### 外部服务（需要注册获取 API Key）

| 服务 | 用途 | 获取地址 |
|------|------|----------|
| DeepSeek（token-cloud 代理） | 对话生成 & 意图识别 | 由授课老师提供 Key（模型：DeepSeek-V4-Flash） |
| SiliconFlow | 文本向量化（Embedding） | https://siliconflow.cn（有免费额度） |

> **说明**：本项目使用 token-cloud 代理（`www.token-cloud.cn`）访问 DeepSeek。如果你自己申请 DeepSeek 官方 Key，需将 `backend/.env` 中 `DEEPSEEK_BASE_URL` 改为 `https://api.deepseek.com`，`DEEPSEEK_MODEL` 改为 `deepseek-chat`。

### 本地环境

- **Python** >= 3.10
- **Node.js** >= 18 + npm
- **Windows 用户**：安装 `chromadb` 可能需要 Visual Studio C++ Build Tools。如遇到编译报错，可从 [visualstudio.microsoft.com](https://visualstudio.microsoft.com/downloads/) 下载安装，勾选「C++ 桌面开发」工作负载。

### Python 依赖（backend/requirements.txt）

```
flask>=3.0.0
flask-cors>=4.0.0
python-dotenv>=1.0.0
langchain>=0.3.0
langchain-community>=0.3.0
langchain-openai>=0.2.0,<0.3.0
langchain-text-splitters>=0.3.0
chromadb>=0.5.0
langchain-chroma>=0.1.0
pypdf>=4.0.0
docx2txt>=0.8
openai>=1.0.0
sqlalchemy>=2.0.0
werkzeug>=3.0.0
```

### 前端依赖（frontend/package.json）

| 包 | 版本 |
|---|------|
| vue | ^3.5.0 |
| vue-router | ^4.4.0 |
| element-plus | ^2.8.0 |
| @element-plus/icons-vue | ^2.3.1 |
| axios | ^1.7.0 |
| mermaid | ^11.0 |
| vite (dev) | ^5.4.0 |
| @vitejs/plugin-vue (dev) | ^5.1.0 |

## 快速启动

### 1. 配置环境变量

```bash
cd StudyAgent/backend

# 复制模板文件
copy .env.example .env
```

编辑 `.env`，填入真实 API Key：

```env
# DeepSeek Chat API（token-cloud 代理 / DeepSeek 官方二选一）

# 方式一：token-cloud 代理（老师提供 Key）
DEEPSEEK_API_KEY=sk-你的deepseek-api-key
DEEPSEEK_BASE_URL=https://www.token-cloud.cn/v1
DEEPSEEK_MODEL=DeepSeek-V4-Flash

# 方式二：DeepSeek 官方（自己注册）
# DEEPSEEK_API_KEY=sk-你的deepseek-api-key
# DEEPSEEK_BASE_URL=https://api.deepseek.com
# DEEPSEEK_MODEL=deepseek-chat

# Embedding API（OpenAI 兼容格式，推荐 SiliconFlow 的 BAAI/bge-m3）
EMBEDDING_API_KEY=sk-你的siliconflow-api-key
EMBEDDING_BASE_URL=https://api.siliconflow.cn/v1
EMBEDDING_MODEL=BAAI/bge-m3

# Flask
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
FLASK_DEBUG=true
```

> **说明**：DeepSeek 官方 API 目前不提供 Embedding 端点。项目通过 OpenAI 兼容接口调用 Embedding 服务。推荐使用 [SiliconFlow](https://siliconflow.cn) 的 `BAAI/bge-m3` 模型（中文效果好，有免费额度）。

### 2. 启动后端

```bash
cd StudyAgent/backend

# 创建虚拟环境（首次）
python -m venv .venv

# 激活虚拟环境
# Windows:
.venv\Scripts\activate
# macOS / Linux:
# source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 启动
python run.py
```

> **注意**：务必在虚拟环境中运行，否则依赖包可能找不到。启动后终端出现 `(.venv)` 前缀表示虚拟环境已激活。后端默认运行在 http://localhost:5000。

### 3. 启动前端

新开一个终端：

```bash
cd StudyAgent/frontend
npm install
npm run dev
```

前端默认运行在 http://localhost:5173，通过 Vite 代理将 `/api` 请求转发到后端 5000 端口。

访问浏览器即可使用。

## 常见问题

### 智能问答/对话失败

1. **401 Authentication Fails / Api key is invalid**：API Key 失效或 Base URL 不匹配。
   - token-cloud 代理：`DEEPSEEK_BASE_URL=https://www.token-cloud.cn/v1`
   - DeepSeek 官方：`DEEPSEEK_BASE_URL=https://api.deepseek.com`
2. **403 This token has no access to model**：模型名错误。
   - token-cloud 代理可用模型：`DeepSeek-V4-Flash`
   - DeepSeek 官方可用模型：`deepseek-chat`
3. **Base URL 结尾不要加 `/chat/completions`**：SDK 会自动拼接路径，重复会导致 404。

### Embedding / 文档向量化失败

- 确认 `EMBEDDING_API_KEY` 已在 SiliconFlow 注册获取
- SiliconFlow 有免费额度，注册地址：https://siliconflow.cn

## Git 协作 & 上传 GitHub

### 首次克隆

```bash
git clone https://github.com/acline123/small.git
cd small
```

### 日常开发流程

```bash
# 1. 拉取最新代码
git pull origin main

# 2. 修改代码后提交
git add .
git commit -m "描述你的改动"

# 3. 推送到 GitHub
git push origin main
```

### API Key 保护机制

`.env` 文件已在 `.gitignore` 中配置忽略，**不会被上传到 GitHub**。每位同学 clone 后需根据 `.env.example` 模板自行创建：

```bash
cd StudyAgent/backend
copy .env.example .env
# 编辑 .env 填入自己的 API Key
```

> 如果某个文件已经不小心被 Git 追踪了，运行 `git rm --cached <文件>` 可以只从 Git 移除而不删除本地文件。

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/upload | 上传文档 |
| GET | /api/documents | 文档列表 |
| DELETE | /api/document?id= | 删除文档 |
| POST | /api/chat | 智能问答 |
| POST | /api/summary | 文档摘要 |
| GET | /api/history | 聊天历史 |
| POST | /api/exercise/assess | 评估知识水平 |
| POST | /api/exercise/generate | 生成习题 |
| POST | /api/exercise/submit | 提交答案（自动批改） |
| GET | /api/exercise/history | 答题历史 |
| GET | /api/exercise/stats | 答题统计 |

> **POST /api/chat 返回新增字段**：`analysis`（学习分析结果）、`tool_used`（使用的工具）、`sources`（参考来源）。分析失败时自动降级返回空结构。

## 项目结构

```
StudyAgent/
├── frontend/          # Vue3 前端
├── backend/           # Flask 后端
│   ├── app/
│   │   ├── agent/     # Agent 核心 + 意图识别 + 记忆
│   │   ├── analysis/  # 学习分析模块
│   │   ├── tools/     # MCP Tools（5个）
│   │   ├── routes/    # API 路由
│   │   ├── rag/       # RAG 检索
│   │   ├── kg/        # 知识图谱
│   │   └── models/    # 数据库模型
│   └── ...
└── docs/              # 设计文档
```

## 课程要求对照

| 要求 | 实现 |
|------|------|
| 调用 LLM API | `app/llm/deepseek.py` |
| RAG 检索 | `app/rag/` |
| ≥2 MCP Tool | `app/tools/search_document.py`、`summary_document.py` |
| 多轮对话 | `app/agent/memory.py` + SQLite |
| Agent 工作流 | `app/agent/agent_core.py` + LLM 意图识别 |

## 修复记录

### 2026-07-10

- **新增智能习题功能**：后端新增 Exercise/ExerciseResult 表 + 5 个 API，MCP Tool `generate_exercise` 通过 LLM 评估知识水平并生成适配习题（选择/判断/填空），前端新增 Exercise 页面逐题作答即时批改。
- **合并组员学习分析模块**：`app/analysis/` 模块在每次提问时并行分析用户水平（ThreadPoolExecutor），结合聊天历史生成问题总结、知识评估和学习路线。Agent 并行架构：分析+意图识别同时执行。
- **合并组员其他更新**：会话置顶（pinned 字段）、Bing 搜索增强、ChatWindow 可视化渲染组件。
- **修复可视化缺失**：组员提交中缺少 Mermaid 图表生成后端模块，暂不可用。剩余功能均可正常运行。

### 2026-07-07

- **修复 API Key 认证失败（401）**：`.env` 中 `DEEPSEEK_BASE_URL` 和 `DEEPSEEK_MODEL` 配置错误。项目实际使用老师提供的 token-cloud 代理平台（`www.token-cloud.cn`），而非 DeepSeek 官方 API。修正 `BASE_URL` 为 `https://www.token-cloud.cn/v1`，模型名为 `DeepSeek-V4-Flash`。
- **修复 Base URL 路径重复**：SDK 自动拼接 `/chat/completions`，`.env` 中不应在 Base URL 末尾包含该路径。
- **移动 README 到项目根目录**：原位于 `StudyAgent/README.md`，移至 `README.md`，与内部路径引用保持一致。

### 2026-06-30

- **修复 Flask 实例变量名冲突**：`app/__init__.py` 中 `app = Flask(__name__)` 与包名 `app` 重名，`import app.tools` 后 Flask 实例被模块覆盖，导致 `AttributeError: module 'app' has no attribute 'register_blueprint'`。已将 Flask 实例变量重命名为 `flask_app`。
