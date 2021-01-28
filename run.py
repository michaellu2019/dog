import time
import math
import curses

import Adafruit_PCA9685
import RPi.GPIO as GPIO

run_program = True

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

servo_channels = [[0, 1, 2], [4, 5, 6], [8, 9, 10], [12, 13, 14]]
#servo_neutral_vals = [[90, 90, 90], [90, 90, 90], [90, 90, 90], [90, 90, 90]];
servo_neutral_vals = [[90, 45, 90], [90, 45, 90], [90, 45, 90], [90, 45, 90]]; # leg: [foot, knee, shoulder]
servo_vals = [[servo_neutral_vals[i][j] for j in range(NUM_LEG_SERVOS)] for i in range(NUM_LEGS)]
pwm.set_pwm_freq(60)

screen = curses.initscr()
curses.noecho()
curses.cbreak()
screen.keypad(True)

def setup():
    global pos
    global rot
    
    curses_log("Configuring all servos...")
    for i in range(NUM_LEGS):
        for j in range(NUM_LEG_SERVOS):
            curses_log("Configuring Servo " + str(i) + " " + str(j))
            write_servo(servo_channels[i][j], servo_neutral_vals[i][j])
            time.sleep(1.0)
    curses_log("Servo configuration complete...")
    time.sleep(1.0)
    screen.clear()
    screen.refresh()

def loop():
    """
    pos = input_pos()
    rot = input_rot()
    
    for i in range(NUM_LEGS):
        move_ik(i, pos, rot)
    """
    char = screen.getch()
    speed = 0.5
    if char > 0:
        screen.clear()
        
        if char == ord("q"):
            curses_log("Escape")
            move("pos", [-pos[0], -pos[1], -pos[2] + 89.0])
            move("rot", [-rot[0], -rot[1], -rot[2]])
            return False
        
        if char == ord(" "):
            curses_log("Reset")
            move("pos", [-pos[0], -pos[1], -pos[2] + 89.0])
            move("rot", [-rot[0], -rot[1], -rot[2]])
            
        if char == ord("o"):
            curses_log("Pitch Up")
            move("rot", [0.0, -speed, 0.0])
        elif char == ord("l"):
            curses_log("Pitch Down")
            move("rot", [0.0, speed, 0.0])
        if char == ord("k"):
            curses_log("Yaw Left")
            move("rot", [0.0, 0.0, speed])
        elif char == ord(";"):
            curses_log("Yaw Right")
            move("rot", [0.0, 0.0, -speed])
        if char == ord("i"):
            curses_log("Roll Up")
            move("rot", [speed, 0.0, 0.0])
        if char == ord("p"):
            curses_log("Roll Down")
            move("rot", [-speed, 0.0, 0.0])
            
            
        if char == ord("w"):
            curses_log("Move Forward")
            move("pos", [speed, 0.0, 0.0])
        elif char == ord("s"):
            curses_log("Move Backward")
            move("pos", [-speed, 0.0, 0.0])
        if char == ord("a"):
            curses_log("Move Left")
            move("pos", [0.0, -speed, 0.0])
        elif char == ord("d"):
            curses_log("Move Right")
            move("pos", [0.0, speed, 0.0])
        if char == ord("r"):
            curses_log("Move Up")
            move("pos", [0.0, 0.0, speed])
        if char == ord("f"):
            curses_log("Move Down")
            move("pos", [0.0, 0.0, -speed])
            

    return True

def move(move_type, vel):
    prev_pos = pos
    prev_rot = rot
    
    if move_type == "pos":
        pos[0] += float(vel[0])
        pos[1] += float(vel[1])
        pos[2] += float(vel[2])
    elif move_type == "rot":
        rot[0] += float(vel[0])
        rot[1] += float(vel[1])
        rot[2] += float(vel[2])
    
    curses_log("Position: " + str(tuple(pos)))
    curses_log("Rotation: " + str(tuple(rot)))
    
    error = False
    for i in range(NUM_LEGS):
        move_ik(i, pos, rot)
        
        """
        This code still caused a fire so maybe don't use it?
        try:
            move_ik(i, pos, rot)
        except ValueError:
            curses_log("Error! Dangerous orientation for servos! Fire!!!")
            error = True
            break
        
    if error:
        curses_log("Returning to previous orientation!")
        for i in range(NUM_LEGS):
            try:
                move_ik(i, prev_pos, prev_rot)
            except ValueError:
                curses_log("Error! Dangerous orientation for servos! Fire!!!")
                break
        """
    
    
def rotate(ang_vel):
    pos[0] += float(ang_vel[0])
    pos[1] += float(ang_vel[1])
    pos[2] += float(ang_vel[2])
    
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

def curses_log(msg):
    screen.addstr(msg + "\n")
    screen.refresh()
    
setup()

try:
    while run_program:
        run_program = loop()
        # time.sleep(0.01)
finally:
    print("EXIT")
    GPIO.cleanup()
    curses.nocbreak()
    screen.keypad(0)
    curses.echo()
    curses.endwin()

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

