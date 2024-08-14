from classes_arduino import ArdUIno
from classes_arduino import *
from grabPorts import grabPorts
from failing import *
from saving_data import *
import matplotlib.pyplot as plt
from classes_audio import Sound
from classes_speech import *
from index_funcs import *
from classes_colther import Zaber
from classes_colther import *
from classes_camera import TherCam
from saving_data import *
from classes_text import TextIO
from grabPorts import grabPorts
import simpleaudio as sa
from classes_tharnal import *
from classes_conds import ConditionsHandler
from classes_conds import *
from failing import *
from saving_data import *
from rand_cons import *
import wave

import threading
import pandas as pd
import numpy as np
import pickle

if __name__ == "__main__":
    try:
        # Grab ports
        ports = grabPorts()
        print(ports.ports)
        subject_n = getSubjNumDec()

        # Check experimental situation, check and/or create folders
        situ = parsing_situation()
        path_day, path_anal, path_figs, path_data, path_videos, path_audios = mkpaths(
            situ, subject_n
        )

        # Data stuff
        data = buildDict(
            "subject",
            "trial",
            "delta_stimulation",
            "delta_target",
            "reversed",
            "response",
            "time_delay",
            "stimulus_time",
            "position",
            "staircase",
            "watson_listens",
            "watson_hypothesises",
            "watson_confidence",
            "failed",
        )
        temp_data_writer, temp_file, temp_file_name = tempSaving(
            path_data, list(data.keys())
        )

        pattern_data_failed = f"data_failedstaircase.*\.csv"
        patternc_data_failed = re.compile(pattern_data_failed)
        print(patternc_data_failed)
        names_data_failed = []

        for filename in os.listdir(f"{path_data}"):
            # print(filename)
            if patternc_data_failed.match(filename):
                # print(filename)
                name, form = filename.split(".")
                names_data_failed.append(name)
            else:
                continue

        names_data_failed.sort(key=natural_keys)
        # printme(names_data_failed)

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

        #### LOAD HARDWARE
        # Zabers
        zabers = set_up_big_three(globals.axes)
        homingZabersConcu(zabers, globals.haxes)

        # Arduino syringe motors
        arduino_syringe = ArdUIno(usb_port=1, n_modem=1)
        arduino_syringe.arduino.flushInput()

        # Arduino dimmers
        arduino_dimmer = ArdUIno(usb_port=1, n_modem=24)
        arduino_dimmer.arduino.flushInput()

        # Arduino PanTilt
        arduino_pantilt = ArdUIno(usb_port=1, n_modem=23)
        arduino_pantilt.arduino.flushInput()

        # Thermal camera
        cam = TherCam()
        cam.startStream()
        cam.setShutterManual()

        movetostartZabersConcu(
            zabers,
            "colther",
            list(reversed(globals.haxes["colther"])),
            pos=globals.dry_ice_pos,
        )

        # Dry ice load
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

        # Subject in position
        os.system("clear")
        input("\n\n Press enter when participant is comfortable and ready\n\n")

        # Shutter refresh and stabilisation
        cam.setShutterManual()
        cam.performManualff()
        printme(
            "Performing shutter refresh and taking a 10-second break\nto let the thermal image stabilise"
        )
        time.sleep(10)

        # STAIRCASE PARAMETERS
        step_up = 0.14
        step_down = 0.1
        reversals_correction = 1

        if os.path.exists(f"{path_data}/online_back_up_staircases.pkl"):
            printme("RECOVERING staircase dict")
            backup_staircase_file = open(
                f"{path_data}/online_back_up_staircases.pkl", "rb"
            )
            staircases = pickle.load(backup_staircase_file)
            backup_staircase_file.close()
            printme(staircases)
        else:
            staircases = {
                "staircase_1": {
                    "reversals": 0,
                    "first_ramp": True,
                    "tracker": 0,
                    "delta_stimulation": 1.2,
                    "delta_target": 1.2,
                    "reversed_bool": False,
                    "last_response": None,
                    "trial": 1,
                    "direction": "down",
                },
                "staircase_2": {
                    "reversals": 0,
                    "first_ramp": True,
                    "tracker": 0,
                    "delta_stimulation": 0.2,
                    "delta_target": 0.2,
                    "reversed_bool": False,
                    "last_response": None,
                    "trial": 1,
                    "direction": "up",
                },
            }

        last_response = None

        if situ == "ex":
            stop_reversals = 8
            time_out = 12

        elif situ == "tb":
            stop_reversals = 4
            time_out = 12

        positions_list = []
        limit = 2
        # failed_trial = False

        # Recover information
        globals.positions = csvtoDictZaber(path_data)
        globals.grid = csvToDictGridAll(path_data)
        globals.haxes = csvToDictHaxes(path_data)
        globals.ROIs = csvToDictROIAll(path_data)
        globals.PanTilts = csvToDictPanTiltsAll(path_data)
        subject_n = txtToVar(path_data, "temp_subj_n")

        print(f"\nPositions Zabers: {globals.positions}\n")
        print(f"\nPanTilts: {globals.PanTilts}\n")
        print(f"\nROIs: {globals.ROIs}\n")
        print(f"\nHaxes: {globals.haxes}")
        print(f"\nGrids Colther: {globals.grid['colther']}\n")
        print(f"\nGrids Camera: {globals.grid['camera']}\n")
        print(f"\nGrids Tactile: {globals.grid['tactile']}\n")
        time.sleep(5)

        try:
            globals.stimulus = 6
            arduino_syringe.arduino.write(struct.pack(">B", globals.stimulus))
            globals.stimulus = 4
        except Exception as e:
            errorloc(e)

        shakeShutter(arduino_syringe, 5)

        ### AUDIO
        speaker = initSpeak()
        speech_to_text = initSpeech2Text()
        beep_speech_success = Sound(1000, 0.2)
        beep = Sound(400, 40)
        channels = 1
        fs = 44100

        park_touch = {"x": 0, "y": 0, "z": 209974}
        movetostartZabersConcu(
            zabers, "tactile", list(reversed(["x", "y", "z"])), pos=park_touch
        )

        # get positions with constraints online
        while staircases["staircase_1"]["reversals"] < (
            stop_reversals + reversals_correction
        ) or staircases["staircase_2"]["reversals"] < (
            stop_reversals + reversals_correction
        ):
            # Interblock
            if keyboard.is_pressed("s"):
                homingZabersConcu(zabers, globals.haxes)

                movetostartZabersConcu(
                    zabers,
                    "colther",
                    list(reversed(globals.haxes["colther"])),
                    pos=globals.dry_ice_pos,
                )

                try:
                    arduino_syringe.arduino.write(struct.pack(">B", globals.stimulus))
                except Exception as e:
                    errorloc(e)
                    os.system("clear")
                    input("\n\n Press enter when Arduino is fixed...")
                    arduino_syringe = ArdUIno(usb_port=1, n_modem=1)
                    arduino_syringe.arduino.flushInput()
                    arduino_syringe.arduino.write(struct.pack(">B", globals.stimulus))

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

            moveZabersUp(zabers, ["colther"])

            try:
                globals.stimulus = 6
                arduino_syringe.arduino.write(struct.pack(">B", globals.stimulus))
                globals.stimulus = 4
            except Exception as e:
                errorloc(e)

            # Prepare position ZABERS
            while True:
                randomly_chosen_next = np.random.choice(
                    list(globals.coor_cells.keys()), 1, replace=True
                )[0]
                if len(positions_list) == 0:
                    positions_list.append(randomly_chosen_next)
                    break
                else:
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

            p = randomly_chosen_next
            cROI = globals.ROIs[p]

            # Feedback closure + TONE
            ev = threading.Event()
            beep_trial = threading.Thread(target=beep.play, args=[ev])
            beep_trial.name = "Beep thread"
            beep_trial.daemon = True
            beep_trial.start()

            # STIMULATION
            stimulus = 2
            while True:
                ss = np.random.choice([1, 2])
                if staircases[f"staircase_{str(ss)}"]["reversals"] >= (
                    stop_reversals + reversals_correction
                ):
                    print(f"staircase_{str(ss)} is finished")
                else:
                    # print(f'On staircase_{str(ss)}')
                    break

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

            for k, v in reversed(globals.haxes.items()):
                if k == "tactile":
                    printme("Not moving touch")
                else:
                    if (
                        k == "colther"
                        and staircases[f"staircase_{str(ss)}"]["delta_stimulation"]
                        > 0.9
                    ):
                        stimu_position = globals.grid[k][str(p)].copy()
                        stimu_position["z"] -= 14110
                    else:
                        stimu_position = globals.grid[k][str(p)]

                    movetostartZabersConcu(
                        zabers, k, list(reversed(v)), pos=stimu_position
                    )
                    time.sleep(0.1)

            printme(stimu_position)
            printme(f"Staircase: {str(ss)}")
            printme(f"Trial number: {staircases[f'staircase_{str(ss)}']['trial']}")
            printme(f"Grid position: {p}")
            printme(
                f"Delta stimulation: {staircases[f'staircase_{str(ss)}']['delta_stimulation']}"
            )

            file_path = (
                path_videos
                + "/"
                + f"staircase{str(ss)}_trial{staircases[f'staircase_{str(ss)}']['trial']}_pos{p}"
            )

            cam.targetTempAutoDiffDelta(
                file_path,
                staircases[f"staircase_{str(ss)}"]["delta_stimulation"],
                cROI,
                20,
                arduino_syringe,
                stimulus,
                time_out,
                ev,
            )

            globals.delta = 0

            # ############### Terminate trial
            sa.stop_all()

            # RESPONSE
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
            # print(end)

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

            response = globals.answered

            staircases[f"staircase_{str(ss)}"]["reversed_bool"] = False
            print(cam.shutter_open_time)

            if cam.shutter_open_time < 0.4:
                cam.failed_trial = True

            if cam.failed_trial == False:
                print("SUCCESSFUL stimulation")
                if (
                    staircases[f"staircase_{str(ss)}"]["last_response"] != response
                    and staircases[f"staircase_{str(ss)}"]["last_response"] is not None
                ):
                    staircases[f"staircase_{str(ss)}"]["reversals"] += 1
                    staircases[f"staircase_{str(ss)}"]["reversed_bool"] = True

            time.sleep(1)

            if cam.failed_trial == True:
                this_trial_n = 0
            else:
                this_trial_n = staircases[f"staircase_{str(ss)}"]["trial"]

            ### SAVE RESPONSES
            tempRowToWrite = [
                subject_n,
                this_trial_n,
                staircases[f"staircase_{str(ss)}"]["delta_stimulation"],
                staircases[f"staircase_{str(ss)}"]["delta_target"],
                staircases[f"staircase_{str(ss)}"]["reversed_bool"],
                response,
                delay,
                cam.shutter_open_time,
                p,
                ss,
                globals.listened,
                globals.hypothesis,
                globals.confidence,
                cam.failed_trial,
            ]
            data = appendDataDict(data, tempRowToWrite)
            print(data)
            temp_data_writer.writerow(tempRowToWrite)

            # Tracking algorithm
            if not cam.failed_trial:
                if not staircases[f"staircase_{str(ss)}"]["first_ramp"]:
                    if response == 0:
                        staircases[f"staircase_{str(ss)}"]["tracker"] = 0

                    elif response == 1:
                        staircases[f"staircase_{str(ss)}"]["tracker"] += 1

                    if staircases[f"staircase_{str(ss)}"]["tracker"] == 3:
                        staircases[f"staircase_{str(ss)}"]["delta_target"] = (
                            staircases[f"staircase_{str(ss)}"]["delta_target"]
                            - step_down
                        )
                        staircases[f"staircase_{str(ss)}"]["tracker"] = 0

                    elif staircases[f"staircase_{str(ss)}"]["tracker"] == 0:
                        staircases[f"staircase_{str(ss)}"]["delta_target"] = (
                            staircases[f"staircase_{str(ss)}"]["delta_target"] + step_up
                        )

                else:
                    if staircases[f"staircase_{str(ss)}"]["direction"] == "down":
                        if response == 0:
                            staircases[f"staircase_{str(ss)}"]["delta_target"] = (
                                staircases[f"staircase_{str(ss)}"]["delta_target"]
                                + step_up
                            )
                            staircases[f"staircase_{str(ss)}"]["first_ramp"] = False
                            printme("Trigger algorithm")
                        elif response == 1:
                            staircases[f"staircase_{str(ss)}"]["delta_target"] = (
                                staircases[f"staircase_{str(ss)}"]["delta_target"]
                                - step_down
                            )

                    elif staircases[f"staircase_{str(ss)}"]["direction"] == "up":
                        if response == 0:
                            staircases[f"staircase_{str(ss)}"]["delta_target"] = (
                                staircases[f"staircase_{str(ss)}"]["delta_target"]
                                + step_up
                            )
                        elif response == 1:
                            staircases[f"staircase_{str(ss)}"]["delta_target"] = (
                                staircases[f"staircase_{str(ss)}"]["delta_target"]
                                - step_down
                            )
                            staircases[f"staircase_{str(ss)}"]["first_ramp"] = False
                            printme("Trigger algorithm")

            if staircases[f"staircase_{str(ss)}"]["delta_target"] > 1.2:
                staircases[f"staircase_{str(ss)}"]["delta_stimulation"] = 1.2
            elif staircases[f"staircase_{str(ss)}"]["delta_target"] < 0.2:
                staircases[f"staircase_{str(ss)}"]["delta_stimulation"] = 0.2
            else:
                staircases[f"staircase_{str(ss)}"]["delta_stimulation"] = staircases[
                    f"staircase_{str(ss)}"
                ]["delta_target"]

            printme(staircases[f"staircase_{str(ss)}"]["delta_stimulation"])
            printme(staircases[f"staircase_{str(ss)}"]["delta_target"])

            printme(f"Staircase 1 reversals: {staircases['staircase_1']['reversals']}")
            printme(f"Staircase 2 reversals: {staircases['staircase_2']['reversals']}")

            if cam.failed_trial == False:
                staircases[f"staircase_{str(ss)}"]["last_response"] = response

            globals.stimulus = 4

            try:
                arduino_syringe.arduino.write(struct.pack(">B", globals.stimulus))
            except Exception as e:
                errorloc(e)
                os.system("clear")
                input("\n\n Press enter when Arduino is fixed...")
                arduino_syringe = ArdUIno(usb_port=1, n_modem=1)
                arduino_syringe.arduino.flushInput()

            audio_file_name = f"{path_audios}/response_staircase{str(ss)}_trial{staircases[f'staircase_{str(ss)}']['trial']}_wans{globals.answered}_conf{globals.confidence}.wav"
            wf = wave.open(audio_file_name, "wb")
            wf.setnchannels(channels)
            wf.setsampwidth(2)
            wf.setframerate(fs)
            wf.writeframes(b"".join(globals.frames))
            wf.close()

            globals.frames = []

            start_trial_pos = {
                "colther": {
                    "x": globals.positions["colther"]["x"],
                    "y": globals.positions["colther"]["y"] - 90000,
                    "z": globals.positions["colther"]["z"] - 90000,
                },
                "camera": {
                    "x": globals.positions["camera"]["x"],
                    "y": globals.positions["camera"]["y"],
                    "z": globals.positions["camera"]["z"] - 90000,
                },
                "tactile": {
                    "x": globals.positions["tactile"]["x"],
                    "y": globals.positions["tactile"]["y"] - 90000,
                    "z": globals.positions["tactile"]["z"] - 50000,
                },
            }

            # MOVE TO NEW GRID POSITION
            for k, v in globals.haxes.items():
                if k == "tactile":
                    printme("Not moving tactile for mol")
                else:
                    movetostartZabersConcu(
                        zabers, k, list(reversed(v)), pos=start_trial_pos[k]
                    )
                    time.sleep(0.1)

            if cam.failed_trial == False:
                staircases[f"staircase_{str(ss)}"]["trial"] += 1

            backup_staircase_file = open(
                f"{path_data}/online_back_up_staircases.pkl", "wb"
            )
            pickle.dump(staircases, backup_staircase_file)
            backup_staircase_file.close()

            if keyboard.is_pressed("p"):
                os.system("clear")
                input("\n\n Press enter when panic is over...")

        homingZabersConcu(zabers, globals.haxes)

        saveZaberPos("temp_zaber_pos", path_data, globals.positions)
        saveROI("temp_ROI", path_data, globals.centreROI)
        saveHaxesAll(path_data, globals.haxes)
        name_subj_file = f"data_staircase_subj"
        saveIndv(name_subj_file, path_data, data)
        changeNameTempFile(path_data)
        rootToUser(path_day, path_anal, path_data, path_figs, path_videos, path_audios)

        if os.path.exists(f"{path_data}/online_back_up_staircases.pkl"):
            os.remove(f"{path_data}/online_back_up_staircases.pkl")

    except Exception as e:
        errorloc(e)
        rootToUser(path_day, path_anal, path_data, path_figs, path_videos, path_audios)
        temp_file.close()
        changeNameTempFile(path_data, outcome="failedstaircase")
        terminateSpeechRecognition(stream, audio, audio_source)

        globals.stimulus = 0
        arduino_syringe.arduino.write(struct.pack(">B", globals.stimulus))

    except KeyboardInterrupt:
        print("Keyboard Interrupt")
        rootToUser(path_day, path_anal, path_data, path_figs, path_videos, path_audios)
        temp_file.close()
        changeNameTempFile(path_data, outcome="failedstaircase")
        terminateSpeechRecognition(stream, audio, audio_source)

        globals.stimulus = 0
        arduino_syringe.arduino.write(struct.pack(">B", globals.stimulus))
