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
- [x] Running a prompt that produces a figure shows that figure inline in the timeline card, live.
- [x] Clicking a figure opens a full-screen lightbox.
- [x] Only newly-created PNGs are emitted; old figures are not re-shown.
- [x] A new figure is emitted exactly once over SSE (covered by a test).
- [x] After implementation, create a git commit with a relevant `-m` message describing what was achieved. **Commit only — do not push.**

## Implementation notes
- **Choke-point watch** ([backend/instrumented_session.py](../../backend/instrumented_session.py)): after each `tool_result`, `_emit_new_figures()` scans `figures_dir` (oldest-first) and emits any PNG not already seen as a `figure` event. The seen-set is seeded with the folder's contents at construction, so pre-existing figures (prior turns/runs) are never re-emitted and each new figure is sent exactly once — decoupled from the agent's chosen filename. `figures_dir` is threaded from `agent.FIGURES_DIR` via `run_turn`; the lifespan `mkdir`s it so `exportgraphics` and the watch always have a folder.
- **New SSE event** ([backend/events.py](../../backend/events.py)): `figure(call_id, name, data, mime)` — base64 PNG tied to the producing tool call's `id`.
- **UI** ([public/app.js](../../public/app.js), [styles.css](../../public/styles.css), [index.html](../../public/index.html)): `renderFigure` appends a column-width `<img>` into the matching card; click → full-screen lightbox overlay (backdrop-click or Escape to close) — for 50/50 Teams legibility.
- **Tests** ([tests/test_instrumented_session.py](../../tests/test_instrumented_session.py)): a new PNG after a `tool_result` is emitted exactly once and attributed to its call (`tool_use → tool_result → figure`); pre-existing PNGs are never emitted. 14 tests pass.
- **Verified live** (real Core Server, stubbed driver, no Anthropic API): a plot + the system-prompt `exportgraphics` line produced `agent_text → tool_use → tool_result → figure → done`, with a real ~27 KB PNG whose `id` matches the tool card. The model-*driven* run is pending `ant auth login` (as in Issue 05); the figure pipeline and UI are complete.

## Blocked by
- #7 (MATLAB live) — real MATLAB must generate figures via the export instruction.
