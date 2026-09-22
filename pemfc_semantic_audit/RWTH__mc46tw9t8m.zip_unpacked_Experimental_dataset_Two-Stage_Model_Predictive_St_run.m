%% This file executes all necessary functions to plot the results shown in 
%% the paper
op_readme = true;  % Set true if you want to open the readme
pl_cycle1 = true;  % Set true if you want to plot the results for cycle 1
pl_cycle2 = true;  % Set true if you want to plot the results for cycle 2
pl_cycle3 = true;  % Set true if you want to plot the results for cycle 3

%% add the paths: 
addpath('01_ExperimentalData\'); 
addpath('02_Functions\'); 

%% load the measurement data: 
if op_readme
    open 00_readme.txt
end

if pl_cycle1
    load cycle_1_TSOS.mat
    load cycle_1_MPC.mat
    plot_data(cycle_1_MPC, cycle_1_TSOS)
    plot_U(cycle_1_MPC, cycle_1_TSOS)
end

if pl_cycle2
    load cycle_2_TSOS.mat
    load cycle_2_MPC.mat
    plot_data(cycle_2_MPC, cycle_2_TSOS)
end

if pl_cycle3
    load cycle_3_MPC.mat
    plot_data(cycle_3_MPC)
end


