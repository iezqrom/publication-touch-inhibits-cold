import sys
sys.path.append('../..')
from arduino import tryexceptArduino
from grabPorts import grabPorts
from failing import (
    getNames,
    recoverData,
    recoverPickleRick,
    spaceLeftWarning,
    rewriteRecoveredData,
)
from saving_data import (
    createTempName,
    saveIndv,
    rootToUser,
    changeNameTempFile,
    tempSaving,
    buildDict,
    csvToDictGridIndv,
    csvToDictROIAll,
    csvToDictPanTiltsAll,
    saveIndvVar,
    handleItiSave,
    copyDict,
    getSubjNumDec
)
from local_functions import (
    closeEnvelope,
    thermalCalibration,
    arduinos_zabers,
    triggerHandleReload,
    panicButton,
    homeButton,
    itiZaberDanceIn,
    itiZaberDanceAway,
    triggeredException,
    deltaToZaberHeight,
    grabNextPosition,
    saveAudio,
    startWatson,
    initWatson,
    waitForWatson,
    deltaTemperature,
    controlSyringeTrial,
    movetostartZabersConcu
)
from audio import Sound
from index_funcs import parsingSituation, mkpaths
from camera import TherCam
from text import printme
from speech import (
    terminateSpeechRecognition,
)

from staircases import Staircase
import threading

from globals import (
    pantilts,
    delay_data_display,
    haxes,
    initial_staircase_temp,
    step_sizes,
    lower_bound_delay,
    higher_bound_delay,
    min_bound_staircase,
    max_bound_staircase,
    rule_down,
    rule_up,
    size_down,
    size_up,
    limit_restimulation,
    staircases_info,
    tone_trial_frequency,
    time_out,
    stop_reversals,
    number_human_mapping,
    park_touch
)

##### READY-MADE CODE
import threading
import numpy as np
import os
import time
import simpleaudio as sa
import keyboard

if __name__ == "__main__":

    path_data = "/Users/ivan/Documents/aaa_online_stuff/coding/python/phd/experiment2_control/data/staircase_check/data"
    staircases = []
    name_staircase_file = f"online_back_up_staircase_up"
    situ = "ex"
    if os.path.exists(f"{path_data}/{name_staircase_file}.pkl"):
        printme(f"RECOVERING staircase dict")
        for staircase in staircases_info:
            name_staircase_file = f"online_back_up_staircase_{staircases_info[staircase]['direction']}"
            staircases.append(recoverPickleRick(path_data, name_staircase_file))
    else:
        for staircase in staircases_info:
            temp_staircase = Staircase(
                total_reversals = stop_reversals[situ],
                initial = staircases_info[staircase]["starting_temp"],
                direction = staircases_info[staircase]["direction"],
            )
            staircases.append(temp_staircase)

    # get positions with constraints online
    while (
        staircases[0].reversals < staircases[0].total_reversals
        or staircases[1].reversals < staircases[1].total_reversals
    ):

        while True:
            current_staircase = np.random.choice([0, 1])
            if (
                staircases[current_staircase].reversals
                >= staircases[current_staircase].total_reversals
            ):
                print(f"staircase_{str(current_staircase)} is finished")
            else:
                break

        print(staircases[current_staircase].stimulation, staircases[current_staircase].tracked_stimulation)
        print(staircases_info[current_staircase]["direction"])
        response = int(input("0 or 1: "))
        print("SUCCESSFUL stimulation")
        staircases[current_staircase].reversal(response)
        staircases[current_staircase].within_block_successful_counter += 1
        staircases[current_staircase].last_response = response
        staircases[current_staircase].trial += 1

        staircases[current_staircase].XupYdownFixedStepSizesTrackingAlgorithm(
            rule_down, rule_up, size_down, size_up, 0.2
        )


        ############################
        ################# Save data
        ############################
        staircases[current_staircase].clampBoundary(
            min_bound_staircase, max_bound_staircase
        )

        printme(
            f"Staircase {current_staircase} reversals: {staircases[current_staircase].reversals}"
        )

        staircases[current_staircase].within_block_counter += 1
        name_staircase_file = f"online_back_up_staircase_{staircases_info[current_staircase]['direction']}"
        staircases[current_staircase].saveStaircase(path_data, name_staircase_file)
