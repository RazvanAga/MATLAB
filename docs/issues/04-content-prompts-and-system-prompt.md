# Slice 4 — Content: scripted prompts + system prompt + tool subset

**Type:** HITL · **Recommended model:** Opus 4.8 · **Blocked by:** #3 (skeleton)

## Parent
PRD #1 — Live AI Demo: Chatbot care conduce MATLAB/Simulink prin MCP

## What to build
Author and review the agent-facing content and configuration — the "De definit înainte de build" checklist. Requires human judgment, so this is HITL.

- **Exact text of the 3 scripted demo prompts** (1: mass-spring-damper; 2: overshoot/settling follow-up; 3: Simulink) **and** the "extra-safe" prompt.
- **The focused system prompt** (calm, not aggressive — opus-4-8 follows literally and narrates a lot), covering:
  - instruction to export any figure to a fixed timestamped path via `exportgraphics(gcf, fullfile("<abs path>", sprintf("fig_%s.png", datestr(now,"HHMMSSFFF"))))`;
  - tool-selection guidance toward the restricted demo subset;
  - read-only Simulink + no-destructive-operations guardrail;
  - defensive workspace re-derivation (reuse base-workspace vars if present, otherwise re-run the simulation);
  - instruction to verify code with `check_matlab_code` before running it (the visible quality beat).
- **The restricted tool subset config**: from the ~12 available (5 core + 7 Simulink), expose only `evaluate_matlab_code`, `check_matlab_code`, and the Simulink read/sim tools.
- Note: the toolkit's 9 markdown skills do **not** auto-load in this custom harness; if their expertise is wanted it must be injected manually into the system prompt.

## Acceptance criteria
- [x] Final text of all 3 scripted prompts + the extra-safe prompt is written down and reviewed.
- [x] The system prompt is written and includes: figure-export instruction, tool-selection guidance, read-only/no-destructive Simulink guardrail, defensive workspace re-derivation, and `check_matlab_code`-before-run instruction.
- [x] The restricted tool subset is defined (only the demo tools exposed to the agent).
- [x] Content is stored where the backend/UI slices can consume it.
- [x] Commit the produced content (prompts, system prompt, tool-subset config) with a relevant `-m` message. **Commit only — do not push.**

## Implementation notes
- Scripted prompts live in [public/app.js](../../public/app.js) (`PROMPTS`); the UI buttons already consume them. Kept high-level — the system prompt carries the guardrails — so prompts 1+2 share one mass-spring-damper response and prompt 3 is the same physics in Simulink.
- System prompt + restricted tool subset live in [backend/agent.py](../../backend/agent.py): `SYSTEM_PROMPT` (calm/concise, since opus-4-8 over-narrates), `DEMO_TOOLS` allowlist (filtered in `run_turn`), and `FIGURES_DIR` (pinned in the export instruction; Issue 06 watches it).
- `DEMO_TOOLS` exposes only `evaluate_matlab_code`, `check_matlab_code`, and the five read-only Simulink inspection tools — model-editing/test tools are withheld so the read-only guardrail holds at the tool surface, not just in the prompt. Simulation runs via `sim(...)` inside `evaluate_matlab_code`.
- System prompt also pins the no-Control-System-Toolbox constraint (compute overshoot/settling from arrays, no `stepinfo`), which prompt 2 depends on.

## Blocked by
- #3 (skeleton) — the harness shape determines how the system prompt and tool subset are wired.
