import json

from flask import Blueprint, Response, request, stream_with_context

from app.agent.agent_core import handle_chat, stream_chat
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


@chat_bp.route("/chat/stream", methods=["POST"])
def chat_stream_route():
    """SSE 流式对话：逐段产出回复，结束产出 done 事件（含 session_id、sources 等元信息）。"""
    data = request.get_json(silent=True) or {}
    message = (data.get("message") or "").strip()
    if not message:
        return error("消息不能为空")

    session_id = data.get("session_id")
    use_web_search = bool(data.get("web_search", False))

    def generate():
        try:
            for event in stream_chat(session_id, message, use_web_search=use_web_search):
                yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"
        except Exception as exc:
            yield f"data: {json.dumps({'type': 'error', 'message': f'对话失败: {exc}'}, ensure_ascii=False)}\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
