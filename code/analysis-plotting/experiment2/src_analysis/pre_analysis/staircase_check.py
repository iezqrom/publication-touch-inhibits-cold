# %%
import sys
sys.path.append("../..")
from failing import recoverPickleRick
from globals import data_path, staircases_info

mode = "staircase"
date = "check"
staircases = []
for staircase in staircases_info:
    name_staircase_file = f"online_back_up_staircase_{staircases_info[staircase]['direction']}"
    subject_path = f"{data_path}/{mode}_{date}/data"
    staircases.append(recoverPickleRick(subject_path, name_staircase_file))

print(staircases)
# %%
# function to print all the attributes of an object
def print_attributes(obj):
    for attr in dir(obj):
        if not attr.startswith("__"):
            print("obj.%s = %r" % (attr, getattr(obj, attr)))
print_attributes(staircases[0])
# %%
path_figs = "/Users/ivan/Documents/aaa_online_stuff/coding/python/phd/experiment2_control/data/staircase_check/figs"
for staircase_index, staircase in enumerate(staircases):
    staircase.estimateValue()
    print(f"Estimated point: {staircase.estimated_point}")
    # Save delta estimation
    # Plot staircase and save
    staircase.plotStaircase(
        path_figs,
        f"staircase_{staircases_info[staircase_index]['direction']}",
        "Delta",
        [-1, 3],
        show=False,
    )

# %%
