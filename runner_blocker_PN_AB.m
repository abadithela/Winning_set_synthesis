%% Runner-blocker test synthesis
% 11/4/19 A. Badithela
% In this program, we use the ARCs toolbox to generate winning sets for the
% runner/blocker example. There are 5 physical locations in the system
% which the runner/blocker could occupy. The runner tries to get from home
% to goal state by getting past the blocker lane. The blocker is
% constrained to move up/down in the middle lane.
% References: Synthesis of Reactive Protocols, RM Murray, N. Wongpiromsarn,
% U Topcu, (http://www.cds.caltech.edu/~murray/courses/afrl-sp12/L7_reactive-25Apr12.pdf) 
% Toolbox used: ARCS by P. Nilsson (github.com/pettni/arcs/blob/master/tests/test_synthesis.m)
% See reference for an illustration of the runner blocker example or run
% simulation below:

% System can occupy states 1 through 5. 1 is the initial state of the
% system and 5 is the goal state. The blocker occupies states {2,3,4}
% (which correspond to states {1,2,3} in the environment's perspective}

% This file is very similar to runner-blocker_petter_mods. The one
% difference is that the environment must constantly keep changing and
% can't stay where it is. The environment can only stay where it is in
% "bad" states.

clear 
close all
nX = 5;
nE = 5;
nStates = nX*nE;
nActions = 5; 
s = TransSyst(nStates, nActions);
s.b_debug = 1;
states = []; % Stores all the states of the system

get_state = @(sys_state, env_state) 3 * (sys_state-1) + env_state;

% Add system transitions:
sys_trans = {[1,2,3,4]; [1,2,3,5]; [1,2,3,4,5]; [1,3,4,5]; [2,3,4,5]};
env_trans = {[1]; [3]; [2,4]; [3]; [5]};
for sys_state1 = 1:nX
	for sys_state2 = sys_trans{sys_state1}
		for env_state1 = 1:nE
			for env_state2 = env_trans{env_state1}
				s.add_transition(get_state(sys_state1, env_state1), ...
										     get_state(sys_state2, env_state2), ...
										     sys_state2);
			end
		end
	end
end


% Finding collision states:
% Collision happens when system and environment occupy the same state:
% (sys_state 2 =  env_state 1), (sys_state 3 =  env_state 2), (sys_state 4 =  env_state 3)
collision_states = [];
for state = 1:nX
    collision_states = [collision_states,  get_state(state, state)];
end

%% Finding winning sets:
% ARCS generates winning sets for specifications of the form: []A & <>[] B
% & intersection([]<> C_i)
% The goal set is given by V0, which is where the runner wants to reach
% finally
goal_set = [];
for state = 1:nX
	goal_set = [goal_set get_state(5, state)]; 
end
goal_set = setdiff(goal_set, collision_states);

% Specifying safety and liveness properties:
% Safety property is captured in A because the spec is []A
% Liveness is captured by Ci because we have []<> Ci. In this example, 
% A = {safe states i.e no collisions}
% B = {}
% C = V0 (because eventually the runner needs to reach goal)

A = setdiff(1:25, collision_states);
B = [];
Clist = {goal_set};
quant1 = 'exists';
quant2 = 'forall';
[V, Cv, cont] = s.win_primal(A, B, Clist, quant1, quant2);

% Winning sets 
sys_win = [];
env_win = [];
for win_state = double(V)
    if(rem(win_state,5) == 0)
        env_win = [env_win, 5];
        sys_win = [sys_win, fix(win_state/5)];
    else
        env_win = [env_win, mod(win_state,5)];
        sys_win = [sys_win, fix(win_state/5)+1];
    end
end
%% Plotting runner/blocker game graph
% Defining a sparse adjacency matrix as the transition system with both
% environment and system actions
iS = []; jS = []; vS = [];
for iX = 1:nX
    sys_next = cell2mat(sys_trans(iX));
    iS = [iS, iX*ones(1, length(sys_next))];
    jS = [jS, sys_next];
    vS = [vS, 2*ones(1, length(sys_next))];
end

% for iE = 1:nE
%     env_next = cell2mat(env_trans(iE));
%     iS = [iS, (iE+1)*ones(1, length(env_next))];
%     jS = [jS, env_next+1];
%     vS = [vS, ones(1, length(env_next))];
% end

ADJ = sparse(iS, jS, vS, 5, 5);
G = graph(ADJ);
figure(1)
title('Runner/Blocker Illustration');
plot(G);
%% Plotting runner/blocker simulation:
