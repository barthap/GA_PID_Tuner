function [ise,t,y] = simulate2(sim_step,sim_time,kp,Ti,Td,T,tau,num,den)
%SIMULATE Summary of this function goes here
%   Detailed explanation goes here

time_vec = 0:sim_step:sim_time;


tf_P = tf(kp);
tf_I = tf([1], [Ti 0]);
tf_D = tf([Td 0], [T 1]);

tf_PID = parallel(tf(1), tf_I);
tf_PID = parallel(tf_PID, tf_D);
tf_PID = series(tf_PID, tf_P);

tf_obj = tf(num, den, 'InputDelay', tau);
G = series(tf_PID, tf_obj);
G = feedback(G, 1);

[y, t] = step(G, time_vec);
[y2, ~] = step(tf(1), t);

uchyby = y2-y;        % uchyb
uchyby = uchyby.^2;         % kwadrat uchybu
uchyby = uchyby.*sim_step;  % e^2 * dt
ise = sum(uchyby);          % całka jako suma

end

