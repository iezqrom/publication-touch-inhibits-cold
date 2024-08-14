# %%
import sys 
sys.path.append("../../")

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
from plotting import (
    plotParams,
    removeSpines,
    prettifySpinesTicks,
    params_figure,
    colours,
    cohenD,
)
import os

from globals import data_path, figures_path
import json

plotParams(size = 40)
# %%
data = {'experiment1': {}, 'experiment2': {}, 'experiment3': {}}
name_sdt_file = ['cleaned_data', 'data_replicationsdt_subj', 'data_controlsdt_subj']
# add the name_sdt_file as 'file_name' to data dict
for n_exp, exp in enumerate(data.keys()):
    data[exp]['file_name'] = name_sdt_file[n_exp]

# %%
for n_exp, exp in enumerate(data.keys()):
    exp_folder = f"{data_path}/experiment{n_exp + 1}"
    # get all the folders and only folders in the experiment folder
    folders = [f for f in os.listdir(exp_folder) if os.path.isdir(f"{exp_folder}/{f}")]
    # read the value of the file 'data/to_analyse.txt' in each folder
    to_analyse = []
    for folder in folders:
        with open(f"{exp_folder}/{folder}/data/to_analyse.txt", "r") as f:
            to_analyse.append(f.read())

    # get the names of the folders to analyse basde on the boolean array to_analyse
    to_analyse_folders = list(np.array(folders)[np.array(to_analyse) == 'True'])
    
    # check whether the corresponding file in data[n_exp+1] is in the folders to analyse data/ folders
    data[exp]['to_analyse'] = to_analyse_folders

# %%
# iterate over the folders to analyse and check whether the file {name_sdt_file}.csv exists for each corresponding folder
for n_exp, exp in enumerate(data.keys()):
    for folder in data[exp]['to_analyse']:
        if not os.path.exists(f"{data_path}/experiment{n_exp + 1}/{folder}/data/{data[exp]['file_name']}.csv"):
            print(f"File {data[exp]['file_name']}.csv does not exist for folder {folder} in experiment {exp}")
        else:
            print(f"File {data[exp]['file_name']}.csv exists for folder {folder} in experiment {exp}")
# %%
# extract one random subject from each folder to do some pilot testing
for folder in data[exp]['to_analyse']:
    df = pd.read_csv(f"{data_path}/experiment{n_exp + 1}/{folder}/data/{data[exp]['file_name']}.csv")

# %%
# count the number of rows that are True and False in the 'failed' column
for n_exp, exp in enumerate(data.keys()):
    data[exp]['failed_counts'] = []
    for folder in data[exp]['to_analyse']:
        df = pd.read_csv(f"{data_path}/experiment{n_exp + 1}/{folder}/data/{data[exp]['file_name']}.csv")
        counts = df['failed'].value_counts()
        counts = counts.values
        data[exp]['failed_counts'].append(counts)

# %%
# iterate over experiments and count number of failed trials
# iterate over the list in failed_counts, if the lenght is 1 then it's a value of successful trials and if the length is 2, then the first value is successful trials and the second is failed trials
for n_exp, exp in enumerate(data.keys()):
    data[exp]['failed'] = []
    data[exp]['success'] = []  # Add success key
    for failed in data[exp]['failed_counts']:
        if len(failed) == 1:
            data[exp]['failed'].append(0)
            data[exp]['success'].append(failed[0])  # Add success value
        else:
            data[exp]['failed'].append(failed[1])
            data[exp]['success'].append(failed[0])  # Add success value
# %%
failed_counts = [data[exp]['failed'] for exp in data.keys()]
success_counts = [data[exp]['success'] for exp in data.keys()]
# sum the failed counts
failed_counts = np.sum(failed_counts)
success_counts = np.sum(success_counts)

print('Failed trials', failed_counts)
print('Successful trials', success_counts)
print('Total trials', failed_counts + success_counts)

# print the percentage of failed trials
print('Percentage of failed trials', round(failed_counts / (failed_counts + success_counts) * 100, 1))

# print the average number of failed trials per subject, there are 36 trials in total
print('Average number of failed trials per subject', round(failed_counts / 36, 1))



# %%
