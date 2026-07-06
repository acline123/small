import config


def search_web(query: str, max_results: int = None) -> list[dict]:
    """使用 DuckDuckGo 进行全网搜索，返回标题、链接、摘要。"""
    limit = max_results or config.WEB_SEARCH_MAX_RESULTS
    try:
        from duckduckgo_search import DDGS

        with DDGS() as ddgs:
            raw = list(ddgs.text(query, max_results=limit))
        results = []
        for item in raw:
            results.append(
                {
                    "title": item.get("title", ""),
                    "url": item.get("href", item.get("link", "")),
                    "snippet": item.get("body", item.get("snippet", "")),
                }
            )
        return results
    except Exception as exc:
        return [{"title": "搜索失败", "url": "", "snippet": str(exc)}]
