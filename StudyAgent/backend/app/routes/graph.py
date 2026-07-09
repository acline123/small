from flask import Blueprint, request

from app.kg.query import get_graph_data
from app.utils.response import error, success

graph_bp = Blueprint("graph", __name__)


@graph_bp.route("/graph", methods=["GET"])
def get_graph():
    document_id = request.args.get("document_id", type=int)
    try:
        data = get_graph_data(document_id=document_id)
        return success(data)
    except Exception as exc:
        return error(f"获取知识图谱失败: {exc}", code=500)
