import sys
sys.path.append('..')
from local_functions import (
    thermalCalibration,
    arduinos_zabers,
    closeEnvelope,
    triggeredException,
    deltaToZaberHeight,
    initPLotLive,
    ROIcheck,
    arduinoPantiltControl,
    arduinoSyringeControl,
    checkVminVmax
)

from local_classes import gridData

from index_funcs import parsingSituation, mkpaths
from arduino import tryexceptArduino, movePanTilt
from grabPorts import grabPorts
from zabers import movetostartZabersConcu, moveAxisTo
from local_zaber_functions import gridManualControlPantilt
from camera import TherCam
from saving_data import (
    csvToDictGridIndv,
    saveROIAll,
    savePanTiltAll,
    saveGridIndv,
    rootToUser,
    getSubjNumDec,
    csvToDictPanTiltsAll,
)
from globals import (
    dry_ice_pos,
    haxes,
    pantilts,
    step_sizes,
    data_path, 
    vmin_file_name,
    vmax_file_name,
    default_touch_z_offset,
    training_temp
)
from local_classes import gridData

##### EXTERNAL LIBRARIES
import threading
import os

if __name__ == "__main__":
    try:
        ports = grabPorts()
        print(ports.ports)

        situ, day, _ = parsingSituation()
        subject_n = getSubjNumDec(day=day)
        path_day, path_anal, path_figs, path_data, path_videos, path_audios = mkpaths(
            situ, numdaysubj=subject_n, folder_name=day
        )

        grid_data = gridData(haxes, pantilts, "camera")
        print(grid_data.current_device)

        if os.path.exists(f"{path_data}/temp_grid_camera.csv"):
            grid_data.positions["camera"] = csvToDictGridIndv(path_data, "temp_grid_camera.csv")
        if os.path.exists(f"{path_data}/temp_grid_tactile.csv"):
            grid_data.positions["tactile"] = csvToDictGridIndv(path_data, "temp_grid_tactile.csv")
        if os.path.exists(f"{path_data}/temp_grid_colther.csv"):
            grid_data.positions["colther"] = csvToDictGridIndv(path_data, "temp_grid_colther.csv")
        if os.path.exists(f"{path_data}/temp_PanTilts.csv"):
            pantilts = csvToDictPanTiltsAll(path_data)

        print(pantilts)
        print(grid_data.positions)

        for position in pantilts.keys():
            grid_data.positions["colther"][position]["z"] = deltaToZaberHeight(
                training_temp, grid_data.positions, position, step_sizes
            )

        ### ARDUINOS & ZABERS
        (
            zabers,
            arduinos
        ) = arduinos_zabers()

        vminT, vmaxT = checkVminVmax(data_path, vmin_file_name, vmax_file_name)
        cam = TherCam(vminT=vminT, vmaxT=vmaxT)
        cam.startStream()
        cam.setShutterManual()

        movetostartZabersConcu(
            zabers,
            "colther",
            list(reversed(haxes["colther"])),
            pos=dry_ice_pos,
        )

        thermalCalibration(zabers, arduinos["syringe"], arduinos["dimmer"], arduinos["pantilt"], cam)

        movetostartZabersConcu(zabers, "tactile", ["y", "x"], pos = grid_data.positions["tactile"]["1"])

        pre_touch = grid_data.positions["tactile"]["1"]["z"] - default_touch_z_offset

        moveAxisTo(zabers, "tactile", "z", pre_touch)


        movePanTilt(arduinos["pantilt"], pantilts["1"])

        movetostartZabersConcu(zabers, "camera", ["x", "y"], pos = grid_data.positions["camera"]["1"])
        movetostartZabersConcu(zabers, "camera", ["z"], pos = grid_data.positions["camera"]["1"])
        movetostartZabersConcu(
            zabers,
            "colther",
            list(reversed(haxes["colther"])),
            pos = grid_data.positions["colther"]["1"],
        )

        # thread zaber
        zabers_thread = threading.Thread(
            target = gridManualControlPantilt, args=[zabers, grid_data, arduinos['pantilt']], daemon=True)
        zabers_thread.start()

        # thread pantilt
        pantilt_thread = threading.Thread(
            target = arduinoPantiltControl, args=[arduinos["pantilt"], grid_data], daemon=True)
        pantilt_thread.start()

        # thread syringe
        syringe_thread = threading.Thread(
            target = arduinoSyringeControl, args=[arduinos["syringe"], grid_data], daemon=True)
        syringe_thread.start()

        fig, ax, img = initPLotLive(cam)
        cam.grabDataFunc(ROIcheck, ax=ax, grid_data=grid_data)

        tryexceptArduino(arduinos["syringe"], 7)

        grid_data.positions["camera"] = grid_data.positions['camera']
        
        print(grid_data.rois)
        saveROIAll(path_data, grid_data.rois)
        savePanTiltAll(path_data, grid_data.pantilts)
        saveGridIndv("temp_grid", path_data, grid_data.positions, "camera")

        rootToUser([path_day, path_anal, path_data, path_figs, path_videos])

        closeEnvelope(zabers, arduinos)

    except Exception as e:
        triggeredException(
            zabers=zabers,
            arduinos = arduinos,
            e=e,
        )

    except KeyboardInterrupt:
        triggeredException(
            zabers=zabers,
            arduinos = arduinos,
        )
