import sys
sys.path.append('..')
from arduino import tryexceptArduino, movePanTilt
from zabers import movetostartZabersConcu
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
    copyDict,
    handleItiSave,
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
    controlSyringeTrial
)
from audio import Sound
from index_funcs import parsingSituation, mkpaths
from camera import TherCam
from speech import (
    terminateSpeechRecognition,
)
from local_classes import gridData, TimeStamps, TemperatureData
from speech import initSpeak, speak
from globals import (
    pantilts,
    delay_data_display,
    haxes,
    step_sizes,
    lower_bound_delay,
    higher_bound_delay,
    limit_restimulation,
    tone_trial_frequency,
    time_out,
    number_human_mapping,
    question,
    park_touch
)

import threading
import numpy as np
import os
import time
import keyboard
import random

if __name__ == "__main__":
    try:
        # Grab ports
        ports = grabPorts()
        print(ports.ports)

        spaceLeftWarning()
        grid_data = gridData(haxes, pantilts, 'colther')

        # Check experimental situation, check and/or create folders
        situ, day, _ = parsingSituation()
        subject_n = getSubjNumDec(day=day)
        path_day, path_anal, path_figs, path_data, path_videos, path_audios = mkpaths(
            situ, numdaysubj=subject_n, folder_name=day
        )
        path_day_bit = path_day.rsplit("/", 3)[-1]

        # Data stuff
        data = buildDict(
            "trial",
            "delta_stimulation",
            "response",
            "listened",
            "hypothesis",
            "confidence",
            "reaction_time",
            "time_delay",
            "stimulus_time",
            "position",
            "failed"
        )
        temp_data = copyDict(data)

        failed_name = f"data_trainingfailed"

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

        trial_positions = []

        # Recover information
        grid_data.positions["camera"] = csvToDictGridIndv(path_data, "temp_grid_camera.csv")
        grid_data.positions["colther"] = csvToDictGridIndv(path_data, "temp_grid_colther.csv")
        grid_data.positions["tactile"] = csvToDictGridIndv(path_data, "temp_grid_tactile.csv")
        rois = csvToDictROIAll(path_data)
        pantilts = csvToDictPanTiltsAll(path_data)
        subject_n = txtToVar(path_data, "temp_subj_n")

        print(f"\nrois: {rois}\n")
        print(f"\nPanTilts: {pantilts}\n")
        print(f"\nHaxes: {haxes}")
        print(f"\nGrids Colther: {grid_data.positions['colther']}\n")
        print(f"\nGrids Camera: {grid_data.positions['camera']}\n")
        print(f"\nGrids Tactile: {grid_data.positions['tactile']}\n")
        time.sleep(delay_data_display)

        ### AUDIO
        tone_trial = Sound(tone_trial_frequency, 40)

        ## WATSON
        speaker, speech_to_text = initWatson()

        training_temp = 1.5

        trials_training = ["close_random_shutter", "open_random_shutter", "open_random_shutter",  "close_random_shutter"]
        trial_n = 1

        movetostartZabersConcu(zabers, "tactile", ["x", "z"], pos = park_touch)

        speaker = initSpeak()

        # get positions with constraints online
        while trials_training != []:
            # Interblock
            if keyboard.is_pressed("s"):
                (
                    _,
                    _,
                    _,
                ) = triggerHandleReload(
                    zabers=zabers,
                    arduinos = arduinos,
                    cam=cam,
                    n_block = 0,
                    within_block_counter = 0,
                )
            
            trial_type = trials_training.pop(0)
            tryexceptArduino(arduinos["syringe"], 6)

            # Prepare position ZABERS
            grid_data.current_roi, trial_positions = grabNextPosition(
                trial_positions, limit_restimulation, pantilts
            )
            temp_data["position"] = grid_data.current_roi
            centre_roi = rois[temp_data["position"]]

            print('centre_roi', centre_roi)

            # Feedback closure + TONE
            event_stimulation = threading.Event()
            events = {"cooling": event_stimulation}
            tone_trial_thread = threading.Thread(
                target = tone_trial.play,
                args = [events["cooling"]],
                daemon = True,
                name = "Tone thread",
            )
            tone_trial_thread.start()

            movePanTilt(arduinos["pantilt"], pantilts[temp_data["position"]])


            grid_data.positions["colther"][temp_data["position"]]["z"] = deltaToZaberHeight(
                training_temp,
                grid_data.positions,
                temp_data["position"],
                step_sizes,
            )

            print("HEIGHT IS:", grid_data.positions["colther"][temp_data["position"]]["z"])

            itiZaberDanceIn(
                zabers, arduinos["pantilt"], pantilts, grid_data
            )

            # get hour, minutes and seconds for file name as a string
            time_now = time.localtime()
            time_now_string = time.strftime("%H_%M_%S", time_now)

            file_name = f"training_n{trial_n}_pos{temp_data['position']}_{trial_type}_{time_now_string}"

            thread_arduino_syringe = threading.Thread(
                target = controlSyringeTrial,
                args = [arduinos["syringe"], number_human_mapping[trial_type], events["cooling"]],
                daemon = True,
                name = "Arduino syringe thread",
            )
            thread_arduino_syringe.start()

            if trial_type == "open_random_shutter":
                max_stimulation_duration = time_out[situ]
            elif trial_type == "close_random_shutter":
                max_stimulation_duration = random.uniform(0.4, time_out[situ])

            print(f"max_stimulation_duration: {max_stimulation_duration}")

            time_stamps = TimeStamps(max_stimulation_duration)
            temperature_data = TemperatureData(number_human_mapping[trial_type], training_temp)

            cam.grabDataFunc(
                deltaTemperature,
                time_stamps = time_stamps,
                temperature_data = temperature_data,
                file_name = file_name,
                roi_coordinates = centre_roi,
                events = events,
            )

            ### ANSWER
            if time_stamps.shutter_open_duration < 0.4:
                temperature_data.failed = True
            
            print(f"Failed: {temperature_data.failed}")
            temp_data["failed"] = temperature_data.failed
            temp_data["stimulus_time"] = time_stamps.shutter_open_duration

            if not temperature_data.failed:
                stream, audio, audio_source, recognize_yes_no, frames = startWatson(
                    speech_to_text
                )

                temp_data["time_delay"] = np.random.uniform(
                    lower_bound_delay, higher_bound_delay
                )
                speak(speaker, question)
                time.sleep(temp_data["time_delay"])

                waitForWatson(recognize_yes_no)

                temp_data["response"] = recognize_yes_no.answered
                temp_data["trial"] = trial_n
                temp_data["confidence"] = recognize_yes_no.confidence
                temp_data["listened"] = recognize_yes_no.listened
                temp_data["hypothesis"] = recognize_yes_no.hypothesis
                temp_data['reaction_time'] = recognize_yes_no.time_out_watson

                terminateSpeechRecognition(stream, audio, audio_source)

                # Save audio
                audio_file_name = f"training_n{trial_n}_pos{temp_data['position']}"
                saveAudio(frames, path_audios, audio_file_name)
                trial_n += 1

            else:
                # put trial back in the list
                trials_training.append(trial_type)
                temp_data["response"] = 3
                time_response_end = 0
                temp_data["trial"] = 0
                temp_data["confidence"] = 0
                temp_data["listened"] = 0
                temp_data["hypothesis"] = 0
                temp_data['reaction_time'] = 0

            if trial_type == "close_random_shutter":
                temp_data["delta_stimulation"] = 0
            elif trial_type == "open_random_shutter":
                temp_data["delta_stimulation"] = training_temp

            trial_values = list(temp_data.values())
            data = handleItiSave(
                trial_values, data, path_data, temp_file_name
            )
            itiZaberDanceAway(zabers)

            panicButton()
            homeButton(zabers, arduinos["pantilt"])

        name_subj_file = f"data_training_subj"
        saveIndv(name_subj_file, path_data, data)
        changeNameTempFile(path_data, outcome="success")
        if os.path.exists(f"./src_testing/temp_folder_name.txt"):
            os.remove(f"./src_testing/temp_folder_name.txt")
        saveIndvVar("./src_testing", path_day_bit, "temp_folder_name")

        rootToUser([path_day, path_anal, path_data, path_figs, path_videos, path_audios])

        closeEnvelope(zabers, arduinos)

    except Exception as e:
        if stream is not None:
            terminateSpeechRecognition(stream, audio, audio_source)
        triggeredException(
            path_day=path_day,
            path_anal=path_anal,
            path_data=path_data,
            path_figs=path_figs,
            path_videos=path_videos,
            zabers=zabers,
            arduinos = arduinos,
            e=e,
            outcome=f"failedtraining",
        )

    except KeyboardInterrupt:
        if stream is not None:
            terminateSpeechRecognition(stream, audio, audio_source)
        triggeredException(
            path_day=path_day,
            path_anal=path_anal,
            path_data=path_data,
            path_figs=path_figs,
            path_videos=path_videos,
            zabers=zabers,
            arduinos = arduinos,
            outcome=f"failedfailedtraining",
        )
