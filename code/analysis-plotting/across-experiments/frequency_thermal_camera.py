# %%
import sys 
sys.path.append("../../")

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
from plotting import (
    plotParams,
    removeSpines,
    prettifySpinesTicks,
    params_figure,
    colours,
    cohenD,
)
import os

from globals import data_path, figures_path, videos_path
import json

def weighted_average_hz_calculation(timestamps):
    """
    Calculates a weighted average Hz based on the intervals between consecutive timestamps,
    where longer intervals have less influence on the average.

    Parameters:
    timestamps (list): A list of numpy arrays, each containing a single timestamp float.

    Returns:
    float: The weighted average Hz.
    """
    # Convert list of numpy arrays to a list of floats
    flat_timestamps = np.sort([ts[0] for ts in timestamps])

    # Compute intervals between consecutive timestamps
    intervals = np.diff(flat_timestamps)

    # Avoid division by zero by filtering out zero intervals if any exist
    non_zero_intervals = intervals[intervals > 0]

    # Calculate frequencies as the reciprocal of intervals
    frequencies = 1 / non_zero_intervals

    # Weights are reciprocal of the intervals, meaning longer intervals have less weight
    weights = 1 / non_zero_intervals

    # Calculate the weighted average of frequencies
    weighted_average_hz = np.average(frequencies, weights=weights) if frequencies.size > 0 else 0

    return weighted_average_hz

def interval_based_hz_calculation(timestamps):
    """
    Calculates the average Hz based on the inverse of intervals between consecutive timestamps.

    Parameters:
    timestamps (list): A list of numpy arrays, each containing a single timestamp float.

    Returns:
    float: The average Hz calculated as the inverse of the average of intervals between timestamps.
    """
    # Convert list of numpy arrays to a list of floats
    flat_timestamps = np.sort([ts[0] for ts in timestamps])

    # Compute intervals between consecutive timestamps
    intervals = np.diff(flat_timestamps)

    # Avoid division by zero by filtering out zero intervals if any exist
    non_zero_intervals = intervals[intervals > 0]

    # Calculate frequencies as the reciprocal of intervals
    frequencies = 1 / non_zero_intervals

    # Calculate the average Hz
    average_hz = np.mean(frequencies) if frequencies.size > 0 else 0

    return average_hz

def calculate_timestamps_hz(timestamps):
    """
    Calculates the number of timestamps in each full second and the average Hz of timestamps.

    Parameters:
    timestamps (list): A list of numpy arrays, each containing a single timestamp float.

    Returns:
    tuple:
        - dict: A dictionary with keys being the second and values the count of timestamps in that second.
        - float: The average Hz (frequency) of timestamps per second.
    """
    # Convert list of numpy arrays to a list of floats
    flat_timestamps = [ts[0] for ts in timestamps]

    # Extract integer parts to represent full seconds
    seconds = np.floor(flat_timestamps).astype(int)

    # Determine the maximum complete second
    max_complete_second = int(max(seconds))

    # Count timestamps in each full second
    counts_per_second = {}
    for second in range(max_complete_second + 1):
        counts_per_second[second] = np.sum(seconds == second)

    # Calculate average Hz, excluding incomplete final second
    total_counts = sum(counts_per_second.values())
    num_full_seconds = len(counts_per_second)
    average_hz = total_counts / num_full_seconds if num_full_seconds > 0 else 0

    return counts_per_second, average_hz


plotParams(size = 40)
# %%
data = {'experiment1': {}, 'experiment2': {}, 'experiment3': {}}
name_exp_folder = ['experiment1', 'experiment2', 'experiment3']
# add the name_sdt_file as 'file_name' to data dict
for n_exp, exp in enumerate(data.keys()):
    data[exp]['folder_name'] = name_exp_folder[n_exp]


# %%
for n_exp, exp in enumerate(data.keys()):
    exp_folder = f"{data_path}/experiment{n_exp + 1}"
    # get all the folders and only folders in the experiment folder
    folders = [f for f in os.listdir(exp_folder) if os.path.isdir(f"{exp_folder}/{f}")]
    # read the value of the file 'data/to_analyse.txt' in each folder
    to_analyse = []
    for folder in folders:
        with open(f"{exp_folder}/{folder}/data/to_analyse.txt", "r") as f:
            to_analyse.append(f.read())

    # get the names of the folders to analyse basde on the boolean array to_analyse
    to_analyse_folders = list(np.array(folders)[np.array(to_analyse) == 'True'])
    
    # check whether the corresponding file in data[n_exp+1] is in the folders to analyse data/ folders
    data[exp]['to_analyse'] = to_analyse_folders

# %%
# iterate over the folders to analyse for each experiment at at the videos_path/{folder_name}/data/ folder and list all the videos in path/{folder_name}/data/{to_analyse}/videos/
for n_exp, exp in enumerate(data.keys()):
    # create dictionary to store the frequencies
    data[exp]['frequencies'] = {}
    # create a list for each type of frequency
    data[exp]['frequencies']['weighted_average'] = []
    data[exp]['frequencies']['interval_based'] = []
    data[exp]['frequencies']['timestamps_hz'] = []

    for folder in data[exp]['to_analyse']:
        folder_path = rf"{videos_path}/{data[exp]['folder_name']}/data/{folder}/videos"
        if os.path.exists(folder_path):
            videos = os.listdir(folder_path)
            # remove those that do not end with .hdf5
            videos = [v for v in videos if v.endswith(".hdf5")]
            # remove those that include training and staircase
            videos = [v for v in videos if not ("training" in v or "staircase" in v)]

            print(f"Videos in {folder_path}: {videos}")

            # iterate over the videos and extract the timestamps
            for video in videos:
                try:
                    #remove the extension
                    video = video.split(".")[0]
                    video_data = ReAnRaw(f"{folder_path}/{video}")
                    video_data.datatoDic()
                    timestamps = video_data.data['time_now']

                    # Calculate frequencies
                    weighted_average_hz = weighted_average_hz_calculation(timestamps)
                    interval_based_hz = interval_based_hz_calculation(timestamps)
                    timestamps_hz = calculate_timestamps_hz(timestamps)

                    # Append frequencies to the list
                    data[exp]['frequencies']['weighted_average'].append(weighted_average_hz)
                    data[exp]['frequencies']['interval_based'].append(interval_based_hz)
                    data[exp]['frequencies']['timestamps_hz'].append(timestamps_hz[1])
                except Exception as e:
                    print(f"Error processing video {video}: {e}")

# %%
# iterate and extract mean per experiment and frequency type
for n_exp, exp in enumerate(data.keys()):
    # create a mean key to store the mean of the frequencies
    data[exp]['mean_frequency'] = {}
    for freq_type in data[exp]['frequencies'].keys():
        data[exp]['mean_frequency'][freq_type] = np.mean(data[exp]['frequencies'][freq_type])

# %%
# iterate and get the mean and std of the frequencies
for n_exp, exp in enumerate(data.keys()):
    # create a mean key to store the mean of the frequencies
    data[exp]['mean_frequency'] = {}
    data[exp]['std_frequency'] = {}
    for freq_type in data[exp]['frequencies'].keys():
        data[exp]['mean_frequency'][freq_type] = np.mean(data[exp]['frequencies'][freq_type])
        data[exp]['std_frequency'][freq_type] = np.std(data[exp]['frequencies'][freq_type])
# %%
# print the mean and std of the frequencies
for n_exp, exp in enumerate(data.keys()):
    print(f"Experiment {n_exp + 1}")
    for freq_type in data[exp]['mean_frequency'].keys():
        print(f"Frequency type: {freq_type}")
        print(f"Mean: {data[exp]['mean_frequency'][freq_type]}")
        print(f"Std: {data[exp]['std_frequency'][freq_type]}")
# %%
# now let's focus on the timestamps_hz and get the mean and std across experiments
timestamps_hz = []
for n_exp, exp in enumerate(data.keys()):
    timestamps_hz.append(data[exp]['frequencies']['timestamps_hz'])

timestamps_hz = np.array(timestamps_hz)
# flatten
timestamps_hz = timestamps_hz.flatten()
# merge lists
timestamps_hz = np.concatenate(timestamps_hz)

mean_timestamps_hz = np.mean(timestamps_hz)
std_timestamps_hz = np.std(timestamps_hz)

print(f"Mean timestamps Hz: {mean_timestamps_hz}")
print(f"Std timestamps Hz: {std_timestamps_hz}")
# %%
# calculate the range of the timestamps_hz
range_timestamps_hz = np.ptp(timestamps_hz)
print(f"Range timestamps Hz: {range_timestamps_hz}")
# get the min and max bounds
min_timestamps_hz = np.min(timestamps_hz)
max_timestamps_hz = np.max(timestamps_hz)
print(f"Min timestamps Hz: {min_timestamps_hz}")
print(f"Max timestamps Hz: {max_timestamps_hz}")
# %%
