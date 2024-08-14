import matplotlib.pyplot as plt
from saving_data import *
import time
from local_functions import *
import os
from classes_tharnal import *
from classes_plotting import *
from datetime import date
import pandas as pd
import random

from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import letter, portrait, A4, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from PyPDF2 import PdfFileMerger


def hfamcrsdtout(
    present_yest,
    present_not,
    absent_yest,
    absent_not,
    present_yesnt,
    present_nont,
    absent_yesnt,
    absent_nont,
):

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

    sdtstouch = SDTloglinear(
        present_touch[0], present_touch[1], absent_touch[0], absent_touch[1]
    )
    sdtsnotouch = SDTloglinear(
        present_notouch[0], present_notouch[1], absent_notouch[0], absent_notouch[1]
    )

    return sdtstouch, sdtsnotouch


def randplot(data, title, label, cate, subj=1, ylim=[0, 4]):
    fig, ax = plt.subplots(figsize=(5, 3))

    means = []
    for k in data.keys():
        ax.scatter([k] * len(data[k]), data[k], color="k", alpha=0.6)
        means.append(np.mean(data[k]))

    ax.set_title(f"{title}")
    ax.set_xlabel("Number of failed trials")
    ax.set_ylabel(f"{label}")
    ax.set_ylim(ylim)
    plt.tight_layout()
    # print(len(means))

    ax.plot(list(data.keys()), means, color="yellow", lw=4)
    plt.savefig(
        f"{root_path}/globalfigures/simulations_efffectsize/{label}_{cate}_{subj}.png"
    )

    return means


# mean across participants for each condition
# mean across simulations

if __name__ == "__main__":
    path = os.path.realpath(__file__)
    root_path = path.rsplit("/", 2)[0]

    to_simulate = [
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

    # to_simulate = ['28052021_3', '28052021_2', '28052021_1']

    filename_SDT = "cleaned_data"

    means_dis = []
    means_ces = []

    dis = {"touch": {}, "notouch": {}}
    ces = {"touch": {}, "notouch": {}}

    ite = 1000
    simu_failed = 36

    for i in range(0, simu_failed):
        dis["touch"][i] = {}
        dis["notouch"][i] = {}
        ces["touch"][i] = {}
        ces["notouch"][i] = {}

        for sf in range(0, ite):
            dis["touch"][i][sf] = []
            dis["notouch"][i][sf] = []
            ces["touch"][i][sf] = []
            ces["notouch"][i][sf] = []

    for ti, ts in enumerate(to_simulate):
        folder_name = "test_" + ts

        table_data = pd.read_csv(
            f"{root_path}/data/{folder_name}/data/{filename_SDT}.csv"
        )
        table_cold = table_data.loc[table_data["cold"] == 1]
        print(f"Original failed trials {(54 - len(table_cold))}")
        table_nocold = table_data.loc[table_data["cold"] == 0]
        always_keep = list(table_nocold.index)

        nsubj = ti + 1

        for fa in range(0, simu_failed):

            loop_ad = []
            loop_bd = []
            loop_ac = []
            loop_bc = []

            for i in range(0, ite):
                keep_index = random.sample(
                    list(table_cold.index), len(list(table_cold.index)) - fa
                )
                to_keep = keep_index + always_keep

                table_rand = table_data.loc[to_keep]

                present_yest, present_not, absent_yest, absent_not = tableTosdtDoble(
                    table_rand, 1
                )
                (
                    present_yesnt,
                    present_nont,
                    absent_yesnt,
                    absent_nont,
                ) = tableTosdtDoble(table_rand, 0)

                touch, notouch = hfamcrsdtout(
                    present_yest,
                    present_not,
                    absent_yest,
                    absent_not,
                    present_yesnt,
                    present_nont,
                    absent_yesnt,
                    absent_nont,
                )

                dis["touch"][fa][i].append(touch["d"])
                dis["notouch"][fa][i].append(notouch["d"])

                ces["touch"][fa][i].append(touch["c"])
                ces["notouch"][fa][i].append(notouch["c"])

            print(f"LENGTH: {len(table_rand)}")

    effect_sizes = {}
    meaned_effectsizes = []

    for i in range(0, simu_failed):
        effect_sizes[i] = []
        for sf in range(0, ite):
            temp_effect_size = (
                np.mean(dis["notouch"][i][sf]) - np.mean(dis["touch"][i][sf])
            ) / np.std((dis["notouch"][i][sf] + dis["touch"][i][sf]))
            effect_sizes[i].append(temp_effect_size)
        meaned_effectsizes.append(np.mean(effect_sizes[i]))

    print(meaned_effectsizes)

    fig, ax = plt.subplots(figsize=(5, 3))

    means = []
    for k in effect_sizes:
        ax.scatter(
            np.repeat(k, len(effect_sizes[k])), effect_sizes[k], color="k", alpha=0.6
        )

    ax.set_xlabel("Number of removed trials")
    ax.set_ylabel("Effect size")
    # ax.set_ylim(ylim)
    plt.tight_layout()

    ax.plot(meaned_effectsizes, color="yellow", lw=4)

    plt.savefig(f"{root_path}/globalfigures/simulations_efffectsize/effectsize_all.png")
