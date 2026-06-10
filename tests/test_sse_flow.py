"""End-to-end SSE flow test against the real Mock MCP, with the model stubbed.

This exercises the whole spine — FastAPI -> SSE -> run_turn -> InstrumentedSession
wrapper -> real ``echo`` over stdio — without MATLAB and without the Anthropic API.
The only stubbed piece is the model loop (``default_driver``), replaced by a fake
that decides to call ``echo`` exactly once. Asserts the observable SSE event order.
"""

import json

import httpx

from backend.app import app


class _TextBlock:
    def __init__(self, text: str) -> None:
        self.type = "text"
        self.text = text


class _Message:
    def __init__(self, text: str) -> None:
        self.content = [_TextBlock(text)]


def _fake_driver(client, messages, tools, instrumented):
    """Stand-in for the Anthropic tool_runner: narrate, call echo via the real
    wrapper, narrate again. Drives the genuine wrapper + Mock MCP."""

    async def gen():
        yield _Message("I'll echo that back.")
        user_text = messages[-1]["content"]
        await instrumented.call_tool("echo", {"text": user_text})
        yield _Message("Done — echoed your message.")

    return gen()


async def _collect_events(monkeypatch, message: str) -> list[dict]:
    monkeypatch.setattr("backend.agent.default_driver", _fake_driver)
    async with app.router.lifespan_context(app):
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            events: list[dict] = []
            async with client.stream(
                "GET", "/api/stream", params={"message": message}
            ) as resp:
                assert resp.status_code == 200
                async for line in resp.aiter_lines():
                    if line.startswith("data:"):
                        events.append(json.loads(line[len("data:") :].strip()))
            return events


async def test_sse_event_sequence(monkeypatch):
    events = await _collect_events(monkeypatch, "hello world")

    assert [e["type"] for e in events] == [
        "agent_text",
        "tool_use",
        "tool_result",
        "agent_text",
        "done",
    ]

    tool_use = events[1]
    tool_result = events[2]
    assert tool_use["name"] == "echo"
    assert tool_use["id"] == tool_result["id"]
    assert tool_result["output"] == "hello world"  # round-tripped through real Mock MCP
    assert tool_result["is_error"] is False
