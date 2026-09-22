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
yline(ref_Deltap_mb_mabr, 'LineWidth',1.0,'Color','black','LineStyle','-.');
set(gca,'FontSize',10)
ylabel('$\Delta p / \mathrm{mbar}$','Interpreter','latex')
xlim([MPC.t(1), MPC.t(end)])
ylim([0, 400])
grid on; box on;
ax = gca; ax.TickLabelInterpreter = 'latex';
ax.GridLineStyle = '-';
ax.GridAlpha = 0.45; 
hold off

% Eff ---------------------------------------------------------------------
subplot(3,6,[13 14]);
hold on 
if nargin == 2
    plot(TSOS.t, TSOS.eta_st_, 'LineWidth',1.0,'Color',rwth_gray_2,'LineStyle',':');
end
plot(MPC.t, MPC.eta_st_, 'LineWidth',1.0,'Color',rwth_blue_1,'LineStyle','-');
set(gca,'FontSize',10)
xlabel('$t / \mathrm{s}$','Interpreter','latex')
ylabel('$\eta_\mathrm{st} / -$','Interpreter','latex')
xlim([MPC.t(1), MPC.t(end)])
ylim([0.35, 0.7])
grid on; box on;
ax = gca; ax.TickLabelInterpreter = 'latex';
ax.GridLineStyle = '-';
ax.GridAlpha = 0.45; 
hold off

% lambda ------------------------------------------------------------------
subplot(3,6,[15 16]);
hold on
if nargin == 2
    plot(TSOS.t, TSOS.lambda_mb_, 'LineWidth',1.0,'Color',rwth_gray_2,'LineStyle',':');
end
plot(MPC.t, MPC.lambda_mb_, 'LineWidth',1.0,'Color',rwth_blue_1,'LineStyle','-');
yline(limit_lambda_mb_, 'LineWidth',1.0,'Color',rwth_red_1,'LineStyle','-.');
set(gca,'FontSize',10)
xlabel('$t / \mathrm{s}$','Interpreter','latex')
ylabel('$\lambda_\mathrm{mb} / -$','Interpreter','latex')
xlim([MPC.t(1), MPC.t(end)])
ylim([4, 22])
grid on; box on;
ax = gca; ax.TickLabelInterpreter = 'latex';
ax.GridLineStyle = '-';
ax.GridAlpha = 0.45; 
hold off

% Tmb ------------------------------------------------------------------
subplot(3,6,[17 18]);
hold on
if nargin == 2
    plot(TSOS.t, TSOS.T_mb_gradC, 'LineWidth',1.0,'Color',rwth_gray_2,'LineStyle',':');
end
plot(MPC.t, MPC.T_mb_gradC, 'LineWidth',1.0,'Color',rwth_blue_1,'LineStyle','-');
yline(limit_T_mb_gradC, 'LineWidth',1.0,'Color',rwth_red_1,'LineStyle','-.');
set(gca,'FontSize',10)
xlabel('$t / \mathrm{s}$','Interpreter','latex')
ylabel('$T_\mathrm{mb} / ^\circ \mathrm{C}$','Interpreter','latex')
xlim([MPC.t(1), MPC.t(end)])
ylim([57.5, 85])
grid on; box on;
ax = gca; ax.TickLabelInterpreter = 'latex';
ax.GridLineStyle = '-';
ax.GridAlpha = 0.45; 
hold off



%% Ins --------------------------------------------------------------------
figure('Name','Control variables')
subplot(2,3,1);
% i_dens ------------------------------------------------------------------
hold on
if nargin == 2
    plot(TSOS.t, TSOS.i_dens_A_cm2, 'LineWidth',1.0,'Color',rwth_gray_2,'LineStyle',':');
end
plot(MPC.t, MPC.i_dens_A_cm2, 'LineWidth',1.0,'Color',rwth_blue_1,'LineStyle','-');
yline(limit_i_dens_A_cm2, 'LineWidth',1.0,'Color',rwth_red_1,'LineStyle','-.');
set(gca,'FontSize',10)
ylabel('$i_\mathrm{dens} / \mathrm{A}\cdot\mathrm{cm}^\mathrm{-2}$','Interpreter','latex')
xlim([MPC.t(1), MPC.t(end)])
ylim([0, 1.2])
grid on; box on;
ax = gca; ax.TickLabelInterpreter = 'latex';
ax.GridLineStyle = '-';
ax.GridAlpha = 0.45; 
hold off

% p_rm_c ------------------------------------------------------------------
subplot(2,3,2);
hold on
if nargin == 2
    plot(TSOS.t, TSOS.p_out_c_bar, 'LineWidth',1.0,'Color',rwth_gray_2,'LineStyle',':');
end
plot(MPC.t, MPC.p_out_c_bar, 'LineWidth',1.0,'Color',rwth_blue_1,'LineStyle','-');
yline(limit_p_out_c_bar, 'LineWidth',1.0,'Color',rwth_red_1,'LineStyle','-.');
set(gca,'FontSize',10)
ylabel('$p_\mathrm{out}^\mathrm{c} / \mathrm{bar}$','Interpreter','latex')
xlim([MPC.t(1), MPC.t(end)])
ylim([0, 3])
grid on; box on;
ax = gca; ax.TickLabelInterpreter = 'latex';
ax.GridLineStyle = '-';
ax.GridAlpha = 0.45; 
hold off
if nargin == 2
    legend('TSOS','MPC','Bound','Location','North','Orientation','Horizontal')
else
    legend('MPC','Bound','Location','North','Orientation','Horizontal')
end

% Mass flow c -------------------------------------------------------------
subplot(2,3,3);
hold on
if nargin == 2
    plot(TSOS.t, TSOS.dotm_in_c_g_s, 'LineWidth',1.0,'Color',rwth_gray_2,'LineStyle',':');
end
plot(MPC.t, MPC.dotm_in_c_g_s, 'LineWidth',1.0,'Color',rwth_blue_1,'LineStyle','-');
yline(limit_dotm_in_c_g_s, 'LineWidth',1.0,'Color',rwth_red_1,'LineStyle','-.');
set(gca,'FontSize',10)
ylabel('$\dot{m}_\mathrm{in}^\mathrm{c} / \mathrm{g}\cdot\mathrm{s}^\mathrm{-1}$', 'Interpreter','latex')
xlim([MPC.t(1), MPC.t(end)])
ylim([0, 40])
grid on; box on;
ax = gca; ax.TickLabelInterpreter = 'latex';
ax.GridLineStyle = '-';
ax.GridAlpha = 0.45; 
hold off

% RH c --------------------------------------------------------------------
subplot(2,3,4);
hold on
if nargin == 2
    plot(TSOS.t, TSOS.phi_in_c_, 'LineWidth',1.0,'Color',rwth_gray_2,'LineStyle',':');
end
plot(MPC.t, MPC.phi_in_c_, 'LineWidth',1.0,'Color',rwth_blue_1,'LineStyle','-');
yline(limit_phi_in_c_, 'LineWidth',1.0,'Color',rwth_red_1,'LineStyle','-.');
set(gca,'FontSize',10)
xlabel('$t / \mathrm{s}$','Interpreter','latex')
ylabel('$\phi_\mathrm{in}^\mathrm{c} / -$','Interpreter','latex')
xlim([MPC.t(1), MPC.t(end)])
ylim([0, 1])
grid on; box on;
ax = gca; ax.TickLabelInterpreter = 'latex';
ax.GridLineStyle = '-';
ax.GridAlpha = 0.45; 
hold off

% Tcool -------------------------------------------------------------------
subplot(2,3,5);
hold on
if nargin == 2
    plot(TSOS.t, TSOS.T_in_cool_gradC, 'LineWidth',1.0,'Color',rwth_gray_2,'LineStyle',':');
end
plot(MPC.t, MPC.T_in_cool_gradC, 'LineWidth',1.0,'Color',rwth_blue_1,'LineStyle','-');
yline(limit_T_in_cool_gradC, 'LineWidth',1.0,'Color',rwth_red_1,'LineStyle','-.');
set(gca,'FontSize',10)
xlabel('$t / \mathrm{s}$','Interpreter','latex')
ylabel('$T_\mathrm{in}^\mathrm{cool} / ^\circ \mathrm{C} $','Interpreter','latex')
xlim([MPC.t(1), MPC.t(end)])
ylim([57.5, 82.5])
grid on; box on;
ax = gca; ax.TickLabelInterpreter = 'latex';
ax.GridLineStyle = '-';
ax.GridAlpha = 0.45; 
hold off

% dot_m_cool --------------------------------------------------------------
subplot(2,3,6);
hold on
if nargin == 2
    plot(TSOS.t, TSOS.dotm_in_cool_kg_s, 'LineWidth',1.0,'Color',rwth_gray_2,'LineStyle',':');
end
plot(MPC.t, MPC.dotm_in_cool_kg_s, 'LineWidth',1.0,'Color',rwth_blue_1,'LineStyle','-');
yline(limit_dotm_in_cool_kg_s, 'LineWidth',1.0,'Color',rwth_red_1,'LineStyle','-.');
set(gca,'FontSize',10)
xlabel('$t / \mathrm{s}$','Interpreter','latex')
ylabel('$\dot{m}_\mathrm{in}^\mathrm{cool} / \mathrm{g}\cdot\mathrm{s}^\mathrm{-1}$', 'Interpreter','latex')
xlim([MPC.t(1), MPC.t(end)])
ylim([0, 2.1])
grid on; box on;
ax = gca; ax.TickLabelInterpreter = 'latex';
ax.GridLineStyle = '-';
ax.GridAlpha = 0.45; 
hold off

end