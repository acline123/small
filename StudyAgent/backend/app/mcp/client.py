"""同步 MCP client：通过 in-memory transport 调用 MCP server 上的工具。"""
import asyncio
import json

from mcp.shared.memory import create_connected_server_and_client_session

from app.mcp.server import mcp


def call_tool(name: str, arguments: dict = None) -> dict:
    """同步调用 MCP 工具，返回工具结果 dict。"""
    # 过滤 None：调用方常传 document_id=None 表示“不限定”，
    # 直接发送会导致 pydantic 对 Optional[int] 字段报错。
    args = {k: v for k, v in (arguments or {}).items() if v is not None}

    async def _run():
        async with create_connected_server_and_client_session(mcp, raise_exceptions=False) as session:
            return await session.call_tool(name, args)

    result = asyncio.run(_run())

    if result.isError:
        detail = "".join(c.text for c in result.content if hasattr(c, "text"))
        raise RuntimeError(detail or f"MCP 工具 {name} 调用失败")

    # 返回 dict 的工具：FastMCP 序列化为 JSON 文本，structuredContent 为空。
    # 返回标量的工具：structuredContent 形如 {"result": 值}。
    if result.structuredContent is not None:
        sc = dict(result.structuredContent)
        if set(sc.keys()) == {"result"}:
            return sc["result"]
        return sc

    text = "".join(c.text for c in result.content if hasattr(c, "text"))
    if text:
        try:
            return json.loads(text)
        except Exception:
            return {"text": text}
    return {}
