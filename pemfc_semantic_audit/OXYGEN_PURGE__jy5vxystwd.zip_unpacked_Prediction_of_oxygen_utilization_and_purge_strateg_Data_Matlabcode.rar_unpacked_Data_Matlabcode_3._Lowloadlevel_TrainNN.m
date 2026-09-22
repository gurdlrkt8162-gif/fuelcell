
%Program for predicting oxygen utilization of OH-PEMFC
clc
clear all
close all

load Input_Data_104 %Training data at purge durations: 0.1, 0.5, and 0.9 s


Train_Input   = Input_Data_104(:,1:5);%Train input
Train_Output  = Input_Data_104(:,6);%Train ouput
X=[0	0.1	10	65	60	12.5
1	0.1	20	65	60	12.5
2	0.1	30	65	60	12.5
3	0.1	40	65	60	12.5
4	0.1	50	65	60	12.5
5	0.1	60	65	60	12.5
6	0.1	70	65	60	12.5
7	0.1	80	65	60	12.5
8	0.1	90	65	60	12.5
9	0.1	100	65	60	12.5
10	0.1	110	65	60	12.5
11	0.1	120	65	60	12.5
12	0.1	130	65	60	12.5
13	0.1	150	65	60	12.5
14	0.1	170	65	60	12.5
15	0.1	190	65	60	12.5
16	0.1	210	65	60	12.5
17	0.1	230	65	60	12.5
18	0.1	250	65	60	12.5
19	0.1	280	65	60	12.5
20	0.1	300	65	60	12.5
21	0.1	330	65	60	12.5
22	0.1	350	65	60	12.5
23	0.1	370	65	60	12.5
24	0.1	390	65	60	12.5
25	0.1	410	65	60	12.5
26	0.1	430	65	60	12.5
27	0.1	450	65	60	12.5
28	0.1	470	65	60	12.5];% Input variable [Time in simulink ANN; Purge duration; Purge interval; Cell temp; Anode humidity temp; Current];
