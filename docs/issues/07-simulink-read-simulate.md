# Slice 7 — Simulink read + simulate on `demo.slx`

**Type:** AFK · **Blocked by:** #7 (MATLAB live); needs `demo.slx` from #2

## Parent
PRD #1 — Live AI Demo: Chatbot care conduce MATLAB/Simulink prin MCP

## What to build
Show the agent driving Simulink, tying the demo to the team's MBD work (PRD phase F3). We use the full Simulink Agentic Toolkit but expose **only read + simulate** to keep the ISO 26262 read-only narrative.

- Expose the Simulink read/sim tool subset to the agent (no write/modify tools).
- Scripted **prompt 3** drives: open `demo.slx` → `sim` → read the **To Workspace** signal → return output + figure.
- The read-only / no-destructive guardrail (from the system prompt) holds — the model `.slx` is never modified.

## Acceptance criteria
- [ ] Prompt 3 opens `demo.slx`, simulates it, and reads the logged To Workspace signal.
- [ ] Output and a figure for the Simulink run appear in the timeline.
- [ ] No write/modify Simulink tools are exposed; `demo.slx` is not modified.
- [ ] After implementation, create a commit with a descriptive message summarizing what was achieved.

## Blocked by
- #7 (MATLAB live) — real MCP + session required.
- (Also depends on `demo.slx` from #2.)
