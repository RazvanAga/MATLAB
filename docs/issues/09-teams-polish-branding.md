# Slice 9 — Teams-readable polish + branding + error cards

**Type:** AFK · **Recommended model:** Sonnet 4.6 · **Blocked by:** #3 (skeleton)

## Parent
PRD #1 — Live AI Demo: Chatbot care conduce MATLAB/Simulink prin MCP

## What to build
Visual polish calibrated for Teams video compression and the agentic-step/explainability story (supports S3/S4). The skeleton UI already exists; this makes it legible and branded.

- **Aesthetic:** light technical-console look, high contrast, large fonts (avoid thin fonts and low-contrast greys that die under Teams compression).
- **Code/text rendering:** `highlight.js` (MATLAB code) + `marked` (agent markdown), **vendored locally** — zero CDN.
- **Branding:** discrete Schaeffler logo top (`public/Schaeffler_logo.svg.png`) + an "internal demo tool" line; Schaeffler green accent (~#009B3D). Optional discrete MATLAB/Simulink logos on cards/footer.
- **Running feedback:** card appears immediately in "running" state with a spinner ("rulează în MATLAB…") and fills on `tool_result`, making latency visible rather than frozen.
- **Error card:** clean card with a sober red accent + the real traceback hidden under an expand (supports S4).
- **Defaults:** auto-scroll that follows the latest card (no jerk when scrolled up), system sans + mono for code, horizontal scroll on long code blocks.

## Acceptance criteria
- [ ] MATLAB code is syntax-highlighted and agent text renders markdown, both via locally-vendored libs (no CDN).
- [ ] Schaeffler logo + green accent + "internal demo tool" line are present and discrete.
- [ ] Running cards show a spinner; errors render as a red-accented card with traceback under an expand.
- [ ] Auto-scroll follows the latest card; long code blocks scroll horizontally; fonts are large/high-contrast for Teams.
- [ ] After implementation, create a git commit with a relevant `-m` message describing what was achieved. **Commit only — do not push.**

## Blocked by
- #3 (skeleton) — the UI/timeline to style must exist.
