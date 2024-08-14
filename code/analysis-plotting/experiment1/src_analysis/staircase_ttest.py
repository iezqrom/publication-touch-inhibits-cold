# %%
from matplotlib import pyplot as plt
from saving_data import *

import numpy as np

# from index_funcs import *

import scipy


mc = "black"
plt.rcParams.update(
    {
        "font.size": 40,
        "axes.labelcolor": "{}".format(mc),
        "xtick.color": "{}".format(mc),
        "ytick.color": "{}".format(mc),
        "font.family": "sans-serif",
    }
)


# %%
### Change permissions
# PLOT and Calculate MEAN
def summary_staircase(data, n_staircase):
    which_staircase = [
        i for i, val in enumerate(data["staircase"]) if val == n_staircase
    ]
    which_reversed = [i for i, val in enumerate(data["reversed"]) if val]
    intersection = list(set(which_reversed) & set(which_staircase))
    delta_stimulation_list = [data["delta_stimulation"][i] for i in intersection[3:]]
    delta_mean = np.mean(delta_stimulation_list)
    return delta_mean


to_analyse = [
    "28052021_3",
    "28052021_2",
    "28052021_1",
    "27052021_1",
    "24052021_1",
    "21052021_3",
    "21052021_2",
    "20052021_1",
    "18052021_1",
    "14052021_1",
    "07052021_2",
    "08062021_1",
]

asc_list = []
des_list = []

for i, fo in enumerate(to_analyse):
    # Recover data
    data = pd.read_csv(f"../data/test_{fo}/data/data_staircase_subj.csv")
    data = data.to_dict("list")

    asc_list.append(summary_staircase(data, 1))
    des_list.append(summary_staircase(data, 2))

# staircase 1: descending
# staircase 2: ascending
# %%
plt.bar(np.repeat(0, len(asc_list)), asc_list)
plt.bar(np.repeat(0, len(des_list)), des_list)
# %%
weare = scipy.stats.ttest_rel(asc_list, des_list)
# %%
md_asc = np.mean(asc_list)
md_des = np.mean(des_list)
lenD = 10
ss = 150
lwD = 5

fig, ax = plt.subplots(1, 1, figsize=(20, 15))

ax.scatter(np.repeat(0, len(asc_list)), asc_list, s=ss)
ax.scatter(np.repeat(1, len(des_list)), des_list, s=ss)

offset = 0.2
ax.plot([0 - offset, 0 + offset], [md_asc, md_asc], lw=lenD, color="b")
ax.plot([1 - offset, 1 + offset], [md_des, md_des], lw=lenD, color="r")

for aa, dd in zip(asc_list, des_list):
    ax.plot([0, 1], [aa, dd], color="k", lw=3)

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

ax.yaxis.set_tick_params(width=lwD, length=lenD)
ax.xaxis.set_tick_params(width=lwD, length=lenD)

ax.tick_params(axis="y", which="major", pad=10)
ax.tick_params(axis="x", which="major", pad=10)

ax.spines["left"].set_linewidth(lwD)
ax.spines["bottom"].set_linewidth(lwD)

# ax.set_xticks(['Tactile', 'No tactile'])

ax.tick_params(axis="y", which="major", pad=10)
ax.tick_params(axis="x", which="major", pad=10)

plt.tight_layout()
# %%
