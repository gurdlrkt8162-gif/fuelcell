# Parsed PEMFC candidate facts

Machine-generated reduction of the raw-file audit. Scientific admission still requires manual interpretation.

## RWTH

### `mendeley_raw/RWTH/Experimental_dataset_Two-Stage_Model_Predictive_St.zip`
- bytes: 20680323; sha256: `8dceee1467afb83b9e801f70fa4542855286b90d2dd48e1b4a46db0bd965e67a`; archive: PASS; state: None; error: None
- members: Experimental dataset Two-Stage Model Predictive St/run.m (855), Experimental dataset Two-Stage Model Predictive St/00_readme.txt (24676), Experimental dataset Two-Stage Model Predictive St/02_Functions/plot_U.m (1540), Experimental dataset Two-Stage Model Predictive St/02_Functions/plot_data.m (10689), Experimental dataset Two-Stage Model Predictive St/01_ExperimentalData/cycle_3_MPC.mat (5793043), Experimental dataset Two-Stage Model Predictive St/01_ExperimentalData/cycle_1_MPC.mat (3099517), Experimental dataset Two-Stage Model Predictive St/01_ExperimentalData/cycle_1_TSOS.mat (10018827), Experimental dataset Two-Stage Model Predictive St/01_ExperimentalData/cycle_2_MPC.mat (956655), Experimental dataset Two-Stage Model Predictive St/01_ExperimentalData/cycle_2_TSOS.mat (940885)

### `mendeley_raw/RWTH/Experimental_dataset_Two-Stage_Model_Predictive_St.zip__unpacked/Experimental dataset Two-Stage Model Predictive St/00_readme.txt`
- bytes: 24676; sha256: `76932274a2ff24d70c8f20c15cba22f3deb50cfbf257eda747a7e0fbaea006fb`; archive: None; state: None; error: None
```text
% -------------------------------------------------------------------------
 Experimental Dataset: Two-Stage Model Predictive Stack Control for PEM 
 Fuel Cell Systems
% -------------------------------------------------------------------------

%% INFORMATION:

1. Abstract: 
Proton-exchange membrane fuel cells (PEMFCs) play a pivotal role in 
decarbonizing the transport sector due to their high efficiency and Zero
local emissions. This work proposes an embedded, nonlinear, two-stage model 
predictive control (MPC) that optimally allocates the stack supply from the 
air, hydrogen, and coolant subsystems. A physics-based process model of the 
stack captures the dominant dynamics of membrane hydration, temperature, 
and reactant pressures, representing key internal states that influence 
performance and durability. The two-stage structure separates the optimal 
economic planning from the real-time tracking MPC, (1) ensuring constraint-
compliant regulation of the considered states under highly dynamic 
operation, (2) maintaining efficient stack operation, and (3) resolving the 
over-actuated nature of the multi-input system. Experimental validation on 
a full-scale PEMFC test bench demonstrates efficiency gains of up to 8% and 
reduced reactant consumption compared to a nominal stack control. At the 
same time, membrane temperature and water content remain within prescribed 
limits.

2. Author Information
A. Principal Investigator Contact Information
	Name: Nikolai Weber
	Institutions: Insitute of Automatic Control
            RWTH Aachen University
	Address: Campus-Boulevard 30, 52074 Aachen, Germany
	Email: n.weber@irt.rwth-aachen.de

B. Second Investigator Contact Information
	Name: Daniel Sallach
	Institutions: Chair of Thermodynamics of Mobile Energy Conversion 
                  Systems, RWTH Aachen University
	Address: Forckenbeckstr. 4, 52074 Aachen, Germany
	Email: sallach@tme.rwth-aachen.de

3. Date of data collection: 01/2025

4. Geographic location of data collection: Aachen, Germany

5. Information about funding sources that supported the collection of the 
   data: 
This work was funded by the Federal Ministry of Research, Technology
and Space as part of the Hydrogen Clusters4Future under the grant number
03ZU1115EC. The authors are responsible for the content of this 
publication.

USER INSTRUCTIONS
This folder contains the experimental data used in this publication.

EXPERIMENTAL DATA: 
- the data was recorded with 20 Hz directly from the RCP hardware and test 
  stand operating system
- the data contains the raw signal values, as well as calculated values
- use the run.m file to open and plot the data in MATLAB 
  (works with R2024b)

Definition of variables: 
- t:                  time since measurement start / s
- i_dens_A_cm2:       current density / A/cm^2
- p_out_c_bar:        pressure at the cathode outlet / bar
- p_out_a_bar:        pressure at the anode outlet / bar
- phi_in_c_:          relative humidity at the cathode inlet / -
- dotm_in_c_g_s:      mass flow rate at the cathode inlet / g/s
- T_in_cool_gradC:    coolant inlet temperature / °C
- dotm_in_cool_kg_s:  coolant mass flow rate / kg/s
- phi_in_a_:          relative humidity at the anode inlet / -
- dotm_in_a_g_s:      mass flow rate at the anode inlet / g/s
- p_O2_c_bar:         partial pressure of O2 in cathode gas channel / bar
- p_N2_c_bar:         partial pressure of N2 in cathode gas channel / bar
- p_H2O_c_bar:        partial pressure of H2O in cathode gas channel / bar
- p_H2_a_bar:         partial pressure of H2 in anode gas channel / bar
- p_N2_a_bar:         partial pressure of N2 in anode gas channel / bar
- p_H2O_a_bar:        partial pressure of H2O in anode gas channel / bar
- c_H2O_CCL_mol_m3:   water vapor concentration in the CCL / mol/m^3
- c_H2O_ACL_mol_m3:   water vapor concentration in the ACL / mol/m^3
- lambda_mb_:         membrane water content / -
- T_mb_gradC:         membrane temperature / °C
- T_cool_gradC:       coo
```

### `mendeley_raw/RWTH/Experimental_dataset_Two-Stage_Model_Predictive_St.zip__unpacked/Experimental dataset Two-Stage Model Predictive St/01_ExperimentalData/cycle_1_MPC.mat`
- bytes: 3099517; sha256: `2505b23ec40acd68dd373a46098ceb4cfba984b6abc8bae682fcf0d2afcc09fa`; archive: None; state: None; error: None
- MAT arrays: [{"path": "cycle_1_MPC", "shape": [1], "dtype": "[('_TypeSystem', 'O'), ('_Class', 'O'), ('_ObjectMetadata', 'O')]", "min": null, "max": null, "finite": null, "nonfinite": null}]

### `mendeley_raw/RWTH/Experimental_dataset_Two-Stage_Model_Predictive_St.zip__unpacked/Experimental dataset Two-Stage Model Predictive St/01_ExperimentalData/cycle_1_TSOS.mat`
- bytes: 10018827; sha256: `af1a7d698d915261853f18fbdc79f2ad4cf4d01775cfbb7104060d7f9fd87788`; archive: None; state: None; error: None
- MAT arrays: [{"path": "cycle_1_TSOS", "shape": [1], "dtype": "[('_TypeSystem', 'O'), ('_Class', 'O'), ('_ObjectMetadata', 'O')]", "min": null, "max": null, "finite": null, "nonfinite": null}]

### `mendeley_raw/RWTH/Experimental_dataset_Two-Stage_Model_Predictive_St.zip__unpacked/Experimental dataset Two-Stage Model Predictive St/01_ExperimentalData/cycle_2_MPC.mat`
- bytes: 956655; sha256: `63251f1b050145771fcea69d467731d1baab8e8a83c797e83250a744223b5ae1`; archive: None; state: None; error: None
- MAT arrays: [{"path": "cycle_2_MPC", "shape": [1], "dtype": "[('_TypeSystem', 'O'), ('_Class', 'O'), ('_ObjectMetadata', 'O')]", "min": null, "max": null, "finite": null, "nonfinite": null}]

### `mendeley_raw/RWTH/Experimental_dataset_Two-Stage_Model_Predictive_St.zip__unpacked/Experimental dataset Two-Stage Model Predictive St/01_ExperimentalData/cycle_2_TSOS.mat`
- bytes: 940885; sha256: `540d7780de515fa592e7f06b90a825171ab8801b513ce1453df83519cd04d06e`; archive: None; state: None; error: None
- MAT arrays: [{"path": "cycle_2_TSOS", "shape": [1], "dtype": "[('_TypeSystem', 'O'), ('_Class', 'O'), ('_ObjectMetadata', 'O')]", "min": null, "max": null, "finite": null, "nonfinite": null}]

### `mendeley_raw/RWTH/Experimental_dataset_Two-Stage_Model_Predictive_St.zip__unpacked/Experimental dataset Two-Stage Model Predictive St/01_ExperimentalData/cycle_3_MPC.mat`
- bytes: 5793043; sha256: `9ea6f5fbf9112465650f249c4840435f4ec7d93a67708177cd65c668af507bd8`; archive: None; state: None; error: None
- MAT arrays: [{"path": "cycle_3_MPC", "shape": [1], "dtype": "[('_TypeSystem', 'O'), ('_Class', 'O'), ('_ObjectMetadata', 'O')]", "min": null, "max": null, "finite": null, "nonfinite": null}]

### `mendeley_raw/RWTH/Experimental_dataset_Two-Stage_Model_Predictive_St.zip__unpacked/Experimental dataset Two-Stage Model Predictive St/02_Functions/plot_U.m`
- bytes: 1540; sha256: `614af09562274bd901310dc8dce417c4cba8f9d60729eb82f559caba08c7cf37`; archive: None; state: None; error: None
```text
function plot_U(MPC, TSOS)
% Define color 
rwth_blue_1 = [0,0.329411764705882,0.623529411764706];
rwth_gray_2 = [0.392156862745098,0.396078431372549,0.403921568627451];
% Define setpoints
PstMPCref = [2.4 7 12.3 17.2];
PstDataref = [1.7 7 12.3 17.2];
% Define range +-
deltaPref = [0.05 0.05 0.05 0.05];

PstMPC  = MPC.P_st_kW;
for ii = 1:length(PstMPCref)
    indicesMPC{:,ii} = find(PstMPC >= PstMPCref(ii)-deltaPref(ii) & PstMPC <= PstMPCref(ii)+deltaPref(ii));
    uMeanMPC{ii} = mean(MPC.U_st_V(indicesMPC{:,ii})');
end

PstData = TSOS.P_st_kW(1:1250/0.05);
for ii = 1:length(PstDataref)
    indicesData{:,ii} = find(PstData >= PstDataref(ii)-deltaPref(ii) & PstData <= PstDataref(ii)+deltaPref(ii));
    uMeanData{ii} = mean(TSOS.U_st_V(indicesData{:,ii})');
end

IstDataref = PstDataref./(cell2mat(uMeanData));
IstMPCref  = PstMPCref./(cell2mat(uMeanMPC));

figure()
hold on
plot(IstDataref,cell2mat(uMeanData), 'LineWidth',2.0,'Color',rwth_gray_2,'LineStyle',':','marker','*','MarkerSize',10);
plot(IstMPCref,cell2mat(uMeanMPC), 'LineWidth',2.0,'Color',rwth_blue_1,'LineStyle','--','marker','+','MarkerSize',10);
set(gca,'FontSize',10)
xlabel('$I_\mathrm{st} / \mathrm{A}$','Interpreter','latex')
ylabel('$U_\mathrm{cell} / \mathrm{V}$','Interpreter','latex')
xlim([0, 35])
ylim([0.5, 0.8])
grid on; box on;
ax = gca; ax.TickLabelInterpreter = 'latex';
ax.GridLineStyle = '-';
ax.GridAlpha = 0.45;
hold off
legend('TSOS','MPC','Location','NorthOutside','Orientation','Horizontal')

end



```

### `mendeley_raw/RWTH/Experimental_dataset_Two-Stage_Model_Predictive_St.zip__unpacked/Experimental dataset Two-Stage Model Predictive St/02_Functions/plot_data.m`
- bytes: 10689; sha256: `ea80008d58152cec5bbc17cd8b99c5bdffbd3a0239620513d1b6f234341ef4fb`; archive: None; state: None; error: None
```text
function plot_data(MPC, TSOS)
% Define color 
rwth_blue_1 = [0,0.329411764705882,0.623529411764706];
rwth_gray_2 = [0.392156862745098,0.396078431372549,0.403921568627451];
rwth_red_1  = [0.800000000000000,0.027450980392157,0.117647058823529];
% Set limits and refs
limit_St_O2_            = [2 6];
limit_DeltaT_cool_K     = [-7.5 7.5];
limit_lambda_mb_        = [5 21];
limit_T_mb_gradC        = [60 75];
ref_Deltap_mb_mabr      = 200;
limit_i_dens_A_cm2      = [0.1 1];
limit_p_out_c_bar       = [1.2 2.5];
limit_phi_in_c_         = [0.6 0.9];
limit_dotm_in_c_g_s     = [4 35];
limit_T_in_cool_gradC   = [60 80];
limit_dotm_in_cool_kg_s = [0 2];


%% Control results --------------------------------------------------------
figure('Name','Control results')
subplot(3,6,[1 3]);
% Pst ---------------------------------------------------------------------
hold on
if nargin == 2
    p11 = plot(TSOS.t, TSOS.P_st_kW, 'LineWidth',1.0,'Color',rwth_gray_2,'LineStyle',':');
else
    p11 = plot(MPC.t, MPC.P_st_ref_kW, 'LineWidth',1.0,'Color',rwth_gray_2,'LineStyle',':');
end
p12 = plot(MPC.t, MPC.P_st_kW, 'LineWidth',1.0,'Color',rwth_blue_1,'LineStyle','-');
set(gca,'FontSize',10)
xlabel('$t / \mathrm{s}$','Interpreter','latex')
ylabel('$P_\mathrm{st} / \mathrm{kW}$','Interpreter','latex')
p13 = yline(NaN, 'LineWidth',1.0,'Color',rwth_red_1,'LineStyle','-.');
xlim([MPC.t(1), MPC.t(end)])
ylim([0, 20])
grid on; box on;
ax = gca; ax.TickLabelInterpreter = 'latex';
ax.GridLineStyle = '-';
ax.GridAlpha = 0.45;
ax.YTick = 0:5:20;
hold off
% Legend
if nargin == 2
    legend([p11 p12 p13],{'TSOS','MPC','Bound'}, ...
    'Orientation','horizontal', ...
    'Location','north');
else
    legend([p11 p12 p13],{'Ref','MPC','Bound'}, ...
    'Orientation','horizontal', ...
    'Location','north');
end

% St_O2 -------------------------------------------------------------------
subplot(3,6,[4 6]);
hold on
plot(MPC.t, MPC.t_comp_s*1e3, 'LineWidth',1.0,'Color',rwth_blue_1,'LineStyle','-');
set(gca,'FontSize',10)
xlabel('$t / \mathrm{s}$','Interpreter','latex')
ylabel('$t_\mathrm{ex} / \mathrm{ms}$','Interpreter','latex')
xlim([MPC.t(1), MPC.t(end)])
ylim([6, 7.5])
grid on; box on;
ax = gca; ax.TickLabelInterpreter = 'latex';
ax.GridLineStyle = '-';
ax.GridAlpha = 0.45; 
hold off

% St_O2 -------------------------------------------------------------------
subplot(3,6,[7 8]);
hold on
if nargin == 2
    plot(TSOS.t, TSOS.St_O2_, 'LineWidth',1.0,'Color',rwth_gray_2,'LineStyle',':');
end
plot(MPC.t, MPC.St_O2_, 'LineWidth',1.0,'Color',rwth_blue_1,'LineStyle','-');
yline(limit_St_O2_, 'LineWidth',1.0,'Color',rwth_red_1,'LineStyle','-.');
set(gca,'FontSize',10)
ylabel('$St_\mathrm{O2} / -$','Interpreter','latex')
xlim([MPC.t(1), MPC.t(end)])
ylim([0, 7])
grid on; box on;
ax = gca; ax.TickLabelInterpreter = 'latex';
ax.GridLineStyle = '-';
ax.GridAlpha = 0.45; 
hold off

% dTcool ------------------------------------------------------------------
subplot(3,6,[9 10]);
hold on
if nargin == 2
    plot(TSOS.t, TSOS.DeltaT_cool_K, 'LineWidth',1.0,'Color',rwth_gray_2,'LineStyle',':');
end
plot(MPC.t, MPC.DeltaT_cool_K, 'LineWidth',1.0,'Color',rwth_blue_1,'LineStyle','-');
yline(limit_DeltaT_cool_K, 'LineWidth',1.0,'Color',rwth_red_1,'LineStyle','-.');
set(gca,'FontSize',10)
ylabel('$\Delta T_\mathrm{cool} / \mathrm{K}$','Interpreter','latex')
xlim([MPC.t(1), MPC.t(end)])
ylim([-8.5, 8.5])
grid on; box on;
ax = gca; ax.TickLabelInterpreter = 'latex';
ax.GridLineStyle = '-';
ax.GridAlpha = 0.45; 
hold off

% dp ----------------------------------------------------------------------
subplot(3,6,[11 12]);
hold on
if nargin == 2
    plot(TSOS.t, TSOS.Deltap_mb_mbar, 'LineWidth',1.0,'Color',rwth_gray_2,'LineStyle',':');
end
plot(MPC.t, MPC.Deltap_mb_mbar, 'LineWidth',1.0,'Color',rwth_blue_1,'LineStyle','-');
yline(ref_Deltap_mb_mabr, 'LineWidth',1.0,'Color','black','LineStyle'
```

### `mendeley_raw/RWTH/Experimental_dataset_Two-Stage_Model_Predictive_St.zip__unpacked/Experimental dataset Two-Stage Model Predictive St/run.m`
- bytes: 855; sha256: `01872b780b461061456d24e103eb54ea81adc4f9624b842010dc4786d4f75b04`; archive: None; state: None; error: None
```text
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



```

## OXYGEN_PURGE

### `mendeley_raw/OXYGEN_PURGE/Prediction_of_oxygen_utilization_and_purge_strateg.zip`
- bytes: 177269; sha256: `8d9ef72cabfe8eb7964122767cbb38a323b4fde16dfc61eef274b278608151f4`; archive: PASS; state: None; error: None
- members: Prediction of oxygen utilization and purge strateg/Data_Matlabcode.rar (179674), Prediction of oxygen utilization and purge strateg/Data_Matlabcode.rar__unpacked/Data_Matlabcode/2. Mediumloadlevel/2. Medium load level (experiments).xlsx (17727), Prediction of oxygen utilization and purge strateg/Data_Matlabcode.rar__unpacked/Data_Matlabcode/2. Mediumloadlevel/ANN_mediumload.slxc (5002), Prediction of oxygen utilization and purge strateg/Data_Matlabcode.rar__unpacked/Data_Matlabcode/2. Mediumloadlevel/2. Medium load level (training).xlsx (14944), Prediction of oxygen utilization and purge strateg/Data_Matlabcode.rar__unpacked/Data_Matlabcode/2. Mediumloadlevel/ANN_mediumload.slx (29447), Prediction of oxygen utilization and purge strateg/Data_Matlabcode.rar__unpacked/Data_Matlabcode/2. Mediumloadlevel/TrainNN.m (996), Prediction of oxygen utilization and purge strateg/Data_Matlabcode.rar__unpacked/Data_Matlabcode/2. Mediumloadlevel/Input_Data_104.mat (1199), Prediction of oxygen utilization and purge strateg/Data_Matlabcode.rar__unpacked/Data_Matlabcode/3. Lowloadlevel/ANN_lowload.slxc (4995), Prediction of oxygen utilization and purge strateg/Data_Matlabcode.rar__unpacked/Data_Matlabcode/3. Lowloadlevel/3. Low load level (experiments).xlsx (17316), Prediction of oxygen utilization and purge strateg/Data_Matlabcode.rar__unpacked/Data_Matlabcode/3. Lowloadlevel/TrainNN.m (1035), Prediction of oxygen utilization and purge strateg/Data_Matlabcode.rar__unpacked/Data_Matlabcode/3. Lowloadlevel/3. Low load level (training).xlsx (14630), Prediction of oxygen utilization and purge strateg/Data_Matlabcode.rar__unpacked/Data_Matlabcode/3. Lowloadlevel/ANN_lowload.slx (29664), Prediction of oxygen utilization and purge strateg/Data_Matlabcode.rar__unpacked/Data_Matlabcode/3. Lowloadlevel/Input_Data_104.mat (1246), Prediction of oxygen utilization and purge strateg/Data_Matlabcode.rar__unpacked/Data_Matlabcode/4.Modelevaluation/Model_evaluation.m (1223), Prediction of oxygen utilization and purge strateg/Data_Matlabcode.rar__unpacked/Data_Matlabcode/1.Highloadlevel/ANN_highload.slx (29407), Prediction of oxygen utilization and purge strateg/Data_Matlabcode.rar__unpacked/Data_Matlabcode/1.Highloadlevel/ANN_highload.slxc (4997), Prediction of oxygen utilization and purge strateg/Data_Matlabcode.rar__unpacked/Data_Matlabcode/1.Highloadlevel/1. High load level (training).xlsx (13396), Prediction of oxygen utilization and purge strateg/Data_Matlabcode.rar__unpacked/Data_Matlabcode/1.Highloadlevel/TraiNN.m (649), Prediction of oxygen utilization and purge strateg/Data_Matlabcode.rar__unpacked/Data_Matlabcode/1.Highloadlevel/1. High load level (experiments).xlsx (13460), Prediction of oxygen utilization and purge strateg/Data_Matlabcode.rar__unpacked/Data_Matlabcode/1.Highloadlevel/Input_Data_104.mat (638), Prediction of oxygen utilization and purge strateg/Data_Matlabcode.rar__unpacked/Data_Matlabcode/2. Mediumloadlevel/slprj/sim/varcache/ANN_mediumload/checksumOfCache.mat (392), Prediction of oxygen utilization and purge strateg/Data_Matlabcode.rar__unpacked/Data_Matlabcode/2. Mediumloadlevel/slprj/sim/varcache/ANN_mediumload/varInfo.mat (664), Prediction of oxygen utilization and purge strateg/Data_Matlabcode.rar__unpacked/Data_Matlabcode/2. Mediumloadlevel/slprj/sim/varcache/ANN_mediumload/tmwinternal/simulink_cache.xml (312), Prediction of oxygen utilization and purge strateg/Data_Matlabcode.rar__unpacked/Data_Matlabcode/3. Lowloadlevel/slprj/sim/varcache/ANN_lowload/checksumOfCache.mat (392), Prediction of oxygen utilization and purge strateg/Data_Matlabcode.rar__unpacked/Data_Matlabcode/3. Lowloadlevel/slprj/sim/varcache/ANN_lowload/varInfo.mat (664), Prediction of oxygen utilization and purge strateg/Data_Matlabcode.rar__unpacked/Data_Matlabcode/3. Lowloadlevel/slprj/sim/varcache/ANN_lowload/tmwinternal/simulink_cache.xml (312), Prediction of oxygen utilization and purge strateg/Data_Matlabcode.rar__unpacked/Data_Matlabcode/1.Highloadlevel/slprj/sim/varcache/ANN_highload/checksumOfCache.mat (392), Prediction of oxygen utilization and purge strateg/Data_Matlabcode.rar__unpacked/Data_Matlabcode/1.Highloadlevel/slprj/sim/varcache/ANN_highload/varInfo.mat (664), Prediction of oxygen utilization and purge strateg/Data_Matlabcode.rar__unpacked/Data_Matlabcode/1.Highloadlevel/slprj/sim/varcache/ANN_highload/tmwinternal/simulink_cache.xml (312)

### `mendeley_raw/OXYGEN_PURGE/Prediction_of_oxygen_utilization_and_purge_strateg.zip__unpacked/Prediction of oxygen utilization and purge strateg/Data_Matlabcode.rar`
- bytes: 179674; sha256: `586a76e7240d35d5e1959072436e17a762f724763625bb34e76eeb0f7f1f6d42`; archive: PASS; state: None; error: None
- members: Data_Matlabcode/2. Mediumloadlevel/2. Medium load level (experiments).xlsx (17727), Data_Matlabcode/2. Mediumloadlevel/ANN_mediumload.slxc (5002), Data_Matlabcode/2. Mediumloadlevel/2. Medium load level (training).xlsx (14944), Data_Matlabcode/2. Mediumloadlevel/ANN_mediumload.slx (29447), Data_Matlabcode/2. Mediumloadlevel/TrainNN.m (996), Data_Matlabcode/2. Mediumloadlevel/Input_Data_104.mat (1199), Data_Matlabcode/3. Lowloadlevel/ANN_lowload.slxc (4995), Data_Matlabcode/3. Lowloadlevel/3. Low load level (experiments).xlsx (17316), Data_Matlabcode/3. Lowloadlevel/TrainNN.m (1035), Data_Matlabcode/3. Lowloadlevel/3. Low load level (training).xlsx (14630), Data_Matlabcode/3. Lowloadlevel/ANN_lowload.slx (29664), Data_Matlabcode/3. Lowloadlevel/Input_Data_104.mat (1246), Data_Matlabcode/4.Modelevaluation/Model_evaluation.m (1223), Data_Matlabcode/1.Highloadlevel/ANN_highload.slx (29407), Data_Matlabcode/1.Highloadlevel/ANN_highload.slxc (4997), Data_Matlabcode/1.Highloadlevel/1. High load level (training).xlsx (13396), Data_Matlabcode/1.Highloadlevel/TraiNN.m (649), Data_Matlabcode/1.Highloadlevel/1. High load level (experiments).xlsx (13460), Data_Matlabcode/1.Highloadlevel/Input_Data_104.mat (638), Data_Matlabcode/2. Mediumloadlevel/slprj/sim/varcache/ANN_mediumload/checksumOfCache.mat (392), Data_Matlabcode/2. Mediumloadlevel/slprj/sim/varcache/ANN_mediumload/varInfo.mat (664), Data_Matlabcode/2. Mediumloadlevel/slprj/sim/varcache/ANN_mediumload/tmwinternal/simulink_cache.xml (312), Data_Matlabcode/3. Lowloadlevel/slprj/sim/varcache/ANN_lowload/checksumOfCache.mat (392), Data_Matlabcode/3. Lowloadlevel/slprj/sim/varcache/ANN_lowload/varInfo.mat (664), Data_Matlabcode/3. Lowloadlevel/slprj/sim/varcache/ANN_lowload/tmwinternal/simulink_cache.xml (312), Data_Matlabcode/1.Highloadlevel/slprj/sim/varcache/ANN_highload/checksumOfCache.mat (392), Data_Matlabcode/1.Highloadlevel/slprj/sim/varcache/ANN_highload/varInfo.mat (664), Data_Matlabcode/1.Highloadlevel/slprj/sim/varcache/ANN_highload/tmwinternal/simulink_cache.xml (312)

### `mendeley_raw/OXYGEN_PURGE/Prediction_of_oxygen_utilization_and_purge_strateg.zip__unpacked/Prediction of oxygen utilization and purge strateg/Data_Matlabcode.rar__unpacked/Data_Matlabcode/1.Highloadlevel/1. High load level (experiments).xlsx`
- bytes: 13460; sha256: `ee1d8d699f0ff45e9f9bda2f4475bec623c664f5c0574e27b83a65901a0ce2ba`; archive: None; state: None; error: None
- sheet `Experiments_0.8 Acm^(-2)`: 72×9; headers=['Unnamed: 0', 'Unnamed: 1', 'Unnamed: 2', 'Purge duration \n( s )', 'Purge interval \n( s )', 'Operating Cell Temp \n(oC)', 'Anode Humidity Temp \n( oC)', 'Current \n( A )', 'Oxygen utilization\n( kJ/L ) ']

### `mendeley_raw/OXYGEN_PURGE/Prediction_of_oxygen_utilization_and_purge_strateg.zip__unpacked/Prediction of oxygen utilization and purge strateg/Data_Matlabcode.rar__unpacked/Data_Matlabcode/1.Highloadlevel/1. High load level (training).xlsx`
- bytes: 13396; sha256: `9dcfb3fa65543fd52e0c8992d3bba2f4982a4fe3be066a8699e5319534ed59e8`; archive: None; state: None; error: None
- sheet `Training data_0.8 Acm^(-2)`: 43×9; headers=['Unnamed: 0', 'Unnamed: 1', 'Unnamed: 2', 'Purge duration \n( s )', 'Purge interval \n( s )', 'Operating Cell Temp \n(oC)', 'Anode Humidity Temp \n( oC)', 'Current \n( A )', 'Oxygen utilization\n( kJ/L ) ']

### `mendeley_raw/OXYGEN_PURGE/Prediction_of_oxygen_utilization_and_purge_strateg.zip__unpacked/Prediction of oxygen utilization and purge strateg/Data_Matlabcode.rar__unpacked/Data_Matlabcode/1.Highloadlevel/ANN_highload.slx`
- bytes: 29407; sha256: `9c6052f45e63012b234a27cc51e231e0effb78b10d714bf4fec1ad14423e3b8a`; archive: None; state: binary-unparsed; error: None

### `mendeley_raw/OXYGEN_PURGE/Prediction_of_oxygen_utilization_and_purge_strateg.zip__unpacked/Prediction of oxygen utilization and purge strateg/Data_Matlabcode.rar__unpacked/Data_Matlabcode/1.Highloadlevel/ANN_highload.slxc`
- bytes: 4997; sha256: `a3c94604ed6b753d388509d242c5c221ab6ff0768639a9e98b0473bb5638e90a`; archive: None; state: binary-unparsed; error: None

### `mendeley_raw/OXYGEN_PURGE/Prediction_of_oxygen_utilization_and_purge_strateg.zip__unpacked/Prediction of oxygen utilization and purge strateg/Data_Matlabcode.rar__unpacked/Data_Matlabcode/1.Highloadlevel/Input_Data_104.mat`
- bytes: 638; sha256: `439f5245fa6772c3aa0387c1bd8133a00fd597e0f5183aa3f84316e04975906c`; archive: None; state: None; error: None
- MAT arrays: [{"path": "Input_Data_104", "shape": [43, 6], "dtype": "float64", "min": 0.1, "max": 100.0, "finite": 258, "nonfinite": 0}]

### `mendeley_raw/OXYGEN_PURGE/Prediction_of_oxygen_utilization_and_purge_strateg.zip__unpacked/Prediction of oxygen utilization and purge strateg/Data_Matlabcode.rar__unpacked/Data_Matlabcode/1.Highloadlevel/TraiNN.m`
- bytes: 649; sha256: `fcdc2f79806ab22e2737ff1e99edf19b6336c8b2449ac143c39293615fce0ef0`; archive: None; state: None; error: None
```text
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

```

### `mendeley_raw/OXYGEN_PURGE/Prediction_of_oxygen_utilization_and_purge_strateg.zip__unpacked/Prediction of oxygen utilization and purge strateg/Data_Matlabcode.rar__unpacked/Data_Matlabcode/1.Highloadlevel/slprj/sim/varcache/ANN_highload/checksumOfCache.mat`
- bytes: 392; sha256: `ba9d9b854862ea73deb12bd2e88cd5b70e76eb75c9b38d90b81b97870db67cab`; archive: None; state: None; error: None
- MAT arrays: [{"path": "GlobalWorkspace", "shape": [4], "dtype": "uint32", "min": 1379954502.0, "max": 3593057757.0, "finite": 4, "nonfinite": 0}, {"path": "ConfigSetRef", "shape": [4], "dtype": "uint32", "min": 78774415.0, "max": 3649838548.0, "finite": 4, "nonfinite": 0}, {"path": "ModelWorkspace", "shape": [4], "dtype": "uint32", "min": 78774415.0, "max": 3649838548.0, "finite": 4, "nonfinite": 0}]

### `mendeley_raw/OXYGEN_PURGE/Prediction_of_oxygen_utilization_and_purge_strateg.zip__unpacked/Prediction of oxygen utilization and purge strateg/Data_Matlabcode.rar__unpacked/Data_Matlabcode/1.Highloadlevel/slprj/sim/varcache/ANN_highload/tmwinternal/simulink_cache.xml`
- bytes: 312; sha256: `69138ffa77fd673ba953c9ceb42c0a03f638e1199d5b30633c4a338bd0e5835c`; archive: None; state: binary-unparsed; error: None

### `mendeley_raw/OXYGEN_PURGE/Prediction_of_oxygen_utilization_and_purge_strateg.zip__unpacked/Prediction of oxygen utilization and purge strateg/Data_Matlabcode.rar__unpacked/Data_Matlabcode/1.Highloadlevel/slprj/sim/varcache/ANN_highload/varInfo.mat`
- bytes: 664; sha256: `5b24e37a4e4a304ca4d2a335dcb5d86023c0022a21b8f693902750d3ef09c25f`; archive: None; state: None; error: None
- MAT arrays: [{"path": "GlobalWorkspace", "shape": [5], "dtype": "object", "min": null, "max": null, "finite": null, "nonfinite": null}, {"path": "ConfigSetRef", "shape": [0], "dtype": "object", "min": null, "max": null, "finite": null, "nonfinite": null}, {"path": "ModelWorkspace", "shape": [0], "dtype": "object", "min": null, "max": null, "finite": null, "nonfinite": null}]

### `mendeley_raw/OXYGEN_PURGE/Prediction_of_oxygen_utilization_and_purge_strateg.zip__unpacked/Prediction of oxygen utilization and purge strateg/Data_Matlabcode.rar__unpacked/Data_Matlabcode/2. Mediumloadlevel/2. Medium load level (experiments).xlsx`
- bytes: 17727; sha256: `49c2855af72a4946ec94da47a79f8883f7721889dadd6827d06facc01a38c40a`; archive: None; state: None; error: None
- sheet `Experimental data_0.4 Acm^(-2)`: 185×9; headers=['Unnamed: 0', 'Unnamed: 1', 'Unnamed: 2', 'Purge duration \n( s )', 'Purge interval \n( s )', 'Operating Cell Temp \n(oC)', 'Anode Humidity Temp \n( oC)', 'Current \n( A )', 'Oxygen utilization\n( kJ/L ) ']

### `mendeley_raw/OXYGEN_PURGE/Prediction_of_oxygen_utilization_and_purge_strateg.zip__unpacked/Prediction of oxygen utilization and purge strateg/Data_Matlabcode.rar__unpacked/Data_Matlabcode/2. Mediumloadlevel/2. Medium load level (training).xlsx`
- bytes: 14944; sha256: `845e4742a1cabbefe5da32cea1ba41aa5e61bfd58702a3637cd77dbcd8e630d4`; archive: None; state: None; error: None
- sheet `Training data_0.4 Acm^(-2)`: 110×9; headers=['Unnamed: 0', 'Unnamed: 1', 'Unnamed: 2', 'Purge duration \n( s )', 'Purge interval \n( s )', 'Operating Cell Temp \n(oC)', 'Anode Humidity Temp \n( oC)', 'Current \n( A )', 'Oxygen utilization\n( kJ/L ) ']

### `mendeley_raw/OXYGEN_PURGE/Prediction_of_oxygen_utilization_and_purge_strateg.zip__unpacked/Prediction of oxygen utilization and purge strateg/Data_Matlabcode.rar__unpacked/Data_Matlabcode/2. Mediumloadlevel/ANN_mediumload.slx`
- bytes: 29447; sha256: `858a9723d5b8f2901ea0d672388096e46be999ed72aa31b97a4bc18f3469816b`; archive: None; state: binary-unparsed; error: None

### `mendeley_raw/OXYGEN_PURGE/Prediction_of_oxygen_utilization_and_purge_strateg.zip__unpacked/Prediction of oxygen utilization and purge strateg/Data_Matlabcode.rar__unpacked/Data_Matlabcode/2. Mediumloadlevel/ANN_mediumload.slxc`
- bytes: 5002; sha256: `ec717e9d4b51589a6e829b88af54eb3635b16410a5ca3c4b761aabcb4ff771d9`; archive: None; state: binary-unparsed; error: None

### `mendeley_raw/OXYGEN_PURGE/Prediction_of_oxygen_utilization_and_purge_strateg.zip__unpacked/Prediction of oxygen utilization and purge strateg/Data_Matlabcode.rar__unpacked/Data_Matlabcode/2. Mediumloadlevel/Input_Data_104.mat`
- bytes: 1199; sha256: `97180fe893043248370aa45473ac55173146265a88415c1a08f82996b8b87217`; archive: None; state: None; error: None
- MAT arrays: [{"path": "Input_Data_104", "shape": [110, 6], "dtype": "float64", "min": 0.1, "max": 400.0, "finite": 660, "nonfinite": 0}]

### `mendeley_raw/OXYGEN_PURGE/Prediction_of_oxygen_utilization_and_purge_strateg.zip__unpacked/Prediction of oxygen utilization and purge strateg/Data_Matlabcode.rar__unpacked/Data_Matlabcode/2. Mediumloadlevel/TrainNN.m`
- bytes: 996; sha256: `2a22f5f86d4157b9219e1396ac0d012f16f76176e5f1e8cbb5f1254f2e465e5a`; archive: None; state: None; error: None
```text
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

```

### `mendeley_raw/OXYGEN_PURGE/Prediction_of_oxygen_utilization_and_purge_strateg.zip__unpacked/Prediction of oxygen utilization and purge strateg/Data_Matlabcode.rar__unpacked/Data_Matlabcode/2. Mediumloadlevel/slprj/sim/varcache/ANN_mediumload/checksumOfCache.mat`
- bytes: 392; sha256: `76fe3871f397d1522a9518af72b4464f836770ad7fedef5ae2135d5ade365320`; archive: None; state: None; error: None
- MAT arrays: [{"path": "GlobalWorkspace", "shape": [4], "dtype": "uint32", "min": 1379954502.0, "max": 3593057757.0, "finite": 4, "nonfinite": 0}, {"path": "ConfigSetRef", "shape": [4], "dtype": "uint32", "min": 78774415.0, "max": 3649838548.0, "finite": 4, "nonfinite": 0}, {"path": "ModelWorkspace", "shape": [4], "dtype": "uint32", "min": 78774415.0, "max": 3649838548.0, "finite": 4, "nonfinite": 0}]

### `mendeley_raw/OXYGEN_PURGE/Prediction_of_oxygen_utilization_and_purge_strateg.zip__unpacked/Prediction of oxygen utilization and purge strateg/Data_Matlabcode.rar__unpacked/Data_Matlabcode/2. Mediumloadlevel/slprj/sim/varcache/ANN_mediumload/tmwinternal/simulink_cache.xml`
- bytes: 312; sha256: `d9f584807029b44451caf284d53a65e593b47aa0f3fc20b21712442e72078e2c`; archive: None; state: binary-unparsed; error: None

### `mendeley_raw/OXYGEN_PURGE/Prediction_of_oxygen_utilization_and_purge_strateg.zip__unpacked/Prediction of oxygen utilization and purge strateg/Data_Matlabcode.rar__unpacked/Data_Matlabcode/2. Mediumloadlevel/slprj/sim/varcache/ANN_mediumload/varInfo.mat`
- bytes: 664; sha256: `99383d9f8013f06839cd2b99808a1cdc283af522dcde3fa6861c1e1850fa8418`; archive: None; state: None; error: None
- MAT arrays: [{"path": "GlobalWorkspace", "shape": [5], "dtype": "object", "min": null, "max": null, "finite": null, "nonfinite": null}, {"path": "ConfigSetRef", "shape": [0], "dtype": "object", "min": null, "max": null, "finite": null, "nonfinite": null}, {"path": "ModelWorkspace", "shape": [0], "dtype": "object", "min": null, "max": null, "finite": null, "nonfinite": null}]

### `mendeley_raw/OXYGEN_PURGE/Prediction_of_oxygen_utilization_and_purge_strateg.zip__unpacked/Prediction of oxygen utilization and purge strateg/Data_Matlabcode.rar__unpacked/Data_Matlabcode/3. Lowloadlevel/3. Low load level (experiments).xlsx`
- bytes: 17316; sha256: `b6c0ecc209cd24c5f47cabd822adfc69b96cc0bc12fae859142d3d5f3e764c62`; archive: None; state: None; error: None
- sheet `Experiment data_0.1 Acm^(-2)`: 182×9; headers=['Unnamed: 0', 'Unnamed: 1', 'Unnamed: 2', 'Purge duration \n( s )', 'Purge interval \n( s )', 'Operating Cell Temp \n(oC)', 'Anode Humidity Temp \n( oC)', 'Current \n( A )', 'Oxygen utilization\n( kJ/L ) ']

### `mendeley_raw/OXYGEN_PURGE/Prediction_of_oxygen_utilization_and_purge_strateg.zip__unpacked/Prediction of oxygen utilization and purge strateg/Data_Matlabcode.rar__unpacked/Data_Matlabcode/3. Lowloadlevel/3. Low load level (training).xlsx`
- bytes: 14630; sha256: `31209184067be0ab1ead26dd891adcba6c6d4bc9d9dcdb462b70e36c198c6622`; archive: None; state: None; error: None
- sheet `Training data_0.1 Acm^(-2)`: 109×9; headers=['Unnamed: 0', 'Unnamed: 1', 'Unnamed: 2', 'Purge duration \n( s )', 'Purge interval \n( s )', 'Operating Cell Temp \n(oC)', 'Anode Humidity Temp \n( oC)', 'Current \n( A )', 'Oxygen utilization\n( kJ/L ) ']

### `mendeley_raw/OXYGEN_PURGE/Prediction_of_oxygen_utilization_and_purge_strateg.zip__unpacked/Prediction of oxygen utilization and purge strateg/Data_Matlabcode.rar__unpacked/Data_Matlabcode/3. Lowloadlevel/ANN_lowload.slx`
- bytes: 29664; sha256: `4d68863145a8120e511d37ee36ac9e7b4e74244219a9c9f357b58e08e6e572c8`; archive: None; state: binary-unparsed; error: None

### `mendeley_raw/OXYGEN_PURGE/Prediction_of_oxygen_utilization_and_purge_strateg.zip__unpacked/Prediction of oxygen utilization and purge strateg/Data_Matlabcode.rar__unpacked/Data_Matlabcode/3. Lowloadlevel/ANN_lowload.slxc`
- bytes: 4995; sha256: `19436edd750f196bb9f480925ab5c2ccf4ed60e1aea08077cf2bdebdd77960f1`; archive: None; state: binary-unparsed; error: None

### `mendeley_raw/OXYGEN_PURGE/Prediction_of_oxygen_utilization_and_purge_strateg.zip__unpacked/Prediction of oxygen utilization and purge strateg/Data_Matlabcode.rar__unpacked/Data_Matlabcode/3. Lowloadlevel/Input_Data_104.mat`
- bytes: 1246; sha256: `3a10ac4b73cf995818e812b4c401902bb19115f5785baa3c08d782bab8740e6e`; archive: None; state: None; error: None
- MAT arrays: [{"path": "Input_Data_104", "shape": [109, 6], "dtype": "float64", "min": 0.1, "max": 750.0, "finite": 654, "nonfinite": 0}]

### `mendeley_raw/OXYGEN_PURGE/Prediction_of_oxygen_utilization_and_purge_strateg.zip__unpacked/Prediction of oxygen utilization and purge strateg/Data_Matlabcode.rar__unpacked/Data_Matlabcode/3. Lowloadlevel/TrainNN.m`
- bytes: 1035; sha256: `52654adbb5f43bdf51209e105e9c8180aedd3703c392b09f1e2aa5e51747fa4b`; archive: None; state: None; error: None
```text

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

```

### `mendeley_raw/OXYGEN_PURGE/Prediction_of_oxygen_utilization_and_purge_strateg.zip__unpacked/Prediction of oxygen utilization and purge strateg/Data_Matlabcode.rar__unpacked/Data_Matlabcode/3. Lowloadlevel/slprj/sim/varcache/ANN_lowload/checksumOfCache.mat`
- bytes: 392; sha256: `4d3005437abdabfaf64915d0d83cc1790f16db1615009902d6998b83a28337d6`; archive: None; state: None; error: None
- MAT arrays: [{"path": "GlobalWorkspace", "shape": [4], "dtype": "uint32", "min": 1379954502.0, "max": 3593057757.0, "finite": 4, "nonfinite": 0}, {"path": "ConfigSetRef", "shape": [4], "dtype": "uint32", "min": 78774415.0, "max": 3649838548.0, "finite": 4, "nonfinite": 0}, {"path": "ModelWorkspace", "shape": [4], "dtype": "uint32", "min": 78774415.0, "max": 3649838548.0, "finite": 4, "nonfinite": 0}]

### `mendeley_raw/OXYGEN_PURGE/Prediction_of_oxygen_utilization_and_purge_strateg.zip__unpacked/Prediction of oxygen utilization and purge strateg/Data_Matlabcode.rar__unpacked/Data_Matlabcode/3. Lowloadlevel/slprj/sim/varcache/ANN_lowload/tmwinternal/simulink_cache.xml`
- bytes: 312; sha256: `47e3b088190aabdb27c10e5f8e2053d481e081b4c611624b4a14381745b0f680`; archive: None; state: binary-unparsed; error: None

### `mendeley_raw/OXYGEN_PURGE/Prediction_of_oxygen_utilization_and_purge_strateg.zip__unpacked/Prediction of oxygen utilization and purge strateg/Data_Matlabcode.rar__unpacked/Data_Matlabcode/3. Lowloadlevel/slprj/sim/varcache/ANN_lowload/varInfo.mat`
- bytes: 664; sha256: `146ae7c593a7b673ccf76451f2a358e1ef38f0730142eaaf74f1dcbd22f823a6`; archive: None; state: None; error: None
- MAT arrays: [{"path": "GlobalWorkspace", "shape": [5], "dtype": "object", "min": null, "max": null, "finite": null, "nonfinite": null}, {"path": "ConfigSetRef", "shape": [0], "dtype": "object", "min": null, "max": null, "finite": null, "nonfinite": null}, {"path": "ModelWorkspace", "shape": [0], "dtype": "object", "min": null, "max": null, "finite": null, "nonfinite": null}]

### `mendeley_raw/OXYGEN_PURGE/Prediction_of_oxygen_utilization_and_purge_strateg.zip__unpacked/Prediction of oxygen utilization and purge strateg/Data_Matlabcode.rar__unpacked/Data_Matlabcode/4.Modelevaluation/Model_evaluation.m`
- bytes: 1223; sha256: `78df206ebef178d5f956f14d1c0883afe5115e4a3e4fd0a4e39a5bf3f3e3da7e`; archive: None; state: None; error: None
```text
%Program for evaluating the ANN model
clc
clear all

%At high load level, at purge duration 100 ms
%(Experimental values)
ExperimentalValues = [8.69204
9.04187
9.27368
9.36003
9.40222
9.43755
9.42333
9.39739
9.36341
9.27603
9.2017
9.12072
8.93889];
% Predicted values (ANN)
PredictedValues = [8.693236187
9.060482208
9.266255444
9.370970567
9.417999257
9.432184123
9.424182281
9.395789659
9.347402478
9.285033971
9.211360164
9.105657363
8.948789433];
% Calculate evaluation metrics
MAE = mean(abs(ExperimentalValues - PredictedValues));
RMSE = sqrt(mean((ExperimentalValues - PredictedValues).^2));
SS_total = sum((ExperimentalValues - mean(ExperimentalValues)).^2);
SS_residual = sum((ExperimentalValues - PredictedValues).^2);
R_squared = 1 - SS_residual / SS_total;
% Calculate MAPE
MAPE = mean(abs((ExperimentalValues - PredictedValues) ./ ExperimentalValues)) 

%Parity plot
figure (1)
scatter(ExperimentalValues, PredictedValues);
xlabel('Experimental value / kJ/L');
ylabel('Predicted value / kJ/L');
title('Parity Plot');
grid on

% Print evaluation metrics
fprintf('MAE: %.4f\n', MAE);
fprintf('RMSE: %.4f\n', RMSE);
fprintf('R-squared: %.4f\n', R_squared);


```

## TWO_SYSTEM_FAULT

### `mendeley_raw/TWO_SYSTEM_FAULT/Data_for_A_novel_method_for_polymer_electrolyte_membrane_fuel_cell_fault_diagnosis_using_2D_data.zip`
- bytes: 1620626; sha256: `cf00c5293d8f93e83b26f6a95e7b9e107a8e5b388c5c7f840453eb663d15ac72`; archive: PASS; state: None; error: None
- members: Data for A novel method for polymer electrolyte membrane fuel cell fault diagnosis using 2D data/experimental data.xlsx (1756704)

### `mendeley_raw/TWO_SYSTEM_FAULT/Data_for_A_novel_method_for_polymer_electrolyte_membrane_fuel_cell_fault_diagnosis_using_2D_data.zip__unpacked/Data for A novel method for polymer electrolyte membrane fuel cell fault diagnosis using 2D data/experimental data.xlsx`
- bytes: 1756704; sha256: `e88928c95672243e4691c435529e2d59175f5cb085c57e48455a63d2ca57c224`; archive: None; state: None; error: None
- sheet `Sheet1`: 31002×27; headers=['PEMFC1_Dehydration', 'Unnamed: 1', 'Unnamed: 2', 'PEMFC1_Flooding(1)', 'Unnamed: 4', 'Unnamed: 5', 'PEMFC1_Flooding(2)', 'Unnamed: 7', 'Unnamed: 8', 'PEMFC2_Flooding(1)', 'Unnamed: 10', 'Unnamed: 11', 'PEMFC2_Flooding(2)', 'Unnamed: 13', 'Unnamed: 14', 'PEMFC2_Flooding(3)', 'Unnamed: 16', 'Unnamed: 17', 'PEMFC2_Dehydration(1)', 'Unnamed: 19', 'Unnamed: 20', 'PEMFC2_Dehydration(2)', 'Unnamed: 22', 'Unnamed: 23', 'PEMFC2_Dehydration(3)', 'Unnamed: 25', 'Unnamed: 26']

## SENSOR_FAULT

### `mendeley_raw/SENSOR_FAULT/Data_for_Polymer_Electrolyte_Membrane_Fuel_Cell_Fault_Diagnosis_and_Sensor_Abnormality_Identification_using_Sensor_Selection_Method.zip`
- bytes: 896172; sha256: `f446e5c52422b848ce846d6a1d3e061b3a29a5b8a6886fd184d85abf56cf32af`; archive: PASS; state: None; error: None
- members: Data for Polymer Electrolyte Membrane Fuel Cell Fault Diagnosis and Sensor Abnormality Identification using Sensor Selection Method/full_test_data.csv (5816271)

### `mendeley_raw/SENSOR_FAULT/Data_for_Polymer_Electrolyte_Membrane_Fuel_Cell_Fault_Diagnosis_and_Sensor_Abnormality_Identification_using_Sensor_Selection_Method.zip__unpacked/Data for Polymer Electrolyte Membrane Fuel Cell Fault Diagnosis and Sensor Abnormality Identification using Sensor Selection Method/full_test_data.csv`
- bytes: 5816271; sha256: `bd3ae382ee6c05af6d1cbafa7d437db39a2e50866e4e1abe2f549817c28a7cc6`; archive: None; state: None; error: None
- table: 37899 rows × 24 columns; headers: ['tsec', 'U_totV', 'iA', 'PW', 'm_Air', 'm_H2', 'RH_Air', 'RH_H2', 'P_Air_supply', 'P_H2_supply', 'P_Air_inlet', 'P_H2_inlet', 'T_1', 'T_2', 'T_3', 'T_4', 'T_Air_inlet', 'T_H2_inlet', 'T_Stack_inlet', 'T_Heater', 'm_Air_write', 'm_H2_write', 'Heater_power', 'i_write']
- ranges: [{"tsec": {"min": 1.047, "max": 10828.814, "numeric": 37899}}, {"U_totV": {"min": 0.0, "max": 0.956, "numeric": 37899}}, {"iA": {"min": 0.077, "max": 40.087, "numeric": 37899}}, {"PW": {"min": 0.0, "max": 19.171, "numeric": 37899}}, {"m_Air": {"min": -0.358, "max": 10.877, "numeric": 37899}}, {"m_H2": {"min": -0.004, "max": 1.556, "numeric": 37899}}, {"RH_Air": {"min": 53.054, "max": 105.451, "numeric": 37899}}, {"RH_H2": {"min": 64.239, "max": 106.216, "numeric": 37899}}, {"P_Air_supply": {"min": 0.022, "max": 0.96, "numeric": 37899}}, {"P_H2_supply": {"min": 0.086, "max": 1.699, "numeric": 37899}}, {"P_Air_inlet": {"min": 0.012, "max": 1.467, "numeric": 37899}}, {"P_H2_inlet": {"min": 0.029, "max": 1.767, "numeric": 37899}}, {"T_1": {"min": 13.43, "max": 16.281, "numeric": 37899}}, {"T_2": {"min": -64762.981, "max": -64253.294, "numeric": 37899}}, {"T_3": {"min": 17.775, "max": 36.324, "numeric": 37899}}, {"T_4": {"min": 13.404, "max": 16.443, "numeric": 37899}}, {"T_Air_inlet": {"min": 24.495, "max": 30.958, "numeric": 37899}}, {"T_H2_inlet": {"min": 17.564, "max": 22.873, "numeric": 37899}}, {"T_Stack_inlet": {"min": 18.794, "max": 45.526, "numeric": 37899}}, {"T_Heater": {"min": 55.583, "max": 66.614, "numeric": 37899}}, {"m_Air_write": {"min": 0.024, "max": 1.232, "numeric": 37899}}, {"m_H2_write": {"min": 0.002, "max": 0.546, "numeric": 37899}}, {"Heater_power": {"min": 0.0, "max": 5.0, "numeric": 37899}}, {"i_write": {"min": -1.0, "max": 40.0, "numeric": 37899}}]
```text
tsec,U_totV,iA,PW,m_Air,m_H2,RH_Air,RH_H2,P_Air_supply,P_H2_supply,P_Air_inlet,P_H2_inlet,T_1,T_2,T_3,T_4,T_Air_inlet,T_H2_inlet,T_Stack_inlet,T_Heater,m_Air_write,m_H2_write,Heater_power,i_write
1.047,0.956,0.112,0.107,7.749,1.052,94.016,100.098,0.96,0.556,1.059,0.677,14.691,-64762.981,34.011,14.584,29.724,18.663,42.509,64.992,0.024,0.002,0,0
1.297,0.956,0.112,0.107,7.43,0.917,95.894,99.928,0.897,0.556,0.934,0.639,14.691,-64762.981,34.011,14.584,29.724,18.663,42.509,64.992,0.024,0.002,0,0
1.547,0.955,0.112,0.107,6.664,0.795,97.088,99.758,0.829,0.543,0.84,0.617,14.68,-64762.827,34.021,14.591,29.74,18.628,42.529,64.99,0.024,0.002,0,0
1.797,0.955,0.112,0.107,5.898,0.684,94.357,98.058,0.778,0.537,0.783,0.583,14.68,-64762.827,34.021,14.591,29.74,18.628,42.529,64.99,0.024,0.002,0,0
2.047,0.954,0.112,0.107,5.068,0.574,92.821,96.699,0.731,0.531,0.727,0.566,14.702,-64762.618,34.035,14.593,29.755,18.646,42.523,64.866,0.024,0.002,0,0
2.297,0.954,0.112,0.107,4.302,0.488,94.87,96.359,0.689,0.524,0.695,0.549,14.702,-64762.618,34.035,14.593,29.755,18.646,42.523,64.866,0.024,0.002,0,0
2.547,0.952,0.112,0.107,3.6,0.414,94.699,95.679,0.65,0.518,0.652,0.524,14.683,-64762.451,34.038,14.589,29.764,18.653,42.535,64.784,0.024,0.002,0,0
2.797,0.952,0.112,0.107,3.025,0.365,92.821,94.32,0.621,0.499,0.627,0.515,14.683,-64762.451,34.038,14.589,29.764,18.653,42.535,64.784,0.024,0.002,0,0
3.047,0.951,0.112,0.107,2.451,0.316,94.187,93.47,0.587,0.493,0.589,0.494,14.675,-64762.436,34.027,14.583,29.753,18.651,42.563,64.83,0.024,0.002,0,0
3.297,0.951,0.112,0.107,2.004,0.279,96.406,94.829,0.565,0.493,0.564,0.485,14.675,-64762.436,34.027,14.583,29.753,18.651,42.563,64.83,0.024,0.002,0,0
3.547,0.951,0.112,0.106,1.684,0.242,95.552,94.829,0.536,0.486,0.545,0.468,14.669,-64762.23,34.043,14.567,29.71,18.634,42.551,64.781,0.024,0.002,0,0
3.797,0.948,0.112,0.106,1.365,0.205,93.163,95.339,0.515,0.473,0.514,0.464,14.669,-64762.23,34.043,14.567,29.71,18.634,42.551,64.781,0.024,0.002,0,0
4.047,0.948,0.112,0.106,1.046,0.181,94.87,96.529,0.493,0.473,0.501,0.451,14.642,-64762.102,34.062,14.56,29.679,18.626,42.571,64.737,0.024,0.002,0,0
4.327,0.945,0.112,0.106,0.918,0.156,96.235,98.058,0.481,0.461,0.476,0.438,14.642,-64762.102,34.062,14.56,29.679,18.626,42.571,64.737,0.024,0.002,0,0
4.614,0.945,0.112,0.106,0.727,0.144,94.016,97.718,0.464,0.461,0.457,0.43,14.611,-64761.907,34.068,14.559,29.662,18.622,42.583,64.602,0.024,0.002,0,0
4.901,0.945,0.112,0.106,0.663,0.119,91.968,98.398,0.447,0.448,0.445,0.426,14.611,-64761.907,34.068,14.559,29.662,18.622,42.583,64.602,0.024,0.002,0,0
5.185,0.944,0.112,0.106,0.535,0.131,93.675,99.758,0.425,0.442,0.42,0.413,14.631,-64761.732,34.075,14.536,29.602,18.579,42.598,64.784,0.024,0.002,0,0
5.474,0.944,0.112,0.106,0.472,0.107,92.821,100.438,0.413,0.442,0.413,0.413,14.631,-64761.732,34.075,14.536,29.602,18.579,42.598,64.784,0.024,0.002,0,0
5.757,0.942,0.112,0.106,0.472,0.095,93.333,99.928,0.4,0.435,0.395,0.4,14.615,-64761.619,34.074,14.521,29.563,18.618,42.599,64.904,0.024,0.002,0,0
6.046,0.942,0.112,0.106,0.344,0.107,93.845,100.607,0.383,0.423,0.388,0.392,14.615,-64761.619,34.074,14.521,29.563,18.618,42.599,64.904,0.024,0.002,0,0
6.328,0.942,0.112,0.106,0.28,0.095,95.211,101.287,0.374,0.416,0.369,0.383,14.597,-64761.501,34.073,14.531,29.513,18.566,42.614,65.048,0.024,0.002,0,0
6.614,0.942,0.112,0.106,0.216,0.095,94.699,101.117,0.362,0.416,0.351,0.379,14.597,-64761.501,34.073,14.531,29.513,18.566,42.614,65.048,0.024,0.002,0,0
6.897,0.94,0.112,0.105,0.216,0.082,92.48,100.438,0.353,0.41,0.344,0.37,14.591,-64761.341,34.078,14.514,29.493,18.554,42.628,65.09,0.024,0.002,0,0
7.217,0.94,0.112,0.105,0.216,0.082,93.845,100.947,0.34,0.404,0.338,0.366,14.591,-64761.341,34.078,14.514,29.493,18.554,42.628,65.09,0.024,0.002,0,0
7.468,0.94,0.112,0.105,0.088,0.082,95.552,100.947,0.323,0.397,0.319,0.357,14.64,-64761.213,34.091,14.531,29.438,18.515,42.638,65.059,0.024,0.002,0,0
7.76,0.94,0.112,0.105,0.025,0.095,93.504,100.098,0.319,0.391,
```

## JRC_ZERO_GRADIENT

### `mendeley_raw/JRC_ZERO_GRADIENT/n5csdjfg3c-2.zip`
- bytes: 6318551; sha256: `77ac1d1524f2055a7830a13298208f78901639f36449c3521a23386e06eae821`; archive: PASS; state: None; error: None
- members: ZEROCELL_IV_EIS.xlsx (5662634), S-S_HW_IV_EIS.xlsx (900510)

### `mendeley_raw/JRC_ZERO_GRADIENT/n5csdjfg3c-2.zip__unpacked/S-S_HW_IV_EIS.xlsx`
- bytes: 900510; sha256: `5c255a237cb803e87bf029be261ef4774cf4e346bda0594b29aa798ae585c00e`; archive: None; state: None; error: None
- sheet `data`: 8033×57; headers=['Unnamed: 0', 'Unnamed: 1', 'Unnamed: 2', 'Unnamed: 3', 'Unnamed: 4', 'Unnamed: 5', 'Unnamed: 6', 'Unnamed: 7', 'Unnamed: 8', 'Unnamed: 9', 'Unnamed: 10', 'Unnamed: 11', 'Unnamed: 12', 'Unnamed: 13', 'Unnamed: 14', 'Unnamed: 15', 'Unnamed: 16', 'Unnamed: 17', 'Unnamed: 18', 'Unnamed: 19', 'Unnamed: 20', 'Unnamed: 21', 'Unnamed: 22', 'Unnamed: 23', 'Unnamed: 24', 'Unnamed: 25', 'Unnamed: 26', 'Unnamed: 27', 'Unnamed: 28', 'Unnamed: 29', 'Unnamed: 30', 'Unnamed: 31', 'Unnamed: 32', 'Unnamed: 33', 'Unnamed: 34', 'Unnamed: 35', 'Unnamed: 36', 'Unnamed: 37', 'Unnamed: 38', 'Unnamed: 39', 'Unnamed: 40', 'Unnamed: 41', 'Unnamed: 42', 'Unnamed: 43', 'Unnamed: 44', 'Unnamed: 45', 'Unnamed: 46', 'Unnamed: 47', 'Unnamed: 48', 'Unnamed: 49', 'Unnamed: 50', 'Unnamed: 51', 'Unnamed: 52', 'Unnamed: 53', 'Unnamed: 54', 'Unnamed: 55', 'Unnamed: 56']
- sheet `magnifications`: 606×9; headers=['Unnamed: 0', 'Unnamed: 1', 'Unnamed: 2', 'Unnamed: 3', 'Unnamed: 4', 'Unnamed: 5', 'Unnamed: 6', 'Unnamed: 7', 'Unnamed: 8']
- sheet `EIS_data`: 203×20; headers=['0.5', ' A cm-2', 'Unnamed: 2', 'Unnamed: 3', 'Unnamed: 4', 'Unnamed: 5', 'Unnamed: 6', 'Unnamed: 7', 'Unnamed: 8', 'Unnamed: 9', 'Unnamed: 10', 'Unnamed: 11', '0.5 A cm-2', '25', 'Unnamed: 14', 'Unnamed: 15', 'Unnamed: 16', 'Unnamed: 17', 'K-K', 'K-K.1']

### `mendeley_raw/JRC_ZERO_GRADIENT/n5csdjfg3c-2.zip__unpacked/ZEROCELL_IV_EIS.xlsx`
- bytes: 5662634; sha256: `0836aa748e36d6cf1cfcae032703b064ae1ea77efa9c1277d18892f4cdcaf6a0`; archive: None; state: None; error: None
- sheet `data`: 14227×53; headers=['Unnamed: 0', 'Unnamed: 1', 'Unnamed: 2', 'Unnamed: 3', 'Unnamed: 4', 'Unnamed: 5', 'Unnamed: 6', 'Unnamed: 7', 'Unnamed: 8', 'Unnamed: 9', 'Unnamed: 10', 'Unnamed: 11', 'Unnamed: 12', 'Unnamed: 13', 'Unnamed: 14', 'Unnamed: 15', 'Unnamed: 16', 'Unnamed: 17', 'Unnamed: 18', 'Unnamed: 19', 'Unnamed: 20', 'Unnamed: 21', 'Unnamed: 22', 'Unnamed: 23', 'Unnamed: 24', 'Unnamed: 25', 'Unnamed: 26', 'Unnamed: 27', 'Unnamed: 28', 'Unnamed: 29', 'Unnamed: 30', 'Unnamed: 31', 'Unnamed: 32', 'Unnamed: 33', 'Unnamed: 34', 'Unnamed: 35', 'Unnamed: 36', 'Current density set', 'Current density', 'Voltage', 'IV slope', 'st dev', 'Cathode pressure drop', 'cathode pressure deviation', 'Anode pressure drop', 'anode pressure deviation', '0', 'Average temperature in the anode compartment', 'Temperature variation in the anode compartment', '0.1', 'Average temperature in the cathode compartment', 'Temperature variation in the cathode compartment', '0.2']
- sheet `votage_magnification`: 308×18; headers=['Unnamed: 0', 'Unnamed: 1', 'Unnamed: 2', 'Unnamed: 3', 'Unnamed: 4', 'Unnamed: 5', 'Unnamed: 6', 'Unnamed: 7', 'Unnamed: 8', 'Unnamed: 9', 'Unnamed: 10', 'Unnamed: 11', 'Unnamed: 12', 'Unnamed: 13', 'Unnamed: 14', 'Unnamed: 15', 'Unnamed: 16', 'Unnamed: 17']
- sheet `EIS_data`: 220×21; headers=['0.5', ' A cm-2', 'Unnamed: 2', 'Unnamed: 3', 'Unnamed: 4', 'Unnamed: 5', 'Unnamed: 6', 'Unnamed: 7', 'Unnamed: 8', 'Unnamed: 9', 'Unnamed: 10', 'Unnamed: 11', 'Unnamed: 12', 'Unnamed: 13', 'Unnamed: 14', '0.5 A cm-2', '10', 'Unnamed: 17', '0.5 A cm-2 JRC', 'Unnamed: 19', 'Unnamed: 20']

## NPL_CO_CONTAMINATION

### `mendeley_raw/NPL_CO_CONTAMINATION/sp4pc8w9xh-1.zip`
- bytes: 8366785; sha256: `5e92b77de567a3f1c736b1121405a3a06e78edce8cab5264a0cec339d3ce933f`; archive: PASS; state: None; error: None
- members: 13CO_single_cell_public_data.xlsx (7538166), 13CO_single_cell_public_data.csv (3985998)

### `mendeley_raw/NPL_CO_CONTAMINATION/sp4pc8w9xh-1.zip__unpacked/13CO_single_cell_public_data.csv`
- bytes: 3985998; sha256: `ff2c6797bc23b3b988a4a06419cb3b8a93683b078874b80daa2c449512d4d052`; archive: None; state: None; error: None
- table: 29677 rows × 27 columns; headers: ['Time / s', 'Cell voltage / V', 'Smoothed cell voltage / V', 'Anode inlet / kPag', 'Anode outlet / kPag', 'Cathode inlet / kPag', 'Cathode outlet / kPag', 'Unnamed: 7', 'Time / s.1', 'CO / ppm', 'CO2 / ppm', 'Unnamed: 11', 'Time / s.2', 'CO fit / ppm', 'CO fit low / ppm', 'CO fit high / ppm', 'Unnamed: 16', 'Smoothed time / s', '13CO2 / ppm', '12CO2 / ppm', '13CO2 low / ppm', '13CO2 high / ppm', 'Unnamed: 22', 'Time / s.3', 'Adsorbed CO', 'Adsorbed CO - error minimum', 'Adsorbed CO - error max']
- ranges: [{"Time / s": {"min": 0.0, "max": 29676.0, "numeric": 29677}}, {"Cell voltage / V": {"min": 0.06293, "max": 0.66616, "numeric": 29677}}, {"Smoothed cell voltage / V": {"min": 0.41392, "max": 0.62951, "numeric": 29677}}, {"Anode inlet / kPag": {"min": 3.70719, "max": 10.19476, "numeric": 29677}}, {"Anode outlet / kPag": {"min": 3.95379, "max": 10.76778, "numeric": 29677}}, {"Cathode inlet / kPag": {"min": 3.70458, "max": 100.29743, "numeric": 29677}}, {"Cathode outlet / kPag": {"min": -0.33671, "max": 98.50829, "numeric": 29677}}, {"Unnamed: 7": {"min": null, "max": null, "numeric": 0}}, {"Time / s.1": {"min": 300.0, "max": 28920.0, "numeric": 53}}, {"CO / ppm": {"min": 0.0, "max": 11.67831, "numeric": 53}}, {"CO2 / ppm": {"min": 5.77821, "max": 79.04025, "numeric": 53}}, {"Unnamed: 11": {"min": null, "max": null, "numeric": 0}}, {"Time / s.2": {"min": 1.0, "max": 53.0, "numeric": 53}}, {"CO fit / ppm": {"min": 0.0128, "max": 0.0128, "numeric": 53}}, {"CO fit low / ppm": {"min": 0.01216, "max": 0.01216, "numeric": 53}}, {"CO fit high / ppm": {"min": 0.01344, "max": 0.01344, "numeric": 53}}, {"Unnamed: 16": {"min": null, "max": null, "numeric": 0}}, {"Smoothed time / s": {"min": 1.0, "max": 29409.0, "numeric": 29409}}, {"13CO2 / ppm": {"min": 0.10838, "max": 26.41542, "numeric": 29409}}, {"12CO2 / ppm": {"min": 4.85612, "max": 60.41286, "numeric": 29409}}, {"13CO2 low / ppm": {"min": 0.10296, "max": 25.09465, "numeric": 29409}}, {"13CO2 high / ppm": {"min": 0.11379, "max": 27.73619, "numeric": 29409}}, {"Unnamed: 22": {"min": null, "max": null, "numeric": 0}}, {"Time / s.3": {"min": 1.0, "max": 28379.0, "numeric": 28379}}, {"Adsorbed CO": {"min": -0.0049, "max": 0.65968, "numeric": 28379}}, {"Adsorbed CO - error minimum": {"min": -0.00466, "max": 0.83899, "numeric": 28379}}, {"Adsorbed CO - error max": {"min": -0.00515, "max": 0.59258, "numeric": 28379}}]
```text
Time / s,Cell voltage / V,Smoothed cell voltage / V,Anode inlet / kPag,Anode outlet / kPag,Cathode inlet / kPag,Cathode outlet / kPag,,Time / s,CO / ppm,CO2 / ppm,,Time / s,CO fit / ppm,CO fit low / ppm,CO fit high / ppm,,Smoothed time / s,13CO2 / ppm,12CO2 / ppm,13CO2 low / ppm,13CO2 high / ppm,,Time / s,Adsorbed CO,Adsorbed CO - error minimum,Adsorbed CO - error max
0,0.58834,0.5872,5.13951,5.21564,4.37815,0.16835,,300,0,6.20067,,1,0.0128,0.01216,0.01344,,1,0.18434,6.01633,0.17513,0.19356,,1,-1.79E-06,-1.71E-06,-1.88E-06
1,0.58754,0.5872,5.13951,5.21564,4.37815,0,,840,0,5.99603,,2,0.0128,0.01216,0.01344,,2,0.18388,6.01827,0.17469,0.19308,,2,-3.59E-06,-3.41E-06,-3.76E-06
2,0.58559,0.5872,5.13951,5.38389,4.37815,0.42089,,1440,0,5.77821,,3,0.0128,0.01216,0.01344,,3,0.18344,6.02038,0.17427,0.19261,,3,-5.37E-06,-5.10E-06,-5.64E-06
3,0.58669,0.5872,5.13951,5.46801,4.37815,0,,1980,0,6.17417,,4,0.0128,0.01216,0.01344,,4,0.18302,6.02265,0.17387,0.19217,,4,-7.15E-06,-6.80E-06,-7.51E-06
4,0.5887,0.5872,5.13951,5.21564,4.37815,0,,2520,0,6.66853,,5,0.0128,0.01216,0.01344,,5,0.18261,6.02508,0.17348,0.19174,,5,-8.93E-06,-8.49E-06,-9.38E-06
5,0.58779,0.5872,5.13951,5.21564,4.37815,0,,3060,0,7.14882,,6,0.0128,0.01216,0.01344,,6,0.18222,6.02767,0.17311,0.19133,,6,-1.07E-05,-1.02E-05,-1.12E-05
6,0.58364,0.5872,5.13951,5.38389,4.37815,0.50506,,3600,0,7.5982,,7,0.0128,0.01216,0.01344,,7,0.18185,6.0304,0.17276,0.19094,,7,-1.25E-05,-1.19E-05,-1.31E-05
7,0.58474,0.5872,5.13951,5.46801,4.37815,0.58924,,4140,0.05763,7.27066,,8,0.0128,0.01216,0.01344,,8,0.1815,6.03328,0.17242,0.19057,,8,-1.43E-05,-1.35E-05,-1.50E-05
8,0.58827,0.5872,5.13951,5.38389,4.29395,0.42089,,4740,0.37783,7.59117,,9,0.0128,0.01216,0.01344,,9,0.18116,6.03629,0.1721,0.19022,,9,-1.60E-05,-1.52E-05,-1.68E-05
9,0.58663,0.5872,5.13951,5.21564,4.37815,0.42089,,5280,1.76444,7.92572,,10,0.0128,0.01216,0.01344,,10,0.18085,6.03943,0.1718,0.18989,,10,-1.78E-05,-1.69E-05,-1.87E-05
10,0.58547,0.5872,5.13951,5.38389,4.37815,0.50506,,5820,4.66567,8.25545,,11,0.0128,0.01216,0.01344,,11,0.18055,6.04269,0.17152,0.18957,,11,-1.95E-05,-1.86E-05,-2.05E-05
11,0.58681,0.5872,5.30802,5.38389,4.37815,0.16835,,6360,8.60448,8.54898,,12,0.0128,0.01216,0.01344,,12,0.18027,6.04606,0.17125,0.18928,,12,-2.13E-05,-2.02E-05,-2.24E-05
12,0.5837,0.58721,5.13951,5.21564,4.29395,0.25253,,6900,11.13689,10.59227,,13,0.0128,0.01216,0.01344,,13,0.18,6.04955,0.171,0.189,,13,-2.31E-05,-2.19E-05,-2.42E-05
13,0.58559,0.58721,5.13951,5.21564,4.37815,0.58924,,7440,11.67831,12.83883,,14,0.0128,0.01216,0.01344,,14,0.17976,6.05313,0.17077,0.18875,,14,-2.48E-05,-2.36E-05,-2.60E-05
14,0.58998,0.58721,5.13951,5.38389,4.29395,0.50506,,8040,11.538,14.76975,,15,0.0128,0.01216,0.01344,,15,0.17953,6.05681,0.17055,0.18851,,15,-2.66E-05,-2.52E-05,-2.79E-05
15,0.58895,0.58721,5.13951,5.46801,4.37815,0.42089,,8580,11.27503,15.61133,,16,0.0128,0.01216,0.01344,,16,0.17932,6.06057,0.17035,0.18828,,16,-2.83E-05,-2.69E-05,-2.97E-05
16,0.58559,0.58721,5.13951,5.38389,4.37815,-0.08418,,9120,11.399,15.57178,,17,0.0128,0.01216,0.01344,,17,0.17912,6.06442,0.17017,0.18808,,17,-3.01E-05,-2.86E-05,-3.16E-05
17,0.59023,0.58721,5.13951,5.21564,4.37815,0.16835,,9660,11.18417,15.71542,,18,0.0128,0.01216,0.01344,,18,0.17894,6.06833,0.17,0.18789,,18,-3.18E-05,-3.02E-05,-3.34E-05
18,0.58675,0.58722,5.13951,5.38389,4.29395,-0.08418,,10200,11.12491,15.32229,,19,0.0128,0.01216,0.01344,,19,0.17878,6.07231,0.16984,0.18772,,19,-3.35E-05,-3.19E-05,-3.52E-05
19,0.58937,0.58722,5.13951,5.46801,4.29395,0,,10740,10.52158,35.89246,,20,0.0128,0.01216,0.01344,,20,0.17863,6.07634,0.1697,0.18756,,20,-3.53E-05,-3.35E-05,-3.70E-05
20,0.58669,0.58722,5.13951,5.38389,4.37815,0.16835,,11340,10.57199,24.4801,,21,0.0128,0.01216,0.01344,,21,0.1785,6.08042,0.16957,0.18742,,21,-3.70E-05,-3.52E-05,-3.89E-05
21,0.5887,0.58722,5.13951,5.21564,4.37815,0.25253,,11880,10.66787,25.08853,,22,0.0128,0.01216,0.01344,,22,0.17838,6.08454,0.16946,0.18729,,22,-3.88E-05,-3.68E-05
```

### `mendeley_raw/NPL_CO_CONTAMINATION/sp4pc8w9xh-1.zip__unpacked/13CO_single_cell_public_data.xlsx`
- bytes: 7538166; sha256: `44517bfb7b78e3163bd08680db840e58fc98f9e84acd2a363ed8b090fe8d54ce`; archive: None; state: None; error: None
- sheet `All data`: 29677×27; headers=['Time / s', 'Cell voltage / V', 'Smoothed cell voltage / V', 'Anode inlet / kPag', 'Anode outlet / kPag', 'Cathode inlet / kPag', 'Cathode outlet / kPag', 'Unnamed: 7', 'Time / s.1', 'CO / ppm', 'CO2 / ppm', 'Unnamed: 11', 'Time / s.2', 'CO fit / ppm', 'CO fit low / ppm', 'CO fit high / ppm', 'Unnamed: 16', 'Smoothed time / s', '13CO2 / ppm', '12CO2 / ppm', '13CO2 low / ppm', '13CO2 high / ppm', 'Unnamed: 22', 'Time / s.3', 'Adsorbed CO', 'Adsorbed CO - error minimum', 'Adsorbed CO - error max']
- sheet `FC data`: 29677×7; headers=['Time / s', 'Cell voltage / V', 'Smoothed cell voltage / V', 'Anode inlet / kPag', 'Anode outlet / kPag', 'Cathode inlet / kPag', 'Cathode outlet / kPag']
- sheet `GC-methaniser data`: 28379×8; headers=['Time / s', 'CO / ppm', 'CO2 / ppm', 'Unnamed: 3', 'Time / s.1', 'CO fit / ppm', 'CO fit low / ppm', 'CO fit high / ppm']
- sheet `SIFT data`: 29409×5; headers=['Smoothed time / s', '13CO2 / ppm', '12CO2 / ppm', '13CO2 low / ppm', '13CO2 high / ppm']
- sheet `CO adsorbed`: 29409×4; headers=['Time / s', 'Adsorbed CO', 'Adsorbed CO - error minimum', 'Adsorbed CO - error max']
