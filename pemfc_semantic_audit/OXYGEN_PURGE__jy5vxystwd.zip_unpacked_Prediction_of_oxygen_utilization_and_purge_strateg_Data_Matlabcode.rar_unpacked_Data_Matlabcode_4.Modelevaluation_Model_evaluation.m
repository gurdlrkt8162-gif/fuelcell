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

