temp = -1
indx0, indy0 = 1, 1
current_device = "colther"
amount = 10000
centreROI = 1, 2
light = 3

frames = []

grid_heights = {
    "1": 70000,
    "2": 56242,
    "3": 70000,
    "4": 70000,
    "5": 40743,
    "6": 70000,
    "7": 70000,
    "8": 65743,
    "9": 70000,
}

positions = {
    "colther": {"x": 285190, "y": 241108, "z": 0},
    "camera": {"x": 316915, "y": 226965 + 52493, "z": 0},
    "tactile": {"x": 124614, "y": 759198 + 52493, "z": 0},
}

dry_ice_pos = {"x": 0, "y": 290000, "z": 0}

grid = {"colther": None, "camera": None, "tactile": None}

# For dict of zabers
axes = {
    "colther": ["x", "y", "z"],
    "camera": ["y", "x", "z"],
    "tactile": ["x", "y", "z"],
}

# Order of movement
haxes = {
    "colther": ["z", "x", "y"],
    "camera": ["x", "y", "z"],
    "tactile": ["y", "x", "z"],
}

ROIs = {}

default_pantilt = [78, 97, 55]  # [48, 158, 20]
PanTilts = {}
keydelay = 0.15
weDone = False

stimulus = 0
timeout = 2
momen = 0

delta = 0

pid_out = 0
pos_zaber = None

step_sizes = {"colther": 0.49609375, "camera": 0.1905, "tactile": 0.1905}

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

rules = {
    "colther": {"x": True, "y": True, "z": True},
    "camera": {"x": False, "y": True, "z": True},
    "tactile": {"x": False, "y": True, "z": True},
}

answer = None
answered = None

temp = 32
pid_out = 0
current = 0

dummy = True

pos_init = {"x": 260000, "y": 210000, "z": 0}
pos_knuckle = {"x": 300000, "y": 180000, "z": 0}
pos_centre = {"x": 250000, "y": 240472, "z": 0}

hypothesis = None
listened = None
confidence = None

lamp = 0

z_ds = {"colther": None, "camera": None, "tactile": None}
# ds = {'colther': 11.15, 'camera': 9.60, 'tactile': 10.50}
# ds_offset = {'colther': 4.8, 'camera': 0.1, 'tactile': 0.7}


# ds = {'colther': 12.32, 'camera': 11.13, 'tactile': 10.87} # before xmas 2020
# ds = {'colther': 11.40, 'camera': 10.80, 'tactile': 10.5} # 23/03/2021
ds = {"colther": 11.15, "camera": 10.60, "tactile": 9.50}
ds_offset = {"colther": 4.8, "camera": 0.8, "tactile": 0.15}
