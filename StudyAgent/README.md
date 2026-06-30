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

## 快速启动

### 1. 后端

```bash
cd StudyAgent/backend
python -m venv .venv
# Windows
.venv\Scripts\activate
pip install -r requirements.txt

# 复制并填写 API Key
copy .env.example .env
```

`.env` 需配置：

- `DEEPSEEK_API_KEY`：DeepSeek 对话 API Key
- `EMBEDDING_API_KEY` / `EMBEDDING_BASE_URL` / `EMBEDDING_MODEL`：Embedding 服务（OpenAI 兼容格式）

> **说明**：DeepSeek 官方 API 目前不提供 Embedding 端点。项目 `embedder.py` 封装了 DeepSeek Embedding 模块，通过 OpenAI 兼容接口调用 Embedding 服务。推荐使用 [SiliconFlow](https://siliconflow.cn) 的 `BAAI/bge-m3` 模型（中文效果好，有免费额度）。

```bash
python run.py
```

后端默认运行在 http://localhost:5000

### 2. 前端

```bash
cd StudyAgent/frontend
npm install
npm run dev
```

前端默认运行在 http://localhost:5173

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
