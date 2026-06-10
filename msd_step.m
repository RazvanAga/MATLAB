% Mass-spring-damper step response


m = 1; c = 2; k = 20; F = 1;


odefun = @(t,x) [x(2); (F - c*x(2) - k*x(1))/m];


tspan = [0 5];


x0 = [0; 0];


[t, x] = ode45(odefun, tspan, x0);


disp_mm = x(:,1);


figure;


plot(t, disp_mm, 'LineWidth', 1.5);


grid on;


xlabel('Time (s)');


ylabel('Displacement (m)');


title('Step Response of Mass-Spring-Damper System');


exportgraphics(gcf, fullfile("C:/Users/Razvan/Projects/MATLAB/figures", sprintf("fig_%s.png", datestr(now, "HHMMSSFFF"))))
