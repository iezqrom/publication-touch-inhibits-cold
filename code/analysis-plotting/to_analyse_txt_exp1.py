# %%
import sys 
sys.path.append("../")

import os

from globals import data_path, figures_path, to_analyse_exp1

#  %%
# we're going to iterate over the folders in the experiment1 folder and we are going to create a to_analyse.txt file with True or False, if the folder is in to_analyse_exp1 then True, else False
exp_folder = f"{data_path}/experiment1"
# get all the folders and only folders in the experiment folder
folders = [f for f in os.listdir(exp_folder) if os.path.isdir(f"{exp_folder}/{f}")]
print(folders)

to_analyse = []
# add test_ to the beginning of values in to_analyse_exp1
to_analyse_exp1 = [f"test_{f}" for f in to_analyse_exp1]
for folder in folders:
    to_analyse.append(folder in to_analyse_exp1)

print(to_analyse)

# %%
# iterate over folders and create a to_analyse.txt file with True or False in each folder but within the test_{date}/data folder
for folder, analyse in zip(folders, to_analyse):
    print(folder, analyse)
    if analyse:
        path = f"{exp_folder}/{folder}/data"
        if not os.path.exists(path):
            os.makedirs(path)
        with open(f"{path}/to_analyse.txt", "w") as f:
            f.write("True")
    else:
        path = f"{exp_folder}/{folder}/data"
        if not os.path.exists(path):
            os.makedirs(path)
        with open(f"{path}/to_analyse.txt", "w") as f:
            f.write("False")
# %%
