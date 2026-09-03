# StudyAgent — 基于 RAG 的智能学习助手 Agent

《智能 Agent 应用开发项目》课程实践项目。

## 功能

- 文档上传（PDF / DOCX / TXT / PPTX）并自动构建 ChromaDB 知识库（知识图谱后台异步构建，不阻塞上传）
- RAG 检索增强问答（LangChain + ChromaDB）
- **流式输出**：聊天 SSE 流式渲染（`/api/chat/stream`），回复逐字上屏，首字延迟大幅降低
- Agent 工作流：规则引擎意图识别 → MCP Tool 调用 → DeepSeek 生成
- **标准 MCP Tool**（官方 mcp SDK / FastMCP，同进程 in-memory 调用）：`search_document`、`summary_document`、`generate_exercise`、`query_knowledge_graph`、`web_search`
- **学习分析**：每次提问自动分析用户水平（Beginner/Intermediate/Advanced），生成个性化学习路线（后台执行、限时降级，不阻塞回复）
- **智能习题**：基于聊天记录和文档生成习题（选择/判断/填空），自动批改+解析（填空题支持模糊匹配与 LLM 语义判分）
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
| MCP | 官方 mcp Python SDK（FastMCP），同进程 in-memory transport |

## 前置依赖

### 外部服务（需要注册获取 API Key）

| 服务 | 用途 | 获取地址 |
|------|------|----------|
| DeepSeek（token-cloud 代理） | 对话生成 & 意图识别 | 由授课老师提供 Key（模型：DeepSeek-V4-Flash） |
| SiliconFlow | 文本向量化（Embedding） | https://siliconflow.cn（有免费额度） |

> **说明**：本项目使用 token-cloud 代理（`api.token-cloud.cn`）访问 DeepSeek。如果你自己申请 DeepSeek 官方 Key，需将 `backend/.env` 中 `DEEPSEEK_BASE_URL` 改为 `https://api.deepseek.com`，`DEEPSEEK_MODEL` 改为 `deepseek-chat`。

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
mcp>=1.0.0,<2
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
DEEPSEEK_BASE_URL=https://api.token-cloud.cn/v1
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

# 学习分析限时（秒），后台执行，超时降级不阻塞回复
ANALYSIS_TIMEOUT=3
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
   - token-cloud 代理：`DEEPSEEK_BASE_URL=https://api.token-cloud.cn/v1`
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
| POST | /api/chat | 智能问答（非流式） |
| POST | /api/chat/stream | 智能问答（SSE 流式，推荐） |
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
│   │   ├── mcp/       # 标准 MCP server（注册工具）+ client（call_tool）
│   │   ├── tools/     # 5 个工具函数的业务实现
│   │   ├── routes/    # API 路由
│   │   ├── rag/       # RAG 检索
│   │   ├── kg/        # 知识图谱
│   │   └── models/    # 数据库模型
│   └── ...
└── docs/              # 设计文档
```

## MCP 工具机制（标准 MCP 实现）

> 本项目的 5 个工具基于**官方 MCP（Model Context Protocol）Python SDK** 实现，通过**同进程 in-memory transport** 注册与调用，不依赖额外进程或端口。

### 哪些功能用到了 MCP

| 用户输入 / 操作 | 意图 | MCP 工具 | 实际作用 |
|------|------|---------|---------|
| 问“搜索/查找一下 XX” | `search` | `search_document` | 知识库向量检索 |
| 问“总结/摘要文档” | `summary` | `summary_document` | 读文档 → LLM 生成摘要 |
| 问“联网/最新的 XX” | `web_search` | `web_search` | 网页搜索（duckduckgo） |
| 问“XX 和 YY 什么关系” | `graph_query` | `query_knowledge_graph` | 查询知识图谱实体关系 |
| 问“出几道题” / 页面“生成习题” | `exercise` | `generate_exercise` | 评估水平 + 生成习题并存库 |
| 页面“文档摘要” | — | `summary_document` | 经 `/api/summary` 调用 |

> 普通对话问答**不**走 MCP，而是直接 RAG 检索；只有当规则引擎（`app/agent/intent.py`）把输入识别为上述动作时，才经 MCP 调用对应工具。

### MCP 在这里起什么作用

它把 5 个业务函数包装成**带标准元数据的 MCP 工具**：每个工具都有名称、描述（docstring）和参数 JSON Schema（由类型注解自动生成），可被 `list_tools()` 发现、被 `call_tool()` 按名调用，参数在进入函数前由 pydantic 自动校验。这套协议是业界标准，换成任何 MCP client 都能识别这些工具。

### 怎么实现的

**① Server：把函数注册为工具**（`app/mcp/server.py`）

```python
mcp = FastMCP("study-agent")
mcp.tool()(search_document)   # 函数签名+docstring → 工具名/描述/参数Schema
mcp.tool()(summary_document)
mcp.tool()(web_search)
mcp.tool()(query_knowledge_graph)
mcp.tool()(generate_exercise)
```

工具函数（`app/tools/*.py`）靠类型注解 + docstring 提供 schema 与描述：

```python
def search_document(query: str, top_k: int = 4, document_id: int = None) -> dict:
    """在知识库中搜索与问题相关的文档内容。"""
    docs = similarity_search(query, top_k=top_k, document_id=document_id)
    ...
```

**② Client：同步调用封装**（`app/mcp/client.py`）

```python
async with create_connected_server_and_client_session(mcp) as session:
    result = await session.call_tool(name, args)   # in-memory 直连，不走网络
```

内部完成标准 MCP `initialize` 握手 → 发送 `CallToolRequest` → server 分发到对应函数 → 返回 `CallToolResult`。工具返回 dict 时 FastMCP 序列化为 JSON 文本，client 解析还原；工具抛异常时 `isError=true`，client 转成 `RuntimeError` 抛出；`None` 参数在发送前被过滤（避免 pydantic 对 Optional 字段报错）。

**③ 决策：谁决定调用哪个工具**（`app/agent/agent_core.py` → `_route_and_build`）

```python
intent = recognize_intent(message)                 # 关键词规则
if intent == "search":
    tool_result = call_tool("search_document", {"query": message, ...})
elif intent == "exercise":
    tool_result = call_tool("generate_exercise", {"session_id": ..., "types": ..., "count": ...})
...
```

**调用时序**

```
用户 → 规则引擎识别意图 → MCP client.call_tool(name, args)
                                    │  (in-memory transport)
                                    ▼
                         MCP server(同进程) → 分发到工具函数 → 执行业务逻辑
                                    │
                                    ▼
                         结果(dict → JSON) 返回 client → 格式化后拼进 prompt → DeepSeek 生成回复
```

**与改造前对比**：改造前 5 个工具是自定义 `BaseTool` 类 + `ToolRegistry` 注册表，属于项目私有约定；改造后统一为标准 MCP 协议。若未来想把工具拆成独立服务，只需把 transport 换成 stdio 或 streamable HTTP，MCP server 端代码无需改动。

## 课程要求对照

| 要求 | 实现 |
|------|------|
| 调用 LLM API | `app/llm/deepseek.py` |
| RAG 检索 | `app/rag/` |
| ≥2 MCP Tool（标准 MCP 协议） | 5 个工具注册于 `app/mcp/server.py`，实现于 `app/tools/*`，经 `app/mcp/client.py` 调用 |
| 多轮对话 | `app/agent/memory.py` + SQLite |
| Agent 工作流 | `app/agent/agent_core.py` + 规则引擎意图识别（`app/agent/intent.py`） |

## 修复记录

### 2026-09-03

- **工具层改造为标准 MCP 协议**：将 5 个自定义 `BaseTool` 工具类重构为带类型注解/docstring 的纯函数（`app/tools/*.py`），删除 `app/tools/base.py` 私有注册表。新增 `app/mcp/server.py`（FastMCP 注册工具）与 `app/mcp/client.py`（同步 `call_tool`，同进程 in-memory transport）。`app/agent/agent_core.py`、`app/routes/exercise.py`、`app/routes/summary.py` 全部改经 `call_tool` 调用。新增依赖 `mcp>=1.0.0,<2`。功能逻辑不变，详见上方「MCP 工具机制」章节。

### 2026-09-01

- **修复 token-cloud API 域名变更**：代理平台 API 已从 `www.token-cloud.cn` 迁移至 `api.token-cloud.cn`，旧域名现在只保留官网页面，导致 `/api/chat` 返回连接错误（APIConnectionError）。已更新 `.env` / `.env.example` / README 中的 `DEEPSEEK_BASE_URL` 为 `https://api.token-cloud.cn/v1`，Key 无需更换。
- **优化响应延迟（聊天/上传/习题）**：
  - 聊天新增 `/api/chat/stream` SSE 流式端点，前端逐字渲染，首字延迟约 7s（原整段等待 10~30s）；意图识别改为规则引擎（`app/agent/intent.py`），去掉每次聊天的一次 LLM 调用；学习分析移至后台线程限时等待（`ANALYSIS_TIMEOUT`，默认 3s），超时降级不阻塞回复。
  - 习题生成合并为一次 LLM 调用（评估水平 + 出题，原两次串行）；填空题批改先做规范化模糊匹配，未命中时 LLM 判分并行执行。
  - 上传时知识图谱构建移到后台线程，上传请求不再等待图谱 LLM 提取（实测该调用约 48s）；图谱提取范围缩小（1500 字 / 10 实体）。
  - DeepSeek client 改为惰性单例，新增 `chat_stream()` 流式生成。

### 2026-07-10

- **新增智能习题功能**：后端新增 Exercise/ExerciseResult 表 + 5 个 API，MCP Tool `generate_exercise` 通过 LLM 评估知识水平并生成适配习题（选择/判断/填空），前端新增 Exercise 页面逐题作答即时批改。
- **合并组员学习分析模块**：`app/analysis/` 模块在每次提问时并行分析用户水平（ThreadPoolExecutor），结合聊天历史生成问题总结、知识评估和学习路线。Agent 并行架构：分析+意图识别同时执行。
- **合并组员其他更新**：会话置顶（pinned 字段）、Bing 搜索增强、ChatWindow 可视化渲染组件。
- **修复可视化缺失**：组员提交中缺少 Mermaid 图表生成后端模块，暂不可用。剩余功能均可正常运行。
- **修复聊天消息**： 修复 markdown 格式渲染，可以正常显示内容。

### 2026-07-07

- **修复 API Key 认证失败（401）**：`.env` 中 `DEEPSEEK_BASE_URL` 和 `DEEPSEEK_MODEL` 配置错误。项目实际使用老师提供的 token-cloud 代理平台（`www.token-cloud.cn`），而非 DeepSeek 官方 API。修正 `BASE_URL` 为 `https://www.token-cloud.cn/v1`，模型名为 `DeepSeek-V4-Flash`。
- **修复 Base URL 路径重复**：SDK 自动拼接 `/chat/completions`，`.env` 中不应在 Base URL 末尾包含该路径。
- **移动 README 到项目根目录**：原位于 `StudyAgent/README.md`，移至 `README.md`，与内部路径引用保持一致。

### 2026-06-30

- **修复 Flask 实例变量名冲突**：`app/__init__.py` 中 `app = Flask(__name__)` 与包名 `app` 重名，`import app.tools` 后 Flask 实例被模块覆盖，导致 `AttributeError: module 'app' has no attribute 'register_blueprint'`。已将 Flask 实例变量重命名为 `flask_app`。
