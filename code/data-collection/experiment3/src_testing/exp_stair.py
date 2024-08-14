import sys
sys.path.append('..')
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
    deltaTemperature,
    controlSyringeTrial,
    controlLightTrial,
    movetostartZabersConcu,
    readInputKeyPad
)
from audio import Sound
from index_funcs import parsingSituation, mkpaths
from camera import TherCam
from text import printme
from local_classes import gridData, TimeStamps, TemperatureData

from staircases import Staircase
import threading

from globals import (
    pantilts,
    delay_data_display,
    haxes,
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
import keyboard

if __name__ == "__main__":
    try:
        # Grab ports
        ports = grabPorts()
        print(ports.ports)

        spaceLeftWarning()
        grid_data = gridData(haxes, pantilts, 'colther')

        # Check experimental situation, check and/or create folders
        situ, day, _ = parsingSituation()
        subject_n = getSubjNumDec(day = day)

        path_day, path_anal, path_figs, path_data, path_videos, path_audios = mkpaths(
            situ, numdaysubj = subject_n, folder_name = day
        )
        path_day_bit = path_day.rsplit("/", 3)[-1]

        # Data stuff
        data = buildDict(
            "trial",
            "delta_stimulation",
            "delta_target",
            "reversed",
            "response",
            "reaction_time",
            "time_delay",
            "stimulus_time",
            "position",
            "failed",
            "n_block",
            "within_block_counter"
        )
        temp_data = copyDict(data)

        staircases = []

        failed_name = f"data_failedstaircase"

        # Check whether data and recover
        names_data_failed = getNames(path_data, f"{failed_name}.*\.csv")
        name_temp_file = createTempName(failed_name)

        _, temp_file, temp_file_name = tempSaving(
            path_data, list(data.keys()), temp_file_name=name_temp_file
        )

        data = recoverData(names_data_failed, path_data, data)
        rewriteRecoveredData(data, path_data, temp_file_name)

        ################### LOAD HARDWARE ##################
        ### ARDUINOS & ZABERS
        (
            zabers,
            arduinos
        ) = arduinos_zabers()

        ### THERMAL CAMERA
        cam = TherCam()
        cam.startStream()
        cam.setShutterManual()
        cam.setPathName(path_videos)

        thermalCalibration(zabers, arduinos["syringe"], arduinos["dimmer"], arduinos["pantilt"], cam)

        name_staircase_file = f"online_back_up_staircase_up"
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

        printme(staircases)
        trial_positions = []

        # Recover information
        grid_data.positions["camera"] = csvToDictGridIndv(path_data, "temp_grid_camera.csv")
        grid_data.positions["colther"] = csvToDictGridIndv(path_data, "temp_grid_colther.csv")
        grid_data.positions["tactile"] = csvToDictGridIndv(path_data, "temp_grid_tactile.csv")
        rois = csvToDictROIAll(path_data)
        pantilts = csvToDictPanTiltsAll(path_data)

        print(f"\nROIs: {rois}\n")
        print(f"\nPanTilts: {pantilts}\n")
        print(f"\nHaxes: {haxes}")
        print(f"\nGrids Colther: {grid_data.positions['colther']}\n")
        print(f"\nGrids Camera: {grid_data.positions['camera']}\n")
        print(f"\nGrids Tactile: {grid_data.positions['tactile']}\n")
        time.sleep(delay_data_display)

        movetostartZabersConcu(zabers, "tactile", ["x", "z"], pos = park_touch)

        # get positions with constraints online
        while (
            staircases[0].reversals < staircases[0].total_reversals
            or staircases[1].reversals < staircases[1].total_reversals
        ):
            # Interblock
            if keyboard.is_pressed("s"):
                (
                    _,
                    staircases[0].block,
                    staircases[0].within_block_counter,
                ) = triggerHandleReload(
                    zabers=zabers,
                    arduinos = arduinos,
                    cam=cam,
                    n_block=staircases[0].block,
                    within_block_counter=staircases[0].within_block_counter,
                )

            tryexceptArduino(arduinos["syringe"], 6)

            # Prepare position ZABERS
            grid_data.current_roi, trial_positions = grabNextPosition(
                trial_positions, limit_restimulation, pantilts
            )
            temp_data["position"] = grid_data.current_roi
            cROI = rois[temp_data["position"]]

            while True:
                current_staircase = np.random.choice([0, 1])
                if (
                    staircases[current_staircase].reversals
                    >= staircases[current_staircase].total_reversals
                ):
                    print(f"staircase_{str(current_staircase)} is finished")
                else:
                    break

            grid_data.positions["colther"]["z"] = deltaToZaberHeight(
                staircases[current_staircase].stimulation,
                grid_data.positions,
                temp_data["position"],
                step_sizes,
            )

            print("HEIGHT IS:", grid_data.positions["colther"]["z"])

            itiZaberDanceIn(zabers, arduinos["pantilt"], pantilts, grid_data)

            printme(f"Trial number: {staircases[current_staircase].trial}")
            printme(f"Grid position: {temp_data['position']}")
            printme(f"Delta stimulation: {staircases[current_staircase].stimulation}")
            printme(
                f"Delta tracked stimulation: {staircases[current_staircase].tracked_stimulation}"
            )
            printme(f"Block number: {staircases[current_staircase].block}")
            printme(
                f"Within block trial counter: {staircases[current_staircase].within_block_counter}"
            )
            printme(
                f"Within block SUCCESSFUL trial counter: {staircases[current_staircase].within_block_successful_counter}"
            )

            # Feedback closure + TONE
            event_cooling = threading.Event()
            events = {"cooling": event_cooling}
            
            light_trial_thread = threading.Thread(
                target = controlLightTrial,
                args = [arduinos, events["cooling"]],
                daemon = True,
                name = "Light thread",
            )
            light_trial_thread.start()

            thread_arduino_syringe = threading.Thread(
                target = controlSyringeTrial,
                args = [arduinos["syringe"], number_human_mapping["open_random_shutter"], events["cooling"]],
                daemon = True,
                name = "Arduino syringe thread",
            )
            thread_arduino_syringe.start()

            # ############### Start trial
            time_stamps = TimeStamps(time_out[situ])
            temperature_data = TemperatureData(number_human_mapping["open_random_shutter"], staircases[current_staircase].stimulation)

            time_now = time.localtime()
            time_now_string = time.strftime("%H_%M_%S", time_now)
            file_name = f"staircase{str(current_staircase)}_trial{staircases[current_staircase].trial}_pos{temp_data['position']}_time{time_now_string}"

            cam.grabDataFunc(
                deltaTemperature,
                time_stamps = time_stamps,
                temperature_data = temperature_data,
                file_name = file_name,
                roi_coordinates = cROI,
                events = events,
            )

            ### ANSWER
            if time_stamps.shutter_open_duration < 0.4:
                temperature_data.failed = True

            print(f"Failed: {temperature_data.failed}")
            temp_data["failed"] = temperature_data.failed
            temp_data["stimulus_time"] = time_stamps.shutter_open_duration
            
            if not temperature_data.failed:

                temp_data["time_delay"] = np.random.uniform(
                    lower_bound_delay, higher_bound_delay
                )
                time.sleep(temp_data["time_delay"])

                temp_data["response"], temp_data["reaction_time"] = readInputKeyPad()

                if temp_data["response"] in [0, 1]:
                    print("SUCCESSFUL stimulation")
                    staircases[current_staircase].reversal(temp_data["response"])
                    staircases[current_staircase].within_block_successful_counter += 1
                    temp_data["trial"] = staircases[current_staircase].trial
                    staircases[current_staircase].last_response = int(temp_data["response"])
                    staircases[current_staircase].trial += 1

                    staircases[current_staircase].XupYdownFixedStepSizesTrackingAlgorithm(
                        rule_down, rule_up, size_down, size_up, 0.2
                    )
                else:
                    temp_data["trial"] = 0

            else:
                temp_data["response"] = 3
                time_response_end = 0
                temp_data["trial"] = 0
                temp_data["confidence"] = 0
                temp_data["listened"] = 0
                temp_data["hypothesis"] = 0
                temp_data["reaction_time"] = 0
                temp_data["time_delay"] = 0

            ############################
            ################# Save data
            ############################
            temp_data["n_block"] = staircases[current_staircase].block
            temp_data["delta_stimulation"] = staircases[current_staircase].stimulation
            temp_data["delta_target"] = staircases[
                current_staircase
            ].tracked_stimulation
            temp_data["reversed"] = staircases[current_staircase].reversed_bool
            temp_data["within_block_counter"] = staircases[
                current_staircase
            ].within_block_counter


            trial_values = list(temp_data.values())
            data = handleItiSave(
                trial_values, data, path_data, temp_file_name
            )

            staircases[current_staircase].clampBoundary(
                min_bound_staircase, max_bound_staircase
            )

            printme(
                f"Staircase 0 reversals: {staircases[0].reversals} // Staircase 1 reversals: {staircases[1].reversals}"
            )

            tryexceptArduino(arduinos["syringe"], 4)

            staircases[current_staircase].within_block_counter += 1
            name_staircase_file = f"online_back_up_staircase_{staircases_info[current_staircase]['direction']}"
            staircases[current_staircase].saveStaircase(path_data, name_staircase_file)

            itiZaberDanceAway(zabers)

            panicButton()
            homeButton(zabers, arduinos["pantilt"])

        name_subj_file = f"data_staircase_subj"
        saveIndv(name_subj_file, path_data, data)
        changeNameTempFile(path_data, outcome="success")
        if os.path.exists(f"./src_testing/temp_folder_name.txt"):
            os.remove(f"./src_testing/temp_folder_name.txt")
        
        saveIndvVar("./src_testing", path_day_bit, "temp_folder_name")
        rootToUser([path_day, path_anal, path_data, path_figs, path_videos, path_audios])

        closeEnvelope(zabers, arduinos)

    except Exception as e:
        triggeredException(
            path_day = path_day,
            path_anal = path_anal,
            path_data = path_data,
            path_figs = path_figs,
            path_videos = path_videos,
            zabers = zabers,
            arduinos = arduinos,
            e = e,
            outcome = failed_name,
        )

    except KeyboardInterrupt:
        triggeredException(
            path_day = path_day,
            path_anal = path_anal,
            path_data = path_data,
            path_figs = path_figs,
            path_videos = path_videos,
            zabers = zabers,
            arduinos = arduinos,
            outcome = failed_name,
        )
