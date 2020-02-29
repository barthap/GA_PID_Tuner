clear;

% Ten plik sluzy do testowania matlabowej funkcji 

sim_step = 0.01;
sim_time = 10;

kp = 14.98;
Ti = 1.592;
Td = 4.343;
T = 0.01;
tau = 0.1;
num = [1];
den = [1 1];

[ise, t, y] = simulate(sim_step,sim_time,kp,Ti,Td,T,tau,num,den);
plot(t, y, 'b', 'LineWidth', 2), hold on
disp(ise)

[ise, t2, y2] = simulate2(sim_step,sim_time,kp,Ti,Td,T,tau,num,den);
plot(t2, y2, 'g', 'LineWidth', 2)
disp(ise)

%disp(sum(y-y2))