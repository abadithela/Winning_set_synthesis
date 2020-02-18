# Vertices of players: V1, V2, and Vp(half-player)
# Player 1: Circle
# Player 2: Diamond
# Stochastic player: Square
# Finite set of actions for environment and system: A1, A2 and finite set of actions
# of the probabilistic player, Ap.
# Transition map from V1 to V2 given by T1
# Transition map from V2 to Vp given by T2
# Probabilistic transition map from Vp to V1 given by Tdelta
# Phi is the specification

import numpy as np
import networkx as nx

# class GG:
#     def __init__(self, V1, V2, Vp, A1, A2, Ap, T1, T2, Tp, L):
#         self.V = (V1, V2, Vp)
#         self.A = (A1, A2, Ap)
#         self.T = (T1, T2, Tp)
#         self.label = L
#         if not Vp:
#             self.graph = nx.complete_bipartite_graph(len(V1), len(V2))
#         else:
#             self.graph = nx.complete_multipartite_graph(len(V1), len(V2), len(Vp))
#         self.build_DFA()

#     def build_DFA(self):
#         pass


# def trans_automata(V1, V2, Vp, x0, A1, A2, Ap, T1, T2, Tp, L, phi):
#     TA = GG(V1, V2, Vp, A1, A2, Ap, T1, T2, Tp, L)
#     return TA

# Unsafe set:
def unsafe(collision_indices):
    U = []
    for ii in collision_indices:
        s = state(ii,ii)
        U.extend(["v1_"+str(s)])
        U.extend(["v2_"+str(s)])
    return U
# Generate transition system:
def trans_sys(V1, V2, Vp, T1, T2, Tp):
    if not Vp:
        GVp = []
    GEdges=[]
    # First all environment action transitions:
    for env_state in range(1,6):
        for end_env_state in T1[env_state-1]:
            for sys_state in range(1,6):
                start_state = state(sys_state, env_state)
                start_vtx = "v1_"+str(start_state)
                end_state = state(sys_state, end_env_state)
                end_vtx = "v2_"+str(end_state)
                edge = [start_vtx, end_vtx, "ae"]
                GEdges.append(edge)
    # Now, all system action transitions:
    for sys_state in range(1,6):
        for end_sys_state in T2[sys_state-1]:
            for env_state in range(1,6):
                start_state = state(sys_state, env_state)
                start_vtx = "v2_"+str(start_state)
                end_state = state(end_sys_state, env_state)
                end_vtx = "v1_"+str(end_state)
                edge = [start_vtx, end_vtx, "as"]
                GEdges.append(edge)
    return GVp, GEdges
# Generate winning sets for 2 player games:
def state(sys_loc, env_loc):
    return 5*(sys_loc) + env_loc

# Given number of system and environment transitions:
def vertices(Ns, Ne):
    Vp =[]
    V1 = []
    V2 = []
    for xs in range(1,Ns+1):
        for xe in range(1,Ne+1):
            s = state(xs, xe)
            V1.extend(["v1_"+str(s)]) # Environment action vertices
            V2.extend(["v2_"+str(s)]) # System action vertices
    return V1, V2, Vp
# Main function to synthesize winning sets:
# Returns winning set for n steps
# N: Maximum number of iterations for fixed-point iterations
# Win_ii_n: The entire winning set upto the nth fixed point iteration
# Pre_ii_n: Consists only of the Pre set of states computed at the nth iteration
def synt_winning_set(GVp, GEdges, U, W0, N):
    W = [W0] # Winning set with 0 iterations
    Pre_cur = W0.copy()
    Win_cur = W0.copy()
    for ii in range(1,N+1):
        Pre_ii = pre(GVp, GEdges, Pre_cur, U, 1, 0, 1)
        Pre_ii_1 = Pre_ii[0].copy()
        Pre_ii_2 = Pre_ii[1].copy()
        Win_cur_1 = Win_cur[0].copy()
        Win_cur_2 = Win_cur[1].copy()
        if Pre_ii_1: # If it is not empty
            Win_cur_1.extend(Pre_ii_1)
            Win_cur_1 = list(dict.fromkeys(Win_cur_1)) # Removes duplicates
        if Pre_ii_2: # If it is not empty
            Win_cur_2.extend(Pre_ii_2)
            Win_cur_2 = list(dict.fromkeys(Win_cur_2)) # Removes duplicates
        Win_ii_1 = Win_cur_1.copy()
        Win_ii_2 = Win_cur_2.copy()
        Win_ii = [Win_ii_1, Win_ii_2]
        W.append(Win_ii)
        Pre_cur = Pre_ii.copy()
        Win_cur = Win_ii.copy()
    return W

# ToDo: Fix the notation of W0 here...
# Defining Predecessor operator for synthesizing winning sets: 
# Assume: Player 1 is the environment and Player 2 is the System
# Winning sets would only contain environment action states
# Pre(S):= {x \in V2| \forall   }
# U: Unsafe set of states
# Qualifier notations: there_exists: 0 and forall: 1
def pre(GVp, GEdges, W0, U, qual1, qual2, qual3):
    if not GVp: # 2-player game winning set
        # Simple backward reachability:
        env_W0 = W0[0].copy() # First row of W0 has env action nodes in winning set
        sys_W0 = W0[1].copy() # Second row of W0 has sys action nodes in winning set
        Win1 = [] # Winning set containing environment action states
        Win2 = [] # Winning set containing system action states
        Win = [] # Winning set containing env winning actions in the first row and sys winning actions in the second row

        # Backward reachability for winning set with environment action state
        for env_win in env_W0:
            end_node = [row[1] for row in GEdges]
            env_win_idx = [ii for ii, x in enumerate(end_node) if x==env_win]
            start_node = [row[0] for row in GEdges] # Extracting the first column in G.Edges
            env_nbr = [start_node[ii] for ii in env_win_idx]
            if env_nbr: # If list is not empty
                for env_nbr_elem in env_nbr:
                    if env_nbr_elem not in U:  # Not in unsafe set
                        Win2.append(env_nbr_elem)

        # Backward reachability for winning set with system action state. All environment actions must lead to a winning state
        for sys_win in sys_W0:
            end_node = [row[1] for row in GEdges]
            potential_sys_win_idx = [ii for ii, x in enumerate(end_node) if x==sys_win]
            start_node = [row[0] for row in GEdges] # Extracting the first column in G.Edges                
            potential_sys_nbr = [start_node[ii] for ii in potential_sys_win_idx]
            sys_nbr = []
            for potential_nbr in potential_sys_nbr:
                if potential_nbr not in U:
                    potential_nbr_idx = [ii for ii, x in enumerate(start_node) if x==potential_nbr]
                    potential_nbr_end_node = [end_node[ii] for ii in potential_nbr_idx]
                    if set(potential_nbr_end_node) <= set(sys_W0):
                        sys_nbr.extend([potential_nbr])
         
            Win1.extend(sys_nbr) 
        Win1 = list(dict.fromkeys(Win1)) # Removes duplicates
        Win2 = list(dict.fromkeys(Win2)) # Removes duplicates
        Win.append(Win1)
        Win.append(Win2)

    else: # Find sure, almost-sure and positive winning sets
        Win=[]
    return Win

def get_state(state):
    if state%5 == 0:
        env_state = 5
        sys_state = state/5 - 1
    else:
        env_state = state%5
        sys_state = state//5
    return sys_state, env_state


### Main run of the file:
# Runner blocker example
Ns = 5
Ne = 5
V1, V2, Vp = vertices(Ns,Ne)
# Transition system
T1 = [[1], [3], [2,4], [3], [5]] #Environment transitions
T2 = [[1,2,3,4], [1,2,3,5], [1,2,3,4,5], [1,3,4,5], [2,3,4,5]] # SYstem transitions
Tp = []

# Graph transition
GVp, GEdges = trans_sys(V1, V2, Vp, T1, T2, Tp)
collision_indices = [2,3,4]

# Unsafe set
U = unsafe(collision_indices)

# Initial Winning set:
sys_W0 = [] # Winning states from system action states
env_W0 = [] # Winning states from environment action states
for env_state in [2,3,4]:
    for sys_state in [5]:
        w0 = state(sys_state, env_state)
        sys_W0.extend(["v2_"+str(w0)])
        env_W0.extend(["v1_"+str(w0)])
W0 = [env_W0, sys_W0]

N = 5 # Can reach winning set in atmost 5 steps
W = synt_winning_set(GVp, GEdges, U, W0, N)
print(W)

# Retrieve states:
sys_win = []
env_win = []
for ii in range(0,N):
    W_ii = W[ii].copy()
    env_action_states = W_ii[0].copy()
    sys_action_states = W_ii[1].copy()
    sys_win_ii = []
    env_win_ii = []
    for ee in env_action_states:
        s = int(ee[3:])
        [sys_st, env_st] = get_state(s)
        sys_win_ii.append([env_st, sys_st])
    for ss in sys_action_states:
        s = int(ss[3:])
        [sys_st, env_st] = get_state(s)
        env_win_ii.append([env_st, sys_st])
    sys_win.append(sys_win_ii)
    env_win.append(env_win_ii)

print(sys_win[0])
print(sys_win[1])    
print(sys_win[2])
print(sys_win[3])
print(sys_win[4])
print("Environment action winning states")
print(env_win[0])
print(env_win[1])
print(env_win[2])
print(env_win[3])
print(env_win[4])
