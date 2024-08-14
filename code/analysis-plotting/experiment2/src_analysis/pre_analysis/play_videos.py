import os
import keyboard

# path to the folder containing the videos
video_dir = "/Users/ivan/Documents/aaa_online_stuff/coding/python/phd/experiment2_control/data/ex_20230217_2/animations"

# list all files in the folder
videos = os.listdir(video_dir)

# loop through all the videos and play each one
for video in videos:
    # construct the full path to the video file
    video_path = os.path.join(video_dir, video)

    # play the video using the default player on macOS
    os.system(f"open -a 'QuickTime Player' '{video_path}' --args -AutoPlay YES")

    # wait for the video player to exit before playing the next video
    while True:
        # check if the QuickTime Player process is still running
        if os.system("pgrep 'QuickTime Player' > /dev/null") != 0:
            break
        elif keyboard.is_pressed("e"):
            # if the user presses the q key, stop playing videos
            exit()