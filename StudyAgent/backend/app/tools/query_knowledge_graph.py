from app.kg.query import search_entities
from app.tools.base import BaseTool


class QueryKnowledgeGraphTool(BaseTool):
    name = "query_knowledge_graph"
    description = "在知识图谱中查询实体及其关联关系"

    def run(self, query: str, document_id: int = None, **_) -> dict:
        results = search_entities(query, document_id=document_id)
        return {"results": results, "count": len(results)}


query_knowledge_graph = QueryKnowledgeGraphTool()
