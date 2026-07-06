from flask import Blueprint, request

from app.models.database import ChatRecord, SessionModel, get_db
from app.utils.response import success

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
            .order_by(SessionModel.updated_at.desc())
            .limit(limit)
            .all()
        )
        data = [
            {
                "session_id": s.id,
                "title": s.title or "新对话",
                "created_at": s.created_at.strftime("%Y-%m-%d %H:%M:%S") if s.created_at else "",
                "updated_at": s.updated_at.strftime("%Y-%m-%d %H:%M:%S") if s.updated_at else "",
            }
            for s in sessions
        ]
        return success(data)
    finally:
        db.close()
