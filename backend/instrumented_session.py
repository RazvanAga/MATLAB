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

This is also where Issue 06's figure detection hooks in: after each tool call we
scan ``figures_dir`` and emit any *new* PNG (base64) as a ``figure`` event. The
set of already-seen files is seeded with whatever is on disk at construction
time, so pre-existing figures (from earlier turns/runs) are never re-emitted and
each new figure is emitted exactly once — decoupled from the exact filename the
agent chose.
"""

import base64
import uuid
from pathlib import Path
from typing import Any, Awaitable, Callable

from mcp.types import CallToolResult

from . import events

Emit = Callable[[dict[str, Any]], Awaitable[None]]


class InstrumentedSession:
    def __init__(self, session: Any, emit: Emit, figures_dir: Path | None = None) -> None:
        self._session = session
        self._emit = emit
        self._figures_dir = figures_dir
        # Seed "already emitted" with everything on disk now, so only figures
        # created *during this turn* are sent, and only once.
        self._emitted: set[str] = {str(p) for p in _list_pngs(figures_dir)}

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
        await self._emit_new_figures(call_id)
        return result

    async def _emit_new_figures(self, call_id: str) -> None:
        """Emit every PNG that appeared since construction, oldest first, once."""
        for path in _list_pngs(self._figures_dir):
            key = str(path)
            if key in self._emitted:
                continue
            self._emitted.add(key)
            data = base64.b64encode(path.read_bytes()).decode("ascii")
            await self._emit(events.figure(call_id, path.name, data))


def _list_pngs(figures_dir: Path | None) -> list[Path]:
    """PNGs in ``figures_dir``, oldest first. Empty if the dir is unset/missing."""
    if figures_dir is None or not figures_dir.exists():
        return []
    return sorted(figures_dir.glob("*.png"), key=lambda p: p.stat().st_mtime)


def _result_text(result: CallToolResult) -> str:
    """Flatten an MCP tool result's content blocks to displayable text."""
    parts: list[str] = []
    for block in result.content:
        text = getattr(block, "text", None)
        if text is not None:
            parts.append(text)
    return "\n".join(parts)
