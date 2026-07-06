# StudyAgent — 基于 RAG 的智能学习助手 Agent

《智能 Agent 应用开发项目》课程实践项目。

## 功能

- 文档上传（PDF / DOCX / TXT）并自动构建 ChromaDB 知识库
- RAG 检索增强问答（LangChain + ChromaDB）
- Agent 工作流：LLM 意图识别 → MCP Tool 调用 → DeepSeek 生成
- MCP Tool：`search_document`、`summary_document`
- 多轮对话 + SQLite 聊天记录
- Vue3 + Element Plus 前端三页面

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue3、Element Plus、Axios、Vite |
| 后端 | Python、Flask、LangChain |
| 向量库 | ChromaDB |
| 数据库 | SQLite |
| 大模型 | DeepSeek API |
| Embedding | BAAI/bge-m3（SiliconFlow） |

## 前置依赖

### 外部服务（需要注册获取 API Key）

| 服务 | 用途 | 获取地址 |
|------|------|----------|
| DeepSeek | 对话生成 & 意图识别 | https://platform.deepseek.com |
| SiliconFlow | 文本向量化（Embedding） | https://siliconflow.cn（有免费额度） |

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
# DeepSeek Chat API
DEEPSEEK_API_KEY=sk-你的deepseek-api-key
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat

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

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/upload | 上传文档 |
| GET | /api/documents | 文档列表 |
| DELETE | /api/document?id= | 删除文档 |
| POST | /api/chat | 智能问答 |
| POST | /api/summary | 文档摘要 |
| GET | /api/history | 聊天历史 |

## 项目结构

```
StudyAgent/
├── frontend/     # Vue3 前端
├── backend/      # Flask 后端
└── docs/         # 设计文档
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

### 2026-06-30

- **修复 Flask 实例变量名冲突**：`app/__init__.py` 中 `app = Flask(__name__)` 与包名 `app` 重名，`import app.tools` 后 Flask 实例被模块覆盖，导致 `AttributeError: module 'app' has no attribute 'register_blueprint'`。已将 Flask 实例变量重命名为 `flask_app`。
