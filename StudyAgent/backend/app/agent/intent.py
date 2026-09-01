"""意图识别 — 规则引擎实现，不调用 LLM，避免每次对话增加一次 API 往返。"""
import re

# 文档编号：如 "文档1"、"第 2 个文档"
DOC_ID_PATTERNS = [
    re.compile(r"文档\s*(\d+)"),
    re.compile(r"第\s*(\d+)\s*个文档"),
]

# 出题 / 做习题
EXERCISE_WORDS = [
    "出题", "出几道", "出几题", "来几题", "习题", "做练习", "做做题",
    "自测", "测试一下", "考考我", "小测", "刷题", "练练手",
]
# 摘要总结
SUMMARY_WORDS = ["总结", "摘要", "概括", "归纳", "提炼", "梳理"]
# 知识图谱 / 实体关系
GRAPH_PATTERNS = [
    re.compile(r"什么关系|有何关系|有哪些关系|之间(的)?(关系|关联|联系)|的(关系|关联|联系)"),
    re.compile(r"知识图谱|实体关系|概念关联"),
]
# 联网搜索（实时信息）
WEB_WORDS = [
    "联网", "最新", "实时", "新闻", "今年", "今天", "最近发生",
    "最新技术动态", "最新进展", "热搜", "时事",
]
# 知识库内搜索
SEARCH_WORDS = ["搜索", "查找", "检索", "找一下", "查一下", "找找"]

_VALID_INTENTS = ("chat", "search", "summary", "web_search", "graph_query", "exercise")


def _extract_document_id(message: str):
    for pattern in DOC_ID_PATTERNS:
        match = pattern.search(message)
        if match:
            return int(match.group(1))
    return None


def recognize_intent(message: str) -> dict:
    """基于关键词/正则的意图识别，返回 {"intent": ..., "document_id": ...}。

    判断顺序从"动作明确"到"泛泛而谈"：
    web_search（实时） > exercise（出题） > summary（总结） > search（搜索） > graph_query（关系） > chat
    """
    text = message or ""

    if any(w in text for w in WEB_WORDS):
        return {"intent": "web_search", "document_id": None}
    if any(w in text for w in EXERCISE_WORDS):
        return {"intent": "exercise", "document_id": None}
    if any(w in text for w in SUMMARY_WORDS):
        return {"intent": "summary", "document_id": _extract_document_id(text)}
    if any(p.search(text) for p in GRAPH_PATTERNS):
        return {"intent": "graph_query", "document_id": _extract_document_id(text)}
    if any(w in text for w in SEARCH_WORDS):
        return {"intent": "search", "document_id": _extract_document_id(text)}
    return {"intent": "chat", "document_id": None}
