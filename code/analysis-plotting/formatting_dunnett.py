# %%
import sys 
sys.path.append("../")

import numpy as np
import pandas as pd
import os

from globals import data_path, figures_path
import json

# %%
sdt_results_folder = '/sdt_summaries/'
sdt_results_path = data_path + sdt_results_folder

# get all files in the sdt_results folder
sdt_results_files = os.listdir(sdt_results_path)

# %%
data_control = pd.read_csv(sdt_results_path + 'df_control.csv')

# %%
# remove index column and Unnamed columns
data_control = data_control.drop(columns=['Unnamed: 0'])

# %%
#change the column name subj to participant
data_control = data_control.rename(columns={'subj': 'participant'})
# change the column name touch to condition
data_control = data_control.rename(columns={'touch': 'condition'})
# remove column exp
data_control = data_control.drop(columns=['exp'])
# %%
# save the data without index
data_control.to_csv(sdt_results_path + 'df_control_dunnett.csv', index=False)
# %%
