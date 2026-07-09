# 数据库设计（SQLite）

## documents

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 文档 ID |
| filename | TEXT | 文件名 |
| file_path | TEXT | 存储路径 |
| file_type | TEXT | pdf/docx/txt |
| file_size | INTEGER | 字节数 |
| chunk_count | INTEGER | 文本块数 |
| status | TEXT | ready/processing/error |
| created_at | DATETIME | 上传时间 |

## sessions

| 字段 | 类型 | 说明 |
|------|------|------|
| id | TEXT PK | UUID 会话 ID |
| title | TEXT | 会话标题 |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

## chat_records

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 记录 ID |
| session_id | TEXT FK | 会话 ID |
| role | TEXT | user/assistant |
| content | TEXT | 消息内容 |
| tool_used | TEXT | 调用的工具 |
| created_at | DATETIME | 时间 |

## summaries

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | |
| document_id | INTEGER FK | 文档 ID |
| summary | TEXT | 摘要内容 |
| created_at | DATETIME | 生成时间 |
