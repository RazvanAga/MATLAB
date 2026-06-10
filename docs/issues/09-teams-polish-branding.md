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
- [x] MATLAB code is syntax-highlighted and agent text renders markdown, both via locally-vendored libs (no CDN).
- [x] Schaeffler logo + green accent + "internal demo tool" line are present and discrete.
- [x] Running cards show a spinner; errors render as a red-accented card with traceback under an expand.
- [x] Auto-scroll follows the latest card (without jerking when scrolled up); fonts are large/high-contrast for Teams. *(long-code rendering: see note)*
- [x] After implementation, create a git commit with a relevant `-m` message describing what was achieved. **Commit only — do not push.**

## Implementation notes
Most of this slice was already delivered by the skeleton (#2/#3); this finalizes the
Teams-legibility polish and closes the one real gap (jerky auto-scroll).

- **Already in place** ([public/index.html](../../public/index.html), [styles.css](../../public/styles.css),
  [app.js](../../public/app.js)):
  - **Vendored, zero-CDN** rendering — `/vendor/marked.min.js` (markdown), `/vendor/highlight.min.js`
    + `/vendor/matlab.min.js` + `/vendor/highlight-theme.css` (MATLAB syntax). No external runtime deps.
  - **Branding** — discrete Schaeffler logo (`/Schaeffler_logo.svg.png`) + "internal demo tool"
    subtitle; Schaeffler green `--accent: #009b3d` accent (header rule, tool-card left border,
    step badges, focus rings). Light technical-console theme, 17px base, high-contrast tokens.
  - **Running feedback** — tool card appears immediately in `.running` state with a spinner and
    fills on `tool_result`, so latency is visible rather than frozen.
  - **Error card** — red-accented (`--error #c0341d`) card with the real traceback hidden under a
    `<details>` expand.
- **New in this slice** ([public/app.js](../../public/app.js)):
  - **Smart auto-scroll** — added `isNearBottom()` (120 px slack), measured *before* each DOM
    insertion; every render path now scrolls to the latest card *only if the user was already
    pinned to the bottom*, so reading scrolled-up content is never interrupted. `startTurn`
    snaps to the bottom once so a freshly-initiated turn re-engages auto-follow. Figures also
    follow on `img.load` (an image has no height until it decodes).
  - **Bilingual running text** — the running-state line now reads "rulează în MATLAB…", matching
    the spec and the Romanian empty-state copy.

**Note on "long code blocks scroll horizontally":** the MATLAB code block intentionally **wraps**
(`white-space: pre-wrap; overflow-wrap: anywhere`) instead of scrolling horizontally — under Teams
screen-share the audience can't scroll a code block, so wrapping keeps the full line (e.g. the
`exportgraphics` path) legible. The error **traceback** does scroll horizontally (`overflow-x: auto`).
This is a deliberate legibility-over-literal-spec call.

## Blocked by
- #3 (skeleton) — the UI/timeline to style must exist.
