from flask import Blueprint, request

from app.tools.summary_document import summary_document
from app.utils.response import error, success

summary_bp = Blueprint("summary", __name__)


@summary_bp.route("/summary", methods=["POST"])
def summary():
    data = request.get_json(silent=True) or {}
    document_id = data.get("document_id")
    if not document_id:
        return error("缺少 document_id")

    try:
        result = summary_document.run(document_id=int(document_id))
        return success(
            {
                "document_id": result.get("document_id"),
                "filename": result.get("filename", ""),
                "summary": result.get("summary", ""),
            }
        )
    except Exception as exc:
        return error(f"摘要生成失败: {exc}", code=500)
