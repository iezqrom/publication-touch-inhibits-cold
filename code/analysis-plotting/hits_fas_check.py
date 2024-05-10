# %%
import sys 
sys.path.append("../")

from sdt_analysis import SDTloglinear, tableTosdtDoble
import numpy as np
import pandas as pd
import csv
import os

from plotting import (
    plotParams,
)

from globals import data_path, figures_path

plotParams(size = 40)

# %%
data = {'experiment1': {}, 'experiment2': {}, 'experiment3': {}}
name_sdt_file = ['cleaned_data', 'data_replicationsdt_subj', 'data_controlsdt_subj']
name_interactor = ['touch', 'interactor', 'interactor']
name_target = ['cold', 'cooling', 'cooling']
name_respomse = ['responses', 'response', 'response']
# add the name_sdt_file as 'file_name' to data dict
for n_exp, exp in enumerate(data.keys()):
    data[exp]['file_name'] = name_sdt_file[n_exp]
    data[exp]['interactor'] = name_interactor[n_exp]
    data[exp]['target'] = name_target[n_exp]
    data[exp]['response'] = name_respomse[n_exp]

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
counter = 0
counter_fas = 0
for n_exp, exp in enumerate(data.keys()):
    data[exp]['failed_counts'] = []
    for folder in data[exp]['to_analyse']:
        table_data = pd.read_csv(f"{data_path}/experiment{n_exp + 1}/{folder}/data/{data[exp]['file_name']}.csv")
# for nsub, folder_name in enumerate(to_analyse):
        
        ### SUBJECT
        success_rows = table_data[table_data["failed"] == False]

        # print(folder)

        # print(success_rows)
        present_yesnt, present_nont, absent_yesnt, absent_nont = tableTosdtDoble(success_rows, 0, name_response = data[exp]['response'], name_stimulus = data[exp]['target'], name_interactor = data[exp]['interactor'])
        present_yest, present_not, absent_yest, absent_not = tableTosdtDoble(success_rows, 1, name_response = data[exp]['response'], name_stimulus = data[exp]['target'], name_interactor = data[exp]['interactor'])

        present_notouch = [
            len(present_yesnt.loc[:, data[exp]['response']]),
            len(present_nont.loc[:, data[exp]['response']]),
        ]
        absent_notouch = [
            len(absent_yesnt.loc[:, data[exp]['response']]),
            len(absent_nont.loc[:, data[exp]['response']]),
        ]

        present_touch = [
            len(present_yest.loc[:, data[exp]['response']]),
            len(present_not.loc[:, data[exp]['response']]),
        ]
        absent_touch = [
            len(absent_yest.loc[:, data[exp]['response']]),
            len(absent_not.loc[:, data[exp]['response']]),
        ]

        correc_present_notouch = (present_notouch[0] / sum(present_notouch)) * 100
        correc_absent_notouch = (absent_notouch[1] / sum(absent_notouch)) * 100

        correc_present_touch = (present_touch[0] / sum(present_touch)) * 100
        correc_absent_touch = (absent_touch[1] / sum(absent_touch)) * 100

        all_in = [
            correc_present_notouch,
            correc_absent_notouch,
            correc_present_touch,
            correc_absent_touch,
        ]
        ab_in = [
            np.mean([correc_present_notouch, correc_absent_notouch]),
            np.mean([correc_present_touch, correc_absent_touch]),
        ]

        all_in = np.asarray(all_in)
        ab_in = np.asarray(ab_in)

        to_rand = ["notouch", "touch"]

        sdts = {}
        tables_sdt = {}
        for cond in to_rand:
            tables_sdt[cond] = {'hits': [], 'misses': [], 'fas': [], 'crs': []}

        sdts["notouch"] = SDTloglinear(
            present_notouch[0], present_notouch[1], absent_notouch[0], absent_notouch[1]
        )
        
        sdts["touch"] = SDTloglinear(
            present_touch[0], present_touch[1], absent_touch[0], absent_touch[1]
        )

        counter += 1
        total = present_notouch[0] + present_notouch[1]
        
        if present_notouch[0] == 0 or present_touch[0] == 0 or absent_notouch[0] == 0 or absent_touch[0] == 0:
            print("One or more values are 0.")
            print(f"hit notouch: {present_notouch[0]}")
            print(f"hit touch: {present_touch[0]}")
            print(f"fa notouch: {absent_notouch[0]}")
            print(f"fa touch: {absent_touch[0]}")
            counter_fas += 1
        elif present_notouch[0] == total or present_touch[0] == total or absent_notouch[0] == total or absent_touch[0] == total:
            print("One or more values are 1.")
            # print the value that is 1
        else:
            continue

# %%
counter
# %%
counter_fas
# %%
