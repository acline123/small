"""习题生成 MCP Tool。"""
import json
import re

from app.agent.memory import load_history
from app.llm.deepseek import chat
from app.models.database import Document, Exercise, get_db
from app.rag.vectorstore import similarity_search
from app.tools.base import BaseTool

ASSESS_PROMPT = """你是一名学习评估专家。根据以下用户的对话记录和已上传的文档信息，
评估该用户的当前知识水平。

【聊天记录】
{history}

【已学文档】
{documents}

请只输出 JSON（不要其他文字）：
{{
  "level": "初级|中级|高级",
  "topics": ["已掌握或正在学习的知识点"],
  "strengths": ["擅长的领域"],
  "weaknesses": ["薄弱的领域"],
  "suggestion": "一句话学习建议"
}}"""

GENERATE_PROMPT = """根据以下参考资料，生成 {count} 道习题，难度适配 {level} 水平。

参考资料：
{context}

请只输出 JSON 数组（不要其他文字）：
[
  {{
    "question_type": "choice",
    "question": "题目",
    "options": ["A. 选项A", "B. 选项B", "C. 选项C", "D. 选项D"],
    "answer": "A",
    "explanation": "解析",
    "topic": "知识点"
  }},
  {{
    "question_type": "true_false",
    "question": "题目",
    "answer": "对",
    "explanation": "解析",
    "topic": "知识点"
  }},
  {{
    "question_type": "fill_blank",
    "question": "题目（用 ___ 表示填空位置）",
    "answer": "正确答案",
    "explanation": "解析",
    "topic": "知识点"
  }}
]"""


def _parse_json(reply: str, default=None):
    try:
        match = re.search(r"(\[.*\]|\{.*\})", reply, re.DOTALL)
        if match:
            return json.loads(match.group())
    except (json.JSONDecodeError, Exception):
        pass
    return default


class ExerciseGeneratorTool(BaseTool):
    name = "generate_exercise"
    description = "根据知识库内容和用户学习水平，自动生成适配习题（选择题/判断题/填空题）"

    def run(self, session_id=None, types=None, count=5, document_id=None, **_):
        if types is None:
            types = ["choice", "true_false", "fill_blank"]
        if not session_id:
            return {"exercises": [], "error": "缺少 session_id"}

        # 1. 获取聊天记录
        history = load_history(session_id, limit=10)
        history_text = "\n".join(
            f"[{h['role']}]: {h['content'][:300]}" for h in history
        ) or "（暂无聊天记录）"

        # 2. 获取文档列表
        db = get_db()
        try:
            docs = db.query(Document).order_by(Document.created_at.desc()).all()
            doc_text = "\n".join(d.filename for d in docs) or "（暂无文档）"
        finally:
            db.close()

        # 3. 评估水平
        assess_prompt = ASSESS_PROMPT.format(history=history_text, documents=doc_text)
        assess_reply = chat(
            [
                {"role": "system", "content": "你只输出 JSON，不做解释。"},
                {"role": "user", "content": assess_prompt},
            ],
            temperature=0.3,
        )
        level_data = _parse_json(assess_reply, {})
        level = level_data.get("level", "中级")

        # 4. 检索参考资料
        query = history_text[-300:] if history_text.strip() != "（暂无聊天记录）" else "知识点"
        docs_chunks = similarity_search(query, top_k=6, document_id=document_id)
        context = "\n\n".join(d.page_content[:500] for d in docs_chunks) or "（知识库暂无内容，请根据通用知识出题）"

        # 5. 生成习题
        generate_prompt = GENERATE_PROMPT.format(count=count, level=level, context=context[:6000])
        gen_reply = chat(
            [
                {"role": "system", "content": "你只输出 JSON 数组，不做解释。"},
                {"role": "user", "content": generate_prompt},
            ],
            temperature=0.7,
        )
        exercises_raw = _parse_json(gen_reply, [])

        # 6. 保存到数据库
        db = get_db()
        saved = []
        try:
            for ex in exercises_raw:
                q_type = ex.get("question_type", "choice")
                opts = json.dumps(ex.get("options", []), ensure_ascii=False) if q_type == "choice" else None
                record = Exercise(
                    session_id=session_id,
                    question_type=q_type,
                    question=ex.get("question", ""),
                    options=opts,
                    answer=ex.get("answer", ""),
                    explanation=ex.get("explanation", ""),
                    topic=ex.get("topic", ""),
                )
                db.add(record)
                db.flush()
                saved.append({
                    "id": record.id,
                    "question_type": q_type,
                    "question": record.question,
                    "options": ex.get("options") if q_type == "choice" else (
                        ["对", "错"] if q_type == "true_false" else None
                    ),
                    "topic": record.topic,
                })
            db.commit()
        finally:
            db.close()

        return {"exercises": saved, "level": level_data}


exercise_generator = ExerciseGeneratorTool()
