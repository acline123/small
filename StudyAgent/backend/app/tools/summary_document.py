from app.llm.deepseek import chat
from app.models.database import Document, Summary, get_db
from app.rag.loader import load_document
from app.rag.vectorstore import similarity_search
from app.tools.base import BaseTool


class SummaryDocumentTool(BaseTool):
    name = "summary_document"
    description = "对指定文档或知识库内容生成摘要"

    def run(self, document_id: int = None, query: str = None, **_) -> dict:
        db = get_db()
        try:
            if document_id:
                cached = db.query(Summary).filter(Summary.document_id == document_id).first()
                if cached:
                    doc = db.query(Document).filter(Document.id == document_id).first()
                    return {
                        "summary": cached.summary,
                        "document_id": document_id,
                        "filename": doc.filename if doc else "",
                        "cached": True,
                    }

                doc = db.query(Document).filter(Document.id == document_id).first()
                if not doc:
                    return {"summary": "文档不存在", "document_id": document_id}
                documents = load_document(doc.file_path, doc.file_type)
                text = "\n".join(d.page_content for d in documents)
                filename = doc.filename
            else:
                docs = similarity_search(query or "文档主要内容", top_k=6)
                if not docs:
                    return {"summary": "知识库中暂无相关内容，请先上传文档。"}
                text = "\n\n".join(d.page_content for d in docs)
                filename = docs[0].metadata.get("filename", "知识库")

            if len(text) > 8000:
                text = text[:8000] + "..."

            messages = [
                {
                    "role": "system",
                    "content": "你是一名学习助手，请根据给定文档内容生成简洁、结构清晰的中文摘要。",
                },
                {"role": "user", "content": f"请为以下文档生成摘要：\n\n文件名：{filename}\n\n{text}"},
            ]
            summary = chat(messages, temperature=0.3)

            if document_id:
                db.add(Summary(document_id=document_id, summary=summary))
                db.commit()

            return {"summary": summary, "document_id": document_id, "filename": filename}
        finally:
            db.close()


summary_document = SummaryDocumentTool()
