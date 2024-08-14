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
import scipy

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
        f"{root_path}/globalfigures/simulations_failed/{label}_{cate}_{subj}.png"
    )

    return means
    ########### ALL TOGETHER


def meanplots(data, title, label, ylim=[0, 4]):
    fig, ax = plt.subplots(figsize=(5, 3))

    means = []
    for k in data:
        ax.plot(k, color="k", alpha=0.6)

    ax.set_title(f"{title}")
    ax.set_xlabel("Number of failed trials")
    ax.set_ylabel(f"{label}")
    ax.set_ylim(ylim)
    plt.tight_layout()

    ax.plot(np.mean(data, axis=0), color="yellow", lw=4)

    plt.savefig(f"{root_path}/globalfigures/simulations_failed/{label}_all.png")


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

    simu_dprimetouch = []
    simu_dprimenotouch = []

    simu_cbiastouch = []
    simu_cbiasnotouch = []

    for ti, ts in enumerate(to_simulate):
        folder_name = "test_" + ts

        table_data = pd.read_csv(
            f"{root_path}/data/{folder_name}/data/{filename_SDT}.csv"
        )
        table_cold = table_data.loc[table_data["cold"] == 1]
        print(f"Original failed trials {(54 - len(table_cold))}")
        table_nocold = table_data.loc[table_data["cold"] == 0]
        always_keep = list(table_nocold.index)

        dis_a = {}
        dis_b = {}
        ces_a = {}
        ces_b = {}
        nsubj = ti + 1

        fa = 36

        loop_ad = []
        loop_bd = []
        loop_ac = []
        loop_bc = []

        ite = 1000

        for i in range(0, ite):
            keep_index = random.sample(
                list(table_cold.index), len(list(table_cold.index)) - fa
            )
            to_keep = keep_index + always_keep

            table_rand = table_data.loc[to_keep]
            # print(f'LENGTH: {len(table_rand)}')

            present_yest, present_not, absent_yest, absent_not = tableTosdtDoble(
                table_rand, 1
            )
            present_yesnt, present_nont, absent_yesnt, absent_nont = tableTosdtDoble(
                table_rand, 0
            )

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

            pairtorandomise = [touch, notouch]

            loop_ad.append(touch["d"])
            loop_bd.append(notouch["d"])

            loop_ac.append(touch["c"])
            loop_bc.append(notouch["c"])

        print(f"LENGTH: {len(table_rand)}")
        dis_a[fa] = loop_ad
        dis_b[fa] = loop_bd

        ces_a[fa] = loop_ac
        ces_b[fa] = loop_bc

        simu_dprimetouch.append(loop_ad)
        simu_dprimenotouch.append(loop_bd)

        simu_cbiastouch.append(loop_ac)
        simu_cbiasnotouch.append(loop_bc)

        meandA = randplot(dis_a, "Touch - d'", "d-prime", "a", nsubj)
        means_dis.append(meandA)

        meandB = randplot(dis_b, "No touch - d'", "d-prime", "b", nsubj)
        means_dis.append(meandB)

        meancA = randplot(ces_a, "Touch - c", "c", "a", nsubj, [-1, 1])
        means_ces.append(meancA)

        meancB = randplot(ces_b, "No touch+ - c", "c", "b", nsubj, [-1, 1])
        means_ces.append(meancB)

        ##############################################################################
        ########################## CREATE PDF SECTION for subj #######################
        ##############################################################################

        name_figures = ["d-prime_a", "d-prime_b", "c_a", "c_b"]

        doc = SimpleDocTemplate(
            f"{root_path}/globalfigures/simulations_failed/section_subj_{nsubj}.pdf",
            pagesize=landscape(A4),
            rightMargin=0,
            leftMargin=0,
            topMargin=18,
            bottomMargin=18,
        )

        styles = getSampleStyleSheet()
        styles.add(
            ParagraphStyle(
                name="Justify",
                alignment=TA_JUSTIFY,
                fontName="Helvetica-Bold",
                fontSize=15,
            )
        )

        Subj = []

        n_subj = f"Subject {nsubj} {ts} Original failed trials {(54 - len(table_cold))}"

        Subj.append(Paragraph(n_subj, styles["Justify"]))

        image_table_write = []
        for pair in pairwise(name_figures):

            temp_pair = []
            for partnerfig in pair:
                if partnerfig:
                    # print(partnerfig)
                    try:
                        graph = Image(
                            f"{root_path}/globalfigures/simulations_failed/{partnerfig}_{nsubj}.png",
                            5 * inch,
                            3 * inch,
                        )
                        temp_pair.append(graph)
                    except:
                        print("COULNT FIND IMAGE")
                        pass

            image_table_write.append(temp_pair)

        table = Table(image_table_write)

        Subj.append(table)

        doc.build(Subj)

    simu_dprimenotouch = np.asarray(simu_dprimenotouch)
    simu_dprimetouch = np.asarray(simu_dprimetouch)
    simu_cbiasnotouch = np.asarray(simu_cbiasnotouch)
    simu_cbiastouch = np.asarray(simu_cbiastouch)

    d_statistic = []
    d_ttest = []
    for i in range(0, ite):
        # print(simu_dprimenotouch[:, i])
        ttest = scipy.stats.ttest_rel(
            simu_dprimenotouch[:, i], simu_dprimetouch[:, i], alternative="greater"
        )
        d_statistic.append(ttest.statistic)
        d_ttest.append(ttest.pvalue)

    c_statistic = []
    c_ttest = []
    for i in range(0, ite):
        # print(simu_dprimenotouch[:, i])
        ttest = scipy.stats.ttest_rel(simu_cbiasnotouch[:, i], simu_cbiastouch[:, i])
        c_statistic.append(ttest.statistic)
        c_ttest.append(ttest.pvalue)

    print(len(d_statistic))
    print(len(d_ttest))

    md_dsta = np.mean(d_statistic)
    md_dtt = np.mean(d_ttest)

    # d_tstatistic
    fig, ax = plt.subplots(figsize=(5, 3))

    ax.scatter(np.repeat(1, len(d_statistic)), d_statistic, color="k", alpha=0.6)

    ax.set_title(f"Statistic d prime")
    plt.tight_layout()

    ax.axhline(y=md_dsta, color="r", linestyle="-")

    plt.savefig(
        f"{root_path}/globalfigures/simulations_failed/dprime_statistic_all.png"
    )

    # d_ttest
    fig, ax = plt.subplots(figsize=(5, 3))

    ax.scatter(np.repeat(1, len(d_ttest)), d_ttest, color="k", alpha=0.6)

    ax.set_title(f"T test d prime")
    plt.tight_layout()

    ax.axhline(y=md_dtt, color="r", linestyle="-")

    plt.savefig(f"{root_path}/globalfigures/simulations_failed/dprime_t_test_all.png")

    md_csta = np.mean(c_statistic)
    md_ctt = np.mean(c_ttest)

    # c bias tstatistic
    fig, ax = plt.subplots(figsize=(5, 3))

    ax.scatter(np.repeat(1, len(c_statistic)), c_statistic, color="k", alpha=0.6)

    ax.set_title(f"Statistic c bias")
    plt.tight_layout()

    ax.axhline(y=md_csta, color="r", linestyle="-")

    plt.savefig(
        f"{root_path}/globalfigures/simulations_failed/c_bias_statistic_all.png"
    )

    # d_ttest
    fig, ax = plt.subplots(figsize=(5, 3))

    ax.scatter(np.repeat(1, len(c_ttest)), c_ttest, color="k", alpha=0.6)

    ax.set_title(f"T test c bias")
    plt.tight_layout()

    ax.axhline(y=md_ctt, color="r", linestyle="-")

    plt.savefig(f"{root_path}/globalfigures/simulations_failed/c_bias_t_test_all.png")

    # meanplots(means_dis, "d'", "d-prime")
    # meanplots(means_ces, "c", "c", [-1, 1])

    # doc = SimpleDocTemplate(f"{root_path}/globalfigures/simulations_failed/section_subj_all.pdf"
    #                 ,pagesize=landscape(A4), rightMargin=0,leftMargin=0,
    #                 topMargin=18,bottomMargin=18)

    # styles=getSampleStyleSheet()
    # styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY, fontName='Helvetica-Bold', fontSize=15))

    # everyone = []

    # image_table_write = []
    # name_figures_all = ['d-prime', 'c']
    # for pair in pairwise(name_figures_all):

    #     temp_pair = []
    #     for partnerfig in pair:
    #         if partnerfig:
    #             # print(partnerfig)
    #             try:
    #                 graph = Image(f'{root_path}/globalfigures/simulations_failed/{partnerfig}_all.png', 5*inch, 3*inch)
    #                 temp_pair.append(graph)
    #             except:
    #                 print('COULNT FIND IMAGE')
    #                 pass

    #     image_table_write.append(temp_pair)

    # table = Table(image_table_write)
    # all_towrite = 'Pooled simulations'
    # everyone.append(Paragraph(all_towrite, styles["Justify"]))

    # all_towrite = 'Each line is the mean d-prime or c of all simulations for one subject. Categories are grouped together.'
    # everyone.append(Paragraph(all_towrite, styles["Justify"]))

    # everyone.append(table)

    # doc.build(everyone)

    # pdf_merger = PdfFileMerger()

    # for tti, ta in enumerate(to_simulate):
    #     pdf_document = f'{root_path}/globalfigures/simulations_failed/section_subj_{tti+1}.pdf'
    #     pdf_merger.append(pdf_document)

    # pdf_document = f'{root_path}/globalfigures/simulations_failed/section_subj_all.pdf'
    # pdf_merger.append(pdf_document)

    # pdf_merger.write(f'{root_path}/globalfigures/simulations_failed/all_simulations.pdf')
    # print('PDF with all subjects created!')


# %%
