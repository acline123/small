RAG_SYSTEM_PROMPT = """你是一名智能学习助手，基于提供的知识库内容回答用户问题。
要求：
1. 优先使用【参考资料】中的内容回答
2. 如果资料不足，请诚实说明
3. 回答简洁清晰，适合大学生理解
4. 结合对话历史理解用户的追问（如"那UDP呢"应联系上文）
5. 涉及代码时，用 markdown 代码块格式
"""


def build_rag_prompt(history: list[dict], context: str, message: str) -> list[dict]:
    messages = [{"role": "system", "content": RAG_SYSTEM_PROMPT}]
    for item in history:
        messages.append({"role": item["role"], "content": item["content"]})
    user_content = f"【参考资料】\n{context}\n\n【用户问题】\n{message}"
    messages.append({"role": "user", "content": user_content})
    return messages


def build_tool_prompt(history: list[dict], tool_name: str, tool_result: str, message: str) -> list[dict]:
    system = f"你是一名智能学习助手。已调用工具 `{tool_name}` 获取结果，请基于工具结果回答用户。"
    messages = [{"role": "system", "content": system}]
    for item in history:
        messages.append({"role": item["role"], "content": item["content"]})
    user_content = f"【工具结果】\n{tool_result}\n\n【用户问题】\n{message}"
    messages.append({"role": "user", "content": user_content})
    return messages


def format_search_results(results: list[dict]) -> str:
    if not results:
        return "未找到相关内容。"
    parts = []
    for i, item in enumerate(results, 1):
        parts.append(f"[{i}] 来源：{item.get('filename', '未知')}\n{item.get('content', '')}")
    return "\n\n".join(parts)


def format_web_search_results(results: list[dict]) -> str:
    if not results:
        return "未找到相关网页。"
    parts = []
    for i, item in enumerate(results, 1):
        title = item.get("title", "无标题")
        url = item.get("url", "")
        snippet = item.get("snippet", "")
        parts.append(f"[{i}] {title}\n链接：{url}\n摘要：{snippet}")
    return "\n\n".join(parts)


def format_graph_results(results: list[dict]) -> str:
    if not results:
        return "知识图谱中未找到相关实体。"
    parts = []
    for i, item in enumerate(results, 1):
        relations = item.get("relations", [])
        rel_text = "\n".join(f"  - {r}" for r in relations) if relations else "  （无关联关系）"
        parts.append(f"[{i}] 实体：{item.get('name')}（{item.get('type')}）\n关联：\n{rel_text}")
    return "\n\n".join(parts)
