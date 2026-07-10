import logging
import re
from html import unescape

import config

logger = logging.getLogger(__name__)

BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "zh-CN,zh;q=0.9",
}


def _normalize_ddgs_results(raw: list[dict]) -> list[dict]:
    results = []
    for item in raw:
        title = (item.get("title") or "").strip()
        url = (item.get("href") or item.get("link") or item.get("url") or "").strip()
        snippet = (item.get("body") or item.get("snippet") or "").strip()
        if title and url:
            results.append({"title": title, "url": url, "snippet": snippet})
    return results


def _search_duckduckgo(query: str, max_results: int) -> list[dict]:
    ddgs_cls = None
    try:
        from ddgs import DDGS as DDGSClient
        ddgs_cls = DDGSClient
    except ImportError:
        try:
            from duckduckgo_search import DDGS as DDGSClient
            ddgs_cls = DDGSClient
        except ImportError:
            return []

    for backend in ("duckduckgo", "bing", "brave", "google"):
        try:
            with ddgs_cls() as client:
                raw = list(client.text(query, max_results=max_results, backend=backend))
            results = _normalize_ddgs_results(raw)
            if results:
                return results
        except Exception as exc:
            logger.debug("DuckDuckGo backend %s failed: %s", backend, exc)
    return []


def _search_bing_cn(query: str, max_results: int) -> list[dict]:
    import requests

    response = requests.get(
        "https://cn.bing.com/search",
        params={"q": query, "count": max_results},
        headers=BROWSER_HEADERS,
        timeout=15,
    )
    response.raise_for_status()
    html = response.text

    results = []
    seen = set()
    for match in re.finditer(
        r'<h2[^>]*>\s*<a[^>]+href="([^"]+)"[^>]*>([\s\S]*?)</a>\s*</h2>',
        html,
    ):
        url = unescape(match.group(1)).strip()
        title = unescape(re.sub(r"<.*?>", "", match.group(2))).strip()
        if not title or not url.startswith("http") or url in seen:
            continue
        seen.add(url)

        snippet = ""
        tail = html[match.end() : match.end() + 800]
        snippet_match = re.search(r'<p[^>]*>([\s\S]*?)</p>', tail)
        if snippet_match:
            snippet = unescape(re.sub(r"<.*?>", "", snippet_match.group(1))).strip()

        results.append({"title": title, "url": url, "snippet": snippet})
        if len(results) >= max_results:
            break
    return results


def search_web(query: str, max_results: int = None) -> list[dict]:
    """联网搜索。国内网络优先使用 Bing 中国版，海外可回退 DuckDuckGo。"""
    config.reload_env()
    limit = max_results or config.WEB_SEARCH_MAX_RESULTS
    engine = config.WEB_SEARCH_ENGINE
    results: list[dict] = []

    if engine in ("auto", "bing"):
        try:
            results = _search_bing_cn(query, limit)
        except Exception as exc:
            logger.warning("Bing CN search failed: %s", exc)

    if not results and engine in ("auto", "duckduckgo"):
        results = _search_duckduckgo(query, limit)

    return results
