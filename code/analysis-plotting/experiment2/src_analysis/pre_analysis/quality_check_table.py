from local_functions import *
import numpy as np
import pandas as pd
import time
from saving_data import *


if __name__ == "__main__":

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
        "category-a-perc-correct",
        "category-b-perc-correct",
        "hr-a-loglinear",
        "fa-a-loglinear",
        "hr-b-loglinear",
        "fa-b-loglinear",
        "d-prime-a",
        "d-prime-b",
        "c-response-a",
        "c-response-b",
    )
    temp_data_writer, temp_file, temp_file_name = tempSaving(
        "../globalfigures", list(data.keys())
    )

    for nsub, ta in enumerate(to_analyse):
        folder_name = "test" + "_" + ta

        ### SUBJECT
        filename = "cleaned_data"

        table_data = pd.read_csv(f"../data/{folder_name}/data/{filename}.csv")

        print(folder_name)

        present_yest, present_not, absent_yest, absent_not = tableTosdtDoble(
            table_data, 1
        )
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

        np.random.shuffle(all_in)
        np.random.shuffle(ab_in)

        to_rand = ["touch", "notouch"]
        np.random.shuffle(to_rand)

        sdts = {}
        sdts["touch"] = SDTloglinear(
            present_touch[0], present_touch[1], absent_touch[0], absent_touch[1]
        )
        sdts["notouch"] = SDTloglinear(
            present_notouch[0], present_notouch[1], absent_notouch[0], absent_notouch[1]
        )

        tempRowToWrite = [
            (nsub + 1),
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

    temp_file.close()
