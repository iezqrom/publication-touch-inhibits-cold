# %% Script to animate sdt trials

from classes_tharnalBeta import ReAnRaw
from matplotlib import animation
import mpl_toolkits.mplot3d.axes3d as p3

colorMapType = 0
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib import animation

### Data structure
import numpy as np

## Media
from imutils.video import VideoStream
from classes_tharnal import *
from classes_plotting import *
from datetime import date
import pandas as pd
import time
import argparse
from saving_data import *

# %%
# todaydate = '07122020'
# head_folder = 'test'
# folder_name = head_folder + '_' + todaydate

# n = 'sdt_subj3_trial3_pos7'
# dat_im = ReAnRaw(f'../data/{folder_name}/videos/{n}')
# dat_im.datatoDic()


# %%

# if np.shape(dat_im.data['diff_ROI'][31])[1] == 2:
#     print(dat_im.data['diff_ROI'][30][:, 0])
# else:
#     print('hello')

# [::-1]


# %%

if __name__ == "__main__":
    # parser = argparse.ArgumentParser(description='Experimental situation: troubleshooting (tb) or experimenting (ex)')
    # parser.add_argument("-s", type=str)
    # args = parser.parse_args()
    # situ = args.s
    # if situ != 'ex' and situ != 'tb':
    #     raise Exception("Only 'ex' and 'tb' are valid arguments")

    todaydate = date.today().strftime("%d%m%Y")
    # when_anal = input(f"Input date (DDMMYYYY) or press enter to get today's date {todaydate}:  ")
    # subj = input('Subject number: ')
    # subj = int(subj)

    # if len(when_anal) != 0:
    # todaydate = when_anal

    todaydate = "11062021_"

    subj = 1

    # if situ == 'tb':
    #     head_folder = 'tb'
    # elif situ == 'ex':
    #     head_folder = 'test'

    # todaydate = '01122020'
    folder_name = "tb" + "_" + todaydate
    # os.chdir('/Users/ivanezqrom/Documents/AAA_online_stuff/Coding/python/phd/expt4_py_nontactileCold/src_analysis')
    print(folder_name)
    path_animation = checkORcreate(f"../data/{folder_name}/animations")
    print(path_animation)

    ### SUBJECT

    # pattern = f'sdt_{subj}.*\.hdf5$'
    pattern = f"sdt_.*\.hdf5$"
    # filenname = ''

    # filename = 'data_subj'
    filename = "data_all"
    # filename = 'temp_data'

    table_data = pd.read_csv(f"../data/{folder_name}/data/{filename}.csv")
    cold_bool = np.asarray(table_data["cold"])
    touch_bool = np.asarray(table_data["touch"])
    responses_bool = np.asarray(table_data["responses"])

    patternc = re.compile(pattern)
    names = []

    for filename in os.listdir(f"../data/{folder_name}/videos/"):
        if patternc.match(filename):
            print(filename)
            name, form = filename.split(".")
            names.append(name)
        else:
            continue

    names.sort(key=natural_keys)
    print(names)

    tdus = todaydate.split(todaydate)

    pattern_delta = f"delta_.*\_{tdus[0]}.*\.txt"
    patternc_delta = re.compile(pattern_delta)
    print(patternc_delta)
    names_delta = []

    for filename in os.listdir(f"../data/{folder_name}/data/"):
        # print(filename)
        if patternc_delta.match(filename):
            # print(filename)
            name, form = filename.split(".")
            names_delta.append(name)
        else:
            continue

    names_delta.sort(key=natural_keys)
    print(names_delta)
    # names_delta = 'delta_failed_18032021_13_08_46'

    with open(f"../data/{folder_name}/data/{names_delta[0]}.txt") as f:
        var = f.readline()
        delta_value = float(var)

    print(f"DELTA: {delta_value}")

    if np.isnan(delta_value):
        delta_value = 0.1
        printme("DELTA IS NAN")

    # ANIMATION
    for i, n in enumerate(names):
        print(n)
        if cold_bool[i] == 1:
            dat_im = ReAnRaw(f"../data/{folder_name}/videos/{n}")
            dat_im.datatoDic()
            # if len(dat_im.data['time_now']) < 50:
            print(n)
            print(dat_im.data["time_now"][-1])
            means = []
            # print(dat_im.data['sROI'])
            # print(dat_im.data['shutter_pos'])
            ######################
            # dat_im.data['eud'] = np.arange(0, len(dat_im.data['image']) + 0.1, 1)
            ######################

            Writer = animation.writers["ffmpeg"]
            writer = Writer(fps=9, metadata=dict(artist="Me"), bitrate=1800)
            vminT = 29
            vmaxT = 34

            def animate(
                i,
                data,
                plots,
                axs,
                fixed_coor,
                diff_coor,
                means,
                sROI,
                baseline_buffer,
                deltas,
                shutter,
                delta_value,
                momen,
                baseline_frames_buffer,
                shutter_state,
            ):
                # print(shutter_state)
                widthtick = 3
                title_pad = 20
                lwD = 5
                widthtick = 5
                lenD = 15
                r = 20

                shutter_closed = 4
                shutter_open = 2

                # First subplot: 2D RAW
                ax1.clear()
                xs = np.arange(0, 160)
                ys = np.arange(0, 120)

                circles = []

                if sROI[i] == 1:
                    if np.shape(diff_coor[i])[1] > 1:
                        cdif = diff_coor[i][:, 0]
                        # print(cdif)
                        cy = cdif[1]
                        cx = cdif[0]
                    else:
                        cdif = diff_coor[i]
                        cy = cdif[1][0]
                        cx = cdif[0][0]

                    cir = plt.Circle(cdif[::-1], r, color="b", fill=False, lw=lwD * 1.2)
                    # print(diff_coor[i][0])
                    mask = (xs[np.newaxis, :] - cy) ** 2 + (
                        ys[:, np.newaxis] - cx
                    ) ** 2 < r**2
                    roiC = data[i][mask]
                    temp = round(np.mean(roiC), 2)
                    means.append(temp)

                elif sROI[i] == 0:
                    cir = plt.Circle(
                        fixed_coor[i][::-1], r, color="b", fill=False, lw=lwD * 1.2
                    )
                    mask = (xs[np.newaxis, :] - fixed_coor[i][1]) ** 2 + (
                        ys[:, np.newaxis] - fixed_coor[i][0]
                    ) ** 2 < r**2
                    roiC = data[i][mask]
                    temp = round(np.mean(roiC), 2)
                    means.append(temp)

                ax1.imshow(data[i], cmap="hot", vmin=vminT, vmax=vmaxT)
                ax1.add_artist(cir)

                ax1.set_title("Thermal image", pad=title_pad)
                ax1.set_axis_off()

                # Second subplot: 2D RAW
                if shutter[i] == shutter_closed:
                    x = np.arange(0, 160, 1)
                    y = np.arange(0, 120, 1)
                    xs, ys = np.meshgrid(x, y)
                    difframe = (xs * 0) + (ys * 0)

                    if momen[i] > 1.6 and momen[i] < 2:
                        baseline_frames_buffer.append(data[i])

                elif shutter[i] == shutter_open:
                    if len(shutter_state) == 0:
                        shutter_time_open = time.time()
                        shutter_state.append(shutter_time_open)
                        # print(shutter_state)

                    meaned_baseline = np.mean(baseline_frames_buffer, axis=0)
                    # print(meaned_baseline, )
                    difframe = meaned_baseline - data[i]
                    difframe[data[i] <= 28] = 0
                    maxdif = np.max(difframe)
                    # print(f'Max dif {maxdif}')
                    # print(f'Time shutter open {time.time() - shutter_state[0]}')

                else:
                    x = np.arange(0, 160, 1)
                    y = np.arange(0, 120, 1)
                    xs, ys = np.meshgrid(x, y)
                    difframe = (xs * 0) + (ys * 0)

                ax4.clear()
                ax4.imshow(difframe, cmap="winter", vmin=vminDF, vmax=vmaxDF)
                # ax4.add_artist(cir)
                ax4.set_title("Thermal difference image", pad=title_pad)

                # MEAN TEMPERATURE
                ax2.clear()
                ax2.plot(means, lw=lwD * 1.2, color="#007CB7")
                ax2.set_ylim([27, 34])
                ax2.set_xlim([0, len(means)])
                ax2.set_title("Mean temperature fixed ROI", pad=title_pad)

                steps = 1
                framesToseconds(ax2, steps, data)

                ax2.spines["top"].set_visible(False)
                ax2.spines["right"].set_visible(False)

                ax2.yaxis.set_tick_params(width=lwD, length=lenD)
                ax2.xaxis.set_tick_params(width=lwD, length=lenD)

                ax2.tick_params(axis="y", which="major", pad=10)
                ax2.tick_params(axis="x", which="major", pad=10)

                ax2.spines["left"].set_linewidth(lwD)
                ax2.spines["bottom"].set_linewidth(lwD)
                ax2.set_xlabel("Time (s)")

                # ########
                # if shutter[i] == shutter_closed: # closed
                #     delta = 0
                #     baseline_buffer.append(temp)

                # elif shutter[i] == shutter_open: #open
                #     mean_baseline = np.mean(baseline_buffer)
                #     delta = mean_baseline - temp
                # else:
                #     delta = 0

                # deltas.append(delta)

                # Delta
                ax3.clear()
                ax3.plot(deltas[:i], lw=lwD * 1.2, color="#007CB7")
                ax3.set_ylim([0, 3])
                ax3.set_xlim([0, len(means)])
                ax3.set_title("Delta", pad=title_pad)
                ax3.axhline(delta_value, 0, len(means), color="b", ls="--")

                framesToseconds(ax3, steps, data)

                ax3.spines["top"].set_visible(False)
                ax3.spines["right"].set_visible(False)

                ax3.yaxis.set_tick_params(width=lwD, length=lenD)
                ax3.xaxis.set_tick_params(width=lwD, length=lenD)

                ax3.tick_params(axis="y", which="major", pad=10)
                ax3.tick_params(axis="x", which="major", pad=10)

                ax3.spines["left"].set_linewidth(lwD)
                ax3.spines["bottom"].set_linewidth(lwD)
                ax3.set_xlabel("Time (s)")

                plt.tight_layout()

            ################ Plot figure
            fig = plt.figure(figsize=(35, 20))

            mc = "black"
            plt.rcParams.update(
                {
                    "font.size": 40,
                    "axes.labelcolor": "{}".format(mc),
                    "xtick.color": "{}".format(mc),
                    "ytick.color": "{}".format(mc),
                    "font.family": "sans-serif",
                }
            )

            #######################Axes
            ax1 = fig.add_subplot(221)
            ax2 = fig.add_subplot(223)
            ax3 = fig.add_subplot(224)
            ax4 = fig.add_subplot(222)

            x = np.arange(0, 160, 1)
            y = np.arange(0, 120, 1)

            xs, ys = np.meshgrid(x, y)
            zs = (xs * 0 + 15) + (ys * 0 + 15)

            ######################Plots
            ## First subplot: 2D video
            plot1 = ax1.imshow(zs, cmap="hot", vmin=vminT, vmax=vmaxT)
            cb = fig.colorbar(plot1, ax=ax1)
            cb.set_ticks(np.arange(vminT, (vmaxT + 0.01), 1))

            vminDF = 0
            vmaxDF = delta_value
            plot4 = ax1.imshow(zs, cmap="winter", vmin=vminDF, vmax=vmaxDF)
            cbdif = fig.colorbar(plot4, ax=ax4)
            cbdif.set_ticks(np.arange(vminDF, (vmaxDF + 0.01), 1))

            ## Second subplot: mean ROI
            plot2 = ax2.plot(
                np.arange(len(dat_im.data["image"])),
                np.arange(len(dat_im.data["image"])),
                color="black",
            )

            ## Third subplot:
            plot3 = ax3.plot(
                np.arange(len(dat_im.data["image"])),
                np.arange(len(dat_im.data["image"])),
                color="black",
            )

            # Aesthetics
            plots = [plot1, plot2, plot3]
            axes = [ax1, ax2, ax3]

            baseline_buffer = []
            delta = []
            baseline_frames_buffer = []

            # Animation & save
            shutter_state = []
            ani = animation.FuncAnimation(
                fig,
                animate,
                frames=len(dat_im.data["image"]),
                fargs=(
                    dat_im.data["image"],
                    plots,
                    axes,
                    dat_im.data["fixed_ROI"],
                    dat_im.data["diff_ROI"],
                    means,
                    dat_im.data["sROI"],
                    baseline_buffer,
                    dat_im.data["delta"],
                    dat_im.data["shutter_pos"],
                    delta_value,
                    dat_im.data["time_now"],
                    baseline_frames_buffer,
                    shutter_state,
                ),
                interval=1000 / 8.7,
            )

            mp4_name = "mp4_" + n + f"_cold_{cold_bool[i]}" + f"_touch_{touch_bool[i]}"
            # mp4_name = 'mp4_' + n
            ani.save(f"./{path_animation}/{mp4_name}.mp4", writer=writer)

            fig.clf()


# print(dat_im.data['eud'])delta_value

# dat_im.data['eud']

# %%
# try:
#     if diff_coor[i][0] != -1:
#         patch = True
#     else:
#         patch = False
# except:
#     patch = True

# if sROI[i] ==  1:
# print(diff_coor[i])
# if patch:
#     if np.shape(diff_coor[i])[1] > 1:
#         cdif = diff_coor[i][:, 0]
#         cy = cdif[1]
#         cx = cdif[0]
#     else:
#         cdif = diff_coor[i]
#         cy = cdif[1][0]
#         cx = cdif[0][0]

#     print(cdif)

#     cir = plt.Circle(cdif[::-1], r, color='b', fill = False, lw=lwD*1.2)
#     # print(diff_coor[i][0])
#     mask = (xs[np.newaxis,:] - cy)**2 + (ys[:,np.newaxis] - cx)**2 < r**2
#     roiC = data[i][mask]
#     temp = round(np.mean(roiC), 2)
#     means.append(temp)
# else:
#     cir = plt.Circle(fixed_coor[i][::-1], r, color='b', fill = False, lw=lwD*1.2)
#     mask = (xs[np.newaxis,:] - fixed_coor[i][1])**2 + (ys[:,np.newaxis] - fixed_coor[i][0])**2 < r**2
#     roiC = data[i][mask]
#     temp = round(np.mean(roiC), 2)
#     means.append(temp)
