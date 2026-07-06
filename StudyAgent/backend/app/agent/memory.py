import config
from app.models.database import ChatRecord, SessionModel, get_db


def load_history(session_id: str, limit: int = None) -> list[dict]:
    """加载最近 N 轮对话作为上下文。"""
    limit = limit or config.MEMORY_LIMIT
    db = get_db()
    try:
        records = (
            db.query(ChatRecord)
            .filter(ChatRecord.session_id == session_id)
            .order_by(ChatRecord.created_at.desc())
            .limit(limit * 2)
            .all()
        )
        records.reverse()
        return [{"role": r.role, "content": r.content} for r in records]
    finally:
        db.close()


def save_message(session_id: str, role: str, content: str, tool_used: str = None):
    db = get_db()
    try:
        session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
        if not session:
            session = SessionModel(id=session_id, title=content[:50] if role == "user" else "新对话")
            db.add(session)
        elif role == "user" and not session.title:
            session.title = content[:50]
        db.add(
            ChatRecord(
                session_id=session_id,
                role=role,
                content=content,
                tool_used=tool_used,
            )
        )
        db.commit()
    finally:
        db.close()
