# Slice 7 — Simulink read + simulate on `mbd_demo.slx`

**Type:** AFK · **Recommended model:** Sonnet 4.6 · **Blocked by:** #7 (MATLAB live); needs `mbd_demo.slx` from #2

## Parent
PRD #1 — Live AI Demo: Chatbot care conduce MATLAB/Simulink prin MCP

## What to build
Show the agent driving Simulink, tying the demo to the team's MBD work (PRD phase F3). We use the full Simulink Agentic Toolkit but expose **only read + simulate** to keep the ISO 26262 read-only narrative.

- Expose the Simulink read/sim tool subset to the agent (no write/modify tools).
- Scripted **prompt 3** drives: open `mbd_demo.slx` → `sim` → read the **To Workspace** signal → return output + figure.
- The read-only / no-destructive guardrail (from the system prompt) holds — the model `.slx` is never modified.

## Acceptance criteria
- [ ] Prompt 3 opens `mbd_demo.slx`, simulates it, and reads the logged To Workspace signal. *(code in place; live run pending — see notes)*
- [ ] Output and a figure for the Simulink run appear in the timeline. *(pipeline complete from #6; live run pending)*
- [x] No write/modify Simulink tools are exposed; `mbd_demo.slx` is not modified.
- [x] After implementation, create a git commit with a relevant `-m` message describing what was achieved. **Commit only — do not push.**

## Implementation notes
The read+simulate plumbing was front-loaded into #4 (tool subset + prompt 3) and #6
(figure pipeline), so this slice is wiring-verification rather than new code.

- **Read-only tool surface** ([backend/agent.py](../../backend/agent.py) `DEMO_TOOLS`): of the
  7 Simulink tools in the toolkit manifest
  (`~/.matlab/agentic-toolkits/simulink/tools/tools.json` — `model_overview`, `model_read`,
  `model_query_params`, `model_resolve_params`, `model_edit`, `model_check`, `model_test`),
  the agent is exposed **only** the five read-only ones. The sole write/modify tool,
  `model_edit` (add/delete/configure/save blocks), and the test-executing `model_test` are
  **withheld** — so the read-only / no-destructive ISO-26262 narrative holds at the tool
  surface, not just in the system prompt. Verified against the manifest.
- **Prompt 3** ([public/app.js](../../public/app.js) `PROMPTS["3"]`): opens `mbd_demo.slx`,
  asks for a short structural overview, simulates it, reads the logged displacement signal,
  and plots it to compare against the step-1 MATLAB response (same physics).
- **Guardrail** ([backend/agent.py](../../backend/agent.py) `SYSTEM_PROMPT`, "Simulink guardrail"):
  every model is treated as READ-ONLY; the model is opened/inspected/simulated but never
  edited or saved.
- **Figure export**: reuses the #6 watch-folder → base64 SSE pipeline; the system prompt's
  `exportgraphics` instruction renders the Simulink-signal plot inline in the timeline card.

**Pending live verification:** the model-driven prompt-3 run needs a shared MATLAB R2026a
session (`shareMATLABSession`) plus `ant auth login` for the backend's `AsyncAnthropic`
credentials — both still outstanding (as in #5/#6). Static review confirms the tool surface
is read-only and the prompt/figure wiring is correct; the open → `sim` → read-To-Workspace →
plot behavior against real Simulink remains to be exercised end-to-end.

## Blocked by
- #7 (MATLAB live) — real MCP + session required.
- (Also depends on `mbd_demo.slx` from #2.)
