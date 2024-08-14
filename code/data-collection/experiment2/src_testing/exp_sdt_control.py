import sys
sys.path.append('..')

from arduino import tryexceptArduino
from grabPorts import grabPorts
from failing import (
    getNames,
    recoverData,
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
    txtToVar,
    saveIndvVar,
    handleItiSave,
    copyDict,
    getSubjNumDec,
    booleanValueModify
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
    TouchingUntouching,
    grabNextPosition,
    deltaTemperature,
    controlSyringeTrial,
    controlLightTrial,
    controlSoundTrial,
    readInputKeyPad
)
from audio import Sound
from index_funcs import parsingSituation, mkpaths
from camera import TherCam
from text import printme
from local_classes import gridData, TimeStamps, TemperatureData
from conds import sdtSetup
from rand_cons import expRand, checkTwoD

import threading

from globals import (
    pantilts,
    delay_data_display,
    haxes,
    coor_cells,
    lower_bound_delay,
    higher_bound_delay,
    limit_restimulation,
    tone_stimulus_frequency,
    time_out,
    number_human_mapping,
    control_info
)

##### READY-MADE CODE
import threading
import numpy as np
import os
import time
import simpleaudio as sa
import keyboard

if __name__ == "__main__":

    try:
        ports = grabPorts()
        print(ports.ports)

        spaceLeftWarning()
        grid_data = gridData(haxes, pantilts, 'colther')

        situ, day, _ = parsingSituation()
        subject_n = getSubjNumDec(day=day)
        path_day, path_anal, path_figs, path_data, path_videos, path_audios = mkpaths(
            situ, numdaysubj = subject_n, folder_name=day
        )
        path_day_bit = path_day.rsplit("/", 3)[-1]
        saveIndvVar("./src_testing", path_day_bit, "temp_folder_name")

        # Data stuff
        data = buildDict(
            "trial",
            "interactor",
            "cooling",
            "response",
            "time_delay",
            "reaction_time",
            "stimulus_time",
            "position",
            "failed",
            "n_block",
            "within_block_counter"
        )
        temp_data = copyDict(data)
        
        failed_name = "data_failedsdtcontrol"

        # Check whether there's data and recover it
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

        thermalCalibration(zabers, arduinos["syringe"], arduinos["dimmer"], cam)

        if os.path.exists(f"{path_data}/online_back_up_conds.npy") and os.path.exists(
            f"{path_data}/online_back_up_location.npy"
        ):
            stimulations = np.load(f"{path_data}/online_back_up_conds.npy")
            final_order = np.load(f"{path_data}/online_back_up_location.npy")

            stimulations = stimulations.tolist()
            final_order = final_order.tolist()
            printme("GRABBING CONDS AND STIMULATION LOCATIONS FROM TEMP FILES")
        else:
            stimulations = sdtSetup(control_info[situ]["number_trials"], control_info[situ]["number_conditions"])
            init_pos = np.arange(1, 9.01, 1)
            init_rep = np.repeat(init_pos, (control_info[situ]["number_repetitions"] * 2))
            np.random.shuffle(init_rep)
            final_order = expRand(
                    init_rep, checkTwoD, restart = control_info[situ]["restart_n"], coor_cells = coor_cells
            )

        # Recover information
        grid_data.positions["camera"] = csvToDictGridIndv(path_data, "temp_grid_camera.csv")
        grid_data.positions["colther"] = csvToDictGridIndv(path_data, "temp_grid_colther.csv")
        grid_data.positions["tactile"] = csvToDictGridIndv(path_data, "temp_grid_tactile.csv")
        rois = csvToDictROIAll(path_data)
        pantilts = csvToDictPanTiltsAll(path_data)
        delta = txtToVar(path_data, "temp_delta")

        delta_target = round(float(delta), 2)

        print(f"\nROIs: {rois}\n")
        print(f"\nPanTilts: {pantilts}\n")
        print(f"\nHaxes: {haxes}")
        print(f"\nGrids Colther: {grid_data.positions['colther']}\n")
        print(f"\nGrids Camera: {grid_data.positions['camera']}\n")
        print(f"\nGrids Tactile: {grid_data.positions['tactile']}\n")
        time.sleep(delay_data_display)
        print(f"\nPeak delta temperature {delta_target}\n")
        time.sleep(5)

        tone_stimulus = Sound(tone_stimulus_frequency, 40)

        tryexceptArduino(arduinos["syringe"], 6)

        block_n = 1
        within_block_counter = 1
        trial_positions = []
        stimulus_present_trial_duration = []

        if os.path.exists(f"{path_data}/trial_n.npy"):
            trial_n = int(np.load(f"{path_data}/trial_n.npy"))
            printme("Grabbing trial number from failed temporal trial_n file")
            print(trial_n)
        else:
            trial_n = 1

        for fo in final_order[-3:]:
            trial_positions.append(fo)

        while len(stimulations) > 0:
            if keyboard.is_pressed("s"):
                (
                    _,
                    block_n,
                    within_block_counter,
                ) = triggerHandleReload(
                    zabers = zabers,
                    arduinos = arduinos,
                    cam = cam,
                    n_block = block_n,
                    within_block_counter = within_block_counter,
                )
                
            if len(final_order) > 0:
                int_p = final_order.pop(0)
                grid_data.current_roi = str(int_p)
            else:
                grid_data.current_roi, trial_positions = grabNextPosition(
                    trial_positions, limit_restimulation, pantilts
                )

            temp_data["position"] = grid_data.current_roi
            centre_roi = rois[temp_data["position"]]

            np.random.shuffle(stimulations)
            stimuli_present_absent = stimulations.pop(0)
            temp_data["cooling"] = stimuli_present_absent[1]
            temp_data["interactor"] = stimuli_present_absent[0]

            printme(f"\nTrial number: {trial_n}\n")
            printme(f"Grid position: {int_p}")
            printme(f"Fixed ROI for this position: {centre_roi}")
            printme(f"Stimuli present: {stimuli_present_absent}")

            tryexceptArduino(arduinos["syringe"], 6)

            event_cooling = threading.Event()
            event_interactor = threading.Event()

            events = {"cooling": event_cooling, "interactor": event_interactor}

            itiZaberDanceIn(zabers, arduinos["pantilt"], pantilts, grid_data, touch = True)

            ######### Feedback closure + TONE

            if temp_data["cooling"] == 0:
                trial_type = "close_random_shutter"
                if len(stimulus_present_trial_duration) == 0:
                    max_stimulation_duration = np.random.randint(
                        1, 5, size = 1
                    ) + np.random.random_sample(1)
                else:
                    max_stimulation_duration = np.random.choice(stimulus_present_trial_duration)

            elif temp_data["cooling"] == 1:
                trial_type = "open_random_shutter"
                max_stimulation_duration = time_out[situ]

            #######################################
            # Start threads
            #######################################
            light_trial_thread = threading.Thread(
                target = controlLightTrial,
                args = [arduinos, events["cooling"]],
                daemon = True,
                name = "Light thread",
            )
            light_trial_thread.start()


            thread_arduino_syringe = threading.Thread(
                target = controlSyringeTrial,
                args = [arduinos["syringe"], number_human_mapping[trial_type], events["cooling"]],
                daemon = True,
                name = "Arduino syringe thread",
            )
            thread_arduino_syringe.start()

            if stimuli_present_absent[0] == 1:
                touch_height = grid_data.positions['tactile'][temp_data["position"]]["z"]
                interactor_thread = threading.Thread(
                    target = TouchingUntouching,
                    args = [zabers, touch_height, events["interactor"]],
                    daemon = True,
                    name = "Touch thread",
                    )
                interactor_thread.start()

            if stimuli_present_absent[0] == 2:
                interactor_thread = threading.Thread(
                    target = controlSoundTrial,
                    args = [tone_stimulus, events["interactor"]],
                    daemon = True,
                    name = "Sound thread",
                )
                interactor_thread.start()

            #######################################
            # Start trial
            #######################################
            time_stamps = TimeStamps(max_stimulation_duration)
            temperature_data = TemperatureData(number_human_mapping[trial_type], delta_target)

            time_now = time.localtime()
            time_now_string = time.strftime("%H_%M_%S", time_now)
            file_name = f"controlsdt_trial{trial_n}_pos{temp_data['position']}_time{time_now_string}"

            cam.grabDataFunc(
                deltaTemperature,
                time_stamps = time_stamps,
                temperature_data = temperature_data,
                file_name = file_name,
                roi_coordinates = centre_roi,
                events = events,
            )

            # ############### Terminate trial
            if time_stamps.shutter_open_duration < 0.4:
                temperature_data.failed = True

            if not temperature_data.failed:

                temp_data["time_delay"] = np.random.uniform(
                    lower_bound_delay, higher_bound_delay
                )
                time.sleep(temp_data["time_delay"])

                temp_data["response"], temp_data["reaction_time"] = readInputKeyPad()

                print("SUCCESSFUL stimulation")
                stimulus_present_trial_duration.append(time_stamps.shutter_open_duration)

                # Save audio
                audio_file_name = f"controlsdt_trial{str(trial_n)}_pos{temp_data['position']}"

            else:
                temp_data["response"] = 3
                time_response_end = 0
                temp_data["reaction_time"] = 0
                temp_data["time_delay"] = 0
                stimulations.insert(0, stimuli_present_absent)
                np.random.shuffle(stimulations)

            # Dictionary saving
            temp_data["failed"] = temperature_data.failed
            temp_data["n_block"] = block_n
            temp_data["within_block_counter"] = within_block_counter
            temp_data["stimulus_time"] = time_stamps.shutter_open_duration
            temp_data["trial"] = trial_n

            if temp_data["cooling"] == 0:
                # remove the video file
                os.remove(f"{cam.pathset}/{file_name}.hdf5")

            trial_values = list(temp_data.values())
            data = handleItiSave(
                trial_values, data, path_data, temp_file_name
            )

            trial_n += 1
            within_block_counter += 1
            print("Trial number: ", trial_n)
            print("Total number of stimulations: ", len(stimulations))
            print("Stimulations left: ", len(stimulations))
            np.save(f"{path_data}/online_back_up_conds", stimulations)
            np.save(f"{path_data}/online_back_up_loca", final_order)
            np.save(f"{path_data}/trial_n", trial_n)
            
            itiZaberDanceAway(zabers)
            panicButton()
            homeButton(zabers, arduinos["pantilt"])

        # apendAll(path_data, 1, data)

        name_subj_file = f"data_controlsdt_subj"
        saveIndv(name_subj_file, path_data, data)
        changeNameTempFile(path_data, outcome="success")
        if os.path.exists(f"./src_testing/temp_folder_name.txt"):
            os.remove(f"./src_testing/temp_folder_name.txt")

        saveIndvVar("./src_testing", path_day_bit, "temp_folder_name")

        booleanValueModify(path_data, "to_analyse", True)

        rootToUser([path_day, path_anal, path_data, path_figs, path_videos, path_audios])
        
        name_temp_online = ["trial_n", "online_back_up_conds", "online_back_up_loca"]
        for nto in name_temp_online:
            if os.path.exists(f"{path_data}/{nto}.npy"):
                os.remove(f"{path_data}/{nto}.npy")

        closeEnvelope(zabers, arduinos)

    except Exception as e:
        # check whether stream exists
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
