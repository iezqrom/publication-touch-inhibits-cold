# %%
import sys 
sys.path.append("../../")

import numpy as np
import pandas as pd
from scipy import stats
from plotting import (
    cohenD,
)
import os

from globals import data_path

# %%
sdt_results_folder = '/sdt_summaries/'
sdt_results_path = data_path + sdt_results_folder

# get all files in the sdt_results folder
sdt_results_files = os.listdir(sdt_results_path)

# %%
# iterate through all files and extract the data
data = {}
experiments = ['experiment1', 'experiment2', 'experiment3']
for experiment in experiments:
    data[experiment] = pd.read_csv(sdt_results_path + 'df_' + experiment + '.csv')

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

# %% Experiments with sound vs experiments without sound
from scipy.stats import ttest_ind

concatenated_df = pd.concat([data['experiment1'], data['experiment2']], ignore_index=True)

# Isolate dprime values for touch=0 in both concatenated data and Experiment 3
dprime_touch_0_concat = concatenated_df[concatenated_df['touch'] == 0]['dprime']
dprime_touch_0_exp3 = data['experiment3'][data['experiment3']['touch'] == 0]['dprime']

# Perform Welch's t-test for dprime (touch=0) between concatenated data and Experiment 3
welch_ttest_result = ttest_ind(dprime_touch_0_concat, dprime_touch_0_exp3, equal_var=False)

# Calculate means for dprime (touch=0)
mean_dprime_touch_0_concat = dprime_touch_0_concat.mean()
mean_dprime_touch_0_exp3 = dprime_touch_0_exp3.mean()

print(f"Mean dprime (touch=0) for concatenated experiments 1&2: {mean_dprime_touch_0_concat:.2f} ± {dprime_touch_0_concat.std():.2f}")
print(f"Mean dprime (touch=0) for experiment 3: {mean_dprime_touch_0_exp3:.2f} ± {dprime_touch_0_exp3.std():.2f}")

print(f"Welch's t-test result: t={welch_ttest_result.statistic:.2f}, p={welch_ttest_result.pvalue:.2f}")

# %%
# Isolate cresponse values for touch=0 in both concatenated data and Experiment 3
cresponse_touch_0_concat = concatenated_df[concatenated_df['touch'] == 0]['cresponse']
cresponse_touch_0_exp3 = data['experiment3'][data['experiment3']['touch'] == 0]['cresponse']

# Calculate means and SDs for cresponse (touch=0)
mean_cresponse_touch_0_concat = cresponse_touch_0_concat.mean()
mean_cresponse_touch_0_exp3 = cresponse_touch_0_exp3.mean()

print(f"Mean cresponse (touch=0) for concatenated experiments 1&2: {mean_cresponse_touch_0_concat:.2f} ± {cresponse_touch_0_concat.std():.2f}")
print(f"Mean cresponse (touch=0) for experiment 3: {mean_cresponse_touch_0_exp3:.2f} ± {cresponse_touch_0_exp3.std():.2f}")

# Perform Welch's t-test for cresponse (touch=0) between concatenated data and Experiment 3
welch_ttest_cresponse = ttest_ind(cresponse_touch_0_concat, cresponse_touch_0_exp3, equal_var=False)

print(f"Welch's t-test result: t={welch_ttest_cresponse.statistic:.2f}, p={welch_ttest_cresponse.pvalue:.2f}")

# %%
# Isolate dprime and cresponse values for touch=1 in both concatenated data and Experiment 3
dprime_touch_1_concat = concatenated_df[concatenated_df['touch'] == 1]['dprime']
dprime_touch_1_exp3 = data['experiment3'][data['experiment3']['touch'] == 1]['dprime']

cresponse_touch_1_concat = concatenated_df[concatenated_df['touch'] == 1]['cresponse']
cresponse_touch_1_exp3 = data['experiment3'][data['experiment3']['touch'] == 1]['cresponse']

# Calculate means and SDs for dprime and cresponse (touch=1)
mean_dprime_touch_1_concat = dprime_touch_1_concat.mean()
mean_dprime_touch_1_exp3 = dprime_touch_1_exp3.mean()
mean_cresponse_touch_1_concat = cresponse_touch_1_concat.mean()
mean_cresponse_touch_1_exp3 = cresponse_touch_1_exp3.mean()

print(f"Mean dprime (touch=1) for concatenated experiments 1&2: {mean_dprime_touch_1_concat:.2f} ± {dprime_touch_1_concat.std():.2f}")
print(f"Mean dprime (touch=1) for experiment 3: {mean_dprime_touch_1_exp3:.2f} ± {dprime_touch_1_exp3.std():.2f}")
print(f"Mean cresponse (touch=1) for concatenated experiments 1&2: {mean_cresponse_touch_1_concat:.2f} ± {cresponse_touch_1_concat.std():.2f}")
print(f"Mean cresponse (touch=1) for experiment 3: {mean_cresponse_touch_1_exp3:.2f} ± {cresponse_touch_1_exp3.std():.2f}")

# Perform Welch's t-test for dprime (touch=1) between concatenated data and Experiment 3
welch_ttest_dprime_touch_1 = ttest_ind(dprime_touch_1_concat, dprime_touch_1_exp3, equal_var=False)

# Perform Welch's t-test for cresponse (touch=1) between concatenated data and Experiment 3
welch_ttest_cresponse_touch_1 = ttest_ind(cresponse_touch_1_concat, cresponse_touch_1_exp3, equal_var=False)

print(f"Welch's t-test result for dprime (touch=1): t={welch_ttest_dprime_touch_1.statistic:.2f}, p={welch_ttest_dprime_touch_1.pvalue:.2f}")
print(f"Welch's t-test result for cresponse (touch=1): t={welch_ttest_cresponse_touch_1.statistic:.2f}, p={welch_ttest_cresponse_touch_1.pvalue:.2f}")

# %%
import pandas as pd

# Compile all test results into a DataFrame for clarity

# Creating a summary of test results for each condition
test_results = {
    "Comparison": [
        "dprime (touch=0)", 
        "cresponse (touch=0)", 
        "dprime (touch=1)", 
        "cresponse (touch=1)"
    ],
    "t-statistic": [
        welch_ttest_result.statistic, 
        welch_ttest_cresponse.statistic, 
        welch_ttest_dprime_touch_1.statistic, 
        welch_ttest_cresponse_touch_1.statistic
    ],
    "p-value": [
        welch_ttest_result.pvalue, 
        welch_ttest_cresponse.pvalue, 
        welch_ttest_dprime_touch_1.pvalue, 
        welch_ttest_cresponse_touch_1.pvalue
    ]
}

# Convert to DataFrame
results_df = pd.DataFrame(test_results)

# Round to two decimal places
results_df = results_df.round(2)

results_df

# %%
# Variance tests for touch = 0 between concatenated data and Experiment 3
levene_dprime_touch_0 = stats.levene(dprime_touch_0_concat, dprime_touch_0_exp3)
levene_cresponse_touch_0 = stats.levene(cresponse_touch_0_concat, cresponse_touch_0_exp3)

# Variance tests for touch = 1 between concatenated data and Experiment 3
levene_dprime_touch_1 = stats.levene(dprime_touch_1_concat, dprime_touch_1_exp3)
levene_cresponse_touch_1 = stats.levene(cresponse_touch_1_concat, cresponse_touch_1_exp3)

# Compile variance test results into a DataFrame
variance_test_results = {
    "Comparison": [
        "dprime variance (touch=0)", 
        "cresponse variance (touch=0)", 
        "dprime variance (touch=1)", 
        "cresponse variance (touch=1)"
    ],
    "Levene t-statistic": [
        levene_dprime_touch_0.statistic, 
        levene_cresponse_touch_0.statistic, 
        levene_dprime_touch_1.statistic, 
        levene_cresponse_touch_1.statistic
    ],
    "Levene p-value": [
        levene_dprime_touch_0.pvalue, 
        levene_cresponse_touch_0.pvalue, 
        levene_dprime_touch_1.pvalue, 
        levene_cresponse_touch_1.pvalue
    ]
}

# Convert to DataFrame and round to two decimal places
variance_results_df = pd.DataFrame(variance_test_results).round(2)

variance_results_df

# %%
def welch_dof(x,y):
        dof = (x.var()/x.size + y.var()/y.size)**2 / ((x.var()/x.size)**2 / (x.size-1) + (y.var()/y.size)**2 / (y.size-1))
        print(f"Welch-Satterthwaite Degrees of Freedom= {dof:.4f}")
    
welch_dof(dprime_touch_0_concat, dprime_touch_0_exp3)

# %%
# Calculating the difference in means and standard deviations for dprime in "Cold" (touch=0) between the concatenated data (Experiments 1 and 2) and Experiment 3

# Means and standard deviations for Cold (touch=0)
mean_dprime_touch_0_concat = dprime_touch_0_concat.mean()
std_dprime_touch_0_concat = dprime_touch_0_concat.std()

mean_dprime_touch_0_exp3 = dprime_touch_0_exp3.mean()
std_dprime_touch_0_exp3 = dprime_touch_0_exp3.std()

# Calculating the mean difference
mean_difference_touch_0 = mean_dprime_touch_0_exp3 - mean_dprime_touch_0_concat

# Calculating the pooled standard deviation for the difference
std_difference_touch_0 = np.sqrt((std_dprime_touch_0_concat**2 / len(dprime_touch_0_concat)) + 
                                 (std_dprime_touch_0_exp3**2 / len(dprime_touch_0_exp3)))

# Display the calculated values for Cold (touch=0) comparison
{
    "mean_concat": round(mean_dprime_touch_0_concat, 2),
    "std_concat": round(std_dprime_touch_0_concat, 2),
    "mean_exp3": round(mean_dprime_touch_0_exp3, 2),
    "std_exp3": round(std_dprime_touch_0_exp3, 2),
    "mean_difference": round(mean_difference_touch_0, 2),
    "std_difference": round(std_difference_touch_0, 2)
}

# %%
# Calculating the difference in means and standard deviations for dprime in "Cold & touch" (touch=1) between the concatenated data (Experiments 1 and 2) and Experiment 3

# Means and standard deviations
mean_dprime_touch_1_concat = dprime_touch_1_concat.mean()
std_dprime_touch_1_concat = dprime_touch_1_concat.std()

mean_dprime_touch_1_exp3 = dprime_touch_1_exp3.mean()
std_dprime_touch_1_exp3 = dprime_touch_1_exp3.std()

# Calculating the mean difference
mean_difference = mean_dprime_touch_1_exp3 - mean_dprime_touch_1_concat

# Calculating the pooled standard deviation for the difference
# Using the formula for the standard deviation of the difference between two independent means
std_difference = np.sqrt((std_dprime_touch_1_concat**2 / len(dprime_touch_1_concat)) + 
                         (std_dprime_touch_1_exp3**2 / len(dprime_touch_1_exp3)))

# Display the calculated values
{
    "mean_concat": round(mean_dprime_touch_1_concat, 2),
    "std_concat": round(std_dprime_touch_1_concat, 2),
    "mean_exp3": round(mean_dprime_touch_1_exp3, 2),
    "std_exp3": round(std_dprime_touch_1_exp3, 2),
    "mean_difference": round(mean_difference, 2),
    "std_difference": round(std_difference, 2)
}

# %%
# Calculating the difference in means and standard deviations for cresponse in "Cold & touch" (touch=1) between the concatenated data (Experiments 1 and 2) and Experiment 3

# Means and standard deviations for Cold & touch cresponse (touch=1)
mean_cresponse_touch_1_concat = cresponse_touch_1_concat.mean()
std_cresponse_touch_1_concat = cresponse_touch_1_concat.std()

mean_cresponse_touch_1_exp3 = cresponse_touch_1_exp3.mean()
std_cresponse_touch_1_exp3 = cresponse_touch_1_exp3.std()

# Calculating the mean difference for cresponse (Cold & touch)
mean_difference_cresponse_touch_1 = mean_cresponse_touch_1_exp3 - mean_cresponse_touch_1_concat

# Calculating the pooled standard deviation for the difference in cresponse
std_difference_cresponse_touch_1 = np.sqrt((std_cresponse_touch_1_concat**2 / len(cresponse_touch_1_concat)) + 
                                           (std_cresponse_touch_1_exp3**2 / len(cresponse_touch_1_exp3)))

# Display the calculated values for Cold & touch cresponse (touch=1) comparison
{
    "mean_concat": round(mean_cresponse_touch_1_concat, 2),
    "std_concat": round(std_cresponse_touch_1_concat, 2),
    "mean_exp3": round(mean_cresponse_touch_1_exp3, 2),
    "std_exp3": round(std_cresponse_touch_1_exp3, 2),
    "mean_difference": round(mean_difference_cresponse_touch_1, 2),
    "std_difference": round(std_difference_cresponse_touch_1, 2)
}

# %%
# Calculating the difference in means and standard deviations for cresponse in "Cold" (touch=0) between the concatenated data (Experiments 1 and 2) and Experiment 3

# Means and standard deviations for Cold cresponse (touch=0)
mean_cresponse_touch_0_concat = cresponse_touch_0_concat.mean()
std_cresponse_touch_0_concat = cresponse_touch_0_concat.std()

mean_cresponse_touch_0_exp3 = cresponse_touch_0_exp3.mean()
std_cresponse_touch_0_exp3 = cresponse_touch_0_exp3.std()

# Calculating the mean difference for cresponse (Cold)
mean_difference_cresponse_touch_0 = mean_cresponse_touch_0_exp3 - mean_cresponse_touch_0_concat

# Calculating the pooled standard deviation for the difference in cresponse
std_difference_cresponse_touch_0 = np.sqrt((std_cresponse_touch_0_concat**2 / len(cresponse_touch_0_concat)) + 
                                           (std_cresponse_touch_0_exp3**2 / len(cresponse_touch_0_exp3)))

# Display the calculated values for Cold cresponse (touch=0) comparison
{
    "mean_concat": round(mean_cresponse_touch_0_concat, 2),
    "std_concat": round(std_cresponse_touch_0_concat, 2),
    "mean_exp3": round(mean_cresponse_touch_0_exp3, 2),
    "std_exp3": round(std_cresponse_touch_0_exp3, 2),
    "mean_difference": round(mean_difference_cresponse_touch_0, 2),
    "std_difference": round(std_difference_cresponse_touch_0, 2)
}
