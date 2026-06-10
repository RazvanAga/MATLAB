"""Mock MCP server — the F1 test seam.

A minimal stdio MCP server exposing a single ``echo`` tool. It stands in for the
real MATLAB MCP Core Server so the entire chain (browser -> FastAPI -> SSE ->
tool_runner -> wrapper -> MCP) can be exercised without MATLAB or the Go binary.

Run as a subprocess over stdio:
    python -m mock_mcp.server
"""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("mock-matlab")


@mcp.tool()
def echo(text: str) -> str:
    """Echo the provided text back verbatim. Use this to confirm the tool chain works."""
    return text


if __name__ == "__main__":
    # FastMCP.run() defaults to the stdio transport.
    mcp.run()
