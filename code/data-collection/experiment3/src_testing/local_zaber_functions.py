import sys
sys.path.append('..')
import keyboard
from zabers import homingZabersConcu, grabPositions, movetostartZabersConcu, moveAxisTo, changeAmount, move
from globals import default_touch_z_offset, rules
from text import printme
from arduino import movePanTilt

from index_funcs import threadFunctions

def gridUpDown(
    devices,
    grid_data,
    end_button = "e"
):
    was_pressed = False
    device = devices[grid_data.current_device]
    amount = 10000
    
    while True:
        if keyboard.is_pressed("u"):
            move(device["z"], -amount, rules)

        elif keyboard.is_pressed("d"):
            move(device["z"], amount, rules)

        elif keyboard.is_pressed("p"):
            if not was_pressed:
                grid_data.positions[grid_data.current_device][grid_data.current_roi] = grabPositions(devices[grid_data.current_device])
                printme(grid_data.positions[grid_data.current_device])

                was_pressed = True

        elif keyboard.is_pressed("n"):
            if not was_pressed:
                grid_data.current_roi = str(int(grid_data.current_roi) + 1)

                if int(grid_data.current_roi) > len(grid_data.positions[grid_data.current_device]):
                    grid_data.current_roi = "1"

                movetostartZabersConcu(
                    devices,
                    grid_data.current_device,
                    'z',
                    pos = 0
                )
                movetostartZabersConcu(
                    devices,
                    grid_data.current_device,
                    list(reversed(grid_data.haxes[grid_data.current_device])),
                    pos =  grid_data.positions[grid_data.current_device][grid_data.current_roi],
                )
                print(f"Current roi: ",  grid_data.current_roi)
                was_pressed = True

        elif keyboard.is_pressed("b"):
            if not was_pressed:
                grid_data.current_roi = str(int(grid_data.current_roi) - 1)

                if int(grid_data.current_roi) <= 0:
                    grid_data.current_roi = str(len(list(grid_data.positions[grid_data.current_device].keys())))

                movetostartZabersConcu(
                    devices,
                    grid_data.current_device,
                    'z',
                    pos = 0
                )
                movetostartZabersConcu(
                    devices,
                    grid_data.current_device,
                    list(reversed(grid_data.haxes[grid_data.current_device])),
                    pos =  grid_data.positions[grid_data.current_device][grid_data.current_roi],
                )
                print(f"Current roi: ",  grid_data.current_roi)
                was_pressed = True

        elif keyboard.is_pressed("5"):
            if not was_pressed:
                amount = 50000
                print(f"Amount changed to {amount}")
                was_pressed = True

        elif keyboard.is_pressed("6"):
            if not was_pressed:
                amount = 10000
                print(f"Amount changed to {amount}")
                was_pressed = True

        elif keyboard.is_pressed("7"):
            if not was_pressed:
                amount = 1000
                print(f"Amount changed to {amount}")
                was_pressed = True

        elif keyboard.is_pressed(end_button):
            boolean_heights = [grid_data.positions[grid_data.current_device][position]["z"] == 0 for position in list(grid_data.positions[grid_data.current_device].keys())]
            if not any(boolean_heights):
                break
            elif any(boolean_heights):
                print("You are missing some heights")
                print(boolean_heights)
                was_pressed = True

        else:
            was_pressed = False

def manualControlPanTilt(
    devices,
    home=True,
    end_button="e"
):
    """
        Method for Object Zaber to move the 3 axes of THREE zabers with keyboard presses. Like a game!
        The coordinates of two positions can be saved with 'z' and 'x'
        This method was created and it is specific to the experiment in which we measure cold
        thresholds with and without touch
    """
    was_pressed = False

    print("Zaber game activated")

    amount = 10000
    positions = {}
    current_device = "colther"
    pantilt = False

    device = devices[current_device]
    while True:
        if keyboard.is_pressed("up"):
            if not pantilt:
                move(device["y"], -amount, rules)
                was_pressed = True

        elif keyboard.is_pressed("down"):
            if not pantilt:
                move(device["y"], amount, rules)
                was_pressed = True

        elif keyboard.is_pressed("right"):
            if not pantilt:
                move(device["x"], amount, rules)
                was_pressed = True

        elif keyboard.is_pressed("left"):
            if not pantilt:
                move(device["x"], -amount, rules)
                was_pressed = True

        elif keyboard.is_pressed("u"):
            if not pantilt:
                move(device["z"], -amount, rules)
                was_pressed = True
        
        elif keyboard.is_pressed("d"):
            if not pantilt:
                move(device["z"], amount, rules)
                was_pressed = True

        elif keyboard.is_pressed("5"):
            if not was_pressed:
                amount = 50000
                print(f"Amount changed to {amount}")
                was_pressed = True

        elif keyboard.is_pressed("6"):
            if not was_pressed:
                amount = 10000
                print(f"Amount changed to {amount}")
                was_pressed = True

        elif keyboard.is_pressed("7"):
            if not was_pressed:
                amount = 1000
                print(f"Amount changed to {amount}")
                was_pressed = True

        ### TERMINATE
        elif keyboard.is_pressed(end_button):
            if home:
                homingZabersConcu(devices, concurrently=False)
            print("Terminating Zaber game \n")
            break

        #### GET POSITION
        elif keyboard.is_pressed("p"):
            if not was_pressed:
                positions[current_device] = grabPositions(device)

                printme(positions[current_device])
                was_pressed = True

        # Press letter h and Zaber will home, first z axis, then y and finally x
        # Control
        elif keyboard.is_pressed("h"):
            homingZabersConcu(devices, concurrently=False)

        #### Change Zaber
        elif keyboard.is_pressed("k"):
            if not was_pressed:
                if current_device == "camera":
                    pantilt = not pantilt
                device = devices["camera"]
                current_device = "camera"
                print(f"Controlling CAMERA zabers")
                was_pressed = True

        elif keyboard.is_pressed("f"):
            if not was_pressed:
                device = devices["colther"]
                current_device = "colther"
                print(f"Controlling COLTHER zabers")
                print(device)
                was_pressed = True

        elif keyboard.is_pressed("t"):
            if not was_pressed:
                device = devices["tactile"]
                current_device = "tactile"
                print(f"Controlling TACTILE zabers")
                was_pressed = True

        elif keyboard.is_pressed("a"):
            if not was_pressed:
                amount = changeAmount("a")
                was_pressed = True

        else:
            was_pressed = False

def gridManualControlPantilt(devices, grid_data, arduino, end_button="e"):
    """
    """
    was_pressed = False

    print("Zaber game activated")

    amount = 10000
    device = devices[grid_data.current_device]
    touched = False
    pantilt = False

    while True:
        if keyboard.is_pressed("up"):
            if not pantilt:
                move(device["y"], -amount, rules)

        elif keyboard.is_pressed("down"):
            if not pantilt:
                move(device["y"], amount, rules)

        elif keyboard.is_pressed("right"):
            if not pantilt:
                move(device["x"], amount, rules)

        elif keyboard.is_pressed("left"):
            if not pantilt:
                move(device["x"], -amount, rules)

        elif keyboard.is_pressed("u"):
            if not pantilt:
                move(device["z"], -amount, rules)

        elif keyboard.is_pressed("d"):
            if not pantilt:
                move(device["z"], amount, rules)

        elif keyboard.is_pressed("5"):
            if not was_pressed:
                amount = 50000
                print(f"Amount changed to {amount}")
                was_pressed = True

        elif keyboard.is_pressed("6"):
            if not was_pressed:
                amount = 10000
                print(f"Amount changed to {amount}")
                was_pressed = True

        elif keyboard.is_pressed("7"):
            if not was_pressed:
                amount = 1000
                print(f"Amount changed to {amount}")
                was_pressed = True

        elif keyboard.is_pressed("i"):
            if not was_pressed:
                print(f"Current spot: {grid_data.current_roi}")
                print("ROIS")
                print(grid_data.rois)
                print("Pan tilt")
                print(grid_data.pantilts)
                print("Camera positions")
                print(grid_data.positions['camera'])
                print("Checked Touch")
                print(grid_data.touch_checked)
                was_pressed = True

        #### GET POSITION
        elif keyboard.is_pressed("p"):
            if not was_pressed:
                grid_data.positions["camera"][grid_data.current_roi] = grabPositions(devices["camera"])

                print(grid_data.positions["camera"][grid_data.current_roi])
                was_pressed = True

        elif keyboard.is_pressed("h"):
            homingZabersConcu(devices, concurrently=False)

        #### Change Zaber
        elif keyboard.is_pressed("j"):
            if not was_pressed:
                pantilt = True
                was_pressed = True

        elif keyboard.is_pressed("k"):
            if not was_pressed:
                device = devices["camera"]
                pantilt = False
                grid_data.current_device = "camera"
                print(f"Controlling CAMERA zabers")
                was_pressed = True

        elif keyboard.is_pressed("f"):
            if not was_pressed:
                device = devices["colther"]
                grid_data.current_device = "colther"
                print(f"Controlling COLTHER zabers")
                was_pressed = True

        elif keyboard.is_pressed("t"):
            if not was_pressed:
                if not touched:
                    touching = grid_data.positions["tactile"][grid_data.current_roi]["z"]
                    movetostartZabersConcu(
                        devices, "tactile", ["z"], pos = touching
                    )

                    grid_data.touch_checked[grid_data.current_roi] = True

                    touched = True

                elif touched:
                    pre_touch = (
                        grid_data.positions["tactile"][grid_data.current_roi]["z"]
                        - default_touch_z_offset
                    )
                    movetostartZabersConcu(
                        devices, "tactile", ["z"], pos = pre_touch
                    )

                    touched = False

        elif keyboard.is_pressed("n"):
            if not was_pressed:
                grid_data.current_roi = str(int(grid_data.current_roi) + 1)
                if int(grid_data.current_roi) > len(grid_data.positions[grid_data.current_device]):
                    grid_data.current_roi = "1"

                pre_touch = (
                    grid_data.positions["tactile"][grid_data.current_roi]["z"]
                    - default_touch_z_offset
                )

                moveAxisTo(devices, "colther", "z", 0)
                if touched:
                    movetostartZabersConcu(
                        devices, "tactile", ["z"], pos = pre_touch
                    )

                funcs = [
                    [moveAxisTo, [devices, "camera", "x", 0]],
                    [moveAxisTo, [devices, "camera", "y", grid_data.positions["camera"][grid_data.current_roi]["y"]]],
                    [moveAxisTo, [devices, "colther", "y", grid_data.positions["colther"][grid_data.current_roi]["y"]]],
                    [moveAxisTo, [devices, "colther", "x", grid_data.positions["colther"][grid_data.current_roi]["x"]]],
                    [moveAxisTo, [devices, "tactile", "x", grid_data.positions["tactile"][grid_data.current_roi]["x"]]],
                    [moveAxisTo, [devices, "tactile", "y", grid_data.positions["tactile"][grid_data.current_roi]["y"]]],
                ]

                threadFunctions(funcs)

                touched = False

                funcs = [
                    [moveAxisTo, [devices, "camera", "x", grid_data.positions["camera"][grid_data.current_roi]["x"]]],
                    [moveAxisTo, [devices, "camera", "z", grid_data.positions["camera"][grid_data.current_roi]["z"]]],
                    [moveAxisTo, [devices, "colther", "z", grid_data.positions["colther"][grid_data.current_roi]["z"]]],
                    [movePanTilt, [arduino, grid_data.pantilts[grid_data.current_roi]]],
                ]

                threadFunctions(funcs)

                was_pressed = True

        elif keyboard.is_pressed("b"):
            if not was_pressed:
                grid_data.current_roi = str(int(grid_data.current_roi) - 1)
                if int(grid_data.current_roi) == 0:
                    grid_data.current_roi = list(grid_data.positions["colther"].keys())[-1]

                pre_touch = (
                        grid_data.positions["tactile"][grid_data.current_roi]["z"]
                        - default_touch_z_offset
                    )

                devices["colther"]["z"].device.move_abs(0)
                if touched:
                    movetostartZabersConcu(
                        devices, "tactile", ["z"], pos = pre_touch
                    )

                funcs = [
                    [moveAxisTo, [devices, "camera", "x", 0]],
                    [moveAxisTo, [devices, "camera", "y", grid_data.positions["camera"][grid_data.current_roi]["y"]]],
                    [moveAxisTo, [devices, "colther", "y", grid_data.positions["colther"][grid_data.current_roi]["y"]]],
                    [moveAxisTo, [devices, "colther", "x", grid_data.positions["colther"][grid_data.current_roi]["x"]]],
                    [moveAxisTo, [devices, "tactile", "x", grid_data.positions["tactile"][grid_data.current_roi]["x"]]],
                    [moveAxisTo, [devices, "tactile", "y", grid_data.positions["tactile"][grid_data.current_roi]["y"]]],
                ]

                threadFunctions(funcs)

                touched = False

                funcs = [
                    [moveAxisTo, [devices, "camera", "x", grid_data.positions["camera"][grid_data.current_roi]["x"]]],
                    [moveAxisTo, [devices, "camera", "z", grid_data.positions["camera"][grid_data.current_roi]["z"]]],
                    [moveAxisTo, [devices, "colther", "z", grid_data.positions["colther"][grid_data.current_roi]["z"]]],
                    [movePanTilt, [arduino, grid_data.pantilts[grid_data.current_roi]]],
                ]

                threadFunctions(funcs)

                was_pressed = True


        ### TERMINATE
        elif keyboard.is_pressed(end_button):
            print(list(grid_data.rois.values()))
            boolean_rois = [len(n) < 2 for n in list(grid_data.rois.values())]
            if not any(boolean_rois):
                break
            else:
                print(grid_data.rois.values())
                print(boolean_rois)
                print("You are missing something...")
                was_pressed = True

        else:
            was_pressed = False