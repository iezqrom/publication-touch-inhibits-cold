# %%
import numpy as np
import pandas as pd
import os

from globals import to_analyse

def grabToAnalyse(data_path):
    # list all the folders in the data folder that start with ex_
    subject_folders = [f for f in os.listdir(data_path) if f.startswith('ex_')]
    # sort them
    subject_folders.sort()
    subject_folders_to_analyse = []
    for index, subject_folder in enumerate(subject_folders):
        with open(f"{data_path}/{subject_folder}/data/to_analyse.txt", "r") as f:
            to_analyse = f.read()
        # if it is False, then skip this iteration
        if to_analyse == "True":
            subject_folders_to_analyse.append(subject_folder)

    return subject_folders_to_analyse


def summary_staircase(data, n_staircase):
    which_staircase = [
        i for i, val in enumerate(data["staircase"]) if val == n_staircase
    ]
    which_reversed = [i for i, val in enumerate(data["reversed"]) if val]
    intersection = list(set(which_reversed) & set(which_staircase))
    delta_stimulation_list = [data["delta_stimulation"][i] for i in intersection[3:]]
    delta_mean = np.mean(delta_stimulation_list)
    return delta_mean

base_path = '/home/iezquer/Nextcloud/coding/phd/publication-touch-inhibits-cold/code'
path_data_experiment = f'{base_path}/expt9_stair_sdt/data'

save_data= '/home/iezquer/Nextcloud/coding/phd/publication-touch-inhibits-cold/data/staircase_summaries'

# %% EXPERIMENT
all_deltas = {}
all_deltas["delta_staircases"] = []
all_deltas["delta_mean"] = []
all_deltas['descending'] = []
all_deltas['ascending'] = []

for index, participant in enumerate(to_analyse):

    data = pd.read_csv(f"{path_data_experiment}/test_{participant}/data/data_staircase_subj.csv")
    data = data.to_dict("list")

    ### Change permissions
    # PLOT and Calculate MEAN
    delta_staircases = [summary_staircase(data, 1), summary_staircase(data, 2)]
    all_deltas['descending'].append(delta_staircases[0])
    all_deltas['ascending'].append(delta_staircases[1])
    all_deltas["delta_staircases"].append(delta_staircases)

    delta_mean = -np.mean(delta_staircases)
    all_deltas["delta_mean"].append(delta_mean)

#iterate over all_deltas and ensure values are rounded to 4 decimal places
for key in all_deltas.keys():
    if type(all_deltas[key][0]) == list:
        for i in range(len(all_deltas[key])):
            all_deltas[key][i] = [round(x, 4) for x in all_deltas[key][i]]
    else:
        all_deltas[key] = [round(x, 4) for x in all_deltas[key]]
print(all_deltas)
# %%
# convert to dataframe
df = pd.DataFrame(all_deltas)
df.to_csv(f"{save_data}/df_experiment.csv", index=False)
# %% REPLICATION
path_data_replication = f'{base_path}/expt18_replication/data'

to_analyse = grabToAnalyse(path_data_replication)

all_deltas = []
for index, participant in enumerate(to_analyse):

    # read the number from temp_delta.txt
    data = pd.read_csv(
        path_data_replication + "/" + participant + "/data/temp_delta.txt",
        sep="\t",
        header=None,
    )
    all_deltas.append(-data[0].values)

# %%
# make sure it's a list of numbers and not a list of arrays
all_deltas = [x[0] for x in all_deltas]
# round to 4 decimal places
all_deltas = [round(x, 4) for x in all_deltas]

# %%
# convert to dataframe
df = pd.DataFrame(all_deltas, columns=["delta_mean"])
df.to_csv(f"{save_data}/df_replication.csv", index=False)

# %% CONTROL
path_data_control = f'{base_path}/expt19_control/data'

to_analyse = grabToAnalyse(path_data_control)

all_deltas = []
for index, participant in enumerate(to_analyse):

    # read the number from temp_delta.txt
    data = pd.read_csv(
        path_data_control + "/" + participant + "/data/temp_delta.txt",
        sep="\t",
        header=None,
    )
    all_deltas.append(-data[0].values)

# %%
# make sure it's a list of numbers and not a list of arrays
all_deltas = [x[0] for x in all_deltas]
# round to 4 decimal places
all_deltas = [round(x, 4) for x in all_deltas]

# %%
# convert to dataframe
df = pd.DataFrame(all_deltas, columns=["delta_mean"])
df.to_csv(f"{save_data}/df_control.csv", index=False)
# %%
