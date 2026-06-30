from app.tools.base import registry
from app.tools.search_document import search_document
from app.tools.summary_document import summary_document

registry.register(search_document)
registry.register(summary_document)

__all__ = ["registry", "search_document", "summary_document"]
