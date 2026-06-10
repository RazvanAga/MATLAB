# Required Toolboxes — demo.slx

## Hard requirements (demo fails without these)

| Toolbox | Why |
|---------|-----|
| **Simulink** (base) | Model simulation, all blocks in `demo.slx` |

`demo.slx` uses only standard Simulink base blocks (Step, Sum, Gain, Integrator, To Workspace, Scope). No additional MathWorks toolboxes are required to simulate it.

## Required for the MCP / agentic layer

| Component | Why |
|-----------|-----|
| **Simulink Agentic Toolkit** (`.mltbx`) | Provides the 7 Simulink MCP tools (`open_simulink_model`, `run_simulink_simulation`, etc.) and downloads the MATLAB MCP Core Server (Go binary) into `~/.matlab/agentic-toolkits/`. |

Install via: `setupAgenticToolkit("install")` after adding the `.mltbx` to MATLAB.

## Verification

Run the following in MATLAB after the agentic toolkit is installed:

```matlab
% Lists all licensed toolboxes — confirm Simulink is present
detect_matlab_toolboxes
```

Expected minimum output includes `Simulink`.

## Toolboxes that expand the demo (optional, not required)

| Toolbox | What it enables |
|---------|----------------|
| Control System Toolbox | `stepinfo()` for rise/settling time — used in prompt 2 (overshoot analysis) |
| Signal Processing Toolbox | Advanced signal analysis on logged `x` output |

If Control System Toolbox is unavailable, prompt 2 can be rewritten to compute settling time manually from the `x` array without `stepinfo`.
