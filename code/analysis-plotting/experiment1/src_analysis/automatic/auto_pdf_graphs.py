# %% Script to animate sdt trials

from classes_tharnalBeta import ReAnRaw
from matplotlib import animation
import mpl_toolkits.mplot3d.axes3d as p3

colorMapType = 0
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib import animation

### Data structure
import numpy as np

## Media
from imutils.video import VideoStream
from classes_tharnal import *
from classes_plotting import *
from datetime import date
import pandas as pd
import time
import argparse
from saving_data import *
import time
from local_functions import *
import os
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import letter, portrait, A4, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from PyPDF2 import PdfFileMerger

### Individual

# BEH Perc correct
# BEH Hit and fa rates
# BEH sensitivity with extremes
# BEH sensitivity with loglinear
# BEH A prime
# BEH bias with extremes
# BEH bias with loglinear
# BEH failed trials and total trials

# 'time_dist_sdtC_block1', 'time_dist_sdtC_block2',
# 'time_dist_sdtC_block3', 'time_dist_sdtC_block4',
# 'time_dist_sdtC_block5', 'time_dist_sdtC_block6',
# 'time_dist_sdtNC_block1', 'time_dist_sdtNC_block2',
# 'time_dist_sdtNC_block3', 'time_dist_sdtNC_block4',
# 'time_dist_sdtNC_block5', 'time_dist_sdtNC_block6',
# 'traces_sdtT_block1', 'traces_sdtT_block2',
# 'traces_sdtT_block3', 'traces_sdtT_block4',
# 'traces_sdtT_block5', 'traces_sdtT_block6',
# 'traces_sdtNT_block1', 'traces_sdtNT_block2',
# 'traces_sdtNT_block3', 'traces_sdtNT_block4',
# 'traces_sdtNT_block5', 'traces_sdtNT_block6',


if __name__ == "__main__":
    # time.sleep(60)
    parser = argparse.ArgumentParser(description="Folder name")
    parser.add_argument("-f", type=str)
    args = parser.parse_args()
    folder_name = args.f

    name_figures = [
        "staircases",
        "perc_correct",
        "ab_correct",
        "hr_fa_rates",
        "d_prime",
        "c_bias",
        "a_prime",
        "time_dist_sdtC",
        "time_dist_sdtNC",
        "traces_sdtT",
        "traces_sdtNT",
    ]

    path = os.path.realpath(__file__)
    root_path = path.rsplit("/", 3)[0]

    names = grabManyvideos(root_path, folder_name)

    ### SUBJECT

    tdus = folder_name.split(folder_name)

    pattern_delta = f"delta_.*\_{tdus[1]}.*\.txt"
    patternc_delta = re.compile(pattern_delta)
    print(patternc_delta)
    names_delta = []

    for filename in os.listdir(f"{root_path}/data/{folder_name}/data/"):
        # print(filename)
        if patternc_delta.match(filename):
            # print(filename)
            name, form = filename.split(".")
            names_delta.append(name)
        else:
            continue

    names_delta.sort(key=natural_keys)
    print(names_delta)

    with open(f"{root_path}/data/{folder_name}/data/{names_delta[0]}.txt") as f:
        var = f.readline()
        delta_value = float(var)

    print(f"DELTA: {delta_value}")

    if np.isnan(delta_value):
        delta_value = 0.1
        printme("DELTA IS NAN")

    failed_all = []
    failed_touch = 0
    failed_notouch = 0

    ##### Figures
    save_fig_path = f"{root_path}/data/{folder_name}/figures/"

    ############ SDT
    names_SDT = grabManyvideos(root_path, folder_name, pattern=f"sdt_.*\.hdf5$")
    filename_SDT = "cleaned_data"

    table_data = pd.read_csv(f"{root_path}/data/{folder_name}/data/{filename_SDT}.csv")
    table_cold = table_data.loc[table_data["cold"] == 1]
    table_nocold = table_data.loc[table_data["cold"] == 0]

    cold_bool = np.asarray(table_data["cold"])
    touch_bool = np.asarray(table_data["touch"])
    responses_bool = np.asarray(table_data["responses"])

    times_cold = []
    times_nocold = []
    all_deltas_notouch = []
    all_deltas_touch = []

    for isdt, n in enumerate(names_SDT):
        deltas_notouch = []
        deltas_touch = []
        if (isdt + 1) in list(table_cold["trial"]):
            # print(n, isdt +1)
            dat_im = ReAnRaw(f"{root_path}/data/{folder_name}/videos/{n}")
            dat_im.datatoDic()

            times_cold.append(dat_im.data["time_now"][-1][0])
            # print(times_cold)
            temp_indv_table = table_cold.loc[table_cold["trial"] == isdt + 1]

            if list(temp_indv_table["touch"])[0] == 1:
                for i, dl in enumerate(dat_im.data["delta"]):
                    deltas_touch.append(round(dl[0], 2))

            elif list(temp_indv_table["touch"])[0] == 0:
                for i, dl in enumerate(dat_im.data["delta"]):
                    deltas_notouch.append(round(dl[0], 2))

        if (isdt + 1) in list(table_nocold["trial"]):
            dat_im = ReAnRaw(f"{root_path}/data/{folder_name}/videos/{n}")
            dat_im.datatoDic()

            times_nocold.append(dat_im.data["time_now"][-1][0])

        all_deltas_notouch.append(deltas_notouch)
        all_deltas_touch.append(deltas_touch)

    print(len(times_cold))
    print(len(times_nocold))

    print(len(all_deltas_notouch))
    print(len(all_deltas_touch))

    # SDT time distribution COLD
    fig, ax = plt.subplots(figsize=(5, 3))

    n, bins, patches = plt.hist(times_cold, bins=10, color="k", alpha=0.7, rwidth=0.85)

    ax.set_title(f"Time trial distribution COLD")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Frequency")
    ax.set_xlim([0, 14])
    ax.set_ylim(0)
    plt.tight_layout()

    plt.savefig(f"{save_fig_path}time_dist_sdtC.png")

    # SDT time distribution COLD
    fig, ax = plt.subplots(figsize=(5, 3))

    n, bins, patches = plt.hist(
        times_nocold, bins=10, color="k", alpha=0.7, rwidth=0.85
    )

    ax.set_title(f"Time trial distribution NO COLD")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Frequency")
    ax.set_xlim([0, 14])
    ax.set_ylim(0)
    plt.tight_layout()

    plt.savefig(f"{save_fig_path}time_dist_sdtNC.png")

    # SDT traces per block TOUCH
    fig, ax = plt.subplots(figsize=(5, 3))

    for deltas_to_plot in all_deltas_touch:
        plt.plot(deltas_to_plot, alpha=0.8, color="k")

    framesToseconds(ax, 1, max(all_deltas_touch, key=len))
    ax.set_title(f"Delta trace touch")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Delta")
    ax.axhline(delta_value, color="g")

    plt.tight_layout()

    plt.savefig(f"{save_fig_path}traces_sdtT.png")

    # SDT traces per block NO TOUCH
    fig, ax = plt.subplots(figsize=(5, 3))

    for deltas_to_plot in all_deltas_notouch:
        plt.plot(deltas_to_plot, alpha=0.8, color="k")

    framesToseconds(ax, 1, max(all_deltas_notouch, key=len))

    ax.set_title(f"Delta trace NO touch")
    ax.axhline(delta_value, color="g")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Delta")
    # ax.set_xlim([0, 14])
    plt.tight_layout()

    plt.savefig(f"{save_fig_path}traces_sdtNT.png")

    # BEH Perc correct

    table_data.to_csv(f"{root_path}/data/{folder_name}/data/cleaned_data.csv")

    cleaned_table_data = table_data
    cleaned_table_cold = table_data.loc[table_data["cold"] == 1]

    n_ct_trials = len(cleaned_table_cold.loc[cleaned_table_cold["touch"] == 1])
    n_cnt_trials = len(cleaned_table_cold.loc[cleaned_table_cold["touch"] == 0])

    present_yest, present_not, absent_yest, absent_not = tableTosdtDoble(
        cleaned_table_data, 1
    )
    present_yesnt, present_nont, absent_yesnt, absent_nont = tableTosdtDoble(
        cleaned_table_data, 0
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

    np.random.shuffle(all_in)
    np.random.shuffle(ab_in)

    ### PLOT PERC CORRECT
    fig, ax = plt.subplots(figsize=(5, 3))

    ax.bar(np.arange(1, len(all_in) + 0.1, 1), all_in)

    for i, xpos in enumerate(np.arange(1, len(all_in) + 0.1, 1)):
        ax.text(xpos, all_in[i] + 0.1, str(round(all_in[i], 2)))
    ax.set_xticks([1, 2, 3, 4])
    ax.set_ylim([0, 1])
    ax.set_yticks(np.arange(0, 1.01, 0.1))

    ax.set_ylabel("Perc correct")

    plt.savefig(f"{root_path}/data/{folder_name}/figures/perc_correct.png")
    fig.clf()

    ### PLOT PERC CORRECT pooled by touch vs no-touch
    fig, ax = plt.subplots(figsize=(5, 3))

    ax.bar(np.arange(1, len(ab_in) + 0.1, 1), ab_in)

    for i, xpos in enumerate(np.arange(1, len(ab_in) + 0.1, 1)):
        ax.text(xpos, ab_in[i] + 0.1, str(round(ab_in[i], 2)))

    ax.set_xticks([1, 2])
    ax.set_ylim([0, 1])

    ax.set_ylabel("Perc correct")
    ax.set_yticks(np.arange(0, 1.01, 0.1))

    plt.savefig(f"{root_path}/data/{folder_name}/figures/ab_correct.png")
    fig.clf()

    ######################################################
    ################### MORE BEHAVIOUR ###################
    ######################################################

    temp_summary = {}
    sdts = {
        "extremes": {"touch": None, "notouch": None},
        "loglinear": {"touch": None, "notouch": None},
        "a_prime": {"touch": None, "notouch": None},
    }
    to_rand = ["touch", "notouch"]
    np.random.shuffle(to_rand)

    sdts["extremes"]["touch"] = SDTextremes(
        present_touch[0], present_touch[1], absent_touch[0], absent_touch[1]
    )
    sdts["extremes"]["notouch"] = SDTextremes(
        present_notouch[0], present_notouch[1], absent_notouch[0], absent_notouch[1]
    )

    temp_summary["HR-A-extremes"] = round(sdts["extremes"][to_rand[0]]["hit_rate"], 2)
    temp_summary["FA-A-extremes"] = round(sdts["extremes"][to_rand[0]]["fa_rate"], 2)
    temp_summary["d-A-extremes"] = round(sdts["extremes"][to_rand[0]]["d"], 2)
    temp_summary["c-A-extremes"] = round(sdts["extremes"][to_rand[0]]["c"], 2)

    temp_summary["HR-B-extremes"] = round(sdts["extremes"][to_rand[1]]["hit_rate"], 2)
    temp_summary["FA-B-extremes"] = round(sdts["extremes"][to_rand[1]]["fa_rate"], 2)
    temp_summary["d-B-extremes"] = round(sdts["extremes"][to_rand[1]]["d"], 2)
    temp_summary["c-B-extremes"] = round(sdts["extremes"][to_rand[1]]["c"], 2)

    ### loglinear
    sdts["loglinear"]["touch"] = SDTloglinear(
        present_touch[0], present_touch[1], absent_touch[0], absent_touch[1]
    )
    sdts["loglinear"]["notouch"] = SDTloglinear(
        present_notouch[0], present_notouch[1], absent_notouch[0], absent_notouch[1]
    )

    temp_summary["HR-A-loglinear"] = round(sdts["loglinear"][to_rand[0]]["hit_rate"], 2)
    temp_summary["FA-A-loglinear"] = round(sdts["loglinear"][to_rand[0]]["fa_rate"], 2)
    temp_summary["d-A-loglinear"] = round(sdts["loglinear"][to_rand[0]]["d"], 2)
    temp_summary["c-A-loglinear"] = round(sdts["loglinear"][to_rand[0]]["c"], 2)

    temp_summary["HR-B-loglinear"] = round(sdts["loglinear"][to_rand[1]]["hit_rate"], 2)
    temp_summary["FA-B-loglinear"] = round(sdts["loglinear"][to_rand[1]]["fa_rate"], 2)
    temp_summary["d-B-loglinear"] = round(sdts["loglinear"][to_rand[1]]["d"], 2)
    temp_summary["c-B-loglinear"] = round(sdts["loglinear"][to_rand[1]]["c"], 2)

    ## A'
    sdts["a_prime"]["touch"] = SDTAprime(
        present_touch[0], present_touch[1], absent_touch[0], absent_touch[1]
    )
    sdts["a_prime"]["notouch"] = SDTAprime(
        present_notouch[0], present_notouch[1], absent_notouch[0], absent_notouch[1]
    )

    temp_summary["HR-A-Aprime"] = round(sdts["a_prime"][to_rand[0]]["hit_rate"], 2)
    temp_summary["FA-A-Aprime"] = round(sdts["a_prime"][to_rand[0]]["fa_rate"], 2)
    temp_summary["Aprime-A-Aprime"] = round(sdts["a_prime"][to_rand[0]]["Aprime"], 2)

    temp_summary["HR-B-Aprime"] = round(sdts["a_prime"][to_rand[1]]["hit_rate"], 2)
    temp_summary["FA-B-Aprime"] = round(sdts["a_prime"][to_rand[1]]["fa_rate"], 2)
    temp_summary["Aprime-B-Aprime"] = round(sdts["a_prime"][to_rand[1]]["Aprime"], 2)

    # BEH Hit and fa rates
    fig, ax = plt.subplots(figsize=(5, 3))

    hits_fas = [
        temp_summary["HR-A-extremes"],
        temp_summary["FA-A-extremes"],
        temp_summary["HR-B-extremes"],
        temp_summary["FA-B-extremes"],
        temp_summary["HR-A-loglinear"],
        temp_summary["FA-A-loglinear"],
        temp_summary["HR-B-loglinear"],
        temp_summary["FA-B-loglinear"],
        temp_summary["HR-A-Aprime"],
        temp_summary["FA-A-Aprime"],
        temp_summary["HR-B-Aprime"],
        temp_summary["FA-B-Aprime"],
    ]

    poses_rates = [1, 2, 3, 4, 6, 7, 8, 9, 11, 12, 13, 14]
    ax.bar(poses_rates, hits_fas)

    for i, xpos in enumerate(poses_rates):
        ax.text(xpos, hits_fas[i] + 0.1, str(hits_fas[i]))

    ax.set_xticks(poses_rates)
    ax.set_ylim([0, 1])

    labelsx = [item.get_text() for item in ax.get_xticklabels()]
    ticks_names = [
        "HR-A-extremes",
        "FA-A-extremes",
        "HR-B-extremes",
        "FA-B-extremes",
        "HR-A-loglinear",
        "FA-A-loglinear",
        "HR-B-loglinear",
        "FA-B-loglinear",
        "HR-A-Aprime",
        "FA-A-Aprime",
        "HR-B-Aprime",
        "FA-B-Aprime",
    ]

    for j in enumerate(ticks_names):
        labelsx[j[0]] = j[1]

    ax.set_xticklabels(labelsx, rotation=90)
    plt.tight_layout()

    ax.set_ylabel("Rates")

    plt.savefig(f"{root_path}/data/{folder_name}/figures/hr_fa_rates.png")
    fig.clf()

    # BEH sensitivity with extremes AND loglinear
    fig, ax = plt.subplots(figsize=(5, 3))

    ds_das = [
        temp_summary["d-A-extremes"],
        temp_summary["d-B-extremes"],
        temp_summary["d-A-loglinear"],
        temp_summary["d-B-loglinear"],
    ]

    poses_ds = [1, 2, 4, 5]
    ax.bar(poses_ds, ds_das)

    for i, xpos in enumerate(poses_ds):
        ax.text(xpos, ds_das[i] + 0.1, str(ds_das[i]))

    ax.set_xticks(poses_ds)
    # ax.set_ylim([0, 1])

    labelsx = [item.get_text() for item in ax.get_xticklabels()]
    ticks_names = ["d-A-extremes", "d-B-extremes", "d-A-loglinear", "d-B-loglinear"]

    for j in enumerate(ticks_names):
        labelsx[j[0]] = j[1]

    ax.set_xticklabels(labelsx, rotation=90)
    plt.tight_layout()

    ax.set_ylabel("d-prime")

    plt.savefig(f"{root_path}/data/{folder_name}/figures/d_prime.png")
    fig.clf()

    # BEH bias with extremes AND loglinear
    fig, ax = plt.subplots(figsize=(5, 3))

    cs_ces = [
        temp_summary["c-A-extremes"],
        temp_summary["c-B-extremes"],
        temp_summary["c-A-loglinear"],
        temp_summary["c-B-loglinear"],
    ]

    poses_cs = [1, 2, 4, 5]
    ax.bar(poses_cs, cs_ces)

    for i, xpos in enumerate(poses_cs):
        ax.text(xpos, cs_ces[i] + 0.1, str(cs_ces[i]))

    ax.set_xticks(poses_cs)
    # ax.set_ylim([0, 1])

    labelsx = [item.get_text() for item in ax.get_xticklabels()]
    ticks_names = ["c-A-extremes", "c-B-extremes", "c-A-loglinear", "c-B-loglinear"]

    for j in enumerate(ticks_names):
        labelsx[j[0]] = j[1]

    ax.set_xticklabels(labelsx, rotation=90)
    plt.tight_layout()

    ax.set_ylabel("c-prime")

    plt.savefig(f"{root_path}/data/{folder_name}/figures/c_bias.png")
    fig.clf()

    # BEH A prime

    fig, ax = plt.subplots(figsize=(5, 3))

    as_primes = [temp_summary["Aprime-A-Aprime"], temp_summary["Aprime-B-Aprime"]]

    poses_as = [1, 2]
    ax.bar(poses_as, as_primes)

    for i, xpos in enumerate(poses_as):
        ax.text(xpos, as_primes[i] + 0.1, str(as_primes[i]))

    ax.set_xticks(poses_as)
    ax.set_ylim([0, 1])

    labelsx = [item.get_text() for item in ax.get_xticklabels()]
    ticks_names = ["Aprime-A-Aprime", "Aprime-B-Aprime"]

    for j in enumerate(ticks_names):
        labelsx[j[0]] = j[1]

    ax.set_xticklabels(labelsx, rotation=90)
    plt.tight_layout()

    ax.set_ylabel("a-prime")

    plt.savefig(f"{root_path}/data/{folder_name}/figures/a_prime.png")
    fig.clf()

    ##############################################################################
    ########################## CREATE PDF SECTION for subj #######################
    ##############################################################################
    try:
        os.remove(f"{root_path}/data/{folder_name}/figures/section_subj.pdf")
    except:
        print("REMOVE")
        pass

    doc = SimpleDocTemplate(
        f"{root_path}/data/{folder_name}/figures/section_subj.pdf",
        pagesize=landscape(A4),
        rightMargin=0,
        leftMargin=0,
        topMargin=18,
        bottomMargin=18,
    )

    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="Justify", alignment=TA_JUSTIFY, fontName="Helvetica-Bold", fontSize=15
        )
    )

    Subj = []

    # n_subj = f'Subject {ns + 1}'

    # Subj.append(Paragraph(n_subj, styles["Justify"]))

    image_table_write = []
    for pair in pairwise(name_figures):

        temp_pair = []
        for partnerfig in pair:
            if partnerfig:
                # print(partnerfig)
                try:
                    graph = Image(
                        f"{save_fig_path}{partnerfig}.png", 5 * inch, 3 * inch
                    )
                    temp_pair.append(graph)
                except:
                    print("COULNT FIND IMAGE")
                    pass

        image_table_write.append(temp_pair)

    table = Table(image_table_write)

    # BEH failed trials and total trials
    temp_summary["failed-touch"] = 27 - n_ct_trials
    temp_summary["usable-touch"] = n_ct_trials
    temp_summary["failed-notouch"] = 27 - n_cnt_trials
    temp_summary["usable-notouch"] = n_cnt_trials

    failed_total = [
        f"Failed touch trials: {temp_summary['failed-touch']}",
        f"Failed no touch trials: {temp_summary['failed-notouch']}",
        f"Usable touch trials: {temp_summary['usable-touch']}",
        f"Usable no touch trials: {temp_summary['usable-notouch']}",
    ]

    Subj.append(table)
    for ft in failed_total:
        Subj.append(Paragraph(ft, styles["Justify"]))

    doc.build(Subj)
