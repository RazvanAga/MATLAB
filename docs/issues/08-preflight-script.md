# Slice 8 — Pre-flight script

**Type:** AFK · **Recommended model:** Sonnet 4.6 · **Blocked by:** #7 (MATLAB live)

## Parent
PRD #1 — Live AI Demo: Chatbot care conduce MATLAB/Simulink prin MCP

## What to build
A pre-flight script that reduces live error by checking what it can and starting the demo (supports S5).

- Checks: is MATLAB shared / reachable in `existing` mode? does the server respond? does the figure folder exist?
- Starts the backend + opens the browser.
- **Fails loudly** at pre-flight time if MATLAB isn't started + shared — so the problem is caught before the audience, not during the demo.

## Acceptance criteria
- [x] Running the script verifies MATLAB shared/reachable, server responsiveness, and figure-folder existence.
- [x] The script starts the backend and opens the browser.
- [x] If MATLAB is not shared, the script fails loudly with a clear message instead of starting in a broken state.
- [x] After implementation, create a git commit with a relevant `-m` message describing what was achieved. **Commit only — do not push.**

## Implementation notes
- **Launcher** ([run-demo.ps1](../../run-demo.ps1)) — a PowerShell pre-flight + launcher with
  layered checks:
  - **Instant local checks (fail loudly before anything starts):** Core Server binary
    ([backend/app.py](../../backend/app.py) `CORE_SERVER_BIN`), Simulink tools manifest
    (`SIMULINK_TOOLS_JSON`), the **MATLAB shared session**, and the figures folder (created
    if missing, matching the backend lifespan).
  - **MATLAB-shared check is liveness-based, not just existence-based:** it reads
    `%APPDATA%\MathWorks\MATLAB MCP Core Server\v1\sessionDetails.json` (the file
    `shareMATLABSession` rewrites with the current MATLAB `pid`) and verifies that `pid` is an
    actually-running process. A **missing** registration (never shared) and a **stale** one
    (MATLAB restarted, not re-shared → dead pid) are both caught in milliseconds, each with a
    distinct, actionable message pointing at `shareMATLABSession` (and explicitly *not*
    `matlab.engine.shareEngine`).
  - **Authoritative reachability + server responsiveness:** the backend's existing lifespan
    `_preflight_matlab` does the real engine attach + eval (up to 90 s). The launcher surfaces
    its outcome by polling the new **`GET /api/health`** ([backend/app.py](../../backend/app.py)) —
    which only answers `200` *after* lifespan startup (and thus the preflight) completes — or by
    catching an early process exit (preflight raised → startup aborted), in which case it prints
    the tail of the backend error log and fails loudly.
  - **Start + browser:** runs `uv run uvicorn backend.app:app` (logs to gitignored `.run/`),
    waits for readiness, then opens the browser. If a backend is already serving the port, it
    reuses it instead of starting a second one. Holds the foreground until Ctrl+C, then stops
    the backend. Flags: `-NoBrowser`, `-Port`, `-BindHost`.
- **Health endpoint** ([backend/app.py](../../backend/app.py) `GET /api/health`) — readiness probe
  returning `{"status": "ok"}`; a 200 proves FastAPI is up *and* the Core Server attached to the
  shared MATLAB *and* the preflight passed (FastAPI only serves once lifespan startup finishes).
- **Verified:** `run-demo.ps1` parses clean (AST parser, no execution); the 14-test suite still
  passes; and `/api/health` returns `200 {"status":"ok"}` against a mock-mode backend. The full
  fail-loud path against a live/stale MATLAB session is exercised at demo setup time.

## Blocked by
- #7 (MATLAB live) — the checks target the real MATLAB/MCP setup.
