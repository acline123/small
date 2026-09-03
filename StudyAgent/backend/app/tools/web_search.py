import config
from app.utils.web_search_client import search_web


def web_search(query: str, max_results: int = None) -> dict:
    """在互联网上搜索最新信息，获取网页标题、链接和摘要。"""
    limit = max_results or config.WEB_SEARCH_MAX_RESULTS
    results = search_web(query, max_results=limit)
    return {"results": results, "count": len(results)}
