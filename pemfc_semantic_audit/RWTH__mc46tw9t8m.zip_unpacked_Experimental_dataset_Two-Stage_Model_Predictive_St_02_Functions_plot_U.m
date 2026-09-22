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


