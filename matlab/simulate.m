function [ise,t,y] = simulate(sim_step,sim_time,kp,Ti,Td,T,tau,num,den)
%SIMULATE Summary of this function goes here
%   Detailed explanation goes here

sim('circuit');

t = ScopeData(:,1);
y = ScopeData(:,2);

uchyby = Uchyb(:,2);        % uchyb
uchyby = uchyby.^2;         % kwadrat uchybu
uchyby = uchyby.*sim_step;  % e^2 * dt
ise = sum(uchyby);          % całka jako suma

end

