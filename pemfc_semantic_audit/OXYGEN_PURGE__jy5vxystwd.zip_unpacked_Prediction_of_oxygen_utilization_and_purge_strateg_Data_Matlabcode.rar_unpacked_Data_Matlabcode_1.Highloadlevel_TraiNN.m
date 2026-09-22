%Program for predicting oxygen utilization of OH-PEMFC
clc
clear all
close all

load Input_Data_104 %Training data at purge durations: 0.1, 0.5, and 0.9 s


Train_Input   = Input_Data_104(:,1:5);%Train input
Train_Output  = Input_Data_104(:,6);%Train output
X=[0	0.1	10	65	60	100
1	0.1	15	65	60	100
2	0.1	20	65	60	100
3	0.1	25	65	60	100
4	0.1	30	65	60	100
5	0.1	35	65	60	100
6	0.1	40	65	60	100
7	0.1	45	65	60	100
8	0.1	50	65	60	100
9	0.1	55	65	60	100
10	0.1	60	65	60	100
11	0.1	65	65	60	100
12	0.1	70	65	60	100];% Input variable [Time in simulink ANN; Purge duration; Purge interval; Cell temp; Anode humidity temp; Current];
