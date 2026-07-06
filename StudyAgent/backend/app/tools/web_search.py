import config
from app.tools.base import BaseTool
from app.utils.web_search_client import search_web


class WebSearchTool(BaseTool):
    name = "web_search"
    description = "在互联网上搜索最新信息，获取网页标题、链接和摘要"

    def run(self, query: str, max_results: int = None, **_) -> dict:
        limit = max_results or config.WEB_SEARCH_MAX_RESULTS
        results = search_web(query, max_results=limit)
        return {"results": results, "count": len(results)}


web_search = WebSearchTool()
