################################ Import stuff ################################
# %%
from classes_arduino import ArdUIno
from classes_arduino import *
from classes_colther import Zaber
from classes_colther import *
from classes_tharnal import *
from classes_camera import TherCam
from saving_data import *
from classes_text import TextIO
from grabPorts import grabPorts
from classes_audio import Sound
from classes_conds import ConditionsHandler
from classes_testData import TestingDataHandler
from classes_tharnal import ReAnRaw

import globals
import time
import threading
import random
import numpy as np
import simpleaudio as sa

from index_funcs import *
import argparse

# %%
if __name__ == "__main__":
    try:
        situ = parsing_situation()
        subject_n = getSubjNumDec()
        path_day, path_anal, path_figs, path_data, path_videos, path_audios = mkpaths(
            situ, subject_n
        )

        rootToUser(path_day, path_anal, path_data, path_figs, path_videos, path_audios)

        # Recover data
        data = pd.read_csv(f"{path_data}/data_staircase_subj.csv")
        data = data.to_dict("list")

        ### Change permissions
        # PLOT and Calculate MEAN
        def summary_staircase(data, n_staircase):
            which_staircase = [
                i for i, val in enumerate(data["staircase"]) if val == n_staircase
            ]
            which_reversed = [i for i, val in enumerate(data["reversed"]) if val]
            intersection = list(set(which_reversed) & set(which_staircase))
            delta_stimulation_list = [
                data["delta_stimulation"][i] for i in intersection[3:]
            ]
            delta_mean = np.mean(delta_stimulation_list)
            return delta_mean

        delta_staircases = [summary_staircase(data, 1), summary_staircase(data, 2)]

        delta_mean = np.mean(delta_staircases)

        print(data)
        print(delta_mean)

        #### PLOT RESPONSES AND MEAN
        fig, axs = plt.subplots(2)

        for si, ax in enumerate(axs):
            which_staircase = [
                i for i, val in enumerate(data["staircase"]) if val == (si + 1)
            ]
            which_notfailed = [i for i, val in enumerate(data["failed"]) if not val]

            intersection_notfailed = list(set(which_staircase) & set(which_notfailed))
            delta_stimulation = [
                data["delta_stimulation"][i] for i in intersection_notfailed
            ]
            delta_target = [data["delta_target"][i] for i in intersection_notfailed]

            which_correct = [i for i, val in enumerate(data["response"]) if val == 1]
            intersection_correct = list(
                set(which_staircase) & set(which_correct) & set(which_notfailed)
            )
            height_correct = [
                data["delta_stimulation"][i] for i in intersection_correct
            ]
            trial_correct = [data["trial"][i] for i in intersection_correct]

            which_incorrect = [i for i, val in enumerate(data["response"]) if val == 0]
            intersection_incorrect = list(
                set(which_staircase) & set(which_incorrect) & set(which_notfailed)
            )
            height_incorrect = [
                data["delta_stimulation"][i] for i in intersection_incorrect
            ]
            trial_incorrect = [data["trial"][i] for i in intersection_incorrect]

            ax.plot(
                np.arange(1, (len(delta_stimulation) + 0.1), 1),
                delta_stimulation,
                color="k",
            )
            ax.plot(np.arange(1, (len(delta_target) + 0.1), 1), delta_target, color="g")

            ax.scatter(trial_incorrect, height_incorrect, color="red")
            ax.scatter(trial_correct, height_correct, color="k")

            ax.axhline(delta_mean, color="k")
            ax.axhline(delta_staircases[si], color="r")

            ax.set_ylim([0, 1.6])
            ax.set_ylabel("Delta")
            ax.set_xlabel("Trials")

            plt.savefig(f"{path_figs}/staircases.png")

        plt.show()

        ## Save data
        saveIndvVar(path_data, delta_mean, "temp_delta")

        rootToUser(path_day, path_anal, path_data, path_figs, path_videos)

    except Exception as e:
        errorloc(e)
        rootToUser(path_day, path_anal, path_data, path_figs, path_videos, path_audios)

    except KeyboardInterrupt:
        print("Keyboard Interrupt")
        rootToUser(path_day, path_anal, path_data, path_figs, path_videos, path_audios)
