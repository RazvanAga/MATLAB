# Slice 2 — End-to-end skeleton with Mock MCP (tracer bullet)

**Type:** AFK · **Recommended model:** Sonnet 4.6 · **Blocked by:** none

## Parent
PRD #1 — Live AI Demo: Chatbot care conduce MATLAB/Simulink prin MCP

## What to build
The complete vertical spine of the system with **no MATLAB** — the highest test seam in the design (PRD phase F1). A message sent from the browser drives the Anthropic agentic loop, which calls a tool over MCP, and the UI shows the agentic step appear and complete.

End-to-end path: Browser (chat) ⇄ SSE ⇄ FastAPI ⇄ Anthropic SDK (`client.beta.messages.tool_runner()`) ⇄ MCP `ClientSession` (stdio) ⇄ **Mock MCP server** exposing a single `echo` tool.

Key pieces:
- **FastAPI backend** (Python 3.13) with an SSE endpoint that streams agentic events to the browser.
- **`tool_runner`** loop using MCP tools converted via `anthropic.lib.tools.mcp`, over `stdio_client` → `ClientSession`. Per-message granularity (intentionally, to make the agentic step visible).
- **Tool wrapper** as the single instrumentation choke-point around every MCP tool: emits a `tool_use start` SSE event → calls the MCP tool → emits a `tool_result` SSE event → returns the result to the runner. (This same choke-point will later host figure detection.)
- **Mock MCP server** (minimal `mcp` stdio server with one `echo` tool) so the whole chain runs without MATLAB or the real binary.
- **Minimal single-column UI**: header + timeline + input. Render a three-zone timeline card — agent text (decision) → tool card (tool name + code, shown verbatim) → result — that appears in a **running** state with a spinner on `tool_use start` and **fills in** on `tool_result`.
- **Backend tests** against the Mock MCP that assert observable behavior: a sent message produces `tool_use` / `tool_result` SSE events in the correct order (test external behavior, not internal calls).

## Acceptance criteria
- [ ] A message (hardcoded trigger is fine at this stage) sent from the browser causes the agent to call `echo` via the Mock MCP.
- [ ] A timeline card appears in the **running** state, then fills in with the tool result, driven by SSE events.
- [ ] The tool wrapper emits `tool_use start` and `tool_result` events around the MCP call.
- [ ] Backend tests verify the SSE event sequence against the Mock MCP, without MATLAB and without the real Anthropic API (model stubbed or test-keyed).
- [ ] No CDN dependency for the UI beyond the Anthropic API itself.
- [ ] After implementation, create a git commit with a relevant `-m` message describing what was achieved. **Commit only — do not push.**

## Blocked by
None — can start immediately.
