from app.rag.vectorstore import similarity_search
from app.tools.base import BaseTool


class SearchDocumentTool(BaseTool):
    name = "search_document"
    description = "在知识库中搜索与问题相关的文档内容"

    def run(self, query: str, top_k: int = 4, document_id: int = None, **_) -> dict:
        docs = similarity_search(query, top_k=top_k, document_id=document_id)
        results = []
        for doc in docs:
            results.append(
                {
                    "content": doc.page_content,
                    "filename": doc.metadata.get("filename", "未知"),
                    "document_id": doc.metadata.get("document_id"),
                }
            )
        return {"results": results, "count": len(results)}


search_document = SearchDocumentTool()
