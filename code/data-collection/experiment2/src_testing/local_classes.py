import numpy as np
import time

class gridData():
    def __init__(self, haxes, pantilts, current_device):
        self.positions = {}
        self.haxes = haxes
        self.pantilts = pantilts
        self.current_roi = "1"
        self.current_device = current_device
        # create a dictinary with keys positions and value false
        self.touch_checked = {key: False for key in self.pantilts}
        self.rois = {key: [] for key in self.pantilts}
        self.positions = {key: None for key in self.haxes}
    
    # print all the attributes of the class
    def __repr__(self):
        return f"gridData({self.haxes}, Pantilts {self.pantilts}, current device: {self.current_device})"

class TimeStamps():
    def __init__(self, time_out):
        self.start_time = time.time()
        self.shutter_opened = 0
        self.end = False
        self.time_out = time_out
        self.buffering_duration = 0

class TemperatureData():
    def __init__(self, stimulus, delta):
        self.stimulus = stimulus
        self.delta_target = delta
        self.baseline_buffer = []
        self.diff_buffer = []
        self.failed = False

        self.xs = np.arange(0, 160)
        self.ys = np.arange(0, 120)
