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

pos = [0.0, 0.0, 89.0]
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
    """
    MIN_Z = 75.0
    MAX_Z = 110.0
    
    pos[2] += vel[2]
    if pos[2] < MIN_Z:
        vel[2] = 0.5
        pos[2] = MIN_Z
    if pos[2] > MAX_Z:
        vel[2] = -0.5
        pos[2] = MAX_Z
    
    z = pos[2]
    c = math.acos(float(z)**2/(2 * LEG_LEN**2) - 1) * 180/math.pi
    b = (180.0 - c)/2
    print(z, c, b)
    """
    pos = input_pos()
    move_ik(pos)
    
def move_ik(pos):
    x = pos[0]
    y = pos[1]
    z = pos[2]
    
    z2 = z
    shoulder_angle1 = math.atan(x/z2)
    z3 = z2/math.cos(shoulder_angle1)
    
    knee_angle = math.acos(z3**2/(2 * LEG_LEN**2) - 1)
    shoulder_angle2 = (math.pi - knee_angle)/2
    #print(shoulder_angle1 * (180.0/math.pi), shoulder_angle2 * (180.0/math.pi))
    
    shoulder_angle = (shoulder_angle1 + shoulder_angle2) * (180.0/math.pi)
    knee_angle = knee_angle * (180.0/math.pi)
    
    print('IK1:', pos, [shoulder_angle, knee_angle])
    
    write_servo(servo_channels[0][0], knee_angle)
    write_servo(servo_channels[0][1], shoulder_angle)
    write_servo(servo_channels[2][0], knee_angle)
    write_servo(servo_channels[2][1], shoulder_angle)
    
    write_servo(servo_channels[1][0], knee_angle)
    write_servo(servo_channels[1][1], shoulder_angle)
    write_servo(servo_channels[3][0], knee_angle)
    write_servo(servo_channels[3][1], shoulder_angle)
    
    
def write_servo(channel, angle):
    if abs(90 - angle) > 60:
        raise ValueError("Dangerous servo angle!")
    
    if channel in {4, 5, 6, 12, 13, 14}:
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

