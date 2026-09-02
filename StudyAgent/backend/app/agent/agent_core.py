import uuid
from concurrent.futures import ThreadPoolExecutor

import config
from app.agent.intent import recognize_intent
from app.agent.memory import load_history, save_message
from app.agent.prompt import (
    build_analysis_context,
    build_rag_prompt,
    build_tool_prompt,
    format_exercise_results,
    format_graph_results,
    format_search_results,
    format_web_search_results,
)
from app.analysis.service import EMPTY_ANALYSIS, analyze_learning
from app.llm.deepseek import chat, chat_stream
from app.rag.vectorstore import similarity_search
from app.tools import registry

# 学习分析在后台线程执行，主流程限时等待（超时降级为空分析，不阻塞回复）
_analysis_executor = ThreadPoolExecutor(max_workers=2)


def _get_tool(name: str):
    tool = registry.get(name)
    if not tool:
        raise RuntimeError(f"工具 {name} 未注册")
    return tool


def _wait_analysis(future, timeout: float = None) -> dict:
    """限时等待学习分析结果，超时或失败返回空分析。"""
    try:
        return future.result(timeout=timeout or config.ANALYSIS_TIMEOUT)
    except Exception:
        return EMPTY_ANALYSIS


def _route_and_build(session_id: str, message: str, use_web_search: bool, history: list[dict]):
    """意图识别 → 工具调用/RAG 检索 → 组装 messages。返回 (messages, tool_used, sources, intent)。"""
    intent_data = recognize_intent(message)
    intent = intent_data.get("intent", "chat")
    document_id = intent_data.get("document_id")

    if use_web_search:
        intent = "web_search"

    tool_used = None
    sources = []

    if intent == "web_search":
        tool = _get_tool("web_search")
        tool_result = tool.run(query=message)
        tool_used = "web_search"
        sources = tool_result.get("results", [])
        context_str = format_web_search_results(sources)
        messages = build_tool_prompt(history, tool_used, context_str, message)

    elif intent == "graph_query":
        tool = _get_tool("query_knowledge_graph")
        tool_result = tool.run(query=message, document_id=document_id)
        tool_used = "query_knowledge_graph"
        sources = tool_result.get("results", [])
        context_str = format_graph_results(sources)
        messages = build_tool_prompt(history, tool_used, context_str, message)

    elif intent == "search":
        tool = _get_tool("search_document")
        tool_result = tool.run(query=message, top_k=config.RETRIEVE_TOP_K, document_id=document_id)
        tool_used = "search_document"
        sources = tool_result.get("results", [])
        context_str = format_search_results(sources)
        messages = build_tool_prompt(history, tool_used, context_str, message)

    elif intent == "summary":
        tool = _get_tool("summary_document")
        tool_result = tool.run(document_id=document_id, query=message)
        tool_used = "summary_document"
        summary_text = tool_result.get("summary", "")
        messages = build_tool_prompt(history, tool_used, summary_text, message)

    elif intent == "exercise":
        tool = _get_tool("generate_exercise")
        tool_result = tool.run(session_id=session_id, types=["choice", "true_false", "fill_blank"], count=5)
        tool_used = "generate_exercise"
        sources = tool_result.get("exercises", [])
        context_str = format_exercise_results(tool_result)
        messages = build_tool_prompt(history, tool_used, context_str, message)

    else:
        docs = similarity_search(message, top_k=config.RETRIEVE_TOP_K)
        sources = [
            {
                "content": d.page_content,
                "filename": d.metadata.get("filename", "未知"),
                "document_id": d.metadata.get("document_id"),
            }
            for d in docs
        ]
        context_str = format_search_results(sources) if sources else "（知识库暂无相关内容）"
        messages = build_rag_prompt(history, context_str, message)

    return messages, tool_used, sources, intent


def handle_chat(session_id: str | None, message: str, use_web_search: bool = False) -> dict:
    """
    Agent 主流程（非流式）：
    用户输入 → load_history → (后台) 学习分析 + 规则意图识别 → 工具调用/RAG → DeepSeek 生成 → 保存历史
    """
    if not session_id:
        session_id = str(uuid.uuid4())

    history = load_history(session_id)

    # 学习分析放后台执行，限时等待；意图识别走规则引擎，即时返回
    future_analysis = _analysis_executor.submit(analyze_learning, history, message)
    messages, tool_used, sources, intent = _route_and_build(session_id, message, use_web_search, history)

    analysis = _wait_analysis(future_analysis)
    if analysis:
        messages.insert(1, {"role": "system", "content": build_analysis_context(analysis)})

    reply = chat(messages)

    save_message(session_id, "user", message)
    save_message(session_id, "assistant", reply, tool_used=tool_used)

    return {
        "session_id": session_id,
        "reply": reply,
        "tool_used": tool_used,
        "intent": intent,
        "sources": sources[:3],
        "analysis": analysis,
    }


def stream_chat(session_id: str | None, message: str, use_web_search: bool = False):
    """
    Agent 流式流程：与 handle_chat 相同，但最终回复逐段产出（SSE delta 事件），
    生成结束后产出 done 事件并保存历史。
    """
    if not session_id:
        session_id = str(uuid.uuid4())

    history = load_history(session_id)

    # 学习分析放后台执行，限时等待；意图识别走规则引擎，即时返回
    future_analysis = _analysis_executor.submit(analyze_learning, history, message)
    messages, tool_used, sources, intent = _route_and_build(session_id, message, use_web_search, history)

    analysis = _wait_analysis(future_analysis)
    if analysis:
        messages.insert(1, {"role": "system", "content": build_analysis_context(analysis)})

    full_reply = ""
    try:
        for delta in chat_stream(messages):
            full_reply += delta
            yield {"type": "delta", "content": delta}
    except Exception as exc:
        yield {"type": "error", "message": f"生成失败: {exc}"}
        return

    save_message(session_id, "user", message)
    save_message(session_id, "assistant", full_reply, tool_used=tool_used)

    yield {
        "type": "done",
        "session_id": session_id,
        "tool_used": tool_used,
        "intent": intent,
        "sources": sources[:3],
        "analysis": analysis,
    }
