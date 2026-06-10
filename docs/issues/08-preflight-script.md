# Slice 8 — Pre-flight script

**Type:** AFK · **Blocked by:** #7 (MATLAB live)

## Parent
PRD #1 — Live AI Demo: Chatbot care conduce MATLAB/Simulink prin MCP

## What to build
A pre-flight script that reduces live error by checking what it can and starting the demo (supports S5).

- Checks: is MATLAB shared / reachable in `existing` mode? does the server respond? does the figure folder exist?
- Starts the backend + opens the browser.
- **Fails loudly** at pre-flight time if MATLAB isn't started + shared — so the problem is caught before the audience, not during the demo.

## Acceptance criteria
- [ ] Running the script verifies MATLAB shared/reachable, server responsiveness, and figure-folder existence.
- [ ] The script starts the backend and opens the browser.
- [ ] If MATLAB is not shared, the script fails loudly with a clear message instead of starting in a broken state.
- [ ] After implementation, create a commit with a descriptive message summarizing what was achieved.

## Blocked by
- #7 (MATLAB live) — the checks target the real MATLAB/MCP setup.
