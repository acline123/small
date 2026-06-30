from app.rag.loader import load_document
from app.rag.splitter import split_documents
from app.rag.vectorstore import add_documents


def build_knowledge_base(file_path: str, file_type: str, document_id: int, filename: str) -> int:
    """读取 → 切分 → 向量化 → 存入 ChromaDB。"""
    documents = load_document(file_path, file_type)
    chunks = split_documents(documents)
    if not chunks:
        return 0
    return add_documents(chunks, document_id, filename)
