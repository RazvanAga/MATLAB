# Slice 1 — F0: Environment & `demo.slx`

**Type:** HITL · **Recommended model:** N/A (manual setup) · **Blocked by:** none

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
- [x] The exact list of toolboxes required by `demo.slx` is documented — see `docs/toolboxes.md`.
- [ ] The `.mltbx` install was tested in isolation before relying on it (risk mitigation).
- [ ] Commit any produced artifacts (e.g. `demo.slx`, toolbox list) with a relevant `-m` message. **Commit only — do not push.**

## How to build demo.slx

Run `scripts/build_demo_slx.m` in MATLAB from the repo root. It builds the block diagram programmatically and runs a smoke-test simulation before saving.

```matlab
run('scripts/build_demo_slx.m')
```

The script will:
1. Create the mass-spring-damper block diagram (Step → Sum → Gain(1/m) → Integrator → Integrator → To Workspace)
2. Wire the damping and stiffness feedback paths
3. Save as `demo.slx` at the repo root
4. Smoke-test by running a 10 s simulation and asserting `x` is non-empty

## Blocked by
None — can start immediately.
