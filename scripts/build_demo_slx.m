%% build_demo_slx.m
% Builds demo.slx: mass-spring-damper as a Simulink block diagram.
%
% System: m·ẍ + c·ẋ + k·x = F(t)
%   m = 1 kg, c = 1.5 N·s/m, k = 20 N/m
%   F = unit step at t = 0 (1 N)
%
% Same physics as the first MATLAB chat prompt (mass_spring_damper_ode45),
% now expressed as a block diagram for the MBD narrative.
%
% Output signal x(t) is logged via a To Workspace block (variable "x",
% Array format) so it is trivially readable without depending on out.yout.
% The simulation time vector is available as "tout" in the base workspace.
%
% Usage: run from MATLAB with the repo root on the path, or call directly:
%   >> run('scripts/build_demo_slx.m')

mdl      = 'demo';
out_path = fullfile(fileparts(mfilename('fullpath')), '..', 'demo.slx');

% --- Parameters ---
m = 1;     % mass [kg]
c = 1.5;   % damping coefficient [N·s/m]
k = 20;    % spring stiffness [N/m]

% --- Setup ---
if bdIsLoaded(mdl)
    close_system(mdl, 0);
end
new_system(mdl);
open_system(mdl);

set_param(mdl, ...
    'StopTime',  '10', ...
    'Solver',    'ode45', ...
    'SolverType','Variable-step');

% =============================================================
% Main signal path (left → right, y-centre ≈ 150)
% Layout: F → Sum → Gain(1/m) → Int(v) → Int(x) → outputs
% =============================================================

add_block('simulink/Sources/Step', [mdl '/F'], ...
    'Position',   [40 135 80 165], ...
    'Time',       '0', ...
    'Before',     '0', ...
    'After',      '1', ...
    'SampleTime', '0');

% Sum with three inputs: +F -c·v -k·x
add_block('simulink/Math Operations/Sum', [mdl '/Sum'], ...
    'Position', [150 110 190 200], ...
    'Inputs',   '+--');

% Acceleration: a = (F - c·v - k·x) / m
add_block('simulink/Math Operations/Gain', [mdl '/Gain_inv_m'], ...
    'Position', [240 135 290 165], ...
    'Gain',     num2str(1/m));

% Integrator 1: a → v (velocity)
add_block('simulink/Continuous/Integrator', [mdl '/Int_v'], ...
    'Position',          [360 135 400 165], ...
    'InitialCondition',  '0');

% Integrator 2: v → x (position)
add_block('simulink/Continuous/Integrator', [mdl '/Int_x'], ...
    'Position',          [470 135 510 165], ...
    'InitialCondition',  '0');

% To Workspace: logs position x(t) — Array format, no out.yout dependency
add_block('simulink/Sinks/To Workspace', [mdl '/x_out'], ...
    'Position',      [590 130 670 160], ...
    'VariableName',  'x', ...
    'SaveFormat',    'Array', ...
    'MaxDataPoints', 'inf');

% Scope: visual confirmation during manual runs
add_block('simulink/Sinks/Scope', [mdl '/Scope'], ...
    'Position', [590 185 670 215]);

% =============================================================
% Feedback path (below main path)
% c·v and k·x return to the Sum as negative inputs
% =============================================================

% Damping feedback: v → Gain(c) → Sum port 2
add_block('simulink/Math Operations/Gain', [mdl '/Gain_c'], ...
    'Position', [360 255 400 285], ...
    'Gain',     num2str(c));

% Stiffness feedback: x → Gain(k) → Sum port 3
add_block('simulink/Math Operations/Gain', [mdl '/Gain_k'], ...
    'Position', [470 310 510 340], ...
    'Gain',     num2str(k));

% =============================================================
% Connections
% =============================================================
ar = {'autorouting', 'smart'};

% Main path
add_line(mdl, 'F/1',          'Sum/1',         ar{:});
add_line(mdl, 'Sum/1',        'Gain_inv_m/1',  ar{:});
add_line(mdl, 'Gain_inv_m/1', 'Int_v/1',       ar{:});
add_line(mdl, 'Int_v/1',      'Int_x/1',       ar{:});
add_line(mdl, 'Int_x/1',      'x_out/1',       ar{:});
add_line(mdl, 'Int_x/1',      'Scope/1',       ar{:});

% Velocity feedback (port 2 = negative)
add_line(mdl, 'Int_v/1',   'Gain_c/1', ar{:});
add_line(mdl, 'Gain_c/1',  'Sum/2',    ar{:});

% Position feedback (port 3 = negative)
add_line(mdl, 'Int_x/1',  'Gain_k/1', ar{:});
add_line(mdl, 'Gain_k/1', 'Sum/3',    ar{:});

% =============================================================
% Save
% =============================================================
save_system(mdl, out_path);
close_system(mdl, 0);
fprintf('Saved: %s\n', out_path);

% Quick smoke-test: simulate and verify output is non-empty
fprintf('Running smoke-test simulation...\n');
load_system(out_path);
simOut = sim(mdl, 'StopTime', '10');
assert(exist('x', 'var') == 1 && ~isempty(x), ...
    'Smoke test failed: variable x not written to workspace.');
fprintf('Smoke test passed — x has %d samples.\n', length(x));
close_system(mdl, 0);
