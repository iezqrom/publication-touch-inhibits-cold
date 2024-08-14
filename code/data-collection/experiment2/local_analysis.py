import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os
from globals import data_path

# function to read an integer from a file

colour_roi = 'black'
radius_roi = 20
width_line_roi = 3

def animateSingle(
    i,
    data,
    axes,
):

    # First subplot: 2D RAW
    axes[0].clear()
    axes[0].imshow(data[i], cmap="coolwarm")

    axes[0].set_title("Thermal image")
    axes[0].set_axis_off()

    plt.tight_layout()


def animateROI(
    i,
    thermal_data,
    roi,
    axes,
):

    # First subplot: 2D RAW
    axes[0].clear()
    axes[0].imshow(thermal_data[i], cmap="coolwarm")

    axes[0].set_axis_off()

    plt.tight_layout()

    # draw a circle on the image
    circle = patches.Circle(
        (roi[i][0], roi[i][1]),
        radius_roi,
        linewidth = width_line_roi,
        edgecolor = colour_roi,
        facecolor = "none",
    )
    axes[0].add_patch(circle)


def animateFourPanels(
    i,
    thermal_data,
    roi,
    diff_data,
    temperatures,
    deltas,
    axes,
    bounds_thermal_image,
    bounds_difference
):
    print(roi[i][0], roi[i][1])

    # draw a circle
    circle = patches.Circle(
        (roi[i][0], roi[i][1]),
        radius_roi,
        linewidth = width_line_roi,
        edgecolor = colour_roi,
        facecolor = "none",
    )
    
    # First subplot: 2D RAW
    axes[0, 0].clear()
    axes[0, 0].imshow(thermal_data[i], cmap="coolwarm", vmin = bounds_thermal_image[0], vmax = bounds_thermal_image[1])
    # axes[0, 0].set_axis_off()
    circle = patches.Circle(
        (roi[i][1], roi[i][0]),
        radius_roi,
        linewidth = width_line_roi,
        edgecolor = colour_roi,
        facecolor = "none",
    )
    axes[0, 0].add_patch(circle)

    # Second subplot: 2D difference
    axes[0, 1].clear()
    axes[0, 1].imshow(diff_data[i], cmap="winter", vmin = bounds_difference[0], vmax = bounds_difference[1])
    # axes[0, 1].set_axis_off()
    circle = patches.Circle(
        (roi[i][1], roi[i][0]),
        radius_roi,
        linewidth = width_line_roi,
        edgecolor = colour_roi,
        facecolor = "none",
    )
    axes[0, 1].add_patch(circle)

    # Third temperature in ROI
    axes[1, 0].clear()
    axes[1, 0].plot(temperatures[:i], color="blue")
    axes[1, 0].set_xlim([0, len(temperatures)])
    axes[1, 0].set_ylim([25, 34])


    # Third temperature in ROI
    axes[1, 1].clear()
    axes[1, 1].plot(deltas[:i], color="blue")
    axes[1, 1].set_xlim([0, len(deltas)])
    axes[1, 1].set_ylim([-1, 3])

    plt.tight_layout()

def grabToAnalyse():
    # list all the folders in the data folder that start with ex_
    subject_folders = [f for f in os.listdir(data_path) if f.startswith('ex_')]
    # sort them
    subject_folders.sort()
    subject_folders_to_analyse = []
    for index, subject_folder in enumerate(subject_folders):
        with open(f"{data_path}/{subject_folder}/data/to_analyse.txt", "r") as f:
            to_analyse = f.read()
        # if it is False, then skip this iteration
        if to_analyse == "True":
            subject_folders_to_analyse.append(subject_folder)

    return subject_folders_to_analyse
