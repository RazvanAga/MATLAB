# Slice 6 — Figures inline + lightbox

**Type:** AFK · **Recommended model:** Sonnet 4.6 · **Blocked by:** #7 (MATLAB live)

## Parent
PRD #1 — Live AI Demo: Chatbot care conduce MATLAB/Simulink prin MCP

## What to build
The wow-factor of live figures appearing in the chat (PRD phase F3, supports S3). Built on the existing tool-wrapper choke-point.

- The tool wrapper **watches the figure folder** and, after a `tool_result`, emits any **new** PNG as base64 over SSE — decoupled from the exact filename, and **without re-emitting** older figures.
- The UI renders figures **inline at column width**, with **click → full-screen lightbox** (essential for 50/50 Teams screen-share legibility).
- Figure-detection tests: a new file appearing in the folder after a `tool_result` is emitted exactly **once** on SSE (never re-emitted).

## Acceptance criteria
- [ ] Running a prompt that produces a figure shows that figure inline in the timeline card, live.
- [ ] Clicking a figure opens a full-screen lightbox.
- [ ] Only newly-created PNGs are emitted; old figures are not re-shown.
- [ ] A new figure is emitted exactly once over SSE (covered by a test).
- [ ] After implementation, create a git commit with a relevant `-m` message describing what was achieved. **Commit only — do not push.**

## Blocked by
- #7 (MATLAB live) — real MATLAB must generate figures via the export instruction.
