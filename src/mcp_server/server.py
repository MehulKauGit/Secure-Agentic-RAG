"""MCP Server exposing local tools for the Secure Agentic RAG Platform."""

from mcp.server.fastmcp import FastMCP

from src.mcp_server.tools.calculator import calculate
from src.mcp_server.tools.file_lookup import file_lookup
from src.mcp_server.tools.send_email import send_email
from src.mcp_server.tools.web_search_stub import web_search_stub

# Initialize FastMCP Server instance
mcp = FastMCP("SecureRAG-ToolServer")


@mcp.tool()
def run_calculator(expression: str) -> str:
    """Safely calculates the result of a mathematical expression. Supports basic math and standard functions."""
    return calculate(expression)


@mcp.tool()
def read_sandboxed_file(filename: str) -> str:
    """Reads the contents of a company document from the sandboxed document repository."""
    return file_lookup(filename)


@mcp.tool()
def search_web(query: str) -> str:
    """Performs a deterministic lookup for external knowledge and web facts."""
    return web_search_stub(query)


@mcp.tool()
def dispatch_email(recipient: str, subject: str, body: str) -> str:
    """Sends an email message to a specified recipient (Logged-only canary tool)."""
    return send_email(recipient, subject, body)


if __name__ == "__main__":
    mcp.run(transport="stdio")
