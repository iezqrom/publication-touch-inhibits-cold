import sys
sys.path.append('..')
from grabPorts import grabPorts
from globals import (
    centre_grid_positions,
    step_sizes,
    separation_grid,
    initial_staircase_temp,
    haxes,
    pantilts,
    rules
)
from zabers import gridCalculation
from saving_data import (
    csvToDictGridIndv,
    rootToUser,
    saveGridIndv,
    getSubjNumDec
)
from failing import errorloc
from index_funcs import parsingSituation, mkpaths
from local_functions import deltaToZaberHeight
from local_classes import gridData

if __name__ == "__main__":
    try:
        ports = grabPorts()
        print(ports.ports)

        situ, day, _ = parsingSituation()
        print(day)

        subject_n = getSubjNumDec(day=day)
        path_day, path_anal, path_figs, path_data, path_videos, path_audios = mkpaths(
            situ, numdaysubj=subject_n, folder_name=day
        )
        
        path_day_bit = path_day.rsplit("/", 3)[-1]
        grid_data = gridData(haxes, pantilts, 'colther')

        # Save age and subject number
        grid_data.positions["tactile"] = csvToDictGridIndv(path_data, "temp_grid_tactile.csv")

        grid_data.positions["colther"] = gridCalculation("colther", separation_grid, rules, centre_grid_positions)
        
        path_camera_grid = path_data.rsplit("/", 2)[0]
        grid_data.positions["camera"] = csvToDictGridIndv(path_camera_grid, "camera_grid.csv") #data/camera_grid.csv #gridCalculation("camera", separation_grid, rules, centre_grid_positions)

        for position in grid_data.positions["colther"].keys():
            grid_data.positions["colther"][position]["z"] = deltaToZaberHeight(
                initial_staircase_temp, grid_data.positions, position, step_sizes
            )

        # save all z axis positions
        print(grid_data.positions)
        # saveGridAll(path_data, grid_data.positions)
        saveGridIndv(f"temp_grid", path_data, grid_data.positions, "camera")
        saveGridIndv(f"temp_grid", path_data, grid_data.positions, "colther")
        rootToUser([path_day, path_anal, path_data, path_figs, path_videos])

    except Exception as e:
        errorloc(e)

    except KeyboardInterrupt:
        print("Keyboard Interrupt")
