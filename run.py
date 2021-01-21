import time
import math
import keyboard

import Adafruit_PCA9685
import RPi.GPIO as GPIO

pwm = Adafruit_PCA9685.PCA9685()

MIN_SERVO_PULSE = 100
MAX_SERVO_PULSE = 650
NUM_LEGS = 4
NUM_LEG_SERVOS = 3
LEG_LEN = 63 # millimeters
BODY_LEN = 153
BODY_WID = 112

pos = [0.0, 0.0, 89.0]
rot = [0.0, 0.0, 0.0]
vel = [0.0, 0.0, 0.5]

servo_channels = [[0, 1, 2], [4, 5, 6], [8, 9, 10], [12, 13, 14]]
#servo_neutral_vals = [[90, 90, 90], [90, 90, 90], [90, 90, 90], [90, 90, 90]];
servo_neutral_vals = [[90, 45, 90], [90, 45, 90], [90, 45, 90], [90, 45, 90]];
servo_vals = [[servo_neutral_vals[i][j] for j in range(NUM_LEG_SERVOS)] for i in range(NUM_LEGS)]
pwm.set_pwm_freq(60)

def setup():
    print("Configuring all servos...");
    for i in range(NUM_LEGS):
        for j in range(NUM_LEG_SERVOS):
            print("Configuring Servo", i, j)
            write_servo(servo_channels[i][j], servo_neutral_vals[i][j])
            time.sleep(1.0)
    print("Servo configuration complete...")
    time.sleep(1.0)

def loop():
    pos = input_pos()
    rot = input_rot()
    
    for i in range(NUM_LEGS):
        move_ik(i, pos, rot)
    
def move_ik(leg_id, pos, rot):
    x, y, z = pos
    roll, pitch, yaw = [angle * (math.pi/180.0) for angle in rot]
    
    x2 = x
    y2 = y
    
    # pitch
    if leg_id <= 1:
        pitch *= -1
        x2 *= -1
    
    pitch_diff_z = z + math.sin(pitch) * BODY_LEN/2.0
    pitch_diff_x = x2 + (BODY_LEN/2.0 - math.cos(pitch) * BODY_LEN/2.0)
        
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
        y2 *= -1
        
    roll_diff_z = pitch_z + math.sin(roll) * BODY_WID/2.0
    roll_diff_y = y2 + (BODY_WID/2.0 - math.cos(roll) * BODY_WID/2.0)
    
    roll_small_hip_angle = math.atan(roll_diff_y/roll_diff_z)
    roll_leg_len = roll_diff_z/math.cos(roll_small_hip_angle)
    
    roll_hip_angle = roll + roll_small_hip_angle
    
    roll_z = roll_leg_len * math.cos(roll_hip_angle)
    roll_y = roll_leg_len * math.sin(roll_hip_angle)
    
    # y
    hip_angle = math.atan(roll_y/roll_z)
    z1 = roll_z/math.cos(hip_angle)
    
    # x
    y_shoulder_angle = math.atan(pitch_x/z1)
    z2 = z1/math.cos(y_shoulder_angle)
    
    # z
    knee_angle = math.acos(z2**2/(2 * LEG_LEN**2) - 1)
    z_shoulder_angle = (math.pi - knee_angle)/2
    
    hip_angle = 90.0 + hip_angle * (180.0/math.pi)
    shoulder_angle = (y_shoulder_angle + z_shoulder_angle) * (180.0/math.pi)
    knee_angle = knee_angle * (180.0/math.pi)
    
    leg_angles = [knee_angle, shoulder_angle, hip_angle]
    print(leg_id, 'IK:', pos, leg_angles)
    
    for i in range(NUM_LEG_SERVOS):
        write_servo(servo_channels[leg_id][i], leg_angles[i])
    
    
def write_servo(channel, angle):
    if (channel in {2, 6, 10, 14} and abs(90.0 - angle) > 15.0) or abs(90.0 - angle) > 60.0:
        raise ValueError("Dangerous servo angle!")
    
    if channel in {4, 5, 12, 13}:
        angle = 180 - angle
    pulse_val = int(MIN_SERVO_PULSE + (angle/180.0) * (MAX_SERVO_PULSE - MIN_SERVO_PULSE))
    pwm.set_pwm(channel, 0, pulse_val)

def move_servo():
    pass

def input_pos():
    x = float(input("Input X:"))
    y = float(input("Input Y:"))
    z = float(input("Input Z:"))
    print("Pos:", [x, y, z])

    time.sleep(1.0)
    return [x, y, z]

def input_rot():
    roll = float(input("Input Roll:"))
    pitch = float(input("Input Pitch:"))
    yaw = float(input("Input Yaw:"))
    print("Rot:", [roll, pitch, yaw])

    time.sleep(1.0)
    return [roll, pitch, yaw]
    
setup()

try:
    while True:
        loop()
        time.sleep(0.01)
finally:
    GPIO.cleanup()

"""
while True:
    # Move servo on channel O between extremes.
    pwm.set_pwm(0, 0, servo_min)
    time.sleep(1)
    pwm.set_pwm(0, 0, servo_max/2)
    time.sleep(1)
    pwm.set_pwm(0, 0, servo_max)
    time.sleep(1)
"""

