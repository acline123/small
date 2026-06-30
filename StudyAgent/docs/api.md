# API 接口文档

Base URL: `http://localhost:5000/api`

## 统一响应

```json
{ "code": 200, "message": "success", "data": {} }
```

## POST /upload

上传文档，multipart/form-data，字段 `file`。

## GET /documents

获取文档列表。

## DELETE /document?id={id}

删除文档及向量数据。

## POST /chat

```json
{ "session_id": "可选", "message": "用户问题" }
```

## POST /summary

```json
{ "document_id": 1 }
```

## GET /history

- `?session_id=xxx` 获取指定会话消息
- 无参数时返回会话列表
