"""习题 API 路由 — 知识水平评估、生成习题、提交批改。"""
import json
import re

from flask import Blueprint, request

from app.agent.memory import load_history
from app.llm.deepseek import chat
from app.models.database import Document, Exercise, ExerciseResult, get_db
from app.rag.vectorstore import similarity_search
from app.utils.response import error, success

exercise_bp = Blueprint("exercise", __name__)

# ---------- LLM Prompts ----------

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
题型：选择题、判断题、填空题。

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
]

注意：
- 选择题的 answer 是选项字母（如 "A"）
- 判断题的 answer 是 "对" 或 "错"
- 填空题的 answer 是完整填空内容"""


def _parse_json(reply: str, default=None):
    """从 LLM 回复中提取 JSON。"""
    try:
        match = re.search(r"(\[.*\]|\{.*\})", reply, re.DOTALL)
        if match:
            return json.loads(match.group())
    except (json.JSONDecodeError, Exception):
        pass
    return default


# ---------- Routes ----------


@exercise_bp.route("/exercise/assess", methods=["POST"])
def assess_level():
    """评估用户当前知识水平。"""
    data = request.get_json(silent=True) or {}
    session_id = (data.get("session_id") or "").strip()
    if not session_id:
        return error("缺少 session_id")

    # 获取聊天记录
    history = load_history(session_id, limit=10)
    history_text = "\n".join(
        f"[{h['role']}]: {h['content'][:300]}" for h in history
    ) or "（暂无聊天记录）"

    # 获取已上传文档列表
    db = get_db()
    try:
        docs = db.query(Document).order_by(Document.created_at.desc()).all()
        doc_text = "\n".join(d.filename for d in docs) or "（暂无文档）"
    finally:
        db.close()

    prompt = ASSESS_PROMPT.format(history=history_text, documents=doc_text)
    reply = chat(
        [
            {"role": "system", "content": "你只输出 JSON，不做解释。"},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
    )
    result = _parse_json(reply, {})
    return success(result)


@exercise_bp.route("/exercise/generate", methods=["POST"])
def generate_exercise():
    """根据知识水平和文档内容生成习题。"""
    data = request.get_json(silent=True) or {}
    session_id = (data.get("session_id") or "").strip()
    types = data.get("types") or ["choice", "true_false", "fill_blank"]
    count = int(data.get("count", 5))
    document_id = data.get("document_id")

    if not session_id:
        return error("缺少 session_id")
    if count < 1 or count > 20:
        return error("题量范围为 1-20")

    # 1. 评估知识水平
    history = load_history(session_id, limit=10)
    history_text = "\n".join(
        f"[{h['role']}]: {h['content'][:300]}" for h in history
    ) or "（暂无聊天记录）"

    db = get_db()
    try:
        docs = db.query(Document).order_by(Document.created_at.desc()).all()
        doc_text = "\n".join(d.filename for d in docs) or "（暂无文档）"
    finally:
        db.close()

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

    # 2. 从向量库检索参考资料
    docs_chunks = similarity_search(history_text[-200:] if history_text.strip() != "（暂无聊天记录）" else "知识点", top_k=6, document_id=document_id)
    context = "\n\n".join(d.page_content[:500] for d in docs_chunks) or "（知识库暂无内容，请根据通用知识出题）"

    # 3. 生成习题
    generate_prompt = GENERATE_PROMPT.format(count=count, level=level, context=context[:6000])
    gen_reply = chat(
        [
            {"role": "system", "content": "你只输出 JSON 数组，不做解释。"},
            {"role": "user", "content": generate_prompt},
        ],
        temperature=0.7,
    )
    exercises_raw = _parse_json(gen_reply, [])

    # 4. 存入数据库
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

    return success({"exercises": saved, "level": level_data})


@exercise_bp.route("/exercise/submit", methods=["POST"])
def submit_answer():
    """提交答案并自动批改。"""
    data = request.get_json(silent=True) or {}
    session_id = (data.get("session_id") or "").strip()
    answers = data.get("answers") or []

    if not session_id:
        return error("缺少 session_id")
    if not answers:
        return error("缺少答案")

    db = get_db()
    results = []
    correct_count = 0

    try:
        for ans in answers:
            ex_id = ans.get("exercise_id")
            user_answer = (ans.get("user_answer") or "").strip()
            exercise = db.query(Exercise).filter(Exercise.id == ex_id).first()

            if not exercise:
                results.append({"exercise_id": ex_id, "error": "习题不存在"})
                continue

            correct_answer = (exercise.answer or "").strip()
            is_correct = user_answer == correct_answer

            # 填空题 LLM 辅助判断（宽松匹配）
            if exercise.question_type == "fill_blank" and not is_correct:
                check_reply = chat(
                    [
                        {"role": "system", "content": "你是一个批改助手。判断用户答案与标准答案含义是否一致。只输出 true 或 false。"},
                        {"role": "user", "content": f"题目：{exercise.question}\n标准答案：{correct_answer}\n用户答案：{user_answer}\n含义一致？"},
                    ],
                    temperature=0,
                )
                is_correct = "true" in check_reply.lower()

            if is_correct:
                correct_count += 1

            # 保存答题记录
            rec = ExerciseResult(
                exercise_id=ex_id,
                session_id=session_id,
                user_answer=user_answer,
                is_correct=1 if is_correct else 0,
            )
            db.add(rec)

            results.append({
                "exercise_id": ex_id,
                "is_correct": is_correct,
                "correct_answer": correct_answer,
                "explanation": exercise.explanation or "",
            })

        db.commit()
    finally:
        db.close()

    return success({
        "results": results,
        "score": correct_count,
        "total": len(answers),
    })


@exercise_bp.route("/exercise/history", methods=["GET"])
def exercise_history():
    """获取答题历史。"""
    session_id = request.args.get("session_id", "").strip()
    if not session_id:
        return error("缺少 session_id")

    db = get_db()
    try:
        records = (
            db.query(ExerciseResult)
            .filter(ExerciseResult.session_id == session_id)
            .order_by(ExerciseResult.created_at.desc())
            .limit(50)
            .all()
        )
        result = []
        for r in records:
            ex = db.query(Exercise).filter(Exercise.id == r.exercise_id).first()
            result.append({
                "id": r.id,
                "exercise_id": r.exercise_id,
                "question": ex.question if ex else "",
                "question_type": ex.question_type if ex else "",
                "user_answer": r.user_answer,
                "is_correct": bool(r.is_correct),
                "created_at": r.created_at.strftime("%Y-%m-%d %H:%M:%S") if r.created_at else "",
            })
        return success(result)
    finally:
        db.close()


@exercise_bp.route("/exercise/stats", methods=["GET"])
def exercise_stats():
    """获取答题统计。"""
    session_id = request.args.get("session_id", "").strip()
    if not session_id:
        return error("缺少 session_id")

    db = get_db()
    try:
        total = db.query(ExerciseResult).filter(ExerciseResult.session_id == session_id).count()
        correct = (
            db.query(ExerciseResult)
            .filter(ExerciseResult.session_id == session_id, ExerciseResult.is_correct == 1)
            .count()
        )
        # 按题型统计
        by_type = {}
        results = (
            db.query(ExerciseResult)
            .filter(ExerciseResult.session_id == session_id)
            .all()
        )
        for r in results:
            ex = db.query(Exercise).filter(Exercise.id == r.exercise_id).first()
            t = ex.question_type if ex else "unknown"
            if t not in by_type:
                by_type[t] = {"total": 0, "correct": 0}
            by_type[t]["total"] += 1
            if r.is_correct:
                by_type[t]["correct"] += 1

        # 按知识点统计
        by_topic = {}
        for r in results:
            ex = db.query(Exercise).filter(Exercise.id == r.exercise_id).first()
            topic = ex.topic if ex and ex.topic else "未分类"
            if topic not in by_topic:
                by_topic[topic] = {"total": 0, "correct": 0}
            by_topic[topic]["total"] += 1
            if r.is_correct:
                by_topic[topic]["correct"] += 1

        return success({
            "total": total,
            "correct": correct,
            "accuracy": round(correct / total * 100, 1) if total > 0 else 0,
            "by_type": by_type,
            "by_topic": by_topic,
        })
    finally:
        db.close()
