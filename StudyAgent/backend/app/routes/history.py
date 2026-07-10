from flask import Blueprint, request

from app.models.database import ChatRecord, SessionModel, get_db
from app.utils.response import error, success

history_bp = Blueprint("history", __name__)


@history_bp.route("/history", methods=["GET"])
def history():
    session_id = request.args.get("session_id")
    limit = request.args.get("limit", 20, type=int)

    db = get_db()
    try:
        if session_id:
            records = (
                db.query(ChatRecord)
                .filter(ChatRecord.session_id == session_id)
                .order_by(ChatRecord.created_at.asc())
                .limit(limit * 2)
                .all()
            )
            messages = [
                {
                    "role": r.role,
                    "content": r.content,
                    "tool_used": r.tool_used,
                    "created_at": r.created_at.strftime("%Y-%m-%d %H:%M:%S") if r.created_at else "",
                }
                for r in records
            ]
            return success({"session_id": session_id, "messages": messages})

        sessions = (
            db.query(SessionModel)
            .order_by(SessionModel.pinned.desc(), SessionModel.updated_at.desc())
            .limit(limit)
            .all()
        )
        data = [
            {
                "session_id": s.id,
                "title": s.title or "新对话",
                "pinned": bool(s.pinned),
                "created_at": s.created_at.strftime("%Y-%m-%d %H:%M:%S") if s.created_at else "",
                "updated_at": s.updated_at.strftime("%Y-%m-%d %H:%M:%S") if s.updated_at else "",
            }
            for s in sessions
        ]
        return success(data)
    finally:
        db.close()


@history_bp.route("/session", methods=["DELETE"])
def delete_session():
    session_id = request.args.get("session_id") or (request.get_json(silent=True) or {}).get("session_id")
    if not session_id:
        return error("session_id 不能为空")

    db = get_db()
    try:
        session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
        if not session:
            return error("会话不存在", code=404)
        db.delete(session)
        db.commit()
        return success(message="会话已删除")
    finally:
        db.close()


@history_bp.route("/session/pin", methods=["PUT"])
def toggle_pin():
    data = request.get_json(silent=True) or {}
    session_id = data.get("session_id")
    if not session_id:
        return error("session_id 不能为空")

    db = get_db()
    try:
        session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
        if not session:
            return error("会话不存在", code=404)
        session.pinned = 0 if session.pinned else 1
        db.commit()
        return success({"pinned": bool(session.pinned)}, message="操作成功")
    finally:
        db.close()


@history_bp.route("/session/rename", methods=["PUT"])
def rename_session():
    data = request.get_json(silent=True) or {}
    session_id = data.get("session_id")
    title = (data.get("title") or "").strip()
    if not session_id:
        return error("session_id 不能为空")
    if not title:
        return error("标题不能为空")

    db = get_db()
    try:
        session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
        if not session:
            return error("会话不存在", code=404)
        session.title = title
        db.commit()
        return success({"title": session.title}, message="重命名成功")
    finally:
        db.close()
