# Slice 10 — Safety-net: rehearsal, recording, Teams staging test

**Type:** HITL · **Blocked by:** #8, #9, #10, #6

## Parent
PRD #1 — Live AI Demo: Chatbot care conduce MATLAB/Simulink prin MCP

## What to build
Final rehearsal and fallback assets so the live demo is safe (PRD S1). Manual, judgment-driven work — HITL.

- **3 consecutive successful end-to-end runs** at rehearsal (S1 reliability criterion), each starting from reset.
- **Video recording + screenshots** of one successful run as a fallback if anything fails live.
- **Teams staging test:** share full screen with browser + MATLAB 50/50, on a trial Teams call, confirming that text and figures are legible at the far end. Tune MATLAB Command Window font (~16–18pt) + Editor, and confirm cards work in a narrow column.

## Acceptance criteria
- [ ] 3 consecutive successful runs completed without crash, each from reset.
- [ ] A video recording and screenshots of a successful run are saved as backup.
- [ ] A trial Teams 50/50 screen-share confirms legibility of text and figures at the receiving end.
- [ ] MATLAB font sizes and card layout adjusted as needed for narrow-column legibility.

## Blocked by
- #8 (figures), #9 (Simulink), #10 (pre-flight), #6 (polish) — the full demo must be working.
