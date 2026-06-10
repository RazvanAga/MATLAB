"""Unit tests for the instrumentation choke-point (no MCP, no API).

Verifies the externally observable contract: wrapping a tool call emits exactly
one ``tool_use`` then one ``tool_result`` with a matching id, and propagates the
error flag — the behaviour the timeline UI depends on.
"""

from mcp.types import CallToolResult, TextContent

from backend.instrumented_session import InstrumentedSession


class _FakeSession:
    def __init__(self, is_error: bool = False) -> None:
        self._is_error = is_error
        self.calls: list[tuple[str, dict]] = []

    async def call_tool(self, name, arguments=None, **kwargs):
        self.calls.append((name, arguments))
        text = "boom" if self._is_error else arguments["text"]
        return CallToolResult(
            content=[TextContent(type="text", text=text)], isError=self._is_error
        )

    # An arbitrary passthrough attribute to prove delegation works.
    async def initialize(self):
        return "initialized"


async def test_emits_tool_use_then_result_with_matching_id():
    seen: list[dict] = []

    async def emit(event):
        seen.append(event)

    fake = _FakeSession()
    session = InstrumentedSession(fake, emit)

    result = await session.call_tool("echo", {"text": "hello"})

    assert [e["type"] for e in seen] == ["tool_use", "tool_result"]
    assert seen[0]["name"] == "echo"
    assert seen[0]["input"] == {"text": "hello"}
    assert seen[0]["id"] == seen[1]["id"]  # same card start->fill
    assert seen[1]["output"] == "hello"
    assert seen[1]["is_error"] is False
    # The real MCP call actually happened, with the right arguments.
    assert fake.calls == [("echo", {"text": "hello"})]
    assert result.isError is False


async def test_propagates_tool_error_flag():
    seen: list[dict] = []

    async def emit(event):
        seen.append(event)

    session = InstrumentedSession(_FakeSession(is_error=True), emit)
    await session.call_tool("echo", {"text": "x"})

    assert seen[1]["type"] == "tool_result"
    assert seen[1]["is_error"] is True


async def test_delegates_unknown_attributes_to_session():
    async def emit(event):  # pragma: no cover - not exercised here
        pass

    session = InstrumentedSession(_FakeSession(), emit)
    assert await session.initialize() == "initialized"
