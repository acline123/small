import uuid
from concurrent.futures import ThreadPoolExecutor

import config
from app.agent.intent import recognize_intent
from app.agent.memory import load_history, save_message
from app.agent.prompt import (
    build_rag_prompt,
    build_tool_prompt,
    format_graph_results,
    format_search_results,
    format_web_search_results,
)
from app.analysis.service import analyze_learning
from app.llm.deepseek import chat
from app.rag.vectorstore import similarity_search
from app.tools import registry


def _get_tool(name: str):
    tool = registry.get(name)
    if not tool:
        raise RuntimeError(f"工具 {name} 未注册")
    return tool


def handle_chat(session_id: str | None, message: str, use_web_search: bool = False) -> dict:
    """
    Agent 主流程：
    用户输入 → load_history → (并发) 学习分析 + 意图识别 → 工具调用/RAG → DeepSeek 生成 → 可视化 → 保存历史
    """
    if not session_id:
        session_id = str(uuid.uuid4())

    history = load_history(session_id)

    # 并行执行：学习分析 + 意图识别（两者完全独立）
    with ThreadPoolExecutor(max_workers=2) as executor:
        future_analysis = executor.submit(analyze_learning, history, message)
        future_intent = executor.submit(recognize_intent, message)

        analysis = future_analysis.result()
        intent_data = future_intent.result()

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
        messages = build_tool_prompt(history, tool_used, context_str, message, analysis=analysis)

    elif intent == "graph_query":
        tool = _get_tool("query_knowledge_graph")
        tool_result = tool.run(query=message, document_id=document_id)
        tool_used = "query_knowledge_graph"
        sources = tool_result.get("results", [])
        context_str = format_graph_results(sources)
        messages = build_tool_prompt(history, tool_used, context_str, message, analysis=analysis)

    elif intent == "search":
        tool = _get_tool("search_document")
        tool_result = tool.run(query=message, top_k=config.RETRIEVE_TOP_K, document_id=document_id)
        tool_used = "search_document"
        sources = tool_result.get("results", [])
        context_str = format_search_results(sources)
        messages = build_tool_prompt(history, tool_used, context_str, message, analysis=analysis)

    elif intent == "summary":
        tool = _get_tool("summary_document")
        tool_result = tool.run(document_id=document_id, query=message)
        tool_used = "summary_document"
        summary_text = tool_result.get("summary", "")
        messages = build_tool_prompt(history, tool_used, summary_text, message, analysis=analysis)

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
        messages = build_rag_prompt(history, context_str, message, analysis=analysis)

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

