############################################################################################################
# This file contains all the global variables used in the experiment. It is imported in all the other files. #
############################################################################################################

############################################
# Thermal image
############################################
temp = -1
indx0, indy0 = 1, 1
radius = 20
centreROI = 1, 2
default_vminT = 20
default_vmaxT = 32

coor_cells = {
    "1": (1, 1),
    "2": (1, 2),
    "3": (1, 3),
    "4": (2, 1),
    "5": (2, 2),
    "6": (2, 3),
    "7": (3, 1),
    "8": (3, 2),
    "9": (3, 3),
}

vmin_file_name = 'vminT'
vmax_file_name = 'vmaxT'

############################################
# Zabers
############################################
zaber_models = {
    "colther": {"x": "end_X-LSQ150B", "y": "end_A-LSQ150B", "z": "end_A-LSQ150B"},
    "camera": {"x": "end_LSM100B-T4", "y": "end_LSM200B-T4", "z": "end_LSM100B-T4"},
    "tactile": {"x": "end_LSM100B-T4", "y": "end_LSM200B-T4", "z": "end_LSM100B-T4"},
}
zaber_models_end = {
    "end_X-LSQ150B": 305381,
    "end_A-LSQ150B": 305381,
    "end_LSM100B-T4": 533333,
    "end_LSM200B-T4": 1066667,
}


centre_grid_positions = {
    "colther": {"x": 221000, "y": 182000, "z": 0},
    "camera": {"x": 128000, "y": 29000, "z": 60000},
    "tactile": {"x": 183724, "y": 342494, "z": 295261},
}

position_z_camera_check = 310000

dry_ice_pos = {"x": 0, "y": 290000, "z": 40000}

grid = {"colther": None, "camera": None, "tactile": None}

# For dict of zabers
axes = {
    "colther": ["x", "y", "z"],
    "camera": ["y", "z", "x"],
    "tactile": ["x", "z", "y"],
}

# Order of movement
haxes = {
    "colther": ["z", "x", "y"],
    "camera": ["x", "y", "z"],
    "tactile": ["y", "x", "z"],
}


step_sizes = {"colther": 0.49609375, "camera": 0.1905, "tactile": 0.1905}
separation_grid = 1

rules = {
    "colther": {"x": True, "y": True, "z": True},
    "camera": {"x": False, "y": False, "z": True},
    "tactile": {"x": False, "y": True, "z": True},
}
init_grid = {"x": 50000, "y": 800000, "z": 70000}
init_meta = {"x": 110000, "y": 170000, "z": 10000}

pos_init = {"x": 260000, "y": 210000, "z": 0}
pos_knuckle = {"x": 300000, "y": 180000, "z": 0}
pos_centre = {"x": 250000, "y": 240472, "z": 0}

touch_z_offset = 52494 
tactile_y_save = 413491
base_touch = 20000
tactile_x_save = 533332

z_ds = {"colther": 40000, "camera": 0}

diff_colther_touch = 52494

adjust_colther = 0.8

stability = {
    0: {'x': 9000, 'y': 64000, 'z': 368000},
    1: {'x': 528000, 'y': 0, 'z': 352000},
} 

safe_post_z_touch = 330000
speed = 153600 * 4
park_touch = {"x": 533332, "z": 270000}
park_pantilt = (125, 0, 0)

limit_restimulation = 3

default_touch_z_offset = 40000

############################################################################################################
# Arduinos
############################################################################################################
# Shutter and syringe
close_shutter = 0
open_shutter = 1

# Pantilt
pantilts = {
    "1": (63, 81, 70),
    "2": (54, 87, 60),
    "3": (50, 91, 61),
    "4": (56, 76, 64),
    "5": (46, 91, 51),
    "6": (49, 89, 61),
    "7": (69, 72, 57),
    "8": (58, 86, 57),
    "9": (37, 97, 57),
}

init_pantilt = (44, 0, 158)

dimmer_usbname = "1423401"
syringe_usbname = "1423101"
pantilt_usbname = "1423301"
light_usbname = "1423201"

turn_off_dimmer = 0

number_human_mapping = {
    "open_shutter": 1,
    "close_shutter": 0,
    "open_random_shutter": 2,
    "close_random_shutter": 3
}

############################################################################################################
# Sound
############################################################################################################
tone_stimulus_frequency = 1400
tone_response_frequency = 1000
tone_trial_frequency = 500

############################################################################################################
# Staircase
############################################################################################################
min_bound_staircase = 0.2
max_bound_staircase = 2

rule_down = 3
rule_up = 1

size_down = 0.1
size_up = 0.14

initial_staircase_temp = 1.2

staircases_info = {
    0: {"direction": "up", "starting_temp": 0.2},
    1: {"direction": "down", "starting_temp": 1.4}
}

stop_reversals = {
    "ex": 13,
    "tb": 5,
}
question = "Was there any temperature change during the tone?"

############################################################################################################
# SDT replication
############################################################################################################
training_temp = 1.5
replication_info = {
    "ex": {
        "restart_n": 800,
        "number_repetitions": 6,
        "number_trials": 108,
        "number_conditions": 2
    },
    "tb": {
        "restart_n": 100,
        "number_repetitions": 1,
        "number_trials": 9,
        "number_conditions": 2
    },
}

control_info = {
    "ex": {
        "restart_n": 800,
        "number_repetitions": 6,
        "number_trials": 162,
        "number_conditions": 3
    },
    "tb": {
        "restart_n": 100,
        "number_repetitions": 1,
        "number_trials": 12,
        "number_conditions": 3
    },
}

############################################################################################################
# Miscellanous
############################################################################################################
keydelay = 0.15
delay_data_display = 1

time_out = {
    "ex": 10,
    "tb": 3,
}

lower_bound_delay = 0.1
higher_bound_delay = 0.4

pre_stimulation_duration = 2.5
post_stimulation_duration = 1


data_path = "/home/ivan/Documents/aaa_online_stuff/coding/phd/publication-touch-inhibits-cold/code/experiment2/data"
thesis_expt_path = "chapter3/originals"

