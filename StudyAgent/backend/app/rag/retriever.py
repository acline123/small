import threading

from app.kg.builder import build_knowledge_graph
from app.rag.loader import load_document
from app.rag.splitter import split_documents
from app.rag.vectorstore import add_documents


def _build_graph_in_background(chunks, document_id: int):
    """后台线程构建知识图谱（LLM 提取耗时较长，不阻塞上传请求）。"""
    try:
        build_knowledge_graph(chunks, document_id)
    except Exception:
        pass


def build_knowledge_base(file_path: str, file_type: str, document_id: int, filename: str) -> int:
    """读取 → 切分 → 向量化 → 存入 ChromaDB → 后台构建知识图谱。"""
    documents = load_document(file_path, file_type)
    chunks = split_documents(documents)
    if not chunks:
        return 0
    count = add_documents(chunks, document_id, filename)
    threading.Thread(
        target=_build_graph_in_background, args=(chunks, document_id), daemon=True
    ).start()
    return count
