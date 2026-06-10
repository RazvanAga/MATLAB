# Slice 10 — Safety-net: rehearsal, recording, Teams staging test

**Type:** HITL · **Recommended model:** N/A (manual) · **Blocked by:** #8, #9, #10, #6

## Parent
PRD #1 — Live AI Demo: Chatbot care conduce MATLAB/Simulink prin MCP

## What to build
Final rehearsal and fallback assets so the live demo is safe (PRD S1). Manual, judgment-driven work — HITL.

- **3 consecutive successful end-to-end runs** at rehearsal (S1 reliability criterion), each starting from reset.
- **Video recording + screenshots** of one successful run as a fallback if anything fails live.
- **Teams staging test:** share full screen with browser + MATLAB 50/50, on a trial Teams call, confirming that text and figures are legible at the far end. Tune MATLAB Command Window font (~16–18pt) + Editor, and confirm cards work in a narrow column.

## Acceptance criteria
- [ ] 3 consecutive successful runs completed without crash, each from reset. *(human rehearsal — protocol + sign-off table ready)*
- [ ] A video recording and screenshots of a successful run are saved as backup. *(capture steps + asset scaffold ready)*
- [ ] A trial Teams 50/50 screen-share confirms legibility of text and figures at the receiving end. *(staging checklist ready; needs a second person/device)*
- [ ] MATLAB font sizes and card layout adjusted as needed for narrow-column legibility. *(tuning guide + settings log ready)*
- [x] Commit any produced artifacts (screenshots, recording links, tuned settings notes) with a relevant `-m` message. **Commit only — do not push.**

## Implementation notes
This slice is **HITL / manual** (`Recommended model: N/A`): the three live deliverables — three
consecutive clean runs, a screen recording, and a far-end-verified Teams 50/50 share — can only
be done by a person on a real call, and depend on a live shared MATLAB session + `ant auth login`
(still pending, as in #5/#6). What an agent *can* produce is the rehearsal apparatus, committed
here so the manual work is mechanical and the boxes above get ticked during the actual rehearsal:

- **[docs/rehearsal/README.md](../rehearsal/README.md)** — the runbook: per-session setup
  (incl. the `shareMATLABSession` gotcha and a warm-up run), display/font tuning for Teams
  compression, the **3-run protocol** (Reset → Step 1 → Step 2 → Step 3, with a per-beat
  expectations table and a 3-run results table), fallback-asset capture, the Teams 50/50
  **far-end legibility** checklist, and a go/no-go + live-call ritual.
- **[docs/rehearsal/tuned-settings.md](../rehearsal/tuned-settings.md)** — table to record the
  final MATLAB font / browser zoom / display-scaling / window-split values that survive the
  far-end test (the "adjusted as needed" criterion).
- **[docs/rehearsal/fallback-assets.md](../rehearsal/fallback-assets.md)** +
  **[docs/rehearsal/screenshots/](../rehearsal/screenshots/)** — where the recording **link** and
  **screenshots** go. `.gitignore` now excludes `*.mp4/*.mov/*.mkv/*.webm` so a large raw
  recording can't be committed by accident; screenshots (PNG) are tracked.

**Status:** apparatus committed; the live rehearsal, recording, and Teams staging remain for the
human to execute (and tick off in the runbook) once a live session + credentials are available.

## Blocked by
- #8 (figures), #9 (Simulink), #10 (pre-flight), #6 (polish) — the full demo must be working.
