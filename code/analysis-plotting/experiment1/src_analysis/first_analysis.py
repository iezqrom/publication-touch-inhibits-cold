# %%
from sdt_analysis import SDTloglinear, tableTosdtDoble
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from saving_data import buildDict, appendDataDict
import scipy
from plotting import (
    plotParams,
    pad_size_label,
    pad_size_ticks,
    width_lines,
    length_ticks,
    scatter_size,
    nt_color,
    t_color,
)

import csv

plotParams()

# %%
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

data = buildDict(
    "subject",
    "correc_present_touch",
    "correc_absent_touch",
    "correc_present_notouch",
    "correc_absent_notouch",
    "touch-perc-correct",
    "no-touch-perc-correct",
    "hr-touch-loglinear",
    "fa-touch-loglinear",
    "hr-notouch-loglinear",
    "fa-notouch-loglinear",
    "d-prime-touch",
    "d-prime-notouch",
    "c-response-touch",
    "c-response-notouch",
)
temp_file_name = "unblind"
temp_file = open(f"../globalfigures/{temp_file_name}.csv", "w")
temp_data_writer = csv.writer(temp_file)
temp_data_writer.writerow(list(data.keys()))

data_stats = []

for nsub, ta in enumerate(to_analyse):
    folder_name = "test" + "_" + ta

    ### SUBJECT
    filename = "cleaned_data"

    table_data = pd.read_csv(f"../data/{folder_name}/data/{filename}.csv")

    print(folder_name)

    present_yest, present_not, absent_yest, absent_not = tableTosdtDoble(table_data, 1)
    present_yesnt, present_nont, absent_yesnt, absent_nont = tableTosdtDoble(
        table_data, 0
    )

    present_touch = [
        len(present_yest.loc[:, "responses"]),
        len(present_not.loc[:, "responses"]),
    ]
    absent_touch = [
        len(absent_yest.loc[:, "responses"]),
        len(absent_not.loc[:, "responses"]),
    ]

    present_notouch = [
        len(present_yesnt.loc[:, "responses"]),
        len(present_nont.loc[:, "responses"]),
    ]
    absent_notouch = [
        len(absent_yesnt.loc[:, "responses"]),
        len(absent_nont.loc[:, "responses"]),
    ]

    correc_present_touch = present_touch[0] / sum(present_touch)
    correc_absent_touch = absent_touch[1] / sum(absent_touch)

    correc_present_notouch = present_notouch[0] / sum(present_notouch)
    correc_absent_notouch = absent_notouch[1] / sum(absent_notouch)

    all_in = [
        correc_present_touch,
        correc_absent_touch,
        correc_present_notouch,
        correc_absent_notouch,
    ]
    ab_in = [
        np.mean([correc_present_touch, correc_absent_touch]),
        np.mean([correc_present_notouch, correc_absent_notouch]),
    ]

    all_in = np.asarray(all_in)
    ab_in = np.asarray(ab_in)

    to_rand = ["touch", "notouch"]

    sdts = {}
    sdts["touch"] = SDTloglinear(
        present_touch[0], present_touch[1], absent_touch[0], absent_touch[1]
    )
    sdts["notouch"] = SDTloglinear(
        present_notouch[0], present_notouch[1], absent_notouch[0], absent_notouch[1]
    )

    tempRowToWrite = [
        (nsub + 1),
        correc_present_touch,
        correc_absent_touch,
        correc_present_notouch,
        correc_absent_notouch,
        ab_in[0],
        ab_in[1],
        sdts[to_rand[0]]["hit_rate"],
        sdts[to_rand[0]]["fa_rate"],
        sdts[to_rand[1]]["hit_rate"],
        sdts[to_rand[1]]["fa_rate"],
        sdts[to_rand[0]]["d"],
        sdts[to_rand[1]]["d"],
        sdts[to_rand[0]]["c"],
        sdts[to_rand[1]]["c"],
    ]
    tempRowToWrite = [round(num, 2) for num in tempRowToWrite]
    temp_data_writer.writerow(tempRowToWrite)

    data = appendDataDict(data, tempRowToWrite)
    print(data)

    to_rand.reverse()
    for i, cond in enumerate(to_rand):
        data_stats.append([nsub, 0, i, sdts[cond]["d"], sdts[cond]["c"]])


temp_file.close()


stats_pd = pd.DataFrame(
    data_stats, columns=["subj", "exp", "touch", "dprime", "cresponse"]
)

stats_pd.to_csv(f"../globalfigures/df_4_stats_exp1.csv", header=True)

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
scipy.stats.ttest_rel(
    data["d-prime-notouch"], data["d-prime-touch"], alternative="greater"
)

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
