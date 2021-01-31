NUM_LEGS = 4
NUM_LEG_SERVOS = 3
LEG_LEN = 63.0 # all length float units in millimeters
BODY_LEN = 153.0
BODY_WID = 112.0
DEFAULT_HEIGHT = 89.0

STEP_SIZE = 20.0
STEP_SPEED = 2.5

pos = [0.0, 0.0, DEFAULT_HEIGHT]
rot = [0.0, 0.0, 0.0]

gait = [[0.0, 0.0, DEFAULT_HEIGHT], [STEP_SIZE, 0.0, DEFAULT_HEIGHT], [STEP_SIZE/2, 0.0, DEFAULT_HEIGHT - 10.0]]
gait_states = [0, 0, 0, 0]
gait_dest = [gait[1], gait[1], gait[1], gait[1]]
gait_src = [gait[0], gait[0], gait[0], gait[0]]
gait_pos = [gait[0], gait[0], gait[0], gait[0]]
gait_divs = STEP_SIZE/STEP_SPEED

servo_channels = [[0, 1, 2], [4, 5, 6], [8, 9, 10], [12, 13, 14]]
#servo_neutral_vals = [[90, 90, 90], [90, 90, 90], [90, 90, 90], [90, 90, 90]];
servo_neutral_vals = [[90, 45, 90], [90, 45, 90], [90, 45, 90], [90, 45, 90]]; # leg: [foot, knee, shoulder]
servo_vals = [[servo_neutral_vals[i][j] for j in range(NUM_LEG_SERVOS)] for i in range(NUM_LEGS)]