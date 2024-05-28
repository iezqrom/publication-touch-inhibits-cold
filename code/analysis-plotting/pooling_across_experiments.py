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

all_d_primes = {'cold_touch': [], 'cold_notouch': []}
all_response_biases = {'cold_touch': [], 'cold_notouch': []}

for key in data:
    cold_and_no_touch = data[key]['dprime'][data[key]['touch'] == 0]
    cold_and_touch = data[key]['dprime'][data[key]['touch'] == 1]
    all_d_primes['cold_notouch'].extend(cold_and_no_touch)
    all_d_primes['cold_touch'].extend(cold_and_touch)

    cold_and_no_touch = data[key]['cresponse'][data[key]['touch'] == 0]
    cold_and_touch = data[key]['cresponse'][data[key]['touch'] == 1]
    all_response_biases['cold_notouch'].extend(cold_and_no_touch)
    all_response_biases['cold_touch'].extend(cold_and_touch)

# %% DELTAS
cold_notouch = all_d_primes['cold_notouch']
cold_touch = all_d_primes['cold_touch']
diff_deltas = np.array(cold_notouch) - np.array(cold_touch)

print('d-prime mean std sem cold', np.mean(cold_notouch), np.std(cold_notouch), stats.sem(cold_notouch))
print('d-prime mean std sem cold & touch', np.mean(cold_touch), np.std(cold_touch), stats.sem(cold_touch))
print('d-prime mean std sem diff', np.mean(diff_deltas), np.std(diff_deltas), stats.sem(diff_deltas))

# t-test and cohen's d
t_stat, p_val = stats.ttest_rel(cold_notouch, cold_touch, alternative='greater')
print('t stat p-value', t_stat, p_val)
print('cohen D', cohenD(cold_notouch, cold_touch))

# %% resopnse bias
response_bias_notouch = all_response_biases['cold_notouch']
response_bias_touch = all_response_biases['cold_touch']
diff_response_bias =  np.array(response_bias_notouch) - np.array(response_bias_touch)

print('response bias mean std sem cold', np.mean(response_bias_notouch), np.std(response_bias_notouch), stats.sem(response_bias_notouch))
print('response bias mean std sem cold & touch', np.mean(response_bias_touch), np.std(response_bias_touch), stats.sem(response_bias_touch))
print('response bias mean std sem diff', np.mean(diff_response_bias), np.std(diff_response_bias), stats.sem(diff_response_bias))

# t-test and cohen's d
t_stat, p_val = stats.ttest_rel(response_bias_notouch, response_bias_touch, alternative='greater')
print('t stat p-value', t_stat, p_val)
print('cohen D', cohenD(response_bias_notouch, response_bias_touch))

# %%