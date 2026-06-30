import os

from flask import Blueprint, request

from app.models.database import Document, get_db
from app.rag.vectorstore import delete_by_document_id
from app.utils.response import error, success

document_bp = Blueprint("document", __name__)


@document_bp.route("/document", methods=["DELETE"])
def delete_document():
    doc_id = request.args.get("id", type=int)
    if not doc_id:
        return error("缺少文档 id")

    db = get_db()
    try:
        doc = db.query(Document).filter(Document.id == doc_id).first()
        if not doc:
            return error("文档不存在", code=404)

        if os.path.exists(doc.file_path):
            os.remove(doc.file_path)

        delete_by_document_id(doc_id)
        db.delete(doc)
        db.commit()
        return success(message="删除成功")
    finally:
        db.close()
