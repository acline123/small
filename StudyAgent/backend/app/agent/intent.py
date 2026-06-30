import json
import re

from app.llm.deepseek import chat

INTENT_PROMPT = """你是一个意图分类器。根据用户输入，判断应执行哪种动作。

可选意图（只返回 JSON，不要其他文字）：
- "chat"：普通问答，基于知识库回答学习问题
- "search"：用户明确要求搜索、查找文档中的内容
- "summary"：用户要求摘要、总结、概括文档

返回格式：
{"intent": "chat|search|summary", "document_id": null}

如果用户提到具体文档编号如"文档1"可提取 document_id，否则 document_id 为 null。

用户输入：{message}
"""


def recognize_intent(message: str) -> dict:
    """使用 LLM 进行意图识别。"""
    try:
        reply = chat(
            [
                {"role": "system", "content": "你只输出 JSON，不做解释。"},
                {"role": "user", "content": INTENT_PROMPT.format(message=message)},
            ],
            temperature=0,
        )
        match = re.search(r"\{.*\}", reply, re.DOTALL)
        if match:
            data = json.loads(match.group())
            intent = data.get("intent", "chat")
            if intent not in ("chat", "search", "summary"):
                intent = "chat"
            return {"intent": intent, "document_id": data.get("document_id")}
    except Exception:
        pass
    return {"intent": "chat", "document_id": None}
