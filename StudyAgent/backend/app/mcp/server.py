"""标准 MCP server：将工具函数注册为 MCP Tool。"""
from mcp.server.fastmcp import FastMCP

from app.tools.exercise_generator import generate_exercise
from app.tools.query_knowledge_graph import query_knowledge_graph
from app.tools.search_document import search_document
from app.tools.summary_document import summary_document
from app.tools.web_search import web_search

mcp = FastMCP("study-agent")

mcp.tool()(search_document)
mcp.tool()(summary_document)
mcp.tool()(web_search)
mcp.tool()(query_knowledge_graph)
mcp.tool()(generate_exercise)
