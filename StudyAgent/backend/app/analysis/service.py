import json
import logging
import re

from app.analysis.prompt import build_analysis_messages
from app.llm.deepseek import chat

logger = logging.getLogger(__name__)

# 空分析结果（用于失败降级）
EMPTY_ANALYSIS = {
    "question_analysis": {},
    "knowledge_assessment": {},
    "learning_path": [],
}


def _parse_analysis_reply(reply: str) -> dict:
    """从 LLM 回复中提取并解析 JSON 分析结果"""
    if not reply:
        return EMPTY_ANALYSIS

    # 去掉可能的 markdown 代码块标记
    cleaned = reply.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json|JSON)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
        cleaned = cleaned.strip()

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\{[\s\S]*\}", cleaned)
        if match:
            try:
                data = json.loads(match.group())
            except json.JSONDecodeError:
                return EMPTY_ANALYSIS
        else:
            return EMPTY_ANALYSIS

    if not isinstance(data, dict):
        return EMPTY_ANALYSIS

    return data


def analyze_learning(history: list[dict], message: str) -> dict:
    """
    学习分析主入口

    参数：
        history: 对话历史列表
        message: 用户当前问题

    返回：分析结果字典（失败时返回空结构）
    """
    try:
        messages = build_analysis_messages(history, message)
        reply = chat(messages, temperature=0.2)
        result = _parse_analysis_reply(reply)

        qa = result.get("question_analysis", {})
        ka = result.get("knowledge_assessment", {})
        logger.info(
            "[LearningAnalysis] summary=%s | level=%s | score=%s | path_steps=%s",
            qa.get("summary", "")[:60],
            ka.get("level", "N/A"),
            ka.get("score", "N/A"),
            len(result.get("learning_path", [])),
        )

        return result
    except Exception:
        logger.warning("[LearningAnalysis] 分析失败，降级处理", exc_info=True)
        return EMPTY_ANALYSIS
