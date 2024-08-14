from arduino import ArdUIno, tryexceptArduino, reLoad, movePanTilt
from zabers import (
    moveAxisTo,
    homingZabersConcu,
    setUpBigThree,
    findHeight,
    stepsToCm,
    cmToSteps,
    movetostartZabersConcu,
)
from audio import Sound
from camera import saveh5py

from globals import (
    radius,
    diff_colther_touch,
    haxes,
    init_pantilt,
    turn_off_dimmer,
    dry_ice_pos,
    axes,
    pantilt_usbname,
    dimmer_usbname,
    syringe_usbname,
    light_usbname,
    speed,
    pre_stimulation_duration,
    post_stimulation_duration,
    tone_response_frequency,
    number_human_mapping,
    default_touch_z_offset,
    default_vminT,
    default_vmaxT,
    stability,
    park_touch,
    park_pantilt
)

from failing import errorloc
from saving_data import rootToUser, changeNameTempFile
from text import printme, waitForEnter
from index_funcs import threadFunctions
from rand_cons import checkLinear
from speech import (
    initSpeak,
    initSpeech2Text,
    startAudioWatson,
    audioInstance,
    openStream,
    YesNotoRecognition,
)

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import keyboard
import time

import os
import sys
import wave
import threading


from termios import TCIFLUSH, tcflush


##############################################
# Functions for the zabers
##############################################
def closeEnvelope(zabers, arduinos):

    #### HOMER ARDUINOS & ZABERS
    # check colther position
    homingZabersConcu(zabers, {"colther": ["z", "x", "y"]})

    homingZabersConcu(zabers, {"camera": ["z"]})

    homingZabersConcu(zabers, {"tactile": ["z", "y"]})

    homeArduinos(arduinos)
    homingZabersConcu(zabers, {"camera": ["x", "y"]})
    homingZabersConcu(zabers, haxes)

def checkTouch(zabers):
    try:
        tcflush(sys.stdin, TCIFLUSH)
    except:
        printme("\n Could not flush the input buffer \n")
    input("Press enter to check next point")
    movetostartZabersConcu(
        zabers,
        "tactile",
        ["x", "y", "z"],
        pos={"x": 183333, "y": 660000, "z": 0},
    )

    input("Press enter to finish next point")
    #### HOMER ARDUINOS & ZABERS
    homingZabersConcu(zabers, {"tactile": haxes["tactile"]})


def itiZaberDanceAway(zabers):
    funcs = [
        [moveAxisTo, [zabers, "colther", "z", 0]],
        [moveAxisTo, [zabers, "camera", "x", 0]],
        [moveAxisTo, [zabers, "colther", "x", 120000]],
        [moveAxisTo, [zabers, "colther", "y", 90000]],
    ]
    threadFunctions(funcs)


def itiZaberDanceIn(zabers, arduino_pantilt, pantilt, grid, touch = False):


    if touch:
        pre_touch = grid.positions["tactile"][str(grid.current_roi)]["z"] - default_touch_z_offset
        funcs = [
            [
                movetostartZabersConcu,
                [zabers, "tactile", ["x", "y"], grid.positions["tactile"][str(grid.current_roi)]],
            ],
            [
                movetostartZabersConcu,
                [zabers, "camera", ["x", "y", "z"], grid.positions["camera"][str(grid.current_roi)]],
            ],
            [movePanTilt, [arduino_pantilt, pantilt[grid.current_roi]]],
            [moveAxisTo, [zabers, "tactile", "z", pre_touch]]
        ]

    else:
        funcs = [
            [
                movetostartZabersConcu,
                [zabers, "camera", ["x", "y", "z"], grid.positions["camera"][str(grid.current_roi)]],
            ],
            [movePanTilt, [arduino_pantilt, pantilt[grid.current_roi]]],
        ]
    # pantilt[grid.current_roi]

    threadFunctions(funcs)
    movetostartZabersConcu(zabers, "camera", ["z"], pos = grid.positions["camera"][str(grid.current_roi)])
    movetostartZabersConcu(
        zabers,
        "colther",
        list(reversed(haxes["colther"])),
        pos = grid.positions["colther"][str(grid.current_roi)],
    )


def TouchingUntouching(zabers, touch_position, event):
    time.sleep(0.5)
    movetostartZabersConcu(zabers, "tactile", "z", touch_position)
    printme("Touching...")

    event.set()

    while event.is_set():
        pass

    movetostartZabersConcu(
        zabers, "tactile", "z", (touch_position - default_touch_z_offset)
    )
    printme("Untouching...")

def controlSoundTrial(tone_stimulus, event):
    time.sleep(0.5)
    tone_stimulus.play()
    printme("Playing sound...")

    event.set()
    
    while event.is_set():
        # loop
        pass
    
    tone_stimulus.stop()
    printme("Stopping sound...")

def deltaToZaberHeight(delta, grid, position, step_sizes):
    height = findHeight(delta)
    z_cm_colther = (
        stepsToCm(grid["tactile"][position]["z"], step_sizes["tactile"])
        + stepsToCm(diff_colther_touch, step_sizes["colther"])
        - height
    )
    zaber_height = cmToSteps(z_cm_colther, step_sizes["colther"])

    return zaber_height

##############################################
# Functions for the arduino
##############################################
def homeArduinos(arduinos):

    if arduinos["syringe"]:
        tryexceptArduino(arduinos["syringe"], 0)

    if arduinos["pantilt"]:
        movePanTilt(arduinos["pantilt"], init_pantilt)

    if arduinos["dimmer"]:
        tryexceptArduino(arduinos["dimmer"], turn_off_dimmer)


def dryiceRiskAssess(ard_syringe, times=3):
    for i in range(times):
        tryexceptArduino(ard_syringe, 1)
        time.sleep(0.4)

        tryexceptArduino(ard_syringe, 6)
        time.sleep(0.4)

        tryexceptArduino(ard_syringe, 0)
        time.sleep(0.4)


def arduinoSyringeControl(arduino, grid_data = None, end_button="e"):
    tryexceptArduino(arduino, 0)
    was_pressed = False

    while True:
        if keyboard.is_pressed("o"):  # Open Arduino shutter
            if not was_pressed:
                tryexceptArduino(arduino, 1)
                was_pressed = True

        elif keyboard.is_pressed("c") or keyboard.is_pressed("n") or keyboard.is_pressed("b"):  # Close Arduino shutter
            if not was_pressed:
                tryexceptArduino(arduino, 0)
                was_pressed = True
        
        elif keyboard.is_pressed("w"):
            if not was_pressed:
                tryexceptArduino(arduino, 6)
                was_pressed = True
                
        elif keyboard.is_pressed(end_button):
            # check whether grid_data is not None
            if grid_data:
                boolean_rois = [len(n) < 2 for n in list(grid_data.rois.values())]
                if not any(boolean_rois):
                    break
                else:
                    print("You are missing something...")
                    was_pressed = True
            else:
                break
        else:
            was_pressed = False

def arduinoPantiltControl(arduino, grid_data = None, end_button="e"):
    was_pressed = False
    pantilt = False
    camera = False

    while True:
        data_arduino = arduino.arduino.readline()
    
        if keyboard.is_pressed("p"):
            if not was_pressed:
                if len(str(data_arduino)) > 10:
                    try:
                        pan, tilt, head = str(data_arduino)[2:-5].split("-")
                        print(pan, tilt, head)
                    except Exception as e:
                        errorloc(e)

                    if grid_data:
                        grid_data.pantilts[grid_data.current_roi] = [
                            int(pan),
                            int(tilt),
                            int(head),
                        ]
                        
                was_pressed = True

        elif keyboard.is_pressed("up"):
            if pantilt:
                tryexceptArduino(arduino, 3)
                was_pressed = True

        elif keyboard.is_pressed("down"):
            if pantilt:
                tryexceptArduino(arduino, 4)
                was_pressed = True

        elif keyboard.is_pressed("right"):
            if pantilt:
                tryexceptArduino(arduino, 2)
                was_pressed = True
        
        elif keyboard.is_pressed("left"):
            if pantilt:
                tryexceptArduino(arduino, 1)
                was_pressed = True

        elif keyboard.is_pressed("u"):
            if pantilt:
                tryexceptArduino(arduino, 5)
                was_pressed = True

        elif keyboard.is_pressed("d"):
            if pantilt:
                tryexceptArduino(arduino, 6)
                was_pressed = True

        # elif keyboard.is_pressed("n") or keyboard.is_pressed("b"):
        #     if not was_pressed:
        #         if grid_data:
                    
        #         was_pressed = True

        elif keyboard.is_pressed("j"):
            if not was_pressed:
                pantilt = True
                was_pressed = True
        elif keyboard.is_pressed("k"):
            if not was_pressed:
                pantilt = False
                was_pressed = True
        elif keyboard.is_pressed(end_button):
            if grid_data:
                boolean_rois = [len(n) < 2 for n in list(grid_data.rois.values())]
                if not any(boolean_rois):
                    break
                else:
                    print(grid_data.rois.values())
                    print(boolean_rois)
                    print("Pantilt: you are missing something...")
                    was_pressed = True
            else:
                break
        else:
            was_pressed = False
    
# Thread arduino_syringe
def controlSyringeTrial(arduino, stimulus, event):
    event.wait()
    tryexceptArduino(arduino, stimulus)
    
    while event.is_set():
        pass

    tryexceptArduino(arduino, number_human_mapping["close_shutter"])

def controlLightTrial(arduinos, event):
    event.wait()
    tryexceptArduino(arduinos["light"], 1)

    # wait for event to be false again
    while event.is_set():
        # loop
        pass

    tryexceptArduino(arduinos["light"], 0)


############################################################################################################
# Functions for arduino and zaber
############################################################################################################
def arduinos_zabers():
    zabers = setUpBigThree(axes)

    homingZabersConcu(zabers, {"colther": ["z", "x", "y"]})

    homingZabersConcu(zabers, {"camera": ["z"]})
    homingZabersConcu(zabers, {"camera": ["x", "y"]})

    homingZabersConcu(zabers, {"tactile": ["y"]})

    homingZabersConcu(zabers, haxes, speed=speed)

    arduinos = {}

    arduinos["pantilt"] = ArdUIno(
        usbname = pantilt_usbname,
        name="PanTilt",
    )
    arduinos["pantilt"].arduino.flushInput()
    time.sleep(0.1)

    # Arduino syringe motors
    arduinos["syringe"] = ArdUIno(
        usbname= syringe_usbname,
        name="syringe",
    )
    arduinos["syringe"].arduino.flushInput()
    time.sleep(0.1)

    # Arduino dimmers
    arduinos["dimmer"] = ArdUIno(
        usbname = dimmer_usbname,
        name="dimmer",
    )
    arduinos["dimmer"].arduino.flushInput()
    time.sleep(0.1)

    arduinos["light"] = ArdUIno(
        usbname = light_usbname,
        name="light",
    )
    arduinos["light"].arduino.flushInput()
    time.sleep(0.1)

    return zabers, arduinos


def triggeredException(
    zabers=None,
    path_day=None,
    path_anal=None,
    path_data=None,
    path_videos=None,
    path_figs=None,
    arduinos=None,
    e=None,
    outcome="failed",
):

    if e:
        errorloc(e)
    else:
        print("Keyboard Interrupt")

    if path_data:
        rootToUser([path_day, path_anal, path_data, path_figs, path_videos])
        changeNameTempFile(path_data, outcome=outcome)

    if zabers:
        homingZabersConcu(zabers, {"colther": ["z", "x", "y"]})

        homingZabersConcu(zabers, {"camera": ["z"]})
        homingZabersConcu(zabers, {"camera": ["x", "y"]})

        homingZabersConcu(zabers, {"tactile": ["y"]})

    if arduinos["syringe"]:
        tryexceptArduino(arduinos["syringe"], 0)

    if arduinos["pantilt"]:
        movePanTilt(arduinos["pantilt"], init_pantilt)

    if arduinos["dimmer"]:
        tryexceptArduino(arduinos["dimmer"], 0)

    if arduinos["light"]:
        tryexceptArduino(arduinos["light"], 0)

    if zabers:
        homingZabersConcu(zabers, haxes, speed=speed)

    time.sleep(1)


def panicButton():
    if keyboard.is_pressed("p"):
        os.system("clear")
        waitForEnter("\n\n Press enter when panic is over...")


def homeButton(zabers, arduino_pantilt):
    if keyboard.is_pressed("h"):
        os.system("clear")
        homingZabersConcu(zabers, {"colther": haxes["colther"]})
        moveAxisTo(zabers, "camera", "z", 0)
        movePanTilt(arduino_pantilt, init_pantilt)

        homingZabersConcu(zabers, {"camera": haxes["camera"]})
        homingZabersConcu(zabers, {"tactile": haxes["tactile"]})
        waitForEnter("\n\n Press enter when panic is over...")


def triggerHandleReload(
    zabers,
    arduinos,
    cam,
    n_block,
    within_block_counter,
):

    homingZabersConcu(zabers, {"colther": haxes["colther"]})
    moveAxisTo(zabers, "camera", "z", 0)
    movePanTilt(arduinos["pantilt"], init_pantilt)

    homingZabersConcu(zabers, {"camera": haxes["camera"]})
    homingZabersConcu(zabers, {"tactile": haxes["tactile"]})

    thermalCalibration(zabers, arduinos["syringe"], arduinos["dimmer"], arduinos['pantilt'], cam)
    n_block += 1
    within_block_counter = 0

    movetostartZabersConcu(zabers, "tactile", ["x", "z"], pos = park_touch)

    return True, n_block, within_block_counter


def grabNextPosition(positions, limit, positions_to_grab):
    while True:
        randomly_chosen_next = np.random.choice(
            list(positions_to_grab.keys()), 1, replace=True
        )[0]
        if len(positions) == 0:
            positions.append(randomly_chosen_next)
            break
        else:
            backwards = []
            for bi in np.arange(1, limit + 0.1, 1):
                current_check = checkLinear(positions, randomly_chosen_next, bi)
                backwards.append(current_check)

            if np.all(backwards):
                positions.append(randomly_chosen_next)
                break
            else:
                print("WRONG VALUE!")
    return randomly_chosen_next, positions





##############################################
# Functions for the camera
##############################################


def initPLotLive(cam):
    mpl.rc("image", cmap="coolwarm")
    fig = plt.figure(1)
    ax = plt.axes()

    fig.tight_layout()

    dummy = np.zeros([120, 160])

    img = ax.imshow(
        dummy,
        interpolation="nearest",
        vmin=cam.vminT,
        vmax=cam.vmaxT,
        animated=True,
    )
    fig.colorbar(img)

    return fig, ax, img


def thermalCalibration(zabers, arduino_syringe, arduino_dimmer, arduino_pantilt, cam):

    movetostartZabersConcu(
        zabers,
        "colther",
        list(reversed(haxes["colther"])),
        pos = dry_ice_pos,
    )
    # Dry ice load
    tryexceptArduino(arduino_syringe, 7)
    tryexceptArduino(arduino_syringe, 0)

    # Turn lamp on
    tryexceptArduino(arduino_dimmer, 1)

    movetostartZabersConcu(zabers, "camera", ["y"], {"y": 530000})

    # Get camera out of the way
    reLoad(arduino_syringe)

    os.system("clear")

    # Turn lamp off
    tryexceptArduino(arduino_dimmer, 0)

    # Subject in position
    movetostartZabersConcu(zabers, "camera", ["y"], {"y": 530000})
    movetostartZabersConcu(zabers, "tactile", ["x"], {"x": stability[1]['x']})
    movePanTilt(arduino_pantilt, park_pantilt)
    os.system("clear")
    waitForEnter("\n\n Press enter when participant is comfortable and ready\n\n")

    homingZabersConcu(zabers)
    # Shutter refresh and stabilisation
    cam.setShutterManual()
    cam.performManualff()
    printme(
        "Performing shutter refresh and taking a 10-second break\nto let the thermal image stabilise"
    )
    time.sleep(10)

    dryiceRiskAssess(arduino_syringe)

    tryexceptArduino(arduino_syringe, 4)
    printme("Resuming experiment...")


def ROIcheck(**kwargs):
    if "thermal_image_data" in kwargs and "cam" in kwargs and "ax" in kwargs and "grid_data" in kwargs:
        dataC = kwargs["thermal_image_data"]
        cam = kwargs["cam"]
        ax = kwargs["ax"]
        grid_data = kwargs["grid_data"]
        # print(kwargs)
    global dev
    global devh

    was_pressed = False

    # We get the min temp and draw a circle
    edgexl = 15
    edgexr = 15
    edgey = 0

    subdataC = dataC[edgey : edgey + (120 - edgey * 2), edgexl : (160 - edgexr)]
    minimoC = np.min(subdataC)

    xs = np.arange(0, 160)
    ys = np.arange(0, 120)

    indy, indx = np.where(subdataC == minimoC)

    indx, indy = indy + edgey, indx + edgexl
    mask = (xs[np.newaxis, :] - indy[0]) ** 2 + (
        ys[:, np.newaxis] - indx[0]
    ) ** 2 < radius**2

    roiC = dataC[mask]
    mean = round(np.mean(roiC), 2)
    print(f"Mean: {mean}")

    circles = []

    for a, j in zip(indx, indy):
        cirD = plt.Circle((j, a), radius, color="b", fill=False)
        circles.append(cirD)

    if keyboard.is_pressed("p"):
        grid_data.rois[grid_data.current_roi] = [indx[0], indy[0]]
        print(grid_data.rois[grid_data.current_roi])

    ax.clear()
    ax.set_xticks([])
    ax.set_yticks([])

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.imshow(dataC, vmin=cam.vminT, vmax=cam.vmaxT)
    ax.add_artist(circles[0])
    plt.pause(0.0005)

    if not was_pressed and keyboard.is_pressed("i") and keyboard.is_pressed("up"):
        cam.vmaxT += 1
        print(cam.vminT, cam.vmaxT)
        was_pressed = True
    elif not was_pressed and keyboard.is_pressed("i") and keyboard.is_pressed("down"):
        cam.vmaxT -= 1
        print(cam.vminT, cam.vmaxT)
        was_pressed = True
    elif not was_pressed and keyboard.is_pressed("l") and keyboard.is_pressed("up"):
        cam.vminT += 1
        print(cam.vminT, cam.vmaxT)
        was_pressed = True
    elif not was_pressed and keyboard.is_pressed("l") and keyboard.is_pressed("down"):
        cam.vminT -= 1
        print(cam.vminT, cam.vmaxT)
        was_pressed = True
    else:
        was_pressed = False

    if cam.vmaxT <= cam.vminT:
        cam.vmaxT = cam.vminT + 1

    if keyboard.is_pressed("r"):
        print("Manual FFC")
        cam.performManualff()

    if keyboard.is_pressed("e"):
        # check whether the lists in the grid_data.rois are empty
        boolean_rois = [len(n) < 2 for n in list(grid_data.rois.values())]
        if not any(boolean_rois):
            print("ROIs are all set")
            plt.close("all")
            plt.clf()
            return True
        else:
            print(grid_data.rois)
            print("Thermal camera: you are missing some ROIs")
            return False
    else:
        return False


def deltaTemperature(**kwargs):

    temperature_reached = False
    data = {}
    temp_delta = 0
    kwargs["time_stamps"].momen = time.time() - kwargs["time_stamps"].start_time
    temp_diff = np.zeros((kwargs["thermal_image_data"].shape[0], kwargs["thermal_image_data"].shape[1]))

    mask = (kwargs["temperature_data"].xs[np.newaxis, :] - kwargs["roi_coordinates"][1]) ** 2 + (
        kwargs["temperature_data"].ys[:, np.newaxis] - kwargs["roi_coordinates"][0]
    ) ** 2 < radius ** 2
    roiC = kwargs["thermal_image_data"][mask]
    temp = round(np.mean(roiC), 2)
    data["ROI_coordinates"] = kwargs["roi_coordinates"]

    if kwargs["temperature_data"].stimulus in [1, 2] and not kwargs["time_stamps"].end:
            kwargs["temperature_data"].baseline_buffer.append(temp)

    if kwargs["time_stamps"].momen > (pre_stimulation_duration - 0.5) and kwargs["time_stamps"].buffering_duration < 0.3 and kwargs["temperature_data"].stimulus in [1, 2] and not kwargs["time_stamps"].end:
        kwargs["temperature_data"].diff_buffer.append(kwargs["thermal_image_data"])
        print("Buffering...")
        print(kwargs["time_stamps"].momen)

        kwargs["temperature_data"].mean_diff_buffer = np.mean(kwargs["temperature_data"].diff_buffer, axis=0)

    # get delta temperature
    if kwargs["temperature_data"].stimulus in [1, 2] and kwargs["time_stamps"].shutter_opened:
        kwargs["time_stamps"].buffering_duration = time.time() - kwargs["time_stamps"].shutter_start_time
        
        if kwargs["time_stamps"].buffering_duration > 0.3:
            temp_diff = kwargs["temperature_data"].mean_diff_buffer - kwargs["thermal_image_data"]

            temp_diff[kwargs["thermal_image_data"] <= 18] = 0
            temp_diff[temp_diff <= (0.1)] = 0

            maxdif = np.max(temp_diff)
            indxdf, indydf = np.where(temp_diff == maxdif)
            print(indxdf[0], indydf[0])

            mask = (kwargs["temperature_data"].xs[np.newaxis, :] - indydf[0]) ** 2 + (
                kwargs["temperature_data"].ys[:, np.newaxis] - indxdf[0]
            ) ** 2 < radius ** 2
            roiC = kwargs["thermal_image_data"][mask]
            temp = round(np.mean(roiC), 2)

            temp_delta = kwargs["temperature_data"].meaned_baseline_buffer - temp
            print("Delta: " + str(round(temp_delta, 2)))
            
            data["ROI_coordinates"] = (indxdf[0], indydf[0])

    # open shutter
    if kwargs["time_stamps"].momen > pre_stimulation_duration and not kwargs["time_stamps"].end and not kwargs["time_stamps"].shutter_opened:
        print("Opening shutter")
        kwargs["events"]["cooling"].set()
        kwargs["time_stamps"].shutter_opened = 1
        kwargs["time_stamps"].shutter_start_time = time.time()
        kwargs["temperature_data"].meaned_baseline_buffer = np.mean(kwargs["temperature_data"].baseline_buffer)

    # check if we've reached the time limit
    if kwargs["time_stamps"].momen > (pre_stimulation_duration + kwargs["time_stamps"].time_out) and not kwargs["time_stamps"].end and kwargs["time_stamps"].shutter_opened:
        print("Closing shutter")
        print("Time out")
        kwargs["events"]["cooling"].clear()
        # check whether interactor existis
        if "interactor" in kwargs["events"]:
            kwargs["events"]["interactor"].clear()
        if kwargs["temperature_data"].stimulus in [0, 3]:
            kwargs["temperature_data"].failed = False
        else:
            kwargs["temperature_data"].failed = True
        kwargs["time_stamps"].end = True
        kwargs["time_stamps"].shutter_opened = 0
        kwargs["time_stamps"].shutter_open_duration = time.time() - kwargs["time_stamps"].shutter_start_time
        kwargs["time_stamps"].shutter_close_time = time.time()

    # check if delta has reached target
    if temp_delta > kwargs["temperature_data"].delta_target and not kwargs["time_stamps"].end and kwargs["time_stamps"].shutter_opened and temp_delta < (kwargs["temperature_data"].delta_target + 0.8):
        print(f"\nDELTA REACHED: {temp_delta}")
        print("Closing shutter")
        kwargs["events"]["cooling"].clear()
        if "interactor" in kwargs["events"]:
            kwargs["events"]["interactor"].clear()
        kwargs["temperature_data"].failed = False
        kwargs["time_stamps"].end = True
        kwargs["time_stamps"].shutter_opened = 0
        kwargs["time_stamps"].shutter_open_duration = time.time() - kwargs["time_stamps"].shutter_start_time
        kwargs["time_stamps"].shutter_close_time = time.time()

    # check if delta has overshot
    if temp_delta > (kwargs["temperature_data"].delta_target + 0.8) and not kwargs["time_stamps"].end and kwargs["time_stamps"].shutter_opened:
        print(f"\nDELTA OVERSHOT: {temp_delta}")
        print("Closing shutter")
        kwargs["events"]["cooling"].clear()
        if "interactor" in kwargs["events"]:
            kwargs["events"]["interactor"].clear()
        kwargs["temperature_data"].failed = True
        kwargs["time_stamps"].end = True
        kwargs["time_stamps"].shutter_opened = 0
        kwargs["time_stamps"].shutter_open_duration = time.time() - kwargs["time_stamps"].shutter_start_time
        kwargs["time_stamps"].shutter_close_time = time.time()

    # save the data
    data["image"] = kwargs["thermal_image_data"]
    data["shutter_position"] = [kwargs["time_stamps"].shutter_opened]
    data["time_now"] = [kwargs["time_stamps"].momen]
    data["delta"] = [temp_delta]
    data["image_difference"] = temp_diff
    data["roi_temperature"] = [temp]

    print(data["ROI_coordinates"])
    saveh5py(data, kwargs["frame_number"], kwargs["hpy_file"])
    
    if kwargs["time_stamps"].end:
        kwargs["time_stamps"].shutter_close_duration = time.time() - kwargs["time_stamps"].shutter_close_time
        if kwargs["time_stamps"].shutter_close_duration > post_stimulation_duration:
            kwargs["hpy_file"].close()
            return True

    elif temperature_reached:
        return True
    else:
        return False


def checkVminVmax(data_path, vmin_file_name, vmax_file_name):
    if not os.path.isfile(data_path + vmin_file_name):
        vminT = readNumber(data_path, vmin_file_name)
    else:
        vminT = default_vminT
    if not os.path.isfile(data_path + vmax_file_name):
        vmaxT = readNumber(data_path, vmax_file_name)
    else:
        vmaxT = default_vmaxT

    return vminT, vmaxT



############################################################################################################
# Functions for the audio
############################################################################################################


def saveAudio(frames, path_audios, file_name, channels=1, fs=44100):
    audio_file_name = f"{path_audios}/{file_name}.wav"
    wf = wave.open(audio_file_name, "wb")
    wf.setnchannels(channels)
    wf.setsampwidth(2)
    wf.setframerate(fs)
    wf.writeframes(b"".join(frames))
    wf.close()


def startWatson(speech_to_text):
    audio = startAudioWatson()
    audio_source, q = audioInstance()
    stream, frames = openStream(audio, q)
    recognize_yes_no = YesNotoRecognition(speech_to_text, audio_source)
    recognize_yes_no_thread = threading.Thread(
        target=recognize_yes_no.run,
    )
    recognize_yes_no_thread.name = "Speech recognition thread"
    recognize_yes_no_thread.start()

    stream.start_stream()
    return stream, audio, audio_source, recognize_yes_no, frames


def initWatson():
    speaker = initSpeak()
    speech_to_text = initSpeech2Text()
    return speaker, speech_to_text


def waitForWatson(recognize_yes_no):
    tone_response = Sound(tone_response_frequency, 0.2)
    tone_response.play()
    timer_watson = time.time()

    while True:
        recognize_yes_no.time_out_watson = time.time() - timer_watson
        if recognize_yes_no.time_out_watson > 10:
            recognize_yes_no.answered = 2
            break
        elif recognize_yes_no.answered == 1 or recognize_yes_no.answered == 0:
            break

    print("Answered", recognize_yes_no.answered)
    tone_response.play()

# function to save an integer to a file
def writeNumber(value, path, filename):
    with open(f'{path}/{filename}.txt','w') as f:
        f.write(str(value))

# function to read an integer from a file
def readNumber(path, filename):
    with open(f'{path}/{filename}.txt','r') as f:
        value = int(f.read())
        return value


def readInputKeyPad():
    tone_response = Sound(tone_response_frequency, 0.2)
    tone_response.play()
    # get reaction time, start timer
    start_time = time.time()
    # remove any input in the buffer
    tcflush(sys.stdin, TCIFLUSH)
    while True:
        # check whether response is 3 or 1
        if keyboard.is_pressed('3'):
            # calculate reaction time
            reaction_time = time.time() - start_time
            tone_response.play()
            return 1, reaction_time
        elif keyboard.is_pressed('1'):
            # calculate reaction time
            reaction_time = time.time() - start_time
            tone_response.play()
            return 0, reaction_time