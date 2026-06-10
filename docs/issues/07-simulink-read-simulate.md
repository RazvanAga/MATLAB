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
- [ ] Prompt 3 opens `mbd_demo.slx`, simulates it, and reads the logged To Workspace signal.
- [ ] Output and a figure for the Simulink run appear in the timeline.
- [ ] No write/modify Simulink tools are exposed; `mbd_demo.slx` is not modified.
- [ ] After implementation, create a git commit with a relevant `-m` message describing what was achieved. **Commit only — do not push.**

## Blocked by
- #7 (MATLAB live) — real MCP + session required.
- (Also depends on `mbd_demo.slx` from #2.)
