G=tf([1], [5 1], 'InputDelay', 1);   % The plant
[C1,params]=optimPID(G,3,1);   % PID-Control, ISE index

t=0:0.01:25;
y1=step(feedback(C1*G,1),t); %Closed-loop step response of C1

plot(t,y1,'--','Linewidth',2)
legend('ISE')
grid