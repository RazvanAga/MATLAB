# Slice 3 — Demo control surface: prompt buttons + empty state + reset

**Type:** AFK · **Recommended model:** Sonnet 4.6 · **Blocked by:** #3 (skeleton)

## Parent
PRD #1 — Live AI Demo: Chatbot care conduce MATLAB/Simulink prin MCP

## What to build
The demo driver's control surface on top of the existing skeleton UI, so the demo runs entirely from buttons with no live typing.

- A **numbered sequence of prompt buttons** (1, 2, 3) that send the exact scripted prompts, plus a separate **"extra-safe"** button with a second tested prompt (for "can I try it too?").
- All buttons stay **visible and re-clickable** so any step can be repeated on request.
- **Empty state**: title + buttons + one context line ("chatbot care conduce MATLAB/Simulink live prin MCP").
- **Reset** button that clears the timeline **and** sends `close all; clear` to MATLAB through the normal tool path, so each rehearsal run starts from identical state. (Against the Mock MCP the MATLAB effect is inert; the timeline-clear and command dispatch are verifiable now and the MATLAB effect is confirmed in Slice 5.)

The actual prompt text and extra-safe prompt come from Slice 4; wire the buttons to consume that content (placeholders acceptable until Slice 4 lands).

## Acceptance criteria
- [x] Numbered prompt buttons (1/2/3) + an extra-safe button are present and each sends its prompt.
- [x] Buttons remain visible and re-clickable after use; a step can be repeated.
- [x] Empty state shows title, buttons, and the context line.
- [x] Reset clears the timeline and dispatches `close all; clear` over the tool path.
- [x] After implementation, create a git commit with a relevant `-m` message describing what was achieved. **Commit only — do not push.**

## Blocked by
- #3 (skeleton) — the timeline/SSE/tool path must exist.
