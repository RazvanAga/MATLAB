"""The single instrumentation choke-point.

``InstrumentedSession`` is a thin proxy around an MCP ``ClientSession``. Every
attribute except ``call_tool`` is delegated unchanged. ``call_tool`` is the one
method ``anthropic.lib.tools.mcp.async_mcp_tool`` invokes when the agent runs a
tool (verified against the SDK source: it calls
``await client.call_tool(name=..., arguments=...)``), so wrapping it here gives
us exactly one place that:

    1. emits a ``tool_use`` SSE event (card enters the "running" state),
    2. performs the real MCP call,
    3. emits a ``tool_result`` SSE event (card fills in).

This is also where Issue 06's figure detection will hook in (watch the figure
folder between steps 2 and 3) without reshaping the rest of the spine.
"""

import uuid
from typing import Any, Awaitable, Callable

from mcp.types import CallToolResult

from . import events

Emit = Callable[[dict[str, Any]], Awaitable[None]]


class InstrumentedSession:
    def __init__(self, session: Any, emit: Emit) -> None:
        self._session = session
        self._emit = emit

    def __getattr__(self, name: str) -> Any:
        # Delegate everything we don't override (initialize, list_tools, ...).
        return getattr(self._session, name)

    async def call_tool(
        self, name: str, arguments: dict[str, Any] | None = None, **kwargs: Any
    ) -> CallToolResult:
        call_id = uuid.uuid4().hex
        await self._emit(events.tool_use(call_id, name, arguments or {}))
        result = await self._session.call_tool(name, arguments, **kwargs)
        await self._emit(
            events.tool_result(call_id, _result_text(result), bool(result.isError))
        )
        return result


def _result_text(result: CallToolResult) -> str:
    """Flatten an MCP tool result's content blocks to displayable text."""
    parts: list[str] = []
    for block in result.content:
        text = getattr(block, "text", None)
        if text is not None:
            parts.append(text)
    return "\n".join(parts)
