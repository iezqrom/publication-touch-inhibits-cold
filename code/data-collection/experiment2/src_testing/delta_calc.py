import sys
sys.path.append('..')
from saving_data import (
    rootToUser,
    saveIndvVar,
    csvToDictGridIndv,
    saveGridIndv,
    getSubjNumDec
)
from index_funcs import parsingSituation, mkpaths
from failing import errorloc, recoverPickleRick
from globals import step_sizes, staircases_info, haxes, pantilts, adjust_colther
from text import printme
from local_functions import deltaToZaberHeight
from local_classes import gridData

import numpy as np

if __name__ == "__main__":
    try:
        situ, day, n_staircase = parsingSituation()
        subject_n = getSubjNumDec(day=day)
        path_day, path_anal, path_figs, path_data, path_videos, path_audios = mkpaths(
            situ, numdaysubj = subject_n, folder_name=day
        )

        rootToUser([path_day, path_anal, path_data, path_figs, path_videos, path_audios])

        grid_data = gridData(haxes, pantilts, 'colther')

        # Import data data
        grid_data.positions["colther"] = csvToDictGridIndv(path_data, "temp_grid_colther.csv")
        grid_data.positions["tactile"] = csvToDictGridIndv(path_data, "temp_grid_tactile.csv")

        print(grid_data.positions["colther"])

        estimated_points = []
        for staircase_index in staircases_info:
            name_staircase_file = (
                f"online_back_up_staircase_{staircases_info[staircase_index]['direction']}"
            )
            staircase = recoverPickleRick(path_data, name_staircase_file)

            # Get delta estimation
            staircase.estimateValue()
            printme(f"Estimated point: {staircase.estimated_point}")
            # Save delta estimation
            saveIndvVar(path_data, staircase.estimated_point, "temp_delta")
            # Plot staircase and save
            staircase.plotStaircase(
                path_figs,
                f"staircase_{staircases_info[staircase_index]['direction']}",
                "Delta",
                [0, 3],
                show=False,
            )
            estimated_points.append(staircase.estimated_point)

        mean_estimated_point = np.mean(estimated_points)
        # Calculate colther height for each position with estimated delta
        for position in grid_data.positions["colther"].keys():
            grid_data.positions["colther"][position]["z"] = deltaToZaberHeight(
                mean_estimated_point - adjust_colther, grid_data.positions, position, step_sizes
            )
        # Save colther grid
        saveGridIndv(f"temp_grid", path_data, grid_data.positions, "colther")

        # Set folder permissions to current user
        rootToUser([path_day, path_anal, path_data, path_figs, path_videos])

    except Exception as e:
        errorloc(e)
        rootToUser([path_day, path_anal, path_data, path_figs, path_videos, path_audios])

    except KeyboardInterrupt:
        print("Keyboard Interrupt")
        rootToUser([path_day, path_anal, path_data, path_figs, path_videos, path_audios])
