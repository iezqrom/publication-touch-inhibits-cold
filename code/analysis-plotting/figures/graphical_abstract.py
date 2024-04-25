# %%
import sys 
sys.path.append("../../")

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from saving_data import buildDict, appendDataDict
import scipy
from plotting import (
    plotParams,
    removeSpines,
    prettifySpinesTicks,
    doubleSave,
    saveStatsFigure,
    params_figure,
    colours,
    meanSD,
    cohenD,
)
import os
import csv
from globals import data_path, figures_path
import json

plotParams()

# %%
sdt_results_folder = '/sdt_summaries/'
sdt_results_path = data_path + sdt_results_folder

# get all files in the sdt_results folder
sdt_results_files = os.listdir(sdt_results_path)

# %%
# iterate through all files and extract the data
data = {}
for file in sdt_results_files:
    if file.endswith('.csv'):
        name_key = file.split('.')[0]
        data[name_key] = pd.read_csv(sdt_results_path + file)
# %%
# plot the data
fig, ax = plt.subplots(1, 1, figsize=(8, 15))

half_width_mean = 0.1
all_values = {'cold_touch': [], 'cold_notouch': []}

for key in data:
    # key= 'df_control'
    cold_and_no_touch = data[key]['dprime'][data[key]['touch'] == 0]
    cold_and_touch = data[key]['dprime'][data[key]['touch'] == 1]

    # x_values_no_touch = np.repeat(1, len(cold_and_no_touch))
    # x_values_touch = np.repeat(2, len(cold_and_touch))

    # ax.scatter(x_values_no_touch, cold_and_no_touch, color=colours['cold'], s=params_figure["scatter_size"]-100)
    # ax.scatter(x_values_touch, cold_and_touch, color=colours['cold_touch'], s=params_figure["scatter_size"]-100)

    all_values['cold_notouch'].extend(cold_and_no_touch)
    all_values['cold_touch'].extend(cold_and_touch)

ax.plot([1 - half_width_mean, 1 + half_width_mean], [np.mean(all_values['cold_notouch']), np.mean(all_values['cold_notouch'])], color=colours['cold'], lw=params_figure["width_lines"] + 5)
ax.plot([2 - half_width_mean, 2 + half_width_mean], [np.mean(all_values['cold_touch']), np.mean(all_values['cold_touch'])], color=colours['cold_touch'], lw=params_figure["width_lines"] + 5)

# add error bars
ax.errorbar(1, np.mean(all_values['cold_notouch']), yerr=scipy.stats.sem(all_values['cold_notouch']), fmt='o', color=colours['cold'], lw=params_figure["width_lines"] - 2, capsize=10, capthick=7)
ax.errorbar(2, np.mean(all_values['cold_touch']), yerr=scipy.stats.sem(all_values['cold_touch']), fmt='o', color=colours['cold_touch'], lw=params_figure["width_lines"] - 2, capsize=10, capthick=7)

ax.set_ylabel("Sensitivity (d')", labelpad=params_figure["pad_size_label"])

# for cold_notouch, cold_touch in zip(all_values['cold_notouch'], all_values['cold_touch']):
#     ax.plot([1, 2], [cold_notouch, cold_touch], color = 'black', lw = params_figure["width_lines"] - 1, alpha = 0.1, zorder=0)

ax.set_ylim([1.25, 2.25])
ax.set_xlim([0.8, 2.2])

ax.set_xticks([1, 2])
ax.set_yticks([1.25, 1.5, 1.75, 2, 2.25])

ax.set_xticklabels(['Cold only', 'Cold & touch'])

removeSpines(ax)
prettifySpinesTicks(ax)

folder_path = figures_path + 'graphical_abstract/'
# plt.savefig(folder_path + 'all_dprimes_in_sem.png', bbox_inches='tight', dpi=300, transparent=True)

# %%
# get the mean and std of the cold_notouch and cold_touch
print(round(np.mean(all_values['cold_notouch']), 2), round(np.std(all_values['cold_notouch']), 2))
print(round(np.mean(all_values['cold_touch']), 2), round(np.std(all_values['cold_touch']), 2))
# %%
cold_notouch = all_values['cold_notouch']
cold_touch = all_values['cold_touch']

print(np.mean(cold_notouch), np.std(cold_notouch))
print(np.mean(cold_touch), np.std(cold_touch))

# t-test and cohen's d
t_stat, p_val = scipy.stats.ttest_rel(cold_notouch, cold_touch, alternative='greater')
print(round(t_stat, 2), p_val)
print(round(cohenD(cold_notouch, cold_touch), 2))
# %%
data_sdts = {}
# get files that end with .json
for file in sdt_results_files:
    if file.endswith('.json'):
        name_key = file.split('.')[0]
        with open(sdt_results_path + file, 'r') as file:
            data_sdts[name_key] = json.load(file)

# %%
# df_sdts = pd.DataFrame(columns=['experiment','touch', 'hits', 'misses', 'fas', 'crs'])
rows_list = []
for key in data_sdts:
    for subject in data_sdts[key]:
        for key_cond in subject:
            if key_cond != 'sound':
                # create row for the dataframe
                touch = 1 if key_cond == 'touch' else 0
                row = {'experiment': key, 'touch': touch, 'hits': subject[key_cond]['hits'], 'misses': subject[key_cond]['misses'], 'fas': subject[key_cond]['fas'], 'crs': subject[key_cond]['crs']}
                rows_list.append(row)


            # df_sdts = df_sdts.append({'experiment': key, 'touch': touch, 'hits': data_sdts[key][subject][touch]['hits'], 'misses': data_sdts[key][subject][touch]['misses'], 'fas': data_sdts[key][subject][touch]['fas'], 'crs': data_sdts[key][subject][touch]['crs']}, ignore_index=True)
data_sdts_df = pd.DataFrame(rows_list)
# %%
# get rows where touch is 0
cold_notouch = data_sdts_df[data_sdts_df['touch'] == 0]
cold_touch = data_sdts_df[data_sdts_df['touch'] == 1]

# Ignore the experiment column
cold_notouch = cold_notouch[['hits', 'misses', 'fas', 'crs']]
cold_touch = cold_touch[['hits', 'misses', 'fas', 'crs']]

# get the median value for hits, misses, fas and crs
print('Cold only')
print(round(cold_notouch.mean()))
print('\nCold and touch')
print(round(cold_touch.mean()))

# %%
