% Authors: Aristidis G. Vrahatis, Georgios N. Dimitrakopoulos, P. Vlamos

%SIFT preprocessing
EEG = pop_pre_prepData(EEG, 'nogui', 'SignalType',{'Channels'}, ...
        'NormalizeData', {'Method' {'time'  'ensemble'} }, 'verb', 1);

%model order
EEG = pop_est_fitMVAR( EEG, 'nogui', 'Algorithm', 'Vieira-Morf', 'ModelOrder', 5, 'WindowLength', 0.5, 'WindowStepSize', 0.03, 'verb', 1); 

%create PDC networks
EEG = pop_est_mvarConnectivity( EEG, 'nogui', 'ConnectivityMeasures', {'PDC' }, 'Frequencies', [1:50
], 'VerbosityLevel', 1);

EEG = pop_est_mvarConnectivity( EEG, 'nogui', 'ConnectivityMeasures', ...
             {'dDTF08' 'Coh' 'pCoh' 'S'}, 'Frequencies', [2:50], 'VerbosityLevel', 1);
