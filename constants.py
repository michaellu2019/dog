EPSILON = 1e-8

NUM_LEGS = 4
NUM_LEG_SERVOS = 3
NUM_HEAD_SERVOS = 2
LEG_LEN = 63.0 # all length float units in millimeters
BODY_LEN = 153.0
BODY_WID = 112.0
DEFAULT_HEIGHT = 89.0

STANDING_SPEED = 1.0

STEP_SIZE = 15.0
STEP_HEIGHT = 12.0
STEP_SPEED = 5.0

pos = [0.0, 0.0, DEFAULT_HEIGHT]
rot = [0.0, 0.0, 0.0]

leg_forward_gait = [[0.0, 0.0, DEFAULT_HEIGHT], # [X, Y, Z] coordinates for foot placement
				[STEP_SIZE * (1.0/3.0), 0.0, DEFAULT_HEIGHT],
				[STEP_SIZE * (2.0/3.0), 0.0, DEFAULT_HEIGHT],
				[STEP_SIZE, 0.0, DEFAULT_HEIGHT], 
				[STEP_SIZE * (2.0/3.0), 0.0, DEFAULT_HEIGHT - STEP_HEIGHT], 
				[STEP_SIZE * (1.0/3.0), 0.0, DEFAULT_HEIGHT - STEP_HEIGHT]]
leg_reverse_gait = [[-step[0], step[1], step[2]] for step in leg_forward_gait]
leg_left_gait = [[step[1], step[0], step[2]] for step in leg_forward_gait]
leg_right_gait = [[step[0], -step[1], step[2]] for step in leg_left_gait]

forward_gait = [leg_forward_gait for i in range(NUM_LEGS)]
reverse_gait = [leg_reverse_gait for i in range(NUM_LEGS)]
left_gait = [leg_left_gait for i in range(NUM_LEGS)]
right_gait = [leg_right_gait for i in range(NUM_LEGS)]

left_turn_gait = [leg_left_gait if i < NUM_LEGS//2 else leg_right_gait for i in range(NUM_LEGS)]
right_turn_gait = [leg_right_gait if i < NUM_LEGS//2 else leg_left_gait for i in range(NUM_LEGS)]

gait = forward_gait[::1]
gait_states = [0, 3, 3, 0]
gait_dest = [gait[i][gait_states[i] + 1] for i in range(NUM_LEGS)]
gait_src = [gait[i][gait_states[i]] for i in range(NUM_LEGS)]
gait_pos = [gait_src[i] for i in range(NUM_LEGS)]
gait_divs = STEP_SIZE/STEP_SPEED

HEAD_SPEAKING_SWEEP = 7.0
HEAD_SPEAKING_SPEED = 1.0

speaking_animation = [[90.0, 90.0], [90.0 - HEAD_SPEAKING_SWEEP, 90.0], [90, 90.0], [90.0 + HEAD_SPEAKING_SWEEP, 90.0]] # [A, B] angles for head servos
speaking_animation_states = [0, 0]
speaking_animation_dest = [speaking_animation[speaking_animation_states[i] + 1][i] for i in range(NUM_HEAD_SERVOS)]
speaking_animation_src = [speaking_animation[speaking_animation_states[i]][i] for i in range(NUM_HEAD_SERVOS)]
speaking_animation_pos = [speaking_animation_src[i] for i in range(NUM_HEAD_SERVOS)]
speaking_animation_divs = HEAD_SPEAKING_SWEEP/HEAD_SPEAKING_SPEED

HEAD_GAIT_SPEED = 7.0
HEAD_GAIT_SPEED = 1.0

head_gait = [[90, 90], [85, 85]]
# head_gait = [[90.0, 90.0], [90.0 - HEAD_SPEAKING_SWEEP, 90.0], [90, 90.0], [90.0 + HEAD_SPEAKING_SWEEP, 90.0]] 
# speaking_animation_states = [0, 0]
# speaking_animation_dest = [speaking_animation[speaking_animation_states[i] + 1][i] for i in range(NUM_HEAD_SERVOS)]
# speaking_animation_src = [speaking_animation[speaking_animation_states[i]][i] for i in range(NUM_HEAD_SERVOS)]
# speaking_animation_pos = [speaking_animation_src[i] for i in range(NUM_HEAD_SERVOS)]
# speaking_animation_divs = HEAD_SPEAKING_SWEEP/HEAD_SPEAKING_SPEED

servo_channels = [[0, 1, 2], [4, 5, 6], [8, 9, 10], [12, 13, 14], [3, 7]] # leg component order: [foot, knee, shoulder] head component order: [head, neck]
# servo_neutral_vals = [[90, 90, 90], [90, 90, 90], [90, 90, 90], [90, 90, 90]]
servo_neutral_vals = [[90, 45, 90], [90, 45, 90], [90, 45, 90], [90, 45, 90], [90, 90]]
#servo_offsets = [[0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0]]
servo_offsets = [[0, 0, -2], [0, 3, -5], [5, 0, -5], [0, 2, -4], [5, 10]]
servo_vals = [[servo_neutral_vals[i][j] for j in range(NUM_LEG_SERVOS)] for i in range(NUM_LEGS)]