# %%
import sys
sys.path.append('../..')
import pandas as pd
import scipy
from plotting import (
    plotParams,
)
from globals import data_path
import os
import numpy as np
from sdt_analysis import SDTloglinear, tableTosdtDoble

plotParams()
# params_figure['adjust_parti_line'] = 4

# %%
# list all the folders in the data folder that start with ex_
subject_folders = [f for f in os.listdir(data_path) if f.startswith('ex_')]
# sort them
subject_folders.sort()

# %%
# if the file excluded.txt is not False change the value of to_analyse.txt to True
for index, subject_folder in enumerate(subject_folders):
    # read the value of f"{data_path}/{subject_folder}/data/excluded.txt"
    with open(f"{data_path}/{subject_folder}/data/excluded.txt", "r") as f:
        excluded = f.read()
    # if it is not False, then change the value of f"{data_path}/{subject_folder}/data/to_analyse.txt" to True
    print(excluded)
    if excluded == "False":
        with open(f"{data_path}/{subject_folder}/data/to_analyse.txt", "w") as f:
            f.write("True")
# %%

data_stats = {}
data_stats['subject'] = []
data_stats['interactor'] = []
data_stats['dprime'] = []
data_stats['cresponse'] = []

# %%
# check whether each folder contains a file replicationsdt_sdt.csv in the subfolder data/
# if it does, then it is a replication experiment
name_file = "data_controlsdt_subj" #, "data_controlsdt_subj"]

for index, subject_folder in enumerate(subject_folders):
    # check the value of to_analyse.txt
    with open(f"{data_path}/{subject_folder}/data/to_analyse.txt", "r") as f:
        to_analyse = f.read()
    # if it is False, then skip this iteration
    if to_analyse == "True":
        table_data = pd.read_csv(f"{data_path}/{subject_folder}/data/{name_file}.csv")
        success_rows = table_data[table_data["failed"] == False]

        sub_tables = {}
        sdts = {}

        for condition in range(0, 3):
            sub_tables[condition] = {}
            sub_tables[condition]['present_yes'], sub_tables[condition]['present_no'], sub_tables[condition]['absent_yes'], sub_tables[condition]['absent_no'] = tableTosdtDoble(success_rows, condition, name_response = "response", name_stimulus = "cooling", name_interactor = "interactor")

            sub_tables[condition]['present_interactor'] = [
                len(sub_tables[condition]['present_yes'].loc[:, "response"]),
                len(sub_tables[condition]['present_no'].loc[:, "response"]),
            ]
            sub_tables[condition]['absent_interactor'] = [
                len(sub_tables[condition]['absent_yes'].loc[:, "response"]),
                len(sub_tables[condition]['absent_no'].loc[:, "response"]),
            ]

            correc_present_interactor = (sub_tables[condition]['present_interactor'][0] / sum(sub_tables[condition]['present_interactor'])) * 100
            correc_absent_interactor = (sub_tables[condition]['absent_interactor'][1] / sum(sub_tables[condition]['absent_interactor'])) * 100


            all_in = [
                correc_present_interactor,
                correc_absent_interactor,
            ]
            ab_in = [
                np.mean([correc_present_interactor, correc_absent_interactor]),
            ]

            all_in = np.asarray(all_in)
            ab_in = np.asarray(ab_in)


            sdts[condition] = SDTloglinear(
                sub_tables[condition]['present_interactor'][0], sub_tables[condition]['present_interactor'][1], sub_tables[condition]['absent_interactor'][0], sub_tables[condition]['absent_interactor'][1]
            )
            sdts[condition]["percent_all"] = np.mean([sdts[condition]['percent_hits'], sdts[condition]['percent_crs']])
            # round all values to 4 decimals without a for loop
            sdts[condition] = {k: round(v, 4) for k, v in sdts[condition].items()}

            data_stats["subject"].append(index)
            data_stats["interactor"].append(condition)
            data_stats["dprime"].append(sdts[condition]["d"])
            data_stats["cresponse"].append(sdts[condition]["c"])

        # save sdts to csv file for later use with columns named as keys and rows the conditions
        # df = pd.DataFrame(sdts)
        # df = df.transpose()
        # # get the string in name_file before the last underscore
        # name_sdt_file = name_file.rsplit("_")[1]
        # df.to_csv(f"{data_path}/{subject_folder}/data/{name_sdt_file}_sdt.csv", index=False)
    

# %%

stats_pd = pd.DataFrame(
    data_stats, columns=["subject", "interactor", "dprime", "cresponse"]
)

stats_pd.to_csv(f"../../globalfigures/df_replication.csv", header=True, index=False)

#%%


# %%
print(data["d-prime-notouch"])
print(data["d-prime-touch"])
(np.mean(data["d-prime-notouch"]) - np.mean(data["d-prime-touch"])) / np.std(
    (data["d-prime-notouch"] + data["d-prime-touch"])
)
# %%
md_notouch = np.mean(data["d-prime-notouch"])
md_touch = np.mean(data["d-prime-touch"])

# %% D - prime
fig, ax = plt.subplots(figsize=(10, 10))

ax.scatter(
    np.repeat(0, len(data["d-prime-touch"])),
    data["d-prime-touch"],
    s=scatter_size,
    color=t_color,
)
ax.scatter(
    np.repeat(1, len(data["d-prime-notouch"])),
    data["d-prime-notouch"],
    s=scatter_size,
    color=nt_color,
)

offset = 0.2
ax.plot([0 - offset, 0 + offset], [md_touch, md_touch], lw=width_lines, color=t_color)
ax.plot(
    [1 - offset, 1 + offset], [md_notouch, md_notouch], lw=width_lines, color=nt_color
)

for i, dd in enumerate(data["d-prime-touch"]):
    ax.plot(
        [0, 1],
        [data["d-prime-touch"], data["d-prime-notouch"]],
        color="k",
        lw=6,
        alpha=0.1,
    )

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

ax.yaxis.set_tick_params(width=width_lines, length=length_ticks)
ax.xaxis.set_tick_params(width=width_lines, length=length_ticks)

ax.spines["left"].set_linewidth(width_lines)
ax.spines["bottom"].set_linewidth(width_lines)

ax.set_ylabel("Sensitivity (d')", labelpad=25)

ax.set_ylim([0, 4])
ax.set_xlim([-0.3, 1.3])

ax.set_xticks([0, 1])
ax.set_yticks([0, 1, 2, 3, 4])

labels = [item.get_text() for item in ax.get_xticklabels()]

labels[0] = "Cold + Touch"
labels[1] = "Cold"

ax.set_xticklabels(labels)

ax.tick_params(axis="y", which="major", pad=20)
ax.tick_params(axis="x", which="major", pad=20)

plt.tight_layout()

name = "d_prime"
plt.savefig(f"../globalfigures/first_anal/{name}.png", transparent=True)

# %%
mc_notouch = np.mean(data["c-response-notouch"])
mc_touch = np.mean(data["c-response-touch"])

# %% C response
fig, ax = plt.subplots(1, 1, figsize=(20, 15))
lwD = 5
lenD = 10

ax.scatter(
    np.repeat(0, len(data["c-response-touch"])),
    data["c-response-touch"],
    s=ss,
    color=t_color,
)
ax.scatter(
    np.repeat(1, len(data["c-response-notouch"])),
    data["c-response-notouch"],
    s=ss,
    color=nt_color,
)

offset = 0.2
ax.plot([0 - offset, 0 + offset], [mc_touch, mc_touch], color=t_color, lw=lenD)
ax.plot([1 - offset, 1 + offset], [mc_notouch, mc_notouch], color=nt_color, lw=lenD)

for i, dd in enumerate(data["c-response-touch"]):
    ax.plot(
        [0, 1], [data["c-response-touch"], data["c-response-notouch"]], color="k", lw=3
    )

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

ax.yaxis.set_tick_params(width=lwD, length=lenD)
ax.xaxis.set_tick_params(width=lwD, length=lenD)

ax.tick_params(axis="y", which="major", pad=10)
ax.tick_params(axis="x", which="major", pad=10)

ax.spines["left"].set_linewidth(lwD)
ax.spines["bottom"].set_linewidth(lwD)

ax.tick_params(axis="y", which="major", pad=10)
ax.tick_params(axis="x", which="major", pad=10)

ax.set_ylabel("Bias (c)", labelpad=20)
# ax.set_xlabel('Time (s)', labelpad=20)
ax.set_ylim([-1.4, 0.4])

ax.set_xticks([0, 1])
labels = [item.get_text() for item in ax.get_xticklabels()]

labels[0] = "Cold + Touch"
labels[1] = "Cold"

ax.set_xticklabels(labels)

plt.tight_layout()

name = "response_bias"
plt.savefig(f"../globalfigures/first_anal/{name}.png")

# %%
scipy.stats.ttest_rel(data["c-response-notouch"], data["c-response-touch"])

# %% Hit rate & fa rate

m_hrt = np.mean(data["hr-touch-loglinear"])
m_fat = np.mean(data["fa-touch-loglinear"])

m_hrnt = np.mean(data["hr-notouch-loglinear"])
m_fant = np.mean(data["fa-notouch-loglinear"])

# %%

fig, ax = plt.subplots(1, 1, figsize=(20, 15))
lwD = 5
lenD = 10

ax.scatter(
    np.repeat(0, len(data["hr-touch-loglinear"])),
    data["hr-touch-loglinear"],
    s=ss,
    color=t_color,
)
ax.scatter(
    np.repeat(1, len(data["fa-touch-loglinear"])),
    data["fa-touch-loglinear"],
    s=ss,
    color=t_color,
)
ax.scatter(
    np.repeat(3, len(data["hr-notouch-loglinear"])),
    data["hr-notouch-loglinear"],
    s=ss,
    color=nt_color,
)
ax.scatter(
    np.repeat(4, len(data["fa-notouch-loglinear"])),
    data["fa-notouch-loglinear"],
    s=ss,
    color=nt_color,
)

offset = 0.2
ax.plot([0 - offset, 0 + offset], [m_hrt, m_hrt], color=t_color, lw=lenD)
ax.plot([1 - offset, 1 + offset], [m_fat, m_fat], color=t_color, lw=lenD)
ax.plot([3 - offset, 3 + offset], [m_hrnt, m_hrnt], color=nt_color, lw=lenD)
ax.plot([4 - offset, 4 + offset], [m_fant, m_fant], color=nt_color, lw=lenD)

for i, dd in enumerate(data["hr-touch-loglinear"]):
    ax.plot(
        [0, 1, 3, 4],
        [
            data["hr-touch-loglinear"],
            data["fa-touch-loglinear"],
            data["hr-notouch-loglinear"],
            data["fa-notouch-loglinear"],
        ],
        color="k",
        lw=3,
        alpha=0.1,
    )

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

ax.yaxis.set_tick_params(width=lwD, length=lenD)
ax.xaxis.set_tick_params(width=lwD, length=lenD)

ax.tick_params(axis="y", which="major", pad=10)
ax.tick_params(axis="x", which="major", pad=10)

ax.spines["left"].set_linewidth(lwD)
ax.spines["bottom"].set_linewidth(lwD)

ax.tick_params(axis="y", which="major", pad=10)
ax.tick_params(axis="x", which="major", pad=10)

ax.set_ylabel("Percent correct (%)", labelpad=20)
# ax.set_xlabel('Time (s)', labelpad=20)
ax.set_ylim([0, 1])

ax.set_xticks([0, 1, 3, 4])
labels = [item.get_text() for item in ax.get_xticklabels()]

labels[0] = "HR touch"
labels[1] = "FA touch"
labels[2] = "HR no touch"
labels[3] = "FA no touch"

ax.set_xticklabels(labels)

plt.tight_layout()

name = "hr_fa"
plt.savefig(f"../globalfigures/first_anal/{name}.png")

# %%
scipy.stats.ttest_rel(
    data["hr-notouch-loglinear"], data["hr-touch-loglinear"], alternative="greater"
)
# %% % perc correct

m_cpt = np.mean(data["correc_present_touch"])
m_cat = np.mean(data["correc_absent_touch"])

m_cpnt = np.mean(data["correc_present_notouch"])
m_cant = np.mean(data["correc_absent_notouch"])

# %%
fig, ax = plt.subplots(1, 1, figsize=(20, 15))
# lwD = 5
# lenD = 10

ax.scatter(
    np.repeat(0, len(data["correc_present_touch"])),
    data["correc_present_touch"],
    s=ss,
    color=t_color,
)
ax.scatter(
    np.repeat(1, len(data["correc_absent_touch"])),
    data["correc_absent_touch"],
    s=ss,
    color=t_color,
)
ax.scatter(
    np.repeat(2, len(data["correc_present_notouch"])),
    data["correc_present_notouch"],
    s=ss,
    color=nt_color,
)
ax.scatter(
    np.repeat(3, len(data["correc_absent_notouch"])),
    data["correc_absent_notouch"],
    s=ss,
    color=nt_color,
)

offset = 0.2
ax.plot([0 - offset, 0 + offset], [m_cpt, m_cpt], color=t_color, lw=lenD)
ax.plot([1 - offset, 1 + offset], [m_cat, m_cat], color=t_color, lw=lenD)
ax.plot([2 - offset, 2 + offset], [m_cpnt, m_cpnt], color=nt_color, lw=lenD)
ax.plot([3 - offset, 3 + offset], [m_cant, m_cant], color=nt_color, lw=lenD)

for i, dd in enumerate(data["correc_present_touch"]):
    ax.plot(
        [0, 1, 2, 3],
        [
            data["correc_present_touch"],
            data["correc_absent_touch"],
            data["correc_present_notouch"],
            data["correc_absent_notouch"],
        ],
        color="k",
        lw=6,
        alpha=0.1,
    )

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

ax.yaxis.set_tick_params(width=lwD, length=lenD)
ax.xaxis.set_tick_params(width=lwD, length=lenD)

ax.tick_params(axis="y", which="major", pad=10)
ax.tick_params(axis="x", which="major", pad=10)

ax.spines["left"].set_linewidth(lwD)
ax.spines["bottom"].set_linewidth(lwD)

ax.tick_params(axis="y", which="major", pad=10)
ax.tick_params(axis="x", which="major", pad=10)

ax.set_ylabel("Percent correct (%)", labelpad=20)
# ax.set_xlabel('Time (s)', labelpad=20)
ax.set_ylim([0, 1])

ax.set_xticks([0, 1, 2, 3])
labels = [item.get_text() for item in ax.get_xticklabels()]

labels[0] = "Cold + Touch"
labels[1] = "Touch"
labels[2] = "Cold"
labels[3] = "None"

ax.set_xticklabels(labels)

plt.tight_layout()

name = "perc_correct"
plt.savefig(f"../globalfigures/first_anal/{name}.png", transparent=True)

# %%
scipy.stats.ttest_rel(
    data["correc_present_notouch"], data["correc_present_touch"], alternative="greater"
)
# %%
