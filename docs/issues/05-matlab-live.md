# Slice 5 — MATLAB live: real core server, `existing` strict

**Type:** AFK · **Blocked by:** #2 (env/demo.slx), #3 (skeleton), #5 (content)

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
- [ ] Backend connects to the real MATLAB MCP Core Server over stdio.
- [ ] `existing` strict mode fails loudly at startup when no shared MATLAB session is present.
- [ ] Prompt 1 runs in the real MATLAB and returns numeric output shown in the card (not a mock).
- [ ] Base-workspace persistence between `evaluate` calls is validated manually.
- [ ] `check_matlab_code` shows as a distinct beat before the run.
- [ ] After implementation, create a commit with a descriptive message summarizing what was achieved.

## Blocked by
- #2 (environment & `demo.slx`) — core server + shared session must exist.
- #3 (skeleton) — the chain to swap onto real MCP.
- #5 (content) — system prompt (figure export, guardrails, workspace re-derivation) and tool subset.
