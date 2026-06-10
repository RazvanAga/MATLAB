# Slice 1 — F0: Environment & `demo.slx`

**Type:** HITL · **Blocked by:** none

## Parent
PRD #1 — Live AI Demo: Chatbot care conduce MATLAB/Simulink prin MCP

## What to build
Stand up the local prerequisites the live demo depends on (PRD phase F0). This is manual setup on the demo laptop, not application code:

- Install `simulink-agentic-toolkit` (`.mltbx` → `setupAgenticToolkit("install")`), which also downloads the MATLAB MCP Core Server (standalone Go binary) into `~/.matlab/agentic-toolkits/`.
- Run `ant auth login` so the backend can resolve Anthropic credentials with `anthropic.Anthropic()` (no explicit key).
- Build `demo.slx`: the **same** mass-spring-damper system as the first MATLAB prompt, but as a block diagram. Log the output signal explicitly with a **To Workspace** block so it is trivial to read (does not depend on `out.yout` structure).
- Verify available toolboxes with `detect_matlab_toolboxes` and record the exact required-toolbox list for `demo.slx`.

## Acceptance criteria
- [ ] `simulink-agentic-toolkit` installs cleanly and the MATLAB MCP Core Server binary is present under `~/.matlab/agentic-toolkits/`.
- [ ] `ant auth login` completed; credential resolution works for the backend.
- [ ] `demo.slx` exists, simulates, and writes its output signal via a To Workspace block.
- [ ] The exact list of toolboxes required by `demo.slx` is documented (e.g. in `docs/`).
- [ ] The `.mltbx` install was tested in isolation before relying on it (risk mitigation).

## Blocked by
None — can start immediately.
