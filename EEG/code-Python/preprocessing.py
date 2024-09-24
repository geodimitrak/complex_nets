# -*- coding: utf-8 -*-
"""
@author: Aristidis G. Vrahatis, Georgios N. Dimitrakopoulos, P. Vlamos
"""

import numpy as np
import mne


#%% Load Data
# The first time this function is called, the data are downloaded. 
sample_data_folder = mne.datasets.sample.data_path() 
sample_data_raw_file = (
    sample_data_folder / "MEG" / "sample" / "sample_audvis_filt-0-40_raw.fif")
raw = mne.io.read_raw_fif(sample_data_raw_file)

sample_data_folder = mne.datasets.sample.data_path() 
sample_data_raw_file = (
    sample_data_folder / "MEG" / "sample" / "sample_audvis_raw.fif")
raw = mne.io.read_raw_fif(sample_data_raw_file)

print(raw.info)

raw.load_data() #load all data (initially, only metadata are loaded)

#save data
data = raw.get_data()
np.save(file="my_data.npy", arr=data)


#%% Channel manipulation
eeg_and_eog = raw.copy().pick(picks=["eeg", "eog"])

print(len(raw.ch_names), "→", len(eeg_and_eog.ch_names))

#select/remove channels
raw_temp = raw.copy()
print("Number of channels in raw_temp:")
print(len(raw_temp.ch_names), end=" → drop two → ")
raw_temp.drop_channels(["EEG 037", "EEG 059"])
print(len(raw_temp.ch_names), end=" → pick three → ")
raw_temp.pick(["MEG 1811", "EEG 017", "EOG 061"])
print(len(raw_temp.ch_names))


channel_names = ["EOG 061", "EEG 003", "EEG 002", "EEG 001"]
eog_and_frontal_eeg = raw.copy().reorder_channels(channel_names)
print(eog_and_frontal_eeg.ch_names)

raw.rename_channels({"EOG 061": "blink detector"})


raw_selection = raw.copy().crop(tmin=10, tmax=12.5)
print(raw_selection)

print(raw_selection.times.min(), raw_selection.times.max())
raw_selection.crop(tmin=1)
print(raw_selection.times.min(), raw_selection.times.max())


#%% Reject Data
print(raw.info["bads"])

good_eeg = mne.pick_types(raw.info, meg=False, eeg=True, exclude='bads')

fig = raw.plot()
fig.fake_keypress("a")  # Simulates user pressing 'a' on the keyboard.

raw.copy().pick(picks=["mag"]).plot(duration=60, proj=False, n_channels=len(raw.ch_names), remove_dc=False)


#%% Filtering
cutoff = 0.2 #Hz
raw_highpass = raw.copy().pick(picks=["mag"]).load_data().filter(l_freq = cutoff, h_freq=None)
with mne.viz.use_browser_backend("matplotlib"):
    fig = raw_highpass.plot( duration=60, proj=False, n_channels=len(raw.ch_names), remove_dc=False)
    fig.subplots_adjust(top=0.9)
    fig.suptitle("High-pass filtered at {} Hz".format(cutoff), size="xx-large", weight="bold")

fig = raw.compute_psd(fmax=250).plot(average=True, picks="data", exclude="bads")

#plot spectrum
meg_picks = mne.pick_types(raw.info, meg=True)
freqs = (60, 120, 180, 240)
raw_notch = raw.copy().load_data().notch_filter(freqs=freqs, picks=meg_picks)
for title, data in zip(["Un", "Notch "], [raw, raw_notch]):
    fig = data.compute_psd(fmax=250).plot(average=True, picks="data", exclude="bads")
    fig.suptitle("{}filtered".format(title), size="xx-large", weight="bold")


#%% Resampling
raw_downsampled = raw.copy().resample(sfreq=200)


#%% Re-referencing
# use average of mastoid channels as reference
#raw.set_eeg_reference(ref_channels=['M1', 'M2']) #note: sample data do NOT have these channels

# use the average of all channels as reference
raw_avg_ref = raw.copy().set_eeg_reference(ref_channels="average")
raw_avg_ref.plot()


#%% Artifact removal with Independent Component Analysis (ICA)

# pick some channels that clearly show heartbeats and blinks
regexp = r"(MEG [12][45][123]1|EEG 00.)"
artifact_picks = mne.pick_channels_regexp(raw.ch_names, regexp=regexp)
raw.plot(order=artifact_picks, n_channels=len(artifact_picks), show_scrollbars=False)

filt_raw = raw.copy().filter(l_freq=1.0, h_freq=40)

# set up and fit the ICA
ica = mne.preprocessing.ICA(n_components=20, random_state=97, max_iter=800)

ica.fit(filt_raw)

#print results
explained_var_ratio = ica.get_explained_variance_ratio(filt_raw)
for channel_type, ratio in explained_var_ratio.items():
    print(f"Fraction of {channel_type} variance explained by all components: " f"{ratio}")

explained_var_ratio = ica.get_explained_variance_ratio(filt_raw, components=[0], ch_type="eeg")

# This time, print as percentage.
ratio_percent = round(100 * explained_var_ratio["eeg"])
print(f"Fraction of variance in EEG signal explained by first component: " f"{ratio_percent}%")

#plot results
raw.load_data()
ica.plot_sources(raw, show_scrollbars=False)

ica.plot_components()

# blinks
ica.plot_overlay(raw, exclude=[0], picks="eeg")
# heartbeats
ica.plot_overlay(raw, exclude=[1], picks="mag")

ica.plot_properties(raw, picks=[0, 1])

ica.exclude = [0, 1]  # indices chosen based on previous plots

# ica.apply() changes the Raw object in-place, so we make a copy:
reconst_raw = raw.copy()
ica.apply(reconst_raw)

raw.plot(order=artifact_picks, n_channels=len(artifact_picks), show_scrollbars=False)
reconst_raw.plot(order=artifact_picks, n_channels=len(artifact_picks), show_scrollbars=False)
del reconst_raw #not needed anymore


#%% Epochs
# Split data to epochs (based on events)
events = mne.find_events(raw, stim_channel="STI 014")

epochs = mne.Epochs(raw, events, tmin=-0.3, tmax=0.7)

print(epochs)
print(epochs.event_id)

event_dict = {
    "auditory/left": 1,
    "auditory/right": 2,
    "visual/left": 3,
    "visual/right": 4,
    "face": 5,
    "buttonpress": 32,
}
epochs = mne.Epochs(raw, events, tmin=-0.3, tmax=0.7, event_id=event_dict, preload=True)
print(epochs.event_id)


print(epochs.drop_log[-4:])

epochs.plot(n_epochs=10, events=True)

print(epochs["face"])

print(epochs[:10])  # epochs 0-9
print(epochs[2:9:2])  # epochs 2, 4, 6, 8

# first 3 "buttonpress" epochs:
print(epochs["buttonpress"][:3])  
print(epochs["buttonpress"][[0, 1, 2]])  

epochs_eeg = epochs.copy().pick(picks="eeg")
print(epochs_eeg.ch_names)

new_order = ["EEG 002", "STI 014", "EOG 061", "MEG 2521"]
epochs_subset = epochs.copy().reorder_channels(new_order)
print(epochs_subset.ch_names)

shorter_epochs = epochs.copy().crop(tmin=-0.1, tmax=0.1, include_tmax=True)

data_dict = dict(Original=epochs, Cropped= shorter_epochs)
for name, obj in data_dict.items():
    print("{} epochs has {} time samples".format(name, obj.get_data(copy=False).shape[-1]))


epochs.save("saved-audiovisual-epo.fif", overwrite=True)
epochs_from_file = mne.read_epochs("saved-audiovisual-epo.fif", preload=False)

epochs = mne.make_fixed_length_epochs(raw, duration=30, preload=False)


#%% Time-frequency analysis
#raw = mne.io.read_raw_fif(sample_data_raw_file)
raw.compute_psd(method="multitaper", tmin=10, tmax=20, fmin=5, fmax=30, picks="eeg")


with mne.use_log_level("WARNING"):  
# hide some irrelevant info messages
    events = mne.find_events(raw, stim_channel="STI 014")
    event_dict = {
        "auditory/left": 1,
        "auditory/right": 2,
        "visual/left": 3,
        "visual/right": 4,
    }
    epochs = mne.Epochs(raw, events, tmin=-0.3, tmax=0.7, event_id=event_dict, preload=True)

    epo_spectrum = epochs.compute_psd()
    psds, freqs = epo_spectrum.get_data(return_freqs=True)
    print(f"\nPSDs shape: {psds.shape}, freqs shape: {freqs.shape}")
    
    evoked = epochs["auditory"].average()
    evk_spectrum = evoked.compute_psd()

evk_spectrum.plot(picks="data", exclude="bads")

evk_spectrum.plot_topo(color="k", fig_facecolor="w", axis_facecolor="w")

evk_spectrum.plot_topomap(ch_type="eeg", agg_fun=np.median)


mean_spectrum = epo_spectrum.average()
psds, freqs = mean_spectrum.get_data(return_freqs=True)
# then convert to dB and take mean & standard deviation across channels
psds = 10 * np.log10(psds)
psds_mean = psds.mean(axis=0)
psds_std = psds.std(axis=0) / np.sqrt(len(psds))

import matplotlib.pyplot as plt
_, ax = plt.subplots()
ax.plot(freqs, psds_mean, color="k")
ax.fill_between(
    freqs,
    psds_mean - psds_std,
    psds_mean + psds_std,
    color="k",
    alpha=0.5,
    edgecolor="none",
)
ax.set(
    title="PSD",
    xlabel="Frequency (Hz)",
    ylabel="Power Spectral Density (dB)",
)