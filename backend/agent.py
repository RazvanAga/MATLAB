"""The agentic turn.

``run_turn`` wires the Anthropic ``tool_runner`` agentic loop to the MCP tools,
routed through the ``InstrumentedSession`` choke-point so every tool call surfaces
as SSE events. It emits ``agent_text`` for the model's narration; the wrapper
emits the ``tool_use``/``tool_result`` pair, so the loop here deliberately does
NOT re-emit tool blocks (that would double the timeline cards).

The model loop is injected via ``driver`` so tests can substitute a fake that
drives the *real* wrapper + *real* Mock MCP without calling the Anthropic API.
"""

from pathlib import Path
from typing import Any, AsyncIterator, Awaitable, Callable

from anthropic.lib.tools.mcp import async_mcp_tool

from . import events
from .instrumented_session import InstrumentedSession, Emit

MAX_TOKENS = 16000

# Where the agent exports figures, watched by the backend (Issue 06) and emitted
# inline over SSE. The system prompt below pins this exact path; keep them in sync.
FIGURES_DIR = Path(__file__).resolve().parent.parent / "figures"

# Restricted demo tool surface (Issue 04). The MATLAB MCP Core Server exposes ~12
# tools (5 core + 7 Simulink); the agent only ever sees this allowlist. We keep
# `evaluate_matlab_code` (run + simulate via `sim`), `check_matlab_code` (the
# visible quality beat), and the *read-only* Simulink inspection tools. The
# model-editing/test tools are deliberately withheld to back the read-only,
# no-destructive-operations guardrail at the tool surface, not just in the prompt.
DEMO_TOOLS: frozenset[str] = frozenset(
    {
        "evaluate_matlab_code",
        "check_matlab_code",
        "model_read",
        "model_overview",
        "model_query_params",
        "model_resolve_params",
        "model_check",
    }
)

# Selectable model tiers. Adaptive thinking + the effort parameter are
# Opus-4.6+/Sonnet-4.6 features; Haiku 4.5 rejects both (400), so it runs plain.
MODELS: dict[str, str] = {
    "opus": "claude-opus-4-8",
    "sonnet": "claude-sonnet-4-6",
    "haiku": "claude-haiku-4-5",
}
DEFAULT_MODEL = "opus"
_MODEL_PARAMS: dict[str, dict] = {
    "opus": {"thinking": {"type": "adaptive"}, "output_config": {"effort": "medium"}},
    "sonnet": {"thinking": {"type": "adaptive"}, "output_config": {"effort": "medium"}},
    "haiku": {},
}

# Focused system prompt (Issue 04). Calm and concrete, not aggressive — opus-4-8
# follows instructions literally and tends to over-narrate, so we ask explicitly
# for short narration. Covers: tool selection, the check-before-run quality beat,
# figure export to FIGURES_DIR, defensive workspace re-derivation, the read-only
# Simulink guardrail, and the licensed-toolbox limits (no Control System Toolbox).
SYSTEM_PROMPT = f"""\
You are a MATLAB and Simulink engineering assistant in a live demo. A real,
visible MATLAB R2026a session is running and you drive it through MCP tools.
Work calmly and concretely: take the obvious next action, then say briefly what
you did and what the result means. Keep narration short — a sentence or two
between tool calls, never long paragraphs.

Tools
- Run MATLAB code with `evaluate_matlab_code` and lint code with
  `check_matlab_code`. Inspect Simulink models with the read-only model tools
  (`model_read`, `model_overview`, `model_query_params`, `model_resolve_params`,
  `model_check`), and run a simulation with `sim(...)` inside
  `evaluate_matlab_code`.
- Prefer one complete, self-contained script per `evaluate_matlab_code` call
  over many tiny snippets.

Quality
- Before running any non-trivial MATLAB code, first call `check_matlab_code` on
  it and fix anything it flags. Only run the code once it is clean, and note
  briefly that the check passed.

Figures
- Whenever you create a figure, export it so it can be shown inline. In the SAME
  `evaluate_matlab_code` call, right after the plotting commands, run exactly:
    exportgraphics(gcf, fullfile("{FIGURES_DIR.as_posix()}", sprintf("fig_%s.png", datestr(now, "HHMMSSFFF"))))
  Do not change this path or filename pattern.

Workspace continuity
- The base workspace persists between your tool calls. On a follow-up, reuse
  variables that already exist (check with `exist`). If they are missing, re-run
  the simulation that produces them before continuing, so a step never fails on
  a cold workspace.

Simulink guardrail
- Treat every Simulink model as READ-ONLY. Open, inspect, and simulate models,
  but never add, delete, reconfigure, or save blocks or models, and never use a
  model-editing tool. This is a safety-critical (ISO 26262) narrative; do not
  modify models under any circumstances.

Environment
- Only the base MATLAB product and Simulink are licensed — the Control System
  Toolbox is NOT installed. Do not use `stepinfo`, `step`, `tf`, `lsim`, or
  similar; compute step-response metrics such as overshoot and settling time
  directly from the simulated signal arrays."""

# A driver takes (client, messages, tools, instrumented_session, model_key) and
# returns an async iterator of assistant messages (each with a ``.content`` list).
Driver = Callable[
    [Any, list[dict[str, Any]], list[Any], InstrumentedSession, str], AsyncIterator[Any]
]


def default_driver(
    client: Any,
    messages: list[dict[str, Any]],
    tools: list[Any],
    instrumented: InstrumentedSession,
    model: str,
) -> AsyncIterator[Any]:
    """Production driver: the real Anthropic tool_runner agentic loop.

    ``tool_runner`` is a synchronous call that returns an async-iterable runner;
    tools are already bound to ``instrumented`` via ``async_mcp_tool``, so the
    ``instrumented`` argument is unused here (it exists for the fake driver)."""
    return client.beta.messages.tool_runner(
        model=MODELS[model],
        max_tokens=MAX_TOKENS,
        system=SYSTEM_PROMPT,
        messages=messages,
        tools=tools,
        **_MODEL_PARAMS[model],  # adaptive thinking + effort, except on Haiku
    )


async def run_turn(
    message: str,
    emit: Emit,
    session: Any,
    *,
    client: Any = None,
    model: str = DEFAULT_MODEL,
    driver: Driver = default_driver,
) -> None:
    """Run one agentic turn for ``message``, emitting SSE events via ``emit``.

    ``session`` is the live MCP ClientSession; it is wrapped so every tool call
    is instrumented. Always emits a terminal ``done`` event, even on failure."""
    instrumented = InstrumentedSession(session, emit, figures_dir=FIGURES_DIR)
    try:
        tools_result = await session.list_tools()
        # Expose only the restricted demo subset (Issue 04). The Mock MCP's `echo`
        # is not in DEMO_TOOLS, so under the mock this list is empty — fine, since
        # F1 tests drive the wrapper through a stubbed driver, not the tool list.
        tools = [
            async_mcp_tool(t, instrumented)
            for t in tools_result.tools
            if t.name in DEMO_TOOLS
        ]

        messages = [{"role": "user", "content": message}]
        async for msg in driver(client, messages, tools, instrumented, model):
            for block in msg.content:
                if getattr(block, "type", None) == "text":
                    await emit(events.agent_text(block.text))
    except Exception as exc:  # surface failures as a clean error card (S4)
        import traceback as _tb

        await emit(events.error(str(exc), _tb.format_exc()))
    finally:
        await emit(events.done())
