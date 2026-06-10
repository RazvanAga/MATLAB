# MATLAB/Simulink MCP — Live Agentic Demo

A local chatbot that drives a **real, running MATLAB R2026a / Simulink session** through the [Model Context Protocol (MCP)](https://modelcontextprotocol.io). You type a request in natural language; an AI agent decides what to do, calls MCP tools that execute code in the live MATLAB session, and the results — Command Window output and generated figures — stream back into the chat as they happen.

It's built to show the **Schaeffler PMT team** a concrete, working example of how MATLAB/Simulink MCP fits into a real engineering workflow: not a slide about "AI workflows," but one running on MATLAB, live.

## What it does

- **Natural-language control of MATLAB.** Ask for an analysis or a plot; the agent writes the MATLAB code, optionally checks it, runs it in the real session, and shows you the output.
- **Visible agentic steps.** Every step is rendered as a timeline card: the agent's decision → the tool call (with the MATLAB code shown) → the result. Nothing is hidden behind a black box.
- **Live figures in the chat.** Plots generated in MATLAB appear inline in the conversation and expand to full screen on click.
- **Simulink, read + simulate.** The agent can open a Simulink model, run a simulation, and read back logged signals — strictly read-only, no model modification.
- **Real session, real state.** MATLAB runs visibly alongside the browser; the agent reuses the base workspace across turns so follow-up questions build on prior results.

## How it works

```
Browser (chat UI)
   ⇅ SSE
FastAPI backend
   ⇅ Anthropic SDK (agentic tool_runner loop)
   ⇅ MCP ClientSession (stdio)
MATLAB MCP Core Server  (standalone binary)
   ⇅
MATLAB R2026a / Simulink   (visible, shared session)
```

- **Backend** — FastAPI (Python 3.13) running the Anthropic agentic loop. Each MCP tool call is wrapped at a single instrumentation point that streams `tool_use` / `tool_result` events to the browser over SSE and watches for newly generated figures.
- **MCP layer** — the agent talks to MATLAB through the **MATLAB MCP Core Server**, a standalone binary installed alongside the Simulink Agentic Toolkit. No "MATLAB Engine for Python" layer is involved.
- **MATLAB session** — runs in `existing` mode against a session you've registered with `shareMATLABSession`, so everything happens in the MATLAB window you can see.
- **Frontend** — vanilla HTML/JS, no build step. A single-column timeline with prompt buttons, syntax-highlighted MATLAB code, inline figures, and a reset control. Libraries are vendored locally; the only external dependency at runtime is the Anthropic API.

## Why MCP for the PMT workflow

MCP is the stack MathWorks shipped officially for agent-driven MATLAB (core server, late 2025). This demo is a small, opinionated surface on top of it — a narrow set of tools, a focused system prompt, and guardrails — showing how a Schaeffler PMT support engineer could drive MATLAB/Simulink from natural language without leaving a chat window, and how that same pattern could be wrapped into an internal tool for the team.

## Status

Early build. Work is tracked as issues in this repository (see [docs/issues/](docs/issues/) for the planned vertical slices). High level:

1. **End-to-end skeleton** validated against a mock MCP server (no MATLAB needed).
2. **Live MATLAB** — real core server, scripted analysis returning numeric output.
3. **Wow factor** — inline figures + lightbox, Simulink read/simulate, visible code-check step.
4. **Polish** — Teams-legible styling, branding, pre-flight checks.

## Requirements

- MATLAB R2026a with the Simulink Agentic Toolkit installed (this also installs the MATLAB MCP Core Server).
- Python 3.13 with `anthropic[mcp]`.
- Anthropic credentials (`ant auth login`).
- A MATLAB session registered for MCP via `shareMATLABSession` (see below).

## Running the demo

**1. Register the MATLAB session for MCP.** In the **MATLAB Command Window** (R2026a, kept open and visible):

```matlab
shareMATLABSession
```

This starts MATLAB's connector service and writes a fresh `sessionDetails.json` that the Core Server discovers. Run it **once per MATLAB session** — after every MATLAB (or PC) restart.

> ⚠️ This is **not** `matlab.engine.shareEngine` — that's a different, unrelated mechanism the Core Server ignores. Use `shareMATLABSession` (from the MATLAB MCP Core Server Toolbox). If you skip this or run the wrong one, the backend fails at startup with `MATLAB preflight returned an error: failed to attach to MATLAB session` (a stale `sessionDetails.json` pointing at a dead session). Re-run `shareMATLABSession` to fix.

**2. Launch the demo (recommended).** In **PowerShell**, from the repo root:

```powershell
cd C:\Users\Razvan\Projects\MATLAB
.\run-demo.ps1
```

`run-demo.ps1` is the pre-flight launcher. It runs instant local checks (Core Server binary, Simulink tools manifest, **a live `shareMATLABSession` registration — it verifies the registered MATLAB process is actually running, catching a missing or stale registration in milliseconds**, and the figures folder), then starts the backend, waits for the MATLAB preflight to pass, and opens the browser. If anything is wrong — most commonly MATLAB not shared — it **fails loudly with a clear message before the browser opens**, instead of starting in a broken state. Backend logs go to `.run/`. Press **Ctrl+C** to stop. Flags: `-NoBrowser`, `-Port <n>`.

**Manual alternative.** To start the backend yourself:

```powershell
uv run uvicorn backend.app:app
```

On startup the backend launches the real Core Server (`--matlab-session-mode=existing`, strict) and runs a MATLAB preflight ping. Wait for `Application startup complete`, then open <http://127.0.0.1:8000>. (First run in a fresh clone also triggers `uv` to install dependencies; for local development, add `--reload` to pick up code edits automatically.)

**3. Use the UI** at <http://127.0.0.1:8000> — click **Step 1**, or type a message. Watch the MATLAB window execute alongside the chat.

### Run without MATLAB (chain/UI only)

To exercise the FastAPI → SSE → UI spine against the in-repo Mock MCP (no MATLAB, no preflight):

```powershell
$env:MATLAB_MCP_MOCK = "1"; uv run uvicorn backend.app:app
```

### Tests

No MATLAB or Anthropic API needed:

```powershell
uv run pytest
```

## Out of scope

Multi-user auth, server deployment / containerization, and agent-driven **modification** of Simulink models (the demo is read + simulate only, by design).
