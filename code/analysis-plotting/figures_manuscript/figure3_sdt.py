# %%
import sys 
sys.path.append("../../")

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy
from plotting import (
    plotParams,
    removeSpines,
    prettifySpinesTicks,
    params_figure,
    colours,
    )
import os

from globals import data_path, figures_path

plotParams(size=40)
# params_figure['alpha'] = 0.2

# %%
sdt_results_folder = '/sdt_summaries/'
sdt_results_path = data_path + sdt_results_folder

figure_folder_name = 'figure3_sdts'

# get all files in the sdt_results folder
sdt_results_files = os.listdir(sdt_results_path)

# %%
# iterate through all files and extract the data
data = {}
for file in sdt_results_files:
    if file.endswith('.csv'):
        name_key = file.split('.')[0]
        data[name_key] = pd.read_csv(sdt_results_path + file)

# %% EXPERIMENT 1
experiment_name = 'df_experiment1'
data_experiment = data[experiment_name]
params_figure['alpha'] = 0.5
mean_notouch = data_experiment['dprime'][data_experiment['touch'] == 0].mean()
mean_touch = data_experiment['dprime'][data_experiment['touch'] == 1].mean()

fig, ax = plt.subplots(figsize=(10, 10))

offset = 0.1
ax.plot([0 - offset, 0 + offset], [mean_notouch, mean_notouch], lw=params_figure['width_lines'] + 5, color=colours['cold'])
ax.plot(
    [0.5 - offset, 0.5 + offset],
    [mean_touch, mean_touch],
    lw=params_figure['width_lines'] + 5,
    color=colours['cold_touch'],
)

ax.plot([0, 0.5], [mean_notouch, mean_touch], lw=params_figure['width_lines'], color="black", zorder=0)

subj_values_notouch = data_experiment['dprime'][data_experiment['touch'] == 0]
subj_values_touch = data_experiment['dprime'][data_experiment['touch'] == 1]
ax.plot(
    [0, 0.5],
    [subj_values_notouch, subj_values_touch],
    color="grey",
    lw=params_figure['width_lines'] - params_figure['adjust_parti_line'],
    alpha=params_figure['alpha'],
    zorder=0,
)

ax.scatter(
    np.repeat(0, len(subj_values_notouch)),
    subj_values_notouch,
    s=params_figure['scatter_size'],
    color=colours['cold'],
)
ax.scatter(
    np.repeat(0.5, len(subj_values_touch)),
    subj_values_touch,
    s=params_figure['scatter_size'],
    color=colours['cold_touch'],
)

removeSpines(ax)
prettifySpinesTicks(ax)

ax.set_ylabel("Sensitivity (d')", labelpad=params_figure['pad_size_label'])

ax.set_ylim([0, 3.5])
ax.set_xlim([-0.2, 0.7])

ax.set_xticks([])
ax.set_yticks([0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5])

plt.tight_layout()
name = "d_prime"
plt.tight_layout()
plt.savefig(f'{figures_path}/{figure_folder_name}/{experiment_name}_{name}.png', dpi=300, transparent=True)

# %%
mean_notouch = data_experiment['cresponse'][data_experiment['touch'] == 0].mean()
mean_touch = data_experiment['cresponse'][data_experiment['touch'] == 1].mean()

fig, ax = plt.subplots(figsize=(10, 10))

offset = 0.1
ax.plot([0 - offset, 0 + offset], [mean_notouch, mean_notouch], lw=params_figure['width_lines'] + 5, color=colours['cold'])
ax.plot(
    [0.5 - offset, 0.5 + offset],
    [mean_touch, mean_touch],
    lw=params_figure['width_lines'] + 5,
    color=colours['cold_touch'],
)

ax.plot([0, 0.5], [mean_notouch, mean_touch], lw=params_figure['width_lines'], color="black", zorder=0)

subj_values_notouch = data_experiment['cresponse'][data_experiment['touch'] == 0]
subj_values_touch = data_experiment['cresponse'][data_experiment['touch'] == 1]
ax.plot(
    [0, 0.5],
    [subj_values_notouch, subj_values_touch],
    color="grey",
    lw=params_figure['width_lines'] - params_figure['adjust_parti_line'],
    alpha=params_figure['alpha'],
    zorder=0,
)

ax.scatter(
    np.repeat(0, len(subj_values_notouch)),
    subj_values_notouch,
    s=params_figure['scatter_size'],
    color=colours['cold'],
)
ax.scatter(
    np.repeat(0.5, len(subj_values_touch)),
    subj_values_touch,
    s=params_figure['scatter_size'],
    color=colours['cold_touch'],
)

removeSpines(ax)
prettifySpinesTicks(ax)

ax.set_ylabel("Response bias (C)", labelpad=params_figure['pad_size_label'])

ax.axhline(y=0, color="grey", alpha=0.5, linestyle = "--", lw = params_figure["width_lines"] - params_figure["adjust_parti_line"])

ax.set_ylim([-1.5, 1.5])
ax.set_xlim([-0.2, 0.7])

ax.set_xticks([])
ax.set_yticks([-1.5, -1, -0.5, 0, 0.5, 1, 1.5])

plt.tight_layout()
name = "c_bias"
plt.tight_layout()
plt.savefig(f'{figures_path}/{figure_folder_name}/{experiment_name}_{name}.png', dpi=300, transparent=True)

# %% EXPERIMENT 2
experiment_name = 'df_experiment2'
data_experiment = data[experiment_name]

mean_notouch = data_experiment['dprime'][data_experiment['touch'] == 0].mean()
mean_touch = data_experiment['dprime'][data_experiment['touch'] == 1].mean()

fig, ax = plt.subplots(figsize=(10, 10))

offset = 0.1
ax.plot([0 - offset, 0 + offset], [mean_notouch, mean_notouch], lw=params_figure['width_lines'] + 5, color=colours['cold'])
ax.plot(
    [0.5 - offset, 0.5 + offset],
    [mean_touch, mean_touch],
    lw=params_figure['width_lines'] + 5,
    color=colours['cold_touch'],
)

ax.plot([0, 0.5], [mean_notouch, mean_touch], lw=params_figure['width_lines'], color="black", zorder=0)

subj_values_notouch = data_experiment['dprime'][data_experiment['touch'] == 0]
subj_values_touch = data_experiment['dprime'][data_experiment['touch'] == 1]
ax.plot(
    [0, 0.5],
    [subj_values_notouch, subj_values_touch],
    color="grey",
    lw=params_figure['width_lines'] - params_figure['adjust_parti_line'],
    alpha=params_figure['alpha'],
    zorder=0,
)

ax.scatter(
    np.repeat(0, len(subj_values_notouch)),
    subj_values_notouch,
    s=params_figure['scatter_size'],
    color=colours['cold'],
)
ax.scatter(
    np.repeat(0.5, len(subj_values_touch)),
    subj_values_touch,
    s=params_figure['scatter_size'],
    color=colours['cold_touch'],
)

removeSpines(ax)
prettifySpinesTicks(ax)

ax.set_ylabel("Sensitivity (d')", labelpad=params_figure['pad_size_label'])

ax.set_ylim([0, 3.5])
ax.set_xlim([-0.2, 0.7])

ax.set_xticks([])
ax.set_yticks([0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5])

plt.tight_layout()
name = "d_prime"
plt.savefig(f'{figures_path}/{figure_folder_name}/{experiment_name}_{name}.png', dpi=300, transparent=True)

# %%
mean_notouch = data_experiment['cresponse'][data_experiment['touch'] == 0].mean()
mean_touch = data_experiment['cresponse'][data_experiment['touch'] == 1].mean()

fig, ax = plt.subplots(figsize=(10, 10))

offset = 0.1
ax.plot([0 - offset, 0 + offset], [mean_notouch, mean_notouch], lw=params_figure['width_lines'] + 5, color=colours['cold'])
ax.plot(
    [0.5 - offset, 0.5 + offset],
    [mean_touch, mean_touch],
    lw=params_figure['width_lines'] + 5,
    color=colours['cold_touch'],
)

ax.plot([0, 0.5], [mean_notouch, mean_touch], lw=params_figure['width_lines'], color="black", zorder=0)

subj_values_notouch = data_experiment['cresponse'][data_experiment['touch'] == 0]
subj_values_touch = data_experiment['cresponse'][data_experiment['touch'] == 1]
ax.plot(
    [0, 0.5],
    [subj_values_notouch, subj_values_touch],
    color="grey",
    lw=params_figure['width_lines'] - params_figure['adjust_parti_line'],
    alpha=params_figure['alpha'],
    zorder=0,
)

ax.scatter(
    np.repeat(0, len(subj_values_notouch)),
    subj_values_notouch,
    s=params_figure['scatter_size'],
    color=colours['cold'],
)
ax.scatter(
    np.repeat(0.5, len(subj_values_touch)),
    subj_values_touch,
    s=params_figure['scatter_size'],
    color=colours['cold_touch'],
)

removeSpines(ax)
prettifySpinesTicks(ax)

ax.set_ylabel("Response bias (C)", labelpad=params_figure['pad_size_label'])

ax.axhline(y=0, color="grey", alpha=0.5, linestyle = "--", lw = params_figure["width_lines"] - params_figure["adjust_parti_line"])

ax.set_ylim([-1.5, 1.5])
ax.set_xlim([-0.2, 0.7])

ax.set_xticks([])
ax.set_yticks([-1.5, -1, -0.5, 0, 0.5, 1, 1.5])

plt.tight_layout()
name = "c_bias"
plt.savefig(f'{figures_path}/{figure_folder_name}/{experiment_name}_{name}.png', dpi=300, transparent=True)

# %% EXPERIMENT 3
experiment_name = 'df_experiment3'
data_experiment = data[experiment_name]

mean_notouch = data_experiment['dprime'][data_experiment['touch'] == 0].mean()
mean_touch = data_experiment['dprime'][data_experiment['touch'] == 1].mean()
mean_sound = data_experiment['dprime'][data_experiment['touch'] == 2].mean()

fig, ax = plt.subplots(figsize=(10, 10))

offset = 0.1
ax.plot(
    [0 - offset, 0 + offset],
    [mean_notouch, mean_notouch],
    lw=params_figure["width_lines"] + 5,
    color=colours["cold"],
)
ax.plot(
    [0.5 - offset, 0.5 + offset],
    [mean_touch, mean_touch],
    lw=params_figure["width_lines"] + 5 ,
    color=colours["cold_touch"],
)

ax.plot(
    [1 - offset, 1 + offset],
    [mean_sound, mean_sound],
    lw=params_figure["width_lines"] + 5,
    color=colours["sound"],
)

ax.plot([0, 0.5, 1], [mean_notouch, mean_touch, mean_sound], lw=params_figure['width_lines'], color="black", zorder=0)


subj_values_notouch = data_experiment['dprime'][data_experiment['touch'] == 0]
subj_values_touch = data_experiment['dprime'][data_experiment['touch'] == 1]
subj_values_sound = data_experiment['dprime'][data_experiment['touch'] == 2]

ax.plot(
    [0, 0.5, 1],
    [subj_values_notouch, subj_values_touch, subj_values_sound],
    color="grey",
    lw=params_figure["width_lines"] - params_figure["adjust_parti_line"],
    alpha=params_figure["alpha"],
    zorder=0,
)

ax.scatter(
    np.repeat(0, len(subj_values_notouch)),
    subj_values_notouch,
    s=params_figure["scatter_size"],
    color=colours["cold"],
)
ax.scatter(
    np.repeat(0.5, len(subj_values_touch)),
    subj_values_touch,
    s=params_figure["scatter_size"],
    color=colours["cold_touch"],
)

ax.scatter(
    np.repeat(1, len(subj_values_sound)),
    subj_values_sound,
    s=params_figure["scatter_size"],
    color=colours["sound"],
)

removeSpines(ax)
prettifySpinesTicks(ax)

ax.set_ylabel("Sensitivity (d')", labelpad=params_figure["pad_size_label"])

ax.set_ylim([0, 3.5])
ax.set_xlim([-0.2, 1.2])

ax.set_xticks([])
ax.set_yticks([0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5])

plt.tight_layout()
name = "d_prime"
plt.savefig(f'{figures_path}/{figure_folder_name}/{experiment_name}_{name}.png', dpi=300, transparent=True)

# print(data['df_replication_c'])

# %%
fig, ax = plt.subplots(figsize=(10, 10))

mean_notouch = data_experiment['cresponse'][data_experiment['touch'] == 0].mean()
mean_touch = data_experiment['cresponse'][data_experiment['touch'] == 1].mean()
mean_sound = data_experiment['cresponse'][data_experiment['touch'] == 2].mean()

offset = 0.1
ax.plot(
    [0 - offset, 0 + offset],
    [mean_notouch, mean_notouch],
    lw=params_figure["width_lines"] + 5,
    color=colours["cold"],
)
ax.plot(
    [0.5 - offset, 0.5 + offset],
    [mean_touch, mean_touch],
    lw=params_figure["width_lines"] + 5 ,
    color=colours["cold_touch"],
)

ax.plot(
    [1 - offset, 1 + offset],
    [mean_sound, mean_sound],
    lw=params_figure["width_lines"] + 5,
    color=colours["sound"],
)

ax.plot([0, 0.5, 1], [mean_notouch, mean_touch, mean_sound], lw=params_figure['width_lines'], color="black", zorder=0)

subj_values_notouch = data_experiment['cresponse'][data_experiment['touch'] == 0]
subj_values_touch = data_experiment['cresponse'][data_experiment['touch'] == 1]
subj_values_sound = data_experiment['cresponse'][data_experiment['touch'] == 2]

ax.plot(
    [0, 0.5, 1],
    [subj_values_notouch, subj_values_touch, subj_values_sound],
    color="grey",
    lw=params_figure["width_lines"] - params_figure["adjust_parti_line"],
    alpha=params_figure["alpha"],
    zorder=0,
)

ax.scatter(
    np.repeat(0, len(subj_values_notouch)),
    subj_values_notouch,
    s=params_figure["scatter_size"],
    color=colours["cold"],
)
ax.scatter(
    np.repeat(0.5, len(subj_values_touch)),
    subj_values_touch,
    s=params_figure["scatter_size"],
    color=colours["cold_touch"],
)

ax.scatter(
    np.repeat(1, len(subj_values_sound)),
    subj_values_sound,
    s=params_figure["scatter_size"],
    color=colours["sound"],
)

removeSpines(ax)
prettifySpinesTicks(ax)

ax.set_ylabel("Response bias (C)", labelpad=params_figure['pad_size_label'])

ax.axhline(y=0, color="grey", alpha=0.5, linestyle = "--", lw = params_figure["width_lines"] - params_figure["adjust_parti_line"])

ax.set_ylim([-1.5, 1.5])
ax.set_xlim([-0.2, 1.2])

ax.set_xticks([])
ax.set_yticks([-1.5, -1, -0.5, 0, 0.5, 1, 1.5])

plt.tight_layout()
name = "c_bias"
plt.savefig(f'{figures_path}/{figure_folder_name}/{experiment_name}_{name}.png', dpi=300, transparent=True)

# %%

d_prime_replication_cold_alone = data['df_control']['dprime'][data['df_control']['touch'] == 0].to_numpy()
d_prime_replication_cold_touch = data['df_control']['dprime'][data['df_control']['touch'] == 1].to_numpy()
d_prime_replication_cold_sound = data['df_control']['dprime'][data['df_control']['touch'] == 2].to_numpy()

# print(data['df_replication_c'])

print(np.mean(d_prime_replication_cold_sound))
print(np.mean(d_prime_replication_cold_touch))
print(np.mean(d_prime_replication_cold_alone))


# %%
from scipy.stats import ttest_rel

# Perform paired t-tests
t_stat1, p_val1 = ttest_rel(d_prime_replication_cold_alone, d_prime_replication_cold_sound)
t_stat2, p_val2 = ttest_rel(d_prime_replication_cold_alone, d_prime_replication_cold_touch)

