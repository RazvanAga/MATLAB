# Required Toolboxes — mbd_demo.slx

## Hard requirements (demo fails without these)

| Toolbox | Why |
|---------|-----|
| **Simulink** (base) | Model simulation, all blocks in `mbd_demo.slx` |

`mbd_demo.slx` uses only standard Simulink base blocks (Step, Sum, Gain, Integrator, To Workspace, Scope). No additional MathWorks toolboxes are required to simulate it.

## Required for the MCP / agentic layer

| Component | Why |
|-----------|-----|
| **Simulink Agentic Toolkit** (`.mltbx`) | Provides the 7 Simulink MCP tools (`open_simulink_model`, `run_simulink_simulation`, etc.) and downloads the MATLAB MCP Core Server (Go binary) into `~/.matlab/agentic-toolkits/`. |

Install via: `setupAgenticToolkit("install")` after adding the `.mltbx` to MATLAB.

## Verification

Run `ver` in the MATLAB Command Window — it lists licensed products directly.
(`detect_matlab_toolboxes` is an **MCP tool the agent calls**, not a MATLAB
command, so it won't resolve if typed in the Command Window.)

**Verified 2026-06-10 (R2026a)** — `ver` reports:

```
MATLAB                          Version 26.1   (R2026a)
Simulink                        Version 26.1   (R2026a)
MATLAB MCP Core Server Toolbox  Version 0.1.1  (R2026a)
```

i.e. **MATLAB base + Simulink only**. No optional toolboxes are licensed.

## Toolboxes that would expand the demo (NOT licensed on this machine)

| Toolbox | What it enables | Status |
|---------|----------------|--------|
| Control System Toolbox | `stepinfo()` for rise/settling time — prompt 2 (overshoot analysis) | ❌ not licensed |
| Signal Processing Toolbox | Advanced signal analysis on logged `x` output | ❌ not licensed |

**Consequence:** Control System Toolbox is **confirmed absent**, so **prompt 2
(Issue 04) must compute settling time manually from the `x` array** — do not
rely on `stepinfo()`.
