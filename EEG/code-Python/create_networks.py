# -*- coding: utf-8 -*-
"""
@author: Aristidis G. Vrahatis, Georgios N. Dimitrakopoulos, P. Vlamos
"""

import mne
import numpy as np
import matplotlib.pyplot as plt

from mne_connectivity import spectral_connectivity_epochs
from mne.datasets import sample
from mne_connectivity.viz import plot_sensors_connectivity

#%% Load Data
data_path = sample.data_path()
raw_fname = data_path / "MEG/sample/sample_audvis_filt-0-40_raw.fif"
event_fname = data_path / "MEG/sample/sample_audvis_filt-0-40_raw-eve.fif"
raw = mne.io.read_raw_fif(raw_fname)
events = mne.read_events(event_fname)


# Select gradiometers
picks = mne.pick_types(
    raw.info, meg="grad", eeg=False, stim=False, eog=True, exclude="bads"
)

# Create epochs
event_id, tmin, tmax = 3, -0.2, 1.5  # need a long enough epoch for 5 cycles
epochs = mne.Epochs(
    raw,
    events,
    event_id,
    tmin,
    tmax,
    picks=picks,
    baseline=(None, 0),
    reject=dict(grad=4000e-13, eog=150e-6),
)
epochs.load_data().pick_types(meg="grad")  # just keep MEG and no EOG now

fmin, fmax = 4.0, 9.0  # compute connectivity within 8-12 Hz
sfreq = raw.info["sfreq"]  # the sampling frequency
tmin = 0.0  # exclude the baseline period


#%% Compute PLI

con_pli = spectral_connectivity_epochs(
    epochs,
    method="pli",
    mode="multitaper",
    sfreq=sfreq,
    fmin=fmin,
    fmax=fmax,
    faverage=False,
    tmin=tmin,
    mt_adaptive=False,
    n_jobs=1,
)

#In this example, there is strong connectivity between sensors 190-200 and sensors 110-160.

fig, ax = plt.subplots()
img = ax.imshow(con_pli.get_data("dense"), vmin=0, vmax=1)
ax.set_title("PLI")
ax.set_ylabel("Sensor 1")
ax.set_xlabel("Sensor 2")

fig.colorbar(img)
plt.show()



plot_sensors_connectivity(epochs.info, con_pli.get_data(output="dense")[:, :, 0])


conn = spectral_connectivity_epochs(
    epochs,
    method="pli",
    sfreq=sfreq,
    fmin=4,
    fmax=30,
    faverage=False,
    tmin=tmin,
    n_jobs=1,
)

freqs = conn.freqs
d = conn.get_data(output="dense")[2,1,:]

fig, axis = plt.subplots(1, 1)
axis.plot(freqs, d, linewidth=2)
axis.set_xlabel("Frequency (Hz)")
axis.set_ylabel("Connectivity")
fig.suptitle("PLI: [1 -> 2]")