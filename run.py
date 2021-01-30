import time
import math
import curses

import Adafruit_PCA9685
import RPi.GPIO as GPIO

import vector
from movement.py import move, move_ik 

run_program = True

pwm = Adafruit_PCA9685.PCA9685()

MIN_SERVO_PULSE = 100
MAX_SERVO_PULSE = 650
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
mode = "standing"

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
pwm.set_pwm_freq(60)

screen = curses.initscr()
curses.noecho()
curses.cbreak()
screen.keypad(True)

def setup():
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
    global pos
    global rot
    global mode
    global gait_pos
    global gait_states
    
    char = screen.getch()
    speed = 0.5
    if char > 0:
        screen.clear()
        
        if char == ord("q"):
            curses_log("Escape")
            move("pos", [-pos[0], -pos[1], -pos[2] + DEFAULT_HEIGHT])
            move("rot", [-rot[0], -rot[1], -rot[2]])
            return False
        
        if char == ord(" "):
            mode = "standing"
            curses_log("Reset")
            move("pos", [-pos[0], -pos[1], -pos[2] + DEFAULT_HEIGHT])
            move("rot", [-rot[0], -rot[1], -rot[2]])
        
        if mode == "standing":
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
        
        if mode == "walking":
            if char == ord("w"):
                curses_log("Walk Forward")
                if vector.eq(gait_pos[0], gait_dest[0]):
                    gait_pos[0] = gait_dest[0]
                    gait_states[0] = gait_states[0] + 1 if gait_states[0] + 1 < len(gait) else 0
                    gait_src[0] = gait_dest[0]
                    gait_dest[0] = gait[gait_states[0]]
                
                gait_vel = vector.scalar_div(vector.sub(gait_dest[0], gait_src[0]), gait_divs)
                gait_pos[0] = vector.add(gait_pos[0], gait_vel)
                curses_log(str(gait_pos))
                move_ik(0, gait_pos[0], rot)
                
            elif char == ord("s"):
                curses_log("Walk Backward")
            if char == ord("a"):
                curses_log("Walk Left")
            elif char == ord("d"):
                curses_log("Walk Right")
        
        if char == curses.KEY_ENTER or char == 10 or char == 13:
            mode = "walking" if mode == "standing" else "standing"
            curses_log("Changed Mode to " + mode[0].upper() + mode[1:])
            curses_log("Reset")
            move("pos", [-pos[0], -pos[1], -pos[2] + 89.0])
            move("rot", [-rot[0], -rot[1], -rot[2]])
            
    return True

def curses_log(msg):
    screen.addstr(msg + "\n")
    screen.refresh()

try:
	setup()
	while run_program:
		run_program = loop()
finally:
	print("EXIT")
	GPIO.cleanup()
	curses.nocbreak()
	screen.keypad(0)
	curses.echo()
	curses.endwin()