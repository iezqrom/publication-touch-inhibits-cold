#this script analyses the thermal videos
# it either gets the parameters from the terminal (parser) or from the file subject_name.txt
import sys
sys.path.append("../..")
sys.path.append("..")
from tharnal import ReAnRaw
from globals import data_path, vmin_file_name, vmax_file_name
from saving_data import checkORcreate

from local_analysis import animateFourPanels
from local_functions import readNumber
import numpy as np
from matplotlib import animation
import os
import matplotlib.pyplot as plt


if __name__ == "__main__":
    
    date = "20230217_2"
    situ = "ex"
    name_folder = situ + "_" + date
    
    print(f"Participant folder: {name_folder}")

    # list all the videos in the videos folder of the participant/data
    # check whether the folder exists with tb or ex at the beginning of the name
    if os.path.isdir(f"{data_path}/{name_folder}/videos/"):
        videos = os.listdir(f"{data_path}/{name_folder}/videos/")
        videos = [video for video in videos if video != ".DS_Store"]

    else:
        print("No videos folder")
        exit()
    
    print(f"Videos: {videos}")

    path_animation = checkORcreate(f"{data_path}/{name_folder}/animations")

    # check whether the vmin and vmax values are already saved
    if os.path.isfile(f'{data_path}/{vmin_file_name}.txt') and os.path.isfile(f'{data_path}/{vmax_file_name}.txt'):
        # if yes, use them
        tmin = readNumber(data_path, vmin_file_name)
        tmax = readNumber(data_path, vmax_file_name)
    else:
        # if no, use the default values
        tmin = 30
        tmax = 34

    print(f"tmin: {tmin}, tmax: {tmax}")

    # loop through the videos
    for video_dot in videos:
        # if yes, analyse the video
        print(f"Analysing {video_dot}")
        # get the name of the video
        video = video_dot.split(".")[0]
        data = ReAnRaw(f"{data_path}/{name_folder}/videos/{video}")
        data.datatoDic()

        Writer = animation.writers["ffmpeg"]
        writer = Writer(fps=9, metadata=dict(artist="Me"), bitrate=1800)


        ################ Plot figure
        # init figure with 4 subplots
        figs, axes = plt.subplots(2, 2, figsize=(10, 10))

        #######################Axes
        x = np.arange(0, 160, 1)
        y = np.arange(0, 120, 1)

        xs, ys = np.meshgrid(x, y)
        zs = (xs * 0 + 15) + (ys * 0 + 15)

        ######################Plots
        ## First subplot
        plot1 = axes[0, 0].imshow(zs, cmap="coolwarm", vmin=tmin, vmax=tmax)
        cb = figs.colorbar(plot1, ax = axes[0, 0])
        cb.set_ticks(np.arange(tmin, (tmax + 0.01), 2))

        ## Second subplot
        plot2 = axes[0, 1].imshow(zs, cmap="winter", vmin = -1, vmax = 3)
        cb = figs.colorbar(plot2, ax = axes[0, 1])
        cb.set_ticks(np.arange(-1, (3 + 0.01), 1))

        ## Third subplot
        plot3 = axes[1, 0].plot(
            np.arange(len(data.data["image"])),
            data.data["roi_temperature"],
            color="black",
        )

        ## Fourth subplot
        plot4 = axes[1, 1].plot(
            np.arange(len(data.data["image"])),
            data.data["delta"],
            color="black",
        )

        bounds_thermal_image = (tmin, tmax)
        bounds_difference = (-1, 3)
        ani = animation.FuncAnimation(
            figs,
            animateFourPanels,
            frames=len(data.data["image"]),
            fargs=(
                data.data["image"],
                data.data["ROI_coordinates"],
                data.data["image_difference"],
                data.data["roi_temperature"],
                data.data["delta"],
                axes,
                bounds_thermal_image,
                bounds_difference

            ),
            interval=1000 / 8.7,
        )
        mp4_name = "mp4_" + video
        print(f"Generating animation as {mp4_name}.mp4")
        ani.save(f"{path_animation}/{mp4_name}.mp4", writer=writer)

        figs.clf()
