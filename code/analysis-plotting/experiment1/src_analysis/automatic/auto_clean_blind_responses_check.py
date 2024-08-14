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

if __name__ == "__main__":
    # time.sleep(60)
    parser = argparse.ArgumentParser(description="Folder name")
    parser.add_argument("-f", type=str)
    args = parser.parse_args()
    folder_name = args.f

    path = os.path.realpath(__file__)
    root_path = path.rsplit("/", 3)[0]

    ### SUBJECT
    pattern = f"sdt_.*\.hdf5$"
    filename = "data_all"

    table_data = pd.read_csv(f"{root_path}/data/{folder_name}/data/{filename}.csv")
    cold_bool = np.asarray(table_data["cold"])
    touch_bool = np.asarray(table_data["touch"])
    responses_bool = np.asarray(table_data["responses"])

    patternc = re.compile(pattern)
    names = []

    for filename in os.listdir(f"{root_path}/data/{folder_name}/videos/"):
        if patternc.match(filename):
            # print(filename)
            name, form = filename.split(".")
            names.append(name)
        else:
            continue

    names.sort(key=natural_keys)
    print(names)

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

    cleaned_table_data = table_data.loc[table_data["failed"] == False]
    cleaned_table_data = cleaned_table_data.loc[
        cleaned_table_data["stimulus_time"] > 0.4
    ]
    print(cleaned_table_data)
    cleaned_table_data.to_csv(f"{root_path}/data/{folder_name}/data/cleaned_data.csv")

    cleaned_table_cold = cleaned_table_data.loc[cleaned_table_data["cold"] == 1]

    n_ct_trials = len(cleaned_table_cold.loc[cleaned_table_cold["touch"] == 1])
    n_cnt_trials = len(cleaned_table_cold.loc[cleaned_table_cold["touch"] == 0])

    print(f"Clean table: {len(cleaned_table_data)}")
    time.sleep(2)

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

    printme("Percent correct responses")

    printme(all_in)
    printme(ab_in)

    fig, ax = plt.subplots()

    ax.bar(np.arange(1, len(all_in) + 0.1, 1), all_in)

    ax.set_xticks([1, 2, 3, 4])

    ax.set_ylim([0, 1])

    plt.savefig(
        f"{root_path}/data/{folder_name}/figures/cleaned_blind_performance{tdus[0]}.jpg"
    )

    fig.clf()

    fig, ax = plt.subplots()

    ax.bar(np.arange(1, len(ab_in) + 0.1, 1), ab_in)

    ax.set_xticks([1, 2])

    ax.set_ylim([0, 1])

    ax.set_yticks(np.arange(0, 1.01, 0.1))

    plt.savefig(
        f"{root_path}/data/{folder_name}/figures/cleaned_blind_performance_A_B_{tdus[0]}.jpg"
    )

    fig.clf()

    ### D-prime
    sdt_touch = SDTloglinear(
        present_touch[0], present_touch[1], absent_touch[0], absent_touch[1]
    )
    sdt_notouch = SDTloglinear(
        present_notouch[0], present_notouch[1], absent_notouch[0], absent_notouch[1]
    )

    d_t = sdt_touch["d"]
    d_nt = sdt_notouch["d"]

    all_ds = [d_t, d_nt]

    all_ds = np.asarray(all_ds)

    np.random.shuffle(all_ds)

    printme("D-primes")
    printme(all_ds)

    fig = plt.figure(figsize=(15, 13))
    ax = fig.add_subplot(111)

    # ax.bar([1, 2, 4, 5], [correc_present_notouch, correc_present_touch, correc_absent_notouch, correc_absent_touch])
    ax.bar(np.arange(1, len(all_ds) + 0.1, 1), all_ds)

    ax.set_xticks([1, 2])
    ax.set_ylim([0, 3.5])

    ax.set_ylabel("Sensitivity (d')", labelpad=20)

    # ax.legend(custom_lines, ['Cold + Touch', 'Cold'], frameon=False, bbox_to_anchor=(0.7, 0.95))
    plt.savefig(
        f"{root_path}/data/{folder_name}/figures/cleaned_blind_d_prime{tdus[1]}.jpg"
    )

    # %% RESPONSE BIAS
    c_t = sdt_touch["c"]
    c_nt = sdt_notouch["c"]

    all_cs = [c_t, c_nt]

    all_cs = np.asarray(all_cs)

    np.random.shuffle(all_cs)

    printme("Response bias")
    printme(all_cs)

    fig = plt.figure(figsize=(15, 13))
    ax = fig.add_subplot(111)

    # ax.bar([1, 2, 4, 5], [correc_present_notouch, correc_present_touch, correc_absent_notouch, correc_absent_touch])
    ax.bar(np.arange(1, len(all_cs) + 0.1, 1), all_cs)

    ax.set_xticks([1, 2])
    ax.set_xlim([0.5, 2.5])
    ax.set_ylim([-2, 2])

    ax.set_ylabel("Response criterion (C)", labelpad=20)
    plt.savefig(f"{root_path}/data/{folder_name}/figures/cleaned_blind_c_{tdus[1]}.jpg")

    fig.clf()

    text_to_write = f"Percent correct responses: {all_in}\nSensitivity (d): {all_ds}\nResponse bias (C): {all_cs}\nDelta: {delta_value}\nN cold+touch trials: {n_ct_trials}\nN cold+notouch trials: {n_cnt_trials}"

    with open(
        f"{root_path}/data/{folder_name}/figures/cleaned_blind_data.txt", "w"
    ) as f:
        f.write(text_to_write)
