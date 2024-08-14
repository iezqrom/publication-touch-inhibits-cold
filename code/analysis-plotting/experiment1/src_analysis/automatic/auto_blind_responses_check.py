# %%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from classes_text import *
from local_functions import *
from scipy.stats import norm
import argparse
import os

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Folder name")
    parser.add_argument("-f", type=str)
    args = parser.parse_args()
    folder_name = args.f

    path = os.path.realpath(__file__)
    root_path = path.rsplit("/", 3)[0]

    # todaydate = '29032021_1'
    namefile = "data_subj"

    # folder_name = "test_" + todaydate
    table_data = pd.read_csv(f"{root_path}/data/{folder_name}/data/{namefile}.csv")
    # print(len(table_data))

    # exclude = [24, 28, 29, 31, 34, 80, 85, 86, 90]
    # exclude = [x - 1 for x in exclude]
    # table_data = table_data.drop(exclude)

    print(f"Total number of trials: {len(table_data)}")
    dict_data = table_data.to_dict()

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

    all_in = np.asarray(all_in)

    np.random.shuffle(all_in)

    printme("Percent correct responses")

    printme(all_in)

    fig, ax = plt.subplots()

    ax.bar(np.arange(1, len(all_in) + 0.1, 1), all_in)

    ax.set_xticks([1, 2, 3, 4])

    ax.set_ylim([0, 1])

    tdus = folder_name.split(folder_name)

    plt.savefig(
        f"{root_path}/data/{folder_name}/figures/blind_performance{tdus[1]}.jpg"
    )

    fig.clf()

    ### D-prime
    sdt_touch = SDTextremes(
        present_touch[0], present_touch[1], absent_touch[0], absent_touch[1]
    )
    sdt_notouch = SDTextremes(
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
    plt.savefig(f"{root_path}/data/{folder_name}/figures/blind_d_prime{tdus[1]}.jpg")

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
    plt.savefig(f"{root_path}/data/{folder_name}/figures/blind_c_{tdus[1]}.jpg")

    fig.clf()

    text_to_write = f"Percent correct responses: {all_in}\nSensitivity (d): {all_ds}\nResponse bias (C): {all_cs}"

    with open(f"{root_path}/data/{folder_name}/figures/blind_data.txt", "w") as f:
        f.write(text_to_write)


# %%
