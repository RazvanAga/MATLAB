"""SSE event payloads.

Each event is a plain ``dict`` with a ``type`` discriminator plus fields. The
SSE layer (``app.py``) serialises these to ``data:`` lines; the wrapper and the
agent loop only ever deal in these dicts, so they stay decoupled from transport.

The browser (``public/app.js``) switches on ``type``:
    agent_text   -> append/stream a markdown narration block
    tool_use     -> append a timeline card in the "running" state (by ``id``)
    tool_result  -> fill the matching card's result zone (by ``id``)
    error        -> red-accent card; traceback hidden behind an expander
    done         -> terminal event; client closes the EventSource
"""

from typing import Any


def agent_text(text: str) -> dict[str, Any]:
    return {"type": "agent_text", "text": text}


def tool_use(call_id: str, name: str, tool_input: Any) -> dict[str, Any]:
    return {"type": "tool_use", "id": call_id, "name": name, "input": tool_input}


def tool_result(call_id: str, output: str, is_error: bool = False) -> dict[str, Any]:
    return {"type": "tool_result", "id": call_id, "output": output, "is_error": is_error}


def error(message: str, traceback: str = "") -> dict[str, Any]:
    return {"type": "error", "message": message, "traceback": traceback}


def done() -> dict[str, Any]:
    return {"type": "done"}
