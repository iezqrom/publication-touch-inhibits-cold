# Script to animate mol trials
# %%
from tharnal import ReAnRaw
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
from tharnal import *
from plotting import *
from datetime import date
from saving_data import *

if __name__ == "__main__":

    todaydate = "testing"

    folder_name = "tb" + "_" + todaydate
    path_animation = checkORcreate(f"../data/{folder_name}/animations")

    # %% SUBJECT
    pattern = f"staircase.*\.hdf5$"

    patternc = re.compile(pattern)
    names = []

    for filename in os.listdir(f"../data/{folder_name}/videos/"):
        if patternc.match(filename):
            # print(filename)
            name, form = filename.split(".")
            names.append(name)
        else:
            continue

    names.sort(key=natural_keys)
    print(names)

    # ANIMATION

    for n in names:
        print(n)
        dat_im = ReAnRaw(f"../data/{folder_name}/videos/{n}")
        dat_im.datatoDic()
        dat_im.extractMeans(name_coor="diff_ROI")

        shuopen = np.asarray(dat_im.data["sROI"])
        iopen = np.where(shuopen[:-1] != shuopen[1:])[0]
        iopen = iopen[0]
        devs = np.zeros(iopen)
        mean_dev = dat_im.means[iopen:]
        devs = np.append(devs, np.gradient(mean_dev))

        Writer = animation.writers["ffmpeg"]
        writer = Writer(fps=9, metadata=dict(artist="Me"), bitrate=1800)
        vminT = 31
        vmaxT = 36
        means = []

        def animate(
            i,
            data,
            plots,
            axs,
            fixed_coor,
            diff_coor,
            sROI,
            means,
            baseline_buffer,
            deltas,
            shutter,
            baseline_frames_buffer,
            devs,
            momen,
        ):
            widthtick = 3
            title_pad = 20
            lwD = 5
            widthtick = 5
            lenD = 15
            r = 20

            shutter_closed = 4
            shutter_open = 2

            xs = np.arange(0, 160)
            ys = np.arange(0, 120)

            # First subplot: 2D RAW
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

            ax1.clear()
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

                if momen[i] > 1.5 and momen[i] < 1.9:
                    baseline_frames_buffer.append(data[i])

            elif shutter[i] == shutter_open:
                meaned_baseline = np.mean(baseline_frames_buffer, axis=0)
                # print(np.shape(meaned_baseline))
                difframe = meaned_baseline - data[i]

            elif shutter[i] == 0:
                x = np.arange(0, 160, 1)
                y = np.arange(0, 120, 1)
                xs, ys = np.meshgrid(x, y)
                difframe = (xs * 0) + (ys * 0)

                if momen[i] > 1.5 and momen[i] < 1.9:
                    baseline_frames_buffer.append(data[i])

            # print(difframe)

            ax4.clear()
            ax4.imshow(difframe, cmap="winter", vmin=vminDF, vmax=vmaxDF)
            # ax4.add_artist(cir)
            ax4.set_title("Thermal difference image", pad=title_pad)

            # MEAN TEMPERATURE
            r = 20
            xs = np.arange(0, 160)
            ys = np.arange(0, 120)

            ax2.clear()
            ax2.plot(means, lw=lwD * 1.2, color="#007CB7")
            ax2.set_ylim([27, 34])
            ax2.set_xlim([0, len(data)])
            ax2.set_title("Delta", pad=title_pad)

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

            ax3.clear()
            # print(deltas[:i])
            ax3.plot(deltas[:i], lw=lwD * 1.2, color="k")
            ax3.set_ylim([0, 3])
            ax3.set_xlim([0, len(data)])
            ax3.set_title("Delta", pad=title_pad)

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

            ax5.clear()
            # print(devs[:i])
            ax5.plot(devs[:i], lw=lwD * 1.2, color="k")
            ax5.set_ylim([-3, 1])
            ax5.set_xlim([0, len(data)])
            ax5.set_title("Derivative of temperature", pad=title_pad)

            # print(steps)

            framesToseconds(ax5, steps, data)

            ax5.spines["top"].set_visible(False)
            ax5.spines["right"].set_visible(False)

            ax5.yaxis.set_tick_params(width=lwD, length=lenD)
            ax5.xaxis.set_tick_params(width=lwD, length=lenD)

            ax5.tick_params(axis="y", which="major", pad=10)
            ax5.tick_params(axis="x", which="major", pad=10)

            ax5.spines["left"].set_linewidth(lwD)
            ax5.spines["bottom"].set_linewidth(lwD)
            ax5.set_xlabel("Time (s)")

            plt.tight_layout()

        ################ Plot figure
        fig = plt.figure(figsize=(35, 30))

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
        ax1 = fig.add_subplot(321)
        ax4 = fig.add_subplot(322)
        ax2 = fig.add_subplot(323)
        ax3 = fig.add_subplot(324)
        ax5 = fig.add_subplot(325)

        x = np.arange(0, 160, 1)
        y = np.arange(0, 120, 1)

        xs, ys = np.meshgrid(x, y)
        zs = (xs * 0 + 15) + (ys * 0 + 15)

        ######################Plots
        ## First subplot: 2D video
        plot1 = ax1.imshow(zs, cmap="hot", vmin=vminT, vmax=vmaxT)
        cb = fig.colorbar(plot1, ax=ax1)
        cb.set_ticks(np.arange(vminT, (vmaxT + 0.01), 1))

        vminDF = -1
        vmaxDF = 2
        plot4 = ax1.imshow(zs, cmap="winter", vmin=vminDF, vmax=vmaxDF)
        cbdif = fig.colorbar(plot4, ax=ax4)
        cbdif.set_ticks(np.arange(vminDF, (vmaxDF + 0.01), 1))

        ## second subplot: mean ROI
        plot2 = ax2.plot(
            np.arange(len(dat_im.data["image"])),
            np.arange(len(dat_im.data["image"])),
            color="#007CB7",
        )

        ## third subplot: difference
        plot3 = ax3.plot(
            np.arange(len(dat_im.data["image"])),
            np.arange(len(dat_im.data["image"])),
            color="#007CB7",
        )

        plot5 = ax5.plot(
            np.arange(len(dat_im.data["image"])),
            np.arange(len(dat_im.data["image"])),
            color="#007CB7",
        )

        # Aesthetics
        plots = [plot1, plot2, plot3, plot4, plot5]
        axes = [ax1, ax2, ax3, ax4, ax5]

        baseline_buffer = []
        delta = []
        baseline_frames_buffer = []

        # Animation & save
        print(len(dat_im.data["image"]))
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
                dat_im.data["sROI"],
                means,
                baseline_buffer,
                dat_im.data["delta"],
                dat_im.data["shutter_pos"],
                baseline_frames_buffer,
                devs,
                dat_im.data["time_now"],
            ),
            interval=1000 / 8.7,
        )

        mp4_name = "mp4_" + n
        ani.save(f"./{path_animation}/{mp4_name}.mp4", writer=writer)
        print("HERE")

        fig.clf()
