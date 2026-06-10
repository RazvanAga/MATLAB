"""The agentic turn.

``run_turn`` wires the Anthropic ``tool_runner`` agentic loop to the MCP tools,
routed through the ``InstrumentedSession`` choke-point so every tool call surfaces
as SSE events. It emits ``agent_text`` for the model's narration; the wrapper
emits the ``tool_use``/``tool_result`` pair, so the loop here deliberately does
NOT re-emit tool blocks (that would double the timeline cards).

The model loop is injected via ``driver`` so tests can substitute a fake that
drives the *real* wrapper + *real* Mock MCP without calling the Anthropic API.
"""

from typing import Any, AsyncIterator, Awaitable, Callable

from anthropic.lib.tools.mcp import async_mcp_tool

from . import events
from .instrumented_session import InstrumentedSession, Emit

MODEL = "claude-opus-4-8"
MAX_TOKENS = 16000

# Minimal F1 system prompt. The focused, full system prompt (figure export,
# guardrails, workspace re-derivation) is Issue 04.
SYSTEM_PROMPT = (
    "You drive tools over MCP. When the user sends a message, use the available "
    "tools to act on it, then briefly confirm what happened. Keep replies short."
)

# A driver takes (client, messages, tools, instrumented_session) and returns an
# async iterator of assistant messages (each with a ``.content`` list of blocks).
Driver = Callable[[Any, list[dict[str, Any]], list[Any], InstrumentedSession], AsyncIterator[Any]]


def default_driver(
    client: Any,
    messages: list[dict[str, Any]],
    tools: list[Any],
    instrumented: InstrumentedSession,
) -> AsyncIterator[Any]:
    """Production driver: the real Anthropic tool_runner agentic loop.

    ``tool_runner`` is a synchronous call that returns an async-iterable runner;
    tools are already bound to ``instrumented`` via ``async_mcp_tool``, so the
    ``instrumented`` argument is unused here (it exists for the fake driver)."""
    return client.beta.messages.tool_runner(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        thinking={"type": "adaptive"},
        output_config={"effort": "medium"},
        system=SYSTEM_PROMPT,
        messages=messages,
        tools=tools,
    )


async def run_turn(
    message: str,
    emit: Emit,
    session: Any,
    *,
    client: Any = None,
    driver: Driver = default_driver,
) -> None:
    """Run one agentic turn for ``message``, emitting SSE events via ``emit``.

    ``session`` is the live MCP ClientSession; it is wrapped so every tool call
    is instrumented. Always emits a terminal ``done`` event, even on failure."""
    instrumented = InstrumentedSession(session, emit)
    try:
        tools_result = await session.list_tools()
        tools = [async_mcp_tool(t, instrumented) for t in tools_result.tools]

        messages = [{"role": "user", "content": message}]
        async for msg in driver(client, messages, tools, instrumented):
            for block in msg.content:
                if getattr(block, "type", None) == "text":
                    await emit(events.agent_text(block.text))
    except Exception as exc:  # surface failures as a clean error card (S4)
        import traceback as _tb

        await emit(events.error(str(exc), _tb.format_exc()))
    finally:
        await emit(events.done())
