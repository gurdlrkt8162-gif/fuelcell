%Program for predicting oxygen utilization of OH-PEMFC
clc
clear all
close all

load Input_Data_104 %Training data at purge durations: 0.1, 0.5, and 0.9 s


Train_Input   = Input_Data_104(:,1:5);%Train input
Train_Output  = Input_Data_104(:,6);%Train ouput
X=[0	0.1	10	65	60	50
1	0.1	20	65	60	50
2	0.1	30	65	60	50
3	0.1	40	65	60	50
4	0.1	50	65	60	50
5	0.1	60	65	60	50
6	0.1	70	65	60	50
7	0.1	80	65	60	50
8	0.1	90	65	60	50
9	0.1	100	65	60	50
10	0.1	110	65	60	50
11	0.1	120	65	60	50
12	0.1	130	65	60	50
13	0.1	140	65	60	50
14	0.1	150	65	60	50
15	0.1	160	65	60	50
16	0.1	170	65	60	50
17	0.1	180	65	60	50
18	0.1	190	65	60	50
19	0.1	200	65	60	50
20	0.1	210	65	60	50
21	0.1	220	65	60	50
22	0.1	230	65	60	50
23	0.1	240	65	60	50
24	0.1	250	65	60	50
25	0.1	260	65	60	50
26	0.1	270	65	60	50
27	0.1	280	65	60	50
28	0.1	290	65	60	50
29	0.1	300	65	60	50];% Input variable [Time in simulink ANN; Purge duration; Purge interval; Cell temp; Anode humidity temp; Current];
