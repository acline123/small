"""习题 API 路由 — 知识水平评估、生成习题、提交批改。"""
import json
import re
from concurrent.futures import ThreadPoolExecutor

from flask import Blueprint, request

from app.agent.memory import load_history
from app.llm.deepseek import chat
from app.models.database import Document, Exercise, ExerciseResult, get_db
from app.tools.exercise_generator import exercise_generator
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


def _parse_json(reply: str, default=None):
    """从 LLM 回复中提取 JSON。"""
    try:
        match = re.search(r"(\[.*\]|\{.*\})", reply, re.DOTALL)
        if match:
            return json.loads(match.group())
    except (json.JSONDecodeError, Exception):
        pass
    return default


def _normalize_answer(text: str) -> str:
    """规范化答案：全角转半角、去空白与标点、统一小写，用于宽松比较。"""
    text = (text or "").strip().lower()
    for full, half in [
        ("，", ","), ("。", "."), ("！", "!"), ("？", "?"), ("：", ":"),
        ("；", ";"), ("（", "("), ("）", ")"), ("“", '"'), ("”", '"'),
        ("‘", "'"), ("’", "'"),
    ]:
        text = text.replace(full, half)
    return re.sub(r"[\s,.;:!?'\"()\-_、/]", "", text)


def _llm_judge_fill_blank(question: str, correct_answer: str, user_answer: str) -> bool:
    """填空题 LLM 语义判分（单题）。"""
    try:
        check_reply = chat(
            [
                {"role": "system", "content": "你是一个批改助手。判断用户答案与标准答案含义是否一致。只输出 true 或 false。"},
                {"role": "user", "content": f"题目：{question}\n标准答案：{correct_answer}\n用户答案：{user_answer}\n含义一致？"},
            ],
            temperature=0,
        )
        return "true" in check_reply.lower()
    except Exception:
        return False


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
    """根据知识水平和文档内容生成习题（评估 + 生成合并为一次 LLM 调用）。"""
    data = request.get_json(silent=True) or {}
    session_id = (data.get("session_id") or "").strip()
    types = data.get("types") or ["choice", "true_false", "fill_blank"]
    count = int(data.get("count", 5))
    document_id = data.get("document_id")

    if not session_id:
        return error("缺少 session_id")
    if count < 1 or count > 20:
        return error("题量范围为 1-20")

    result = exercise_generator.run(
        session_id=session_id, types=types, count=count, document_id=document_id
    )
    if result.get("error"):
        return error(result["error"], code=400)
    return success(result)


@exercise_bp.route("/exercise/submit", methods=["POST"])
def submit_answer():
    """提交答案并自动批改（填空题 LLM 判分并行执行）。"""
    data = request.get_json(silent=True) or {}
    session_id = (data.get("session_id") or "").strip()
    answers = data.get("answers") or []

    if not session_id:
        return error("缺少 session_id")
    if not answers:
        return error("缺少答案")

    # 阶段 1：读取习题并做精确/宽松匹配，标记需要 LLM 判分的填空题
    db = get_db()
    items = []
    try:
        for ans in answers:
            ex_id = ans.get("exercise_id")
            user_answer = (ans.get("user_answer") or "").strip()
            exercise = db.query(Exercise).filter(Exercise.id == ex_id).first()

            if not exercise:
                items.append({"exercise_id": ex_id, "error": "习题不存在"})
                continue

            correct_answer = (exercise.answer or "").strip()
            is_correct = user_answer == correct_answer
            need_llm = False

            if not is_correct and exercise.question_type == "fill_blank":
                norm_user = _normalize_answer(user_answer)
                if norm_user and norm_user == _normalize_answer(correct_answer):
                    is_correct = True
                else:
                    need_llm = True

            items.append({
                "exercise": exercise,
                "user_answer": user_answer,
                "correct_answer": correct_answer,
                "is_correct": is_correct,
                "need_llm": need_llm,
            })
    finally:
        db.close()

    # 阶段 2：需要 LLM 判分的填空题并行执行
    pending = [it for it in items if it.get("need_llm")]
    if pending:
        with ThreadPoolExecutor(max_workers=min(4, len(pending))) as executor:
            futures = [
                executor.submit(
                    _llm_judge_fill_blank,
                    it["exercise"].question,
                    it["correct_answer"],
                    it["user_answer"],
                )
                for it in pending
            ]
            for it, future in zip(pending, futures):
                it["is_correct"] = future.result()

    # 阶段 3：统计并保存答题记录
    db = get_db()
    results = []
    correct_count = 0
    try:
        for it in items:
            if "error" in it:
                results.append(it)
                continue

            exercise = it["exercise"]
            is_correct = it["is_correct"]
            if is_correct:
                correct_count += 1

            rec = ExerciseResult(
                exercise_id=exercise.id,
                session_id=session_id,
                user_answer=it["user_answer"],
                is_correct=1 if is_correct else 0,
            )
            db.add(rec)

            results.append({
                "exercise_id": exercise.id,
                "is_correct": is_correct,
                "correct_answer": it["correct_answer"],
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
