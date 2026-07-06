from app.tools.base import registry
from app.tools.search_document import search_document
from app.tools.summary_document import summary_document
from app.tools.web_search import web_search
from app.tools.query_knowledge_graph import query_knowledge_graph

registry.register(search_document)
registry.register(summary_document)
registry.register(web_search)
registry.register(query_knowledge_graph)

__all__ = ["registry", "search_document", "summary_document", "web_search", "query_knowledge_graph"]
