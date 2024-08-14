import sys
sys.path.append('..')

from grabPorts import grabPorts
from globals import (
    haxes,
    separation_grid,
    centre_grid_positions,
    rules,
    pantilts,
    stability,
    dry_ice_pos,
    park_pantilt
)
from zabers import (
    movetostartZabersConcu,
    gridCalculation,
    homingZabersConcu,
)
from local_zaber_functions import gridUpDown

from saving_data import (
    rootToUser,
    saveIndvVar,
    numberSubjDay,
    setSubjNumDec,
    saveGridIndv,
    checkFilePathSave,
    createNotesFile,
    booleanValueStore
)
from text import (
    agebyExperimenter,
    sexbyExperimenter,
    handednessbyExperimenter,
)
from failing import pusherWarning, spaceLeftWarning
from index_funcs import parsingSituation, mkpaths
from local_functions import (
    closeEnvelope,
    arduinos_zabers,
    triggeredException,
)
from arduino import movePanTilt
from local_classes import gridData
import os

if __name__ == "__main__":
    try:
        ports = grabPorts()
        print(ports.ports)

        pusherWarning(n_pushes=3000)
        spaceLeftWarning()

        situ, day, _ = parsingSituation()
        print(day)
        grid_data = gridData(haxes, pantilts, 'tactile')

        if situ == "tb":
            subject_n = numberSubjDay()
        elif situ == "ex":
            subject_n = numberSubjDay("y")

        path_day, path_anal, path_figs, path_data, path_videos, path_audios = mkpaths(
            situ, numdaysubj=subject_n, folder_name=day
        )
        path_day_bit = path_day.rsplit("/", 3)[-1]

        if os.path.exists(f"./src_testing/temp_folder_name.txt"):
            os.remove(f"./src_testing/temp_folder_name.txt")

        saveIndvVar("./src_testing", path_day_bit, "temp_folder_name")

        if situ == "tb":
            age = 1
            sex = 0
            handedness = 3
            createNotesFile(path_data)
        elif situ == "ex":
            age = agebyExperimenter()
            handedness = handednessbyExperimenter()
            sex = sexbyExperimenter()
            createNotesFile(path_data)
            booleanValueStore(path_data, 'excluded', False)
            booleanValueStore(path_data, 'to_analyse', False)

        print(f"\nSubject's number within day: {subject_n}\n")
        print(f"\nSubject's age: {age}\n")

        todaydate, time_now = setSubjNumDec(age, subject_n, situ)

        ### ARDUINOS & ZABERS
        (
            zabers,
            arduinos
        ) = arduinos_zabers()

        # Save age, sex and subject number
        checkFilePathSave(path_data, "age", age, subject_n)
        checkFilePathSave(path_data, "sex", sex, subject_n)
        checkFilePathSave(path_data, "handedness", handedness, subject_n)
        saveIndvVar(path_data, subject_n, "temp_subj_n")

        #### MOVE TO FIRST POINT: DEFAULT POSITION
        height_check = False
        grid_data.positions["tactile"] = gridCalculation("tactile", separation_grid, rules, centre_grid_positions)
        print(grid_data.positions["tactile"])


        movetostartZabersConcu(
            zabers,
            "colther",
            list(reversed(haxes["colther"])),
            pos = dry_ice_pos,
        )

        movetostartZabersConcu(zabers, "camera", ["y"], {"y": 530000})
        movetostartZabersConcu(zabers, "tactile", ["x"], {"x": stability[1]['x']})

        movePanTilt(arduinos["pantilt"], park_pantilt)
        input("Press enter when you are ready to find the heights")

        movetostartZabersConcu(
            zabers,
            "tactile",
            haxes["tactile"],
            pos = grid_data.positions["tactile"][grid_data.current_roi],
        )

        ### Move Zaber TOUCH to each position
        gridUpDown(zabers, grid_data)

        homingZabersConcu(zabers, haxes)
        # save all z axis positions
        saveGridIndv("temp_grid", path_data, grid_data.positions, "tactile")
        rootToUser([path_day, path_anal, path_data, path_figs, path_videos])

        #### HOMER ARDUINOS & ZABERS
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
