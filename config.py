URDF_LEFT_PATH = "./models/inspire_hand_left.urdf"
URDF_RIGHT_PATH = "./models/inspire_hand_right.urdf"

DEBUG_AXIS = False
LEFT_HAND_OFFSET = [0.0, 0.1, 0.0]
RIGHT_HAND_OFFSET = [0.0, -0.1, 0.0]

NORM_MIN = 0.0
NORM_MAX = 1.0

L_PAD    = {"pos": [-0.0085, -0.018,  -0.0065], "rot": [90, 90, -80],  "width": 0.015}
L_NAIL   = {"pos": [ 0.00665, 0.0075,  0.0],    "rot": [90, 90, -105], "width": 0.008}
L_TIP    = {"pos": [-0.0038,  0.0075,  0.0],    "rot": [90,  0, -80],  "width": 0.01}
L_PALM   = {"pos": [-0.0165, -0.11,    0.0],    "rot": [ 0, 90,   0],  "width": 0.05}
L_MIDDLE = {"pos": [ 0.0085, -0.0105, -0.0075], "rot": [90, 90, -20],  "width": 0.01}

L_THUMB_PAD   = {"pos": [ 0.015, -0.0285, -0.0075], "rot": [90, 90, -30], "width": 0.02}
L_THUMB_NAIL  = {"pos": [-0.0035, 0.01375, 0.0],    "rot": [90, 90, -45], "width": 0.008}
L_THUMB_TIP   = {"pos": [-0.009,  0.0005,  0.0],    "rot": [90,  0, -25], "width": 0.01}

L_LITTLE_TIP  = {"pos": [-0.003,   0.0075, 0.0],    "rot": [90,  0,  -80], "width": 0.01}
L_LITTLE_NAIL = {"pos": [ 0.007,  0.0075, 0.0],    "rot": [90, 90, -105],  "width": 0.008}

R_PAD    = {"pos": [-0.011,   0.018,  -0.0065], "rot": [90, 90,  80],   "width": 0.015}
R_NAIL   = {"pos": [ 0.0048, -0.0075,  0.0],    "rot": [90, 90, 102.5], "width": 0.008}
R_TIP    = {"pos": [-0.0065, -0.0075,  0.0],    "rot": [90,  0,  80],   "width": 0.01}
R_PALM   = {"pos": [-0.017,  -0.11,    0.0],    "rot": [ 0, 90,   0],   "width": 0.05}
R_MIDDLE = {"pos": [ 0.008,   0.0125, -0.0075], "rot": [90, 90,  20],   "width": 0.01}

R_THUMB_PAD   = {"pos": [ 0.015,    0.03,  -0.0075], "rot": [90, 90,  30],   "width": 0.02}
R_THUMB_NAIL  = {"pos": [-0.0035,  -0.01,   0.0],    "rot": [90, 90,  45],   "width": 0.008}
R_THUMB_TIP   = {"pos": [-0.009,    0.002,  0.0],    "rot": [90,  0,  25],   "width": 0.01}
R_LITTLE_TIP  = {"pos": [-0.004,   -0.0075, 0.0],    "rot": [90,  0,  80],   "width": 0.01}
R_LITTLE_NAIL = {"pos": [ 0.00576, -0.0075, 0.0],    "rot": [90, 90, 102.5], "width": 0.008}

SENSOR_CONFIG_LEFT = {
    "palm":   {"palm": L_PALM},
    "thumb":  {"tip": L_THUMB_TIP, "nail": L_THUMB_NAIL, "pad": L_THUMB_PAD, "middle": L_MIDDLE},
    "index":  {"tip": L_TIP, "nail": L_NAIL, "pad": L_PAD},
    "middle": {"tip": L_TIP, "nail": L_NAIL, "pad": L_PAD},
    "ring":   {"tip": L_TIP, "nail": L_NAIL, "pad": L_PAD},
    "little": {"tip": L_LITTLE_TIP, "nail": L_LITTLE_NAIL, "pad": L_PAD}
}

SENSOR_CONFIG_RIGHT = {
    "palm":   {"palm": R_PALM},
    "thumb":  {"tip": R_THUMB_TIP, "nail": R_THUMB_NAIL, "pad": R_THUMB_PAD, "middle": R_MIDDLE},
    "index":  {"tip": R_TIP, "nail": R_NAIL, "pad": R_PAD},
    "middle": {"tip": R_TIP, "nail": R_NAIL, "pad": R_PAD},
    "ring":   {"tip": R_TIP, "nail": R_NAIL, "pad": R_PAD},
    "little": {"tip": R_LITTLE_TIP, "nail": R_LITTLE_NAIL, "pad": R_PAD}
}

JOINT_MAP_LEFT = {
    "index_proximal_joint": 14, "middle_proximal_joint": 15, "pinky_proximal_joint": 16,
    "ring_proximal_joint": 17, "thumb_proximal_pitch_joint": 18, "thumb_proximal_yaw_joint": 19
}
JOINT_MAP_RIGHT = {
    "index_proximal_joint": 20, "middle_proximal_joint": 21, "pinky_proximal_joint": 22,
    "ring_proximal_joint": 23, "thumb_proximal_pitch_joint": 24, "thumb_proximal_yaw_joint": 25
}