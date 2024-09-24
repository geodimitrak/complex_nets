% Authors: Aristidis G. Vrahatis, Georgios N. Dimitrakopoulos, P. Vlamos

eeglab; %start gui
%load data and channel locations
EEG = pop_loadset('EEG_data_demo.set');
EEG = pop_chanedit(EEG, 'load',{'chan_locs.ced', 'filetype', 'autodetect'});

%set sampling rate
sampling_rate = 256;
EEG = pop_resample(EEG,sampling_rate);

%filtering
filter_low = 1;
filter_high = 45;
EEG = pop_eegfiltnew(EEG, filter_low, filter_high);

%re-referencing
ref= {'A1', 'A2'}; %re-rereference to mastoid channels
%ref= []; %average reference
EEG = pop_reref(EEG, ref);

%split to epochs based on events
events = {'30'};
timelimits = [-1, 3]; %-1 to 3 sec before/after the event
EEG = pop_epoch(EEG, events, timelimits);

%remove baseline
timerange = [-1000 0]; %in msec
EEG = pop_rmbase( EEG, timerange);

%select some trials
EEG = pop_select(EEG, 'trial', 1:10);

eeglab redraw; %refresh gui

%RUN Independent Component Aanlysis (ICA)
EEG = pop_runica(EEG, 'icatype', 'runica');

%plot top 20 components
pop_topoplot( EEG, 0, 1:20); %0 components, 1 erp

%inspect and select some for rejection.
%subtract components
rej=1:2;
EEG = pop_subcomp(EEG, rej, 0);

%save processed EEG data
pop_saveset( EEG, 'filename', 'clean_EEG.set');