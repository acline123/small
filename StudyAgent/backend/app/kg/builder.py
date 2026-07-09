from app.kg.extractor import extract_entities_relations
from app.kg.store import save_graph


def build_knowledge_graph(chunks, document_id: int) -> tuple[int, int]:
    """从文档块构建知识图谱。"""
    if not chunks:
        return 0, 0

    combined = "\n\n".join(c.page_content for c in chunks[:8])
    extracted = extract_entities_relations(combined)
    return save_graph(document_id, extracted.get("entities", []), extracted.get("relations", []))
