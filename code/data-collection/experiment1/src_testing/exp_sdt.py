################################ Import stuff ################################
# %%
from classes_arduino import ArdUIno
from classes_arduino import *
from classes_colther import Zaber
from classes_colther import *
from classes_camera import TherCam
from saving_data import *
from classes_text import TextIO
from grabPorts import grabPorts
from classes_audio import Sound
from classes_conds import ConditionsHandler
from classes_conds import *
from classes_testData import TestingDataHandler
from failing import *
from saving_data import *
from classes_speech import *
from classes_audio import Sound
from classes_tharnal import *
import subprocess
import os
import globals
import time
import threading
import random
import numpy as np
import simpleaudio as sa
import keyboard
import math
from datetime import date
import pyttsx3
import psutil
from rand_cons import *
import argparse
import wave
import random

from index_funcs import *
import keyboard

if __name__ == "__main__":

    try:
        ports = grabPorts()
        print(ports.ports)
        subject_n = getSubjNumDec()

        situ = parsing_situation()
        path_day, path_anal, path_figs, path_data, path_videos, path_audios = mkpaths(
            situ, subject_n
        )

        path_day_bit = path_day.rsplit("/", 3)[-1]
        saveIndvVar("./src_testing", path_day_bit, "temp_folder_name")
        # Data stuff
        data = buildDict(
            "subject",
            "trial",
            "responses",
            "touch",
            "cold",
            "time_delay",
            "stimulus_time",
            "position",
            "watson_listens",
            "watson_hypothesises",
            "watson_confidence",
            "failed",
        )
        temp_data_writer, temp_file, temp_file_name = tempSaving(
            path_data, list(data.keys())
        )

        pattern_data_failed = f"data_failedsdt.*\.csv"
        patternc_data_failed = re.compile(pattern_data_failed)
        print(patternc_data_failed)
        names_data_failed = []

        for filename in os.listdir(f"{path_data}"):
            print(filename)
            if patternc_data_failed.match(filename):
                name, form = filename.split(".")
                names_data_failed.append(name)
            else:
                continue

        names_data_failed.sort(key=natural_keys)
        printme(names_data_failed)

        if len(names_data_failed) > 0:
            printme("Recovering data from temporal failed attempt")
            recovered_data = pd.read_csv(f"{path_data}/{names_data_failed[-1]}.csv")
            lsrd = recovered_data.to_dict("list")
            data = {key: lsrd[key] for key, value in lsrd.items()}
            printme(data)

            for di, ds in enumerate(data["subject"]):
                pastTemprow = []
                # print(ds)
                keys = data.keys()
                for k in keys:
                    pastTemprow.append(data[k][di])

                temp_data_writer.writerow(pastTemprow)

        zabers = set_up_big_three(globals.axes)
        homingZabersConcu(zabers, globals.haxes)

        arduino_syringe = ArdUIno(usb_port=1, n_modem=1)
        arduino_syringe.arduino.flushInput()

        arduino_dimmer = ArdUIno(usb_port=1, n_modem=24)
        arduino_dimmer.arduino.flushInput()

        arduino_pantilt = ArdUIno(usb_port=1, n_modem=23)
        arduino_pantilt.arduino.flushInput()

        cam = TherCam()
        cam.startStream()
        cam.setShutterManual()

        movetostartZabersConcu(
            zabers,
            "colther",
            list(reversed(globals.haxes["colther"])),
            pos=globals.dry_ice_pos,
        )

        if os.path.exists(f"{path_data}/online_back_up_conds.npy") and os.path.exists(
            f"{path_data}/online_back_up_loca.npy"
        ):
            stims = np.load(f"{path_data}/online_back_up_conds.npy")
            final_order = np.load(f"{path_data}/online_back_up_loca.npy")

            stims = stims.tolist()
            final_order = final_order.tolist()
            printme("GRABBING CONDS AND STIMULATION LOCATIONS FROM TEMP FILES")
        else:
            if situ == "ex":
                n_trials = 54 * 2
                conditions = 2
                stims = sdt_setup(n_trials, conditions)

                init_pos = np.arange(1, 9.01, 1)
                init_rep = np.repeat(init_pos, (6 * 2))
                # init_rep = np.repeat(init_pos, 5)
                np.random.shuffle(init_rep)
                final_order = exp_rand(
                    init_rep, check_twoD, restart=800, coor_cells=globals.coor_cells
                )

            elif situ == "tb":
                n_trials = 9
                conditions = 2
                stims = sdt_setup(n_trials, conditions)

                init_pos = np.arange(1, 9.01, 1)
                init_rep = np.repeat(init_pos, 2)
                np.random.shuffle(init_rep)
                final_order = exp_rand(
                    init_rep, check_twoD, restart=100, coor_cells=globals.coor_cells
                )

        globals.stimulus = 0
        arduino_syringe.arduino.write(struct.pack(">B", globals.stimulus))
        printme("Close shutter")

        globals.stimulus = 7
        arduino_syringe.arduino.write(struct.pack(">B", globals.stimulus))
        globals.stimulus = 4

        reLoad(arduino_syringe)

        homingZabersConcu(zabers, globals.haxes)
        os.system("clear")

        # Lamp: warm-up skin
        globals.lamp = 1

        try:
            arduino_dimmer.arduino.write(struct.pack(">B", globals.lamp))
        except Exception as e:
            errorloc(e)
            arduino_dimmer = ArdUIno(usb_port=1, n_modem=24)
            arduino_dimmer.arduino.flushInput()
            print("DIMMER WRITE FAILED")

        input("\n\n Press enter when lamp time is over\n\n")
        globals.lamp = 0

        try:
            arduino_dimmer.arduino.write(struct.pack(">B", globals.lamp))
        except Exception as e:
            errorloc(e)
            arduino_dimmer = ArdUIno(usb_port=1, n_modem=24)
            arduino_dimmer.arduino.flushInput()
            print("DIMMER WRITE FAILED")

        os.system("clear")
        input("\n\n Press enter when participant is comfortable and ready\n\n")

        cam.setShutterManual()
        cam.performManualff()
        printme(
            "Performing shutter refresh and taking a 10-second break\nto let the thermal image stabilise"
        )
        time.sleep(10)

        # Recover information
        globals.positions = csvtoDictZaber(path_data)
        globals.grid = csvToDictGridAll(path_data)
        globals.haxes = csvToDictHaxes(path_data)
        globals.ROIs = csvToDictROIAll(path_data)
        globals.PanTilts = csvToDictPanTiltsAll(path_data)
        delta = txtToVar(path_data, "temp_delta")
        subject_n = txtToVar(path_data, "temp_subj_n")

        target_delta = round(float(delta), 2)

        print(f"\nPositions Zabers: {globals.positions}\n")
        print(f"\nROIs: {globals.ROIs}\n")
        print(f"\nPanTilts: {globals.PanTilts}\n")
        print(f"\nHaxes: {globals.haxes}")
        print(f"\nGrids Colther: {globals.grid['colther']}\n")
        print(f"\nGrids Camera: {globals.grid['camera']}\n")
        print(f"\nGrids Tactile: {globals.grid['tactile']}\n")
        print(f"\nPeak delta temperature {target_delta}\n")
        time.sleep(5)

        try:
            globals.stimulus = 6
            arduino_syringe.arduino.write(struct.pack(">B", globals.stimulus))
            globals.stimulus = 4
        except Exception as e:
            errorloc(e)

        shakeShutter(arduino_syringe, 5)

        speaker = initSpeak()
        speech_to_text = initSpeech2Text()
        beep_speech_success = Sound(1000, 0.2)
        beep = Sound(400, 40)
        channels = 1
        fs = 44100

        # # Temp file init
        response = []

        time_sti_pres = []

        globals.stimulus = 4
        n_nofailed_trials = 0
        positions_list = []
        limit = 2
        to_repeat = []

        if os.path.exists(f"{path_data}/trial_n.npy"):
            trials_counter = int(np.load(f"{path_data}/trial_n.npy"))
            printme("Grabbing trial number from failed temporal trial_n file")
            print(trials_counter)
        else:
            trials_counter = 0

        for fo in final_order[-3:]:
            positions_list.append(fo)

        while len(stims) > 0:
            if keyboard.is_pressed("s"):
                homingZabersConcu(zabers, globals.haxes)

                movetostartZabersConcu(
                    zabers,
                    "colther",
                    list(reversed(globals.haxes["colther"])),
                    pos=globals.dry_ice_pos,
                )

                globals.stimulus = 0

                try:
                    arduino_syringe.arduino.write(struct.pack(">B", globals.stimulus))
                except Exception as e:
                    errorloc(e)
                    os.system("clear")
                    input("\n\n Press enter when Arduino is fixed...")
                    arduino_syringe = ArdUIno(usb_port=1, n_modem=1)
                    arduino_syringe.arduino.flushInput()

                printme("Close shutter")

                reLoad(arduino_syringe)

                homingZabersConcu(zabers, globals.haxes)
                os.system("clear")

                globals.lamp = 1

                try:
                    arduino_dimmer.arduino.write(struct.pack(">B", globals.lamp))
                except Exception as e:
                    errorloc(e)
                    os.system("clear")
                    input("\n\n Press enter when Arduino Dimmer is fixed...")
                    arduino_dimmer = ArdUIno(usb_port=1, n_modem=24)
                    arduino_dimmer.arduino.flushInput()

                input("\n\n Press enter when lamp time is over\n\n")
                globals.lamp = 0

                try:
                    arduino_dimmer.arduino.write(struct.pack(">B", globals.lamp))
                except Exception as e:
                    errorloc(e)
                    os.system("clear")
                    input("\n\n Press enter when Arduino Dimmer is fixed...")
                    arduino_dimmer = ArdUIno(usb_port=1, n_modem=24)
                    arduino_dimmer.arduino.flushInput()

                os.system("clear")
                input("\n\n Press enter when participant is comfortable and ready\n\n")

                cam.setShutterManual()
                cam.performManualff()
                printme(
                    "Performing shutter refresh and taking a 10-second break\nto let the thermal image stabilise"
                )
                time.sleep(10)

                try:
                    arduino_syringe.arduino.write(struct.pack(">B", globals.stimulus))
                except Exception as e:
                    errorloc(e)
                    arduino_syringe = ArdUIno(usb_port=1, n_modem=1)
                    arduino_syringe.arduino.flushInput()

                try:
                    globals.stimulus = 6
                    arduino_syringe.arduino.write(struct.pack(">B", globals.stimulus))
                    globals.stimulus = 4
                except Exception as e:
                    errorloc(e)

                shakeShutter(arduino_syringe, 5)
                printme("Resuming experiment...")
                globals.stimulus = 4

            if len(final_order) > 0:
                int_p = final_order.pop(0)
                p = str(int_p)
            else:
                while True:
                    randomly_chosen_next = np.random.choice(
                        list(globals.coor_cells.keys()), 1, replace=True
                    )[0]

                    backwards = []
                    for bi in np.arange(1, limit + 0.1, 1):
                        if len(positions_list) < bi:
                            break

                        current_check = check_twoD(
                            positions_list, randomly_chosen_next, bi, globals.coor_cells
                        )
                        backwards.append(current_check)

                    if np.all(backwards):
                        positions_list.append(randomly_chosen_next)
                        break
                    else:
                        print("WRONG VALUE!")

                int_p = randomly_chosen_next
                p = str(int_p)

            cROI = globals.ROIs[p]

            if int_p == 1:
                touch = globals.positions["tactile"]["z"] + globals.grid_heights["1"]
            elif int_p == 2:
                touch = globals.positions["tactile"]["z"] + globals.grid_heights["2"]
            elif int_p == 3:
                touch = globals.positions["tactile"]["z"] + globals.grid_heights["3"]
            elif int_p == 4:
                touch = globals.positions["tactile"]["z"] + globals.grid_heights["4"]
            elif int_p == 5:
                touch = globals.positions["tactile"]["z"] + globals.grid_heights["5"]
            elif int_p == 6:
                touch = globals.positions["tactile"]["z"] + globals.grid_heights["6"]
            elif int_p == 7:
                touch = globals.positions["tactile"]["z"] + globals.grid_heights["7"]
            elif int_p == 8:
                touch = globals.positions["tactile"]["z"] + globals.grid_heights["8"]
            elif int_p == 9:
                touch = globals.positions["tactile"]["z"] + globals.grid_heights["9"]

            printme(f"\nTrial number + 1: {trials_counter + 1}\n")
            printme(f"Grid position: {int_p}")
            printme(f"Fixed ROI for this position: {cROI}")

            try:
                globals.stimulus = 6
                arduino_syringe.arduino.write(struct.pack(">B", globals.stimulus))
                globals.stimulus = 4
            except Exception as e:
                os.system("clear")
                errorloc(e)
                input("\n\n Press enter when Arduino is fixed...")
                arduino_syringe = ArdUIno(usb_port=1, n_modem=1)
                arduino_syringe.arduino.flushInput()

            try:
                arduino_pantilt.arduino.write(struct.pack(">B", 8))
                time.sleep(globals.keydelay)
                arduino_pantilt.arduino.write(
                    struct.pack(
                        ">BBB",
                        globals.PanTilts[p][0],
                        globals.PanTilts[p][1],
                        globals.PanTilts[p][2],
                    )
                )
            except Exception as e:
                os.system("clear")
                errorloc(e)
                input("\n\n Press enter when Arduino is fixed...")
                arduino_pantilt = ArdUIno(usb_port=1, n_modem=23)
                arduino_pantilt.arduino.flushInput()
                time.sleep(1)
                arduino_pantilt.arduino.write(struct.pack(">B", 8))
                time.sleep(globals.keydelay)
                arduino_pantilt.arduino.write(
                    struct.pack(
                        ">BBB",
                        globals.PanTilts[p][0],
                        globals.PanTilts[p][1],
                        globals.PanTilts[p][2],
                    )
                )

            movetostartZabersConcu(
                zabers,
                "camera",
                list(reversed(globals.haxes["camera"])),
                pos=globals.grid["camera"][p],
            )
            movetostartZabers(
                zabers,
                "tactile",
                list(globals.haxes["tactile"]),
                pos=globals.grid["tactile"][p],
            )
            movetostartZabersConcu(
                zabers,
                "colther",
                list(reversed(globals.haxes["colther"])),
                pos=globals.grid["colther"][p],
            )

            ######### Feedback closure + TONE
            file_path = path_videos + "/" + f"sdt_trial{trials_counter + 1}_pos{p}"

            ev = threading.Event()
            beep_trial = threading.Thread(target=beep.play, args=[ev])
            beep_trial.name = "Beep thread"
            beep_trial.daemon = True
            beep_trial.start()

            np.random.shuffle(stims)
            s = stims.pop(0)

            if s[1] == 0:
                stimulus = 3
                if len(time_sti_pres) == 0:
                    time_out = np.random.randint(
                        1, 5, size=1
                    ) + np.random.random_sample(1)
                else:
                    time_out = np.random.choice(time_sti_pres)

            elif s[1] == 1:
                stimulus = 2
                if situ == "ex":
                    time_out = 12
                elif situ == "tb":
                    time_out = 6

            ev_touch = None

            if s[0] == 1:
                ev_touch = threading.Event()

                def UpDown():
                    movetostartZabers(zabers, "tactile", "z", touch, ev_touch)
                    printme("Touching...")

                    ev_touch.clear()

                    movetostartZabers(
                        zabers, "tactile", "z", globals.positions["tactile"], ev_touch
                    )
                    printme("Untouching...")

                touch_thread = Thread(target=UpDown)
                touch_thread.name = "Touch thread"
                touch_thread.daemon = True
                touch_thread.start()
            #####

            cam.targetTempAutoDiffDelta(
                file_path,
                target_delta,
                cROI,
                20,
                arduino_syringe,
                stimulus,
                time_out,
                ev,
                ev_touch,
            )

            if cam.shutter_open_time < 0.4:
                cam.failed_trial = True

            if s[1] == 1 and not cam.failed_trial:
                if cam.shutter_open_time:
                    time_sti_pres.append(cam.shutter_open_time)

            globals.delta = 0

            # ############### Terminate trial
            sa.stop_all()

            # Initiliase Watson
            audio = startAudioWatson()
            audio_source, q = audioInstance()
            stream = openStream(audio, q)
            recognize_yes_no = Thread(
                target=recognize_yes_no_weboscket,
                args=[speech_to_text, audio_source, globals.answer],
            )
            recognize_yes_no.name = "Speech recognition thread"
            recognize_yes_no.start()

            stream.start_stream()

            start = time.time()

            globals.answer = None
            globals.answered = None

            delay = np.random.uniform(0.2, 2)

            time.sleep(delay)

            beep_speech_success.play()

            end = time.time() - start

            timer_watson = time.time()

            while True:
                time_out_watson = time.time() - timer_watson
                if time_out_watson > 10:
                    globals.answered = 2
                    break
                elif globals.answer == 1:
                    if (
                        globals.answered == 1
                        or globals.answered == 0
                        or time_out_watson > 10
                    ):
                        print("Answered", globals.answered)
                        break

            terminateSpeechRecognition(stream, audio, audio_source)

            beep_speech_success.play()

            response.append(globals.answered)

            tempRowToWrite = [
                subject_n,
                trials_counter,
                globals.answered,
                s[0],
                s[1],
                delay,
                cam.shutter_open_time,
                p,
                globals.listened,
                globals.hypothesis,
                globals.confidence,
                cam.failed_trial,
            ]

            # Dictionary saving
            data = appendDataDict(data, tempRowToWrite)
            print(data)

            globals.stimulus = 4

            try:
                arduino_syringe.arduino.write(struct.pack(">B", globals.stimulus))
            except Exception as e:
                errorloc(e)
                os.system("clear")
                input("\n\n Press enter when Arduino is fixed...")
                arduino_syringe = ArdUIno(usb_port=1, n_modem=1)
                arduino_syringe.arduino.flushInput()

            # Temporal saving
            temp_data_writer.writerow(tempRowToWrite)

            audio_file_name = f"{path_audios}/response_sdt_trial{trials_counter}_wans{globals.answered}_conf{globals.confidence}.wav"
            wf = wave.open(audio_file_name, "wb")
            wf.setnchannels(channels)
            wf.setsampwidth(2)
            wf.setframerate(fs)
            wf.writeframes(b"".join(globals.frames))
            wf.close()

            globals.frames = []

            for k, v in globals.haxes.items():
                iti_pos = globals.grid[k][p].copy()
                if k == "colther":
                    iti_pos["z"] = 0
                elif k == "tactile":
                    iti_pos["z"] = 240000

                if k != "camera":
                    movetostartZabersConcu(zabers, k, list(reversed(v)), pos=iti_pos)
                    time.sleep(0.1)

            if not cam.failed_trial:
                n_nofailed_trials += 1
                printme("Stimulation successful")
            else:
                stims.insert(0, s)
                np.random.shuffle(stims)
                printme("Stimulation failed")

            trials_counter += 1

            print(n_nofailed_trials)
            print(trials_counter)
            print(len(stims))
            print(len(final_order))
            np.save(f"{path_data}/online_back_up_conds", stims)
            np.save(f"{path_data}/online_back_up_loca", final_order)
            np.save(f"{path_data}/trial_n", trials_counter)

            if keyboard.is_pressed("p"):
                os.system("clear")
                input("\n\n Press enter when panic is over...")

        homingZabersConcu(zabers, globals.haxes)

        apendAll(path_data, 1, data)

        name_subj_file = f"data_subj"
        saveIndv(name_subj_file, path_data, data)

        rootToUser(path_day, path_anal, path_data, path_figs, path_videos, path_audios)

        changeNameTempFile(path_data, outcome="success")

        name_temp_online = ["trial_n", "online_back_up_conds", "online_back_up_loca"]
        for nto in name_temp_online:
            if os.path.exists(f"{path_data}/{nto}.npy"):
                os.remove(f"{path_data}/{nto}.npy")

    except Exception as e:
        errorloc(e)
        rootToUser(path_day, path_anal, path_data, path_figs, path_videos, path_audios)
        temp_file.close()
        changeNameTempFile(path_data, outcome="failedsdt")
        terminateSpeechRecognition(stream, audio, audio_source)

        globals.stimulus = 0
        arduino_syringe.arduino.write(struct.pack(">B", globals.stimulus))

    except KeyboardInterrupt:
        print("Keyboard Interrupt")
        rootToUser(path_day, path_anal, path_data, path_figs, path_videos, path_audios)
        temp_file.close()
        changeNameTempFile(path_data, outcome="failedsdt")
        terminateSpeechRecognition(stream, audio, audio_source)

        globals.stimulus = 0
        arduino_syringe.arduino.write(struct.pack(">B", globals.stimulus))
