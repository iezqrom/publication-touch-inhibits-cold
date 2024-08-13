# %%
import sys 
sys.path.append("../../")

import os
import numpy as np
import matplotlib.pyplot as plt

from tharnal import ReAnRaw
from globals import data_path, figures_path, videos_path

from plotting import (
    plotParams,
    removeSpines,
    prettifySpinesTicks,
    params_figure,
    colours,
    framesToseconds
)

plotParams(size = 40)
# %%
data_path
# %%
figures_path
# %%
videos_path
# %%
data = {'experiment1': {}, 'experiment2': {}, 'experiment3': {}}
name_sdt_file = ['cleaned_data', 'data_replicationsdt_subj', 'data_controlsdt_subj']
name_interactor = ['touch', 'interactor', 'interactor']
name_target = ['cold', 'cooling', 'cooling']
name_respomse = ['responses', 'response', 'response']
name_original = ['expt9_stair_sdt', 'expt18_replication', 'expt19_control']

# add the name_sdt_file as 'file_name' to data dict
for n_exp, exp in enumerate(data.keys()):
    data[exp]['file_name'] = name_sdt_file[n_exp]
    data[exp]['interactor'] = name_interactor[n_exp]
    data[exp]['target'] = name_target[n_exp]
    data[exp]['response'] = name_respomse[n_exp]
    data[exp]['original'] = name_original[n_exp]

for n_exp, exp in enumerate(data.keys()):
    exp_folder = f"{data_path}/experiment{n_exp + 1}"
    # get all the folders and only folders in the experiment folder
    folders = [f for f in os.listdir(exp_folder) if os.path.isdir(f"{exp_folder}/{f}")]
    # read the value of the file 'data/to_analyse.txt' in each folder
    to_analyse = []
    for folder in folders:
        with open(f"{exp_folder}/{folder}/data/to_analyse.txt", "r") as f:
            to_analyse.append(f.read())

    
    data[exp]['to_analyse'] = list(np.array(folders)[np.array(to_analyse) == 'True'])

# %%
durations = []
to_plot = []
for n_exp, exp in enumerate(data.keys()):
    print(f"\nExperiment {exp}\n")
    exp_videos_path = f"{videos_path}/{data[exp]['original']}/data"
    for folder in data[exp]['to_analyse']:
        print(f"\nFolder {folder}\n")
        to_analyse_folder = f"{exp_videos_path}/{folder}/videos"
        # list all the files in the folder
        files = os.listdir(to_analyse_folder)
        # select only files with sdt in the name
        sdt_files = [f for f in files if 'sdt' in f]

        for file in sdt_files:
            try: 
                # remove the extension
                file = file.split(".")[0]
                video_data = ReAnRaw(f"{to_analyse_folder}/{file}")
                video_data.datatoDic()
                timestamps = video_data.data['time_now']

                duration = timestamps[-1]
                duration = duration[0]
                durations.append(duration)

                if duration > 6 and duration < 7:
                    to_plot.append(f"{to_analyse_folder}/{file}")
            except:
                print(f"Error in {to_analyse_folder}/{file}")
                continue

# %%
for_figure1 = [
    '/media/iezquer/ivan_lab/phd/expt19_control/data/ex_20230301_1/videos/controlsdt_trial101_pos9_time10_23_45',
    '/media/iezquer/ivan_lab/phd/expt18_replication/data/ex_20230220_1/videos/replicationsdt_trial7_pos5_time13_14_05'
]

fig, ax = plt.subplots(figsize = (15, 15))
for file in for_figure1:
    print(file)
    video_data = ReAnRaw(file)
    video_data.datatoDic()
    try:
        temperature = video_data.data['roi_temperature']
        baseline = temperature[15:20]
        temperature = temperature - np.mean(baseline)
        ax.plot(temperature, color = colours['cold'], lw=params_figure["width_lines"])
    except:
        pass

removeSpines(ax)
prettifySpinesTicks(ax)

framesToseconds(ax, 1, video_data.data['time_now'])

ax.set_xlim(0)

ax.set_xlabel("Time (s)")

ax.set_ylabel("Relative temperature\n change from baseline ($^\circ$C)")

# add a horizontal line at 1.56 dotted
ax.axhline(-1.6, color = 'black', linestyle = '--', lw = params_figure["width_lines"] - 2)

ax.axhline(-1.2, color = 'black', linestyle = '--', lw = params_figure["width_lines"] - 2)

plt.savefig(os.path.join(figures_path, 'example_traces.png'), bbox_inches='tight', dpi=300, transparent=True)
# %%

# %%
