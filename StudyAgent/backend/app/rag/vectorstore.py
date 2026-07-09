from langchain_chroma import Chroma

import config
from app.rag.embedder import get_embeddings

_vectorstore = None


def get_vectorstore() -> Chroma:
    global _vectorstore
    if _vectorstore is None:
        _vectorstore = Chroma(
            collection_name="study_agent_kb",
            embedding_function=get_embeddings(),
            persist_directory=str(config.CHROMA_DIR),
        )
    return _vectorstore


def add_documents(chunks, document_id: int, filename: str):
    """将文档块写入向量库，附带元数据。"""
    for chunk in chunks:
        chunk.metadata["document_id"] = str(document_id)
        chunk.metadata["filename"] = filename
    vs = get_vectorstore()
    vs.add_documents(chunks)
    return len(chunks)


def delete_by_document_id(document_id: int):
    """删除指定文档的所有向量。"""
    vs = get_vectorstore()
    try:
        vs._collection.delete(where={"document_id": str(document_id)})
    except Exception:
        pass


def similarity_search(query: str, top_k: int = None, document_id: int = None, source: str = None):
    """语义检索，支持按 document_id 或 source 过滤。"""
    k = top_k or config.RETRIEVE_TOP_K
    vs = get_vectorstore()
    filters = {}
    if document_id:
        filters["document_id"] = str(document_id)
    if source:
        filters["source"] = source
    if filters:
        return vs.similarity_search(query, k=k, filter=filters)
    return vs.similarity_search(query, k=k)
