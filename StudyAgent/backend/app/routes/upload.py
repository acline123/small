import os

from flask import Blueprint, request

from app.models.database import Document, get_db
from app.rag.retriever import build_knowledge_base
from app.utils.file_utils import allowed_file, get_file_type, save_upload_file
from app.utils.response import error, success

upload_bp = Blueprint("upload", __name__)


@upload_bp.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return error("未选择文件")
    file = request.files["file"]
    if not file.filename:
        return error("文件名为空")
    if not allowed_file(file.filename):
        return error("仅支持 PDF、DOCX、TXT 格式")

    filename, file_path, file_size = save_upload_file(file)
    file_type = get_file_type(filename)

    db = get_db()
    try:
        doc = Document(
            filename=filename,
            file_path=file_path,
            file_type=file_type,
            file_size=file_size,
            status="processing",
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)

        try:
            chunk_count = build_knowledge_base(file_path, file_type, doc.id, filename)
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
                "file_type": doc.file_type,
                "chunk_count": doc.chunk_count,
                "status": doc.status,
            },
            message="上传成功",
        )
    finally:
        db.close()


@upload_bp.route("/documents", methods=["GET"])
def list_documents():
    db = get_db()
    try:
        docs = db.query(Document).order_by(Document.created_at.desc()).all()
        data = [
            {
                "id": d.id,
                "filename": d.filename,
                "file_type": d.file_type,
                "file_size": d.file_size,
                "chunk_count": d.chunk_count,
                "status": d.status,
                "created_at": d.created_at.strftime("%Y-%m-%d %H:%M:%S") if d.created_at else "",
            }
            for d in docs
        ]
        return success(data)
    finally:
        db.close()
