from app.kg.query import search_entities


def query_knowledge_graph(query: str, document_id: int = None) -> dict:
    """在知识图谱中查询实体及其关联关系。"""
    results = search_entities(query, document_id=document_id)
    return {"results": results, "count": len(results)}
