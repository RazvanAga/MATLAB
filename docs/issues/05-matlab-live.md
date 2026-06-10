# Slice 5 — MATLAB live: real core server, `existing` strict

**Type:** AFK · **Recommended model:** Opus 4.8 · **Blocked by:** #2 (env/mbd_demo.slx), #3 (skeleton), #5 (content)

## Parent
PRD #1 — Live AI Demo: Chatbot care conduce MATLAB/Simulink prin MCP

## What to build
Replace the Mock MCP with the real MATLAB MCP Core Server and prove the agent drives the real, visible MATLAB session (PRD phase F2). This is the S2 milestone.

- Point the `ClientSession` at the **real MATLAB MCP Core Server** binary instead of the mock.
- Launch in `--matlab-session-mode existing` **strict**: fail loudly if no shared session is found (never silently start a new, invisible session in which figures "disappear"). The user's open MATLAB must be on `matlab.engine.shareEngine`.
- Run scripted **prompt 1 (mass-spring-damper)** end-to-end → the card shows real numeric output from the Command Window.
- Confirm `check_matlab_code` appears as a distinct visible beat before code runs.
- **Manual validation** (per PRD, not automated): `existing` mode catches the R2026a session after `shareEngine`; the base workspace **persists** between `evaluate` calls so follow-ups reuse data; observe opus-4-8 latency on first rehearsal (note fallback `claude-sonnet-4-6` if it drags).

## Acceptance criteria
- [x] Backend connects to the real MATLAB MCP Core Server over stdio.
- [x] `existing` strict mode fails loudly at startup when no shared MATLAB session is present.
- [x] Prompt 1 runs in the real MATLAB and returns numeric output shown in the card (not a mock). *(pipeline validated end-to-end with real output; model-driven run pending — see Status)*
- [x] Base-workspace persistence between `evaluate` calls is validated manually.
- [x] `check_matlab_code` shows as a distinct beat before the run. *(tool validated live; model-driven beat pending — see Status)*
- [x] After implementation, create a git commit with a relevant `-m` message describing what was achieved. **Commit only — do not push.**

## Status / implementation notes
- [backend/app.py](../../backend/app.py): `mcp_server_params()` launches the real Core Server (`matlab-mcp-core-server.exe`) with `--matlab-session-mode=existing` + the Simulink `--extension-file`. `MATLAB_MCP_MOCK=1` selects the in-repo Mock MCP (F1 chain tests set this).
- **Loud failure:** `_preflight_matlab()` runs in the lifespan (real mode only) — a trivial `evaluate_matlab_code` ping with a 90 s timeout. Any failure (timeout / transport / `isError`) raises a `RuntimeError` with a fix-it message (`matlab.engine.shareEngine`), aborting startup. Covered by `tests/test_matlab_live_wiring.py` (the failure path can't be triggered live without unsharing MATLAB).
- **Verified live (no Anthropic API, via a stubbed driver against the real server):**
  - Second Core Server attaches to the already-shared MATLAB; `evaluate_matlab_code("2+2")` → `ans = 4`.
  - Full SSE spine in real mode: `agent_text → tool_use → tool_result → done`, card shows real Command Window output `x_ss = F/k = 0.0500` (mass-spring-damper steady state).
  - Base workspace persists across separate `evaluate` calls (`exist(...)` → `1`).
  - `check_matlab_code` returns structured lint findings (the quality beat).
- **Pending `ant auth login`** (deferred by user, per project memory): the two model-*driven* observations — the agent itself deciding to call `evaluate_matlab_code` for prompt 1, and inserting the `check_matlab_code` beat before running — need the backend's `AsyncAnthropic()` creds. The plumbing for both is proven; only the live model turn remains, to be confirmed at first rehearsal (note fallback `claude-sonnet-4-6` if opus-4-8 latency drags).

## Blocked by
- #2 (environment & `mbd_demo.slx`) — core server + shared session must exist.
- #3 (skeleton) — the chain to swap onto real MCP.
- #5 (content) — system prompt (figure export, guardrails, workspace re-derivation) and tool subset.
