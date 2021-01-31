import math

import Adafruit_PCA9685

pwm = Adafruit_PCA9685.PCA9685()
pwm.set_pwm_freq(60)

MIN_SERVO_PULSE = 100
MAX_SERVO_PULSE = 650
NUM_LEGS = 4
NUM_LEG_SERVOS = 3
LEG_LEN = 63.0 # all length float units in millimeters
BODY_LEN = 153.0
BODY_WID = 112.0
DEFAULT_HEIGHT = 89.0

def move_ik(leg_id, pos, rot):
    x, y, z = pos
    roll, pitch, yaw = [angle * (math.pi/180.0) for angle in rot]
    
    # yaw
    leg_x = -x
    leg_y = -y
    
    if leg_id == 0:
        leg_x += BODY_LEN/2.0
        leg_y += BODY_WID/2.0
    elif leg_id == 1:
        leg_x += BODY_LEN/2.0
        leg_y -= BODY_WID/2.0
    elif leg_id == 2:
        leg_x -= BODY_LEN/2.0
        leg_y += BODY_WID/2.0
    elif leg_id == 3:
        leg_x -= BODY_LEN/2.0
        leg_y -= BODY_WID/2.0
    
    leg_angle = math.atan(leg_y/leg_x)
    leg_radius = leg_y/math.sin(leg_angle);
    yaw_angle = yaw + leg_angle
    
    yaw_x = leg_radius * math.cos(yaw_angle)
    yaw_y = leg_radius * math.sin(yaw_angle)
    
    if leg_id == 0:
        yaw_x -= BODY_LEN/2.0
        yaw_y -= BODY_WID/2.0
    elif leg_id == 1:
        yaw_x -= BODY_LEN/2.0
        yaw_y += BODY_WID/2.0
    elif leg_id == 2:
        yaw_x += BODY_LEN/2.0
        yaw_y -= BODY_WID/2.0
    elif leg_id == 3:
        yaw_x += BODY_LEN/2.0
        yaw_y += BODY_WID/2.0
    
    # pitch
    if leg_id <= 1:
        pitch *= -1
        yaw_x *= -1
    
    pitch_diff_z = z + math.sin(pitch) * BODY_LEN/2.0
    pitch_diff_x = yaw_x + (BODY_LEN/2.0 - math.cos(pitch) * BODY_LEN/2.0)
        
    pitch_small_shoulder_angle = math.atan(pitch_diff_x/pitch_diff_z)
    pitch_leg_len = pitch_diff_z/math.cos(pitch_small_shoulder_angle)
    
    pitch_shoulder_angle = pitch + pitch_small_shoulder_angle
        
    pitch_z = pitch_leg_len * math.cos(pitch_shoulder_angle)
    pitch_x = pitch_leg_len * math.sin(pitch_shoulder_angle)
    
    if leg_id <= 1:
        pitch_x *= -1
    
    # roll
    if leg_id == 1 or leg_id == 3:
        roll *= -1
        yaw_y *= -1
        
    roll_diff_z = pitch_z - math.sin(roll) * BODY_WID/2.0
    roll_diff_y = (BODY_WID/2.0 - math.cos(roll) * BODY_WID/2.0) - yaw_y
    
    roll_small_hip_angle = math.atan(roll_diff_y/roll_diff_z)
    roll_leg_len = roll_diff_z/math.cos(roll_small_hip_angle)
    
    roll_hip_angle = roll + roll_small_hip_angle
    
    roll_z = roll_leg_len * math.cos(roll_hip_angle)
    roll_y = roll_leg_len * math.sin(roll_hip_angle)
    
    if leg_id == 1 or leg_id == 3:
        roll_y *= -1
    
    # y
    hip_angle = math.atan(roll_y/roll_z)
    y_trans_z = roll_z/math.cos(hip_angle)
    
    # x
    y_shoulder_angle = math.atan(pitch_x/y_trans_z)
    x_trans_z = y_trans_z/math.cos(y_shoulder_angle)
    
    # z
    knee_angle = math.acos(x_trans_z**2/(2 * LEG_LEN**2) - 1)
    z_shoulder_angle = (math.pi - knee_angle)/2
    
    hip_angle = 90.0 + hip_angle * (180.0/math.pi)
    shoulder_angle = (y_shoulder_angle + z_shoulder_angle) * (180.0/math.pi)
    knee_angle = knee_angle * (180.0/math.pi)
    
    leg_angles = [knee_angle, shoulder_angle, hip_angle]
    # print(leg_id, 'IK:', pos, leg_angles)
    
    for i in range(NUM_LEG_SERVOS):
        write_servo(servo_channels[leg_id][i], leg_angles[i])
    
    
def write_servo(channel, angle):
    MAX_SHOULDER_ANGLE = 30.0
    MAX_LEG_ANGLE = 55.0
    if channel in {2, 6, 10, 14} and abs(90.0 - angle) > MAX_SHOULDER_ANGLE:
        angle = 90.0 - MAX_SHOULDER_ANGLE
        raise ValueError("Dangerous shoulder servo angle!")
    if channel in {0, 4, 8, 12} and abs(90.0 - angle) > MAX_LEG_ANGLE:
        angle = 90.0 - MAX_LEG_ANGLE
        raise ValueError("Dangerous leg servo angle!")
    
    if channel in {4, 5, 12, 13}:
        angle = 180 - angle
    pulse_val = int(MIN_SERVO_PULSE + (angle/180.0) * (MAX_SERVO_PULSE - MIN_SERVO_PULSE))
    pwm.set_pwm(channel, 0, pulse_val)