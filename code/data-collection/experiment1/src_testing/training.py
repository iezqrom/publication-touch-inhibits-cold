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

from classes_conds import ConditionsHandler
from classes_conds import *
from failing import *
from saving_data import *
from rand_cons import *
import wave

import threading
import pandas as pd
import numpy as np

if __name__ == "__main__":
    try:
        # Grab ports
        ports = grabPorts()
        print(ports.ports)
        # Grab subject number
        # subject_n = getSubjNumDec()
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
            "position" "watson_listens",
            "watson_hypothesises",
            "watson_confidence",
        )
        temp_data_writer, temp_file, temp_file_name = tempSaving(
            path_data, list(data.keys())
        )

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

        os.system("clear")

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

        delta_stimulation = 1.2
        time_out = 12

        ### AUDIO
        speaker = initSpeak()
        speech_to_text = initSpeech2Text()
        beep_speech_success = Sound(1000, 0.2)
        beep = Sound(400, 40)
        channels = 1
        fs = 44100

        # Recover information
        globals.positions = csvtoDictZaber(path_data)
        globals.grid = csvToDictGridAll(path_data)
        globals.haxes = csvToDictHaxes(path_data)
        globals.ROIs = csvToDictROIAll(path_data)
        globals.PanTilts = csvToDictPanTiltsAll(path_data)
        subject_n = txtToVar(path_data, "temp_subj_n")

        print(f"\nPositions Zabers: {globals.positions}\n")
        print(f"\nROIs: {globals.ROIs}\n")
        print(f"\nPanTilts: {globals.PanTilts}\n")
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

        ## RANDOMISE POSITIONS
        trials_per_cell = 1
        cells = [1, 3, 7, 9]
        coldnocold = [1, 0, 1, 0]

        init_rep = np.repeat(cells, trials_per_cell)
        np.random.shuffle(init_rep)
        final_order = exp_rand(init_rep, check_linear, restart=10)

        park_touch = {"x": 0, "y": 0, "z": 209974}
        movetostartZabersConcu(
            zabers, "tactile", list(reversed(["x", "y", "z"])), pos=park_touch
        )

        familiar_stimulation = False
        while not familiar_stimulation:
            np.random.shuffle(coldnocold)
            np.random.shuffle(final_order)
            for i, p in enumerate(final_order):
                if keyboard.is_pressed("s"):
                    homingZabersConcu(zabers, globals.haxes)

                    movetostartZabersConcu(
                        zabers,
                        "colther",
                        list(reversed(globals.haxes["colther"])),
                        pos=globals.dry_ice_pos,
                    )

                    globals.stimulus = 5

                    try:
                        arduino_syringe.arduino.write(
                            struct.pack(">B", globals.stimulus)
                        )
                        time.sleep(1)
                        arduino_syringe.arduino.write(
                            struct.pack(">B", globals.stimulus)
                        )
                    except Exception as e:
                        errorloc(e)
                        os.system("clear")
                        input("\n\n Press enter when Arduino is fixed...")
                        arduino_syringe = ArdUIno(usb_port=1, n_modem=1)
                        arduino_syringe.arduino.flushInput()
                        arduino_syringe.arduino.write(
                            struct.pack(">B", globals.stimulus)
                        )
                        time.sleep(1)
                        arduino_syringe.arduino.write(
                            struct.pack(">B", globals.stimulus)
                        )

                    globals.stimulus = 0

                    try:
                        arduino_syringe.arduino.write(
                            struct.pack(">B", globals.stimulus)
                        )
                    except Exception as e:
                        errorloc(e)
                        os.system("clear")
                        input("\n\n Press enter when Arduino is fixed...")
                        arduino_syringe = ArdUIno(usb_port=1, n_modem=1)
                        arduino_syringe.arduino.flushInput()
                        arduino_syringe.arduino.write(
                            struct.pack(">B", globals.stimulus)
                        )

                    printme("Close shutter")

                    os.system("clear")

                    while True:
                        ans = input(
                            '\nPosition syringe pusher ("d" for down / "u" for up / "e" to move on)  '
                        )
                        os.system("clear")
                        if ans:
                            if ans[-1] in ("e", "d", "u"):
                                if ans[-1] == "e":
                                    break
                                elif ans[-1] == "d":
                                    try:
                                        globals.stimulus = 6
                                        arduino_syringe.arduino.write(
                                            struct.pack(">B", globals.stimulus)
                                        )
                                    except Exception as e:
                                        errorloc(e)
                                elif ans[-1] == "u":
                                    try:
                                        globals.stimulus = 5
                                        arduino_syringe.arduino.write(
                                            struct.pack(">B", globals.stimulus)
                                        )
                                    except Exception as e:
                                        errorloc(e)
                            else:
                                printme("Only 'd', 'u' and 'e' are valid responses")

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
                    input(
                        "\n\n Press enter when participant is comfortable and ready\n\n"
                    )

                    cam.setShutterManual()
                    cam.performManualff()
                    printme(
                        "Performing shutter refresh and taking a 10-second break\nto let the thermal image stabilise"
                    )
                    time.sleep(10)

                    try:
                        arduino_syringe.arduino.write(
                            struct.pack(">B", globals.stimulus)
                        )
                    except Exception as e:
                        errorloc(e)
                        arduino_syringe = ArdUIno(usb_port=1, n_modem=1)
                        arduino_syringe.arduino.flushInput()

                    try:
                        globals.stimulus = 6
                        arduino_syringe.arduino.write(
                            struct.pack(">B", globals.stimulus)
                        )
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

                # preliminary trial
                p = str(final_order[i])
                cROI = globals.ROIs[p]
                printme(f"Grid position: {p}")

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
                        movetostartZabersConcu(
                            zabers, k, list(reversed(v)), pos=globals.grid[k][str(p)]
                        )
                        time.sleep(0.1)

                # Feedback closure + TONE
                file_path = path_videos + "/" + f"training_stair_trial{i+1}_pos{p}"

                ev = threading.Event()
                beep_trial = threading.Thread(target=beep.play, args=[ev])
                beep_trial.name = "Beep thread"
                beep_trial.daemon = True
                beep_trial.start()

                # STIMULATION
                presentabsent = coldnocold[i]

                if presentabsent == 0:
                    stimulus = 3
                    time_out = np.random.randint(
                        1, 5, size=1
                    ) + np.random.random_sample(1)
                elif presentabsent == 1:
                    stimulus = 2
                    time_out = 12

                print(delta_stimulation)
                cam.targetTempAutoDiffDelta(
                    file_path,
                    delta_stimulation,
                    cROI,
                    20,
                    arduino_syringe,
                    stimulus,
                    time_out,
                    ev,
                )
                globals.delta = 0

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
                qs = "Was there any temperature change during the tone?"  # el pavo dice: Was there any temperature change during the tone?
                speak(speaker, qs)

                globals.answer = None
                globals.answered = None

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
                globals.stimulus = 4

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

                if keyboard.is_pressed("p"):
                    os.system("clear")
                    input("\n\n Press enter when panic is over...")

            homingZabersConcu(zabers, globals.haxes)
            while True:
                ans = input("\nAre we happy with the familiarisation phase? (y/n)  ")
                if ans[-1] in ("y", "n"):
                    if ans[-1] == "y":
                        # print(ans)
                        familiar_stimulation = True
                        break
                    else:
                        break

                else:
                    printme("Only 'y' and 'n' are valid responses")

    except Exception as e:
        errorloc(e)
        # temp_file.close()
        rootToUser(path_day, path_anal, path_data, path_figs, path_videos, path_audios)
        changeNameTempFile(path_data)
        terminateSpeechRecognition(stream, audio, audio_source)

        globals.stimulus = 0
        arduino_syringe.arduino.write(struct.pack(">B", globals.stimulus))

    except KeyboardInterrupt:
        print("Keyboard Interrupt")
        # temp_file.close()
        changeNameTempFile(path_data)
        terminateSpeechRecognition(stream, audio, audio_source)
        rootToUser(path_day, path_anal, path_data, path_figs, path_videos, path_audios)

        globals.stimulus = 0
        arduino_syringe.arduino.write(struct.pack(">B", globals.stimulus))
