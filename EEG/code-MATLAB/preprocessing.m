% Authors: Aristidis G. Vrahatis, Georgios N. Dimitrakopoulos, P. Vlamos

%start gui
eeglab; 

%load data
EEG = pop_loadset('EEG_data_demo.set');

%add chanlel location information from file
EEG = pop_chanedit(EEG, 'load',{'chan_locs.ced', 'filetype', 'autodetect'});

%resample
sampling_rate = 256;
EEG = pop_resample(EEG,sampling_rate);

%filtering
filter_low = 1;
filter_high = 45;
EEG = pop_eegfiltnew(EEG, filter_low, filter_high);

%re-referencing
ref= {'A1', 'A2'}; %using specific channels
%ref= [];  %for average reference
EEG = pop_reref(EEG, ref);

%dividing into epochs based on events (-1 sec to 3 sec after event '30')
events = {'30'};
timelimits = [-1, 3]; %time in s
EEG = pop_epoch(EEG, events, timelimits);

%remove baseline, -1000 ms to 0 ms relative to event
timerange = [-1000 0]; %time in msec
EEG = pop_rmbase( EEG, timerange);

%select data, here tials 1-10 
EEG = pop_select(EEG, 'trial', 1:10);

%refresh gui
eeglab redraw; 

%run ICA for artifact removal
EEG = pop_runica(EEG, 'icatype', 'runica');

%plot top 20 ICA components
pop_topoplot(EEG, 0, 1:20);

%inspect previous figure and select some components for rejection (here 1-2):
rej=1:2;

%remove ICA components
EEG = pop_subcomp(EEG, rej, 0);

%save data
pop_saveset( EEG, 'filename', 'clean_EEG.set');
