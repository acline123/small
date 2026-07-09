import json
import re

from app.llm.deepseek import chat

EXTRACT_PROMPT = """从以下学习资料文本中提取知识图谱的实体和关系。

要求：
1. 实体 name 使用原文中的术语，type 为：概念、技术、方法、人物、组织 之一
2. 关系 type 描述实体间的关系，如：包含、属于、实现、依赖、对比
3. 只提取文本中明确出现或可直接推断的内容，不要编造
4. 最多提取 15 个实体、20 条关系

只返回 JSON，格式：
{{"entities": [{{"name": "实体名", "type": "概念"}}], "relations": [{{"source": "实体A", "target": "实体B", "type": "关系"}}]}}

文本：
{text}
"""


def extract_entities_relations(text: str) -> dict:
    """使用 LLM 从文本中提取实体和关系。"""
    if not text.strip():
        return {"entities": [], "relations": []}

    truncated = text[:3000]
    try:
        reply = chat(
            [
                {"role": "system", "content": "你只输出 JSON，不做解释。"},
                {"role": "user", "content": EXTRACT_PROMPT.format(text=truncated)},
            ],
            temperature=0,
        )
        match = re.search(r"\{.*\}", reply, re.DOTALL)
        if match:
            data = json.loads(match.group())
            entities = data.get("entities", [])
            relations = data.get("relations", [])
            if isinstance(entities, list) and isinstance(relations, list):
                return {"entities": entities, "relations": relations}
    except Exception:
        pass
    return {"entities": [], "relations": []}
