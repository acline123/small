from flask import Blueprint, request

from app.agent.agent_core import handle_chat
from app.utils.response import error, success

chat_bp = Blueprint("chat", __name__)


@chat_bp.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    message = (data.get("message") or "").strip()
    if not message:
        return error("消息不能为空")

    session_id = data.get("session_id")
    use_web_search = bool(data.get("web_search", False))
    try:
        result = handle_chat(session_id, message, use_web_search=use_web_search)
        return success(result)
    except Exception as exc:
        return error(f"对话失败: {exc}", code=500)
