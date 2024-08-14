################################ Import stuff ################################
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
from classes_testData import TestingDataHandler
from failing import *
from classes_speech import *
from classes_audio import Sound
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
from index_funcs import *

if __name__ == "__main__":
    try:
        ports = grabPorts()
        print(ports.ports)
        situ = parsing_situation()
        subject_n = getSubjNumDec()

        path_day, path_anal, path_figs, path_data, path_videos, path_audios = mkpaths(
            situ, subject_n
        )

        # Recover data
        D = float(txtToVar(path_data, "temp_distance_metre"))

        for i in globals.z_ds:
            globals.z_ds[i] = D - (globals.ds[i] + globals.ds_offset[i])

        printme("D")
        print(D)
        printme("Z ds")
        print(globals.z_ds)

        for k, v in globals.haxes.items():
            z_steps = z_axis_pos(globals.z_ds[k], globals.step_sizes[k])
            globals.z_ds[k] = z_steps
            globals.positions[k]["z"] = globals.z_ds[k]
            print(f"{k} {globals.z_ds[k]}")

        saveHaxesAll(path_data, globals.haxes)
        saveZaberPos("temp_zaber_pos", path_data, globals.positions)

        print(f"\nPositions Zabers: {globals.positions}\n")
        print(f"\nHaxes: {globals.haxes}")

        zabers = set_up_big_three(globals.axes)
        homingZabersConcu(zabers, globals.haxes)

        arduino_syringe = ArdUIno(usb_port=1, n_modem=1)
        arduino_syringe.arduino.flushInput()

        arduino_dimmer = ArdUIno(usb_port=1, n_modem=24)
        arduino_dimmer.arduino.flushInput()

        arduino_pantilt = ArdUIno(usb_port=1, n_modem=23)
        arduino_pantilt.arduino.flushInput()

        cam = TherCam(vminT=31, vmaxT=36)
        cam.startStream()
        cam.setShutterManual()

        movetostartZabersConcu(
            zabers,
            "colther",
            list(reversed(globals.haxes["colther"])),
            pos=globals.dry_ice_pos,
        )
        os.system("clear")

        # Dry ice load
        globals.stimulus = 7
        arduino_syringe.arduino.write(struct.pack(">B", globals.stimulus))
        globals.stimulus = 4

        reLoad(arduino_syringe)

        # input('\n\n Press enter to home Colther Zaber\n\n')
        homingZabersConcu(zabers, globals.haxes)
        os.system("clear")

        globals.lamp = 1

        try:
            arduino_dimmer.arduino.write(struct.pack(">B", globals.lamp))
        except Exception as e:
            errorloc(e)
            print("DIMMER WRITE FAILED")

        input("\n\n Press enter when lamp time is over\n\n")
        globals.lamp = 0

        try:
            arduino_dimmer.arduino.write(struct.pack(">B", globals.lamp))
        except Exception as e:
            errorloc(e)
            print("DIMMER WRITE FAILED")

        os.system("clear")
        input("\n\n Press enter when participant is comfortable and ready\n\n")

        cam.setShutterManual()
        cam.performManualff()
        printme(
            "Performing shutter refresh and taking a 10-second break\nto let the thermal image stabilise"
        )
        time.sleep(10)

        try:
            globals.stimulus = 6
            arduino_syringe.arduino.write(struct.pack(">B", globals.stimulus))
        except Exception as e:
            errorloc(e)

        shakeShutter(arduino_syringe, 5)

        arduino_pantilt.arduino.write(struct.pack(">B", 8))
        time.sleep(globals.keydelay)
        arduino_pantilt.arduino.write(
            struct.pack(
                ">BBB",
                globals.default_pantilt[0],
                globals.default_pantilt[1],
                globals.default_pantilt[2],
            )
        )

        print(f"\nCalculating grids...\n")

        c3 = [3, 6, 9]
        for d in globals.axes.keys():
            globals.grid[d] = grid_calculation(d, 10, pos=globals.positions)
            # print(globals.grid[d].keys())
            for i in globals.grid[d].keys():
                if any(str(pc) == i for pc in c3):
                    if d == "colther":
                        globals.grid[d][i]["z"] += 1920
                    else:
                        globals.grid[d][i]["z"] += 5000
                    # print(globals.grid[d][i]['z'])

            print(globals.grid[d])

        saveGridAll(path_data, globals.grid)

        # moveZabersUp(zabers, ['colther', 'tactile'])
        for k, v in reversed(globals.haxes.items()):
            if k != "tactile":
                movetostartZabers(
                    zabers, k, list(reversed(v)), pos=globals.grid[k]["1"]
                )

        manual = threading.Thread(
            target=zabers["colther"]["x"].gridCon3pantilt,
            args=[zabers, arduino_pantilt, arduino_syringe],
            daemon=True,
        )
        manual.start()

        cam.plotLiveROINEcheck()

        try:
            globals.stimulus = 7
            arduino_syringe.arduino.write(struct.pack(">B", globals.stimulus))
        except Exception as e:
            errorloc(e)

        globals.ROIs = zabers["colther"]["x"].rois
        globals.PanTilts = zabers["colther"]["x"].PanTilts

        print(globals.ROIs)
        print(globals.PanTilts)

        saveROIAll(path_data, globals.ROIs)
        savePanTiltAll(path_data, globals.PanTilts)

        homingZabersConcu(zabers, globals.haxes)

        # cam.killStreaming()

    except Exception as e:
        errorloc(e)
        rootToUser(path_day, path_anal, path_data, path_figs, path_videos)
        changeNameTempFile(path_data)

        globals.stimulus = 0
        arduino_syringe.arduino.write(struct.pack(">B", globals.stimulus))

    except KeyboardInterrupt:
        print("Keyboard Interrupt")
        rootToUser(path_day, path_anal, path_data, path_figs, path_videos)
        changeNameTempFile(path_data)

        globals.stimulus = 0
        arduino_syringe.arduino.write(struct.pack(">B", globals.stimulus))
