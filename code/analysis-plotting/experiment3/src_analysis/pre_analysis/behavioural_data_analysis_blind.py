import sys
sys.path.append("../..")
sys.path.append("..")
from sdt_analysis import SDTloglinear, tableTosdtDoble
import numpy as np
import pandas as pd
from index_funcs import parsingSituation, mkpaths
from saving_data import getSubjNumDec

if __name__ == "__main__":

    situ, day, _ = parsingSituation()
    subject_n = getSubjNumDec(day=day)
    path_day, path_anal, path_figs, path_data, path_videos, path_audios = mkpaths(
        situ, numdaysubj = subject_n, folder_name=day
    )

    name_file = "data_controlsdt_subj"


    table_data = pd.read_csv(f"{path_data}/{name_file}.csv")
    
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

    # randomise the order of the keys in the dictionary
    sdts = {k: sdts[k] for k in np.random.permutation(list(sdts.keys()))}

    # save sdts to csv file for later use with columns named as keys and rows the conditions
    df = pd.DataFrame(sdts)
    df = df.transpose()
    # get the string in name_file before the last underscore
    name_sdt_file = name_file.rsplit("_")[1]
    df.to_csv(f"{path_data}/{name_sdt_file}_sdt_blind.csv", index=False)