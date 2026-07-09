import os

from flask import Blueprint, request

import config
from app.kg.store import delete_graph_by_document
from app.models.database import Document, get_db
from app.rag.retriever import build_knowledge_base
from app.rag.vectorstore import delete_by_document_id
from app.utils.response import error, success

document_bp = Blueprint("document", __name__)


@document_bp.route("/document/rebuild", methods=["POST"])
def rebuild_document():
    """重新构建失败文档的知识库向量。"""
    data = request.get_json(silent=True) or {}
    doc_id = data.get("document_id") or request.args.get("id", type=int)
    if not doc_id:
        return error("缺少文档 id")

    missing = config.check_api_keys()
    if missing:
        return error(f"API Key 未配置：{', '.join(missing)}", code=500)

    db = get_db()
    try:
        doc = db.query(Document).filter(Document.id == doc_id).first()
        if not doc:
            return error("文档不存在", code=404)
        if not os.path.exists(doc.file_path):
            return error("文件已丢失，请重新上传", code=404)

        delete_by_document_id(doc_id)
        delete_graph_by_document(doc_id)
        doc.status = "processing"
        db.commit()

        try:
            chunk_count = build_knowledge_base(doc.file_path, doc.file_type, doc.id, doc.filename)
            doc.chunk_count = chunk_count
            doc.status = "ready"
        except Exception as exc:
            doc.status = "error"
            db.commit()
            return error(f"知识库构建失败: {exc}", code=500)

        db.commit()
        return success(
            {
                "document_id": doc.id,
                "filename": doc.filename,
                "chunk_count": doc.chunk_count,
                "status": doc.status,
            },
            message="重建成功",
        )
    finally:
        db.close()


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
        delete_graph_by_document(doc_id)
        db.delete(doc)
        db.commit()
        return success(message="删除成功")
    finally:
        db.close()
@document_bp.route('/document/content', methods=['GET'])
def get_document_content():
    doc_id = request.args.get('id', type=int)
    if not doc_id:
        return error('缺少文档 id')
    db = get_db()
    try:
        doc = db.query(Document).filter(Document.id == doc_id).first()
        if not doc:
            return error('文档不存在', code=404)
        if not os.path.exists(doc.file_path):
            return error('文件已丢失', code=404)
        from app.rag.loader import load_document
        from app.utils.file_utils import get_file_type
        file_type = get_file_type(doc.filename)
        documents = load_document(doc.file_path, file_type)
        content = '\n\n'.join(d.page_content for d in documents if d.page_content.strip())
        return success({
            'id': doc.id,
            'filename': doc.filename,
            'file_type': file_type,
            'file_size': doc.file_size,
            'content': content,
        })
    finally:
        db.close()
